---
tags: [research-log, review, summary]
date: 2026-08-24
source: multi-agent review workflow wf_29148ee0-552 (5 reviewers + 5 adversarial verifiers, 1.29M tokens, 63 min)
---

# 2026-08-24 Phase 2 review — summary

> [!abstract] Five lines
> - **59 findings** across the five notebooks: 13 high · 23 medium · 23 low. Verifiers re-ran the evidence: **56 confirmed, 3 partially, 0 refuted**, plus 14 items the verifiers added.
> - The **headline numbers do not mean what the deck says**: 83/90/90 are accuracy and weighted f1 (macro f1 is 0.77/0.87/0.87), and about half of that score is a lookup of the vetting flags.
> - The **habitable-zone result is not defensible**: the filter never looks at the planet; the 12 "habitable" planets are 3.3–11.7 Earth radii receiving 1.5–4.9× Earth's sunlight.
> - The **2020 web app was very likely broken**: its neural net was trained on unscaled data while the app scaled inputs, the shipped model files cannot be reproduced, and its verdict is 99.9% "did you tick a flag".
> - A **plaintext database password** has been public in the repo since 2020; redacted from the tracked tree in this batch, still in git history (Rich's call).

Per-notebook evidence (every number reproduced in-session, cell references included):
[01 cleaning & EDA](2026-08-24%20Review%2001_cleaning_eda.md) · [02 clustering](2026-08-24%20Review%2002_clustering.md) · [03 sklearn models](2026-08-24%20Review%2003_sklearn_models.md) · [04 neural net](2026-08-24%20Review%2004_neural_net.md) · [05 habitable zone](2026-08-24%20Review%2005_habitable_zone.md)

## Scorecard

| Notebook | High | Medium | Low | Verifier | Headline |
|---|---|---|---|---|---|
| 01 cleaning & EDA | 2 | 5 | 6 | 11 ✅ 2 🟡 | FP flags kept as features; chained `fillna(inplace=True)` silently breaks under pandas 3 (2,282 rows, 2 classes); 619 rows dropped, not 363 |
| 02 clustering | 2 | 5 | 5 | 12 ✅ | k-means on unscaled data (transit depth = 99.9% of variance); "elbow at 4" refuted; clusters carry no disposition signal (ARI 0.004); all 5,023 false positives silently dropped first |
| 03 sklearn models | 3 | 5 | 4 | 12 ✅ | Flags supply the score (GBT macro f1 0.87 → 0.71 without them); web-app LR "accuracy" is a stale `y_pred` from the BRF; GBT tuned on the test set; scaler not shared with the NN |
| 04 neural net | 3 | 4 | 5 | 12 ✅ | Served 17-feature net trained unscaled while the app scales inputs; shipped `.h5`/scaler not reproducible; tuner validated on the test set; 99.5% train vs 84.7% test accuracy |
| 05 habitable zone | 3 | 4 | 3 | 9 ✅ 1 🟡 | No planet property used; deck lists 5 criteria, code runs 4; README's 11 comes from a superseded version; inner join drops 434 KOIs; password in tracked archive |

## The 7 findings that change the project

> [!danger] 1. Target leakage is doing most of the work
> With the notebook's own split, removing the four `koi_fpflag_*` columns takes GBT from accuracy 0.90 / macro f1 0.87 to 0.75 / 0.71 (LR 0.83/0.77 → 0.66/0.56; BRF 0.90/0.87 → 0.73/0.71). The rule "any flag → FALSE POSITIVE" alone scores FP-class f1 0.991, the same as the full models. The 2020 web app's planet/not-planet verdict equals "no flag ticked" on 99.9% of test rows. *(03-F1, 03 missed #1, 01-F1, 04-F3)*

> [!danger] 2. The metrics are mislabelled
> 83 / 90 / 90 are accuracy and support-weighted f1, which coincide because FALSE POSITIVE is 50.6% of the test set and scores 0.99. Macro f1: 0.77 / 0.87 / 0.87; CANDIDATE and CONFIRMED f1 sit at 0.63–0.82. The NN's "84% f1" is not an f1 the notebook computes (its only f1 is macro 0.80 / weighted 0.85; 0.835 is the 17-feature model's accuracy). *(03-F4, 04-F5)*

> [!danger] 3. The habitable-zone screen never looks at the planet
> Filter terms: period, stellar Teff, stellar radius, metallicity. Survivors: 12 confirmed with radii 3.28–11.67 R⊕ (9 of 12 ≥ 6 R⊕, Neptune to Jupiter class) and insolation 1.49–4.93 Earth flux; 0 of 12 inside the conservative Kopparapu band (0.35–1.02). The 200–400 day window sits *inside* the inner edge for the Sun-like stars selected (their HZ starts at 402–812 days). A flat insolation screen finds a disjoint set: 27 planets at any radius, 13 at ≤ 2 R⊕, 7 at ≤ 1.6 R⊕ (provisional), 12 of the 13 orbiting stars cooler than 5,500 K, which the Teff cut excludes. *(05-F1, 05-F2, 05 missed #1)*

> [!danger] 4. The deployed model was probably broken and cannot be rebuilt
> The 17-feature network in the saved notebook trains on unscaled inputs while `app.py` applies `scaler_param.joblib` first; the saved optimizer state in the shipped `.h5` matches raw-unit training. Neither the scaler nor the model reproduces from any split of the committed data (export cells are commented out). The web-app logistic regression's printed accuracy 0.8994 is the 23-feature BRF's `y_pred` scored against the wrong model; its true accuracy is 0.8176. *(04-F1, 04-F2, 03-F2, 03-F3)*

> [!danger] 5. The clustering story is an artifact of not scaling
> Transit depth carries 99.91% of the unscaled variance, so the k=4 solution is four transit-depth bins (3,998 / 46 / 5 / 2 objects). No elbow at 4 by any criterion (kneedle picks 3 or 5; silhouette prefers 2). The clustered population silently excludes every FALSE POSITIVE and 22 confirmed planets (including Kepler-10 b) via a `KOI_Probability != 0` filter. Clusters have ARI 0.004 against the dispositions: a real null result the deck never stated. *(02-F1, 02-F2, 02-F5)*

> [!warning] 6. Data handling has silent failure modes
> 619 rows dropped (6.5%), not 363, and 9.9% of false positives vs 0.3% of confirmed planets, so missingness is a signal. `df["col"].fillna(..., inplace=True)` does nothing under pandas 3 copy-on-write; the notebook then keeps 2,282 rows and loses the CANDIDATE class entirely, with no exception. The habitable-zone inner join drops 434 KOIs (62 candidates) without a message; `koi_teq` is a deterministic transform of `koi_insol` (median ratio 255.0 K, 5th–95th percentile 254.7–255.3). *(01-F5, 01-F2, 05-F5, 05 claims)*

> [!danger] 7. Security: a database password is public
> A 12-character Postgres password and the AWS RDS endpoint were committed in Oct 2020 (commit `359e7de`) and are still in `archive/database/Connect to AWS postgres.ipynb` at HEAD. This batch redacts the tracked copy (`[REDACTED-2026-08-24]`). It remains in git history on GitHub, and possibly in the original team repo. If that password was ever reused, treat it as compromised. History rewrite = Rich's decision (force-push, re-clone). *(05-F10, 05 missed #2)*

## What holds up (keep in the rewrite)

- Staged data flow with an artifact per stage; every deterministic step reproduces from the raw CSV to 1e-13 six years later.
- `kepoi_name` as the row index (unique; `kepid` is not: 8,214 stars for 9,564 KOIs).
- Stratified split with fixed `random_state`, scaler fit on train only, confusion matrix + full classification report per model, balanced accuracy for the BRF.
- Physics-only feature set in the clustering notebook; `StandardScaler` before PCA with explained variance printed.
- The habitable-zone notebook's explicit one-criterion-per-line masks and per-criterion counts (easy to audit) and the idea of a "candidates worth a second look" list.
- The correct 3-class evaluation recipe in the NN notebook (argmax → sklearn report), and the archived tuner search space.

## Consequences for the plan (folded into the Roadmap)

- **Phase 2 rewrite:** one load path via `kepler.paths`; no raw-cell graveyard; explicit label mapping; keep `koi_score` numeric with an indicator; report the 619; tests that assert row counts and class labels after cleaning.
- **Phase 3 models:** two named feature sets (`with_flags`, `physics_only`) reported side by side; macro f1 + per-class f1 always; 5-fold stratified CV with error bars (single-split GBT-vs-BRF gap 0.004 is within fold noise 0.006–0.014); log1p on heavy-tailed columns (LR improves markedly); missingness indicators + NaN-native `HistGradientBoostingClassifier`; drop provenance features (RA/Dec, TCE delivery) from the physics variant.
- **Phase 4 habitable zone:** screen on `koi_insol` (with `_err1/_err2`) and `koi_prad`; decide whether K- and M-dwarf hosts are in scope (that is where Kepler's small HZ planets are); metallicity is not a habitability criterion; left join, report join losses.
- **Phase 4 neural net:** validation split, early stopping, calibration check; state the served decision rule; export with the feature order and scaler in one artifact.
- **Phase 5 app:** verdict must not be a flag lookup; show physics-only predictions with honest uncertainty; ship the model with its scaler and column contract.
- **Clustering:** keep as a short null-result notebook (scaled features, all classes, ARI reported) or retire it.
