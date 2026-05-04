# FlagFix 017 — Print Green Line Decoration Standardization

**Status:** Open / tracked for future sprint  
**Priority:** Low–Medium  
**Area:** Print CSS / visual consistency / review PDFs  
**Observed page:** `https://niddhi.pages.dev/pages/TL.EE.003/`  
**Reference symptom:** Some printed essays show a short green line near the top of the printed page; other printed essays do not.

---

## 1. Problem statement

In print/PDF mode, some AXIS-NIDDHI pages display a small green horizontal line near the top of the first printed page. The line is visually pleasant and may even be desirable as a subtle AXIS-NIDDHI print accent, but its current behavior appears inconsistent.

The immediate concern is not that the green line exists. The concern is that it appears on some essays and not others, which creates the impression of accidental styling rather than intentional print design.

For a long-term review corpus, inconsistent visual markers can cause confusion:

- reviewers may wonder whether the green line signals a special status;
- printed PDFs may look like they came from different templates;
- small accidental differences accumulate and make the corpus feel less polished;
- future contributors may cargo-cult the behavior without knowing its source.

This should be tracked and standardized.

---

## 2. Current interpretation

The green line is likely caused by one of these sources:

1. **A screen CSS element leaking into print**  
   Example candidates: active tab underline, language selector state, reading progress indicator, section navigation marker, or decorative heading border.

2. **A per-page content structure difference**  
   Some essays begin with headings, accordions, quote blocks, or metadata structures that trigger a print-visible green border or accent; other essays do not.

3. **A print CSS rule that only matches certain DOM shapes**  
   A selector may be too narrow, so the decoration appears only when a specific element order exists.

4. **Browser print artifact from a fixed/sticky UI element**  
   A fixed header, progress bar, or hidden navigation item may be partially visible in Firefox/Chromium print preview.

The correct fix depends on finding the exact selector and element responsible.

---

## 3. Why this matters

AXIS-NIDDHI print/PDF output is becoming a review artifact, not merely a browser convenience. Once reviewers use PDFs for translation, grammar, Pāli, glossary, and doctrinal review, the layout becomes part of the trust layer.

A small visual inconsistency can be tolerated temporarily, but it should be classified:

- **intentional seal/decorative element**, or
- **accidental CSS leak**.

Unclassified visual artifacts should not become permanent.

---

## 4. Desired future behavior

Choose one of the following policies.

### Option A — Standardize the green line as a print accent

Create a deliberate print-only AXIS-NIDDHI accent line under the browser/page header area or above the printed title.

Suggested properties:

- appears on every printed essay;
- uses the AXIS green palette;
- has consistent width, thickness, and spacing;
- does not depend on page content;
- does not overlap browser-generated print headers;
- is documented in CSS as intentional.

Possible selector:

```css
@media print {
  .post-title::before {
    content: "";
    display: block;
    width: 6rem;
    border-top: 2pt solid var(--green-axiom, #138a36);
    margin: 0 auto 1.25rem auto;
  }
}
```

This would make the green line a deliberate, likable print identity marker.

### Option B — Remove it everywhere

If the line is an accidental leak from screen UI, hide the source element in print.

Possible targets to inspect:

```css
@media print {
  .reading-progress,
  .progress-bar,
  .language-toggle .active::after,
  .tab-active::after,
  .toc-toggle::before,
  .site-accent-line {
    display: none !important;
  }
}
```

This option is safer if the line is not semantically meaningful.

### Option C — Replace it with a full print seal style

Fold the green line into a broader print identity system:

- title centered;
- draft/review banner;
- color legend;
- canonical ID;
- source URL;
- optional top accent line;
- optional footer seal.

This is the most polished long-term option, but should be done only after the current print fixes stabilize.

---

## 5. Recommended policy

Recommended: **Option A, but only after confirming the current line is not hiding a bug.**

In other words:

1. First identify the current source of the inconsistent line.
2. If it is accidental, neutralize it.
3. Then add a deliberate print-only green accent line in one controlled place.

This preserves the good visual idea while eliminating accidental behavior.

---

## 6. Investigation checklist

Run these checks on pages that show the line and pages that do not.

### 6.1 Compare print DOM/CSS candidates

Inspect these classes/selectors in DevTools print emulation:

```text
reading-progress
progress
language
lang
active
tab
post-title
title-en
title-pt
content-block
section-heading
accordion
collapsible
toc
```

### 6.2 Search CSS for green borders or top bars

Suggested command:

