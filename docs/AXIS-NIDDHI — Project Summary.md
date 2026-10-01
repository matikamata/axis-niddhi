# AXIS-NIDDHI — Project Summary

AXIS-NIDDHI preserves and translates the teaching corpus published by Lal A. at [PureDhamma.net](https://puredhamma.net/). It combines a static reading archive, traceable source material and a translation workflow with human review.

## 🎯 Purpose

Keep the material accessible, make comparison with the English source straightforward, and preserve the meaning of the teachings through careful review. PureDhamma.net remains the primary reference. Translations are study aids whose review status must remain visible.

## 🏗️ How the project works

1. Preserve source backups and extract article text, links and media.
2. Associate articles with stable **PD#PN** identifiers in the Canonical Source Library (CSL).
3. Prepare translations with terminology glossaries and record their status.
4. Review source differences, translations, links, audio and images.
5. Build and validate static publication packages, retaining manifests and release evidence.

Published files are derived artifacts. A static copy is not, by itself, proof that a translation is complete or that a full rebuild has been reproduced.

## 📦 Repository areas

Paths below are relative to the repository root; availability depends on the checkout or distribution package.

| Path | Purpose |
| --- | --- |
| `pipeline/09-csl/` | Source records, identities and language-specific article content |
| `pipeline/03-translations/` | Translation working material |
| `pipeline/13-ssg/` | Static-site generation code and templates |
| `pipeline/13-static-site/` | Generated publication output |
| `pipeline/scripts/` | Pipeline and maintenance utilities |
| `pipeline/metadata/` | Catalogs, glossaries and translation metadata |
| `docs/` | Public guides, policies and review records |

## 🌐 Reading and collaboration

The public archive offers language selection, search by topic or PD#PN, pronunciation recordings where available, glossary help and artwork by Mariinha. Language availability varies by article; a navigation option does not mean that its translation is ready.

The [Netlify archive](https://niddhi.netlify.app/) and [Cloudflare review preview](https://niddhi.pages.dev/welcome) can represent different release stages. Consult the notices on the page you are reading.

The LABZ area contains optional reading and exploration tools. It does not assign doctrinal authority to generated suggestions or alter the source articles.

## 🔎 Traceability and review

Release manifests and checksums identify the files included in a particular package. Source comparisons and human review serve different purposes: matching a file hash establishes file identity, not doctrinal correctness.

Useful contributions include reporting broken links, comparing a translation with its English source, preserving Pāḷi terminology and improving accessibility. Include the PD#PN, language and relevant passage when reporting a problem.

Start with [START HERE](START_HERE.md), the [translation review guide](TRANSLATION_REVIEW_GUIDE.md), or the [portable path conventions](PORTABLE_PATHS.md).
