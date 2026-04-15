# AXIS-NIDDHI — Time Capsule
## A Preserved Archive of the PureDhamma Canon

---

## What is this?

This archive preserves the complete teachings originally published at **PureDhamma.net**
by Lal A. — a scientific interpretation of the Buddha's teaching based on the original
Pāli Canon.

The archive contains **748 posts** covering the full scope of Buddha Dhamma:
foundational ethics, Abhidhamma, dependent origination, meditation, and the path
to Nibbāna.

This capsule was produced by the **AXIS-NIDDHI Canon Compilation Engine**.

---

## What is AXIS-NIDDHI?

AXIS-NIDDHI is a deterministic content preservation pipeline.

It was designed to:
- Extract, clean, and version the original PureDhamma corpus
- Translate the corpus into Portuguese (pt-BR) via DeepL
- Generate a static website for offline reading
- Preserve the corpus with cryptographic integrity guarantees
- Distribute the corpus via a peer-to-peer mirror protocol

The system is fully reproducible: given the original source backup, every output
can be regenerated bit-for-bit.

---

## What is in this capsule?

```
capsule/
├── README_HUMANS.md        ← this file
├── README_MACHINES.json    ← machine-readable manifest with all hashes
├── AXIS_PROTOCOL.md        ← complete protocol description
├── seeds/                  ← minimal corpus fingerprint
│   └── puredhamma_seed/
│       ├── corpus.json             corpus registry (748 entries)
│       ├── pipeline_profile.json   pipeline stage map
│       ├── canon_manifest.json     cryptographic manifest
│       ├── build_seal.json         reproducibility declaration
│       └── seed_manifest.json      seed integrity hash
├── ledger/                 ← append-only canon registry
│   ├── ledger.json                 registry index
│   └── entries/
│       └── puredhamma-v1.json      registered canon entry
├── semantic/               ← concept index (non-canonical)
│   ├── index.json                  concept registry
│   ├── concept_schema.json         field definitions
│   └── concepts/
│       ├── anicca.json             Anicca — impermanence
│       └── nibbana.json            Nibbāna — liberation
├── navigator/              ← study paths (non-canonical)
│   ├── concept_map.json            concept graph (10 nodes, 35 edges)
│   ├── learning_paths.json         3 structured study paths
│   └── query_index.json            concept → post lookup
└── mirror_endpoint/        ← distributable mirror snapshot
    ├── ledger.json
    ├── seeds/
    └── tags/
```

---

## How to rebuild the full system

**Requirements:**
- Ubuntu / Debian Linux
- Python 3.10+
- The original PureDhamma backup ZIP
- A DeepL API key (for translation only)

**Full rebuild:**

```bash
# 1. Clone or restore the pipeline
cd /path/to/pipeline

# 2. Configure credentials
echo "YOUR_WP_PASS"   > scripts/private/wp_password.txt
echo "YOUR_DEEPL_KEY" > scripts/private/deepl_key.txt

# 3. Run the full pipeline
bash scripts/tools/run_full_pipeline.sh

# 4. Verify the output
bash scripts/tools/axis_cli.sh verify canon

# 5. Serve the static site locally
bash scripts/tools/axis_cli.sh serve
```

**Verify this capsule without rebuilding:**

```bash
bash scripts/tools/axis_cli.sh verify canon
bash scripts/tools/axis_cli.sh ledger verify
bash scripts/tools/axis_cli.sh seed verify
```

---

## The teaching

The Buddha's teaching is a science of the mind and reality.

Its core insight — that all conditioned things are impermanent (anicca), 
unsatisfactory (dukkha), and without a permanent self (anattā) — was discovered
through direct investigation, not faith.

The path described in this corpus leads from ordinary human experience through
the understanding of suffering, its origin, and its cessation, to Nibbāna —
the unconditioned, the permanent, the final liberation.

This archive exists so that this teaching is never lost.

---

## Contact / Origin

Source: PureDhamma.net  
Author: Lal A.  
Archive engine: AXIS-NIDDHI  
Archive date: SEE README_MACHINES.json → built  
