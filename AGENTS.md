# 🤖 AGENTS.md — Autonomous Agent System Manifest & Routing Protocol

> **Target Workspace:** `[@Justinhubbard37](https://github.com/Justinhubbard37)` AI Repository Vault  
> **Audience:** Autonomous AI Agents (Claude Code, Codex CLI, Cursor, Windsurf, A2UI Agents, LangGraph Swarms)  
> **Canonical Manifest:** `catalog-manifest.json` (419 Repositories) • `llms.txt` (Compact Standard)  
> **Catalog Version:** `v7.0.0` • **Schema Version:** `1.1.0`  
> **Governance Policy:** Policy A (Intentional Metadata Indexing; Source Code Protected)  

---

## 🎯 1. System Identity & Objective

You are an expert autonomous AI software engineer, architect, and assistant operating within **Justin Hubbard's (@Justinhubbard37)** sovereign GitHub ecosystem. 

Your objective is to:
1. **Accurately identify and route tasks** to existing codebases in this account without reinventing the wheel or hallucinating repositories.
2. **Reuse proven architectural patterns** from Justin's 31 proprietary core builds (e.g., Tauri v2 desktop harnesses, SQLite persistence boundaries, GraphRAG, OPFS vaults, and marketing OS pipelines).
3. **Programmatically query and extract** repository metadata using `catalog-manifest.json` across all routing fields.

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

## ⚡ 3. Full-Field Programmatic Query Snippets (Zero-Hallucination)

AI agents should query `catalog-manifest.json` across **all routing fields** (name, description, tags, and topics) using these deterministic one-liners:

### Full-Field Multi-Signal Search (Name + Description + Tags + Topics):
```bash
python3 -c "import json; m=json.load(open('catalog-manifest.json')); q='sqlite'; print([{'name': r['name'], 'desc': r['description'], 'tags': r['tags'], 'lang': r['language'], 'priv': r['is_private']} for r in m['repositories'] if q in (r['name']+' '+r['description']+' '+' '.join(r.get('topics',[]))+' '+' '.join(r.get('tags',[]))).lower()])"
```

### Enumerate All 31 Core Proprietary Builds:
```bash
python3 -c "import json; m=json.load(open('catalog-manifest.json')); print([r['name'] for r in m['repositories'] if 'core_build' in r.get('tags', [])])"
```

### Inspect Upstream Provenance for Forks:
```bash
python3 -c "import json; m=json.load(open('catalog-manifest.json')); print([{'name': r['name'], 'upstream': r.get('upstream')} for r in m['repositories'] if r['is_fork']][:10])"
```

---

## 🏗️ 4. Complete Catalog of All 31 Core Proprietary Builds

