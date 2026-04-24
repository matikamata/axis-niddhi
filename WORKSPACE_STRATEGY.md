# AXIS-NIDDHI Workspace Strategy

## 1. Purpose

This document defines the current workspace, branch, repository, storage, review, snapshot, and large-file strategy for the local AXIS-NIDDHI LAB at:

`<workspace-root>`

Its purpose is to keep development active and flexible without destabilizing production deployment, while preserving reproducibility, storage discipline, and a clear distinction between canonical inputs, mutable LAB state, derived publication, and sealed archival outputs.

Current governing decisions:

- Keep one repository for now.
- Keep Cloudflare Pages deploy from `main` unchanged.
- Keep GitHub Pages backup deploy from `gh-pages` unchanged.
- `/sources` is the single canonical home for original heavyweight source ZIPs.
- Review and snapshot flows must reference canonical source ZIPs by filename, size, sha256, and canonical path.
- Review and snapshot flows must not copy heavyweight source ZIPs by default.
- Full source copies are allowed only in explicit sealed or offline archival modes.

## 2. Workspace Map

The workspace currently contains several classes of folders with different roles. They must not be treated as equivalent.

### Canonical Source Layer

- `sources/`
  - Single canonical home for original heavyweight source ZIPs.
  - This is the only approved default location for original PureDhamma source archives.

### LAB Engine and Mutable Working Layer

- `pipeline/`
  - Active development pipeline.
  - Contains engine scripts, metadata, mutable CSL, derived working directories, SSG engine, and generated static site output.

Important subareas:

- `pipeline/09-csl/`
  - Canonical Source Library in LAB form.
  - Single source of truth for publication generation inside the pipeline.
- `pipeline/13-ssg/`
  - Static site generator engine.
- `pipeline/13-static-site/`
  - Derived publication output used by the current Cloudflare deployment path.
- `pipeline/01-extracted-htmls/`
  - Generated working data.
- `pipeline/02-preprocessed/`
  - Generated working data.
- `pipeline/03-translations/`
  - Generated working data.
- `pipeline/metadata/`
  - Manifests, seals, and operational metadata.
- `pipeline/logs/`
  - Operational logs.

### Review Layer

- `review/`
  - Review workspace built from LAB state for inspection, validation, printing, and controlled review runs.
  - This is operational and reproducible, but it is not the canonical home of heavyweight source archives.

### Snapshot Layer

- `snapshots/`
  - Frozen review or validation snapshots.
  - Used for traceable review states and reproducible checkpoints.
  - Must store source references by default rather than duplicate heavyweight ZIP payloads.

### Runtime and Local-Only Operational Layer

- `wordpress/`
  - Runtime workspace and imported operational environment.
- `logs/`
  - Local top-level logs.
- `.venv/`, `.venv_test/`, `node_modules/`, `.netlify/`
  - Local tooling and runtime dependencies.

### Parallel Local Projects

- `axis-*`
- `The-Skunkworks-Sublime-Saga/`
- `ToDoList/`
- `docs/`

These may coexist in the same workspace, but they are not part of the canonical source policy for AXIS-NIDDHI publication inputs.

## 3. Branch Strategy

The branch model is intentionally conservative.

### `main`

- Production-ready public branch.
- Remains the source for Cloudflare Pages.
- May contain the currently deployed derived static site because deploy behavior is intentionally unchanged at this stage.
- Must stay stable, reviewable, and suitable as the public showcase branch.

### `gh-pages`

- Backup publication branch only.
- Remains the source for GitHub Pages backup.
- Should contain generated site output only, not LAB internals, review workspaces, or heavyweight source archives.

### Development Branches

Use short-lived working branches for active changes:

- `dev/<topic>`
- `lab/<topic>`
- `fix/<topic>`
- `hotfix/<topic>`

Rules:

- Active experimentation happens off `main`.
- Merge to `main` only when the result is stable and intentional.
- Do not use review snapshots as a substitute for code branches.

### Release Tags

Use annotated tags for approved release points.

Suggested formats:

- `release/2026-04-23-v5.4.0`
- `canon/puredhamma-2025-12-31`

Tags mark approved states. Snapshots mark operational review states. They serve different purposes and should remain distinct.

## 4. Repo Strategy

AXIS-NIDDHI should remain a single repository for now.

Reasoning:

- Current deploy behavior is already wired to `main` and `gh-pages`.
- Splitting the repository now would add complexity and deployment risk before the storage model is fully stabilized.
- The immediate problem is not repository count. It is uncontrolled duplication of heavyweight artifacts inside the same workspace.

Recommended one-repo model:

- Public repo contents:
  - Engine code
  - Pipeline code
  - Metadata
  - Documentation
  - Current public deployable output already required by production
- Local-only non-public contents:
  - Heavy source ZIPs
  - Review workspaces
  - Snapshots
  - Runtime WordPress folders
  - Logs
  - Caches

Future repo splitting can be reconsidered later only if it becomes operationally useful after source-reference discipline is in place.

## 5. Canonical Source Policy

`/sources` is the single canonical home for original heavyweight source ZIPs.

Canonical path:

`<workspace-root>/sources`

Policy:

- Original PureDhamma source ZIPs belong in `/sources` only.
- No other folder should act as a second default home for the same ZIP.
- Review, snapshot, release, and distribution workflows must treat `/sources` as the authoritative origin.
- Canonical source identity is established by:
  - filename
  - byte size
  - sha256
  - canonical absolute path

