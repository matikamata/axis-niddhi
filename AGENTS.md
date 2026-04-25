# AXIS-NIDDHI — AGENTS.md
# Operational Rules for Codex / AI Agents

## 1. Mission

AXIS-NIDDHI is a canonical corpus preservation engine.

Goal:
- Preserve corpus with integrity, reproducibility, independence
- Ensure deterministic rebuild from source ZIP → CSL → publication

Reference:
- Engine model and purpose :contentReference[oaicite:0]{index=0}

---

## 2. Core Invariants (NON-NEGOTIABLE)

1. CSL is the single source of truth
2. Publication is always derived (never edited directly)
3. Rebuild must be deterministic
4. No silent mutations (everything traceable)
5. Archaeology is immutable (read-only, never touched)

Architecture:
- Lab → mutable
- Release → reproducible
- Archaeology → permanent record :contentReference[oaicite:1]{index=1}

---

## 3. Operational Rules

### DO:
- Make minimal, surgical changes
- Prefer compatibility shims over refactors
- Respect existing pipeline flow
- Identify dependencies before editing
- Always map before modifying

### DO NOT:
- Rename scripts without explicit instruction
- Move files across layers (Lab/Release/Archaeology)
- Break run_full_pipeline.sh flow
- Introduce hidden side effects
- Modify CSL structure

---

## 4. Pipeline Reality (CRITICAL)

Entry point:
- run_full_pipeline.sh

SSG:
- build.py = real engine
- SD03_static_site_build.py = compatibility shim

Bootstrap:
- setup_v54_static_site.sh prepares 13-ssg/

Important:
- Missing SD03 triggers bootstrap logic
- Pipeline is designed to self-heal at SSG stage :contentReference[oaicite:2]{index=2}

---

## 5. Change Strategy

All changes must follow:

1. Map current behavior
2. Identify failure points
3. Propose minimal fix
4. Apply only approved patch

Never:
- Refactor before stabilizing
- Optimize before confirming correctness

---

## 6. Current Priority

Focus:
- Stabilize SSG bootstrap
- Ensure build reproducibility
- Maintain compatibility with V5.4 pipeline

No architectural changes yet.

---

## 7. Definition of Success

A valid state is:

source ZIP
→ full pipeline
→ CSL
→ static site (13-static-site/)
→ reproducible on another machine

This must work without manual intervention.

---

## 8. Authority

If conflict exists:
- AGENTS.md overrides convenience decisions
- Canonical documents define truth
- Implementation must conform to protocol

Reference index:
:contentReference[oaicite:3]{index=3}

---

## 🔒 PRODUCTION SAFETY

All agents MUST read:

AXIS_NAVIGATOR_PRODUCTION_GUARDRAILS.md

This file overrides any optimization, refactor or suggestion.

If there is any conflict:
- Guardrails ALWAYS win

## Path Classification Rule

Before editing, classify every touched path as one of:

- CANON
- ENGINE
- DERIVED
- DOCS
- OUTPUT
- SECRET
- LEGACY
- SKUNKWORKS

If classification is unclear, do not edit the file.

Rules:

- CANON files are sources of truth and must not be changed unless the task explicitly names them.
- ENGINE files may be changed only for implementation tasks with clear scope.
- DERIVED and OUTPUT files may be regenerated, but should not become sources of truth.
- SECRET files must never be committed, copied to release artifacts, or exposed in logs.
- LEGACY and SKUNKWORKS files are historical or experimental unless explicitly promoted.
- DOCS may be updated freely when documenting current state, decisions, or handoffs.

## Protected Areas

Do not modify these unless the user explicitly asks:

- `pipeline/sources/`
- `pipeline/03-translations/`
- `pipeline/09-csl/`
- `pipeline/metadata/ledger*`
- `pipeline/capsule/`
- `pipeline/seeds/`
- `pipeline/scripts/private/`
- release manifests and seal files

-> Leitura "Humanizada":
[Skunkworks  = bagunçado, livre, cheiroso, laboratório
Root        = claro, só comandos e bússolas
Pipeline    = limpo, auditável, sem poesia excessiva
Vitrine     = Steve Jobs
Canon       = Monastério]
-->> Essa é a arquitetura humana ideal do projeto. Bagunça criativa com borda clara.

END OF FILE
