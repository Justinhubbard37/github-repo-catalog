#!/usr/bin/env python3
"""Phase 2 canonical catalog synchronizer.

GitHub input -> normalized canonical state -> deterministic validation ->
canonical manifest -> post-write verification -> success.

This file intentionally does not regenerate downstream Phase 3 surfaces.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, os, re, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import urllib.error, urllib.parse, urllib.request

ACCOUNT = "Justinhubbard37"
API = "https://api.github.com"
GENERATOR = "sync-catalog.py"
GENERATOR_VERSION = "2.0.0"
SCHEMA_VERSION = "1.2.0"
POLICY_ID = "director-d1-private-metadata-included"
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")

class SyncError(RuntimeError): pass
class SourceError(SyncError): pass
class ValidationError(SyncError): pass
class WriteError(SyncError): pass

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def script_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict): raise ValidationError("manifest root must be an object")
    return value

def atomic_bytes(path: Path, payload: bytes) -> None:
    path = path.resolve(); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent); tmp = Path(name)
        with os.fdopen(fd, "wb") as f: f.write(payload); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    except OSError as exc: raise WriteError(f"atomic write failed: {exc}") from exc
    finally:
        if tmp and tmp.exists(): tmp.unlink(missing_ok=True)

def atomic_json(path: Path, value: dict[str, Any]) -> None:
    atomic_bytes(path, (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode())

class GitHub:
    def __init__(self, token: str, account: str):
        if not token: raise SourceError("authenticated GitHub token is required")
        self.account = account
        self.headers = {
            "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "github-repo-catalog-sync/2.0"
        }
    def get(self, path: str) -> Any:
        url = path if path.startswith("https://") else API + path
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as r: raw = r.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")[:300]
            raise SourceError(f"GitHub GET failed HTTP {exc.code}: {body}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise SourceError(f"GitHub GET failed: {exc}") from exc
        try: return json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc: raise SourceError("GitHub returned invalid JSON") from exc
    def inventory(self) -> list[dict[str, Any]]:
        out, page = [], 1
        while True:
            q = urllib.parse.urlencode({"affiliation":"owner","visibility":"all","per_page":100,"page":page,"sort":"full_name","direction":"asc"})
            batch = self.get("/user/repos?" + q)
            if not isinstance(batch, list): raise SourceError("inventory response is not an array")
            out += [r for r in batch if isinstance(r, dict) and str(r.get("owner",{}).get("login","")).casefold()==self.account.casefold()]
            if len(batch) < 100: break
            page += 1
            if page > 100: raise SourceError("pagination safety limit exceeded")
        if not out: raise SourceError("authoritative owner inventory is empty")
        return out
    def detail(self, full_name: str) -> dict[str, Any]:
        owner, name = full_name.split("/",1)
        value = self.get(f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}")
        if not isinstance(value, dict): raise SourceError(f"detail for {full_name} is not an object")
        return value

def iso(value: Any, label: str, nullable: bool=False) -> None:
    if value is None and nullable: return
    if not isinstance(value, str) or not ISO.match(value): raise ValidationError(f"{label} must be ISO UTC timestamp")
    try: datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc: raise ValidationError(f"{label} invalid timestamp") from exc

def upstream_repo(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict): return None
    owner = value.get("owner",{}).get("login") if isinstance(value.get("owner"),dict) else None
    if not all(isinstance(value.get(k),str) and value.get(k) for k in ("full_name","name","html_url")) or not isinstance(owner,str): return None
    return {"full_name":value["full_name"],"owner":owner,"repository":value["name"],"html_url":value["html_url"],
            "default_branch":value.get("default_branch") if isinstance(value.get("default_branch"),str) else None,
            "updated_at":value.get("updated_at") if isinstance(value.get("updated_at"),str) else None,
            "pushed_at":value.get("pushed_at") if isinstance(value.get("pushed_at"),str) else None,
            "archived":value.get("archived") if isinstance(value.get("archived"),bool) else None,
            "private":value.get("private") if isinstance(value.get("private"),bool) else None}

def upstream(detail: dict[str, Any], old: Any, checked: str) -> dict[str, Any]:
    parent, source = upstream_repo(detail.get("parent")), upstream_repo(detail.get("source"))
    curated = {}
    if isinstance(old,dict):
        for k in ("upstream_sync_state","intended_fork_role","repository_role","curated_role"):
            if k in old: curated[k] = copy.deepcopy(old[k])
    return {"provenance_status":"available" if parent else "unavailable_from_github","relationship":"fork",
            "parent":parent,"source":source or parent,"last_checked_at":checked,"curated":curated}

def counts(repos: list[dict[str, Any]]) -> dict[str,int]:
    return {"total_repositories":len(repos),
            "source_repositories_count":sum(not r["is_fork"] for r in repos),
            "fork_repositories_count":sum(r["is_fork"] for r in repos),
            "public_repositories_count":sum(not r["is_private"] for r in repos),
            "private_repositories_count":sum(r["is_private"] for r in repos),
            "core_repositories_count":sum("core_build" in r.get("tags",[]) for r in repos)}

def require(repo: dict[str, Any], key: str) -> Any:
    if key not in repo: raise SourceError(f"GitHub object missing {key}: {repo.get('full_name')}")
    return repo[key]

def normalize(old: dict[str, Any], live: list[dict[str, Any]], details: dict[str,dict[str,Any]], account: str,
              started: str, generator_commit: str | None, code_hash: str, allow_removals: bool) -> dict[str,Any]:
    old_repos = old.get("repositories")
    if not isinstance(old_repos,list): raise ValidationError("existing manifest repositories must be an array")
    old_by_id = {r.get("id"):r for r in old_repos if isinstance(r,dict) and isinstance(r.get("id"),int)}
    old_by_name = {str(r.get("full_name","")).casefold():r for r in old_repos if isinstance(r,dict) and r.get("full_name")}
    live_names = {str(r.get("full_name","")).casefold() for r in live}
    removed = sorted(str(r.get("full_name")) for r in old_repos if isinstance(r,dict) and str(r.get("full_name","")).casefold() not in live_names)
    if removed and not allow_removals:
        preview = ", ".join(removed[:5]); suffix = "..." if len(removed)>5 else ""
        raise SourceError(f"authoritative inventory omitted {len(removed)} catalog records ({preview}{suffix}); use --allow-removals only after review")
    out, added = [], []
    for g in live:
        rid, full = require(g,"id"), require(g,"full_name")
        if not isinstance(rid,int) or isinstance(rid,bool) or not isinstance(full,str): raise SourceError("invalid GitHub repository identity")
        prior = old_by_id.get(rid) or old_by_name.get(full.casefold())
        r = copy.deepcopy(prior) if isinstance(prior,dict) else {}
        if not prior: added.append(full)
        desc = g.get("description") if isinstance(g.get("description"),str) else None
        lang = g.get("language") if isinstance(g.get("language"),str) else None
        if "description" not in r: r["description"] = desc
        if "language" not in r: r["language"] = lang
        if "tags" not in r or not isinstance(r["tags"],list): r["tags"] = []
        topics = g.get("topics",[])
        if not isinstance(topics,list) or any(not isinstance(x,str) for x in topics): raise SourceError(f"invalid GitHub topics for {full}")
        r.update({"id":rid,"name":require(g,"name"),"full_name":full,"html_url":require(g,"html_url"),"clone_url":require(g,"clone_url"),
                  "github_description":desc,"github_language":lang,"topics":topics,"is_fork":bool(require(g,"fork")),"is_private":bool(require(g,"private")),
                  "is_archived":bool(require(g,"archived")),"default_branch":require(g,"default_branch"),"stars":require(g,"stargazers_count"),
                  "forks":require(g,"forks_count"),"created_at":require(g,"created_at"),"updated_at":require(g,"updated_at"),"pushed_at":g.get("pushed_at"),
                  "last_sync_date":started[:10]})
        r["upstream"] = upstream(details.get(full.casefold(),{}), r.get("upstream"), started) if r["is_fork"] else None
        out.append(r)
    out.sort(key=lambda r:(r["full_name"].casefold(),r["id"]))
    c = counts(out); old_meta = old.get("catalog_metadata",{}) if isinstance(old.get("catalog_metadata"),dict) else {}
    meta = {"schema_version":SCHEMA_VERSION,"catalog_version":str(old_meta.get("catalog_version") or "7.0.0"),"generated_at":started,
            "last_sync_timestamp":old_meta.get("last_successful_sync_at") or old_meta.get("last_sync_timestamp"),
            "last_successful_sync_at":old_meta.get("last_successful_sync_at") or old_meta.get("last_sync_timestamp"),"account":account,**c,
            "source_inventory_count":len(live),"source_public_repositories_count":c["public_repositories_count"],
            "source_private_repositories_count":c["private_repositories_count"],
            "information_governance_policy":"Director D1: private repositories remain first-class machine-discoverable catalog entries; contents remain access-controlled",
            "governance":{"policy_id":POLICY_ID,"private_repository_metadata":"included","private_repository_contents":"github-access-controlled"},
            "generator":{"name":GENERATOR,"version":GENERATOR_VERSION,"source_commit":generator_commit,"script_sha256":code_hash},
            "synchronization":{"status":"candidate","source":"authenticated GitHub owner inventory","started_at":started,"completed_at":None,"inventory_sha256":sha(live)},
            "field_authority":{"github_derived":["id","name","full_name","html_url","clone_url","github_description","github_language","topics","is_fork","is_private","is_archived","default_branch","stars","forks","created_at","updated_at","pushed_at","upstream.parent","upstream.source"],
                               "catalog_curated":["description","language","tags","core_build tag","preserved non-GitHub classification fields"],
                               "generated":["schema_version","generated_at","last_successful_sync_at","counts","generator","synchronization"],
                               "derived_operational":[]},
            "inventory_changes":{"added":sorted(added,key=str.casefold),"removed":removed}}
    return {"$schema":old.get("$schema","https://json-schema.org/draft/2020-12/schema"),"catalog_metadata":meta,"repositories":out}

def finalize(candidate: dict[str,Any], completed: str) -> None:
    m = candidate["catalog_metadata"]; m["generated_at"] = completed; m["last_sync_timestamp"] = completed; m["last_successful_sync_at"] = completed
    m["synchronization"]["status"] = "success"; m["synchronization"]["completed_at"] = completed

def validate(value: Any, success: bool) -> dict[str,int]:
    if not isinstance(value,dict): raise ValidationError("manifest root must be an object")
    m, repos = value.get("catalog_metadata"), value.get("repositories")
    if not isinstance(m,dict) or not isinstance(repos,list): raise ValidationError("catalog_metadata object and repositories array are required")
    for k in ("schema_version","catalog_version","generated_at","account","generator","synchronization","governance"):
        if k not in m: raise ValidationError(f"missing catalog_metadata.{k}")
    iso(m["generated_at"],"generated_at")
    if success: iso(m.get("last_successful_sync_at"),"last_successful_sync_at")
    if m.get("governance",{}).get("policy_id") != POLICY_ID or m.get("governance",{}).get("private_repository_metadata") != "included":
        raise ValidationError("Director D1 governance invariant failed")
    if m.get("synchronization",{}).get("status") != ("success" if success else "candidate"): raise ValidationError("synchronization status invalid")
    if success: iso(m["synchronization"].get("completed_at"),"synchronization.completed_at")
    gen = m["generator"]
    if not isinstance(gen,dict) or gen.get("name")!=GENERATOR or gen.get("version")!=GENERATOR_VERSION: raise ValidationError("generator identity invalid")
    if gen.get("source_commit") is not None and not re.fullmatch(r"[0-9a-fA-F]{40}",str(gen["source_commit"])): raise ValidationError("generator source_commit invalid")
    if not re.fullmatch(r"[0-9a-f]{64}",str(gen.get("script_sha256",""))): raise ValidationError("generator script hash invalid")
    ids, names = set(), set()
    req = {"id":int,"name":str,"full_name":str,"html_url":str,"clone_url":str,"topics":list,"is_fork":bool,"is_private":bool,"is_archived":bool,
           "default_branch":str,"stars":int,"forks":int,"created_at":str,"updated_at":str,"tags":list}
    for r in repos:
        if not isinstance(r,dict): raise ValidationError("repository record must be an object")
        for k,t in req.items():
            if k not in r or not isinstance(r[k],t) or (t is int and isinstance(r[k],bool)): raise ValidationError(f"{r.get('full_name','?')}.{k} invalid")
        if r["id"] in ids or r["full_name"].casefold() in names: raise ValidationError(f"duplicate repository identity: {r['full_name']}")
        ids.add(r["id"]); names.add(r["full_name"].casefold()); iso(r["created_at"],r["full_name"]+".created_at"); iso(r["updated_at"],r["full_name"]+".updated_at")
        iso(r.get("pushed_at"),r["full_name"]+".pushed_at",nullable=True)
        if any(not isinstance(x,str) for x in r["topics"]+r["tags"]): raise ValidationError(f"{r['full_name']} tags/topics invalid")
        u = r.get("upstream")
        if r["is_fork"]:
            if not isinstance(u,dict) or u.get("relationship")!="fork" or u.get("provenance_status") not in {"available","unavailable_from_github"}: raise ValidationError(f"fork provenance invalid: {r['full_name']}")
            iso(u.get("last_checked_at"),r["full_name"]+".upstream.last_checked_at")
            if u["provenance_status"]=="available":
                p=u.get("parent")
                if not isinstance(p,dict) or any(not isinstance(p.get(k),str) or not p[k] for k in ("full_name","owner","repository","html_url")): raise ValidationError(f"fork parent invalid: {r['full_name']}")
        elif u is not None: raise ValidationError(f"non-fork has upstream data: {r['full_name']}")
    c=counts(repos)
    for k,v in c.items():
        if m.get(k)!=v: raise ValidationError(f"count mismatch {k}: declared={m.get(k)} actual={v}")
    if m.get("source_inventory_count")!=c["total_repositories"] or m.get("source_private_repositories_count")!=c["private_repositories_count"] or m.get("source_public_repositories_count")!=c["public_repositories_count"]:
        raise ValidationError("authoritative source inventory/count governance invariant failed")
    if c["source_repositories_count"]+c["fork_repositories_count"]!=c["total_repositories"]: raise ValidationError("source+fork invariant failed")
    if c["public_repositories_count"]+c["private_repositories_count"]!=c["total_repositories"]: raise ValidationError("public+private invariant failed")
    return c

def retrieve(client: GitHub) -> tuple[list[dict[str,Any]],dict[str,dict[str,Any]]]:
    live=client.inventory(); ids,names=set(),set(); details={}
    for r in live:
        rid,full=r.get("id"),r.get("full_name")
        if not isinstance(rid,int) or isinstance(rid,bool) or not isinstance(full,str) or rid in ids or full.casefold() in names: raise SourceError(f"invalid/duplicate source identity: {full}")
        ids.add(rid); names.add(full.casefold())
    for r in live:
        if bool(r.get("fork")): details[r["full_name"].casefold()]=client.detail(r["full_name"])
    return live,details

def run(manifest: Path, client: GitHub, dry: bool, candidate_out: Path|None, generator_commit: str|None, allow_removals: bool) -> dict[str,Any]:
    before=manifest.read_bytes(); old=load(manifest); started=now(); live,details=retrieve(client)
    candidate=normalize(old,live,details,client.account,started,generator_commit,script_sha(Path(__file__)),allow_removals)
    validate(candidate,False); finalize(candidate,now()); c=validate(candidate,True)
    if dry:
        if candidate_out:
            if candidate_out.resolve()==manifest.resolve(): raise WriteError("dry-run candidate may not overwrite canonical manifest")
            atomic_json(candidate_out,candidate)
        if manifest.read_bytes()!=before: raise WriteError("dry-run modified canonical manifest")
        return {"counts":c,"candidate_sha256":sha(candidate)}
    try:
        atomic_json(manifest,candidate); reloaded=load(manifest); validate(reloaded,True)
        if sha(reloaded)!=sha(candidate): raise WriteError("post-write serialized state differs from validated candidate")
    except Exception as exc:
        atomic_bytes(manifest,before)
        if isinstance(exc,SyncError): raise
        raise WriteError(f"post-write verification failed; predecessor restored: {exc}") from exc
    return {"counts":c,"candidate_sha256":sha(candidate)}

def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="Synchronize canonical GitHub repository catalog")
    p.add_argument("--token",help="GitHub token with complete owner-repository access"); p.add_argument("--account",default=ACCOUNT)
    p.add_argument("--manifest",type=Path,default=Path(__file__).with_name("catalog-manifest.json")); p.add_argument("--dry-run",action="store_true")
    p.add_argument("--candidate-out",type=Path); p.add_argument("--allow-removals",action="store_true"); p.add_argument("--validate-only",action="store_true")
    p.add_argument("--generator-commit",help="40-character generator commit SHA"); return p

def main(argv:list[str]|None=None)->int:
    a=parser().parse_args(argv)
    try:
        if a.validate_only:
            c=validate(load(a.manifest),True); print(f">> Catalog validation passed: {c['total_repositories']} repositories"); return 0
        if not a.token: raise SourceError("--token is required for synchronization")
        if a.generator_commit and not re.fullmatch(r"[0-9a-fA-F]{40}",a.generator_commit): raise ValidationError("--generator-commit must be a 40-character SHA")
        print(">> Starting GitHub Repository Catalog synchronization...")
        result=run(a.manifest,GitHub(a.token,a.account),a.dry_run,a.candidate_out,a.generator_commit,a.allow_removals); c=result["counts"]
        if a.dry_run: print(f">> Dry-run validation passed: {c['total_repositories']} repositories; canonical manifest unchanged.")
        else: print(f">> Synchronization complete: {c['total_repositories']} repositories; canonical manifest written and post-write validation passed.")
        return 0
    except SyncError as exc: print(f"!! Synchronization failed: {exc}",file=sys.stderr); return 1
    except Exception as exc: print(f"!! Synchronization failed unexpectedly: {exc}",file=sys.stderr); return 1

if __name__=="__main__": raise SystemExit(main())
