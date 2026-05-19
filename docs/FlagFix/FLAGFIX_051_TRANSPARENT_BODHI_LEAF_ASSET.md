# FlagFix 051 — Transparent Bodhi Leaf Asset

Date: 2026-05-18

## Scope

This sprint preserves the approved transparent/no-background Bodhi leaf asset as a small visual static asset update.

Asset path:

- `pipeline/13-static-site/assets/BodhiCircuitLeaf.png`

## Reason

The previous version rendered with a visible white square around the leaf. The updated PNG removes that background so the leaf reads cleanly against the site surface.

## Operator Confirmation

The operator confirmed:

- the background removal was intentional;
- the transparent/no-background version was visually tested and approved;
- the old white square around the leaf looked bad;
- this asset should be preserved in its own small PR rather than bundled into #FlagFix_050.

## Change Type

This is a visual/static asset-only update.

No generator, renderer, metadata, translation, or deployment behavior is changed by this sprint.

## Non-Actions

This sprint did not:

- touch `/home/sanghop/axis/axis-niddhi-published`;
- update Netlify/Vitrine;
- deploy;
- run build or pipeline;
- call DeepL;
- translate anything;
- modify CSL content;
- modify metadata CSVs;
- modify `Translation_Control_Center.csv`;
- modify SP10/SP11;
- modify any source/template behavior.
