#!/usr/bin/env python3
"""
=============================================================================
PORTFOLIO CATALOG SYNCHRONIZATION & VALIDATION ENGINE
=============================================================================
Regenerates catalog-manifest.json from live GitHub data and verifies that
every artifact in this repository agrees with it.

USAGE
    python3 sync-catalog.py                    # sync via the gh CLI (default)
    python3 sync-catalog.py --token <PAT>      # sync via REST with a token
    python3 sync-catalog.py --check            # validate only, write nothing
    python3 sync-catalog.py --dry-run          # fetch and validate, write nothing

WHAT IT DOES
    1. Fetches every repository in the account from live GitHub.
    2. Carries forward the curated taxonomy tags already in the manifest;
       new repositories are auto-tagged core_build or curated_fork.
    3. Rebuilds catalog-manifest.json with real values for every field.
    4. Runs validate_catalog() and fails loudly on any inconsistency.

WHAT IT DOES NOT DO
    It does not rewrite README.md, DIRECTORY.md or index.html. Those are
    hand-designed human surfaces. When their stated counts drift from the
    manifest, validate_catalog() reports exactly which file and which number
    is wrong so you can correct it deliberately.

EXIT CODES
    0  success
    1  validation failed
    2  could not reach GitHub / bad arguments
=============================================================================
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

ACCOUNT = "Justinhubbard37"
SCHEMA_VERSION = "1.2.0"
CATALOG_VERSION = "7.1.0"
GOVERNANCE_POLICY = (
    "Policy A (Unified Portfolio Directory: Metadata indexed for complete "
    "command discovery; source code remains private and access-controlled)"
)

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(REPO_ROOT, "catalog-manifest.json")
SCHEMA_PATH = os.path.join(REPO_ROOT, "catalog.schema.json")

NO_LANGUAGE = "Docs / Config"

VALID_TAGS = {
    "core_build", "curated_fork", "org_justin",
    "education", "ed_studios", "ed_courses", "ed_engines", "ed_guides",
    "agent_harnesses", "agent_skills", "mcp",
    "rag_graphs", "rag_pipelines", "local_vaults",
    "inf_engines", "inf_acceleration", "inf_multimodal",
    "studio_marketing", "studio_terminals", "studio_chat",
    "eval_simulators", "eval_stress",
    "org_google", "org_openai_anthropic", "org_meta_msft", "org_frontier",
}

REQUIRED_REPO_FIELDS = [
    "id", "name", "full_name", "html_url", "clone_url", "description",
    "language", "topics", "is_fork", "is_private", "is_archived",
    "default_branch", "stars", "forks", "created_at", "updated_at",
    "pushed_at", "last_sync_date", "upstream", "tags",
]

ISO_DT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Files whose stated repository counts must agree with the manifest.
COUNT_SURFACES = [
    "README.md", "DIRECTORY.md", "AGENTS.md", "llms.txt",
    "PORTFOLIO_GUIDE.md", "index.html",
]


# --------------------------------------------------------------------------
# Output helpers
# --------------------------------------------------------------------------

def info(msg):
    print(">> " + msg)


def ok(msg):
    print("   PASS  " + msg)


def fail(msg):
    print("   FAIL  " + msg)


# --------------------------------------------------------------------------
# Fetch
# --------------------------------------------------------------------------

GH_FIELDS = ",".join([
    "id", "name", "nameWithOwner", "url", "description", "primaryLanguage",
    "repositoryTopics", "isFork", "isPrivate", "isArchived",
    "defaultBranchRef", "stargazerCount", "forkCount",
    "createdAt", "updatedAt", "pushedAt", "parent",
])


def fetch_via_gh():
    """Fetch every repository using the authenticated gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "repo", "list", ACCOUNT, "--limit", "1000",
             "--json", GH_FIELDS],
            capture_output=True, timeout=300,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "gh CLI not found. Install GitHub CLI or rerun with --token <PAT>."
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("gh repo list timed out after 300s.")

    # Decode explicitly as UTF-8. Do not rely on the platform locale codec:
    # on Windows that is cp1252, which fails on emoji in repo descriptions.
    stderr_text = (result.stderr or b"").decode("utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError("gh repo list failed: " + stderr_text.strip())

    stdout_text = (result.stdout or b"").decode("utf-8", errors="replace")
    if not stdout_text.strip():
        raise RuntimeError("gh repo list returned no data. " + stderr_text.strip())

    return [normalize_gh(r) for r in json.loads(stdout_text)]


def normalize_gh(r):
    """Map one gh CLI record onto the manifest field names."""
    topics = []
    rt = r.get("repositoryTopics") or []
    for t in rt:
        if isinstance(t, dict):
            name = t.get("name") or (t.get("topic") or {}).get("name")
            if name:
                topics.append(name)
        elif isinstance(t, str):
            topics.append(t)

    parent = r.get("parent")
    upstream = None
    if parent:
        owner = (parent.get("owner") or {}).get("login", "")
        pname = parent.get("name", "")
        if owner and pname:
            upstream = {
                "full_name": owner + "/" + pname,
                "html_url": "https://github.com/" + owner + "/" + pname,
            }

    lang = (r.get("primaryLanguage") or {}).get("name") or NO_LANGUAGE
    branch = (r.get("defaultBranchRef") or {}).get("name") or "main"
    full_name = r.get("nameWithOwner") or (ACCOUNT + "/" + r["name"])

    return {
        "id": gh_id_to_int(r.get("id"), r["name"]),
        "name": r["name"],
        "full_name": full_name,
        "html_url": r.get("url") or ("https://github.com/" + full_name),
        "clone_url": "https://github.com/" + full_name + ".git",
        "description": (r.get("description") or "").strip(),
        "language": lang,
        "topics": sorted(topics),
        "is_fork": bool(r.get("isFork")),
        "is_private": bool(r.get("isPrivate")),
        "is_archived": bool(r.get("isArchived")),
        "default_branch": branch,
        "stars": int(r.get("stargazerCount") or 0),
        "forks": int(r.get("forkCount") or 0),
        "created_at": to_iso(r.get("createdAt")),
        "updated_at": to_iso(r.get("updatedAt")),
        "pushed_at": to_iso(r.get("pushedAt")) or to_iso(r.get("updatedAt")),
        "upstream": upstream,
    }


def gh_id_to_int(raw, name):
    """gh returns a node id string; keep an integer field by hashing stably."""
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    seed = raw if isinstance(raw, str) and raw else name
    h = 0
    for ch in seed:
        h = (h * 131 + ord(ch)) & 0x7FFFFFFFFFFF
    return h


def to_iso(value):
    """Normalize any GitHub timestamp to full ISO-8601 UTC with a Z suffix."""
    if not value:
        return None
    v = str(value).strip()
    if ISO_DT.match(v):
        return v
    if ISO_DATE.match(v):
        return v + "T00:00:00Z"
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


def fetch_via_rest(token):
    """Fetch every repository through the REST API using a personal token."""
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Repo-Catalog-Sync",
    }
    repos, page = [], 1
    while True:
        url = ("https://api.github.com/user/repos?per_page=100&page="
               + str(page) + "&affiliation=owner")
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                batch = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError("GitHub REST error " + str(e.code) + ": " + str(e.reason))
        if not batch:
            break
        repos.extend(batch)
        page += 1
        if page > 20:
            break
    return [normalize_rest(r) for r in repos if r["owner"]["login"] == ACCOUNT]


