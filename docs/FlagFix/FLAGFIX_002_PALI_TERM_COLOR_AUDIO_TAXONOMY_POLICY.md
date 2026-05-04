# FlagFix 002 — Pāli Term Color / Audio Taxonomy Policy

## Status

Planning / review policy only.

No CSS, renderer, CSL, HTML, glossary, translation, audio, pronunciation, metadata, or static-site output changes are authorized by this document.

## Problem

AXIS-NIDDHI contains Pāli terms that may carry doctrinal, pronunciation, color, audio, or didactic meaning.

Some terms may appear with:

- diacritics;
- no diacritics;
- italics;
- color emphasis;
- audio/pronunciation cues;
- glossary links;
- repeated canonical forms;
- translated surrounding text;
- source-specific PureDhamma styling.

If these terms are normalized, translated, recolored, or stripped mechanically, doctrinal meaning and reviewer trust can be degraded.

## Policy

Pāli terms must be treated as source-bound protected tokens until reviewed.

This includes, but is not limited to:

- `Kamma`
- `Dhamma`
- `Saṅkhāra`
- `Anicca`
- `Dukkha`
- `Anatta`
- `Nibbāna`
- `Micchā Diṭṭhi`
- `Sammā Diṭṭhi`
- `Taṇhā`
- `Avijjā`
- `Paṭicca Samuppāda`
- `Ariya`
- `Sotāpanna`
- `Sakadāgāmi`
- `Anāgāmi`
- `Arahant`

## Taxonomy Draft

Each protected term may eventually need these fields:

| Field | Purpose |
|---|---|
| canonical_term | preferred reviewed form |
| ascii_fallback | non-diacritic fallback when present in source |
| source_forms | forms observed in PureDhamma source |
| allowed_translations | translations allowed only when explicitly reviewed |
| forbidden_translations | translations that must not be introduced mechanically |
| color_policy | preserve source didactic color unless explicitly reviewed |
| audio_policy | preserve source audio/pronunciation relationship when available |
| glossary_policy | whether glossary linking is allowed |
| title_policy | whether term is protected in titles |
| body_policy | whether term is protected in body text |
| quote_policy | whether term is protected in quoted passages |
| reviewer_note | human review comments |

## Allowed Actions

- Inventory observed Pāli terms.
- Compare source form vs AXIS rendered form.
- Record whether a term appears in title, body, quote, glossary, color, or audio context.
- Propose taxonomy fields.
- Add human review notes.

## Forbidden Actions

- Do not translate protected Pāli terms automatically.
- Do not remove diacritics automatically.
- Do not add diacritics automatically.
- Do not recolor terms automatically.
- Do not strip didactic colors.
- Do not alter audio/pronunciation links.
- Do not rewrite titles or body text.
- Do not modify CSL, renderer, glossary, CSS, HTML, or generated static-site output.

## Acceptance Criteria

This policy is accepted when:

- the taxonomy risk is documented;
- protected Pāli terms are identified as human-review tokens;
- no implementation changes are made;
- follow-up work is limited to review matrices or source-bound inventories.

## Next Recommended Step

Create a review inventory for a small pilot set of Pāli terms before any renderer, glossary, CSS, translation, or audio behavior is changed.
