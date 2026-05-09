# FLAGFIX_027 — Audio Playback Fails on iPad/iMac Safari-Like Environments

## Status

`DEFERRED / KNOWN DEPLOYMENT-SURFACE LIMITATION`

## Context

After the translated showcase build was merged and deployed, the site appears healthy on Cloudflare Pages.

Observed production page sample:

```text
https://niddhi.pages.dev/pages/TL.EE.003/
```

The current showcase was locally validated and then published through PR `#112` / checkpoint:

```text
checkpoint/showcase-translated-static-preview-20260509
```

A new device-specific issue was observed after publication:

- audio works in Brave browser;
- audio does not work on iPad;
- audio does not work on iMac;
- issue should be investigated without touching production or rerunning the full pipeline first.

## Issue

Some pronunciation/audio assets appear playable in Brave, but fail on Apple devices or Safari-like browser environments.

Possible root-cause categories:

- Safari/iOS audio behavior;
- MIME type served for `.mp3`;
- HTTP range request behavior;
- Cloudflare Pages headers;
- externalized large audio files;
- mixed internal/external audio references;
- filename encoding/case sensitivity;
- JavaScript audio initialization behavior;
- iOS user-gesture requirements;
- service worker or cache interaction.

Do not assume the root cause before testing.

## Guardrails

This is a diagnostic FlagFix only.

Do **not**:

- rerun the full pipeline;
- edit CSL;
- edit `09-csl`;
- edit `03-translations`;
- edit translation metadata;
- edit `Translation_Control_Center.csv`;
- edit production directly;
- mass rewrite audio references;
- change Cloudflare settings blindly;
- commit static-site output without explicit approval;
- introduce UI redesign.

Allowed initial scope:

- read-only inspection;
- browser/device reproduction notes;
- targeted header/MIME checks;
- targeted static-site audio reference audit;
- small docs or review report if needed;
- a minimal patch proposal only after evidence.

## Primary Reproduction Targets

Check audio behavior on:

```text
https://niddhi.pages.dev/pages/TL.BB.004/
https://niddhi.pages.dev/pages/TL.JJ.008/
https://niddhi.pages.dev/pages/TL.EE.003/
https://niddhi.pages.dev/pages/BD.AA.007/
```

Known local audio examples previously requested successfully in local preview:

```text
/assets/audio/en-US/sutta.mp3
/assets/audio/en-US/Nibbana.mp3
/assets/audio/en-US/bhavana.mp3
/pronunciation_manifest.json
```

## Read-Only Investigation Plan

### 1. Confirm repository and branch

```bash
cd /home/sanghop/axis/axis-niddhi-production

pwd
git rev-parse --show-toplevel
git branch --show-current
git status -sb
git log --oneline -5
```

Expected:

- path is `/home/sanghop/axis/axis-niddhi-production`;
- branch is `main`;
- worktree is clean;
- latest main includes PR `#112` merge or later.

Do not edit yet.

### 2. Inspect generated audio references

```bash
grep -RIn --include='*.html' --include='*.json' --include='*.js' \
  -E 'pronunciation_manifest|assets/audio|\.mp3|audio' \
  pipeline/13-static-site pipeline/13-ssg/static \
  | head -200
```

Inspect manifest shape:

```bash
python3 - <<'PY'
import json
from pathlib import Path

p = Path("pipeline/13-static-site/pronunciation_manifest.json")
print("exists:", p.exists(), "size:", p.stat().st_size if p.exists() else None)
if p.exists():
    data = json.loads(p.read_text(encoding="utf-8"))
    print("type:", type(data).__name__)
    if isinstance(data, dict):
        print("top keys:", list(data)[:20])
    elif isinstance(data, list):
        print("rows:", len(data))
        print("sample:", data[:3])
PY
```

### 3. Check local asset properties

```bash
find pipeline/13-static-site/assets/audio -type f -name '*.mp3' | wc -l
find pipeline/13-static-site/assets/audio -type f -name '*.mp3' | head -30
du -ah pipeline/13-static-site/assets/audio | sort -h | tail -30
```

Check whether any referenced MP3 is missing locally:

```bash
python3 - <<'PY'
import re
from pathlib import Path

root = Path("pipeline/13-static-site")
refs = set()

for path in root.rglob("*"):
    if path.suffix.lower() not in {".html", ".json", ".js"}:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for m in re.findall(r'["\']([^"\']+\.mp3(?:\?[^"\']*)?)["\']', text):
        refs.add(m.split("?")[0])

missing = []
external = []
for ref in sorted(refs):
    if ref.startswith(("http://", "https://")):
        external.append(ref)
    elif ref.startswith("/"):
        if not (root / ref.lstrip("/")).exists():
            missing.append(ref)
    else:
        if not (root / ref).exists():
            missing.append(ref)

print("mp3 refs:", len(refs))
print("external:", len(external))
print("missing local:", len(missing))
print("\nExternal sample:")
for x in external[:20]:
    print(x)
print("\nMissing local sample:")
for x in missing[:50]:
    print(x)
PY
```

### 4. Check production headers for MP3 files

