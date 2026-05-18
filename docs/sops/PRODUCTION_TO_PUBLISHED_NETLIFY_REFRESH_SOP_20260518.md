# SOP: Production to Published to Official Netlify Refresh

**Status:** SOP only. Netlify refresh still requires explicit human approval before execution.
Related governance document:
- `docs/NETLIFY_REFRESH_PLAN_20260518.md`

## 0. Principle

`axis-niddhi-production` is the GitHub/Cloudflare work surface.

`axis-niddhi-published` is the manual payload for the official Netlify surface.

Migration must never be a blind sync. The Operator copies only files that were previously approved and visually reviewed on Cloudflare.

`<AXIS_ROOT>` refers to the local AXIS workspace root. On the current maintainer machine this is `/home/sanghop/axis`, but SOPs should avoid relying on one machine-specific path.

## 1. Confirm clean production state

```bash
cd <AXIS_ROOT>/axis-niddhi-production

git status -sb
git log --oneline -n 8
```

Expected:

```text
## main...origin/main
```

If there are modified or untracked files, stop and decide before continuing.

## 2. Confirm Cloudflare is approved

Open and review:

```text
https://niddhi.pages.dev/
https://niddhi.pages.dev/welcome
https://niddhi.pages.dev/contribute
https://niddhi.pages.dev/archive
```

Verify:

- `/` does not enter a redirect loop.
- `welcome` opens correctly.
- `contribute` opens correctly.
- `archive` opens correctly.
- Main links work.
- Language buttons work.
- GitHub links open in a new tab.
- Internal links stay in the same tab.

## 3. Create checkpoint before migration

```bash
cd <AXIS_ROOT>/axis-niddhi-production

git tag -a checkpoint/pre-netlify-refresh-YYYYMMDD \
  -m "Checkpoint: production state approved before Netlify refresh"

git push origin checkpoint/pre-netlify-refresh-YYYYMMDD
```

Replace `YYYYMMDD` with the real date.

## 4. Back up current published payload

```bash
mkdir -p <AXIS_ROOT>/_netlify_refresh_backups

cp -a \
  <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site \
  <AXIS_ROOT>/_netlify_refresh_backups/13-static-site-before-refresh-YYYYMMDD-HHMM
```

Example:

```bash
cp -a \
  <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site \
  <AXIS_ROOT>/_netlify_refresh_backups/13-static-site-before-refresh-20260518-1530
```

## 5. Define approved files to copy

Probable candidates for this phase:

```text
pipeline/13-static-site/_redirects
pipeline/13-static-site/welcome.html
pipeline/13-static-site/contribute.html
pipeline/13-static-site/archive.html
pipeline/13-static-site/css/style.css
pipeline/13-static-site/css/typography-pro.css
pipeline/13-static-site/js/main.js
```

Important: do not copy the whole directory automatically without approval.

## 6. Dry-run the copy

Root files:

```bash
rsync -av --dry-run \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/_redirects \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/welcome.html \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/contribute.html \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/archive.html \
  <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site/
```

CSS:

```bash
rsync -av --dry-run \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/css/style.css \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/css/typography-pro.css \
  <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site/css/
```

JS:

```bash
rsync -av --dry-run \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/js/main.js \
  <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site/js/
```

If the dry-run shows anything unexpected, stop.

## 7. Execute real copy

Only after dry-run approval:

```bash
rsync -av \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/_redirects \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/welcome.html \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/contribute.html \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/archive.html \
  <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site/
```

```bash
rsync -av \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/css/style.css \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/css/typography-pro.css \
  <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site/css/
```

```bash
rsync -av \
  <AXIS_ROOT>/axis-niddhi-production/pipeline/13-static-site/js/main.js \
  <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site/js/
```

## 8. Test published locally

```bash
cd <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site

python3 -m http.server 8788
```

Open:

```text
http://127.0.0.1:8788/welcome.html
http://127.0.0.1:8788/contribute.html
http://127.0.0.1:8788/archive.html
```

Note: `python3 -m http.server` does not interpret `_redirects`, so `/` may not exactly simulate Netlify or Cloudflare routing.

## 9. Checklist before Netlify drag-and-drop

Confirm locally:

- `welcome.html` opens.
- `contribute.html` opens.
- `archive.html` opens.
- CSS loaded.
- JS loaded.
- Buttons work.
- No `localhost` or `127.0.0.1` links.
- No visible `<AXIS_ROOT>` or machine-local paths in HTML.
- GitHub links open correctly.
- Internal links are correct.

Useful command:

```bash
grep -R "localhost\|127.0.0.1\|/home/sanghop\|<AXIS_ROOT>" \
  <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site \
  --exclude-dir=assets \
  --exclude-dir=pages
```

## 10. Publish to Netlify

Drag and drop this folder:

```text
<AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site
```

to the official Netlify surface:

```text
https://niddhi.netlify.app/
```

## 11. Post-publication verification

Open:

```text
https://niddhi.netlify.app/
https://niddhi.netlify.app/welcome
https://niddhi.netlify.app/welcome.html
https://niddhi.netlify.app/contribute
https://niddhi.netlify.app/contribute.html
https://niddhi.netlify.app/archive
```

Verify:

- no redirect loop;
- no 404;
- no unexpected old page;
- `contribute` is correct;
- `archive` is correct;
- main links work.

## 12. Create post-Netlify checkpoint

In `axis-niddhi-production`:

```bash
cd <AXIS_ROOT>/axis-niddhi-production

git tag -a checkpoint/netlify-refresh-published-YYYYMMDD \
  -m "Checkpoint: approved Cloudflare staging payload published to official Netlify surface"

git push origin checkpoint/netlify-refresh-published-YYYYMMDD
```

Optionally create an evidence document:

```text
docs/checkpoints/NETLIFY_REFRESH_EVIDENCE_YYYYMMDD.md
```

Include:

- date/time;
- files copied;
- backup created;
- URLs tested;
- result;
- tag created.

## 13. Rollback

If something goes wrong on Netlify:

1. Restore from backup:

   ```bash
   rm -rf <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site

   cp -a \
     <AXIS_ROOT>/_netlify_refresh_backups/13-static-site-before-refresh-YYYYMMDD-HHMM \
     <AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site
   ```

2. Re-upload the restored folder to Netlify by drag-and-drop.

3. Record the rollback in a checkpoint document.

## Golden rule

```text
Cloudflare proves.
Production tracks.
Published packages.
Netlify publishes.
```

Never do:

```text
production -> published
```

without:

```text
backup + approved file list + local test + human approval
```
