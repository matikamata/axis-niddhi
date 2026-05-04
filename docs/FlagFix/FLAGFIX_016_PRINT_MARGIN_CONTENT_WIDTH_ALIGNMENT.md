# FlagFix_016 — Print Margins, Content Width, and Optical Centering

**Status:** tracked for future fix  
**Priority:** medium  
**Scope:** print/PDF rendering only  
**Observed page:** `https://niddhi.pages.dev/pages/TL.JJ.008/`  
**Observed symptom:** printed content appears optically shifted left; right side has excess empty space or the text block does not feel centered between printable margins.

---

## 1. Problem Statement

During print/PDF review, the readable article column does not appear proportionally centered on the page. Even when browser print margins are adjusted manually, the content block still feels left-biased.

A useful diagnostic test was performed by reducing print scale to **50%**. At that scale, the imbalance becomes obvious: the rendered AXIS-NIDDHI article area has an internal layout width/offset issue, not merely a browser margin issue.

This is not a canonical content issue. It is a print layout issue.

---

## 2. Why This Matters

For normal web reading, the current layout is acceptable and visually pleasant.

For printed/PDF review copies, however, margin balance matters because reviewers use the PDF as a working artifact:

- handwritten notes may be added;
- pages may be archived;
- documents may be shared with collaborators;
- apparent asymmetry makes the output feel less polished;
- inconsistent margins reduce the “likable” quality expected from long-term AXIS-NIDDHI review documents.

The goal is not only functional printing. The goal is a review PDF that feels intentionally typeset.

---

## 3. Current Hypothesis

The problem is likely caused by one or more of the following:

1. A screen-oriented container width or max-width being reused in print.
2. Left/right padding or margins inherited from the online layout.
3. A print `body`, `main`, `.container`, `.content-block`, or article rule that does not reset width cleanly.
4. Browser print headers/footers and custom print margins making the imbalance more visible.
5. The article column being centered relative to a web layout container rather than the physical printable page.

This should be investigated with computed CSS in print emulation.

---

## 4. Acceptance Criteria

A future fix should satisfy all of the following:

- Printed article content is visually centered between left and right page margins.
- The title, review banner, body text, YouTube marker boxes, images, and footer/seal use the same printable column.
- No horizontal clipping occurs.
- No content touches the page edge.
- Output remains readable on A4 and Letter.
- The online/screen layout remains unchanged.
- No CSL, translation, or canonical source files are modified.

---

## 5. Recommended Technical Direction

Create a print-specific content column rule instead of relying on the screen layout.

Candidate direction:

```css
@media print {
  body {
    margin: 0 !important;
  }

  main,
  .container,
  .page-container,
  article.content-block {
    width: 100% !important;
    max-width: none !important;
    margin-left: auto !important;
    margin-right: auto !important;
    box-sizing: border-box !important;
  }

  article.content-block {
    max-width: 170mm !important;
  }
}
```

The exact selectors must be verified against the current template/CSS. The above is only a direction, not a final patch.

A safer production patch should be surgical and target only the actual print container used by generated post pages.

---

## 6. Important Caution

Do **not** solve this by asking reviewers to manually adjust browser margins.

Browser print settings vary by:

- Firefox vs Chrome/Chromium;
- Linux vs macOS vs Windows;
- A4 vs Letter;
- default header/footer settings;
- physical printer drivers.

AXIS-NIDDHI should provide a sane print layout by default. Manual browser settings may still be useful, but they should not be required to make the document look balanced.

---

## 7. Suggested Investigation Commands

Run a local server:

```bash
python3 -m http.server -d pipeline/13-static-site 8080
```

Open:

```text
http://localhost:8080/pages/TL.JJ.008/
```

Then test print preview in browser with:

- A4
- scale 100%
- scale 80%
- scale 50%
- default margins
- custom margins

Also inspect the print CSS sections in:

```text
pipeline/13-ssg/static/css/style.css
pipeline/13-static-site/css/style.css
```

Search for likely layout selectors:

```bash
grep -nE '@media print|content-block|main|container|article|body|page'   pipeline/13-ssg/static/css/style.css   pipeline/13-static-site/css/style.css
```

---

## 8. Recommended Future Patch Shape

Preferred patch scope:

```text
pipeline/13-ssg/static/css/style.css
pipeline/13-static-site/css/style.css
```

Avoid JS unless absolutely necessary.

Do not touch:

```text
pipeline/09-csl/
pipeline/03-translations/
metadata canonical files
source content
```

If the static-site mirror is ignored by `.gitignore`, either:

1. patch only the source SSG asset and rebuild the static site, or  
2. explicitly force-add mirrored assets only when that is the established branch policy.

---

## 9. Reviewer Note

This issue is visual, not doctrinal and not translational.

The content remains traceable to PureDhamma.net and the AXIS-NIDDHI canonical pipeline. The defect is in the PDF/print presentation layer.

It is safe to continue review work while this remains open, but it should be fixed before considering the PDF output “presentation-grade.”

---

## 10. GitHub Issue Draft

**Title:** `#FlagFix_016 — Print layout content column appears left-biased`

**Body:**

Printed/PDF review copies appear optically shifted left. When print scale is reduced to 50%, the imbalance becomes clear: the content column is not proportionally centered between printable margins.

This appears to be a print CSS/layout issue, not a canonical content issue.

Tasks:

- identify the active print container selectors;
- normalize printable column width;
- ensure title, banner, body, images, video markers, and seal/footer align to the same column;
- preserve online layout;
- avoid CSL/content/translation changes.

Acceptance:

- print output looks centered on A4 and Letter;
- no clipping;
- no horizontal overflow;
- no screen layout regression.
