---
tags: [research-log, data-quality, leakage]
date: 2026-08-24
---

# 2026-08-24 Restart reconnaissance

## Question

What state is the 2020 project actually in, and what has moved (data, tooling, science) since it was written?

## What we did

Cloned `Rander417/KeplerExoplanet` (`main` at `c4fcfdb`, 25 commits, 2020-10-04 → 2022-07-01), read the project deck, and ran quick checks with pandas against `data/raw/cumulative_kaggle_snapshot.csv` (formerly `Resources/cumulative.csv`) and the five legacy pickles. Live archive counts came from one TAP query. Everything below was measured in this session; nothing is from memory.

## Findings

### Repository

- 5 analysis notebooks (cleaning/EDA 37 code cells, clustering 30, sklearn models 36, neural net 22, habitable zone 22), all saved with outputs and no error cells; every Markdown header is an HTML `<span style="color:slateblue">`.
- `requirements.txt` pins 2020 versions (pandas 1.0.3, scikit-learn 0.23.2, tensorflow 2.3.1, keras-tuner 1.0.1, mlxtend 0.17.3) plus two dummy packages (`sklearn==0.0`, `imblearn==0.0`). The web app's requirements include `yfinance`, a stock-data library unrelated to this project.
- 52 MB of keras-tuner checkpoints under `tuningOutput/`, a 25 MB pptx, and a stray `.Rhistory` were tracked.
- The Heroku app URL (`kepler-groupa.herokuapp.com`) returns HTTP 404 (checked today).
- The README says **11** confirmed planets passed the habitable filter; the deck and `habitable_Confirmed_exoplanets.pkl` say **12** (the pickle has 12 rows). The candidate pickle has 37 rows, matching the deck. To reconcile in Phase 2.
- The legacy pickles load under pandas 3.0.2 (tested) — no format rescue needed.

### Data

- `cumulative_kaggle_snapshot.csv`: 9,564 rows x 50 columns, 40,557 null cells.
- `koi_disposition` in the snapshot: CONFIRMED 2,293 / CANDIDATE 2,248 / FALSE POSITIVE 5,023. `koi_pdisposition`: CANDIDATE 4,496 / FALSE POSITIVE 5,068.
- **Live archive today (TAP, `select koi_disposition, count(*) from cumulative group by koi_disposition`):** CONFIRMED 2,747 / CANDIDATE 1,978 / FALSE POSITIVE 4,839 — same 9,564 KOIs, 454 more confirmed than the snapshot.
- `koi_tce_delivname`: `q1_q17_dr25_tce` 8,054; `q1_q16_tce` 796; `q1_q17_dr24_tce` 368; missing 346.
- `stellar_info_final.csv` (7,810 x 7) only adds `koi_smet` and `koi_smass` (+ errors), which the TAP table already contains.
- Legacy pipeline shapes: `kepler_RAW` 9,564 x 50 → `kepler_clean_full` 8,945 x 27 → `kepler_processed` 8,945 x 24 (drops `Disposition_Score`, one-hot encodes `TCE_Delivery` into 3 columns, keeps the 4 FP flags).

### Target leakage (the important one)

Cross-tab of "any `koi_fpflag_*` set" against the dispositions, snapshot data:

| any flag set | `koi_pdisposition` CANDIDATE | FALSE POSITIVE |
|---|---|---|
| no | 4,454 | 106 |
| yes | 42 | 4,962 |

| any flag set | `koi_disposition` CANDIDATE | CONFIRMED | FALSE POSITIVE |
|---|---|---|---|
| no | 2,216 | 2,239 | 105 |
| yes | 32 | 54 | 4,918 |

So 98% of pipeline false positives carry a flag and 98% of unflagged rows are candidates: the flags essentially *are* `koi_pdisposition`, which explains the 2020 finding that models hit 99% f1 on that target. With the 3-class archive target the flags still isolate FALSE POSITIVE almost perfectly; what remains (CANDIDATE vs CONFIRMED) depends on follow-up observations not present in the table. Median `koi_score`: CANDIDATE 0.987, CONFIRMED 1.000, FALSE POSITIVE 0.000 (correctly excluded from features in 2020).

### Habitable-zone criteria

The 2020 filter was period 200–400 d, T_eff 5,500–6,500 K, R_star 1–2 R_sun, log g > 4, metallicity > 0. That selects Sun-like stars with Earth-like years; it does not use `koi_insol`, `koi_teq`, or `koi_prad`, which are the quantities habitable-zone definitions are built on.

## Sources

- Repo: https://github.com/Rander417/KeplerExoplanet (fork of https://github.com/tom-jj-G/KeplerExoplanets)
- Archive TAP docs: https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html — "For web browsers: `https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=`"
- KOI column definitions: https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html
- Kopparapu et al. 2013: https://arxiv.org/abs/1301.6674 — "the water loss (inner HZ) and maximum greenhouse (outer HZ) limits for our Solar System are at 0.99 AU and 1.70 AU, respectively"
- Heroku free-plan removal: https://help.heroku.com/RSBRUH58/removal-of-heroku-free-product-plans-faq
- TensorFlow Windows GPU note: https://www.tensorflow.org/install/pip and https://discuss.ai.google.dev/t/2-10-last-version-to-support-native-windows-gpu/32465

## Next

- Phase 2: repoint notebooks, reproduce f1 83/90/90, reconcile 11 vs 12, notebook-by-notebook scrutiny.
- Phase 3: TAP pull script; with-flags vs physics-only models.
- Phase 4: insolation-based HZ; PyTorch NN.