def normalize_rest(r):
    parent = r.get("parent")
    upstream = None
    if parent:
        upstream = {
            "full_name": parent["full_name"],
            "html_url": parent["html_url"],
        }
    return {
        "id": int(r["id"]),
        "name": r["name"],
        "full_name": r["full_name"],
        "html_url": r["html_url"],
        "clone_url": r["clone_url"],
        "description": (r.get("description") or "").strip(),
        "language": r.get("language") or NO_LANGUAGE,
        "topics": sorted(r.get("topics") or []),
        "is_fork": bool(r.get("fork")),
        "is_private": bool(r.get("private")),
        "is_archived": bool(r.get("archived")),
        "default_branch": r.get("default_branch") or "main",
        "stars": int(r.get("stargazers_count") or 0),
        "forks": int(r.get("forks_count") or 0),
        "created_at": to_iso(r.get("created_at")),
        "updated_at": to_iso(r.get("updated_at")),
        "pushed_at": to_iso(r.get("pushed_at")) or to_iso(r.get("updated_at")),
        "upstream": upstream,
    }


# --------------------------------------------------------------------------
# Merge with curated taxonomy
# --------------------------------------------------------------------------

def load_existing_tags():
    """Return {repo_name: [tags]} from the current manifest, if one exists."""
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    return {r["name"]: list(r.get("tags", []))
            for r in data.get("repositories", [])}


def merge_tags(record, existing):
    """Preserve curated tags; guarantee the core_build / curated_fork axis."""
    tags = set(existing.get(record["name"], []))
    tags.discard("core_build")
    tags.discard("curated_fork")
    if record["is_fork"]:
        tags.add("curated_fork")
    else:
        tags.add("core_build")
        tags.add("org_justin")
    unknown = tags - VALID_TAGS
    if unknown:
        raise RuntimeError(
            record["name"] + ": unknown tag(s) " + str(sorted(unknown))
            + ". Add them to VALID_TAGS and catalog.schema.json first."
        )
    return sorted(tags)


