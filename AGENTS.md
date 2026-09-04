# 🤖 AGENTS.md — Autonomous Agent System Manifest & Routing Protocol

> **Target Workspace:** `[@Justinhubbard37](https://github.com/Justinhubbard37)` AI Repository Vault  
> **Audience:** Autonomous AI Agents (Claude Code, Codex CLI, Cursor, Windsurf, A2UI Agents, LangGraph Swarms)  
> **Data Manifest:** `catalog-manifest.json` (419 Repositories) • `llms.txt` (Compact Standard)  
> **Classification:** Sovereign AI Artifact Directory & Autonomous Knowledge Base  

---

## 🎯 1. System Identity & Objective

You are an expert autonomous AI software engineer, architect, and assistant operating within **Justin Hubbard's (@Justinhubbard37)** sovereign GitHub ecosystem. 

Your objective is to:
1. **Accurately identify and route tasks** to existing codebases in this account without reinventing the wheel or hallucinating repositories.
2. **Reuse proven architectural patterns** from Justin's 31 proprietary core builds (e.g., Tauri v2 desktop harnesses, SQLite persistence boundaries, GraphRAG, OPFS vaults, and marketing OS pipelines).
3. **Programmatically query and extract** repository metadata using `catalog-manifest.json`.

---

## 🧭 2. Task-to-Repository Routing Matrix (Decision Tree)

When assigned a task or asked to reference an architectural component, consult this routing matrix first:

| If the User Requests... | Primary Target Repository | Secondary / Upstream Reference | Key Concept / Stack |
| :--- | :--- | :--- | :--- |
| **Desktop Agent Harness / Host** | `code-name` / `code-name-2-claude-desktop-codex-continuation` | `HarneSSHost`, `the-ai-underground-project` | Tauri v2, two-pane governed workspace, localhost LLM routing. |
| **Local-First SQLite Persistence** | `a-team-studio` | `SimplifAI`, `code-name-2` | Rust/SQLite command boundary, mock persistence, OPFS. |
| **GraphRAG & Knowledge Graphs** | `code-name` | `Supabase` | 3D GraphRAG, entity-relationship extraction, local vector search. |
| **Video-to-Assignment RAG** | `RAG-System---Turning-YouTube-into-Assignments` (Atlas) | `MacroMaster` | Multimodal YouTube transcription, paper research, assignment generator. |
| **Adaptive Study & Quiz App** | `Autodidact-AI-Learning-Studio` | `Interactive-Workbook-Pro` | Dynamic quiz generation, concept explanation, adaptive study sessions. |
| **Inference Acceleration / Latency** | `FreeToken` | `vllm`, `llama.cpp` | High-throughput token processing, model optimization. |
| **Multimodal Vision Embeddings** | `Qwen3-VL-Embedding` | `Supabase` | Vision-language embeddings, multimodal rerankers. |
| **Claude Code Skills & Web Builders** | `astro-builder-skill` | `social-media-skills`, `OnTheLLow-Idea-Discovery-System` | Modular Claude skills, Codex CLI tooling, design system integration. |
| **Model Context Protocol (MCP)** | `mcp-course` | `adk-kotlin` | MCP servers, client tools, protocol integration. |
| **Marketing OS & Brand Strategy** | `TARGHIT` | `TARGHIT-TerminalTreason`, `DigitalAlchemy_Master_Canon.json` | Comprehensive strategic brand OS, master prompt canons. |
| **Cybernetic Terminal & Workspace** | `TerminalTreason` | `TerminalTreason-Brand-Width_Merge`, `ScratchPad` | High-performance cybernetic terminal UI, infinite canvas note studio. |
| **Privacy-First Android AI Chat** | `LMSA` | `nextjs-ai-chatbot`, `opengpts` | Encrypted chat history, Zero Data Retention (ZDR), multi-backend routing. |
| **Agent Environment Simulator** | `envharness` | `Projects-for-Code-Merge-App-Stress-Testing` | Awakening static worlds for agent learning, testbed suites. |

---

## ⚡ 3. Programmatic Query Snippets for AI Agents

When executing bash or python tool calls, use these zero-hallucination one-liners to query the local catalog:

### Find all repositories matching a keyword:
```bash
python3 -c "import json; data=json.load(open('catalog-manifest.json')); print([{'name': r['name'], 'desc': r['description'], 'lang': r['language']} for r in data if 'sqlite' in (r['name']+r['description']).lower()])"
```

### List all 31 Justin Hubbard Core Proprietary Builds:
```bash
python3 -c "import json; data=json.load(open('catalog-manifest.json')); print([r['name'] for r in data if 'core_build' in r.get('tags', [])])"
```

### Get repository clone URL and details by exact name:
```bash
python3 -c "import json, sys; data=json.load(open('catalog-manifest.json')); r=next((x for x in data if x['name'].lower() == 'code-name-2-claude-desktop-codex-continuation'.lower()), None); print(json.dumps(r, indent=2) if r else 'Not found')"
```

---

## 🏗️ 4. Flagship Core Architecture Specifications

### 1. The `code-name` Architecture (Agent Harness + GraphRAG)
* **Stack:** Tauri v2, React, TypeScript, Rust, SQLite, Ollama / LM Studio localhost.
* **Key Mechanisms:**
  - 3D Knowledge Graph visualization with semantic entity links.
  - Segregated execution boundary with gated sidecars.
  - A2UI (Agent-to-User Interface) and A2A (Agent-to-Agent) communication channels.
  - Local-first, zero-telemetry data sovereignty.

### 2. The `Atlas` Multimodal Pipeline (`RAG-System---Turning-YouTube-into-Assignments`)
* **Stack:** Python, Whisper/Transcripts, LLM Orchestration, Markdown formatting.
* **Key Mechanisms:**
  - Ingests YouTube video URLs, extracts verified transcripts.
  - Correlates video concepts with academic research papers.
  - Emits structured student assignments, grading rubrics, and conceptual roadmaps.

### 3. The `TARGHIT` Strategy OS
* **Stack:** Strategic OS, Living Knowledge Canon (`DigitalAlchemy_Master_Canon.json`).
* **Key Mechanisms:**
  - Multi-tier brand positioning, campaign execution playbooks, and tactical copy generation.

---

## 🔒 5. Rules for AI Agents Operating in this Workspace

1. **Do not overwrite existing working versions.** Always snapshot prior files to `/archive/` before modifying production catalogs.
2. **Respect the taxonomy.** When categorizing new repositories, adhere to Option B cross-listing rules and unified developer roll-ups (`Google`, `OpenAI`, `Meta`, `Frontier Labs`).
3. **Preserve data sovereignty.** Never log private API tokens or credentials in unencrypted plaintext files.

---
<sub>*AGENTS.md v1.0.0 • Maintained for Autonomous Agent Systems • Account: @Justinhubbard37*</sub>
