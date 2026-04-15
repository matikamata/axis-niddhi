# AXIS-NIDDHI — Canonical Corpus Publishing Engine
**Version:** V5.4  
**Release:** /beng-release

---

## What this is

A self-contained, reproducible pipeline to rebuild the PureDhamma knowledge
archive from the original WordPress backup and publish it as a multilingual
static site.

---

## Quick start

```bash
# 1. Install alias (once)
echo "alias axis='bash /beng-release/axis'" >> ~/.bashrc && source ~/.bashrc

# 2. Check integrity
axis integrity

# 3. Run full rebuild (requires MySQL, Apache, WP-CLI)
axis pipeline --full

# 4. Preview the site
axis preview
```

---

## What's in this release

```
/beng-release/
├── axis                   CLI entry point
├── README.md              This file
├── sources/
│   └── *.zip              PureDhamma WordPress backup (canonical source)
└── pipeline/
    ├── scripts/           30 CORE pipeline scripts
    ├── metadata/          PDPN index, glossary, section map
    ├── 09-csl/            Canonical Source Library (empty → filled by SG phase)
    ├── 01-extracted-htmls/ Working dir (empty → filled by SG01)
    ├── 02-preprocessed/    Working dir (empty → filled by SG02)
    ├── 13-ssg/            SSG engine (empty → bootstrapped by setup_v54)
    ├── 13-static-site/    Site output (empty → filled by SD03)
    ├── logs/              Pipeline logs
    ├── recovery/          Crash recovery files
    └── snapshots/         CSL snapshots
```

---

## System requirements

- Ubuntu 22.04+ (or Debian 12+)
- Python 3.11+
- MySQL 8+
- Apache 2 + PHP 8.1 + mod_rewrite
- WP-CLI
- Python packages: `pandas pymysql beautifulsoup4 requests deepl jinja2 markdown`

---

## Configuration

All paths are derived from `BENG_BASE` environment variable:

```bash
export BENG_BASE=/beng-release/pipeline   # default for this release
```

Credentials (required before first run):
- DeepL API key → place in `pipeline/scripts/deepl_key.txt`
- WordPress App Password → place in `pipeline/scripts/wp_password.txt`

These files are NOT included in the release for security reasons.

---

## Pipeline phases

| Phase | Command | Effect |
|---|---|---|
| Full rebuild | `axis pipeline --full` | SG → SP → SA → SD |
| Genesis only | `axis pipeline --genesis` | WP extract → CSL build |
| Translation | `axis pipeline --preservation` | Identity + DeepL |
| Audit | `axis pipeline --audit` | SHA-256 integrity |
| Distribution | `axis pipeline --distribution` | Static site + WP |

---

## SSG bootstrap (first run only)

Before the SD phase can run, the SSG engine must be initialized:

```bash
bash /beng-release/pipeline/scripts/setup_v54_static_site.sh
```

This is automatic on `axis pipeline --full`.

---

*AXIS-NIDDHI — Preserving the Dhamma for future generations.*

## Verifying release integrity

The manifest uses relative paths and is location-independent.
Verification works from any directory the release is copied to:

```bash
cd /path/to/release-root
sha256sum --check release-manifest.sha256
# All files: OK
```
