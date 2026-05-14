# AXIS-NIDDHI NANA Local Bridge QA (2026-05-14)

## Purpose
Document the successful local visual QA of the end-to-end static integration between the NANA artifacts capsule, the NIDDHI SSG pipeline, and the Navigator frontend.

## Local Visual QA Evidence
Local servers correctly spun up and rendered the combined assets:
- NIDDHI lab archive: `http://127.0.0.1:8766/archive.html`
- NIDDHI static NANA manifest: `http://127.0.0.1:8766/assets/nana/manifest.json`
- Navigator demo: `http://127.0.0.1:8767/demo/`
- Navigator demo local NANA manifest: `http://127.0.0.1:8767/demo/assets/nana/manifest.json`

## Proven Flow
1. **axis-nana fixture** → 2. **axis-niddhi capsule** → 3. **build.py** → 4. **13-static-site/assets/nana** → 5. **HTTP local** → 6. **Navigator demo manifest read**

## What is Proven
- The static SSG pipeline cleanly integrates the NANA JSON artifacts into the `assets/nana` directory upon execution.
- The Navigator application logic perfectly decodes and routes the fetched static output JSON without requiring dynamic APIs.
- The workflow guarantees data immutability and exact byte-for-byte transmission through local endpoints.

## What is Not Proven
- Full execution across the production branch deployment action against live endpoints.
- Real-world interaction with non-fixture dynamically generated AI output (since all test inputs are `display_allowed: false`).

## Explicit Artifact Scope Note
The artifacts promoted during this QA wave are **fixture-only**. They are plumbing tests and mock data; they are strictly not doctrinal and not the output of a real LLM.

## Safety Checks Completed
- No API calls made.
- No provider execution triggered.
- No production repositories touched.
- No rescue repositories touched.
- No secrets found in served JSON outputs.

## Cleanup Performed
- Local `http.server` instances on ports 8766 and 8767 stopped safely.
- Generated `assets/nana` payload removed from SSG output.
- Untracked `demo/assets` symlink cleanly removed from Navigator workspace.
- Modified Git-tracked SSG internal caches (`build_state.json`, etc.) restored perfectly.

## Next Recommended Step
Prepare a controlled production-promotion plan only. No implementation yet.