This policy supports both reproducibility and storage discipline.

## 6. Review/Snapshot Policy

Review and snapshot flows must reference canonical source ZIPs by default instead of copying them.

Default source-reference fields:

- `source_filename`
- `source_size_bytes`
- `source_sha256`
- `source_canonical_path`

Optional helpful fields:

- `source_relative_path`
- `source_recorded_at_utc`
- `source_mode`

Default behavior:

- Review flows do not copy heavyweight source ZIPs into `review/`.
- Snapshot flows do not copy heavyweight source ZIPs into `snapshots/.../sources/`.
- Review and snapshot manifests record the canonical source reference and integrity values.

Reproducibility statement:

Reference plus sha256 is sufficient for LAB and review reproducibility because the workflow records exactly which canonical source file is required and exactly which checksum must match.

Explicit archival modes:

- Full source copies are reserved for sealed offline archival bundles.
- These modes should be explicit, named, and intentional.

Suggested explicit modes:

- `--include-sources`
- `--sealed-full-copy`

These explicit modes are not the default review mode. They are reserved for self-contained sealed bundles intended for offline preservation or distribution.

## 7. Large File Policy

Large files must be handled by role, not by convenience.

### Allowed Canonical Heavy Inputs

- Original PureDhamma ZIPs in `/sources`

### Allowed Derived Heavy Outputs

- Generated publication assets when operationally required
- Sealed offline archival bundles when explicitly requested

### Not Allowed by Default

- Blind duplication of heavyweight ZIPs into `review/`
- Blind duplication of heavyweight ZIPs into `snapshots/`
- Uncontrolled spread of large files across helper workspaces

### Storage Principle

One canonical heavyweight input plus manifest references is the default operating model.

This reduces SSD pressure while preserving exact source identity and reproducibility.

## 8. Git Tracking Policy

Git tracking must reflect role and rebuildability.

### Track in Git

- Engine code
- Pipeline scripts
- SSG code
- Core metadata and manifests
- Documentation
- Configuration files
- Branch and deploy definitions
- Production-tracked static site content currently required by the unchanged deploy strategy

### Do Not Track in Git

- Heavy source ZIPs in `/sources`
- Review workspaces
- Snapshot workspaces
- WordPress runtime folders
- Local logs
- Caches
- Temporary working directories
- Virtual environments
- Dependency installation directories

### Policy Clarification

`.gitignore` must reflect the intended operating model, but tracked production paths already present in Git are governed by current deploy reality until an explicit deploy migration is approved.

## 9. Deploy Strategy

Deploy behavior remains unchanged.

### Cloudflare Pages

- Deploys from `main`
- Publish path remains tied to the current production arrangement
- No deploy migration is part of this document

### GitHub Pages

- Backup publication remains on `gh-pages`
- `gh-pages` continues to serve as the backup static site branch

### Strategic Meaning

This strategy intentionally separates:

- Active LAB development
- Production publication
- Backup publication
- Review workspaces
- Snapshot checkpoints

without changing the live deploy flow at this stage.

## 10. Operational Rules

These rules apply across workspace operations.

- Make minimal, surgical changes.
- Do not move canonical files without explicit approval.
- Do not delete files automatically.
- Do not rewrite history.
- Do not change production deploy behavior without explicit approval.
- Treat `/sources` as the only canonical default home for heavyweight source ZIPs.
- Treat `pipeline/09-csl` as the single source of truth for publication generation.
- Treat publication output as derived.
- Use reference manifests for review and snapshot source identity by default.
- Reserve full source copies for explicit sealed offline archival bundles.
- Keep review and snapshot workflows traceable.
- Avoid uncontrolled duplication.

## 11. Future Layers

These are future extension layers, not current required defaults.

### Cloudflare R2

Potential role:

- Durable object storage for heavyweight archival bundles
- Remote storage for sealed source-inclusive packages
- Operational backup layer without polluting the public repo

### Internet Archive

Potential role:

- Public long-term preservation of approved, distributable archival packages
- Release-level historical preservation for non-sensitive material

### IPFS

Potential role:

- Content-addressed distribution layer
- Verifiable public replication of sealed bundles and manifests

### Piql

Potential role:

- Deep cold-storage preservation for high-value sealed archival bundles
- Long-horizon preservation layer for approved permanent records

### Svalbard / Dhamma Seed

Potential role:

- Symbolic and literal deep-preservation layer
- Final preservation tier for sealed, intentional, fully curated heritage bundles
- Not a default operational workspace mechanism

These future layers should sit on top of the current canonical source and manifest discipline, not replace it.

## 12. Next Steps

Immediate next steps:

1. Add this workspace strategy document to the repo root.
2. Align `.gitignore` with the intended local-only review and snapshot policy.
3. Patch review and snapshot builders so source-reference mode is the default.
4. Add explicit sealed modes for source-inclusive offline bundles.
5. Keep deploy behavior unchanged while storage discipline is stabilized.
6. Revisit longer-term repo splitting only after the source-reference policy is working in practice.

Practical objective:

AXIS-NIDDHI should remain reproducible, storage-aware, operationally disciplined, and ready for future preservation layers without multiplying heavyweight source archives across the LAB by default.
