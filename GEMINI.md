# GEMINI — AXIS OPERATING CONTEXT

Before any action:

1. Read `.axis_rules.md`
2. Follow all invariants strictly

You are operating in a canonical preservation system.

Behavior:

- Audit-first, not action-first
- No autonomous edits
- No architectural assumptions
- No "best practices" unless explicitly requested

Always:

- Explain before suggesting
- Ask before modifying
- Prefer minimal changes

Goal:

Support understanding and safe evolution of the system
without breaking determinism or canonical structure.

## Operational Safety Rule

Before modifying any file, classify the target path as:

CANON, ENGINE, DERIVED, DOCS, OUTPUT, SECRET, LEGACY, or SKUNKWORKS.

If the classification is unclear, stop and ask before editing.

Never treat SKUNKWORKS, LEGACY, DOCS, OUTPUT, or generated artifacts as canonical source of truth.

Canonical authority flows from:

SOURCE ZIP → CSL / Canon → derived layers → UX / apps / experiments.

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
