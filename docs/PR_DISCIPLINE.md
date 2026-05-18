# PR Discipline

## Purpose

`main` is connected to GitHub and Cloudflare. Changes merged or pushed to `main` may trigger a Cloudflare staging deploy.

For normal work, protect `main` with branch and pull request discipline. This keeps review visible, makes rollback easier, and helps new collaborators understand what changed.

## Normal workflow

Use the normal branch workflow for most changes:

1. Create a branch.
2. Make a small scoped change.
3. Run validation.
4. Commit.
5. Push the branch.
6. Open a pull request.
7. Review the diff.
8. Merge after approval.

## When direct main push may be acceptable

Direct pushes to `main` should be controlled exceptions, not the default.

They may be acceptable for:

- tiny docs-only corrections;
- emergency routing fixes;
- staging-only Cloudflare corrections;
- cases where the operator explicitly accepts the bypass risk.

When a direct push is used, document:

- what changed;
- why direct push was used;
- whether a tag or checkpoint is meaningful.

## What should not be direct-pushed

Do not direct-push:

- pipeline architecture changes;
- CSL / `09-csl` changes;
- translation corpus changes;
- Netlify official payload updates;
- large generated output;
- NANA, Navigator, or Cosmos logic;
- secrets or credentials;
- broad refactors.

## Recommended commands

Basic safe branch workflow:

```bash
git switch main
git pull --ff-only origin main
git switch -c docs/example-branch-YYYYMMDD
git status -sb
```

After committing:

```bash
git push origin HEAD
```

Then open a pull request.

## Cloudflare note

Pushes or merges to `main` may trigger a Cloudflare deploy. Even docs-only changes can produce a staging deploy.

## Final rule

If unsure, use a branch and PR.
