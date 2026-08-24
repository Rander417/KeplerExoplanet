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
  - [2026-08-24 Restart, layout, and tooling](Decisions/2026-08-24%20Restart,%20layout,%20and%20tooling.md)
- **Research Log** — findings with numbers, one note per session or experiment
  - [2026-08-24 Restart reconnaissance](Research%20Log/2026-08-24%20Restart%20reconnaissance.md)

## Notebooks (Phase 2 will make these runnable again)

| # | Notebook | Purpose (2020) | Status |
|---|---|---|---|
| 01 | `notebooks/01_cleaning_eda.ipynb` | Load, rename, nulls, variance/correlation, feature selection | legacy paths |
| 02 | `notebooks/02_clustering.ipynb` | Feature importance, k-means, PCA | legacy paths |
| 03 | `notebooks/03_sklearn_models.ipynb` | Logistic regression, gradient-boosted trees, balanced random forest | legacy paths |
| 04 | `notebooks/04_neural_net.ipynb` | Keras deep net + keras-tuner search | to be rebuilt in PyTorch (Phase 4) |
| 05 | `notebooks/05_habitable_zone.ipynb` | Box-filter "habitable" screen | to be replaced by insolation-based HZ (Phase 4) |

## Conventions for notes

- Decisions use [Templates/Decision](Templates/Decision.md); research entries use [Templates/Research Log Entry](Templates/Research%20Log%20Entry.md).
- File names: `YYYY-MM-DD Short title.md` so they sort by date.
- Numbers in notes must come from a run we can point to (notebook cell, script, or query). If a number is provisional, say so.
- Attachments (pasted images) land in `notes/attachments/`.
