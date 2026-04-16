# Contributing to AXIS-NIDDHI
## The Kalyāṇa mittā Protocol

*"Kalyāṇamittatā"* — noble friendship — is, as the Buddha said, not merely a part of the path. It is the whole of it.

A **Kalyāṇa mitta** in this project is a person who brings AXIS-NIDDHI to a new language community. Not a programmer. Not an administrator. A person who has understood the teaching, speaks the language of their community, and is willing to do the work of ensuring that the translation is not just grammatically correct — but *doctrinally faithful*.

---

## Who This Is For

You are a candidate to become a Kalyāṇa mittā if:

- You have read essays at [PureDhamma.net](https://puredhamma.net) and are familiar with them in English
- You are a native speaker (or equivalent fluency) of a language that DeepL supports
- You are willing to review Pāli terminology carefully before approving a translation run
- You understand that *Anicca* is not simply "impermanence," and why that matters

You do not need to be a programmer. The Steward handles the pipeline. Your role is the human layer between the engine and your community.

---

## Step 1 — Contact

Open a GitHub Issue with the title: `[Kalyāṇamitta] — [Language Name]`

Include:
- Your target language (and locale code if applicable, e.g., `de-DE`, `ja-JP`)
- A brief note on your familiarity with the PureDhamma.net essays
- Whether you have a technical Steward collaborating with you, or whether you need one

---

## Step 2 — Glossary Validation

The most important work you will do is review the Pāli glossary.

The Steward will generate a draft glossary CSV for your language based on `pipeline/metadata/Glossario_v5.csv` (the validated pt-BR reference). Your task is to review each term and confirm or correct its rendering in your language.

**Key terms requiring special attention:**

| Pāli | Common mistranslation | PureDhamma.net meaning |
|---|---|---|
| Anicca | "impermanence" | The characteristic of conditioned things that makes them unable to provide lasting satisfaction — subject to change and loss of the expected outcome |
| Dukkha | "suffering" | The previously unknown quality of conditioned existence — arising from the Anicca nature |
| Anattā | "no-self" | The futility of identifying anything in this world as a permanent self — arising from Anicca and Dukkha |
| Nibbāna | "nirvana" | The unconditioned — preserve in Pāli |
| Paṭicca Samuppāda | "dependent origination" / "interdependence" | The precise causal chain explained by the Buddha — preserve in Pāli or use "Paṭicca Samuppāda" without substitution |

Refer to [PureDhamma.net — Tables and Summaries — Pāli Glossary](https://puredhamma.net/three-tipitaka-sections/pali-glossary/) as the source of doctrinal authority. No dictionary is sufficient.

---

## Step 3 — Translation Run

Once the glossary is validated and uploaded to DeepL, the Steward runs:

```bash
axis pipeline --preservation
```

This sends all 748 essays through DeepL with your validated glossary. The output lands in `pipeline/09-csl/<PD#PN>/source/<lang-code>/content.html`.

---

## Step 4 — Review

You review a sample of translated essays (minimum 10% recommended) for:

1. **Pāli terms** — Are they preserved as-is or rendered correctly per the glossary?
2. **Tone** — Is the register appropriate? (These are teachings, not casual articles.)
3. **Accuracy** — Does the doctrinal meaning survive the translation?

File your review notes in a GitHub Issue or PR comment. The Steward will make any necessary corrections and re-run affected essays.

---

## Step 5 — Seal

Once the review passes, the Steward runs:

```bash
axis pipeline --audit
axis pipeline --distribution
```

Your language is now part of the canon. A new Dhamma Seed is generated, sealed, and added to the ledger.

---

## The Bee Does Not Fight for Nectar

The Kalyāṇamitta does their Service and moves on. There is no credit to claim, no territory to defend. If another Kalyāṇamitta arrives for the same language with better qualifications, welcome them — there is no competition in this work.

The flower opens. The pollen travels. The teaching finds those who are ready.

---

## Technical Stewards

If you are a programmer who wants to contribute to the pipeline itself (scripts, SSG engine, integrity model, CLI), open a GitHub Issue with the title: `[Steward] — [area of contribution]`.

#ToDo: Read the [User Manual](https://github.com/matikamata/axis-niddhi.wiki.git) first — especially the Invariants section. Some rules are not negotiable.

---

*With gratitude to Prof Lal A. for the teaching, and to all the Bees who will carry the pollen.*
