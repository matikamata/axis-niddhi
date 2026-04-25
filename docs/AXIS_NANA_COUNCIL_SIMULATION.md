# AXIS NANA Council Simulation

## What this layer is

The Council layer is a deterministic local structure that simulates how multiple future model outputs may be compared inside AXIS NANA.

At this bootstrap stage it does not run models.
It only creates placeholder candidate entries and evaluates citation agreement structure.

## Why it does not call models yet

No real model is called because this phase is building safety-first orchestration.

The goal is to define:

- candidate slots
- citation comparison shape
- dissent note structure
- consensus status rules
- hallucination-risk review hooks

before introducing any external model dependency.

## How future outputs will be compared

Future council runs may compare multiple answer candidates by checking:

- which canonical refs each candidate cites
- whether candidates drift beyond the supplied context
- where citation agreement is high
- where dissent requires review

For now, all candidates are explicit placeholders and all carry `llm_called: false`.

## Why citation agreement matters

Citation agreement is the first safety signal because it is anchored in canon references rather than style, eloquence, or surface similarity.

If multiple candidates converge on the same cited reference set, that is structurally safer than trusting a single uncited answer.

## Why consensus is not doctrinal authority

Consensus is never treated as doctrinal authority.

Canon remains authority.
Council only helps compare derivative answer candidates against canonical citation discipline.

## How this protects against single-model hallucination

The council structure protects against single-model hallucination by:

- keeping candidates separate
- tracking citation agreement explicitly
- reserving dissent notes for review
- refusing to treat agreement itself as truth

This preserves the AXIS principle:

canon first, comparison second, interpretation later.