def build_manifest(records, existing_tags):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    today = now[:10]

    repositories = []
    for rec in sorted(records, key=lambda x: x["name"].lower()):
        rec = dict(rec)
        rec["last_sync_date"] = today
        rec["tags"] = merge_tags(rec, existing_tags)
        repositories.append({k: rec[k] for k in REQUIRED_REPO_FIELDS})

    total = len(repositories)
    forks = sum(1 for r in repositories if r["is_fork"])
    private = sum(1 for r in repositories if r["is_private"])

    return {
        "$schema": "./catalog.schema.json",
        "catalog_metadata": {
            "schema_version": SCHEMA_VERSION,
            "catalog_version": CATALOG_VERSION,
            "generated_at": now,
            "last_sync_timestamp": now,
            "account": ACCOUNT,
            "total_repositories": total,
            "source_repositories_count": total - forks,
            "fork_repositories_count": forks,
            "public_repositories_count": total - private,
            "private_repositories_count": private,
            "information_governance_policy": GOVERNANCE_POLICY,
        },
        "repositories": repositories,
    }


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def validate_catalog(manifest=None, strict_surfaces=True):
    """
    Deterministic consistency checks.

    Returns (failures, warnings).
      failures  provable inconsistencies. The catalog is wrong. Exit 1.
      warnings  states that need a human decision but are not provably
                wrong -- a fork whose upstream was deleted, or a stated
                count in a human surface that no longer matches.
    """
    failures = []
    warnings = []

    if manifest is None:
        if not os.path.exists(MANIFEST_PATH):
            return ([MANIFEST_PATH + " does not exist."], [])
        with open(MANIFEST_PATH, encoding="utf-8") as fh:
            manifest = json.load(fh)

    for key in ("$schema", "catalog_metadata", "repositories"):
        if key not in manifest:
            failures.append("manifest is missing top-level key '" + key + "'.")
    if failures:
        return (failures, warnings)

    meta = manifest["catalog_metadata"]
    repos = manifest["repositories"]

    if not os.path.exists(SCHEMA_PATH):
        failures.append("catalog.schema.json is missing.")
    elif manifest["$schema"] != "./catalog.schema.json":
        failures.append(
            "$schema is '" + str(manifest["$schema"])
            + "'; expected './catalog.schema.json'."
        )

    seen_names, seen_ids = set(), set()
    for r in repos:
        n = r.get("name", "<unnamed>")
        missing = [f for f in REQUIRED_REPO_FIELDS if f not in r]
        if missing:
            failures.append(n + ": missing field(s) " + str(missing) + ".")
            continue
        if n in seen_names:
            failures.append(n + ": duplicate repository name.")
        seen_names.add(n)
        if r["id"] in seen_ids:
            failures.append(n + ": duplicate id " + str(r["id"]) + ".")
        seen_ids.add(r["id"])

        if r["description"] is None:
            failures.append(n + ": description is null (use an empty string).")
        for field in ("created_at", "updated_at", "pushed_at"):
            if not ISO_DT.match(str(r[field])):
                failures.append(
                    n + ": " + field + "='" + str(r[field])
                    + "' is not full ISO-8601 UTC."
                )
        if not ISO_DATE.match(str(r["last_sync_date"])):
            failures.append(
                n + ": last_sync_date='" + str(r["last_sync_date"])
                + "' is not YYYY-MM-DD."
            )

        bad = set(r["tags"]) - VALID_TAGS
        if bad:
            failures.append(n + ": unknown tag(s) " + str(sorted(bad)) + ".")
        has_core = "core_build" in r["tags"]
        has_fork = "curated_fork" in r["tags"]
        if has_core == has_fork:
            failures.append(n + ": must carry exactly one of core_build / curated_fork.")
        if r["is_fork"] and not has_fork:
            failures.append(n + ": is_fork is true but not tagged curated_fork.")
        if not r["is_fork"] and not has_core:
            failures.append(n + ": is_fork is false but not tagged core_build.")
        if r["is_fork"] and not r["upstream"]:
            warnings.append(
                n + ": fork has no upstream provenance. GitHub reports no "
                "parent, which happens when the upstream was deleted or made "
                "private. Recorded as null."
            )
        if not r["is_fork"] and r["upstream"]:
            failures.append(n + ": non-fork should not have an upstream.")
        if r["full_name"] != (ACCOUNT + "/" + r["name"]):
            failures.append(
                n + ": full_name '" + r["full_name"] + "' does not match name."
            )

    total = len(repos)
    forks = sum(1 for r in repos if r["is_fork"])
    private = sum(1 for r in repos if r["is_private"])
    expected = {
        "total_repositories": total,
        "source_repositories_count": total - forks,
        "fork_repositories_count": forks,
        "public_repositories_count": total - private,
        "private_repositories_count": private,
    }
    for key in sorted(expected):
        if meta.get(key) != expected[key]:
            failures.append(
                "catalog_metadata." + key + " is " + str(meta.get(key))
                + "; actual is " + str(expected[key]) + "."
            )
    if expected["source_repositories_count"] + forks != total:
        failures.append("source + fork counts do not sum to total.")
    if expected["public_repositories_count"] + private != total:
        failures.append("public + private counts do not sum to total.")

    if strict_surfaces:
        warnings.extend(
            check_surfaces(total, expected["source_repositories_count"])
        )

    return (failures, warnings)


