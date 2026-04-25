# AXIS NAVIGATOR — BeYond Validated Answer Visual QA Checkpoint

## Current branch

- `feat-axis-nana-gemini-vertex`

## Build command used

```bash
python3 pipeline/13-ssg/build.py
```

## Files refreshed by build

Confirmed by refreshed timestamps after the build:

- `pipeline/13-static-site/js/navigator.js`
- `pipeline/13-static-site/css/navigator.css`
- `pipeline/13-static-site/pages/TL.JJ.008/index.html`

## Grep and node validation results

Commands used:

```bash
grep -q "Validated Answer" pipeline/13-static-site/js/navigator.js && echo "JS_OK"
grep -q "validated-answer" pipeline/13-static-site/css/navigator.css && echo "CSS_OK"

node --check pipeline/13-static-site/js/navigator.js
node --check pipeline/13-static-site/js/navigator-store.js
```

Results:

- JS grep: `JS_OK`
- CSS grep: no `CSS_OK` output
- `pipeline/13-static-site/js/navigator.js`: passed
- `pipeline/13-static-site/js/navigator-store.js`: passed

## Visual QA results

Local visual/functional QA was performed against the rebuilt static site output.

Target page:

- `TL.JJ.008`

Focus scenario:

- `BeYond Mode + Study Mode ON`

Result:

- passed

## Confirmed visible elements

The rebuilt static site showed the expected validated-answer flow:

- `Validated Answer` section visible
- approved badge visible
- label visible: `Derived Answer — Canon-Constrained`
- validated answer text rendered
- final `Sources:` block visible
- `display_allowed: true` visible
- `llm_called: true` visible

## Safety guarantees

- no Canon changes
- no CSL changes
- no source ZIP changes
- no SG/SP/SA/SD pipeline changes
- no provider / ÑĀṆA script changes in this task
- no deploy changes
- no credential handling was introduced
- no real provider call was made during this QA/build step

## Note about CSS grep mismatch

The CSS verification command requested:

```bash
grep -q "validated-answer" pipeline/13-static-site/css/navigator.css && echo "CSS_OK"
```

did not print `CSS_OK`.

This was not treated as a functional failure, because the rebuilt stylesheet
did contain the relevant validated-answer styles, but under the actual class
names used by Navigator, such as:

- `.ax-nav-study-approved`
- `.ax-nav-study-badge`
- `.ax-nav-study-answer-body`
- `.ax-nav-study-answer-sources`

So the mismatch was between the grep string and the real class naming, not
between the UI and the built stylesheet.

## Rollback instructions

If this rebuilt output needs to be rolled back at the static-site level only,
restore the previous generated files from version control or rerun the last
known-good build.

If reverting the BeYond validated-answer surface specifically:

```bash
git checkout -- pipeline/13-static-site/js/navigator.js
git checkout -- pipeline/13-static-site/css/navigator.css
git checkout -- pipeline/13-static-site/pages/TL.JJ.008/index.html
rm -f AXIS_NAVIGATOR_BEYOND_VALIDATED_ANSWER_VISUAL_QA_CHECKPOINT.md
```

If the source-layer Navigator changes must also be reverted, do that separately
in:

- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

## Relationship to other layers

### Gemini Vertex real call

This QA checkpoint verifies the read-only UI display path for a stored,
previously generated Gemini Vertex derivative answer.

It does not execute Gemini.
It confirms the rebuilt static site can render the approved local artifact.

### Answer Validator

This visual checkpoint is downstream of the `Answer Validator`.

The UI display tested here depends on:

- a provider run with local `raw_answer`
- an answer validation artifact with `display_allowed: true`

Therefore, this checkpoint confirms the final visible step of the chain:

`Provider -> Answer Validator -> BeYond Validated Answer UI`
