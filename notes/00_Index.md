---
tags: [index]
updated: 2026-08-24
---

# Kepler Exoplanets — Index

The vault root is the git repo, so code, data docs, and notes all link to each other. Start here.

## Orientation

- [Roadmap](Roadmap.md) — the 5-phase plan and what's done
- [Glossary](Glossary.md) — KOI columns, mission jargon, and the ML terms we lean on
- [References](References/References.md) — every source we cite, with what it's good for
- [CLAUDE.md](../CLAUDE.md) — working agreements (environment, science guardrails, conventions)
- [Data README](../data/README.md) — provenance of every dataset and the column dictionary
- [Project README](../README.md) — the 2020 write-up, paths updated

## Logs

- **Decisions** — one note per non-obvious choice, newest first
  - [2026-08-24 Column names, palette, no external databases](Decisions/2026-08-24%20Column%20names,%20palette,%20no%20external%20databases.md)
  - [2026-08-24 History rewrite, HZ scope, clustering fate](Decisions/2026-08-24%20History%20rewrite,%20HZ%20scope,%20clustering%20fate.md)
  - [2026-08-24 Tag team, git autonomy, and how the app ships](Decisions/2026-08-24%20Tag%20team,%20git%20autonomy,%20and%20how%20the%20app%20ships.md)
  - [2026-08-24 Restart, layout, and tooling](Decisions/2026-08-24%20Restart,%20layout,%20and%20tooling.md)
- **Research Log** — findings with numbers, one note per session or experiment
  - [2026-08-24 Notebook 07 — models v2 and the live-data fetcher](Research%20Log/2026-08-24%20Notebook%2007%20—%20models%20v2%20and%20the%20live-data%20fetcher.md) — all rows, nested CV, calibration; physics-only ceiling ≈ 0.72
  - [2026-08-24 Notebook 05 rebuild — insolation habitable zone](Research%20Log/2026-08-24%20Notebook%2005%20rebuild%20—%20insolation%20habitable%20zone.md) — Kopparapu 2014 limits; 15 small confirmed planets in the conservative zone
  - [2026-08-24 Notebook 02 rewrite — clustering null result](Research%20Log/2026-08-24%20Notebook%2002%20rewrite%20—%20clustering%20null%20result.md) — scaled k-means on all classes; ARI ≈ 0
  - [2026-08-24 Notebook 03 rewrite — honest baseline](Research%20Log/2026-08-24%20Notebook%2003%20rewrite%20—%20honest%20baseline.md) — 2020 numbers reproduced and re-labelled; feature sets compared with CV
  - [2026-08-24 Notebook 01 rewrite](Research%20Log/2026-08-24%20Notebook%2001%20rewrite.md) — what the package now does and the numbers it pins
  - [2026-08-24 Phase 2 review summary](Research%20Log/2026-08-24%20Phase%202%20review%20summary.md) — start here; links to the five per-notebook review notes
  - [2026-08-24 Notebook 01 pre-review](Research%20Log/2026-08-24%20Notebook%2001%20pre-review.md)
  - [2026-08-24 Restart reconnaissance](Research%20Log/2026-08-24%20Restart%20reconnaissance.md)

## Notebooks

| # | Notebook | Purpose (2020) | Status |
|---|---|---|---|
| 01 | `notebooks/01_cleaning_eda.ipynb` | Load, nulls, cleaning, feature sets, EDA figures | ✅ rewritten 2026-08-24, runs clean |
| 02 | `notebooks/02_clustering.ipynb` | k-means sweep with agreement scores, centroids, PCA map | ✅ rewritten 2026-08-24, null result, runs clean |
| 03 | `notebooks/03_sklearn_models.ipynb` | 2020 baselines re-labelled; feature sets compared with 5-fold CV; log1p | ✅ rewritten 2026-08-24, runs clean |
| 04 | `notebooks/04_neural_net.ipynb` | Keras deep net + keras-tuner search | to be rebuilt in PyTorch (Phase 4) |
| 05 | `notebooks/05_habitable_zone.ipynb` | Insolation-based habitable zone (Kopparapu 2014), radius ceiling, 2020 comparison | ✅ rebuilt 2026-08-24, runs clean |
| 07 | `notebooks/07_models_v2.ipynb` | All rows, NaN-native boosting, nested CV, calibration, permutation importance, saved model | ✅ new 2026-08-24, runs clean (≈ 7 min) |

*There is no notebook 06: house rule.*

## Conventions for notes

- Decisions use [Templates/Decision](Templates/Decision.md); research entries use [Templates/Research Log Entry](Templates/Research%20Log%20Entry.md).
- File names: `YYYY-MM-DD Short title.md` so they sort by date.
- Numbers in notes must come from a run we can point to (notebook cell, script, or query). If a number is provisional, say so.
- Attachments (pasted images) land in `notes/attachments/`.
