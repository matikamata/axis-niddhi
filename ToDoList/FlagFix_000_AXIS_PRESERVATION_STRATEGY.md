# ⚑ FLAGFIX — Large Artifact Strategy & Canonical Preservation Layers

## Context

Cloudflare Pages enforces a **25 MiB file size limit**.

During deployment, a canonical PDF (≈71 MiB) caused build failure:
- `48.OTAP_KathaVatthu_Prakarana_2-Sinhala.pdf`

Decision:
> We DO NOT remove canonical artifacts to satisfy platform constraints.

Instead:
> We introduce a **multi-layer preservation and delivery architecture**.

---

## 🧱 AXIS-NIDDHI — Preservation Architecture Layers

### Layer A — Canonical Archive
- Source of truth
- CSL / WordPress extracted corpus
- Immutable snapshots
- Checksums / manifests
- Offline SSD backup

---

### Layer B — Public Web Edition (Cloudflare Pages)
- Lightweight static site
- HTML / CSS / JS
- Images, audio, small assets only (<25 MiB)
- Fast global access

---

### Layer C — Large Artifact Store (PRIMARY DELIVERY)
⚠️ Pending setup (requires billing)

Recommended:
- Cloudflare R2

Purpose:
- Store large PDFs, audio, scans
- Stable URLs
- Externalized from Pages build

Fallback (temporary):
- Direct links to PureDhamma.net

---

### Layer D — Public Preservation Mirror
Recommended:
- Internet Archive

Purpose:
- Long-term public redundancy
- Independent hosting
- Historical preservation

---

## 🌐 Future Layers (Strategic / Non-Urgent)

### Layer E — IPFS (Decentralized Distribution)
- Content-addressed storage
- Immutable hashes (CID)
- Peer-to-peer availability
- Resistant to centralized failure

---

### Layer F — Piql (Long-term Analog/Digital Preservation)
- Film-based archival (hundreds of years)
- Institutional-grade preservation
- Offline + tamper-resistant

---

### Layer S — Svalbard Seed Concept 🌱
- Physical “Dhamma Seed”
- Offline storage (USB / SSD / archival media)
- Stored in extreme redundancy environments
- Symbolic + real preservation layer

---

## 🧠 Core Principle

> **No canonical knowledge is ever removed due to infrastructure limitations.**

Instead:
- Delivery adapts
- Preservation remains absolute

---

## 🛠 Current Implementation Strategy

### Build Rules

- Assets ≤ 25 MiB → bundled into `13-static-site`
- Assets > 25 MiB → externalized via:
  - `asset_map.json`
  - `BENG_EXTERNAL_UPLOADS_BASE_URL`

---

## ⚠️ Current Temporary State

- External large assets → `https://puredhamma.net/...`
- R2 bucket not yet configured (billing pending)

---

## 🚀 Next Steps

### HIGH PRIORITY
- [ ] Configure Cloudflare R2 bucket
- [ ] Define canonical artifact base URL
- [ ] Update asset pipeline to use R2 instead of PureDhamma links

### MEDIUM
- [ ] Upload large PDFs to Internet Archive
- [ ] Add secondary mirror links

### LOW (STRATEGIC)
- [ ] IPFS pinning strategy
- [ ] Evaluate Piql archival feasibility
- [ ] Create physical “Dhamma Seed” storage unit

---

## 🔍 Validation Commands

Check for oversized files in Pages output:

```bash
find pipeline/13-static-site -type f -size +25M
