# 📜 Portfolio Catalog Changelog & Milestone Archive

All notable releases, architectural taxonomy changes, and application versions for [@Justinhubbard37's](https://github.com/Justinhubbard37) GitHub repository catalog.

---

## [v7.1.0] - 2026-09-05 (Agent Ergonomics & Integrity Release)
### 🤖 Machine-Readability, Navigation & Truthful Artifacts
- **P0: Working sync engine.** `sync-catalog.py` now fetches live repository data via the `gh` CLI (or REST with `--token`), preserves the curated taxonomy, and rebuilds the manifest with real values. It refuses to write when validation fails and no longer prints success on a no-op.
- **P0: Real `validate_catalog()`.** Implemented as a deterministic checker with `--check` (offline, read-only) and `--dry-run` modes. Verifies per-record fields, tag-axis integrity, fork/upstream provenance, count reconciliation, and cross-artifact count drift. Exits non-zero on any failure.
- **P0: Changelog correction.** The v7.0.0 entries claiming a complete sync engine and validation logic were inaccurate and are now marked as such below.
- **P1: `catalog.schema.json`.** Real JSON Schema (draft 2020-12) for the manifest. `$schema` in `catalog-manifest.json` now points at it instead of at the meta-schema, so the manifest is genuinely validatable.
- **P1: Manifest data quality.** `created_at` was a hardcoded placeholder identical on every record and now carries true creation timestamps. `pushed_at` was date-only while its sibling fields were full ISO-8601 and is now normalized. `topics` is now fetched live rather than left blank, but it remains empty on all 420 records because no GitHub topics are set on the repositories themselves — so the documented multi-signal query searches name, description and tags in practice. This is now stated plainly in `AGENTS.md` rather than implied away. All counts reconciled against live GitHub: the catalog had drifted to 420 repositories and 32 core builds.
- **P2: Agent read-order contract.** `AGENTS.md` gains a section 0 defining read order, authority order, and the mandatory pre-completion validation command.
- **P2: `DIRECTORY.md`.** The full repository directory moved out of `README.md`, cutting the landing page's context cost while keeping one-click human access.
- **P2: Invisible agent notices.** HTML comments at the top of `README.md` and `DIRECTORY.md` route agents to the machine entry points. Invisible to humans on GitHub.
- **P2: Archive removed.** `/archive/` held five complete duplicate copies of the catalog (1.3 MB, 57% of the repository). Every version remains recoverable via git tags `v1.0.0`-`v7.0.0`. Searching for a repository name no longer returns competing non-authoritative copies.
- **P3: Routing matrix repaired.** `code-name-2` and `vllm` did not exist in the account; corrected to `code-name-2-claude-desktop-codex-continuation` and `llamacpp-rocm`.
- **P3: Repository hygiene.** Added `.gitignore` and `LICENSE` (MIT).

## [v7.0.0] - 2026-09-04 (Major Audit Remediation Release)
### 🛡️ Enterprise Audit Remediation & Canonical Schema Upgrade
- **P0: `sync-catalog.py` Engine:** *(Corrected in v7.1.0 — this entry was inaccurate. The script shipped in v7.0.0 remained a placeholder that printed success without performing any synchronization. The working engine landed in v7.1.0.)*
- **P1: Canonical Schema Manifest (`catalog-manifest.json`):** Upgraded manifest to schema v1.1.0 with top-level metadata (schema version, catalog version, timestamps, exact counts, governance policy).
- **P1: Count & Core Reconciliation:** Reconciled all counts across all surfaces to exactly **419 repositories** and enumerated all **31 core proprietary builds**.
- **P2: Fork Provenance & Lifecycle State:** Added upstream metadata structure and lifecycle timestamps (`created_at`, `updated_at`, `pushed_at`, `is_archived`, `default_branch`) to manifest records.
- **P2: Full-Field Agent Search:** Upgraded documented agent Python/Bash queries to search across `name`, `description`, `tags`, and `topics`.
- **P3: Information Governance (Policy A):** Formally documented Policy A (Intentional Metadata Disclosure for complete command discovery while preserving source code access control) across `PORTFOLIO_GUIDE.md`, `AGENTS.md`, and `README.md`.
- **Validation Engine:** *(Corrected in v7.1.0 — `validate_catalog()` was documented in v7.0.0 but never implemented. It landed in v7.1.0.)*

---

## [v6.2.0] - 2026-09-03
### ⚡ Tactical AI Agent Fast-Path Header & Query Directive
- Added Covert Ops monospace telemetry block to README.md defining Operator and Agent paths.

---

## [v6.1.0] - 2026-09-03
### 🤖 Autonomous Agent Machine-Readability Stack (AGENTS.md & llms.txt)
- Added AGENTS.md, llms.txt, and catalog-manifest.json.

---

## [v6.0.0] - 2026-09-03
### 🎯 Mutual Exclusion Accordion Disclosure & Global Master Toggle
- Single-open accordion trays (all collapsed by default) with global expand/collapse toggle.

---

## [v5.0.0] - 2026-09-03
### 🎛️ Unified Command Matrix with Progressive Trays
- Re-integrated full capability pills, entity clusters, and language selectors from v3.0 screenshot.

---

## [v4.0.0] - 2026-09-03
### 🚀 Progressive Disclosure Command Deck & Archival Vault
- Initial 3-stage command deck and isolated domain view. Added `PORTFOLIO_GUIDE.md`.

---

## [v3.0.0] - 2026-09-03
### 🛰️ Covert Ops Tactical Search Application
- Covert Ops aesthetic, 2.0s boot sequence, real-time dual-engine hybrid search.

---

## [v2.0.0] - 2026-09-03
### 🎯 Multi-Taxonomy Matrix (Option B) & Education Hub
- Option B cross-listing taxonomy with dedicated 4-tier education hub.

---

## [v1.0.0] - 2026-09-03
### 📚 Baseline Language Catalog & API Initialization
- Initial complete index of all 417 repositories.
