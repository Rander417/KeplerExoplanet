---
tags: [research-log, review, notebook-01]
date: 2026-08-24
source: multi-agent review workflow wf_29148ee0-552 (reviewer + adversarial verifier)
---

# 2026-08-24 Review: Notebook 01 cleaning & EDA

> [!abstract] What the notebook does (reviewer's summary)
> 01_cleaning_eda loads the 9,564 x 50 Kaggle snapshot of the KOI cumulative table (cell 4) and pickles it unchanged as kepler_RAW.pkl (cell 5). It sets kepoi_name as the index (15), drops the 22 `_err` columns (16), renames the 27 surviving columns to long descriptive names with units (17), fills kepler_name with "unnamed" and koi_score with the string "not_scored" (21), and drops every row that still contains a null (22, 28), leaving 8,945 rows that are saved as kepler_clean_full.pkl (30). It then drops rowid/Kep_ID/Kepler_Name/koi_pdisposition/koi_score (31), one-hot encodes TCE_Delivery (32), label-encodes koi_disposition to 0/1/2 (33), and saves kepler_processed.pkl: 8,945 x 24 = target + the four koi_fpflag_* columns + 16 numeric columns + 3 delivery dummies, unscaled (35); notebooks 03 and 04 load this pickle, and no downstream notebook loads kepler_clean_full.pkl (02 and 05 load kepler_RAW.pkl). The remainder is EDA: a std/mean ratio table and bar chart, correlation heatmaps, a 25-panel histogram grid, an RA/Dec field-of-view scatter and period-radius scatters (38-63). The mean/median/mode imputation experiments (23-25), a KNN k-sweep (54) and an mlxtend SequentialFeatureSelector run (55) exist only as raw cells that never executed, and three SFS result dictionaries are pasted as raw text (66, 68, 70). Re-running the deterministic steps from the raw CSV in this session reproduces kepler_processed.pkl exactly (same 8,945 index, same 24 columns, max abs value difference 1.1e-13), so the saved artifacts are faithful to the code; the problems are in what the code keeps, what it silently drops, and what the deck/README say about it.

> [!warning] At a glance
> **13 findings**: 2 high · 5 medium · 6 low. Verifier verdicts: 11 confirmed · 2 partially · 0 refuted · 0 unverifiable. Verifier added 2 missed item(s). 6 deck/README claims checked.

## Findings at a glance

| ID | Severity | Category | Finding | Verifier |
|---|---|---|---|---|
| 01-F1 | high | leakage | The four koi_fpflag_* columns survive into kepler_processed.pkl and hand every downstream model the FALSE POSITIVE class | ✅ confirmed |
| 01-F2 | high | bug | Chained `fillna(..., inplace=True)` in cell 21 silently does nothing under pandas Copy-on-Write; dropna then discards 7,282 rows and the CANDIDATE class vanishes | ✅ confirmed |
| 01-F3 | medium | claim-vs-data | The imputation experiments behind the deck's 'Mode had a negative f1 impact' were never executed here, and the code as written cannot run | 🟡 partially |
| 01-F4 | medium | methodology | Sequential feature selection uses a KNN regressor with MSE on a label-encoded nominal target, cannot run as written, and its pasted results contradict the notebook's conclusion | ✅ confirmed |
| 01-F5 | medium | claim-vs-data | dropna removes 619 rows (6.5%), not 363, and the removal is class-biased and structural | ✅ confirmed |
| 01-F6 | medium | leakage | Kepler_Name is a near-perfect proxy for CONFIRMED and is retained (unflagged) in kepler_clean_full.pkl | ✅ confirmed |
| 01-F7 | low | methodology | TCE_Delivery dummies, Transit_Epoch, RA and Dec are provenance/position features rather than physics, and koi_score missingness is structural | ✅ confirmed |
| 01-F8 | medium | reproducibility | The notebook does not run top to bottom on a clean kernel: `plt` is never imported, TensorFlow is imported but unused and absent from the 2026 environment, and plot cells were re-run out of order | 🟡 partially |
| 01-F9 | low | dead-code | Dead code: Postgres cells with a live-looking AWS RDS endpoint, no-op and stale cells | ✅ confirmed |
| 01-F10 | low | bug | Disposition_Score becomes a mixed float/str column ('not_scored') that pandas will refuse to create in a future version | ✅ confirmed |
| 01-F11 | low | reproducibility | pandas drift: get_dummies now yields bool (pickle has uint8) and the cell-39 ratio table silently loses the three delivery dummies | ✅ confirmed |
| 01-F12 | low | documentation | Target encoding is undocumented and unpersisted, and the target is stored inside the feature table where it is treated as a numeric feature | ✅ confirmed |
| 01-F13 | low | bug | Chart bugs: field-of-view hover labels show the wrong quantities and the period-radius scatter's colorscale is a no-op | ✅ confirmed |

## Deck / README claims checked

| Verdict | Claim | Evidence |
|---|---|---|
| ✅ confirmed | Deck/README: "40k+ null cells across 10k rows & 50 columns" | Ran on data/raw/cumulative_kaggle_snapshot.csv: shape (9564, 50); `raw.isnull().sum().sum()` = 40,557 of 478,200 cells (the deck's '500k cells' and '10k rows' are rounded). Context worth adding: 19,128 of those nulls (47%) are koi_teq_err1/koi_teq_err2, which are 100% empty in this snapshot, and 27,859 sit in the 22 `_err` columns that cell 16 drops; the notebook's own cell 19 then shows 12,698. |
| ❌ refuted | Deck/README: "363 rows with nulls after cleaning (including dropping +/- error columns)" and "we decided to drop the nulls due to their small volume" | Ran: after dropping the `_err` columns and filling kepler_name/koi_score, 619 rows still contain a null and `dropna()` keeps 8,945 (matches cell 58's 'Index: 8945 entries'; 9,564 - 8,945 = 619, 6.5% of rows). 363 is the per-column null count of koi_impact/depth/prad/teq/model_snr/steff/slogg/srad (same 363 rows); the two TCE columns add 346 nulls of which 91 overlap, plus 1 koi_kepmag null -> 619. The dropped rows are 499 FALSE POSITIVE / 112 CANDIDATE / 8 CONFIRMED (9.9% of all FPs vs 0.35% of CONFIRMED), so 'small volume' understates a class-biased drop. The README's separate figure '3,572 remain' is partially right: 3,918 null cells remain after the fills, and 3,572 = 3,918 - 346, i.e. it omits one of the two TCE columns. |
| ⚪ unverified | Deck: "Mode had a negative f1 impact while Mean & Median had no discernible impact" (impute methods evaluated) | The mean/median/mode cells (23-25) are raw cells with no outputs, cell 26 is an empty MICE comment, and cell 28 hard-selects the drop-null frame. No f1 is computed anywhere in this notebook. Ran cell 23's code on the frame as it exists after cell 21: `ValueError: Cannot use mean strategy with non-numeric data: could not convert string to float: 'Kepler-227 b'`; cell 25 also imputes the mean-imputed frame instead of its own copy. So the comparison cannot have been produced by this notebook as saved. |
| ⚪ unverified | README: "dropping features actually slightly reduces our percentage. We are currently running the models on all features instead" (Sequential Feature Selection) | No f1 comparison across feature subsets exists in this notebook; the SFS cells (54, 55) are raw, reference undefined `X`/`y`, and use a KNN regressor scored by neg MSE. The pasted SFS output points the other way under its own metric: parsed avg_score at k=23 vs best subset: cell 66 -0.01758 vs -0.01041 (k=9); cell 68 -0.02482 vs -0.01069 (k=7); cell 70 (koi_disposition) -0.16665 vs -0.09854 (k=7). Cell 57's text ('reducing the features does significantly change the f1 scores... Therefore the models are ran on all features') is internally inconsistent. Whether models in notebook 03 lost f1 on subsets is outside this notebook and remains unverified. |
| ✅ confirmed | README: models trained on the Kepler disposition (koi_pdisposition) reached 99% f1; the target was changed to koi_disposition | Reproduced the phenomenon, not notebook 03's exact run: on the 8,945-row processed data, a DecisionTree using only the four koi_fpflag_* columns scores 5-fold macro-F1 0.994 / weighted-F1 0.994 / accuracy 0.994 against koi_pdisposition (the any-flag rule alone agrees with koi_pdisposition==FALSE POSITIVE on 99.44% of rows; 98.45% on the raw 9,564). A physics-only RandomForest (no flags) gets macro-F1 0.847. So the 99% is the flags restating the vetting verdict, which is why the target switch alone does not remove the leakage (see 01-F1). The switch itself is real: cell 33 encodes `Exoplanet_Archive_Disposition` and cell 31 drops `Disposition_Using_Kepler_Data`. |
| 🟡 partially | README: "The processed dataframe is scaled using StandardScaler before the models are run" | Not in this notebook: kepler_processed.pkl is unscaled (ran: Transit_Depth_[ppm] mean 24,402.4, std 83,300.4; Planetary_Radius mean 103.8, std 3,117.3; Insolation_Flux mean 7,636, std 160,156), and StandardScaler appears only inside the never-executed SFS raw cell 55. A grep shows notebooks 03 (cells 1, 12, 40) and 04 (cells 1, 11, 33) import/use StandardScaler after loading kepler_processed.pkl, and the archived app loads `model/scaler_param.joblib`; how correctly it is fitted (train split only?) is for the 03/04 reviews. |

## What the verifier added (missed by the reviewer)

> [!warning] CANDIDATE and CONFIRMED are the same Kepler-pipeline class split by archive validation status, and TCE_Planet_Number (a multiplicity proxy) is missing from the provenance list (medium)
> Ran check_e_missed.py and an inline follow-up on data/legacy pickles. All 2,136 CANDIDATE rows and 2,241 of 2,285 CONFIRMED rows have koi_pdisposition = CANDIDATE (the other 44 CONFIRMED are pipeline FALSE POSITIVEs), so nothing in the Kepler pipeline separates the two classes cell 33 encodes as 0 and 1; the split is the archive's follow-up state. The retained features track that state: KOIs on stars hosting more than one KOI in the processed set (2,055 of 8,945 rows; 7,730 distinct Kep_IDs) are 61.0% CONFIRMED / 26.1% CANDIDATE / 12.9% FP versus 15.0% / 23.2% / 61.8% for single-KOI stars; TCE_Planet_Number >= 2 holds for 29.9% of CONFIRMED, 19.1% of CANDIDATE and 7.2% of FP rows (raw crosstab: plnt_num 1 = 1753 CAND / 1602 CONF / 4390 FP; plnt_num 2 = 285 / 443 / 244; >=3 = 143 / 240 / 118). A CANDIDATE-vs-CONFIRMED RandomForest(200, random_state=0) without the flags reaches 5-fold accuracy 0.813 / macro-F1 0.812 with Transit_Signal-to-Noise as top importance (0.278, fit on all CAND/CONF rows, indicative only); median Kepler magnitude is nearly identical (14.66 vs 14.60), so brightness is not the driver. Useful negative result for the rewrite: StratifiedGroupKFold by Kep_ID does not change the scores (physics-only macro-F1 0.730 vs 0.726 stratified; all-23 0.869 vs 0.865), so sibling KOIs sharing star-level columns (identical Teff/logg/R*/RA/Dec/Kp for 781 of 840 multi-KOI stars) are not a CV-leak problem. The notebook never states any of this; the per-class CANDIDATE F1 (0.548 physics-only) partly measures how far the archive's follow-up has got, and TCE_Planet_Number belongs on the F7 provenance/multiplicity list. Reference to verify once online: the archive's validation-by-multiplicity argument (Lissauer et al. 2012, 'Almost All of Kepler's Multiple-planet Candidates Are Planets').

> [!note] Cell 52's plotly append_trace is deprecated in the installed plotly 6.9.0 and will break the histogram grid on a future upgrade (low)
> Inline run: `make_subplots(rows=1, cols=1).append_trace(go.Histogram(x=[1,2,3]), row=1, col=1)` succeeds under plotly 6.9.0 but emits DeprecationWarning 'The append_trace method is deprecated and will be removed in a future version.' Cell 52 calls append_trace 25 times (view cell 52). It belongs with F11's library-drift list; the fix is add_trace.


## Keep (what the rewrite should preserve)

- The staged data flow (raw pickle -> cleaned full table -> model-ready table) with an artifact saved at each stage; the deterministic parts reproduce exactly from the raw CSV (my rerun matched kepler_processed.pkl to 1.1e-13 with identical index and columns).
- kepoi_name as the row index (verified unique across 9,564 rows; kepid is not, 8,214 distinct stars) so rows stay traceable through processing.
- Dropping koi_score and koi_pdisposition from the feature set (cell 31) and dropping Kepler_Name/kepid/rowid before modelling; these are correct leak removals and the rewrite should extend the same reasoning to the flags.
- Readable column renames that carry units (Orbital_Period_[days], Transit_Depth_[ppm], ...), and data/README.md already maps them back to the archive names.
- Dropping the `_err` columns for the classifier was reasonable for the 2020 goal; the rewrite keeps them only for the habitable-zone work, as CLAUDE.md plans.
- The explicit markdown switch 'CURRENT METHOD: dropping' with alternatives listed: the intent to compare missing-data strategies is good practice and should be executed properly rather than removed.
- The EDA set worth recreating: RA/Dec field-of-view scatter by disposition, log-log period-radius scatter coloured by insolation, masked lower-triangle correlation heatmap, and the per-feature histogram grid with log y-axes (heavy-tailed features such as depth, radius, insolation show why log transforms matter).
- One-hot encoding of TCE_Delivery and a label encoder for the target are fine mechanics once the mapping is persisted and the delivery dummies are confined to the with-provenance variant.

## Rewrite recommendations

- Move the cleaning into src/kepler/preprocess.py as a pure function (raw DataFrame in, features + labels out) loaded through kepler.paths, write parquet to data/processed/, and add pytest checks against data/legacy/kepler_processed.pkl (8,945 x 24, class counts 2136/2285/4524) so the refactor is provably equivalent before the science changes begin.
- Replace chained inplace fills with direct assignment or `df.fillna({...})`, keep koi_score numeric with a boolean `is_dr25` indicator (score is null exactly when the delivery is not DR25), and assert row count and the three class labels after cleaning so a pandas upgrade cannot silently shrink the data (01-F2).
- Separate labels from features: a `labels` table (kepoi_name, kepid, kepler_name, koi_disposition, koi_pdisposition, koi_score) and a features table; persist the class mapping (or keep string labels and encode inside the model pipeline).
- Define and persist two feature lists per CLAUDE.md, `with_flags` and `physics_only`; leave TCE_Delivery, Transit_Epoch, RA and Dec out of physics_only (or justify them), and require every downstream metric to name its variant and its f1 average (macro/weighted/per-class).
- Handle missing data deliberately: keep the 619 rows with `has_transit_fit` / `has_tce` indicators and impute inside a sklearn Pipeline within stratified CV, or if dropping, report the class-biased loss (499 FP / 112 CANDIDATE / 8 CONFIRMED) in the notebook and the Research Log.
- If feature selection is kept, run it as executed code with a classifier and a classification metric under stratified CV on the training split (sklearn SequentialFeatureSelector or permutation importance), and delete the pasted raw-cell result dictionaries and the attached image.
- Strip the notebook to one purpose (clean + EDA): remove the Postgres cells and endpoint, the TensorFlow/SQLAlchemy/unused sklearn imports, the empty MICE and no-op cells; import matplotlib explicitly; use plain Markdown headers; run 'Restart & Run All' before committing and save figures to reports/figures/eda/ instead of embedding 8.6 MB of outputs.
- Make the EDA science-aware: log-scale or log-transform depth, radius, insolation and period; flag koi_impact > 1 (1,275 of 8,945 rows) and the 200,346 Earth-radius 'planet' as likely false positives or fit failures; fix the hover labels; adopt the warm no-blue palette once per notebook.
- Parameterise the input file so the same code runs on the Kaggle snapshot and on data/raw/cumulative_tap_YYYY-MM-DD.csv, asserting expected columns rather than hard-coding '3 delivery values'; record the null accounting (40,557 / 12,698 / 3,918 cells; 619 rows) and the leakage numbers (any-flag rule 98.95% vs koi_disposition FP; RF macro-F1 0.865 with flags vs 0.726 without) in notes/Research Log and the corrected null-handling decision in notes/Decisions/.

## Finding details

### 01-F1 — The four koi_fpflag_* columns survive into kepler_processed.pkl and hand every downstream model the FALSE POSITIVE class

> [!danger] high · leakage · cells [31, 33, 35, 58]

**Evidence**

Cell 31: `# "Disposition Using Kepler Data" and "Disposition Score" both have a high correlation to the target(y). Drop them` / `keplerProcessed_df.drop(["rowid","Kep_ID","Kepler_Name","Disposition_Using_Kepler_Data", "Disposition_Score"], axis =1, inplace=True)`. Cell 58 output: `1   Not_Transit-Like_FPF  8945 non-null int64 / 2   Stellar_Eclipse_FPF / 3   Centroid_Offset_FPF / 4   Ephemeris_Match_Indicates_Contaminat...`. The stated reason for dropping koi_score and koi_pdisposition (high correlation with the target) applies at least as strongly to the four flags, which are kept.

**Reproduction**

Ran (checks.py section E) on data/legacy/kepler_processed.pkl (8,945 rows):
`any_flag = X[flags].sum(axis=1) > 0; np.mean(any_flag == (y==2))` -> 0.9895 (crosstab: 4,516 of 4,524 FALSE POSITIVE rows have a flag set; only 8 FPs unflagged; 32 CANDIDATE + 54 CONFIRMED flagged). Same rule vs koi_pdisposition==FP: 0.9944 on 8,945 rows, 0.9845 on the raw 9,564.
`pr.corr()['Exoplanet_Archive_Disposition']` |corr| top 5: Stellar_Eclipse_FPF 0.479, Centroid_Offset_FPF 0.451, Not_Transit-Like_FPF 0.383, Ephemeris_Match..._FPF 0.340, then Transit_Depth 0.244.
5-fold StratifiedKFold(random_state=0) cross_val_predict on koi_disposition (3-class): DecisionTree on the 4 flags only: macro-F1 0.554, weighted-F1 0.673, acc 0.754, per-class F1 [CAND 0.000, CONF 0.673, FP 0.990]. RandomForest(200, random_state=0) all 23 features: macro-F1 0.865, weighted-F1 0.897, acc 0.898, per-class [0.790, 0.816, 0.989]. Same RF, physics only (flags removed): macro-F1 0.726, weighted-F1 0.760, acc 0.767, per-class [0.548, 0.777, 0.852].

**Impact**

The FALSE POSITIVE class (51% of rows) is essentially read off the vetting flags rather than learned from physics, so every f1/accuracy quoted downstream (README 83-90%) mixes rule reproduction with genuine prediction. The FP-class F1 goes from 0.989 to 0.852 and macro-F1 from 0.865 to 0.726 when the flags are removed. This is exactly the two-variant situation CLAUDE.md's science guardrails require.

**Recommendation**

Build two named feature sets in code (`with_flags`, `physics_only`), persist both lists, and report both variants side by side; never quote a single f1. State in the notebook that the flags are the vetting pipeline's own reasons for calling a KOI a false positive (data/README.md quotes the archive definitions).

**Verifier: ✅ confirmed**

*Corrected statement:* The four koi_fpflag_* columns survive into kepler_processed.pkl (cell 31 drops only rowid/Kep_ID/Kepler_Name/Disposition_Using_Kepler_Data/Disposition_Score; cell 58 output lists the four *_FPF columns). On the 8,945-row pickle the rule 'any flag set' agrees with koi_disposition == FALSE POSITIVE on 98.95% of rows (4,516 of 4,524 FPs flagged, 8 unflagged; 32 CANDIDATE and 54 CONFIRMED flagged) and with koi_pdisposition == FALSE POSITIVE on 99.44% (98.45% on the raw 9,564). The flags are the four strongest |Pearson r| with the encoded target (0.479, 0.451, 0.383, 0.340; next is Transit_Depth 0.244). 5-fold StratifiedKFold(shuffle, random_state=0) cross_val_predict, 3-class koi_disposition: DecisionTree on the 4 flags alone gives macro-F1 0.554 / weighted-F1 0.673 / accuracy 0.754 / per-class F1 [CAND 0.000, CONF 0.673, FP 0.990]; RandomForest(200, random_state=0) on all 23 features gives macro-F1 0.865 / weighted-F1 0.897 / acc 0.898 / per-class [0.790, 0.816, 0.989]; the same RF without the flags gives macro-F1 0.726 / weighted-F1 0.760 / acc 0.767 / per-class [0.548, 0.777, 0.852]. The FP class is read off the vetting flags, exactly the two-variant situation CLAUDE.md requires.

*Verifier evidence:* Ran check_c_leakage.py on data/legacy/kepler_processed.pkl and the raw CSV: agreement 0.9895 / 0.9944 / 0.9845; crosstab any_flag x class = [[2104, 2231, 8],[32, 54, 4516]]; |corr| 0.479/0.451/0.383/0.340/0.244; DT flags-only 0.554/0.673/0.754 [0, 0.673, 0.99]; RF all-23 0.865/0.897/0.898 [0.79, 0.816, 0.989]; RF physics-only 0.726/0.760/0.767 [0.548, 0.777, 0.852]. Every figure matches the reviewer's to the third decimal. Re-read cells 31, 33, 35, 58 in the view: quotes are accurate.

### 01-F2 — Chained `fillna(..., inplace=True)` in cell 21 silently does nothing under pandas Copy-on-Write; dropna then discards 7,282 rows and the CANDIDATE class vanishes

> [!danger] high · bug · cells [21, 22, 28]

**Evidence**

Cell 21: `keplerProcessed_df["Kepler_Name"].fillna("unnamed", inplace = True)` and `keplerProcessed_df["Disposition_Score"].fillna("not_scored", inplace = True)`; cell 22: `keplerProcessedDropNull_df = keplerProcessedDropNull_df.dropna()`. Both fills go through a column selection and rely on the intermediate Series being a view of the frame.

**Reproduction**

Ran the cell-21/22 code verbatim under pandas 2.3.3 (checks.py section C).
CoW=False (today's default): FutureWarning "A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method. The behavior will change in pandas 3.0. This inplace method will never work..."; nulls after fills 3918; rows after dropna 8945; classes ['CANDIDATE','CONFIRMED','FALSE POSITIVE'].
CoW=True (pandas 3 default): ChainedAssignmentError warning; nulls after fills 12698 (unchanged); rows after dropna 2282; classes left ['CONFIRMED','FALSE POSITIVE'] (every CANDIDATE row has no kepler_name and is dropped). A third FutureWarning also fires: "Setting an item of incompatible dtype is deprecated and will raise an error in a future version of pandas. Value 'not_scored' has dtype incompatible with float64".

**Impact**

A rerun under pandas 3 (or with `pd.options.mode.copy_on_write = True`) completes without an exception and produces a 2,282-row, two-class dataset; everything downstream would train on a silently different problem. Today it works only because the deprecated behaviour still exists.

**Recommendation**

Use `df['Kepler_Name'] = df['Kepler_Name'].fillna('unnamed')` (or `df.fillna({'Kepler_Name': 'unnamed'})`), keep koi_score numeric and add a boolean indicator column instead of a string sentinel, and add a test asserting the row count and the three class labels after cleaning.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell 21's `keplerProcessed_df["Kepler_Name"].fillna("unnamed", inplace = True)` and `...["Disposition_Score"].fillna("not_scored", inplace = True)` are chained inplace assignments. Under pandas 2.3.3 with copy_on_write off (the pinned default, pyproject has pandas>=2.2,<3) they still work: two FutureWarnings ('This inplace method will never work...') plus a third FutureWarning about setting 'not_scored' into a float64 column; nulls drop 12,698 -> 3,918, dropna keeps 8,945 rows and all three classes. With pd.options.mode.copy_on_write = True (the pandas 3 default) the same code only emits ChainedAssignmentError warnings, the fills do nothing (nulls stay 12,698, Kepler_Name 7,270 null, Disposition_Score 1,510 null, dtype float64), and cell 22's dropna keeps 2,282 rows with classes {CONFIRMED: 2281, FALSE POSITIVE: 1}, i.e. every CANDIDATE row is silently discarded. No exception is raised in either mode. While the <3 pin holds, this cannot bite in the locked environment unless CoW is switched on, so 'high' is at the upper edge of proportionate; it stays justified because the failure is silent and removes a whole class.

*Verifier evidence:* Ran check_b_cow.py twice (default and with copy_on_write=True) executing cells 15-22 verbatim on the raw CSV. CoW off: 3 FutureWarnings, nulls after fills 3918, rows after dropna 8945, classes ['CANDIDATE','CONFIRMED','FALSE POSITIVE'] counts {FP 4524, CONF 2285, CAND 2136}. CoW on: 2 ChainedAssignmentError warnings + 1 FutureWarning, nulls after fills 12698, rows after dropna 2282, classes ['CONFIRMED','FALSE POSITIVE'] counts {CONFIRMED 2281, FALSE POSITIVE 1}. pyproject.toml line 13 pins 'pandas>=2.2,<3'.

### 01-F3 — The imputation experiments behind the deck's 'Mode had a negative f1 impact' were never executed here, and the code as written cannot run

> [!warning] medium · claim-vs-data · cells [23, 24, 25, 26, 27, 28]

**Evidence**

Cells 23, 24, 25 are RAW (inert, no outputs). Cell 25: `keplerProcessedModeImpute_df.iloc[:,:] = imputer_mode.fit_transform(keplerProcessedMeanImpute_df)` (mode imputer applied to the mean-imputed frame, not its own copy). Cell 26 (executed) is only `# Impute NaNs via MICE`. Cell 27 markdown: `CURRENT METHOD: "dropping"`; cell 28: `keplerProcessed_df = keplerProcessedDropNull_df` with the three impute alternatives commented out. No f1 is computed anywhere in this notebook.

**Reproduction**

Ran cell 23's code on the frame as it stands after cell 21 (checks.py section C): `SimpleImputer(strategy='mean').fit_transform(tmp)` -> `ValueError: Cannot use mean strategy with non-numeric data: could not convert string to float: 'Kepler-227 b'` (Kepler_Name, both dispositions, TCE_Delivery and the 'not_scored' strings are all object columns at that point). The mode cell would additionally impute the wrong frame.

**Impact**

The deck statement 'Mode had a negative f1 impact while Mean & Median had no discernable impact' and the README's 'After evaluating (running the ML models) each impute method' cannot be traced to any executed code or output in the repository. Dropping may still be a fine choice, but the stated evidence for it does not exist here.

**Recommendation**

Either drop the claim or redo the comparison properly: put the imputer inside a sklearn Pipeline (numeric columns only), evaluate with stratified CV on the training split, and keep the executed cell and its output. Record the outcome in notes/Research Log.

**Verifier: 🟡 partially**

*Corrected statement:* The deck really says 'Impute methods evaluated: Mode had a negative f1 impact while Mean & Median had no discernable impact' (project_search hit in Kepler_Analysis_Presentation.pdf), but the notebook contains no executed imputation and no f1 anywhere: cells 23-25 are raw with no outputs, cell 26 is a two-line comment, cell 27 says 'CURRENT METHOD: dropping', cell 28 hard-assigns the drop-null frame with the three impute alternatives commented out. Correction to 'the code as written cannot run': only the mean (cell 23) and median (cell 24) cells fail, with ValueError 'Cannot use mean/median strategy with non-numeric data: could not convert string to float: Kepler-227 b' because Kepler_Name, both dispositions, TCE_Delivery and the 'not_scored' strings are object columns at that point. The mode cell's SimpleImputer(strategy='most_frequent') accepts strings and does run on this mixed frame (fills all nulls, 0 remaining), so a mode experiment could have been executed from the notebook; it is still applied to keplerProcessedMeanImpute_df rather than its own copy (cell 25 source), which after a failed cell 23 would be an un-imputed copy. Bottom line unchanged: the deck's f1 comparison cannot be traced to any executed code or output in this notebook.

*Verifier evidence:* Ran all three strategies on the frame as it stands after cell 21 (inline run): mean -> ValueError, median -> ValueError, most_frequent -> OK with 0 nulls left; mean on numeric-only columns works (9564 x 22). Notebook JSON scan (check_d_nbscan.py): cells 23, 24, 25 are type 'raw' with no outputs; cell 26 exec 14 is comment-only. Deck wording confirmed via project_search.

### 01-F4 — Sequential feature selection uses a KNN regressor with MSE on a label-encoded nominal target, cannot run as written, and its pasted results contradict the notebook's conclusion

> [!warning] medium · methodology · cells [53, 54, 55, 57, 65, 66, 67, 68, 69, 70]

**Evidence**

Cell 55 (raw): `classifier_pipeline = make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=41))` ... `sfs1 = SFS(classifier_pipeline, k_features=23, forward=True, scoring='neg_mean_squared_error', cv=cv)` / `sfs1.fit(X,y)`. Cell 54 (raw): `error.append(mean_squared_error(y,y_pred))`. Cell 57 markdown: `After extensive testing it has been revealed that reducing the features does significantly change the f1 scores of the models. Therefore the models are ran on all features` (reads as a typo for 'does not'). Pasted results use pre-rename names, e.g. cell 66 `'feature_names': ('koi_fpflag_nt', ... 'koi_tce_delivname_q1_q17_dr25_tce')`, which do not exist after cell 17.

**Reproduction**

Notebook JSON scan: no code or raw cell assigns `X` or `y` (the only `y=` matches are plotly keyword arguments in cells 61-63); `mean_squared_error` is never imported; so cells 54/55 would raise NameError. Parsed the pasted dicts (checks.py section F): cell 66 keys run 23->1 (mlxtend backward order) under the heading 'True'; cells 68 and 70 run 1->23 (forward). avg_score (neg MSE) at k=23 vs best: cell 66 -0.01758 vs -0.01041 at k=9; cell 68 -0.02482 vs -0.01069 at k=7 (flags + koi_period + koi_prad + koi_tce_plnt_num); cell 70 (koi_disposition) -0.16665 vs -0.09854 at k=7 (flags + koi_impact + koi_depth + koi_model_snr). Re-running the cell-55 pipeline on kepler_processed.pkl with all 23 features: koi_disposition -0.16702 (pasted -0.16665); koi_pdisposition -0.01904 (pasted -0.01758 and -0.02482, which disagree with each other, so the two pdisposition runs were not on identical inputs).

**Impact**

MSE of a regressor on codes CANDIDATE=0 < CONFIRMED=1 < FALSE POSITIVE=2 rewards predicting 'CONFIRMED' for uncertain objects and has no relation to f1, so the SFS output cannot support any f1 claim. By its own criterion, 7-9 feature subsets beat all 23 in all three runs, the opposite of 'dropping features reduces our percentage'. The results are unreproducible from this notebook.

**Recommendation**

If feature selection is kept, use a classifier with a classification metric (macro-F1 or balanced accuracy) under stratified CV on the training split only (sklearn SequentialFeatureSelector or permutation importance), execute it in the notebook, and let the result decide. Delete the pasted raw dictionaries and the image attachment.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell 55 (raw) wraps KNeighborsRegressor(n_neighbors=41) in StandardScaler and runs mlxtend SFS with scoring='neg_mean_squared_error' and KFold(10, shuffle, random_state=0) on a label-encoded nominal target; cell 54 (raw) scores a KNeighborsClassifier with mean_squared_error. Neither can run as written: no code or raw cell assigns X or y (the only 'y=' matches are plotly keyword arguments in cells 61-63), mean_squared_error is never imported (cell 1 imports none of sklearn.metrics), and plt is undefined. The pasted dictionaries are in mlxtend's backward order in cell 66 (keys 23->1, under the heading 'True') and forward order in cells 68 and 70 (keys 1->23). Under their own criterion, smaller subsets beat all 23 features in every run: cell 66 avg_score -0.01758 at k=23 vs -0.01041 at k=9; cell 68 -0.02482 vs -0.01069 at k=7 (four flags + koi_period + koi_prad + koi_tce_plnt_num); cell 70 (koi_disposition) -0.16665 vs -0.09854 at k=7 (four flags + koi_impact + koi_depth + koi_model_snr). Re-running the cell-55 pipeline on kepler_processed.pkl with all 23 features gives -0.16702 for koi_disposition (pasted -0.16665) and -0.01904 for koi_pdisposition (pasted -0.01758 and -0.02482, which also disagree with each other). Additional evidence the pasted pdisposition runs were not on this data: the same pipeline on the four flags alone scores -0.00549 today vs the pasted -0.02029 at k=4 in cell 66. Cell 57's sentence 'reducing the features does significantly change the f1 scores ... Therefore the models are ran on all features' is internally inconsistent and no f1 is computed here.

*Verifier evidence:* check_d_nbscan.py: regex over notebook JSON found X/y assignments only in cells 61-63 as plotly kwargs; 'mean_squared_error' appears only in raw cells 54, 55; parsed the three pasted dicts with ast.literal_eval (key order 23->1 / 1->23 / 1->23; avg@23 and best-k values as stated); cross_val_score(make_pipeline(StandardScaler(), KNeighborsRegressor(41)), KFold(10, shuffle=True, random_state=0), neg MSE): all-23 vs koi_disposition -0.16702, vs koi_pdisposition -0.01904, flags-only vs pdisposition -0.00549.

### 01-F5 — dropna removes 619 rows (6.5%), not 363, and the removal is class-biased and structural

> [!warning] medium · claim-vs-data · cells [19, 20, 21, 22, 28, 58]

**Evidence**

Cell 19 output `12698`; cell 22 `keplerProcessedDropNull_df = keplerProcessedDropNull_df.dropna()`; cell 58 output `Index: 8945 entries, K00752.01 to K07989.01` (9,564 - 8,945 = 619). Deck: '363 rows with nulls after cleaning'; README: 'roughly 363 rows contain nulls'.

**Reproduction**

checks.py section A on the raw CSV: rows with any null after dropping `_err` columns and filling kepler_name/koi_score = 619; rows after dropna = 8945. Per-column nulls: koi_impact/depth/prad/teq/model_snr/steff/slogg/srad = 363 each and they are the same 363 rows; koi_tce_delivname and koi_tce_plnt_num = 346; koi_insol = 321 (subset of the 363); koi_kepmag = 1; overlap of the 363 block with the 346 TCE-null rows = 91; union = 619. Dropped rows by koi_disposition: FALSE POSITIVE 499, CANDIDATE 112, CONFIRMED 8; share lost per class: FP 9.93%, CANDIDATE 4.98%, CONFIRMED 0.35%.

**Impact**

The '363' is the per-column null count of the transit-fit/stellar block, not the number of rows removed; the 346 rows without a federated TCE add 255 more. Because 81% of the dropped rows are FALSE POSITIVEs (KOIs the pipeline could not fit or federate), the cleaned set is slightly easier than the real table, and the information 'no transit model could be fitted' is itself predictive and is thrown away.

**Recommendation**

Report the drop as 619 rows with the class breakdown, or better, keep the rows: add a `has_transit_fit` / `has_tce` indicator and impute inside the CV pipeline. Whatever is chosen, print and assert the class distribution before and after.

**Verifier: ✅ confirmed**

*Corrected statement:* After dropping the 22 _err columns and filling kepler_name/koi_score, 619 of 9,564 rows (6.5%) still contain a null and cell 22's dropna keeps 8,945 (cell 58 output 'Index: 8945 entries'). The deck's '363 rows with nulls after cleaning' is the per-column null count of one block: koi_impact, koi_depth, koi_prad, koi_teq, koi_model_snr, koi_steff, koi_slogg, koi_srad are null on exactly the same 363 rows (koi_insol null on 321 of them). koi_tce_delivname and koi_tce_plnt_num are null on the same 346 rows, 91 of which overlap the block; union 618, plus one koi_kepmag-only row = 619. Dropped rows by koi_disposition: FALSE POSITIVE 499 (9.93% of FPs), CANDIDATE 112 (4.98%), CONFIRMED 8 (0.35%); by koi_pdisposition 500 FP / 119 CANDIDATE. 81% of the dropped rows are FPs, so the drop is class-biased and 'small volume' understates it.

*Verifier evidence:* check_a_nulls.py on data/raw/cumulative_kaggle_snapshot.csv: null cells 12698 after _err drop (matches cell 19), 3918 after fills, rows with any null 619, rows after dropna 8945; block columns share one 363-row set (True); TCE columns share one 346-row set (True); insol subset of block (True, 321); overlap 91; union 618; kepmag row outside that union; dropped 499/112/8, shares 9.93/4.98/0.35%. Deck wording '363 rows with nulls after cleaning' confirmed via project_search.

### 01-F6 — Kepler_Name is a near-perfect proxy for CONFIRMED and is retained (unflagged) in kepler_clean_full.pkl

> [!warning] medium · leakage · cells [21, 30, 31]

**Evidence**

Cell 21 fills the column rather than dropping it: `keplerProcessed_df["Kepler_Name"].fillna("unnamed", inplace = True)`; cell 30 pickles the frame with it: `kepler_clean_full = keplerProcessed_df.copy()`; only cell 31 removes it, and only from the processed frame. Nothing in the notebook notes that a Kepler name is assigned upon confirmation.

**Reproduction**

checks.py section B on the raw CSV: `pd.crosstab(raw['kepler_name'].notna(), raw['koi_disposition'])` -> named: CANDIDATE 0, CONFIRMED 2293, FALSE POSITIVE 1 (K00126.01 = Kepler-469 b, later reclassified); unnamed: CANDIDATE 2248, CONFIRMED 0, FALSE POSITIVE 5022. In kepler_clean_full.pkl 6,659 of 8,945 rows read 'unnamed'.

**Impact**

The modeling path in this notebook is safe (the column is dropped in cell 31), but kepler_clean_full.pkl is presented as the reusable 'full cleaned table' and any model built from it would score ~100% on CONFIRMED for the wrong reason. A rewrite that starts from a clean table must treat kepler_name, koi_score and koi_pdisposition as labels, not features.

**Recommendation**

Keep identifier/label columns in a separate `labels` table (kepoi_name, kepid, kepler_name, koi_disposition, koi_pdisposition, koi_score) and write the feature table without them; document the name-implies-confirmed rule in the notebook and in data/README.md.

**Verifier: ✅ confirmed**

*Corrected statement:* kepler_name is present iff the KOI is CONFIRMED, with one exception: named rows split CANDIDATE 0 / CONFIRMED 2,293 / FALSE POSITIVE 1 (K00126.01 = Kepler-469 b, koi_pdisposition FALSE POSITIVE); unnamed rows split 2,248 / 0 / 5,022. Cell 21 fills it with 'unnamed' instead of dropping it, cell 30 pickles it into kepler_clean_full.pkl (6,659 of 8,945 rows read 'unnamed'; the column list of the pickle includes Kepler_Name, Disposition_Using_Kepler_Data and Disposition_Score), and only cell 31 removes it from the model frame. No other notebook loads kepler_clean_full.pkl (02 and 05 load kepler_RAW.pkl, 03 and 04 load kepler_processed.pkl), so the exposure is to future code that starts from the 'full cleaned table'.

*Verifier evidence:* check_c_leakage.py: pd.crosstab(raw['kepler_name'].notna(), raw['koi_disposition']) = [[2248, 0, 5022],[0, 2293, 1]]; the one named FP is K00126.01 Kepler-469 b; (cf['Kepler_Name']=='unnamed').sum() = 6659 of 8945; printed cf.columns. grep over notebooks/*.ipynb: kepler_clean_full.pkl appears only in 01.

### 01-F7 — TCE_Delivery dummies, Transit_Epoch, RA and Dec are provenance/position features rather than physics, and koi_score missingness is structural

> [!note] low · methodology · cells [21, 32, 35, 58]

**Evidence**

Cell 32: `# This feature only has (3) values. We convert to dummies to include in the models` / `pd.get_dummies(keplerProcessed_df, columns=["TCE_Delivery"])`; cell 58 lists `Transit_Epoch_[BKJD]`, `right_ascension`, `declination` and the three `TCE_Delivery_*` dummies among the 23 features. Cell 21 fills koi_score with 'not_scored' without noting why it is missing.

**Reproduction**

checks.py section B: `pd.crosstab(raw['koi_tce_delivname'].fillna('<NaN>'), raw['koi_disposition'])` -> q1_q16_tce: 235 CAND / 1 CONF / 560 FP; q1_q17_dr24_tce: 149 / 3 / 216; q1_q17_dr25_tce: 1797 / 2281 / 3976; NaN: 67 / 8 / 271. So only 4 of 1,164 non-DR25 KOIs are CONFIRMED. `(raw['koi_score'].isna() == (raw['koi_tce_delivname'] != 'q1_q17_dr25_tce')).all()` -> True (score is null exactly when the KOI is not from the DR25 delivery). Section E: RF physics-only macro-F1 0.726 with the dummies, 0.723 without them, 0.717 after also removing ra/dec/Transit_Epoch (5-fold, random_state=0).

**Impact**

The delivery dummies encode 'was this KOI re-detected by the final DR25 pipeline', a pipeline-history fact that correlates with disposition; sky position and first-transit time have no physical bearing on planet-hood. They add little to the RF (0.726 -> 0.717) and muddy the 'physics-only' story. The 'not_scored' sentinel really means 'not a DR25 KOI'.

**Recommendation**

Exclude delivery, epoch, RA and Dec from the physics-only feature set (keep them for EDA and provenance), rename the score indicator to something like `is_dr25`, and do not hard-code 'only has (3) values': a live TAP pull can carry different delivery names.

**Verifier: ✅ confirmed**

*Corrected statement:* TCE delivery by koi_disposition on the raw table: q1_q16_tce 235 CAND / 1 CONF / 560 FP; q1_q17_dr24_tce 149 / 3 / 216; q1_q17_dr25_tce 1,797 / 2,281 / 3,976; missing 67 / 8 / 271, so only 4 of 1,164 non-DR25 KOIs are CONFIRMED. koi_score is null exactly when the delivery is not q1_q17_dr25_tce (1,510 = 1,510, elementwise equality True), so 'not_scored' means 'not a DR25 KOI'. Removing the three delivery dummies from the physics-only RF moves 5-fold macro-F1 from 0.726 to 0.723, and also removing right_ascension, declination and Transit_Epoch gives 0.717 (weighted-F1 0.760 -> 0.757 -> 0.752; accuracy 0.767 -> 0.763 -> 0.759). Low severity is right: small effect, but these columns are provenance/position, not transit physics.

*Verifier evidence:* check_c_leakage.py: crosstab of koi_tce_delivname (NaN filled) vs koi_disposition as stated; (raw['koi_score'].isna() == (raw['koi_tce_delivname'] != 'q1_q17_dr25_tce')).all() -> True; RF(200, random_state=0), StratifiedKFold(5, shuffle, random_state=0): physics-only 0.726/0.760/0.767; minus delivery 0.723/0.757/0.763 per-class [0.545, 0.775, 0.847]; minus delivery/ra/dec/epoch 0.717/0.752/0.759 per-class [0.534, 0.772, 0.846].

### 01-F8 — The notebook does not run top to bottom on a clean kernel: `plt` is never imported, TensorFlow is imported but unused and absent from the 2026 environment, and plot cells were re-run out of order

> [!warning] medium · reproducibility · cells [1, 40, 48, 49, 52]

**Evidence**

Cell 1 imports `tensorflow as tf`, `sqlalchemy`, `SVC`, `EnsembleVoteClassifier`, `plot_decision_regions`, `OneHotEncoder`, `NearestNeighbors`, `itertools`, `train_test_split` (none used) and no `matplotlib.pyplot`. Cell 48: `plt.figure(figsize=(10,10))` ... `plt.show()` with output `<Figure size 720x720 with 1 Axes>`. Execution counts: cells 1-63 ran as 1..37 in order, but cell 52 shows `exec 82`, cell 40 `exec 84`, cell 49 `exec 88`. Kernel metadata: Python 3.7.6, kernel 'PythonData'.

**Reproduction**

Notebook JSON scan (checks.py section C): cells importing matplotlib: [] ; cells using `plt.`: [48, 54]. Import check in the uv environment: `import tensorflow` -> ModuleNotFoundError (not installed; pyproject does not list it), sqlalchemy/mlxtend/plotly/seaborn/scipy import fine. How `plt` was defined when cell 48 executed in 2020 is unverified (no cell defines it; a kernel startup file is the likely explanation).

**Impact**

Cell 1 fails immediately in the refreshed environment, and after fixing that, cell 48 raises NameError on a fresh kernel. Out-of-order execution counts mean the saved outputs were not produced by a single clean run.

**Recommendation**

Trim imports to what is used, add `import matplotlib.pyplot as plt`, and adopt a 'Restart kernel and run all' before every commit (or run the notebook with `jupyter nbconvert --execute` in CI).

**Verifier: 🟡 partially**

*Corrected statement:* The notebook does not run top to bottom on a clean kernel, and the reviewer understated it: in the uv environment cell 1 fails on `import tensorflow as tf` AND on `import sqlalchemy` (ModuleNotFoundError for both; neither is in pyproject.toml and 'sqlalchemy' has zero mentions in uv.lock), whereas the reviewer stated sqlalchemy imports fine. mlxtend 0.25.0, plotly 6.9.0, seaborn 0.13.2, scipy and matplotlib 3.11.1 do import. No cell imports matplotlib, yet cell 48 uses plt.figure/plt.title/plt.show and has output '<Figure size 720x720 with 1 Axes>' (raw cell 54 also uses plt.plot); how plt was bound in 2020 is unverified. Execution counts run 1..37 in cell order except cell 40 (84), cell 49 (88) and cell 52 (82); kernel metadata: 'PythonData', Python 3.7.6. Outputs account for about 5.85 MB of the 5.95 MB file.

*Verifier evidence:* Inline import check via uv run python: tensorflow FAIL (ModuleNotFoundError), sqlalchemy FAIL (ModuleNotFoundError), mlxtend/plotly/seaborn/scipy/matplotlib OK; `uv pip list` shows no sqlalchemy; grep -c sqlalchemy uv.lock -> 0; pyproject dependencies lines 12-28 list neither. check_d_nbscan.py: cells importing matplotlib = []; cells using plt. = [48 code, 54 raw]; exec counts >37 at cells 40, 49, 52; kernelspec PythonData / language_info 3.7.6; cell 48 output text as quoted.

### 01-F9 — Dead code: Postgres cells with a live-looking AWS RDS endpoint, no-op and stale cells

> [!note] low · dead-code · cells [6, 7, 8, 9, 10, 11, 17, 26, 37, 42, 50]

**Evidence**

Cell 6 (raw): `userID='postgres'` / `password=''` / `endpoint='kepler-exoplanet.cotbxoedtrfv.us-east-1.rds.amazonaws.com'` / `db_string = f"postgres://{userID}:{password}@{endpoint}:{port}/{dbinstance}"`; cells 7-11 reflect and read `raw_kepler`. Cell 37 (raw): `sp.variation(keplerProcessed_df["koi_period"])` uses the pre-rename column name. Cell 42: `#covMatrix = np.cov(keplerProcessed_df,bias=True)` (would compute a rows-by-rows 8945 x 8945 matrix, hence 'long runtime'). Cell 50: `# Correlation matrix on selected features` recomputes the same matrix; no features were selected. Cell 26 is an empty MICE stub. Cell 17's rename map contains `'kepoi_name' : 'KOI_Name'` (already the index) and `koi_smet`/`koi_smass` (not in this file), all no-ops.

**Reproduction**

Not run: the RDS instance is unreachable/offline by design (no network in this review) and the cells are raw. Notebook scan confirms cells 6 and 10 contain the endpoint/`create_engine` and that the only executed code path reads the CSV (cell 4).

**Impact**

Confuses readers about where the data comes from (the CSV is the only real source), leaves an infrastructure hostname and username in a public repository, and pads the notebook. `np.cov` on the frame would be along the wrong axis if ever uncommented.

**Recommendation**

Delete the database cells (the schema is preserved in archive/database/), the stub and no-op cells, and the unused rename keys; note in data/README.md that the 2020 Postgres copy was a straight import of the same CSV.

**Verifier: ✅ confirmed**

*Corrected statement:* Cells 6-11 are raw and never executed; cell 6 holds `userID='postgres'`, `password=''`, `endpoint='kepler-exoplanet.cotbxoedtrfv.us-east-1.rds.amazonaws.com'` and `create_engine(db_string)` (the endpoint and create_engine are in cell 6 only; cell 10 contains `inspect(engine)`, a small imprecision in the reviewer's wording). The only executed data source is cell 4's read_csv. Cell 17's rename map contains 'kepoi_name' (already the index after cell 15) and 'koi_smet'/'koi_smass', which do not exist in the 50-column file, all no-ops. Cell 37 (raw) references the pre-rename 'koi_period'; cell 42 is entirely commented (np.cov on the frame would treat rows as variables, 8,945 x 8,945); cell 50 recomputes the same correlation matrix under a 'selected features' comment; cell 26 is an empty MICE stub. Not run against the RDS host (no network; cells are raw).

*Verifier evidence:* check_d_nbscan.py: regex for 'rds.amazonaws|create_engine(' matches cell 6 (raw) only; rename keys absent from raw columns = ['koi_smet', 'koi_smass'], 'kepoi_name' present in keys; view cells 6-11, 26, 37, 42, 50 re-read and quotes match.

### 01-F10 — Disposition_Score becomes a mixed float/str column ('not_scored') that pandas will refuse to create in a future version

> [!note] low · bug · cells [21, 30]

**Evidence**

Cell 21: `keplerProcessed_df["Disposition_Score"].fillna("not_scored", inplace = True)` on a float64 column; cell 30 pickles it into kepler_clean_full.pkl.

**Reproduction**

checks.py section D: `cf['Disposition_Score'].map(type).value_counts()` on data/legacy/kepler_clean_full.pkl -> {float: 7994, str: 951}; dtype object. Running the fill under pandas 2.3.3 emits `FutureWarning: Setting an item of incompatible dtype is deprecated and will raise an error in a future version of pandas. Value 'not_scored' has dtype incompatible with float64`. Downstream grep: no notebook loads kepler_clean_full.pkl (02 and 05 load kepler_RAW.pkl; 03 and 04 load kepler_processed.pkl), so the damage is contained today.

**Impact**

Any numeric use of the score (sorting, thresholds, plotting) on the 'full cleaned table' fails or silently coerces; the code will raise outright under a future pandas.

**Recommendation**

Keep koi_score as float with NaN and add a boolean `is_dr25`/`score_missing` column; never store sentinel strings in numeric columns.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell 21 writes the string 'not_scored' into the float64 Disposition_Score column and cell 30 pickles the result: in data/legacy/kepler_clean_full.pkl the column has dtype object with 7,994 float and 951 str values. Under pandas 2.3.3 the fill emits FutureWarning 'Setting an item of incompatible dtype is deprecated and will raise an error in a future version of pandas. Value not_scored has dtype incompatible with float64'. Only notebook 01 touches kepler_clean_full.pkl, so the damage is contained today.

*Verifier evidence:* check_c_leakage.py: cf['Disposition_Score'].map(type).value_counts() -> {float: 7994, str: 951}, dtype object. check_b_cow.py captured the FutureWarning text when running cell 21 verbatim. grep over notebooks/*.ipynb for kepler_clean_full.pkl -> only 01_cleaning_eda.ipynb.

### 01-F11 — pandas drift: get_dummies now yields bool (pickle has uint8) and the cell-39 ratio table silently loses the three delivery dummies

> [!note] low · reproducibility · cells [32, 35, 39, 40, 45, 46]

**Evidence**

Cell 39: `num_columns = keplerProcessed_df.dtypes[keplerProcessed_df.dtypes != "object"].index.tolist()` / `stats_df = variance_df.describe().loc[['mean', 'std']]`; its 2020 output lists `TCE_Delivery_q1_q17_dr24_tce 0.035774 0.185737` and `TCE_Delivery_q1_q16_tce 0.070542 0.256073`. Cells 45/46 use `np.bool`.

**Reproduction**

checks.py section C under pandas 2.3.3 / numpy 2.5.2: `pd.get_dummies(...)` dummy dtype -> [bool] (legacy pickle: uint8); `describe()` on the 23 non-object columns returns 20 columns, missing ['TCE_Delivery_q1_q16_tce', 'TCE_Delivery_q1_q17_dr24_tce', 'TCE_Delivery_q1_q17_dr25_tce'] (bool columns are summarised as categorical and excluded from a mixed describe). `np.bool is np.bool_` -> True in numpy 2.x (the alias was removed in numpy 1.24-1.26 and restored in 2.0), so cells 45/46 happen to work today.

**Impact**

The variance bar chart (cell 40) changes without any error, and pickled dtypes differ between 2020 and a rerun; StandardScaler handles bool fine, so models are unaffected.

**Recommendation**

Pass `dtype=int` (or float) to get_dummies, select numeric columns with `select_dtypes('number')`, replace `np.bool` with `bool`, and write parquet with explicit dtypes instead of pickles.

**Verifier: ✅ confirmed**

*Corrected statement:* pd.get_dummies now produces bool dummy columns (the 2020 pickle has uint8), and cell 39's `variance_df.describe().loc[['mean','std']]` silently omits the three TCE_Delivery_* columns because bool columns are summarised as categorical in a mixed describe(): on my rerun 24 non-object columns (23 features + target) went in and 21 came out, missing exactly the three dummies, whereas the 2020 output of cell 39 lists TCE_Delivery_q1_q17_dr24_tce (0.035774 / 0.185737) and TCE_Delivery_q1_q16_tce (0.070542 / 0.256073). The reviewer's '23 -> 20' count excluded the target; same three columns missing. np.bool is np.bool_ under numpy 2.5.2, so cells 45/46 run today (the alias was absent in numpy 1.24-1.26). corr() and var() still work on the bool frame. Models are unaffected.

*Verifier evidence:* check_b_cow.py (CoW off): get_dummies dtypes [bool]; n num_columns 24; describe() columns 21, missing ['koi_tce_delivname_q1_q16_tce', 'koi_tce_delivname_q1_q17_dr24_tce', 'koi_tce_delivname_q1_q17_dr25_tce']; np.bool is np.bool_ -> True; proc.var() OK (24), proc.corr() OK (24, 24). check_a_nulls.py: legacy pickle dummy dtype uint8 vs my rerun bool.

### 01-F12 — Target encoding is undocumented and unpersisted, and the target is stored inside the feature table where it is treated as a numeric feature

> [!note] low · documentation · cells [33, 35, 38, 39, 44, 52]

**Evidence**

Cell 33: `le = LabelEncoder()` / `keplerProcessed_df['Exoplanet_Archive_Disposition'] = le.fit_transform(...)`; `le` is never saved and the mapping is never printed. Cell 38 output lists `Exoplanet_Archive_Disposition 6.733551e-01` as the first variance; cell 44 correlates it with the features; cell 52 histograms it with the features. The archived web app relies on the mapping implicitly: archive/webapp_flask_2020/app.py `if prediction > 1: output = "Exoplanet not predicted..."` and `model.predict(...)[0][2]` for the neural net.

**Reproduction**

checks.py section D: `LabelEncoder().fit(cf['Exoplanet_Archive_Disposition']).classes_` -> ['CANDIDATE', 'CONFIRMED', 'FALSE POSITIVE'], i.e. CANDIDATE=0, CONFIRMED=1, FALSE POSITIVE=2 (alphabetical); processed target counts {0: 2136, 1: 2285, 2: 4524}.

**Impact**

Anyone reading the pickle must guess the code-to-class map; the arbitrary ordinal order also feeds the SFS regression in 01-F4 and makes the target's correlations/variance in the EDA meaningless.

**Recommendation**

Persist the mapping (a small JSON next to the data, or keep the string labels and encode inside the model pipeline), store y separately from X, and exclude the target from feature-statistics cells.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell 33 fits a LabelEncoder on Exoplanet_Archive_Disposition and never prints or saves the mapping; it is alphabetical: CANDIDATE=0, CONFIRMED=1, FALSE POSITIVE=2, with processed counts {0: 2136, 1: 2285, 2: 4524}. The encoded target sits inside kepler_processed.pkl and is treated as a feature by cell 38 (var, first row 6.733551e-01), cell 44 (corr) and cell 52 (histogram grid). archive/webapp_flask_2020/app.py depends on the mapping implicitly (line 60 `model.predict(...)[0][2]`, line 72 `if prediction > 1:`).

*Verifier evidence:* check_a_nulls.py: LabelEncoder().fit(...).classes_ -> ['CANDIDATE', 'CONFIRMED', 'FALSE POSITIVE']; target counts {0: 2136, 1: 2285, 2: 4524}; grep of app.py shows lines 60 and 72 as quoted; view cells 38, 44, 52 re-read.

### 01-F13 — Chart bugs: field-of-view hover labels show the wrong quantities and the period-radius scatter's colorscale is a no-op

> [!note] low · bug · cells [61, 62]

**Evidence**

Cell 61 plots `x=kepler_confirmed["right_ascension"], y=kepler_confirmed["declination"]` but every trace's `hovertemplate = "...Orbital_Period_[days]: %{x}<br>" + "Planetary_Radius_[Earth radii]: %{y}..."`. Cell 62: `marker=dict(size=4, colorscale="Tealgrn")` and `colorscale="Sunsetdark"` without a `color=` array, so plotly ignores the colorscale and uses default trace colours. Cell 61 also hard-codes `color="blue"` for candidates.

**Reproduction**

Not run: figure-level inspection from the quoted code; the label mismatch is visible in the source and does not depend on data.

**Impact**

Hovering over the sky map reports RA as an orbital period and Dec as a planet radius; the intended colour encoding in the period-radius chart never appears.

**Recommendation**

Fix the hover templates, use `color=<column>` with a warm colorscale, and apply the repo's no-blue chart rule when the figures are recreated.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell 61 plots x=right_ascension, y=declination but all three hovertemplates read 'Orbital_Period_[days]: %{x}' and 'Planetary_Radius_[Earth radii]: %{y}', and the CANDIDATE trace hard-codes color="blue". Cell 62 sets marker colorscale twice ('Tealgrn', 'Sunsetdark') with no marker color array (zero 'color=' occurrences), and in plotly a marker colorscale only applies when marker.color is a numeric array, so the default trace colours are used. Verified from source; the figures were not rendered in this session.

*Verifier evidence:* check_d_nbscan.py: cell 61 contains x=kepler_confirmed["right_ascension"], 'Orbital_Period_[days]: %{x}' and color="blue" (all True); cell 62 has 2 'colorscale=' and 0 'color=' matches. Colorscale behaviour is plotly's documented semantics for marker.colorscale, not something I rendered.
