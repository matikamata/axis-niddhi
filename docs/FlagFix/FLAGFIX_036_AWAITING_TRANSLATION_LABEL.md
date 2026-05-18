# FLAGFIX_036 - Improve pending translation label copy

Date: 2026-05-18
Workspace: `/home/sanghop/axis/axis-niddhi-production`
Scope: visual copy only for untranslated archive/list entries

## Change

Old archive/list label:

```text
pending translation / pendente de tradução
```

New archive/list label:

```text
Awaiting translation / Aguardando tradução
```

The new copy is more human and intentional for the Vitrine surface. It communicates that translation is awaited, not abandoned as an administrative pending item.

## Files changed

```text
pipeline/13-ssg/templates/index.html
pipeline/13-static-site/archive.html
```

## Source of truth

The authoritative source is the SSG archive/index template:

```text
pipeline/13-ssg/templates/index.html
```

`pipeline/13-static-site/archive.html` is generated static output, but it is tracked in this repository. It was updated by the same exact copy replacement to keep source and generated archive parity without running a build.

## Grep summary

Before:

```text
pipeline/13-ssg/templates/index.html: old=1 new=0
pipeline/13-static-site/archive.html: old=439 new=0
```

After:

```text
pipeline/13-ssg/templates/index.html: old=0 new=1
pipeline/13-static-site/archive.html: old=0 new=439
```

The broader search no longer finds the old `pending translation / pendente de tradução` label in the searched project surfaces.

## No-change confirmation

No CSL content was modified.
No `Translation_Control_Center.csv` change was made.
No SP10/SP11 behavior was modified.
No DeepL call was made.
No translation was run.
No build was run.
No pipeline was run.
No deploy was run.
No Netlify/Vitrine update was made.
No Cloudflare configuration was touched.
`/home/sanghop/axis/axis-niddhi-published` was not touched.
