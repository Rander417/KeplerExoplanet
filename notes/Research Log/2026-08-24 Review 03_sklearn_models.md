---
tags: [research-log, review, notebook-03]
date: 2026-08-24
source: multi-agent review workflow wf_29148ee0-552 (reviewer + adversarial verifier)
---

# 2026-08-24 Review: Notebook 03 sklearn models

> [!abstract] What the notebook does (reviewer's summary)
> Notebook 03 loads the 2020 pickle kepler_processed.pkl (8,945 KOIs x 24 columns, verified by loading it: the LabelEncoded archive disposition 0=CANDIDATE 2,136 / 1=CONFIRMED 2,285 / 2=FALSE POSITIVE 4,524, plus 23 numeric features: the four koi_fpflag_* flags, transit/planet/stellar parameters, TCE planet number, RA/Dec, Kepler magnitude and three TCE-delivery dummies; koi_score and koi_pdisposition were already dropped in notebook 01). Cell [10] splits with train_test_split(random_state=1, stratify=y) at the default 25% test size (6,708 train / 2,237 test), cell [12] fits a StandardScaler on the training rows only, and cells [14]-[35] train and evaluate three classifiers on the single held-out split: multinomial logistic regression (lbfgs, max_iter=200), a 20-tree GradientBoostingClassifier whose learning rate was picked by a sweep scored on the test set, and imbalanced-learn's BalancedRandomForestClassifier (100 trees). Each gets accuracy (balanced accuracy for BRF), a confusion matrix, and a classification report. Cells [38]-[56] repeat split/scale/fit for a 17-feature subset (dropping TCE_Planet_Number, RA/Dec and the delivery dummies) for the Flask web app, print one accuracy per model, and contain commented-out joblib.dump calls that once wrote SLR.pkl, GBT.pkl and BRF.pkl; the app's scaler was exported from notebook 04 instead. As committed, the notebook writes no files; the archived pickles live in archive/webapp_flask_2020/model/. Execution counts run 1..36 in order, so the committed outputs come from one top-to-bottom run. I reproduced the LR confusion matrix and accuracy (0.8324) exactly, the GBT to within one test row (0.9021 vs 0.9017), and the BRF exactly (0.8652) once imbalanced-learn 0.7.0's defaults were restored.

> [!warning] At a glance
> **12 findings**: 3 high · 5 medium · 4 low. Verifier verdicts: 12 confirmed · 0 partially · 0 refuted · 0 unverifiable. Verifier added 3 missed item(s). 10 deck/README claims checked.

## Findings at a glance

| ID | Severity | Category | Finding | Verifier |
|---|---|---|---|---|
| 03-F1 | high | leakage | The four FP-flag columns supply most of the score; the 0.99 FALSE POSITIVE f1 is entirely a flag lookup | ✅ confirmed |
| 03-F2 | high | bug | Cell [44] scores a stale y_pred: the printed 0.8994 web-app LR accuracy is the 23-feature BRF's predictions, not the 17-feature LR | ✅ confirmed |
| 03-F3 | high | methodology | The web-app models do not share the neural-net notebook's scaler: each notebook fits its own on a different split, and the archived scaler matches neither | ✅ confirmed |
| 03-F4 | medium | claim-vs-data | The 83 / 90 / 90 '% f1' figures are accuracy and weighted-average f1, not macro f1; macro f1 is 0.77 / 0.87 / 0.87 | ✅ confirmed |
| 03-F5 | medium | methodology | GBT hyperparameters were selected on the test set, with a sweep that used different max_features than the final model, on a single split with no variance estimate | ✅ confirmed |
| 03-F6 | medium | reproducibility | BalancedRandomForestClassifier result depends on imbalanced-learn version defaults; modern defaults give a different answer | ✅ confirmed |
| 03-F7 | medium | dead-code | Notebook cannot run in the 2026 environment and cannot regenerate the archived pickles: unused tensorflow import, commented-out exports, 25 unused imports, and legacy pickles that no longer load | ✅ confirmed |
| 03-F8 | medium | claim-vs-data | The 'chosen to better handle the data imbalance' framing does not match what the code does or what the data shows | ✅ confirmed |
| 03-F9 | low | documentation | Markdown comparison cells [45], [50], [55] quote numbers from an earlier run that contradict the outputs directly above them | ✅ confirmed |
| 03-F10 | low | methodology | The logistic-regression 'feature importance' table is the signed CANDIDATE-class coefficient vector, stored as strings, with the strongest features at the bottom | ✅ confirmed |
| 03-F11 | low | methodology | The 23-feature model includes catalog-provenance features (TCE delivery name, RA/Dec) that encode when/where a KOI was catalogued rather than physics | ✅ confirmed |
| 03-F12 | low | other | Web-app integration: column order matches, but the app reports a CANDIDATE prediction as 'Exoplanet predicted!!!' and relies on a name-less scaler that a modern re-export would break | ✅ confirmed |

## Deck / README claims checked

| Verdict | Claim | Evidence |
|---|---|---|
| 🟡 partially | Deck/README: logistic regression 83% f1 | Notebook cell [19] accuracy 0.8323647742512293; cell [22] weighted-avg f1 0.83, macro-avg f1 0.77. My run (repro_full.py, same split): accuracy 0.8324, f1 weighted 0.8298, f1 macro 0.7729, per-class [0.6278, 0.7001, 0.9908]. So 83% is accuracy / weighted f1; macro f1 is 77%. |
| 🟡 partially | Deck/README: gradient boosted tree 90% f1 | Cell [27] accuracy 0.9016540008940546; cell [29] weighted f1 0.90, macro f1 0.87. My run: accuracy 0.9021, f1 weighted 0.9015, f1 macro 0.8706, per-class [0.8045, 0.8172, 0.9899] (one test row differs from the notebook, sklearn version). 90% is accuracy / weighted f1; macro f1 is 87%. Without the four flags: macro f1 0.7118. |
| 🟡 partially | Deck/README: random forest 90% f1 | Cell [35] imbalanced report 'avg / total' f1 0.90 (support-weighted); cell [32] balanced accuracy 0.8652. My run with imblearn 0.7 defaults: accuracy 0.8994, f1 weighted 0.8987, f1 macro 0.8670, balanced accuracy 0.8652, per-class [0.7989, 0.8131, 0.9890]. 90% is weighted f1 / accuracy; macro f1 is 87%. |
| ✅ confirmed | README: training and testing set split in default manner, 75% train / 25% test | Cell [10] uses train_test_split with no test_size; output (6708, 23). My run: X_train (6708, 23), X_test (2237, 23), train frac 0.7499; 6708 + 2237 = 8945. |
| ✅ confirmed | README: processed dataframe is scaled with StandardScaler before the models are run | Cell [12]: `X_scaler = scaler.fit(X_train)` then transform of train and test; the scaler is fit on training rows only (no leakage from the test rows). Reproduced; note the tree models do not need it, and the app-side scaler is a different object (03-F3). |
| ❌ refuted | Deck: random forest and GBT were chosen to better handle the data imbalance | GBT in cell [25] has no class_weight/sample_weight; only BRF (cell [31]) resamples. Class shares 23.9/25.5/50.6%. LR with class_weight='balanced' changes macro f1 from 0.7729 to 0.7720 and accuracy from 0.8324 to 0.8306, so imbalance is not the cause of LR's weaker result; GBT balanced accuracy 0.8691 vs BRF 0.8652. The BRF part of the claim is true by construction; the GBT part is not. |
| 🟡 partially | Notebook: the web-app models are retrained on 17 features and share the scaler exported from the neural-net notebook | Retraining on 17 features is confirmed (cell [39] output (6708, 17); the 17-feature split has identical rows to the 23-feature split: True). Scaler sharing is refuted for the committed code: cell [40] fits its own scaler; notebook 04 stratifies on a one-hot y which yields a different split (5,036 of 6,708 training rows shared; 1,672 of the 2,237 sklearn test rows are NN training rows); the archived scaler_param.joblib matches neither split (no exact match over random_state 0..100 x 5 stratify modes) and serving the notebook's tree models through it changes 12-16% of test predictions. |
| ✅ confirmed | Focus: random_state and stratification | Both splits use random_state=1, stratify=y (cells [10], [39]); test support 534/572/1131 matches the class proportions; the split is fully reproducible (LR confusion matrix [[307,219,8],[135,426,11],[2,0,1129]] reproduced exactly). |
| ✅ confirmed | Focus: train/test contamination between the full and reduced models | No row-level contamination: the 23- and 17-feature splits put identical rows in train and test (index equality True). What does carry over is the stale y_pred in cell [44] (03-F2) and the test-set-tuned GBT learning rate reused in cell [48] (03-F5). |
| ⚪ unverified | README: neural net 84% f1 (context only, from notebook 04) | TensorFlow/Keras is not installed; not retrained. Notebook 04 cell [18] output shows accuracy 0.85, macro f1 0.80, weighted f1 0.85 on its own split, so 84% appears to be an accuracy-type number there too, but I did not run it. |

## What the verifier added (missed by the reviewer)

> [!warning] The 2020 web app's verdict is decided by the four flag dropdowns; the 13 numeric inputs are nearly decorative (medium)
> Consequence of F1 at the deliverable level, not stated by the reviewer. Inline probe (this session): for the notebook's own 17-feature LR, GBT and BRF (imblearn-0.7 defaults), the app's binary verdict ('planet' = predicted class <= 1) equals 'no flag ticked' on 99.9%, 99.9% and 99.8% of the 2,237 test rows (LR: 1 flagged row called planet, 1 unflagged row called not-planet; GBT 3/0; BRF 2/2); the archived SLR.pkl + scaler_param.joblib agree with 'no flag ticked' on 99.9%. With main.html's default values (all flags 0) the archived SLR returns class 0 -> 'Exoplanet predicted!!!', and setting any single one of the four flag dropdowns to 1 flips it to class 2 -> 'Exoplanet not predicted...'. For the Phase 5 app this means a physics-only model is the only way the app demonstrates any machine learning; with the flags as inputs it is a four-checkbox lookup.

> [!warning] The LR's gap to the tree models is mostly untransformed heavy tails, not model class or imbalance; log1p closes most of it (medium)
> The reviewer's rewrite list mentions log transforms but nothing was measured, and F8 attributes the tree advantage to 'nonlinearity'. v_missed_probes.py: after cell [12]'s StandardScaler, 95.3% of training rows sit within |z| < 0.1 on Insolation_Flux (max z 53.0, raw skew 36.0) and 99.2% within |z| < 0.1 on Planetary_Radius (max z 57.8, skew 48.9), so the linear model effectively cannot use those columns. Applying log1p to 7 heavy-tailed columns (period, depth, planetary radius, insolation, SNR, stellar radius, duration; all minima >= 0) before the same scaler and the same LogisticRegression(lbfgs, max_iter=200, random_state=1) on the same split lifts LR from accuracy 0.8324 / balanced accuracy 0.7726 / macro f1 0.7729 (per-class 0.63/0.70/0.99) to 0.8856 / 0.8465 / 0.8478 (0.77/0.78/0.99), within 0.023 macro f1 of the GBT's 0.8706; without the flags, log1p LR reaches macro f1 0.6713 vs 0.5625. The 2020 LR had converged (n_iter_ 50 of 200), so this is a preprocessing effect, not an optimisation one.

> [!note] Notebook 03 never states which integer is which class; the 0/1/2 mapping is implicit everywhere, including the app's `prediction > 1` rule (low)
> grep of the view: zero occurrences of CANDIDATE, CONFIRMED or FALSE POSITIVE in notebook 03; confusion matrices and reports are labelled 'Actual 0/1/2' and '0 1 2'. The mapping comes from LabelEncoder's alphabetical order in notebook 01 cell [33] and is only recoverable by joining the pickle index to the raw CSV's koi_disposition (which I did: 0 = CANDIDATE 2,136, 1 = CONFIRMED 2,285, 2 = FALSE POSITIVE 4,524, exact). app.py hardcodes the same ordering (`if prediction > 1`). CLAUDE.md's 'Two Ys' guardrail asks every model notebook to say the target explicitly; the rewrite should carry class names through classification_report(target_names=...) and the confusion-matrix labels.


## Keep (what the rewrite should preserve)

- Stratified train/test split with a fixed random_state (cells [10], [39]); it reproduces exactly six years later and gives the reduced and full models an identical test set, so their comparison is apples-to-apples.
- StandardScaler fit on the training rows only and applied to test (cell [12]); no test-set statistics leak into the scaler.
- Per-model confusion matrix plus a full classification report (cells [20]-[22], [28]-[29], [33]-[35]); the per-class numbers are all there, which is what let the metric ambiguity be resolved.
- Balanced accuracy and imbalanced-learn's classification_report_imbalanced for the BRF (cells [32], [35]); the right instincts about imbalance-aware metrics, worth extending to all models.
- The learning-rate sweep printing train vs held-out accuracy side by side (cell [24]) is a good overfitting diagnostic pattern; it only needs to run on a validation fold instead of the test set.
- Explicit choice of the three-class archive disposition (koi_disposition) as the target, consistent with the project's 'two Ys' decision.
- The notebook was executed top-to-bottom in one pass (execution counts 1..36 in order), so its committed outputs are a trustworthy record of one run.
- The idea of a reduced, physically meaningful feature set for the app (dropping RA/Dec, delivery name, planet number) is sound; it just needs to be a documented decision in shared code.

## Rewrite recommendations

- Before changing anything, add a regression test that rebuilds the 2020 pipeline from data/legacy/kepler_processed.pkl and asserts the LR confusion matrix [[307,219,8],[135,426,11],[2,0,1129]] and BRF balanced accuracy 0.8652 (with sampling_strategy='auto', replacement=False, bootstrap=True); this pins the baseline the refresh is measured against.
- Report every model in two variants, 'with flags' and 'physics-only' (no koi_fpflag_*, no koi_score), with macro f1, balanced accuracy and per-class f1, plus the trivial 'any flag -> FALSE POSITIVE' baseline (acc 0.755, FP f1 0.991 on this split). Never print a bare accuracy or weighted f1.
- Replace the single split with StratifiedKFold(5) cross-validation for model comparison and hyperparameter search (GridSearchCV/RandomizedSearchCV on the training rows); hold the test set back for one final number and report CV mean +/- std (fold std here was 0.006-0.014 macro f1, larger than the GBT-vs-BRF gap).
- Build each model as one sklearn Pipeline (scaler + estimator, or estimator alone for trees) and save pipeline + a JSON sidecar (feature names in order, library versions, split seed, metrics) to models/ via kepler.paths; the app loads the pipeline and asserts its input columns equal pipeline.feature_names_in_. Delete the cross-notebook scaler hand-off.
- Put the feature list in src/kepler/features.py with a justification per column: exclude TCE delivery name and RA/Dec from the physics variant; decide explicitly about TCE_Planet_Number (multiplicity is a real prior: 21% CONFIRMED for planet number 1 vs 47-57% for 2-4 in this table).
- Consider log-transforming the heavy-tailed inputs (transit depth, insolation flux, SNR, planetary radius) before the linear model; the archived-scaler episode showed a 75% subsample can shift the insolation mean by 57%, which is what makes StandardScaler + LR fragile here.
- Revisit the target. CANDIDATE vs CONFIRMED is partly a follow-up-status label, not a physical one: per data/README.md (not measured by me) the archive moved from 2,293 CONFIRMED / 2,248 CANDIDATE in the 2020 snapshot to 2,747 / 1,978 on 2026-08-24. A physics-only model cannot separate 'real planet, not yet confirmed' from 'real planet, confirmed', which caps the no-flags macro f1 near 0.71. Options: a binary planet-vs-false-positive target, or using the 2026 live labels as a time-forward test set for models trained on the 2020 snapshot.
- Fix the notebook hygiene items in one pass: remove the tensorflow import and the 24 other unused imports, stop reusing `classifier`/`y_pred` across sections (one function per model that returns predictions and a metrics dict), generate comparison text from variables, and replace the coefficient 'importance' table with per-class |coef| or permutation importance on held-out data.
- For the Phase 5 app, show the three class probabilities and phrase CANDIDATE as 'not yet confirmed' rather than 'exoplanet predicted'; keep the app pure-Python/scikit-learn so it can run under stlite as CLAUDE.md requires.

## Finding details

### 03-F1 — The four FP-flag columns supply most of the score; the 0.99 FALSE POSITIVE f1 is entirely a flag lookup

> [!danger] high · leakage · cells [8, 22, 29, 35]

**Evidence**

Cell [8]: `X = keplerProcessed_df.drop(["Exoplanet_Archive_Disposition"], axis =1)` keeps Not_Transit-Like_FPF, Stellar_Eclipse_FPF, Centroid_Offset_FPF, Ephemeris_Match_Indicates_Contamination_FPF. Cell [22] output: class 2 f1-score 0.99, class 0 0.63, class 1 0.70. Cell [29]: class 2 0.99. Cell [35]: class 2 f1 0.99.

**Reproduction**

leakage.py: refit LR/GBT/BRF (notebook hyperparameters, same split/scaler) on feature subsets. Printed (test set, 2,237 rows):
all 23 (notebook): LR acc 0.8324 f1_macro 0.7729 f1_FP 0.9908 | GBT acc 0.9021 f1_macro 0.8706 f1_FP 0.9899 | BRF acc 0.8994 f1_macro 0.8670 f1_FP 0.9890
19 = 23 minus 4 flags: LR acc 0.6603 f1_macro 0.5625 f1_FP 0.7962 | GBT acc 0.7506 f1_macro 0.7118 f1_FP 0.8373 | BRF acc 0.7313 f1_macro 0.7112 f1_FP 0.8080
4 flags only: LR acc 0.7550 f1_macro 0.5550 f1_CAND 0.0000 f1_FP 0.9908
Rule 'any flag -> FP, else class 1': acc 0.7550 f1_FP 0.9908; confusion [[0,527,7],[0,560,12],[0,2,1129]]
Test rows: any-flag & FP = 1129 ; any-flag & not-FP = 19 ; no-flag & FP = 2 ; no-flag & not-FP = 1087
5-fold stratified CV (scaler inside pipeline): GBT f1_macro 0.8635+/-0.0083 with flags vs 0.7209+/-0.0111 without; BRF 0.8681+/-0.0137 vs 0.7210+/-0.0045; LR 0.7689+/-0.0058 vs 0.5576+/-0.0130.
Whole table (my run): any flag set -> FALSE POSITIVE in 4,516 of 4,602 rows; no flag -> not FP in 4,335 of 4,343.

**Impact**

The headline '90%' is roughly half a lookup of the archive's own vetting flags: the flags-only model reaches the same FP f1 (0.9908) as the full LR, and removing them drops GBT macro f1 from 0.87 to 0.71 and accuracy from 0.90 to 0.75. Every number in the deck/README is the with-flags variant, which the CLAUDE.md guardrail says must never be quoted alone.

**Recommendation**

Report two variants per the science guardrails: 'with flags' (reproduces the Kepler vetting logic; FP class is solved by the flags) and 'physics-only' (no koi_fpflag_*, no koi_score). Put the trivial rule 'any flag -> FP' in as the baseline every model must beat, and make clear that the real modelling problem is CANDIDATE vs CONFIRMED (macro f1 ~0.71 without flags).

**Verifier: ✅ confirmed**

*Corrected statement:* With the notebook's split (random_state=1, stratify) and hyperparameters, dropping the four koi_fpflag_* columns takes GBT from accuracy 0.9021 / macro f1 0.8706 to 0.7506 / 0.7118 (LR 0.8324 / 0.7729 -> 0.6603 / 0.5625; BRF 0.8994 / 0.8670 -> 0.7313 / 0.7112). The four flags alone, or the rule 'any flag -> FALSE POSITIVE else CONFIRMED', reach accuracy 0.7550 and FP-class f1 0.9908, identical to the full LR's FP f1 and above the GBT's 0.9899, so the 0.99 FP f1 is a flag lookup. 5-fold stratified CV agrees (GBT macro f1 0.8635+/-0.0083 with flags vs 0.7209+/-0.0111 without). Of the with-flags GBT's 219 remaining test errors, 196 (89%) are CANDIDATE<->CONFIRMED swaps.

*Verifier evidence:* Re-ran independently (v_leakage.py, own code). all-23: LR acc 0.8324 f1_macro 0.7729 f1_FP 0.9908 | GBT 0.9021 / 0.8706 / 0.9899 | BRF 0.8994 / 0.8670 / 0.9890. no-flags (19): LR 0.6603 / 0.5625 / 0.7962 | GBT 0.7506 / 0.7118 / 0.8373 | BRF 0.7313 / 0.7112 / 0.8080. flags-only LR: acc 0.7550, f1_CAND 0.0000, f1_FP 0.9908. Rule confusion [[0,527,7],[0,560,12],[0,2,1129]]; test rows any-flag&FP 1129, any-flag&notFP 19, noflag&FP 2, noflag&notFP 1087; whole table 4516/4602 and 4335/4343. CV5 (StratifiedKFold shuffle rs=1, scaler in pipeline): LR 0.7689+/-0.0058 vs 0.5576+/-0.0130; GBT 0.8635+/-0.0083 vs 0.7209+/-0.0111; BRF 0.8681+/-0.0137 vs 0.7210+/-0.0045. Every reviewer number matches mine to 4 decimals. GBT permutation importance on the test set (v_missed_probes.py): the four flags are ranks 1,2,4,5 (0.189, 0.153, 0.129, 0.065 macro f1). Error split 196/219 from my GBT confusion matrix. Severity high is proportionate given the CLAUDE.md leakage guardrail.

### 03-F2 — Cell [44] scores a stale y_pred: the printed 0.8994 web-app LR accuracy is the 23-feature BRF's predictions, not the 17-feature LR

> [!danger] high · bug · cells [32, 43, 44, 45]

**Evidence**

Cell [43] trains the 17-feature LR (`classifier.fit(X_train_scaled, y_train)`) but never predicts. Cell [44]: `print(accuracy_score(y_test,y_pred))` -> `0.8994188645507376`. The last assignment to y_pred is cell [32]: `y_pred = brf_model.predict(X_test_scaled)` on the 23-feature BRF. Markdown [45] then concludes '<b>Small increase in accuracy: 0.8971837282074206 vs. 8292355833705856 previously</b>'.

**Reproduction**

stale_and_scaler.py: trained the 23-feature BRF (imblearn 0.7 defaults) exactly as cells [10]-[32], took its y_pred, then made the 17-feature split of cell [39] and scored that y_pred against its y_test. Printed:
(2) 23-feat and 17-feat splits share identical train/test row indices: True
(1) cell [44] as written, accuracy_score(y_test_17, stale BRF23 y_pred) = 0.8994188645507376
    notebook printed                                                  0.8994188645507376
    true 17-feature LR accuracy                                       = 0.8176128743853375
    2012/2237 = 0.8994188645507376
(2012 = 425+459+1128, the diagonal of the BRF confusion matrix in cell [33].)

**Impact**

The notebook's stated accuracy for the exported web-app logistic regression is wrong by 8 points; the true 17-feature LR accuracy is 0.8176, a decrease from 0.8324, so the markdown's 'small increase' conclusion is backwards. Root cause is reusing the module-level names `classifier` and `y_pred` across models.

**Recommendation**

Always predict from the model just fitted (`y_pred = classifier.predict(X_test_scaled)`), and wrap fit+predict+report in one function so stale globals cannot leak between sections. Add an assertion that the printed metric was computed from the current model's predictions.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell [44] `print(accuracy_score(y_test,y_pred))` scores the y_pred last assigned in cell [32] (23-feature BRF predictions) against the 17-feature split's y_test; because both splits contain the same rows in the same order, the printed 0.8994188645507376 is exactly the BRF's 2012/2237. The 17-feature LR fitted in cell [43] is never scored; its true test accuracy is 0.8176, a decrease from the 23-feature LR's 0.8324, so markdown [45]'s 'small increase' is backwards. The exported web-app LR (SLR.pkl) therefore has no valid evaluation anywhere in the notebook.

*Verifier evidence:* View: cell [43] only calls classifier.fit; no y_pred assignment between cells [32] and [44]. v_stale_scaler_app.py: 17-feat test index identical to 23-feat test index: True (train: True); accuracy_score(y_test_17, BRF23 y_pred) = 0.8994188645507376 == cell [44] output; 2012/2237 = 0.8994188645507376 (425+459+1128 from cell [33]); true 17-feature LR accuracy = 0.8176128743853375 (macro f1 0.7522). Note: this bug does not touch the deck's 83/90/90, which come from the 23-feature models; 'high' is defensible because the only stated accuracy for a shipped model is wrong by 8 points with the conclusion reversed.

### 03-F3 — The web-app models do not share the neural-net notebook's scaler: each notebook fits its own on a different split, and the archived scaler matches neither

> [!danger] high · methodology · cells [37, 39, 40]

**Evidence**

Markdown [37]: '### The scaler parameters is the same that the one export in Neural Network Notebbok'. Cell [40] fits a fresh scaler: `X_scaler = scaler.fit(X_train)`. Notebook 04 cells [31]-[33] build `y = to_categorical(...)` and call `train_test_split(X, y, random_state=1, stratify=y)` on the one-hot y, then cell [34] (commented out) dumps that scaler to webapp/model/scaler_param.joblib. app.py: `scaler = load('model/scaler_param.joblib')` is applied to every model's inputs.

**Reproduction**

stale_and_scaler.py, emulating to_categorical with np.eye(3, dtype='float32')[y]:
(2b) NN-notebook one-hot split identical to integer-label split: False
     rows in common between the two TRAIN sets: 5036 of 6708
     test rows of the sklearn split that were TRAIN rows in the NN split: 1672 of 2237
(3) loaded scaler_param.joblib: StandardScaler; n features 17; n_samples_seen_ 6708
    max |mean_ diff| vs scaler on int-label 17-feat split  : 4340.47
    max |mean_ diff| vs scaler on one-hot 17-feat split    : 838.243
Brute force over random_state 0..100 x {stratify int, one-hot f32, one-hot f64, one-hot int, none}: 'exact matches of archived scaler mean_: NONE'. Per-feature relative difference of archived mean vs the sklearn-notebook scaler: Insolation_Flux +56.8%, Planetary_Radius -14.9%, Transit_Depth -10.5%.
Serving the notebook's own 17-feature models through the archived scaler: LR 48/2237 predictions change (2.1%), GBT 268/2237 (12.0%, macro f1 0.8640 -> 0.7832), BRF 357/2237 (16.0%, macro f1 0.8666 -> 0.7510). Through the one-hot-split scaler: GBT 399 (17.8%), BRF 213 (9.5%).
(3) SLR.pkl loaded: max |coef_ diff| vs fresh 17-feature LR from the notebook code: 0.1521 -> the archived pickles come from a run the committed notebook does not reproduce. GBT.pkl and BRF.pkl cannot be loaded in sklearn 1.9 (ModuleNotFoundError sklearn.ensemble._gb_losses; incompatible tree node dtype), so which scaler they were trained with is unverified.

**Impact**

The claim in [37] is false for the committed code, and the mismatch is not cosmetic: a tree model served through a scaler fit on different rows shifts 12-16% of predictions on heavy-tailed features like insolation flux. Whether the deployed 2020 app actually mis-scaled inputs is unverified (the archived tree pickles cannot be opened), but the process guaranteed no consistency.

**Recommendation**

Fit and save scaler + estimator together as one sklearn Pipeline per model, from one notebook, into models/ with feature names and library versions recorded. Never share a scaler between notebooks. Tree models need no scaling at all, so leave the scaler out of the GBT/BRF pipelines (or keep it only for uniformity and prove it is the same object).

**Verifier: ✅ confirmed**

*Corrected statement:* Markdown [37] is false for the committed code: cell [40] fits a fresh StandardScaler on the sklearn notebook's split, while notebook 04 fits and (in a commented-out cell [34]) exported its own scaler from a split stratified on a one-hot y, which is a different split (5,036 of 6,708 training rows in common; 1,672 of the sklearn test rows are NN training rows). The archived scaler_param.joblib (17 features, n_samples_seen_ 6708, no feature names) matches neither split exactly (no match over random_state 0..100 x 5 stratify modes) and its heavy-tailed means differ sharply: Insolation_Flux archived 9,047 vs notebook-split 4,707 Earth flux (+92.2%), Planetary_Radius 98.0 vs 113.5 (-13.7%), Transit_Depth 23,551 vs 26,115 ppm (-9.8%). Serving the notebook's own 17-feature models through the archived scaler changes 48/2237 LR, 268/2237 GBT (macro f1 0.8640 -> 0.7832) and 357/2237 BRF (0.8666 -> 0.7510) predictions. SLR.pkl also does not match the committed notebook (max |coef diff| 0.152; 0.230 even when refit through the archived scaler), and GBT.pkl/BRF.pkl cannot be opened in scikit-learn 1.9, so whether the deployed app mis-scaled is unverifiable; the process guaranteed no consistency.

*Verifier evidence:* v_stale_scaler_app.py reproduced every number: one-hot split identical to int split False; 5036/6708 common train rows; 1672/2237; archived scaler StandardScaler n_features_in_ 17, n_samples_seen_ 6708, feature_names_in_ absent; max|mean_ diff| 4340.47 (int split) / 838.24 (one-hot split) / 1410.90 (all rows); brute force NONE; LR 48, GBT 268 (0.8640->0.7832), BRF 357 (0.8666->0.7510); via one-hot scaler GBT 399, BRF 213; SLR.pkl max|coef diff| 0.1521; GBT.pkl ModuleNotFoundError sklearn.ensemble._gb_losses; BRF.pkl incompatible node dtype. ONE DISCREPANCY: the reviewer's per-feature percentages (+56.8% / -14.9% / -10.5%) do not reproduce under any formula I tried (archived/notebook-1 gives +92.2/-13.7/-9.8; relative to the midpoint +63.1/-14.7/-10.3); use my numbers or the absolute means. Extra: LR refit on int-split rows scaled by the archived scaler still differs from SLR.pkl by 0.230 (one-hot split: 0.419), so the archived pickles come from a data/run state the repo does not contain. Insolation column: max 10,947,555 Earth flux, top 10 rows carry 53.7% of the column sum; 300 random 75% subsamples give means from 4,261 to 9,311, so the mismatch is consistent with a different random split.

### 03-F4 — The 83 / 90 / 90 '% f1' figures are accuracy and weighted-average f1, not macro f1; macro f1 is 0.77 / 0.87 / 0.87

> [!warning] medium · claim-vs-data · cells [19, 22, 27, 29, 32, 35]

**Evidence**

Cell [19] prints accuracy `0.8323647742512293`. Cell [22] report: 'accuracy 0.83 ... macro avg 0.78 0.77 0.77 ... weighted avg 0.83 0.83 0.83'. Cell [27]: 'Accuracy Score : 0.9016540008940546'; cell [29]: 'macro avg 0.87 0.87 0.87 / weighted avg 0.90 0.90 0.90'. Cell [35] (imbalanced report): 'avg / total 0.90 0.90 0.96 0.90' (the avg/total row is support-weighted). Deck: 'LOGISTIC REGRESSION- 83% f1 ... GRADIENT BOOSTED TREES- 90% f1 ... RANDOM FOREST- 90% f1'.

**Reproduction**

repro_full.py on the same split: LR accuracy 0.8324, f1 macro 0.7729, f1 weighted 0.8298, per class [0.6278 0.7001 0.9908]; GBT accuracy 0.9021, f1 macro 0.8706, f1 weighted 0.9015, per class [0.8045 0.8172 0.9899]; BRF (imblearn 0.7 defaults) accuracy 0.8994, balanced accuracy 0.8652, f1 macro 0.8670, f1 weighted 0.8987, per class [0.7989 0.8131 0.9890]. Test support 534/572/1131, so the FP class is 50.6% of the weight.

**Impact**

Weighted f1 and accuracy coincide here because the majority class (FALSE POSITIVE, f1 0.99 from the flags) dominates; the two classes the project actually cares about score 0.63-0.82. Quoting '90% f1' without the averaging overstates performance on CANDIDATE/CONFIRMED.

**Recommendation**

Report macro f1, balanced accuracy and the per-class f1 vector, and name the averaging every time a number is quoted (deck, README, research log). Update the README's 'Current f1 scores' block to 'accuracy / macro f1 (with flags)'.

**Verifier: ✅ confirmed**

*Corrected statement:* The 83 / 90 / 90 '% f1' figures are accuracy and support-weighted f1, which coincide here because FALSE POSITIVE is 50.6% of the test set and scores 0.99. On the notebook's split: LR accuracy 0.8324, weighted f1 0.8298, macro f1 0.7729, per-class f1 CAND/CONF/FP 0.63/0.70/0.99; GBT 0.9021 (notebook 0.9017), 0.9015, 0.8706, 0.80/0.82/0.99; BRF (imblearn-0.7 defaults) accuracy 0.8994, weighted f1 0.8987, macro f1 0.8670, balanced accuracy 0.8652, 0.80/0.81/0.99. The BRF's '0.90' in cell [35] is classification_report_imbalanced's support-weighted 'avg / total' row. The deck text ('LOGISTIC REGRESSION- 83% f1 ... GRADIENT BOOSTED TREES- 90% f1 ... RANDOM FOREST- 90% f1') and README 'Current f1 scores' block never name the averaging.

*Verifier evidence:* v_repro_full.py: LR acc 0.8324 f1_macro 0.7729 f1_weighted 0.8298 per-class [0.6278 0.7001 0.9908]; GBT acc 0.9021 f1_macro 0.8706 f1_weighted 0.9015 [0.8045 0.8172 0.9899]; BRF acc 0.8994 bal_acc 0.8652 f1_macro 0.8670 f1_weighted 0.8987 [0.7989 0.8131 0.9890]; test support {0:534, 1:572, 2:1131}. Cell outputs quoted in view: [22] 'macro avg 0.77 / weighted avg 0.83', [29] 'macro avg 0.87 / weighted avg 0.90', [35] 'avg / total ... 0.90'. Deck wording verified verbatim via project_search of Kepler_Analysis_Presentation.pdf; README lines 51-55 read 'Current f1 scores: ... 83% ... 90% ... 90% ... 84%'.

### 03-F5 — GBT hyperparameters were selected on the test set, with a sweep that used different max_features than the final model, on a single split with no variance estimate

> [!warning] medium · methodology · cells [24, 25]

**Evidence**

Cell [24]: `classifier = GradientBoostingClassifier(n_estimators=20, learning_rate=learning_rate, max_features=.25, max_depth=3, random_state=0)` ... `print("Accuracy score (validation): ...".format(classifier.score(X_test_scaled, y_test)))`. Cell [25]: `classifier = GradientBoostingClassifier(n_estimators=20, learning_rate=0.5, max_features=.5, max_depth=3, random_state=0)` with the comment '# Using the learning_rate value from above (is this instance they are all the same)'. Cell [24] output shows validation accuracy ranging 0.857 to 0.898, so they are not all the same.

**Reproduction**

repro_full.py reproduced the sweep: lr=0.05 test acc 0.857; 0.1 0.878; 0.25 0.894; 0.5 0.898; 0.75 0.894; 1 0.895 (notebook: 0.896). 5-fold CV std of macro f1 across folds: LR 0.0058, GBT 0.0083, BRF 0.0137; i.e. the 0.8706 vs 0.8670 GBT-vs-BRF difference on the single split is within one fold's noise. Data point for the rewrite: GBT with sklearn defaults (100 trees, lr 0.1) gives acc 0.9039 / macro f1 0.8728 vs 0.9021 / 0.8706 for the notebook's 20-tree setting.

**Impact**

The 'validation' score is the test score, so the reported GBT number is mildly optimistic, and the model comparison (GBT vs BRF vs LR) has no error bars. The mismatch between sweep and final settings means the sweep did not inform the final model.

**Recommendation**

Tune with StratifiedKFold cross-validation (GridSearchCV/RandomizedSearchCV) on the training rows only; touch the test set once at the end; report CV mean +/- std alongside the held-out number.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell [24]'s learning-rate sweep scores each candidate on the test set (labelled 'validation'), and the chosen setting is then used with max_features=.5 in cell [25] although the sweep used max_features=.25, so the sweep did not select the final configuration; the comment 'they are all the same' contradicts the printed range 0.857-0.898. All model comparisons rest on one split with no variance estimate: 5-fold macro-f1 std is 0.0058 (LR), 0.0083 (GBT), 0.0137 (BRF), larger than the 0.0036 GBT-vs-BRF gap on the held-out split. GBT with sklearn defaults gives acc 0.9039 / macro f1 0.8728.

*Verifier evidence:* View cell [24] code and outputs quoted; cell [25] `max_features=.5`. v_repro_full.py sweep: lr 0.05 test 0.857, 0.1 0.878, 0.25 0.894, 0.5 0.898, 0.75 0.894, 1 0.895 (notebook 0.896 for lr=1). v_leakage.py CV stds 0.0058/0.0083/0.0137; single-split macro f1 GBT 0.8706 vs BRF 0.8670 (diff 0.0036). GBT sklearn defaults acc 0.9039 f1_macro 0.8728.

### 03-F6 — BalancedRandomForestClassifier result depends on imbalanced-learn version defaults; modern defaults give a different answer

> [!warning] medium · reproducibility · cells [31, 32, 33, 53, 54]

**Evidence**

Cell [31]: `brf_model = BalancedRandomForestClassifier(n_estimators=100, random_state=1)`; cell [32] output `0.8652250607887958`; cell [33] confusion matrix [[425,97,12],[103,459,10],[2,1,1128]]. archive/requirements_2020.txt pins `imbalanced-learn==0.7.0`.

**Reproduction**

repro_full.py with imblearn 0.14.2: modern defaults -> balanced accuracy 0.8614, macro f1 0.8631, confusion [[417,107,10],[101,461,10],[2,1,1128]]; with the 0.7-era defaults `sampling_strategy='auto', replacement=False, bootstrap=True` -> balanced accuracy 0.8652, macro f1 0.8670, confusion [[425,97,12],[103,459,10],[2,1,1128]] (identical to the notebook).

**Impact**

Re-running the committed cell in the 2026 environment silently produces a different model and a different number; anyone checking the 0.8652 would conclude the notebook does not reproduce.

**Recommendation**

Pass sampling_strategy, replacement and bootstrap explicitly (and record library versions in the notebook header or a saved metadata JSON).

**Verifier: ✅ confirmed**

*Corrected statement:* `BalancedRandomForestClassifier(n_estimators=100, random_state=1)` reproduces the notebook's 0.8652250607887958 and confusion matrix [[425,97,12],[103,459,10],[2,1,1128]] only with the imbalanced-learn 0.7 defaults spelled out (sampling_strategy='auto', replacement=False, bootstrap=True); with imbalanced-learn 0.14.2 defaults the same cell gives balanced accuracy 0.8614, macro f1 0.8631, confusion [[417,107,10],[101,461,10],[2,1,1128]].

*Verifier evidence:* v_repro_full.py: modern defaults balanced acc 0.8613968041515503, confusion [[417,107,10],[101,461,10],[2,1,1128]]; 0.7-era defaults 0.8652250607887958 == cell [32], confusion identical to cell [33]. archive/requirements_2020.txt line 76 'imbalanced-learn==0.7.0'; installed imblearn 0.14.2, sklearn 1.9.0.

### 03-F7 — Notebook cannot run in the 2026 environment and cannot regenerate the archived pickles: unused tensorflow import, commented-out exports, 25 unused imports, and legacy pickles that no longer load

> [!warning] medium · dead-code · cells [1, 46, 51, 56]

**Evidence**

Cell [1]: `import tensorflow as tf` (never used). Cells [46], [51], [56]: `# save_location=os.path.join("webapp","model","SLR.pkl")` / `# joblib.dump(classifier, save_location)` all commented out. Also `classifier` is reassigned from the LR to the GBT in cell [25], so the LR object is gone after that cell.

**Reproduction**

Regex scan of all code cells after cell [1]: 'imported but never used after cell [1]: [tf, sn, sp, itertools, px, go, plt, gridspec, skl, OneHotEncoder, LabelEncoder, SimpleImputer, SVC, make_pipeline, KFold, cross_val_predict, NearestNeighbors, KNeighborsClassifier, KNeighborsRegressor, mean_squared_error, r2_score, f1_score, precision_score, recall_score, RandomForestClassifier]'. Kernel metadata: Python 3.7.6. joblib.load of the archive: GBT.pkl -> 'ModuleNotFoundError: No module named sklearn.ensemble._gb_losses'; BRF.pkl -> 'ValueError: node array from the pickle has an incompatible dtype'; SLR.pkl and scaler_param.joblib load.

**Impact**

TensorFlow is not installed in the uv environment, so cell [1] fails before any model runs; the archived GBT/BRF pickles are unusable with scikit-learn 1.9, so the 2020 web-app models cannot be evaluated or served without retraining.

**Recommendation**

Strip the import block to what is used; write artifacts to models/ through kepler.paths with a sidecar JSON of versions and feature names (or use skops); treat the archived pickles as historical only and retrain from code.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell [1] imports tensorflow, which is not installed in the uv environment, so the notebook fails at its first cell; 25 of the 40 imported names are never used after cell [1], and `os`/`joblib` appear only inside the commented-out export lines of cells [46], [51], [56]. Kernel metadata records Python 3.7.6. Of the archived web-app pickles, SLR.pkl and scaler_param.joblib load (with version warnings from sklearn 0.23.2); GBT.pkl and BRF.pkl do not load in scikit-learn 1.9.

*Verifier evidence:* Own regex scan of the .ipynb: 25 unused names (tf, sn, sp, itertools, px, go, plt, gridspec, skl, OneHotEncoder, LabelEncoder, SimpleImputer, RandomForestClassifier, SVC, f1_score, precision_score, recall_score, mean_squared_error, r2_score, make_pipeline, KFold, cross_val_predict, NearestNeighbors, KNeighborsClassifier, KNeighborsRegressor); os/joblib only in '# joblib.dump' / '# save_location=os.path.join' lines; `import tensorflow` -> ModuleNotFoundError; language_info.version 3.7.6; execution counts 1..36 in order. v_stale_scaler_app.py: GBT.pkl ModuleNotFoundError 'sklearn.ensemble._gb_losses'; BRF.pkl ValueError incompatible node dtype; SLR.pkl loads as LogisticRegression.

### 03-F8 — The 'chosen to better handle the data imbalance' framing does not match what the code does or what the data shows

> [!warning] medium · claim-vs-data · cells [14, 25, 31]

**Evidence**

Deck: 'LOGISTIC REGRESSION- 83% f1 - Weaker results likely due to unbalanced data'; 'GRADIENT BOOSTED TREES- 90% f1 - Chosen to better handle the data imbalance'; 'RANDOM FOREST- 90% f1 - Alternative to better handle the data imbalance'. Cell [14] LR has no class_weight; cell [25] GBT has no class_weight or sample_weight; only cell [31]'s BalancedRandomForestClassifier resamples.

**Reproduction**

Class shares in kepler_processed.pkl (my run): CANDIDATE 23.9% / CONFIRMED 25.5% / FALSE POSITIVE 50.6%. LR with class_weight='balanced' on the same split: acc 0.8306, balanced acc 0.7713, macro f1 0.7720 vs 0.8324 / 0.7726 / 0.7729 without. GBT balanced accuracy 0.8691 vs BRF 0.8652 (from repro_full.py). Without flags, GBT macro f1 0.7118 vs LR 0.5625 (leakage.py).

**Impact**

Reweighting the classes changes LR by 0.001 macro f1, so imbalance is not why LR is weaker; the majority class is the easy one and the tree models win through nonlinearity. The narrative in the deck attributes the gain to the wrong mechanism, and GBT in fact contains no imbalance handling.

**Recommendation**

Drop the imbalance justification; describe the models by inductive bias (linear vs tree ensembles). If imbalance handling is wanted, use class_weight / sample_weight and judge it by balanced accuracy and per-class recall, not accuracy.

**Verifier: ✅ confirmed**

*Corrected statement:* The deck's causal story ('LR weaker likely due to unbalanced data'; GBT/RF 'chosen to better handle the data imbalance') does not match the code or the data. Classes are 23.9 / 25.5 / 50.6%, and the majority class is the easy one. Cell [25]'s GradientBoostingClassifier has no imbalance handling (no sample_weight; the estimator has no class_weight parameter). LR with class_weight='balanced' moves macro f1 from 0.7729 to 0.7720 and accuracy from 0.8324 to 0.8306, so imbalance is not why LR trails. Nuance the reviewer did not test: the BRF's resampling does give a small gain over a plain RandomForestClassifier(100, random_state=1) on the same split (macro f1 0.8670 vs 0.8586, balanced accuracy 0.8652 vs 0.8568), within one fold's noise (0.0137), so the claim is wrong for LR and GBT and only weakly true for the BRF.

*Verifier evidence:* Deck text verified verbatim via project_search. v_repro_full.py: class shares {0:23.9, 1:25.5, 2:50.6}; LR class_weight=balanced acc 0.8306 bal_acc 0.7713 f1_macro 0.7720 vs 0.8324/0.7726/0.7729; GBT bal_acc 0.8691 vs BRF 0.8652. v_missed_probes.py: plain RF acc 0.8936 bal_acc 0.8568 f1_macro 0.8586 vs BRF 0.8994/0.8652/0.8670. See missed item 2 for what actually explains the LR gap (heavy tails).

### 03-F9 — Markdown comparison cells [45], [50], [55] quote numbers from an earlier run that contradict the outputs directly above them

> [!note] low · documentation · cells [44, 45, 49, 50, 54, 55]

**Evidence**

[45]: '<b>Small increase in accuracy: 0.8971837282074206 vs. 8292355833705856 previously</b>' (second number lacks its leading '0.'; cell [44] printed 0.8994..., cell [19] 0.8323...). [50]: '<b>Small decrease in accuracy: 0.8936075100581136 vs. 0.902101028162718 previously</b>' but [49] prints 0.8976307554760841 and [27] 0.9016540008940546. [55]: '<b>Slightly increase in accuracy: 0.863978879186163 vs. 0.8619380855917083 previously</b>' but [54] prints 0.8651443803516644 and [32] 0.8652250607887958, a decrease of 0.00008.

**Reproduction**

Not run (comparison of quoted cell text with quoted cell outputs). My own 17-feature runs: GBT accuracy 0.8976 and BRF balanced accuracy 0.8651 match cells [49] and [54]; the true 17-feature LR accuracy is 0.8176 (see 03-F2), so the [45] 'increase' is wrong in both the stale-number sense and the direction.

**Impact**

A reader trusting the prose gets three wrong comparisons; [55]'s direction is opposite to the evidence. Confirms the notebook was re-run at least once after the prose was written, and that the archived pickles predate the committed outputs.

**Recommendation**

Compute comparison text from variables (f-strings) or drop the prose; keep a single results table built in code.

**Verifier: ✅ confirmed**

*Corrected statement:* The three comparison markdowns quote numbers from an earlier run: [45] '0.8971837282074206 vs. 8292355833705856' (cell [44] printed 0.8994188645507376, itself a stale BRF number; the true 17-feature LR is 0.8176, a decrease); [50] '0.8936075100581136 vs. 0.902101028162718' (cells [49]/[27] print 0.8976307554760841 / 0.9016540008940546); [55] 'Slightly increase ... 0.863978879186163 vs. 0.8619380855917083' (cells [54]/[32] print 0.8651443803516644 vs 0.8652250607887958, a decrease of 0.00008). Cells [49] and [54] reproduce exactly today.

*Verifier evidence:* Quoted from the view. v_stale_scaler_app.py: 17-feature GBT accuracy 0.8976307554760841 == cell [49]; 17-feature BRF balanced accuracy 0.8651443803516644 == cell [54]; true 17-feature LR accuracy 0.8176128743853375. Curiosity: the '0.902101028162718' in [50] equals my sklearn-1.9 23-feature GBT accuracy exactly, consistent with the prose having been written under a different library state than the committed outputs.

### 03-F10 — The logistic-regression 'feature importance' table is the signed CANDIDATE-class coefficient vector, stored as strings, with the strongest features at the bottom

> [!note] low · methodology · cells [16]

**Evidence**

Cell [16]: `x = sorted(zip(classifier.coef_[0], X.columns), reverse=True)` then `featureImp = pd.DataFrame(np.array(x).reshape(len(x),2), columns = list(["Importance","Feature"]))`. Output header: '0 1.4194370887669014 Transit_Depth_[ppm]'.

**Reproduction**

Ran cell [16] verbatim on my reproduced LR: `featureImp['Importance'].dtype -> object`, first value repr '1.3943281937008138' (a str; np.array on (float, str) tuples upcasts to strings). `coef_.shape (3, 23)`, `coef_[0]` is classes_[0] = 0 = CANDIDATE. Bottom of the signed sort: Transit_Signal-to-Noise -0.94, Stellar_Eclipse_FPF -1.37, Ephemeris_Match -1.53, Not_Transit-Like_FPF -2.02, Centroid_Offset_FPF -2.13. Top-|coef| for FALSE POSITIVE: Centroid_Offset_FPF +3.18, Stellar_Eclipse_FPF +2.66, Not_Transit-Like_FPF +2.61, Ephemeris_Match +2.53. (My coefficient for Transit_Depth is 1.394 vs the notebook's 1.419, a scikit-learn version difference; the confusion matrix matched exactly.)

**Impact**

The table hides the fact that the four flags are the dominant coefficients (they are negative for CANDIDATE, so sorted last), mislabels one class's coefficients as 'importance', and the values cannot be used numerically.

**Recommendation**

Show |coef| per class (a 3-row table) or permutation importance on the held-out set; keep numeric dtype (build the DataFrame from the arrays, not from np.array of tuples).

**Verifier: ✅ confirmed**

*Corrected statement:* Cell [16] sorts the signed coefficients of classes_[0] (=0=CANDIDATE) only and, via np.array on (float, str) tuples, stores them as strings (dtype object), with the four flags — the largest-magnitude coefficients — at the bottom (Centroid_Offset -2.13, Not_Transit-Like -2.02, Ephemeris_Match -1.53, Stellar_Eclipse -1.37 in my fit). For the FALSE POSITIVE class the flags dominate with +3.18, +2.66, +2.61, +2.53.

*Verifier evidence:* v_repro_full.py ran cell [16] verbatim: featureImp['Importance'].dtype object, first value repr '1.3943281937008138' (notebook 1.4194370887669014; sklearn version difference, confusion matrix identical), classes_ [0 1 2], coef_.shape (3, 23); tail of the sort as stated; FP-class |coef| top four Centroid 3.183, Stellar_Eclipse 2.659, Not_Transit 2.609, Ephemeris 2.528.

### 03-F11 — The 23-feature model includes catalog-provenance features (TCE delivery name, RA/Dec) that encode when/where a KOI was catalogued rather than physics

> [!note] low · methodology · cells [8, 16, 38]

**Evidence**

Cell [8] keeps TCE_Delivery_q1_q16_tce, TCE_Delivery_q1_q17_dr24_tce, TCE_Delivery_q1_q17_dr25_tce, right_ascension, declination, TCE_Planet_Number; cell [16] lists TCE_Delivery_q1_q17_dr24_tce with coefficient 0.138; cell [38] drops all six for the web-app version without explanation.

**Reproduction**

Crosstab on kepler_processed.pkl joined to the string labels: CONFIRMED share by delivery q1_q16_tce 0.2% (1 of 631), q1_q17_dr24_tce 0.9% (3 of 320), q1_q17_dr25_tce 28.5% (2,281 of 7,994). CONFIRMED share by TCE_Planet_Number: 1 -> 21.3% (7,526 rows), 2 -> 46.9%, 3 -> 51.0%, 4 -> 56.7%.

**Impact**

Delivery name is almost a rule 'not DR25 -> not CONFIRMED', which a model will happily learn but which says nothing about the planet; sky position is likewise not a planet property. Planet number (system multiplicity) is a genuine astrophysical prior (multi-planet systems are rarely false positives) but should be a conscious choice, not an accident of which columns survived notebook 01.

**Recommendation**

Define the feature list explicitly in src/kepler/features.py with a one-line justification each; exclude delivery name and RA/Dec from the physics-only variant; keep multiplicity if it is documented as a prior.

**Verifier: ✅ confirmed**

*Corrected statement:* The 23-feature model keeps catalogue-provenance columns: CONFIRMED share by TCE delivery is 1/631 (0.2%) for q1_q16_tce, 3/320 (0.9%) for q1_q17_dr24_tce and 2,281/7,994 (28.5%) for q1_q17_dr25_tce; CONFIRMED share by TCE planet number is 21.3% (n=7,526) for 1, 46.9% for 2, 51.0% for 3, 56.7% for 4. In practice these columns move the with-flags GBT very little (permutation importance on the test set, macro f1: TCE_Planet_Number 0.009, RA 0.007, Dec 0.000), and Transit_Epoch_[BKJD] — a timing quantity that is not a planet property either, kept in both feature sets and in the app form — contributes 0.002. Low severity is right; the point is about a documented feature list, not a large score effect.

*Verifier evidence:* Own crosstab after joining the pickle index to data/raw/cumulative_kaggle_snapshot.csv (8,945/8,945 rows joined; label mapping 0=CANDIDATE 2136, 1=CONFIRMED 2285, 2=FALSE POSITIVE 4524 verified exactly): delivery 1/631, 3/320, 2281/7994; planet number 1602/7526=0.213, 443/944=0.469, 159/312=0.510, 59/104=0.567. View cell [16] lists TCE_Delivery_q1_q17_dr24_tce 0.138. v_missed_probes.py permutation importances as stated; corr(epoch, period) 0.649; epoch range 120.5-1472.5 BKJD.

### 03-F12 — Web-app integration: column order matches, but the app reports a CANDIDATE prediction as 'Exoplanet predicted!!!' and relies on a name-less scaler that a modern re-export would break

> [!note] low · other · cells [38, 40]

**Evidence**

app.py: `input_variables_df = pd.DataFrame([[input_2, input_5, input_1, input_3, input_9, input_13, input_8, input_11, input_4, input_17, input_10, input_12, input_6, input_16, input_15, input_7, input_14]], columns=["c1", ... "c17"], dtype=float)`; `prediction = model.predict(input_variables_scaled); if prediction > 1: output = "Exoplanet not predicted..." else: output = "Exoplanet predicted!!!"`.

**Reproduction**

Mapped input_N to the form labels in main.html and compared with the notebook's 17-column order: 'app column order == notebook 17-feature column order: True'. sklearn 1.9: `sc17.transform(DataFrame with columns c1..c17)` on a scaler fit with real column names -> 'ValueError: The feature names should match those that were passed during fit'; the archived scaler_param.joblib (fit in sklearn 0.23, no feature_names_in_) transforms the c1..c17 frame without error. Archived SLR.pkl through the archived scaler on all 8,945 rows predicts CANDIDATE for 1,889 rows, all of which the app would label 'Exoplanet predicted!!!'.

**Impact**

The order dependence is correct today only by convention; renaming or reordering one column in a rewrite silently breaks it. Conflating CANDIDATE with CONFIRMED in the app's verdict misstates what the 3-class model says.

**Recommendation**

In the Phase 5 app, feed a DataFrame whose columns are the pipeline's feature_names_in_ (assert equality), show the three class probabilities, and word the verdict per class (CANDIDATE is 'not yet confirmed', not 'exoplanet').

**Verifier: ✅ confirmed**

*Corrected statement:* app.py's DataFrame order [input_2, input_5, input_1, input_3, input_9, input_13, input_8, input_11, input_4, input_17, input_10, input_12, input_6, input_16, input_15, input_7, input_14], mapped through the main.html labels, equals the notebook's 17-column order exactly, but only by convention: the archived scaler has no feature names and accepts the c1..c17 frame, whereas a scaler fit under scikit-learn 1.9 on named columns rejects it ('The feature names should match those that were passed during fit'). The verdict logic `prediction > 1` labels both class 0 (CANDIDATE) and class 1 (CONFIRMED) 'Exoplanet predicted!!!'; the archived SLR.pkl through the archived scaler predicts CANDIDATE for 1,889 of 8,945 rows (CONFIRMED 2,452, FP 4,604), and the form's default values yield class 0, i.e. 'Exoplanet predicted!!!' for a KOI the model calls only a candidate.

*Verifier evidence:* v_stale_scaler_app.py: app column order == notebook 17-feature order: True; modern scaler with c1..c17 frame -> ValueError feature names; archived scaler accepts c1..c17: yes; archived SLR+scaler class counts {0:1889, 1:2452, 2:4604}; form defaults -> [0]. app.py and main.html read directly (labels input_1 Centroid Offset ... input_17 Planetary Radius).
