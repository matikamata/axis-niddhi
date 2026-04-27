# AXIS NIDDHI NANA Static Copy Hook
Date: 2026-04-26

## Overview
This document outlines the behavior of the NANA static artifact copy hook introduced in `build.py` (Wave 2c.4c). This hook is responsible for bridging NANA outputs into the static site payload.

## Paths
- **Source:** `pipeline/capsule/nana/`
- **Target:** `pipeline/13-static-site/assets/nana/`

## Rules and Safety Guarantees
- **JSON-only:** Only `.json` files are copied.
- **Fail-closed guard:** Files containing forbidden markers (such as `GOOGLE_APPLICATION_CREDENTIALS`, secret keys, or absolute `/home/` paths) are blocked and rejected.
- **No provider execution:** This step merely copies static JSON. It does not execute LLM models or run NANA core logic.
- **No API calls:** No external networks are contacted.
- **No browser credentials:** The frontend receives pure data; no credentials are leaked or injected.
- **Graceful no-op:** If the `pipeline/capsule/nana/` directory does not exist or has no JSON artifacts, the build logs it and continues safely without breaking the site.
- **No Navigator integration:** In this wave, we only place the artifacts in the target static directory. The frontend UI (Navigator) is not updated to fetch or display them yet.