```bash
grep -RniE "border-top|border-bottom|background|height:.*(2px|3px|4px)|green|--green|progress|active" \
  pipeline/13-ssg/static/css \
  pipeline/13-static-site/css \
  | sed -n '1,240p'
```

### 6.3 Print compare sample set

Use at least these pages:

```text
TL.EE.003  # observed with green line
TL.JJ.008  # prior print-review calibration page
TL.CC.007  # image sizing issue page
TL.DD.005  # YouTube print marker issue page
TL.BB.005  # glossary/title/audio placeholder issues
```

### 6.4 Verify no canonical/content change

This fix must remain CSS/JS/template-only. It must not modify CSL content, translations, glossary definitions, or canonical IDs.

---

## 7. Acceptance criteria

A future fix for this FlagFix is acceptable only if:

- every printed essay either consistently has the green line or consistently does not;
- the behavior is documented in the CSS comment;
- the line does not overlap browser-generated print headers;
- the line does not change source content or translation text;
- print/PDF output remains readable on A4;
- the review banner and color legend remain unaffected;
- screenshots/PDFs from at least 5 representative pages are checked.

---

## 8. Suggested GitHub Issue title

```text
#FlagFix_017: Standardize or remove inconsistent green line in printed PDFs
```

## 9. Suggested labels

```text
flagfix
print-css
visual-consistency
low-risk
needs-investigation
```

---

## 10. Notes for future contributors / Abelhas

This is not a doctrinal issue and does not block translation review. It is a polish and consistency issue.

However, AXIS-NIDDHI aims to produce artifacts that can be trusted and read far beyond the current sprint. A small green line that appears randomly is not yet a design language. A small green line that appears intentionally, consistently, and beautifully can become part of the AXIS-NIDDHI print identity.

Therefore: do not remove or preserve it blindly. First identify the source. Then decide whether it should become a controlled print seal.


REMARKS:
> 20260427_12h50:
Fui imprimir novamente e a linha sumiu, aí enviei essa mensagem:
[Peraí.... fui imprimir o documento de novo e a linha verde sumiu sem que eu tenha mudado qualquer configuração!

> o papel impresso tá com a linha verde! hahaha

> foi um bug? Se foi, talvez seja legal esse bug virar feature, porque ficou muito elegante!]

Resposta ChatGPT 5.5:
[Sim — **foi provavelmente bug/artefato de renderização do print preview**, não comportamento confiável.

Mas concordo 100%: **se no papel ficou elegante, vira feature candidata.**
Só não devemos depender do bug. O caminho correto é registrar no **#FlagFix_017** como:

> “A linha verde apareceu em uma impressão real, mas sumiu no preview sem mudança de configuração. Isso indica comportamento instável do motor de impressão/browser. Porém, o resultado visual foi positivo e pode inspirar uma padronização intencional.”

Minha recomendação arquitetural:

**Não mexer agora no CSS.**
Deixar como FlagFix/design debt, porque estamos numa fase de revisão e não queremos transformar detalhe estético em regressão de impressão.

Para o futuro, eu proporia uma feature deliberada:

### PRINT SEAL ACCENT

Uma linha fina, verde, estável e intencional no topo da primeira página impressa, como “selo visual AXIS-NIDDHI”.

Exemplo conceitual:

```css
@media print {
  .title-pt,
  .title-en {
    border-top: 2pt solid var(--green-axiom);
    padding-top: 0.6rem;
  }
}
```

Mas isso precisa ser testado em:

```text
Firefox print preview
Firefox PDF
Firefox papel real
Chrome/Chromium PDF
Cloudflare production
páginas curtas
páginas longas
páginas com banner
páginas com imagem/vídeo
```

Resumo crica:

| Item                      | Decisão             |
| ------------------------- | ------------------- |
| Linha verde atual         | Não confiar         |
| Resultado visual          | Bom                 |
| Virar feature?            | Sim, candidata      |
| Corrigir agora?           | Não                 |
| Registrar no #FlagFix_017 | Sim                 |
| Nome sugerido             | `PRINT SEAL ACCENT` |

Frase para adicionar no documento:

```md
Observed anomaly: in one real paper print, a thin green line appeared near the top of the printed page, producing an elegant visual “seal” effect. The same line disappeared from print preview without any configuration change, so this must be treated as an unstable browser/print rendering artifact, not a reliable feature. However, the visual result is desirable and should be considered as inspiration for a future intentional PRINT SEAL ACCENT rule.
```

Esse é exatamente o tipo de “bug bom” que merece virar feature — mas só depois de virar CSS determinístico.
]
