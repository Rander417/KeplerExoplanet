---
tags: [research-log, review, notebook-04]
date: 2026-08-24
source: multi-agent review workflow wf_29148ee0-552 (reviewer + adversarial verifier)
---

# 2026-08-24 Review: Notebook 04 neural net

> [!abstract] What the notebook does (reviewer's summary)
> The notebook loads the 2020 processed table (data/legacy/kepler_processed.pkl: 8,945 KOIs x 24 columns, i.e. 23 features plus Exoplanet_Archive_Disposition, which I verified by joining to the raw CSV is encoded 0=CANDIDATE (2,136), 1=CONFIRMED (2,285), 2=FALSE POSITIVE (4,524)). It one-hot encodes the target with keras to_categorical and makes a stratified 75/25 split with random_state=1 (6,708 train / 2,237 test rows; my reproduction of the split gives test class counts 534/572/1131, exactly the row sums of the notebook's confusion matrix). A StandardScaler is fit on the training split, then a hard-coded Keras Sequential net (Dense 260-300-80 with relu, 3-unit softmax, categorical_crossentropy, Adam, metric accuracy) is trained for 100 epochs with no validation data and evaluated on the test split (Keras accuracy 0.8471); f1 is obtained by argmax of the softmax output and sklearn classification_report (per-class 0.70/0.71/0.98, macro 0.80, weighted 0.85). A keras-tuner RandomSearch over layer widths and depth lives in seven inert RAW cells; its search space matches archive/keras_tuner_2020/oracle.json, and its best trial (260/300/80, visible only in a screenshot in cell [26]) is the architecture used everywhere. The final section drops six columns (TCE planet number, RA, Dec, three TCE-delivery dummies) to 17 features, refits the scaler and (in a commented-out cell) exports it as scaler_param.joblib, then trains the same architecture for 200 epochs on the UNSCALED training data (test accuracy 0.8350 on unscaled inputs, no f1 computed) and, in another commented-out cell, exports kepler_NN.h5 for the Flask app, which applies the scaler before calling the network. The saved notebook is a clean top-to-bottom run (execution counts 1-22 in order), but the exported artefacts in archive/webapp_flask_2020/model/ were produced in a different session and cannot be regenerated from it.

> [!warning] At a glance
> **12 findings**: 3 high · 4 medium · 5 low. Verifier verdicts: 12 confirmed · 0 partially · 0 refuted · 0 unverifiable. Verifier added 3 missed item(s). 8 deck/README claims checked.

## Findings at a glance

| ID | Severity | Category | Finding | Verifier |
|---|---|---|---|---|
| 04-F1 | high | bug | Served 17-feature network is trained on unscaled data while the exported scaler is applied to its inputs in the web app (train/serve skew) | ✅ confirmed |
| 04-F2 | high | reproducibility | Shipped web-app artefacts (scaler_param.joblib, kepler_NN.h5) are not reproducible from the saved notebook | ✅ confirmed |
| 04-F3 | high | leakage | The four false-positive flag features hand the model the FALSE POSITIVE class; only the with-flags variant is reported | ✅ confirmed |
| 04-F4 | medium | leakage | Tuner (as written) validates on the test set, trains on raw X_train while validating on scaled X_test_scaled, and optimises plain accuracy | ✅ confirmed |
| 04-F5 | medium | claim-vs-data | The deck/README '84% f1' is not an f1 the notebook ever computes; the only f1 values are macro 0.80 / weighted 0.85 for the 23-feature model | ✅ confirmed |
| 04-F6 | medium | claim-vs-data | Stale hand-typed markdown claims a 'small increase in accuracy' that the saved outputs contradict | ✅ confirmed |
| 04-F7 | medium | methodology | Severe overfitting goes undetected: no validation data, no early stopping, no regularisation, and only training curves are plotted | ✅ confirmed |
| 04-F8 | low | methodology | A default gradient-boosting model beats the 107k-parameter network on the same split in seconds | ✅ confirmed |
| 04-F9 | low | reproducibility | Tuner results survive only as screenshots; the archived oracle.json holds the search space and defaults, not the best trial, and the run stopped at 68 of 100 trials | ✅ confirmed |
| 04-F10 | low | reproducibility | No random seeds and a 2020-pinned stack (Python 3.7.6, TF/Keras 2.4.0, sklearn 0.23.2, 'kerastuner' import) make the notebook non-reproducible today | ✅ confirmed |
| 04-F11 | low | documentation | Target, class encoding and feature-order contract are never stated; the app rebuilds the 17-column order by hand | ✅ confirmed |
| 04-F12 | low | dead-code | Dead imports, unused variables, and an orphaned older model file | ✅ confirmed |

## Deck / README claims checked

| Verdict | Claim | Evidence |
|---|---|---|
| 🟡 partially | Deck/README: deep neural network achieves 84% f1 | The notebook computes f1 once (cell [18], 23-feature scaled model): recomputed from the quoted confusion matrix, per-class f1 0.7000/0.7092/0.9842, macro 0.7978, weighted 0.8460, accuracy 0.8471. The exported 17-feature model (cell [36]) has only Keras accuracy 0.8350469 (rounds to 84%) and no f1. The stale markdown in cell [37] quotes 0.8395 (also rounds to 84%). So '84%' is defensible only as an accuracy, or as a truncated weighted f1 of a different model than the one served; it is not a macro f1 (0.80). |
| ✅ confirmed | Deck/README: the network 'uses relu and softmax' | Cells [13] and [35]: three Dense layers with activation="relu" and an output `Dense(units=3, activation="softmax")`. Parsed kepler_NN.h5 model_config from the file bytes: layers (260, relu), (300, relu), (80, relu), (3, softmax); training_config loss categorical_crossentropy, metrics ['accuracy'], optimizer Adam (lr 0.001). |
| 🟡 partially | Deck: hyperparameter tuning with keras-tuner, results stored under tuningOutput/ (oracle.json, tuner0.json kept) | oracle.json search space (parsed in Python) is exactly RAW cell [20]'s: input_units Int 20-300 step 20, n_layers Int 1-4, inner_0..inner_3_units Int 20-300 step 20. The best values exist only in the cell [26] screenshot (input_units 260, n_layers 2, inner_0 300, inner_1 80) and match the hard-coded architecture. But oracle.json records 67 completed + 1 ongoing trials of max_trials=100 (run incomplete), its 'values' are the defaults (all 20, n_layers 1), tuner0.json is '{}', and no trial scores survive, so the tuning benefit is unverified. As written, the search validated on the test set with raw-vs-scaled input mismatch (RAW cell [23]). |
| 🟡 partially | Notebook: the scaler exported here is the one shared with the sklearn web-app models | app.py applies model/scaler_param.joblib to the inputs of all four models (lines 48-56), and the file is a 17-feature StandardScaler with n_samples_seen_=6708 in the same column order as cell [31]; SLR.pkl expects n_features_in_=17. However its mean_/scale_ do not match a scaler fit on the notebook's random_state=1 stratified split (max \|mean diff\| 838.24 on Insolation; max relative scale diff 11.1%), no random_state in 0-300 (stratified or not) reproduces it, the export cell [34] is commented out, and the notebook's own 17-feature NN (cell [35]) never uses the scaler. GBT.pkl/BRF.pkl could not be unpickled under sklearn 1.9, so their feature contract is unverified. |
| ✅ confirmed | Lead reviewer question: how was f1 computed for a softmax 3-class model? | Keras metrics are accuracy only (`metrics=["accuracy"]`, cells [13]/[35]). Cell [17] does `y_pred=np.argmax(nn.predict(X_test_scaled), axis=1)` and `y_testCM=np.argmax(y_test, axis=1)`, then sklearn confusion_matrix; cell [18] prints sklearn classification_report, which is where the per-class/macro/weighted f1 come from. This was done only for the 23-feature model; the exported 17-feature model got nn.evaluate accuracy only. |
| ❌ refuted | Notebook cell [37]: 'Small increase in accuracy: 0.8574 vs 0.8395 previously' | Printed outputs are 0.8471166 (cell [14], 23 features scaled) and 0.8350469 (cell [36], 17 features unscaled): a decrease of 1.2 points; neither markdown number appears in any output. |
| ❌ refuted | Notebook cell [35] comment: '(same parameters as above, just increasing the epochs)' | The cell also changes the feature set from 23 to 17 (cell [31]) and trains on unscaled X_train instead of X_train_scaled; epoch-1 loss 661.5233 vs 1.0804 in cell [13] shows the input scale changed. |
| ✅ confirmed | The notebook's random_state=1 stratified split is the one behind the printed confusion matrix | My reproduction with sklearn 1.9 (train_test_split(X, one_hot_y, random_state=1, stratify=one_hot_y)) gives X_train (6708, 23) / (6708, 17) and test class counts 534/572/1131, identical to the notebook's shape outputs and confusion-matrix row sums. Exact row identity versus sklearn 0.23.2 was not independently verified, but the split algorithm has not changed to my knowledge. |

## What the verifier added (missed by the reviewer)

> [!warning] The NN notebook's 'random_state=1' split is not the sklearn notebook's split, so the README's cross-model ranking and the 'same scaler' claim compare different test sets (medium)
> 03_sklearn_models cell [8] uses the integer Series (`y = keplerProcessed_df["Exoplanet_Archive_Disposition"]`) while 04 cell [7] uses `to_categorical(...)`; both call `train_test_split(X, y, random_state=1, stratify=y)`. sklearn joins one-hot rows into strings before np.unique, which orders the classes as ['0.0 0.0 1.0', '0.0 1.0 0.0', '1.0 0.0 0.0'] (2,1,0 instead of 0,1,2) and changes the per-class permutation draws. Measured in this session: training-row overlap between the two splits 5,036 of 6,708 (chance expectation 5,031), test overlap 565 of 2,237 (chance 559); class counts are identical (534/572/1131), so confusion-matrix row sums cannot reveal it. A scaler fit on the 03-style split differs from the saved scaler_param.joblib by max |mean diff| 4,340 (vs 838 for the 04-style split), so 03's markdown 'The scaler parameters is the same that the one export in Neural Network Notebook' is false for the committed code, and the reviewer's keep-item 'random_state=1 shared with the other notebooks' is wrong. The README ranking (SLR 83 / GBT 90 / RF 90 / NN 84) therefore mixes scores on different test rows.

> [!warning] The served decision rule is not the notebook's evaluation rule: P(FALSE POSITIVE) >= 0.5 instead of argmax, and CANDIDATE is reported as 'Exoplanet predicted!!!' (medium)
> app.py line 60 `prediction = model.predict(input_variables_scaled)[0][2]` then line 61 `if prediction >= 0.5: output = "Exoplanet not predicted..."` else 'Exoplanet predicted!!!' with prob = 1 - P(FP); a softmax of (0.40, 0.15, 0.45) is argmax-FALSE POSITIVE but the app reports an exoplanet at '55.00%'. For the sklearn models, lines 71-75 `prediction = model.predict(...)`, `if prediction > 1: not predicted else: predicted`, so class 0 (CANDIDATE) is announced as a predicted exoplanet. The product is thus a binary FP-vs-not decision, which on the test split the four flags alone already deliver at class-2 f1 0.988 (my run); none of the notebook's 3-class metrics describe what users see. Code-level reading only; no inference was run.

> [!note] Heavy-tailed physical features are standardized without a log transform, leaving the network near-constant inputs with extreme outliers (low)
> On the notebook's random_state=1 training split, after StandardScaler (cell [33]): Planetary_Radius median 2.4 R_earth, max 200,346, z_max 55.8, 99.3% of standardized values within |z| < 0.1; Insolation_Flux median 146.7, max 10,947,555, z_max 60.6, 97.9% within |z| < 0.1; Stellar_Radius z_max 39.0; Transit_Depth z_max 10.9 (computed this session). Period, depth, radius, insolation and SNR are the usual log-scale quantities; neither the notebook nor the reviewer's rewrite recommendations mention a transform, and the same untransformed scaler is what the web app applies.


## Keep (what the rewrite should preserve)

- Clean, linear structure with execution counts 1-22 in order (a true top-to-bottom run) and one section per model; the RAW-cell convention documents the long tuner search without re-running it.
- Stratified train/test split with a fixed random_state=1 shared with the other notebooks; scaler fit on the training split only (cells [11], [33]) - no scaling leakage.
- Correct 3-class evaluation recipe: argmax of the softmax output, then sklearn confusion_matrix and classification_report for per-class, macro and weighted f1 (cells [17]-[18]) rather than trusting Keras accuracy alone.
- Softmax output with categorical_crossentropy and one-hot targets is the right pairing for a 3-class problem; Adam defaults are sensible.
- Test-set evaluation reports both loss and accuracy, and training curves are plotted (extend to validation curves).
- The served feature set sensibly drops sky coordinates, TCE-delivery dummies and the TCE planet index; I verified the Flask app's hand-written input order matches the notebook's 17-column order exactly.
- The tuner search space is recorded in the archived oracle.json and matches the notebook, so the search is at least documented.

## Rewrite recommendations

- Bind preprocessing to the model: an sklearn Pipeline(StandardScaler -> estimator) or a Keras Normalization layer adapted on the training split and saved inside the model, so the served model can never receive unscaled or wrongly ordered inputs; save the ordered feature names and target encoding (0=CANDIDATE, 1=CONFIRMED, 2=FALSE POSITIVE) in a metadata JSON next to the artefact.
- Baselines before deep learning: flags-only rule, logistic regression and HistGradientBoosting on the same split (my untuned HistGB reached macro f1 0.857 / accuracy 0.891 vs the NN's 0.798 / 0.847). Keep a neural net only if it beats them under proper validation, and then use a small regularised MLP (dropout/L2, early stopping), not 107k parameters for 6.7k rows.
- Report two variants as CLAUDE.md requires: with flags (reproduces the vetting logic) and physics-only (no koi_fpflag_*, no koi_score); state the target (koi_disposition, 3 classes) explicitly; lead with macro f1, balanced accuracy, per-class f1 and the confusion matrix, and never quote a bare percentage.
- Validation protocol: split train/validation/test (or stratified K-fold on the training portion) for every model-selection decision - epochs, architecture, tuner trials; touch the test set once at the end and say so. If tuning, use keras_tuner (new package name) or Optuna with macro-f1 on validation folds, tune learning rate and regularisation as well as widths, and log trials to a committed CSV instead of screenshots.
- Reproducibility: set numpy/TF seeds, pin versions in pyproject, keep export cells live and path-managed (kepler.paths, models/), save in native .keras format, and write the metrics that the notes and README quote from a results table produced by code (no hand-typed numbers).
- Detect overfitting: plot training and validation loss/accuracy together, use EarlyStopping(restore_best_weights=True), and check calibration if probabilities will be shown to users (the 2020 test loss of 1.2055 vs training 0.0197 is a warning sign).
- Feature engineering worth a look for the CANDIDATE-vs-CONFIRMED problem: system multiplicity (number of KOIs per kepid) - in the processed table 69.5% of non-FP KOIs in multi-KOI systems are CONFIRMED vs 39.0% of single KOIs (my crosstab) - which reflects validation-by-multiplicity (Lissauer et al. 2012, 'Almost All of Kepler's Multiple-planet Candidates Are Planets', ApJ 750, 112, https://iopscience.iop.org/article/10.1088/0004-637X/750/2/112). The dropped TCE_Planet_Number was a weak proxy for this (62.5% vs 48.1%). Conversely, Transit Epoch and Kepler magnitude are poor things to ask a web user to supply.
- Housekeeping: plain Markdown headers, warm (non-blue) palette set once for the loss/accuracy plots, remove unused imports and LOG_DIR, and either document or delete the orphaned trained_kepler.h5 (23-input 70/70+LeakyReLU model).

## Finding details

### 04-F1 — Served 17-feature network is trained on unscaled data while the exported scaler is applied to its inputs in the web app (train/serve skew)

> [!danger] high · bug · cells [33, 34, 35, 36]

**Evidence**

Cell [33] fits the scaler and builds X_train_scaled / X_test_scaled, but cell [35] trains on the raw frame: `fit_model = nn.fit(X_train, y_train, epochs=200)` and cell [36] evaluates on the raw frame: `model_loss, model_accuracy = nn.evaluate(X_test,y_test,verbose=2)`. The cell comment claims "(same parameters as above, just increasing the epochs)". The output betrays raw units: cell [35] epoch 1 "loss: 661.5233 - accuracy: 0.28 ... 0s 1ms/step - loss: 106.5716 - accuracy: 0.5004" versus cell [13] (scaled) epoch 1 "loss: 1.0804 ... loss: 0.4030 - accuracy: 0.7923". archive/webapp_flask_2020/app.py lines 48-60: `scaler = load('model/scaler_param.joblib')` ... `input_variables_scaled = scaler.transform(input_variables_df)` ... `prediction = model.predict(input_variables_scaled)[0][2]`.

**Reproduction**

Extracted the full stream output of cell [35] from the ipynb with json: final-batch loss/accuracy at epoch 1 = 106.5716/0.5004, epoch 10 = 27.4140/0.5350, epoch 50 = 0.4748/0.8135, epoch 200 = 0.3257/0.8658; majority-class share of the training split = 3393/6708 = 0.5058, so the net sat at the majority-class rate for ~10 epochs. Raw feature scales from my StandardScaler refit on the reproduced training split: Insolation_Flux std 180,610; Transit_Depth std 82,352; Planetary_Radius std 3,589; Stellar_Teff std 792; the four flags std 0.34-0.43. Whether the shipped kepler_NN.h5 itself was trained on scaled or raw inputs is UNVERIFIED (TensorFlow not installed; per instructions I did not run the network). Circumstantial only: h5 first-layer weight RMS is 3.50-4.37 on the four flag inputs vs 0.066-0.416 on the 13 continuous inputs (Glorot-uniform init RMS for 17->260 = 0.085), which reads more naturally as standardized-input training, but this is inconclusive.

**Impact**

The 17-feature network as coded in the saved notebook learned in raw units; if that network is the one served, every web-app NN prediction receives inputs in the wrong units and the served probabilities are meaningless. Even if an earlier session trained it correctly, the committed code and the serving code disagree, and the notebook's reported 0.8350 accuracy belongs to a model that never saw the scaler.

**Recommendation**

Make scaling part of the model object so it cannot be skipped: an sklearn Pipeline(StandardScaler, model), or a Keras Normalization layer adapted on X_train and saved inside the model. In the rewrite, load the archived h5 under TensorFlow once and evaluate it on scaled vs raw X_test to settle which convention it was trained with, and record the answer in notes/Research Log/.

**Verifier: ✅ confirmed**

*Corrected statement:* The committed notebook trains the served 17-feature network on unscaled inputs (cell [35] `fit_model = nn.fit(X_train, y_train, epochs=200)`, cell [36] `nn.evaluate(X_test, y_test)`), while app.py line 56 applies scaler_param.joblib before `model.predict` (line 60). The reviewer left it unverified whether the shipped kepler_NN.h5 itself was raw-trained; the saved Adam optimizer state in that file strongly indicates it was: the first-layer second-moment estimates span 10^9.0 across input rows and correlate at r=0.935 (log-log slope 0.77) with the raw feature second moments, whereas the orphan trained_kepler.h5 (a scaled-input model) spans 10^3.0 with r=-0.14. Train/serve skew is therefore almost certainly live in the 2020 app, not just in the code as written. Definitive proof still requires loading the h5 under TensorFlow and evaluating on scaled vs raw X_test.

*Verifier evidence:* Re-read cells [33]-[36] in the view (code quoted above). Parsed the cell [35] stream from the ipynb: final-batch loss/acc epoch 1 = 106.5716/0.5004, 10 = 27.4140/0.5350, 50 = 0.4748/0.8135, 200 = 0.3257/0.8658; epochs 1-12 accuracies 0.50-0.57 vs majority share 3393/6708 = 0.5058 (my split reproduction). Raw stds from my StandardScaler refit: Insolation 180,610; Depth 82,352; Radius 3,589; Teff 792; flags 0.337-0.427. Read kepler_NN.h5 with h5py: per-input first-layer kernel RMS flags 3.84/3.50/4.37/3.77 vs continuous 0.066-0.416 (Glorot RMS 0.085) — matches the reviewer. New check: optimizer_weights/Adam/dense_32/kernel/v mean per input row: Teff 6.6, Depth 0.90, Insolation 0.89, Teq 0.24 ... flags 7e-9 to 2.4e-8, Impact 8e-8; max/min ratio 9.4e8; corr(log v, log E[x_raw^2] on the training split) = 0.935. Control trained_kepler.h5 dense_5: spread 10^3.0, corr -0.138, slope -0.02. app.py lines 48-60 quoted in my read of the file.

### 04-F2 — Shipped web-app artefacts (scaler_param.joblib, kepler_NN.h5) are not reproducible from the saved notebook

> [!danger] high · reproducibility · cells [32, 33, 34, 35, 40]

**Evidence**

Both export cells are commented out and were executed as no-ops: cell [34] `# dump(scaler, save_location)` (exec 17) and cell [40] `# nn.save(save_location)` (exec 22). Cell [32] defines the split as `train_test_split(X, y, random_state=1, stratify=y)` giving `(6708, 17)`.

**Reproduction**

Loaded archive/webapp_flask_2020/model/scaler_param.joblib (StandardScaler pickled by sklearn 0.23.2; n_features_in_=17, n_samples_seen_=6708, no feature_names_in_). Compared with a StandardScaler fit on the reproduced random_state=1 stratified training split: max |mean_ difference| = 838.24 (Insolation mean 9,047.27 saved vs 8,209.02 refit; Planetary_Radius mean 98.04 vs 124.99), max relative scale_ difference = 11.1% (Impact_Parameter 3.085 vs 3.469); np.allclose is False for both. Brute-forced random_state 0-300 with and without stratify: closest candidate has max |mean diff| 93.9 (rs=223), i.e. no split of the committed pickle reproduces the saved scaler; an unshuffled split gives 9,530. Parsed kepler_NN.h5 model_config from the file bytes (no inference): model name "sequential_8" with layers dense_32..dense_35, whereas a clean run of this notebook would name the second model sequential_1 / dense_4..7; Adam iteration counter in optimizer_weights = 42,000 = 200 epochs x 210 steps (ceil(6708/32)=210), consistent with cell [35]'s epochs=200 on 6,708 rows.

**Impact**

The numbers in the deck/README and the model served by the 2020 app cannot be tied to any committed code state. The scaler was fit on a different training subset than the notebook produces, and the h5 came from a session that had built nine or more models; whether scaler and model are even mutually consistent is unverifiable.

**Recommendation**

Keep export cells live and write to models/ with a metadata sidecar (ordered feature list, target encoding, split seed, hash of the training table, metrics, library versions). Regenerate all served artefacts from a single clean run and treat archive/webapp_flask_2020/model/* as historical only.

**Verifier: ✅ confirmed**

*Corrected statement:* Neither shipped artefact can be regenerated from the saved notebook: both export cells are commented out (cell [34] `# dump(scaler, save_location)`, exec 17; cell [40] `# nn.save(save_location)`, exec 22) and the 22 code cells carry consecutive execution counts 1-22. The saved scaler (sklearn 0.23.2, n_features_in_=17, n_samples_seen_=6708, no feature_names_in_) does not match a StandardScaler fit on the notebook's random_state=1 one-hot-stratified split (max |mean_ diff| 838.24 on Insolation: 9,047.27 vs 8,209.02; max relative scale_ diff 11.1% on Impact_Parameter 3.085 vs 3.469). Correction to the reviewer's search: their brute force stratified on integer labels, which is a different split family from the notebook's one-hot stratification (at rs=1 only 5,036/6,708 training rows coincide, chance level). Re-searching rs 0-2000 in all three modes (one-hot, integer, unstratified; 6,003 splits) finds nothing closer than max |mean diff| 43.93, so the conclusion stands and is stronger. The saved scaler is statistically a random 6,708-row subset of the same table (all 17 mean_ z-scores within ±2.45; flag mean_ x 6708 = 1093/1594/1381/874 exactly; var_ = p(1-p)), i.e. an unknown seed, not different data. kepler_NN.h5 is model sequential_8 with layers dense_32-dense_35 and Adam iter 42,000 = 200 x 210, so it came from a session that had already built eight 4-Dense-layer models; a clean run of this notebook would produce sequential_1 / dense_4-7.

*Verifier evidence:* Loaded scaler_param.joblib under sklearn 1.9.0 (InconsistentVersionWarning 0.23.2). Refit on the one-hot rs=1 split: reviewer's diffs reproduced to the digit. Computed one-hot vs integer rs=1 split overlap = 5036/6708 (expected 5031 by chance). Brute force 115 s: best (43.93, rs=1846, int), (53.96, rs=839, one-hot). z-scores vs full-table means with sampling-without-replacement SE: max |z| 2.45. h5py: model_config name sequential_8, layer_names dense_32..35, Adam/iter:0 = 42000, keras_version 2.4.0. Exec counts read from the ipynb JSON: [1..22] in cell order.

### 04-F3 — The four false-positive flag features hand the model the FALSE POSITIVE class; only the with-flags variant is reported

> [!danger] high · leakage · cells [7, 17, 18, 31]

**Evidence**

Cell [31] keeps `Not_Transit-Like_FPF`, `Stellar_Eclipse_FPF`, `Centroid_Offset_FPF`, `Ephemeris_Match_Indicates_Contamination_FPF` among the 17 served features (cell [7] keeps all four among the 23). Cell [18] output: class 2 precision 0.98 / recall 0.99 / f1 0.98 versus 0.70 and 0.71 for classes 0 and 1. No physics-only variant appears anywhere; CLAUDE.md's guardrail says "Never quote a single f1 without saying which variant".

**Reproduction**

On the identical 2,237-row test split: rows with any flag set = 1,155, of which 1,129 (97.7%) are FALSE POSITIVE; rows with no flag set = 1,082, of which 2 (0.2%) are FALSE POSITIVE. The rule "any flag -> FALSE POSITIVE" scores precision 0.977, recall 0.998, f1 0.988 for class 2 (the NN's class-2 f1 from the quoted confusion matrix is 0.984). LogisticRegression on the 4 flags alone: accuracy 0.754, per-class f1 0.000/0.674/0.988. HistGradientBoostingClassifier(random_state=1), 17 features with flags: accuracy 0.891, macro f1 0.857; 13 physics-only features: accuracy 0.755, macro f1 0.716, per-class 0.521/0.787/0.839. LogisticRegression physics-only: accuracy 0.624, macro f1 0.528.

**Impact**

Roughly half the test set (the FALSE POSITIVE class) is classified by re-reading the archive's own vetting flags; the headline 0.85 accuracy/weighted-f1 says little about learning physics from transit parameters. The hard problem, CANDIDATE vs CONFIRMED, is where the model is weak (306 of 1,106 non-FP test rows, 27.7%, are swapped between classes 0 and 1 in the quoted confusion matrix).

**Recommendation**

Report two variants side by side (with flags = reproduces the vetting logic; physics-only = no flags, no koi_score), lead with macro f1, balanced accuracy and per-class numbers, and say explicitly that the target is koi_disposition (3 classes).

**Verifier: ✅ confirmed**

*Corrected statement:* All 17 served features (cell [31]) and all 23 (cell [7]) include the four koi_fpflag columns, which by the project's own guardrail (CLAUDE.md line 67) constitute target leakage for the FALSE POSITIVE class; the notebook reports only the with-flags variant. On the 2,237-row test split: 1,155 rows have any flag set, 1,129 (97.7%) of them FALSE POSITIVE; 1,082 have none, only 2 (0.2%) FALSE POSITIVE. The rule 'any flag -> FALSE POSITIVE' scores class-2 precision 0.977 / recall 0.998 / f1 0.988, above the network's class-2 f1 0.984 recomputed from the cell [17] confusion matrix. The hard part is CANDIDATE vs CONFIRMED: 306 of 1,106 non-FP test rows (27.7%) are swapped between classes 0 and 1.

*Verifier evidence:* Re-ran the reviewer's checks.py: any-flag rule precision 0.977 recall 0.998 f1 0.988; LogReg flags-only acc 0.754 per-class f1 0.000/0.674/0.988; HistGB 17 features acc 0.891 macro f1 0.857; HistGB 13 physics-only acc 0.755 macro f1 0.716 per-class 0.521/0.787/0.839; LogReg physics-only 0.624/0.528. My own count on the split: 1155/1129 and 1082/2. CM arithmetic: (141+165)/(534+572) = 0.2767. CLAUDE.md line 67 quoted: 'Never quote a single f1 without saying which variant'.

### 04-F4 — Tuner (as written) validates on the test set, trains on raw X_train while validating on scaled X_test_scaled, and optimises plain accuracy

> [!warning] medium · leakage · cells [20, 21, 23, 26, 13, 35]

**Evidence**

RAW cell [23]: `tuner.search(X_train, y_train, verbose=2, epochs=100, validation_data=(X_test_scaled, y_test))` - training input is the unscaled DataFrame, validation input is the scaled array, and the validation set IS the test set. RAW cell [21]: `objective='val_accuracy', max_trials=100, executions_per_trial=1`. The best values shown in the cell [26] screenshot (`'input_units': 260, 'n_layers': 2, 'inner_0_units': 300, 'inner_1_units': 80`) are exactly the architecture hard-coded in cells [13] and [35], so the flawed selection propagated into the final models. RAW cell [20] tunes only layer widths (20-300 step 20) and depth (1-4); no learning rate, regularisation, batch size or early stopping.

**Reproduction**

Not run (RAW cells are inert and keras-tuner is out of scope). archive/keras_tuner_2020/oracle.json parsed in Python: search space = 6 Int hyperparameters identical to cell [20]; tried_so_far = 67 trial ids plus 1 ongoing trial (run did not reach max_trials=100); "values" = defaults (all units 20, n_layers 1), not the best trial. The size of the optimistic bias on later test scores is unverified.

**Impact**

Model selection used the same 2,237 rows later reported as the held-out test score, so the reported test accuracies are optimistically biased (probably modestly, given 68 trials, but unquantified). Because the trials trained on raw units and were scored on standardized units, val_accuracy compared models in a regime they never trained in, so the choice of 260/300/80 rests on a corrupted objective; accuracy on a 24/26/50 class mix mostly rewards getting the flag-determined class right.

**Recommendation**

Tune on a validation fold (or stratified K-fold) carved from the training split only; use macro f1 or balanced accuracy as the objective; include learning rate, dropout/L2, batch size and EarlyStopping in the search; log every trial to a committed CSV rather than screenshots.

**Verifier: ✅ confirmed**

*Corrected statement:* As written, RAW cell [23] `tuner.search(X_train, y_train, verbose=2, epochs=100, validation_data=(X_test_scaled, y_test))` trains trials on the unscaled 23-feature DataFrame, scores them on the standardized test set, and uses that same test set (later reported as held-out) as the selection objective (`objective='val_accuracy'`, cell [21]); the search space (cell [20]) covers only widths 20-300 step 20 and depth 1-4. Two caveats the reviewer stated or implied: RAW cells are inert, so whether the tuner actually ran with exactly this code is unverifiable; and the cell [28] screenshot (first layer 6,240 params = 23x260+260) shows the search was run on 23 inputs, so the 260/300/80 architecture reused in cells [13] and [35] was never tuned for the 17-feature served model. Minor wording: cell [20] has no hp.conditional_scope; inner_2/inner_3 are simply sampled and unused when n_layers=2.

*Verifier evidence:* Re-read RAW cells [20]-[25] and [27] from the ipynb source (quoted). Parsed oracle.json: space == the six hp.Int calls in cell [20] (checked programmatically, True); 67 unique tried_so_far + 1 ongoing; values = defaults. Screenshot cell [26] read by eye: {'input_units': 260, 'n_layers': 2, 'inner_0_units': 300, 'inner_1_units': 80, 'inner_2_units': 140, 'inner_3_units': 300}; cell [28]: dense 6240 / 78300 / 24080 / 243, total 108,863. Arithmetic: 23*260+260 = 6240. Bias size from test-set selection not quantified (would need the tuner).

### 04-F5 — The deck/README '84% f1' is not an f1 the notebook ever computes; the only f1 values are macro 0.80 / weighted 0.85 for the 23-feature model

> [!warning] medium · claim-vs-data · cells [14, 18, 36]

**Evidence**

Cell [18] (23-feature scaled model): `macro avg 0.80 0.80 0.80`, `weighted avg 0.85 0.85 0.85`, per-class f1 `0.70 / 0.71 / 0.98`. Cell [36] (17-feature model that was exported): only `Loss: 0.4477795660495758, Accuracy: 0.8350469470024109`; no confusion matrix, no f1. README line 55: "Neural Net: 84%" under "Current f1 scores". Keras metrics are `metrics=["accuracy"]` in cells [13] and [35].

**Reproduction**

Recomputed from the confusion matrix quoted in cell [17] ([[378,141,15],[165,395,12],[3,6,1122]]): per-class f1 0.7000 / 0.7092 / 0.9842; macro f1 0.7978; weighted f1 0.8460; accuracy 0.8471; balanced accuracy 0.7968. Rounding checks in code: 0.8350469 -> 84%; the stale markdown's 0.8395172 -> 84%.

**Impact**

'84% f1' is most plausibly the 17-feature model's accuracy (0.835) or a truncation of the 23-feature model's weighted f1 (0.846); neither is a macro f1, and the exported model has no f1 at all. Readers cannot tell which model or which averaging is meant.

**Recommendation**

Every quoted score should name the metric, the averaging (macro/weighted/per-class), the feature variant and the model artefact; put a single results table in the notebook and quote from it.

**Verifier: ✅ confirmed**

*Corrected statement:* The notebook computes f1 exactly once (cell [18], 23-feature scaled model, sklearn classification_report on argmax predictions): per-class 0.70/0.71/0.98, macro 0.80, weighted 0.85 (unrounded from the cell [17] confusion matrix: 0.7000/0.7092/0.9842, macro 0.7978, weighted 0.8460, accuracy 0.8471, balanced accuracy 0.7968). The exported 17-feature model (cell [36]) has only Keras accuracy 0.8350469 and no f1. README line 55 'Neural Net: 84%' under 'Current f1 scores' (line 51) therefore matches no computed f1: it rounds from the 17-feature accuracy (0.835 -> 84%) or the stale markdown 0.8395 (-> 84%); the weighted f1 0.846 rounds to 85%, so it would have to be a truncation.

*Verifier evidence:* grep -n on README.md: line 51 'Current f1 scores:', line 55 'Neural Net: 84%', line 56 the relu/softmax note. Recomputed all metrics from the quoted CM in Python; f-string rounding: 0.8350469 -> '84%', 0.8395172 -> '84%', 0.8460 -> '85%'. Cells [13]/[35] compile with metrics=['accuracy'] (view).

### 04-F6 — Stale hand-typed markdown claims a 'small increase in accuracy' that the saved outputs contradict

> [!warning] medium · claim-vs-data · cells [14, 35, 36, 37]

**Evidence**

Cell [37]: "Small increase in accuracy: 0.857398271560669 vs. 0.8395172357559204 previously". Neither number appears in any output: cell [14] prints `Accuracy: 0.8471166491508484` and cell [36] prints `Accuracy: 0.8350469470024109`. Cell [35]'s comment "(same parameters as above, just increasing the epochs)" is also wrong: the cell changes the feature set from 23 to 17 and drops the scaling.

**Reproduction**

Direct comparison of the two quoted outputs: 0.8350 is 1.2 percentage points below 0.8471, i.e. the saved run shows a decrease, not an increase. (No model run needed.)

**Impact**

The narrative leads a reader to believe the served 17-feature/200-epoch model is better than the 23-feature one; the saved evidence says the opposite.

**Recommendation**

Generate comparison text from variables (f-strings) or a results DataFrame; never hand-type metrics into markdown.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell [37] markdown ('Small increase in accuracy: 0.857398271560669 vs. 0.8395172357559204 previously') matches no output: cell [14] prints Accuracy 0.8471166491508484 and cell [36] prints Accuracy 0.8350469470024109, a decrease of 1.2 points. Cell [35]'s comment '(same parameters as above, just increasing the epochs)' is also wrong: the feature set changes from 23 to 17 and scaling is dropped (epoch-1 running loss 106.6 vs 0.40).

*Verifier evidence:* Direct reading of cells [14], [35], [36], [37] in the view; grep of the ipynb for '0.8573' and '0.8395' finds them only in the markdown cell.

### 04-F7 — Severe overfitting goes undetected: no validation data, no early stopping, no regularisation, and only training curves are plotted

> [!warning] medium · methodology · cells [13, 14, 15, 16, 35, 38, 39]

**Evidence**

Cell [13]: `fit_model = nn.fit(X_train_scaled, y_train, epochs=100)` with no validation_split/validation_data/callbacks; cell [14] output `loss: 1.2055 - accuracy: 0.8471`; cells [15]-[16] plot only `history_df.plot(y="loss")` and `y="accuracy"` (training history has no val_ keys). Same pattern at 200 epochs in cells [35], [38], [39].

**Reproduction**

From the full stream output of cell [13] extracted from the ipynb: final-batch training loss/accuracy at epoch 1 = 0.4030/0.7923, epoch 10 = 0.2807/0.8555, epoch 50 = 0.1107/0.9551, epoch 100 = 0.0197/0.9951. Parameter counts computed: 108,863 for the 23-input net (matches the cell [28] screenshot) and 107,303 for the 17-input net, against 6,708 training rows.

**Impact**

Training accuracy 99.5% vs test 84.7%; test cross-entropy 1.2055 is about 61x the final training loss 0.0197, i.e. the model is confidently wrong on the test set. The web app displays the softmax output as a percentage ('prob'), so calibration matters and is poor.

**Recommendation**

Hold out a validation split, use EarlyStopping(restore_best_weights=True), add dropout or L2, plot training and validation curves together, and check calibration (e.g. reliability curve) if probabilities are shown to users.

**Verifier: ✅ confirmed**

*Corrected statement:* No validation data, callbacks, or regularisation in either training call (cell [13] `nn.fit(X_train_scaled, y_train, epochs=100)`, cell [35] epochs=200); only training curves are plotted (cells [15]-[16], [38]-[39]). Per-epoch running training loss/accuracy in cell [13]: epoch 1 0.4030/0.7923, 10 0.2807/0.8555, 50 0.1107/0.9551, 100 0.0197/0.9951, against test loss 1.2055 / accuracy 0.8471 (cell [14]); the test cross-entropy is 61x the final training loss. Parameter counts 108,863 (23 inputs, matches the cell [28] screenshot) and 107,303 (17 inputs) for 6,708 training rows.

*Verifier evidence:* Parsed both training streams from the ipynb (100 and 200 epochs recovered); numbers identical to the reviewer's. Computed 23*260+260 + 260*300+300 + 300*80+80 + 80*3+3 = 108,863 and the 17-input variant 107,303. 1.2055/0.0197 = 61.2. Note Keras prints a running mean over the epoch, which does not change the conclusion.

### 04-F8 — A default gradient-boosting model beats the 107k-parameter network on the same split in seconds

> [!note] low · methodology · cells [13, 18, 35, 36]

**Evidence**

Notebook NN results: accuracy 0.8471 / macro f1 0.80 (cell [18]) and accuracy 0.8350 (cell [36]). README ranks 'Gradient Boosted Tree: 90%, Random Forest: 90%, Neural Net: 84%'.

**Reproduction**

HistGradientBoostingClassifier(random_state=1) on the identical 17-feature split, no tuning: accuracy 0.891, macro f1 0.857, per-class f1 0.784/0.800/0.987, fit time 6.4 s. LogisticRegression on the same 17 scaled features: accuracy 0.814, macro f1 0.748.

**Impact**

The network (and the multi-hour tuner search) adds complexity without accuracy; the deck's own ranking agrees. For a 9k-row tabular problem this is expected.

**Recommendation**

Establish baselines (flags-only rule, logistic regression, gradient boosting) before any neural net; keep the NN only if it wins under a proper validation protocol, and then prefer a small regularised MLP.

**Verifier: ✅ confirmed**

*Corrected statement:* An untuned HistGradientBoostingClassifier(random_state=1) on the same 17-feature, random_state=1 one-hot-stratified split reaches accuracy 0.891 / macro f1 0.857 (per-class 0.784/0.800/0.987) in seconds, versus the notebook's quoted NN results of accuracy 0.8471 / macro f1 0.80 (23 features) and accuracy 0.8350 (17 features). Caveat: the NN figures are the 2020 outputs, not re-run, and exact row identity of the split under sklearn 0.23.2 is assumed (class counts 534/572/1131 match).

*Verifier evidence:* Re-ran checks.py: 'HistGB 17 with flags acc=0.891 macroF1=0.857 perclass=[0.784 0.8 0.987]'; 'LogReg 17 with flags acc=0.814 macroF1=0.748'. Whole script wall time 7.4 s. README lines 52-55 rank GBT/RF 90% above NN 84%.

### 04-F9 — Tuner results survive only as screenshots; the archived oracle.json holds the search space and defaults, not the best trial, and the run stopped at 68 of 100 trials

> [!note] low · reproducibility · cells [19, 24, 25, 26, 27, 28]

**Evidence**

Cell [19] markdown: "HYPERTUNING in RAW cells due to long runtimes". Cells [26] and [28] are embedded PNG attachments (extracted to /tmp/review/scratch/04_neural_net/): cell [26] shows `{'input_units': 260, 'n_layers': 2, 'inner_0_units': 300, 'inner_1_units': 80, 'inner_2_units': 140, 'inner_3_units': 300}`; cell [28] shows Model "sequential" with Dense 260/300/80/3 and Total params 108,863 (a 23-input model). archive/keras_tuner_2020/tuner0.json is `{}`.

**Reproduction**

Parsed oracle.json: keys ongoing_trials/hyperparameters/seed/seed_state/tried_so_far; 67 ids in tried_so_far plus ongoing {'tuner0': '2212b186...'}; hyperparameters.values = {'input_units': 20, 'n_layers': 1, 'inner_0_units': 20, ...} (the Int defaults), search space identical to RAW cell [20]. Verified 23*260+260 = 6,240 and total 108,863 match the screenshot.

**Impact**

The best trial's val_accuracy and its margin over other trials are unknowable, so the claim that tuning improved the model cannot be checked; inner_2/inner_3 values in the screenshot are unused leftovers of the conditional search space.

**Recommendation**

Persist tuner.results_summary() and get_best_hyperparameters() as text/CSV in the repo (or keep the trial_*/trial.json files), and cite them from the notebook instead of images.

**Verifier: ✅ confirmed**

*Corrected statement:* Tuner results survive only as two PNG attachments (cells [26] and [28]); archive/keras_tuner_2020/oracle.json holds the search space (identical to cell [20]), seed 3494, 67 unique completed trial hashes plus one ongoing trial, and 'values' equal to the Int defaults (all 20, n_layers 1), not the best trial; tuner0.json is '{}'. Because keras-tuner rewrites oracle.json when each trial ends, the archived file was last written during trial 68 of max_trials=100; whether the run continued after that snapshot is unknown. The best trial's val_accuracy and its margin over other trials are unrecoverable.

*Verifier evidence:* Extracted the two attachments from the ipynb and hashed them: sha256 prefixes 7a7703433cc0bf56 and 047118771361f067, identical to the reviewer's PNGs; viewed both images and confirmed the transcriptions. Parsed oracle.json in Python: 67 tried (all unique), ongoing {'tuner0': '2212b186...'}, values all defaults, space == cell [20] (True). tuner0.json content '{}'.

### 04-F10 — No random seeds and a 2020-pinned stack (Python 3.7.6, TF/Keras 2.4.0, sklearn 0.23.2, 'kerastuner' import) make the notebook non-reproducible today

> [!note] low · reproducibility · cells [1, 13, 35]

**Evidence**

Cell [1] imports `from kerastuner.tuners import RandomSearch` (package since renamed keras_tuner) and never calls tf.random.set_seed or np.random.seed; cells [13]/[35] build fresh models with default random initialisation.

**Reproduction**

Notebook metadata: kernelspec 'PythonData', language_info version 3.7.6. kepler_NN.h5 root attrs: keras_version '2.4.0', backend 'tensorflow'. Loading scaler_param.joblib under sklearn 1.9.0 warns 'Trying to unpickle estimator StandardScaler from version 0.23.2'; GBT.pkl fails with ModuleNotFoundError 'sklearn.ensemble._gb_losses' and BRF.pkl fails with an incompatible tree node dtype (SLR.pkl loads: LogisticRegression, n_features_in_=17, classes_ [0,1,2]).

**Impact**

Re-running gives different weights and scores each time, and most archived artefacts cannot be opened in the refreshed environment.

**Recommendation**

Set numpy/TF seeds, pin versions in pyproject, save Keras models in the native .keras format and sklearn models via skops or joblib with recorded versions, and store metrics with the artefact.

**Verifier: ✅ confirmed**

*Corrected statement:* No seeds anywhere in the notebook (zero occurrences of 'seed' in the ipynb), kernelspec PythonData / Python 3.7.6, `from kerastuner.tuners import RandomSearch` (old package name), kepler_NN.h5 keras_version 2.4.0. Under the refreshed stack: scaler_param.joblib loads with InconsistentVersionWarning (0.23.2 -> 1.9.0); SLR.pkl loads (LogisticRegression, n_features_in_=17, classes_ [0,1,2]); GBT.pkl fails (ModuleNotFoundError: sklearn.ensemble._gb_losses); BRF.pkl fails (incompatible tree node dtype).

*Verifier evidence:* grep -c -i seed notebooks/04_neural_net.ipynb -> 0. Notebook metadata read from JSON. h5py root attrs: backend tensorflow, keras_version 2.4.0. joblib.load of each artefact under sklearn 1.9.0 with warnings captured (messages quoted above).

### 04-F11 — Target, class encoding and feature-order contract are never stated; the app rebuilds the 17-column order by hand

> [!note] low · documentation · cells [7, 17, 31, 33]

**Evidence**

Cell [7] `y = to_categorical(keplerProcessed_df["Exoplanet_Archive_Disposition"])`; cell [17] labels rows "Actual 0/1/2" without saying which class is which; app.py line 51 builds `pd.DataFrame([[input_2, input_5, input_1, input_3, input_9, input_13, input_8, input_11, input_4, input_17, input_10, input_12, input_6, input_16, input_15, input_7, input_14]], columns=["c1",...,"c17"])` and line 60 treats `[0][2]` as the not-a-planet probability.

**Reproduction**

Join of the processed index to the raw CSV (0 misses): 0=CANDIDATE 2,136, 1=CONFIRMED 2,285, 2=FALSE POSITIVE 4,524 (alphabetical LabelEncoder order). I checked the app's hand-written order input by input against the 17 columns left by cell [31]: all 17 positions match (Not_Transit-Like_FPF, Stellar_Eclipse_FPF, Centroid_Offset_FPF, Ephemeris_Match..., Orbital_Period, Transit_Epoch, Impact_Parameter, Transit_Duration, Transit_Depth, Planetary_Radius, Equilibrium_Temperature, Insolation_Flux, Transit_SNR, Stellar_Teff, Stellar_Surface_Gravity, Stellar_Radius, Kepler_band). The saved scaler has no feature_names_in_ (sklearn 0.23.2), so nothing would catch a reorder.

**Impact**

Correct today but silent and fragile; the 'Two Ys' guardrail asks every model notebook to state that the target is koi_disposition (3 classes).

**Recommendation**

State target and encoding in a markdown cell, store the ordered feature list with the artefact, and assert feature names at serve time (modern sklearn does this automatically when fit on a DataFrame).

**Verifier: ✅ confirmed**

*Corrected statement:* The notebook never states the target or its encoding; joining the processed index to the raw CSV gives 0=CANDIDATE (2,136), 1=CONFIRMED (2,285), 2=FALSE POSITIVE (4,524). app.py line 51 rebuilds the 17-column order by hand from form inputs; I verified all 17 positions against the columns left by cell [31] and, additionally, against the HTML form labels in templates/main.html (lines 28-89), which agree with the app's original_input dict. The saved scaler carries no feature_names_in_, so a reorder would be silent.

*Verifier evidence:* crosstab from the reviewer's script (0 join misses). Position-by-position comparison of app order [2,5,1,3,9,13,8,11,4,17,10,12,6,16,15,7,14] with X17.columns: 17/17 match. grep of main.html shows input_1 = Centroid Offset FPF ... input_17 = Planetary Radius, same as app.py lines 84-100. hasattr(saved,'feature_names_in_') is False.

### 04-F12 — Dead imports, unused variables, and an orphaned older model file

> [!note] low · dead-code · cells [1, 3, 34, 40]

**Evidence**

Cell [1]: `LOG_DIR = f"{int(time.time())}"` is never used; unused imports include scipy.stats, plotly.express/graph_objects, matplotlib.gridspec, LeakyReLU, HyperParameters, OneHotEncoder, LabelEncoder, SimpleImputer, mean_squared_error, r2_score, balanced_accuracy_score, precision_score, recall_score, and mlxtend's SequentialFeatureSelector/EnsembleVoteClassifier/plot_decision_regions. Cell [3] `file_path_Raw` is never used. Cells [34] and [40] are fully commented out.

**Reproduction**

Parsed archive/webapp_flask_2020/model/trained_kepler.h5 config from bytes: a 23-input Sequential with Dense 70 relu, Dense 70 relu, LeakyReLU, Dense 3 softmax (categorical_crossentropy, Adam) that neither app.py nor this notebook references; it matches the stray LeakyReLU import.

**Impact**

Clutter, plus an undocumented earlier architecture whose scores may be what some deck numbers refer to.

**Recommendation**

Trim imports to what is used, delete or document trained_kepler.h5, and replace commented-out export cells with live, path-managed exports.

**Verifier: ✅ confirmed**

*Corrected statement:* An AST pass over all code cells finds 26 of 36 imported names never used in executed code (the reviewer's list is a subset; also unused: Sequential, Dense (the code uses tf.keras.layers.Dense), f1_score, accuracy_score, plt, skl, RandomSearch (RAW cells only), dump and os (commented-out code only)); LOG_DIR and file_path_Raw are assigned and never read; cells [34] and [40] are fully commented out. archive/webapp_flask_2020/model/trained_kepler.h5 is an orphan 23-input model (sequential_1: Dense 70 relu, Dense 70 relu, LeakyReLU alpha=0.1, Dense 3 softmax; categorical_crossentropy, Adam; Adam iter 52,500 = 250 epochs x 210 steps) referenced by no text file in the repo; its optimizer state indicates scaled-input training.

*Verifier evidence:* ast.parse over concatenated code cells (magics stripped): imported 36, unused 26 (list printed in my session). grep -rIl trained_kepler over the repo (excluding .venv/.git) -> none. h5py read of trained_kepler.h5 model_config and Adam/iter:0 = 52500.
