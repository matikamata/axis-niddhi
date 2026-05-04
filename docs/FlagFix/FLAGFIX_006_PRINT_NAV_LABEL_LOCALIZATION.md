# FlagFix 006 — Print Navigation Label Localization

**Status:** Deferred / documented for future surgical fix  
**Priority:** Low  
**Area:** Static site template + print output  
**Observed by:** Vayo review  
**Scope:** AXIS-NIDDHI printed/PDF review copies

---

## 1. Problem Summary

In some printed/PDF review copies, the post navigation block at the end of the page appears with English labels:

- `From:`
- `To:`

On the live site, the visible navigation links may already appear correctly in Portuguese, such as:

- `Anterior`
- `Próximo`

This means the issue is not necessarily in the translated article body. It is likely in a template-rendered navigation component or print-specific label block that is outside the DeepL translation path.

---

## 2. Why This Matters

This is a low-severity issue because it does not affect doctrinal content, glossary terms, audio markers, citations, or canonical IDs.

However, it affects polish and review clarity. A printed Portuguese review copy should not unexpectedly end with untranslated English interface labels, especially when the rest of the document is being reviewed as a pt-BR artifact.

For long-term archival quality, even small interface fragments should be intentional:

- either localized into Portuguese;
- or explicitly marked as non-translatable UI metadata;
- or hidden from print if not useful for review.

---

## 3. Technical Hypothesis

The labels `From:` and `To:` are likely emitted by a static-site template or navigation renderer rather than by translated CSL content.

Probable areas to inspect later:

```text
pipeline/13-ssg/templates/
pipeline/13-ssg/src/
pipeline/13-static-site/
```

Search terms:

```bash
grep -Rni "From:\|To:\|Previous\|Next\|Anterior\|Próximo" \
  pipeline/13-ssg \
  pipeline/13-static-site \
  | sed -n '1,200p'
```

The issue may appear only in print because screen CSS and print CSS expose different blocks.

---

## 4. Non-Goals

This FlagFix should not modify:

- canonical CSL content;
- translated article body;
- PureDhamma source text;
- glossary terms;
- Pāli/Pāḷi terminology;
- audio term logic;
- global link color rules.

This is a UI/template localization issue only.

---

## 5. Candidate Fix Options

### Option A — Localize the template labels

Replace template labels:

```text
From: → Anterior:
To:   → Próximo:
```

or preferably:

```text
Previous / Anterior
Next / Próximo
```

This is the cleanest solution if the block is intended to be visible in printed Portuguese review copies.

### Option B — Use language-aware labels

If the template knows the current language, render labels conditionally:

```text
en-US: From / To, or Previous / Next
pt-BR: Anterior / Próximo
```

This is better long-term, but only if the current template architecture already exposes language context safely.

### Option C — Mark navigation as non-translatable

If the navigation block must remain stable UI metadata, add:

```html
translate="no"
```

This prevents translation engines from partially altering navigation labels later. However, this does not solve the Portuguese review-copy polish issue by itself.

### Option D — Hide the navigation block in print

If the block is not useful for PDF review copies, hide it under `@media print`.

This is the most conservative visual fix, but it may reduce traceability between adjacent posts.

---

## 6. Recommended Future Direction

Preferred future fix:

1. Locate the exact template or renderer emitting `From:` / `To:`.
2. Confirm whether it appears only in print or also in hidden screen DOM.
3. Replace it with language-aware labels, preserving deterministic output.
4. Keep the patch surgical and limited to template/UI files.
5. Add a small grep-based validation command.

Recommended labels for pt-BR print review:

```text
Anterior:
Próximo:
```

or, for bilingual archival clarity:

```text
Previous / Anterior:
Next / Próximo:
```

For current AXIS-NIDDHI review copies, bilingual labels may be safest because the archive still serves both English and Portuguese readers.

---

## 7. Acceptance Criteria

A future patch should pass:

```bash
git diff --name-only
```

Expected touched files should be limited to template/CSS/JS output layers, not CSL source layers.

Suggested validation:

```bash
grep -Rni "From:\|To:" \
  pipeline/13-ssg \
  pipeline/13-static-site \
  | sed -n '1,120p'
```

Expected result after fix:

- no unintended `From:` / `To:` labels in Portuguese print navigation;
- no change to article content;
- no change to canonical IDs;
- no change to glossary/audio term styling.

---

## 8. Preservation Note

This issue is not a blocker for continuing translation review.

It is a small interface-localization artifact, not a content-integrity failure. The doctrinal source remains PureDhamma.net, and AXIS-NIDDHI can safely continue review work while this remains documented as a future polish fix.

