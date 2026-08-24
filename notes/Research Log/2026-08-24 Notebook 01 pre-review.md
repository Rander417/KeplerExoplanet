---
tags: [research-log, notebook-01, data-quality]
date: 2026-08-24
---

# 2026-08-24 Notebook 01 pre-review (prior-session claims, verified)

## Question

An earlier Claude chat (spring 2026, transcript pasted by Rich) reviewed `Kepler_Cleaning_EDA.ipynb` and reported a list of issues. Which of those survive contact with the actual notebook and data, and what did it miss?

## What we did

Read `notebooks/01_cleaning_eda.ipynb` cell by cell (71 cells: 37 code, 19 markdown, **15 raw**) and re-ran the null-handling logic against `data/raw/cumulative_kaggle_snapshot.csv` with pandas. Checked the saved outputs and the legacy pickles in `data/legacy/`. Every number below comes from those runs.

## Findings

### Claims from the prior session

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | Cells 6–11 connect to an AWS Postgres instance that is surely gone; cell 4 loads the CSV anyway | **Confirmed, with a nuance** | Cells 6–11 are *raw* cells (inert; they never execute). They still contain the RDS endpoint `kepler-exoplanet.cotbxoedtrfv.us-east-1.rds.amazonaws.com`, user `postgres`, and an empty password string. Cell 11 would have overwritten the CSV load with `read_sql_table`. Remove in Phase 2; nothing to migrate. |
| 2 | Mode imputer (cell 25) is fit on the *mean*-imputed frame, not the original | **Confirmed** | Cell 25: `imputer_mode.fit_transform(keplerProcessedMeanImpute_df)` — a frame with zero NaNs, so "mode imputation" was a no-op on already-mean-imputed data. Cells 23–25 are also raw cells, so the saved run never executed any imputation; only `dropna()` (cell 22) is live. The deck's "mode had a negative f1 impact" cannot be reproduced from this code. |
| 3 | MICE cell (26) is empty | **Confirmed** | Two comment lines, no code. |
| 4 | `LabelEncoder` on the target leaves the mapping undocumented | **Confirmed, mapping now recorded** | Alphabetical: **0 = CANDIDATE, 1 = CONFIRMED, 2 = FALSE POSITIVE**. Checked against `data/legacy/kepler_processed.pkl`: counts 0→2,136, 1→2,285, 2→4,524 match the string counts in `kepler_clean_full.pkl`. |
| 5 | Feature engineering is minimal (drop errs, dropna, dummies, label-encode) | Confirmed by reading; a design choice rather than a bug | Cells 16, 22, 32, 33. |
| 6 | Visualizations are interleaved with processing | Confirmed by reading | Structure question for the Phase 2 rewrite. |
| 7 | `requirements.txt` is an environment dump (250+ packages) | Confirmed | 279 lines; now `archive/requirements_2020.txt`, replaced by `pyproject.toml`. |
| 8 | Kaggle CSV matches the repo CSV (same MD5) | **Not verifiable here** | The Kaggle archive was not available in this session. Re-check when `fetch_koi.py` exists (Phase 3). |
| 9 | `stellar_info_final.csv` columns (`koi_smet`, `koi_smass`) could join earlier for the models | Reasonable; superseded | A TAP pull returns those columns natively (see [reconnaissance](2026-08-24%20Restart%20reconnaissance.md)). |

### New findings from this pass

1. **The row-drop count in the README and deck is wrong.** They say "roughly 363 rows contain nulls". Re-running the notebook's logic (drop `_err` columns → fill `kepler_name` and `koi_score` → `dropna()`) removes **619 rows** (9,564 → 8,945), which is also the row count of `kepler_clean_full.pkl`. 363 is the null count of the *stellar* columns (`koi_steff`, `koi_slogg`, `koi_srad`, and the fitted transit columns); the union across all columns is 619 because `koi_tce_delivname`/`koi_tce_plnt_num` (346 nulls) and `koi_insol` (321) only partly overlap.
2. **Missingness is not random — it tracks the label.** Of the 619 dropped rows, 499 are FALSE POSITIVE, 112 CANDIDATE, 8 CONFIRMED: 9.9% of false positives are dropped versus 0.3% of confirmed planets. Dropping them both shifts the class balance and discards a signal (a KOI with no fitted stellar/transit parameters is itself informative). Phase 3 should try missingness-indicator features and NaN-native models such as `HistGradientBoostingClassifier` instead of `dropna`.
3. **`Disposition_Score.fillna("not_scored")` (cell 21) turns a numeric column into strings** (`kepler_clean_full.pkl` stores it as object dtype with values like `'0.969'`). Harmless for the models because the column is dropped in cell 31, but any reuse of `kepler_clean_full` inherits a corrupted column.
4. **`kepoi_name` is set as the index (cell 15) and then listed in the rename map (cell 17)**, where the rename is a no-op. Cosmetic.
5. Null counts after the `_err` drop, for the record: `koi_impact`, `koi_depth`, `koi_prad`, `koi_teq`, `koi_model_snr`, `koi_steff`, `koi_slogg`, `koi_srad` 363 each; `koi_tce_plnt_num` and `koi_tce_delivname` 346; `koi_insol` 321; `koi_kepmag` 1. Total 12,698 cells, matching the notebook's own cell-19 output.

## Sources

- `notebooks/01_cleaning_eda.ipynb` at commit `9d601d1` (cell indices as saved).
- `data/raw/cumulative_kaggle_snapshot.csv`; `data/legacy/kepler_clean_full.pkl`; `data/legacy/kepler_processed.pkl`.
- README section "EDA & Preprocessing" (the 363 claim); deck slide "Handling Null Values".

## Next

- These become inputs to the Phase 2 multi-agent review (agents work independently; agreement with this list is a consistency check on them).
- Phase 2 rewrite of notebook 01: single CSV/TAP load path, no raw-cell graveyard, explicit label mapping, keep `koi_score` numeric, report the 619 honestly.
