# scripts/legacy — Archived Scripts

This directory contains earlier versions of pipeline scripts that have been superseded by the current `core/` implementation.

They are kept here for historical reference — not for use.

---

## Why Keep Them?

Every script in this folder represents a solved problem. Some were written under pressure, some in moments of breakthrough. They document the *process* of building AXIS-NIDDHI, not just its final form.

The `DEPRECATED/` subdirectory contains the oldest generation — the scripts that existed before the SG/SP/SA/SD stage structure was established.

---

## Do Not Run These

Scripts in `legacy/` may:
- Use outdated path conventions
- Depend on database schemas that no longer exist
- Produce outputs incompatible with the current CSL structure

If you are looking for the active pipeline, everything you need is in `scripts/core/`.

---

## Historical Note — MasterPDPN_Raw

Before the PD#PN addressing system existed, the corpus was mapped manually — each PureDhamma.net page visited and recorded by hand, applying an automotive part-numbering strategy to bring structure to 748 essays.

That document (`MasterPDPN_Raw.csv`) is preserved in the private archive. It is the founding artifact of what became AXIS-NIDDHI. One day it may be published as a museum piece.

The resistance that had to be overcome to build it was real. What came through it was the PD#PN system that now makes this entire engine possible.

*— For the archive, with respect for the process.*