| # | Repository | Stack | Visibility | Role & Key Mechanisms |
| :-: | :--- | :---: | :---: | :--- |
| 1 | [`a-team-studio`](https://github.com/Justinhubbard37/a-team-studio) | `TypeScript` | `Public` | Local-first Tauri v2 desktop studio prototype with React/TypeScript frontend and Rust/SQLite persistence boundary. |
| 2 | [`AlchemyArchitect`](https://github.com/Justinhubbard37/AlchemyArchitect) | `Docs / Config` | `Private 🔒` | AlchemyArchitect AI Studio application build |
| 3 | [`Autodidact-AI-Learning-Studio`](https://github.com/Justinhubbard37/Autodidact-AI-Learning-Studio) | `Docs / Config` | `Private 🔒` | This app is an AI-powered learning studio for serious self-learners that turns questions, notes, and uploaded material into structured explanations, quizzes, and adaptive study sessions. |
| 4 | [`ChatGPT-Codex`](https://github.com/Justinhubbard37/ChatGPT-Codex) | `Docs / Config` | `Private 🔒` | Projects created using ChatGPT-Codex |
| 5 | [`Cloned-Outskill-Generative-AI-Engineering-Mastermind-Repo`](https://github.com/Justinhubbard37/Cloned-Outskill-Generative-AI-Engineering-Mastermind-Repo) | `Jupyter Notebook` | `Private 🔒` | Hands-on workshop code, notebooks, and API integration guides for Outskill GenAI Mastermind. |
| 6 | [`code-name`](https://github.com/Justinhubbard37/code-name) | `TypeScript` | `Private 🔒` | End goal: a Tauri v2, model-agnostic agent harness and self-growing local database ecosystem with 3D knowledge graph/GraphRAG, A2A/A2UI, ADK-Python, browser/WebMCP support, Ollama/LM Studio localhost, API-key providers, sidecars, gated execution, maximum user control, and local-first, data-sovereign workflows. |
| 7 | [`code-name-2-claude-desktop-codex-continuation`](https://github.com/Justinhubbard37/code-name-2-claude-desktop-codex-continuation) | `TypeScript` | `Private 🔒` | Local-first, model-agnostic desktop agent harness with two-pane workspace and local knowledge-graph persistence. |
| 8 | [`Codex-SimplifAI`](https://github.com/Justinhubbard37/Codex-SimplifAI) | `Docs / Config` | `Public` | Desktop-first Tauri v2 AI application for turning complex source material into structured guides, summaries, and outlines. |
| 9 | [`DigitalAlchemy_Master_Canon.json`](https://github.com/Justinhubbard37/DigitalAlchemy_Master_Canon.json) | `Docs / Config` | `Private 🔒` | Living master knowledge canon and strategic prompt schema for DigitalAlchemy workflows. |
| 10 | [`github-repo-catalog`](https://github.com/Justinhubbard37/github-repo-catalog) | `Docs / Config` | `Public` | Comprehensive directory, categorized index, and automated overview of all repositories by Justinhubbard37. |
| 11 | [`HarneSSHost`](https://github.com/Justinhubbard37/HarneSSHost) | `Rust` | `Private 🔒` | Modular desktop host and evaluation platform for AI agent harnesses and tool integration. |
| 12 | [`Interactive-Workbook-Pro`](https://github.com/Justinhubbard37/Interactive-Workbook-Pro) | `HTML` | `Private 🔒` | Interactive web-based educational workbook application with dynamic exercise modules. |
| 13 | [`landing-page`](https://github.com/Justinhubbard37/landing-page) | `HTML` | `Public` | Static web landing page deployment with custom domain configuration. |
| 14 | [`landing-page-with-qwen3-coder`](https://github.com/Justinhubbard37/landing-page-with-qwen3-coder) | `Docs / Config` | `Public` | Precision Made Cinematic interactive landing page built with Qwen3-Coder. |
| 15 | [`LMSA`](https://github.com/Justinhubbard37/LMSA) | `Docs / Config` | `Public` | Privacy-first Android AI chat client with encrypted history, ZDR routing, and multi-backend support (OpenRouter, LM Studio, Ollama). |
| 16 | [`MacroMaster`](https://github.com/Justinhubbard37/MacroMaster) | `Docs / Config` | `Private 🔒` | Step-by-step instructional roadmaps and automated macro execution playbooks. |
| 17 | [`NBA-basketball-statistics`](https://github.com/Justinhubbard37/NBA-basketball-statistics) | `Docs / Config` | `Public` | Data tracking, metrics aggregation, and analytics toolkit for NBA basketball games. |
| 18 | [`nextjs-ai-chatbot`](https://github.com/Justinhubbard37/nextjs-ai-chatbot) | `TypeScript` | `Private 🔒` | Full-stack AI chatbot SDK template built with Next.js 14 App Router and Vercel AI SDK. |
| 19 | [`OnTheLLow-Idea-Discovery-System`](https://github.com/Justinhubbard37/OnTheLLow-Idea-Discovery-System) | `Docs / Config` | `Private 🔒` | Autonomous idea discovery and concept extraction workflow built with Claude Code. |
| 20 | [`Projects-for-Code-Merge-App-Stress-Testing`](https://github.com/Justinhubbard37/Projects-for-Code-Merge-App-Stress-Testing) | `HTML` | `Public` | Compiled testbed suite of multi-framework codebases for merge engine stress-testing. |
| 21 | [`RAG-System---Turning-YouTube-into-Assignments`](https://github.com/Justinhubbard37/RAG-System---Turning-YouTube-into-Assignments) | `Python` | `Private 🔒` | Atlas — AI-powered content analysis platform combining YouTube transcription, academic research, and assignment generation. |
| 22 | [`Replit`](https://github.com/Justinhubbard37/Replit) | `Docs / Config` | `Private 🔒` | Cloud development configurations and interactive workspace templates. |
| 23 | [`ScratchPad`](https://github.com/Justinhubbard37/ScratchPad) | `HTML` | `Public` | Local-first, infinite-canvas sticky note desktop application with BYOK AI built with Tauri v2. |
| 24 | [`SimplifAI`](https://github.com/Justinhubbard37/SimplifAI) | `Docs / Config` | `Private 🔒` | Local-first web application with Origin Private File System (OPFS) and BYOK AI integration. |
| 25 | [`Supabase`](https://github.com/Justinhubbard37/Supabase) | `Docs / Config` | `Public` | Data storage, vector embeddings, and backend integration bridge with Mistral AI. |
| 26 | [`TARGHIT`](https://github.com/Justinhubbard37/TARGHIT) | `Docs / Config` | `Private 🔒` | MARKETING_OS — Comprehensive strategic marketing and brand execution operating system. |
| 27 | [`TARGHIT-TerminalTreason`](https://github.com/Justinhubbard37/TARGHIT-TerminalTreason) | `Docs / Config` | `Private 🔒` | Enterprise hygiene archives and deployment assets for TARGHIT and TerminalTreason. |
| 28 | [`TerminalTreason`](https://github.com/Justinhubbard37/TerminalTreason) | `TypeScript` | `Private 🔒` | Enterprise-grade cybernetic terminal UI and agent workspace built with React and Tailwind. |
| 29 | [`TerminalTreason-Brand-Width_Merge`](https://github.com/Justinhubbard37/TerminalTreason-Brand-Width_Merge) | `TypeScript` | `Private 🔒` | Enterprise-grade terminal UI and agent workspace merge branch. |
| 30 | [`the-ai-underground-project`](https://github.com/Justinhubbard37/the-ai-underground-project) | `Rust` | `Private 🔒` | Local-first desktop AI workbench and terminal harness built with Tauri and React. |
| 31 | [`The-Local-Layer`](https://github.com/Justinhubbard37/The-Local-Layer) | `Docs / Config` | `Private 🔒` | Local-first orchestration layer and data-sovereign runtime for local LLMs and tools. |

---

## 🔒 5. Information Governance & Policy A Compliance

1. **Policy A Compliance:** High-level metadata of private projects is intentionally indexed for complete command portfolio discovery. The source code remains private on GitHub.
2. **Deterministic Validation:** The manifest is the authoritative source of truth. Any synchronization must run `validate_catalog()` before reporting success.
3. **Preservation:** Always archive previous milestone artifacts in `/archive/` before modifying production catalogs.

---
<sub>*AGENTS.md v7.0.0 • Maintained for Autonomous Agent Systems • Account: @Justinhubbard37*</sub>