def check_surfaces(total, core):
    """Report human-facing files whose stated counts contradict the manifest."""
    problems = []
    # Only inspect claims about the WHOLE catalog. Section sub-counts such as
    # "(201 repositories)" describe one table and are legitimately not the total.
    stale = re.compile(
        r"(?:Total\s+Repositories\D{0,40}|NODES\s+ACTIVE\D{0,10}|"
        r"all\s+|complete\s+|Total[^\n]{0,20})?\b(\d{3,4})\s*"
        r"(?:Repositories|repositories|NODES\s+ACTIVE|NODES)\b",
        re.IGNORECASE,
    )
    for fname in COUNT_SURFACES:
        path = os.path.join(REPO_ROOT, fname)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        for match in stale.finditer(text):
            n = int(match.group(1))
            context = text[max(0, match.start() - 60):match.end() + 20].lower()
            whole_catalog = any(k in context for k in (
                "total", "nodes", "master", "complete", "all repositories",
                "portfolio", "catalog",
            ))
            if n != total and n != core and whole_catalog:
                line = text[:match.start()].count("\n") + 1
                problems.append(
                    fname + ":" + str(line) + " states '" + match.group(0)
                    + "' but the manifest has " + str(total)
                    + " repositories (" + str(core) + " core builds)."
                )
    return problems


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Synchronize and validate the GitHub repository catalog."
    )
    parser.add_argument("--token", help="GitHub personal access token (REST mode).")
    parser.add_argument("--check", action="store_true",
                        help="Validate the existing manifest and exit. No network, no writes.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and validate, but do not write the manifest.")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as failures. Use in CI.")
    args = parser.parse_args()

    if args.check:
        info("Validating existing catalog-manifest.json (no network, no writes)...")
        f, w = validate_catalog()
        return report(f, w, args.strict)

    info("Fetching live repository data for @" + ACCOUNT + "...")
    try:
        records = fetch_via_rest(args.token) if args.token else fetch_via_gh()
    except RuntimeError as e:
        sys.stderr.write("!! " + str(e) + "\n")
        return 2

    if not records:
        sys.stderr.write(
            "!! GitHub returned zero repositories. Refusing to overwrite the manifest.\n"
        )
        return 2
    info("Fetched " + str(len(records)) + " repositories.")

    existing_tags = load_existing_tags()
    previous = set(existing_tags)
    current = set(r["name"] for r in records)
    added, removed = sorted(current - previous), sorted(previous - current)
    if added:
        info("New since last sync (" + str(len(added)) + "): " + ", ".join(added))
    if removed:
        info("Gone since last sync (" + str(len(removed)) + "): " + ", ".join(removed))
    if not added and not removed:
        info("No repositories added or removed since last sync.")

    try:
        manifest = build_manifest(records, existing_tags)
    except RuntimeError as e:
        sys.stderr.write("!! " + str(e) + "\n")
        return 1

    info("Running validate_catalog()...")
    failures, warnings = validate_catalog(manifest)
    code = report(failures, warnings, args.strict)
    if code != 0:
        sys.stderr.write("!! Validation failed. Manifest NOT written.\n")
        return code

    if args.dry_run:
        info("--dry-run: validation passed, manifest not written.")
        return 0

    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    info("Wrote " + MANIFEST_PATH)
    info("Synchronization complete. " + str(len(records)) + " repositories, "
         + str(manifest["catalog_metadata"]["source_repositories_count"])
         + " core builds.")
    return 0


def warn(msg):
    print("   WARN  " + msg)


def report(failures, warnings=None, strict=False):
    warnings = warnings or []
    for w in warnings:
        warn(w)
    for f in failures:
        fail(f)

    if failures:
        sys.stderr.write(
            "\n!! validate_catalog(): " + str(len(failures)) + " check(s) failed.\n"
        )
        return 1
    if warnings and strict:
        sys.stderr.write(
            "\n!! validate_catalog(): " + str(len(warnings))
            + " warning(s), and --strict is set.\n"
        )
        return 1
    if warnings:
        ok("validate_catalog(): no failures. " + str(len(warnings))
           + " warning(s) above need a human decision.")
    else:
        ok("validate_catalog(): all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
