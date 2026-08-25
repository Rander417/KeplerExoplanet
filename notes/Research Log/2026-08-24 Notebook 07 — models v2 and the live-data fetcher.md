---
tags: [research-log, notebook-07, models, calibration, phase-3]
date: 2026-08-24
---

# 2026-08-24 Notebook 07 — models v2, and the live-data fetcher

> [!success] Outcome
> `notebooks/07_models_v2.ipynb`: every one of the 9,564 KOIs kept (NaN-native gradient boosting + missingness indicators), hyperparameters chosen by **nested** cross-validation, probabilities checked and calibrated, leakage-free permutation importance, and a saved physics-only model with a column contract. `kepler.fetch` pulls the live archive table (to be run on Rich's machine). **31 tests pass.**

> [!abstract] The one-line result
> **Physics-only ceiling ≈ 0.72 macro f1, whichever way the model is built.** More rows, a better learner and honest tuning move it by thousandths. The information that would separate CANDIDATE from CONFIRMED is not in the table.

## Nested CV (5 outer × 3 inner), all 9,564 rows

| | physics_only (22 cols) | with_flags (26 cols) |
|---|---|---|
| macro f1 | **0.722 ± 0.006** | **0.862 ± 0.007** |
| balanced accuracy | 0.733 ± 0.006 | 0.863 ± 0.007 |
| f1 CANDIDATE / CONFIRMED / FALSE POSITIVE | 0.55 / 0.78 / 0.84 | 0.79 / 0.82 / 0.98 |
| log loss | 0.578 ± 0.006 | 0.258 ± 0.003 |

Most-chosen parameters: physics `learning_rate 0.05, max_leaf_nodes 31, min_samples_leaf 20`; with flags `0.05, 15, 50`.

### Rows or model?

| physics_only | macro f1 |
|---|---|
| Notebook 03: 2020 GBT settings, dropna rows (8,945) | 0.715 ± 0.015 |
| HGB tuned, complete rows only (9,200) | 0.723 ± 0.011 |
| HGB tuned, all rows + indicators (9,564), nested CV | 0.722 ± 0.006 |

Neither the extra rows nor the tuning matter at the 0.01 level. The with-flags column tells the same story (0.861 → 0.861 → 0.862).

## Calibration (physics-only, out-of-fold)

| | raw (balanced class weights) | isotonic |
|---|---|---|
| log loss | 0.578 | 0.575 |
| Brier | 0.342 | 0.335 |
| macro f1 of the argmax | 0.723 | **0.701** |

The raw model under-states FALSE POSITIVE probabilities and over-states CANDIDATE ones (balanced class weights do that); isotonic calibration straightens the reliability curves. The trade-off is real: the calibrated argmax leans to the majority class and macro f1 drops by 0.02. **Show calibrated probabilities; make the label decision with an explicit rule.**

## What the physics-only model uses (permutation importance, held-out split)

Transit signal-to-noise (−0.166 macro f1 when shuffled), orbital period (−0.089), planet radius (−0.089), transit duration (−0.073), impact parameter (−0.046), transit depth (−0.035); stellar temperature and the rest below 0.02.

## Built

- `kepler.models`: `add_missing_indicators`, `hgb_model`, `HGB_GRID`, `nested_cv` → `NestedCVResult`, `reliability_table`, `brier_multiclass`.
- `kepler.fetch`: `tap_url`, `fetch`, `save_pull` (+ provenance JSON with SHA-256 and disposition counts), CLI `uv run python -m kepler.fetch [--counts] [--dry-run]`.
- Tests: `tests/test_models_v2.py` (4), `tests/test_fetch.py` (3, offline).
- Saved: `models/hgb_physics_only_calibrated.joblib` (6.4 MB, ignored by git) + `.contract.json` (input columns in order, class codes, params, nested-CV score).
- Figures: `reports/figures/models/confusion_hgb_oof.png`, `reliability_physics_only.png`, `permutation_importance_physics_only.png`. Table: `reports/tables/07_models_v2_metrics.csv`.

## Next

- Claude Code runs `uv run python -m kepler.fetch --counts` then the full pull; commits `data/raw/cumulative_tap_YYYY-MM-DD.csv` + provenance.
- Notebook 08 (live vs snapshot): which KOIs changed class since the Kaggle era, the habitable-zone screen and the models re-run on the live table.
