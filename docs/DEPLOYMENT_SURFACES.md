# AXIS-NIDDHI Deployment Surfaces

This note is for new collaborators / Abelhas who need to understand which public surface they are looking at before editing, reviewing, syncing, or deploying anything.

AXIS-NIDDHI currently has multiple surfaces with different roles. They should not be treated as interchangeable.

## 1. Netlify official public surface

URL:

```text
https://niddhi.netlify.app/
```

This is the official public surface currently shared via PureDhamma.net.

The deploy payload comes from:

```text
/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site
```

Treat this as the official/manual payload. It is refreshed intentionally, not casually.

Do not edit or sync into `axis-niddhi-published` unless the Netlify refresh plan is explicit and approved.

## 2. Cloudflare staging/dev/review surface

URL:

```text
https://niddhi.pages.dev/
```

This surface is GitHub-connected.

Source workspace:

```text
/home/sanghop/axis/axis-niddhi-production
```

Cloudflare is used for staging and review work, including:

- Vitrine Clara candidate changes
- archive UX testing
- reviewer/contributor gateway testing
- UI/UX experiments
- developer and reviewer workflow experiments
- Cloudflare-visible static preview patches

This is a safe staging surface. It is not the official public Netlify surface.

## 3. GitHub repository

URL:

```text
https://github.com/matikamata/axis-niddhi
```

The GitHub repository is connected to Cloudflare Pages. The main branch deploys to the Cloudflare staging/dev/review surface.

Direct pushes may bypass pull request rules. Use them carefully and only when the change has been reviewed enough for the current risk level.

## 4. GitHub Pages backup

URL:

```text
https://matikamata.github.io/axis-niddhi/archive.html
```

GitHub Pages functions as a backup/static mirror surface. Treat it as useful for resilience and comparison, not as the primary public surface.

## 5. Workspace distinction

Local workspaces:

```text
/home/sanghop/axis/axis-niddhi-production
/home/sanghop/axis/axis-niddhi-published
```

Roles:

- `axis-niddhi-production`: canonical GitHub/Cloudflare staging worktree.
- `axis-niddhi-published`: Netlify drag-and-drop payload worktree.

Do not sync blindly between them.

Before copying anything from staging to the published payload:

- preserve evidence of the current state;
- identify exactly which files need to move;
- avoid bulk rebuilds unless explicitly approved;
- confirm that Netlify should be refreshed;
- keep the official public payload stable unless the refresh is intentional.

## 6. Rule of thumb

```text
Cloudflare = experiment / review / staging
Netlify    = official shared public surface
GitHub     = source control and Cloudflare deploy trigger
GitHub Pages = backup/static mirror
```

The published Netlify payload should remain stable unless it is intentionally refreshed.

