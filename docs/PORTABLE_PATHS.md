# Portable workspace paths

Public documentation uses role names and configurable paths instead of an operator's home directory. Existing historical records retain their decisions and dates; machine-specific path prefixes have been replaced with these conventions. This is a documentation redaction, not a rewrite of Git history.

- `AXIS_REPO`: the root of the current repository checkout.
- `AXIS_WORKSPACE`: a directory containing the related checkouts. Choose its location on your computer.
- `HOME`: your operating system's home directory, provided by the shell.
- Paths such as `docs/START_HERE.md` are relative to the repository root.

In a POSIX shell, from inside the checkout:

```bash
export AXIS_REPO="$(git rev-parse --show-toplevel)"
export AXIS_WORKSPACE="$(dirname "$AXIS_REPO")"
```

A path such as `${AXIS_WORKSPACE}/axis-niddhi-production` refers to the checkout serving the production role. If your folders have different names or locations, adjust the variable or the final directory name. These examples do not create folders or grant permission to build, publish or modify another checkout.

In PowerShell:

```powershell
$env:AXIS_REPO = (git rev-parse --show-toplevel)
$env:AXIS_WORKSPACE = Split-Path $env:AXIS_REPO -Parent
```

Use `$env:AXIS_WORKSPACE` in PowerShell commands rather than POSIX `${AXIS_WORKSPACE}` syntax.

## Utilities with explicit paths

The comparison utility takes two existing directories:

```bash
python pipeline/scripts/tools/audit_ssg_zip.py /path/to/extracted/ssg /path/to/current/ssg
```

The patch propagation utility requires the source and every destination explicitly. It writes to the specified targets; inspect them before running it:

```bash
bash pipeline/scripts/tools/propagate_patches.sh /path/to/source/pipeline /path/to/target/pipeline
```

Neither tool depends on a particular user's directory layout. The propagation utility was not executed as part of this documentation update.
