# Enterprise Agent MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local MVP for an enterprise knowledge-base and ticket-collaboration agent with a unified provider interface for OpenAI-compatible and Anthropic APIs.

**Architecture:** The project centers on a provider-agnostic `LLMProvider` contract and a small agent loop that consumes normalized tool requests. Retrieval, ticket persistence, and tool execution are isolated behind small modules so the business flow stays easy to test with fakes.

**Tech Stack:** Python, FastAPI, SQLite, standard-library HTTP clients, unittest

---

### Task 1: Define expected behavior with tests

**Files:**
- Create: `output/enterprise_agent_mvp/tests/test_retriever.py`
- Create: `output/enterprise_agent_mvp/tests/test_ticket_repository.py`
- Create: `output/enterprise_agent_mvp/tests/test_provider_normalization.py`
- Create: `output/enterprise_agent_mvp/tests/test_agent_engine.py`

- [ ] Write failing tests for retrieval ranking, ticket lifecycle, provider normalization, and tool-executing agent loops.
- [ ] Run: `python -m unittest discover -s tests -v`
- [ ] Confirm failure is due to missing app modules.

### Task 2: Implement core domain modules

**Files:**
- Create: `output/enterprise_agent_mvp/app/models.py`
- Create: `output/enterprise_agent_mvp/app/rag/retriever.py`
- Create: `output/enterprise_agent_mvp/app/db/ticket_repository.py`
- Create: `output/enterprise_agent_mvp/app/tools/ticket_tools.py`

- [ ] Implement the shared dataclasses used by providers, tools, and the agent engine.
- [ ] Implement the lightweight retriever with deterministic token-overlap scoring.
- [ ] Implement SQLite-backed ticket storage with create/get/list/escalate helpers.
- [ ] Run the focused tests until green.

### Task 3: Implement provider adapters and agent loop

**Files:**
- Create: `output/enterprise_agent_mvp/app/providers/base.py`
- Create: `output/enterprise_agent_mvp/app/providers/openai_compatible.py`
- Create: `output/enterprise_agent_mvp/app/providers/anthropic_provider.py`
- Create: `output/enterprise_agent_mvp/app/providers/factory.py`
- Create: `output/enterprise_agent_mvp/app/agent/engine.py`

- [ ] Implement normalized provider response parsing for OpenAI-compatible payloads.
- [ ] Implement normalized provider response parsing for Anthropic payloads.
- [ ] Implement the agent loop using normalized tool requests and tool-result feedback.
- [ ] Run: `python -m unittest discover -s tests -v`

### Task 4: Add app wiring, sample data, and docs

**Files:**
- Create: `output/enterprise_agent_mvp/app/config.py`
- Create: `output/enterprise_agent_mvp/app/main.py`
- Create: `output/enterprise_agent_mvp/data/knowledge_base.txt`
- Create: `output/enterprise_agent_mvp/.env.example`
- Create: `output/enterprise_agent_mvp/requirements.txt`
- Create: `output/enterprise_agent_mvp/README.md`

- [ ] Wire the provider factory, retriever, tools, and FastAPI routes together.
- [ ] Add sample knowledge base content and environment configuration examples.
- [ ] Document startup, request examples, provider switching, and project structure.

### Task 5: Resume integration and deliverables

**Files:**
- Modify: `C:\Users\28315\Documents\Codex\2026-05-01\skills\build_resume_docx.py`
- Create: `output/enterprise_agent_mvp/INTERVIEW_QA.md`

- [ ] Rewrite the project into STAR format for the resume.
- [ ] Add interview questions and concise answer directions.
- [ ] Regenerate the Word resume draft and deliver the final file path.
