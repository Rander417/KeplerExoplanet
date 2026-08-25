---
tags: [research-log, notebook-08, live-data, out-of-time, phase-3]
date: 2026-08-25
---

# 2026-08-25 Notebook 08 — the live archive versus the 2020 snapshot

> [!success] Outcome
> Claude Code pulled the archive's cumulative table on 2026-08-25 (`data/raw/cumulative_tap_2026-08-25.csv`, 9,564 × 153, SHA-256 `37fffa14…`). Same KOIs, **identical physics** (only `koi_depth` differs, by rounding at the 1e-5 level), **925 changed verdicts (9.7%)**. The physics-only model trained on 2020 labels predicts which 2020 candidates were later confirmed with **AUC 0.937**. 32 tests pass.

## What moved (snapshot → today)

| from \\ to | CANDIDATE | CONFIRMED | FALSE POSITIVE |
|---|---|---|---|
| CANDIDATE (2,248) | 1,657 | **443** | 148 |
| CONFIRMED (2,293) | 0 | 2,292 | **1** (Kepler-503 b) |
| FALSE POSITIVE (5,023) | **320** | **13** | 4,690 |

- The 320 FALSE POSITIVE → CANDIDATE rows all had a vetting flag in the snapshot and none today: **the flags were rewritten with the verdicts** (`koi_fpflag_nt` changed on 347 rows, `_ss` 207, `_co` 133, `koi_pdisposition` 527). Flags are outputs of vetting, not measurements — the leakage argument, settled by the data itself.
- 13 former false positives are confirmed planets today, among them **Kepler-1649 c** (K03138.02), exactly the case notebook 05 flagged. 443 candidates were confirmed (the statistical-validation era); 148 were dismissed.
- The one retraction: **Kepler-503 b** (K00242.01), CONFIRMED → FALSE POSITIVE in the archive; the literature reason is outside this table (to verify separately).

## Out-of-time test of the physics-only model

Physics-only HGB (notebook-07 parameters), trained on **2020 labels**, out-of-fold P(planet-like) = P(CANDIDATE) + P(CONFIRMED), evaluated against what the archive decided later for the 2020 CANDIDATEs:

| 2020 candidates that are now… | n | median P(planet-like) in 2020 physics |
|---|---|---|
| CONFIRMED | 443 | **0.946** |
| still CANDIDATE | 1,657 | 0.826 |
| FALSE POSITIVE | 148 | **0.257** |

**AUC 0.937** for later-CONFIRMED vs later-FALSE POSITIVE among the 591 decided candidates. The model never saw those verdicts; the flags could not have passed this test because they were changed along with the labels.

## Retrained on today's labels

Physics-only, 5-fold CV, same parameters: **0.747 ± 0.012** macro f1 with the live labels vs 0.723 ± 0.007 with the snapshot labels. Today's labels are a little more consistent with the physics.

## Habitable zone on today's table

Confirmed, conservative zone, ≤ 2 R⊕: **15 → 16** (Kepler-1652 b entered; nothing left). Kepler-1649 c is confirmed but, with the KOI table's own DR25 parameters (insolation 0.16 at a 2,703 K star; conservative outer edge 0.225), sits outside the zone. The discovery paper's revised stellar parameters are not in the cumulative KOI table; getting them means pulling the archive's *planetary systems* table for confirmed planets (later phase).

## Built

- `kepler.data.tap_pulls()` / `load_tap_pull()`; smoke test that the live pull loads and covers the same KOIs.
- `notebooks/08_live_vs_snapshot.ipynb` (21 cells, runs in ~1.5 min).
- Figures: `reports/figures/live/disposition_transitions.png`, `out_of_time_candidates.png`. Tables: `reports/tables/08_disposition_transitions.csv`, `08_movers.csv` (925 rows with the 2020 model's P(planet-like)), `08_hz_confirmed_live.csv` (16 rows).

## Consequences

- The app (Phase 5) should train on **live labels** and show the physics-only calibrated probability; the out-of-time AUC is the honest headline for "can future observers use our models?" (2020 question 3).
- Data provenance now has two dated sources; `data/README.md` records both.
