# AXIS-NIDDHI

AXIS-NIDDHI is a careful preservation and translation project for the
PureDhamma.net teaching corpus.

It has two public-facing goals:

- keep a static, offline-readable archive available without depending on a live database;
- support reviewed Portuguese access without silently changing the original meaning.

It does **not** reinterpret Dhamma, replace PureDhamma.net, or claim authority
over the teaching. Technology assists the work; human discernment remains the
validation layer.

## Start Here

If you are new to the project, read these first:

- [START_HERE.md](docs/START_HERE.md) - a 3-minute orientation for visitors.
- [TRANSLATION_REVIEW_GUIDE.md](docs/TRANSLATION_REVIEW_GUIDE.md) - how to review translation quality.
- [VISION.md](docs/VISION.md) - the deeper intention behind AXIS-NIDDHI.
- [CONTRIBUTING.md](CONTRIBUTING.md) - how Kalyana mitta review works.

## What You Can Read Today

The public archive is a static site generated from the AXIS-NIDDHI corpus. It is
designed to be portable: HTML, images, CSS, and JavaScript files that can be
hosted without a server-side application.

Current public-facing surfaces:

- Official manual Netlify vitrine: `https://niddhi.netlify.app/`
- GitHub-connected Cloudflare preview/test surface: `https://niddhi.pages.dev/welcome.html`

The source corpus comes from PureDhamma.net, a large body of essays explaining
Buddha Dhamma with technical precision. AXIS-NIDDHI preserves source
traceability and avoids presenting translations as final without review.

## How the Project Is Organized

```text
pipeline/
├── metadata/            # control files, status, glossary/reference data
├── 09-csl/              # Canonical Source Library
├── 13-ssg/              # static site generator source
└── 13-static-site/      # generated static site output
docs/                   # orientation, handoffs, review and policy notes
review/                 # review artifacts and audit notes
sources/                # source archive area
```

## Translation Review

Translation quality is not only grammar. Reviewers look for:

- preserved Pali terms where substitution would distort meaning;
- accurate doctrinal sense, especially for Anicca, Dukkha, Anatta, Nibbana, and
  Paticca Samuppada;
- stable tone appropriate to teaching material;
- titles and navigation that help readers without inventing interpretation.

See [TRANSLATION_REVIEW_GUIDE.md](docs/TRANSLATION_REVIEW_GUIDE.md).

Portuguese translations are offered as study and review support for readers who
are not fluent in English. They are not official, final, or doctrinally
certified translations; the English articles at PureDhamma.net remain the
primary reference. See the full translation disclaimer in
[TRANSLATION_REVIEW_GUIDE.md](docs/TRANSLATION_REVIEW_GUIDE.md#important-note-about-the-portuguese-translation).

## Steward Notes

The pipeline can rebuild and audit the corpus, but those commands are
steward-only operations. Do not run them casually.

Before any build, deploy, sync, reset, or cleanup:

1. preserve evidence of local changes;
2. identify which workspace is being used;
3. confirm whether the target is Cloudflare preview or the Netlify deploy
   payload;
4. record the decision.

Monthly maintenance is described in
[MONTHLY_MAINTENANCE.md](docs/MONTHLY_MAINTENANCE.md).

## Design Principles

- Meaning over speed
- Traceability over convenience
- Review before scale
- Static access over platform dependency
- Human discernment over automated confidence

## License

License: MIT. See [LICENSE.md](LICENSE.md).

---

AXIS-NIDDHI - enable continuity without altering meaning.