```bash
curl -I https://niddhi.pages.dev/assets/audio/en-US/sutta.mp3
curl -I https://niddhi.pages.dev/assets/audio/en-US/Nibbana.mp3
curl -I https://niddhi.pages.dev/assets/audio/en-US/bhavana.mp3

curl -I -H "Range: bytes=0-1" https://niddhi.pages.dev/assets/audio/en-US/sutta.mp3
curl -I -H "Range: bytes=0-1" https://niddhi.pages.dev/assets/audio/en-US/Nibbana.mp3
curl -I -H "Range: bytes=0-1" https://niddhi.pages.dev/assets/audio/en-US/bhavana.mp3
```

Record:

- `content-type`;
- `accept-ranges`;
- response code for range request;
- `content-length`;
- cache headers;
- redirects, if any.

Safari/iOS audio playback is often sensitive to correct MIME/range behavior.

### 5. Check externalized audio URLs

From build logs, some audio files were externalized due to size:

```text
Audio: 463 copied, 19 externalized (>25 MiB)
Audio refs externalized: 22 substitutions in 16 pages
Missing local audio refs externalized: 1 substitution in 1 pages
```

Find externalized audio references:

```bash
grep -RIn --include='*.html' --include='*.json' \
  -E 'https?://.*\.mp3' \
  pipeline/13-static-site \
  | head -100
```

Then test a few externalized URLs with:

```bash
curl -I '<URL>'
curl -I -H "Range: bytes=0-1" '<URL>'
```

Do not change anything yet.

### 6. Device-side notes requested from human

Ask the human tester to capture:

- exact device: iPad model/iOS version, iMac/macOS version;
- browser: Safari, Brave, Chrome, Firefox;
- whether tapping the audio button does nothing, shows error, or loads forever;
- whether browser console shows errors on iMac;
- whether the failing audio is local `/assets/audio/...` or external `https://puredhamma.net/...`.

## Decision Tree

### If MP3 headers are wrong

## Resolution / Current Decision

Status: deferred / known deployment-surface limitation.

The current evidence does not support a corpus, CSL, DeepL, translation metadata, or JavaScript player bug as the primary cause.

The issue is currently classified as a deployment-surface limitation:

- local small audio assets exist and work in local/showcase validation;
- Netlify full-folder deployment serves local MP3 assets correctly;
- Cloudflare GitHub-linked deployment currently does not publish the local MP3 asset set under `pipeline/13-static-site/assets/audio/**`;
- Apple/Safari-like environments fail because those local audio URLs return HTML/fallback behavior rather than `audio/mpeg`.

This record preserves the existing audio policy:

- local small pronunciation/audio assets remain desirable;
- only audio files larger than 25 MiB should be externalized by policy;
- do not externalize all pronunciation/audio charm assets merely to satisfy the current Cloudflare GitHub-linked deployment surface.

Operational decision for now:

- Netlify full-folder deploy remains the current audio-complete showcase path;
- GitHub repository + GitHub Pages backup remain acceptable as repository/reference surfaces;
- Cloudflare GitHub-linked deployment may remain audio-incomplete until a future deploy-asset strategy is explicitly approved.

This issue is therefore:

- not a blocker for the next DeepL batch;
- not a reason to rewrite player logic;
- not a reason to touch CSL, `09-csl`, `03-translations`, translation metadata, or `build.py` right now.

Future work, if approved later, should focus on deploy/publication strategy only:

- publish local small audio assets on a deployment surface that truly ships the full `pipeline/13-static-site` folder;
- preserve the current `>25 MiB` externalization rule;
- validate MIME and range behavior on Apple/Safari devices after any approved deploy-surface fix.

If Cloudflare serves `.mp3` with wrong or missing `content-type`, propose a minimal `_headers` file or Cloudflare Pages header config.

Candidate:

```text
/assets/audio/*.mp3
  Content-Type: audio/mpeg
  Accept-Ranges: bytes
```

Do not implement until confirmed.

### If range requests fail

If `Range: bytes=0-1` does not return partial content or behaves inconsistently, investigate Cloudflare Pages/static serving behavior and whether the asset path or compression is interfering.

### If only externalized files fail

If local `/assets/audio/...` files work but externalized `puredhamma.net` files fail, isolate as external-host/CORS/range/hotlink behavior.

Possible future fix:

- keep externalization for size but add visible fallback link;
- or move large audio to a controlled object storage/CDN later;
- or document that large external audio is non-guaranteed on Apple clients.

### If JS gesture handling fails

If headers are fine but iOS fails only through custom UI, inspect `pipeline/13-ssg/static/js/main.js` and generated HTML audio controls.

Potential issue:

- audio playback must be triggered directly by a user gesture on iOS;
- async fetch/init before `.play()` may break gesture trust;
- custom button may need to expose native `<audio controls>` or avoid programmatic playback.

### If native `<audio controls>` works but custom button fails

Recommend minimal JS patch, not corpus or pipeline patch.

## Expected Output from CodeX

Return a read-only report with:

```text
1. repo path / branch / status
2. exact pages tested
3. exact audio URLs tested
4. local vs external audio classification
5. production header results
6. range request results
7. device/browser hypothesis
8. recommended minimal patch, or no-action
9. files that would be touched if patch is approved
10. files explicitly out of scope
```

## Success Criteria

Before any patch:

- root cause category identified;
- at least one failing Apple/Safari case reproduced or strongly inferred;
- at least one working Brave/local case compared;
- patch scope is minimal and reversible.

After any future patch:

- Brave still works;
- iPad/iMac audio works or has graceful fallback;
- no raw shortcode regression;
- no translation/corpus changes;
- no full pipeline rerun required unless explicitly approved.
