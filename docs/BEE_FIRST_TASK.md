# Bee First Task / Primeira Tarefa da Abelha

This note is for new collaborators — Abelhas — arriving for the first time: developers, reviewers, translators, careful readers, and friends of friends who want to help but do not yet understand the whole AXIS-NIDDHI ecosystem.

You do not need to understand the entire project before making a useful contribution.

The first contribution can be small. The goal is preserving meaning, not rushing changes.

PureDhamma.net remains the primary source. Portuguese translations in AXIS-NIDDHI are study and review support, not official or final translations.

## 15-minute first task

1. Open the Cloudflare archive:

   ```text
   https://niddhi.pages.dev/archive
   ```

2. Pick one article.

3. If Portuguese exists, compare one paragraph in English and Portuguese.

4. If Portuguese does not exist, check whether the page clearly says:

   ```text
   🇧🇷 Aguardando tradução
   ```

5. Ask:

   - Does the Portuguese preserve the English meaning?
   - Was any Pāli or Dhamma term simplified too much?
   - Would a sincere new reader be helped or confused?

6. Report only what you can verify.

7. When unsure, mark the passage as `needs review` instead of rewriting the meaning.

## What to look for

- A sentence that seems to say more, less, or something different from the English.
- Pāli terms translated too loosely or flattened into ordinary language.
- Portuguese that sounds fluent but changes the meaning.
- Missing translation status, especially pages without Portuguese content.
- Broken links, confusing buttons, or unclear navigation.
- Places where a reader might mistake a study translation for an official final translation.

## What not to do

- Do not rewrite Dhamma meaning from personal preference.
- Do not claim final authority over a doctrinal point.
- Do not bulk-edit translations.
- Do not change CSL, source data, or generated pipeline output casually.
- Do not treat the Portuguese text as official or final.
- Do not hide uncertainty. Mark it clearly.

## Good first reports

A good first report is small, exact, and easy to verify.

Include:

- page URL;
- article title or PDPN code, if visible;
- paragraph or short quoted phrase;
- what seems unclear;
- whether you compared it with the English original;
- your suggested status: `needs review`, `possible translation issue`, `UI issue`, or `broken link`.

## Examples of useful feedback

```text
Page: https://niddhi.pages.dev/pages/TL.AA.000/index.html
Issue: possible translation issue
English phrase: "..."
Portuguese phrase: "..."
Concern: the Portuguese may make the term sound final/ordinary, while the English keeps it more technical.
Suggested status: needs review
```

```text
Page: https://niddhi.pages.dev/pages/SI.AA.013/index.html
Issue: translation status
Observation: Portuguese content is unavailable and the button says "🇧🇷 Aguardando tradução".
Suggested status: OK
```

```text
Page: https://niddhi.pages.dev/archive
Issue: UI/navigation
Observation: I clicked a section card and the inline section opened near the card grid.
Suggested status: OK
```

## How developers can help

- Improve accessibility without changing canonical content.
- Make navigation clearer for new readers and reviewers.
- Keep staging changes small and reversible.
- Preserve traceability between static pages, source data, and review notes.
- Avoid touching translation data unless the task explicitly requires it.

## How visual QA can help

- Check whether buttons, language pills, and translation status labels are clear.
- Verify that dark/light themes remain readable.
- Confirm that article links, archive links, and contributor links go where they say they go.
- Look for text overflow, low contrast, or confusing visual hierarchy.
- Report screenshots or exact URLs when something feels unclear.

## Report Your Finding

If you complete a first review, report only what you can verify.

Use:

- Bee First Task issue:
  https://github.com/matikamata/axis-niddhi/issues/120

- Guided issue forms:
  https://github.com/matikamata/axis-niddhi/issues/new/choose

Small reports are welcome. A useful first report can be as simple as one article, one paragraph, one observation, and one suggested status.

## Closing note

An Abelha does not need to carry the whole hive at once.

One careful observation, one verified issue, or one clear `needs review` note can protect meaning for the next reader.
