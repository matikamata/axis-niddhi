# FlagFix_019 — Print Previous/Next Navigation Compaction and Box Design

**Status:** tracked for future implementation  
**Severity:** Low to Medium  
**Surface:** print/PDF stylesheet and post navigation template  
**Scope:** AXIS-NIDDHI static site review PDFs  
**Observed on:** printed/PDF review output near the final page of essays

---

## 1. Problem Summary

In printed/PDF review copies, the navigation block currently rendered as:

- `From: <previous post>`
- `To: <next post>`

appears too far below the final content of the essay. This creates excessive vertical whitespace and can push navigation metadata onto an otherwise unnecessary extra printed page.

On the live website, the same navigation concept is visually represented with clean boxed navigation cards. In print mode, however, the navigation is reduced to a plain text block, visually weaker and spatially inefficient.

This is not a canonical content issue. It is a print-layout and template-rendering issue.

---

## 2. Current Symptoms

The print/PDF output shows:

1. A large gap between the final paragraph/link of the essay and the `From / To` navigation block.
2. The `From / To` labels rendered as plain text rather than a structured box.
3. The block consumes space inefficiently near the end of the document.
4. The print version diverges aesthetically from the online page, where previous/next navigation appears as boxes.
5. The English labels `From / To` remain part of the print surface, which overlaps with #FlagFix_006.

---

## 3. Why This Matters

For one or two pages, this looks minor. Across hundreds of essays, it becomes meaningful:

- wastes paper in review printouts;
- interrupts the reading/review flow;
- makes final pages look unfinished or mechanically generated;
- increases cognitive friction for reviewers;
- weakens the “likable” long-term presentation standard of AXIS-NIDDHI.

The goal is not decorative polish only. The goal is to make printed review copies feel intentional, compact, traceable, and dignified.

---

## 4. Desired Future Behavior

In print mode, the previous/next navigation should be compact and visually structured.

Preferred behavior:

- reduce the vertical gap before the navigation block;
- render previous/next links inside a simple bordered or lightly shaded box;
- keep the design grayscale-friendly for physical printing;
- make the navigation look like a deliberate review/reference component;
- avoid consuming an additional sheet unless genuinely necessary;
- localize or neutralize the labels according to the page language.

Possible label options:

```text
Previous / Anterior: <title>
Next / Próximo: <title>
```

or, if the page is printed in Portuguese-only mode:

```text
Anterior: <title>
Próximo: <title>
```

For archival neutrality, another option is:

```text
Navigation / Navegação
Previous / Anterior: ...
Next / Próximo: ...
```

---

## 5. Suggested Print Design

A compact print-only block could use:

- thin gray border;
- small caps or monospace label;
- subtle gray text for labels;
- normal readable serif/sans title links;
- no large top margin;
- no oversized empty previous/next boxes.

Conceptual layout:

```text
┌────────────────────────────────────────────────────┐
│ NAVIGATION / NAVEGAÇÃO                             │
│ Previous / Anterior: Ten Immoral Actions Dasa Akusala
│ Next / Próximo: The Five Precepts What The Buddha Meant By Them
└────────────────────────────────────────────────────┘
```

This would visually match the DRAFT/RASCUNHO traceability block style without competing with it.

---

## 6. Likely Technical Cause

The website likely has two different presentation paths:

1. **Screen mode:** previous/next navigation is rendered as card-like boxes.
2. **Print mode:** CSS hides or overrides the visual navigation cards and exposes a simplified text fallback such as `From / To`.

This suggests the issue is probably in one or more of:

- `pipeline/13-ssg/templates/post.html`
- `pipeline/13-ssg/static/css/style.css`
- mirrored generated assets under `pipeline/13-static-site/css/style.css`
- possibly a print-specific section inside `@media print`

This should be investigated before patching.

---

## 7. Relationship to Other FlagFix Items

This overlaps with:

- **#FlagFix_006** — localization of `From / To` labels in print mode.
- **#FlagFix_016** — print margin/content width alignment.
- **#FlagFix_018** — grayscale typography and box design for print review banners.

Recommendation: solve #FlagFix_019 after or together with #FlagFix_006 and #FlagFix_018, because all three touch print-only review typography and navigation semantics.

---

## 8. Non-Goals

This FlagFix should not:

- edit canonical CSL content;
- change essay ordering logic;
- alter the actual previous/next relationship;
- modify translated article body text;
- introduce JavaScript-dependent behavior for print if a pure template/CSS fix is enough;
- create a new navigation system.

This is a print presentation fix only.

---

## 9. Suggested Implementation Strategy

### Phase 1 — Inspect

Search for current navigation selectors and print rules:

```bash
grep -Rni "From:\|To:\|previous\|next\|prev\|post-nav\|navigation" \
  pipeline/13-ssg/templates \
  pipeline/13-ssg/static/css/style.css \
  pipeline/13-static-site/css/style.css \
  | sed -n '1,220p'
```

Identify whether `From / To` is generated by:

- template text;
- CSS pseudo-content;
- JavaScript;
- a fallback print-only block.

### Phase 2 — Decide

Choose one canonical print strategy:

1. reuse the screen navigation cards with print-friendly CSS; or
2. hide the screen cards and add a compact print-only navigation seal.

The second option is likely cleaner for paper output.

### Phase 3 — Patch

Implement print-only CSS such as:

```css
@media print {
  .post-navigation,
  .prev-next-nav {
    margin-top: 1rem !important;
    padding-top: 0 !important;
    page-break-inside: avoid;
  }

  .print-nav-box {
    display: block !important;
    border: 1pt solid #777;
    padding: 0.75rem 1rem;
    margin: 1rem 0 0 0;
    font-size: 0.85rem;
    color: #555;
    overflow-wrap: anywhere;
  }
}
```

Exact selectors must be confirmed from the current template.

### Phase 4 — Validate

Test with at least:

- a short essay that currently prints navigation on the last page;
- a medium essay;
- one essay with both previous and next links;
- one essay with only previous or only next;
- Portuguese print mode;
- English print mode if still supported.

---

## 10. Acceptance Criteria

A future fix is acceptable only if:

- the `From / To` block no longer floats far below the final content;
- the navigation uses a compact box or similarly deliberate visual design;
- it does not create unnecessary extra pages;
- labels are localized or bilingual by design;
- real links remain visible in PDF output;
- print output remains grayscale-friendly;
- no canonical content files are touched;
- no translation/content edits are introduced.

---

## 11. Recommended GitHub Issue Title

```text
#FlagFix_019: Compact and redesign previous/next navigation in print/PDF output
```

Suggested labels:

- `flagfix`
- `print`
- `ux`
- `low-medium`
- `static-site`
- `review-pdf`

---

## 12. Human Note

This is exactly the kind of “small” detail that separates an automatically generated archive from a carefully preserved study edition.

The current output works, but it does not yet feel inevitable.

For a project intended to remain useful for future reviewers, translators, and preservers, the final page of each printed essay should close with the same dignity as the first page begins.
