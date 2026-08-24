---
tags: [research-log, notebook-03, models, leakage]
date: 2026-08-24
---

# 2026-08-24 Notebook 03 rewrite — honest baseline

> [!success] Outcome
> `notebooks/03_sklearn_models.ipynb` rewritten on `kepler.models`; the 2020 numbers reproduce to four decimals and are re-labelled; three feature sets compared on the same rows with 5-fold cross-validation; 16 tests pass. Metrics saved to `reports/tables/03_baseline_metrics.csv`.

## The 2020 baseline, reproduced (2020 split, `legacy_2020` features)

| Model | Accuracy | Weighted f1 | **Macro f1** | f1 CANDIDATE | f1 CONFIRMED | f1 FALSE POSITIVE |
|---|---|---|---|---|---|---|
| Logistic regression | 0.8324 | 0.8298 | **0.7729** | 0.628 | 0.700 | 0.991 |
| Gradient boosting | 0.9021 | 0.9015 | **0.8706** | 0.805 | 0.817 | 0.990 |
| Balanced random forest | 0.8994 | 0.8987 | **0.8670** | 0.799 | 0.813 | 0.989 |
| *Flag rule: any flag → FP, else CONFIRMED* | 0.7550 | 0.6733 | 0.5550 | 0.000 | 0.674 | **0.991** |

> [!warning] The deck's "83 / 90 / 90% f1" is the accuracy / weighted-f1 column. Macro f1, the number that weights the two planet classes equally, is 0.77 / 0.87 / 0.87. The FALSE POSITIVE column is identical for the models and for a one-line rule.

## Same rows, three feature sets — 5-fold CV macro f1 (mean ± std)

| Model | legacy_2020 (23 cols) | with_flags (16) | physics_only (12) |
|---|---|---|---|
| Logistic regression | 0.768 ± 0.014 | 0.741 ± 0.016 | 0.527 ± 0.006 |
| Gradient boosting | 0.866 ± 0.009 | 0.861 ± 0.007 | 0.715 ± 0.015 |
| Balanced random forest | 0.867 ± 0.005 | 0.860 ± 0.007 | 0.715 ± 0.003 |

- Removing the four flags costs the tree models ≈ 0.15 macro f1; the provenance columns add ≈ 0.005, within fold noise.
- Fold-to-fold spread (0.003–0.016) is as large as the gap between the two tree models: the 2020 "GBT vs RF" ranking was noise.

## `log1p` on heavy-tailed columns (logistic regression)

| Feature set | Scaled only | log1p + scaled |
|---|---|---|
| with_flags | 0.741 ± 0.016 | **0.841 ± 0.007** |
| physics_only | 0.527 ± 0.006 | **0.668 ± 0.006** |

A tenth of macro f1 for one transform; the review's "missed" item confirmed. Trees are unaffected.

## Where physics-only fails (gradient boosting, test split)

Confusion matrix rows = truth: CANDIDATE 279 / 99 / 156, CONFIRMED 75 / 447 / 50, FALSE POSITIVE 121 / 52 / 958. Physics still catches 85% of false positives, but CANDIDATE ↔ FALSE POSITIVE confusions (156 + 121) are where the flags used to do the work, and CANDIDATE ↔ CONFIRMED needs information that is not in the table.

## Built

- `src/kepler/models.py`: `split` (2020 split), `legacy_models` (2020 hyperparameters; imbalanced-learn 0.7 defaults spelled out for the BRF), `scaled`, `log1p_scaled`, `score`/`Scores`, `fit_and_score`, `flag_rule`, `cv_macro_f1`.
- `tests/test_models.py`: 5 tests (split classes 534/572/1131; GBT 0.9021 / 0.8706; flag rule 0.7550 / FP f1 0.9908; physics-only drop > 0.10; log1p + CV run).
- `src/kepler/viz.py`: `FEATURE_SET_COLORS` (ordinal amber ramp, validated).
- Figures: `reports/figures/models/macro_f1_by_feature_set.png`, `confusion_gbt_flags_vs_physics.png`.

## Next

- Phase 3: `HistGradientBoostingClassifier` on all 9,564 rows (NaN-native) with missingness indicators; calibrated probabilities; hyperparameters from validation folds; then the live TAP table.
- Notebook 02 as the null-result clustering notebook.
