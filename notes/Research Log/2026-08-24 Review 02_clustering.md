---
tags: [research-log, review, notebook-02]
date: 2026-08-24
source: multi-agent review workflow wf_29148ee0-552 (reviewer + adversarial verifier)
---

# 2026-08-24 Review: Notebook 02 clustering

> [!abstract] What the notebook does (reviewer's summary)
> The notebook loads the 2020 RAW pickle (9,564 x 50; identical to data/raw/cumulative_kaggle_snapshot.csv apart from float-parsing noise of order 1e-13, checked in my run), sets kepoi_name as the index, drops the *_err columns and renames to the long 2020 names (cell [9] prints (9564, 27); my re-run gives the same). It then builds cluster_df from 15 physics/stellar columns plus a derived "KOI_Probability" = (1 if koi_disposition is CANDIDATE/CONFIRMED else 0) x koi_score, drops rows with any null and rows where that product is 0, leaving 4,051 rows (cell [17]; my run: 2,259 CONFIRMED + 1,792 CANDIDATE, zero FALSE POSITIVEs). A markdown cell [19] asserts, with no code, the four "most important non-flag features" (transit depth, transit SNR, stellar radius, impact parameter); these trace to notebook 03's logistic-regression coefficients. Five raw cells sketch a dendrogram/agglomerative analysis with an interactive input() prompt; they never executed. The executed analysis is (a) k-means on the four features UNscaled: an inertia sweep k=1..10, "elbow at 4", a k=4 model and a 3D scatter, and (b) StandardScaler -> PCA(2) -> inertia sweep -> "elbow at 6" -> k=6 model -> 2D scatter. No cluster labels or figures are written to disk and no later notebook consumes this one (03 loads kepler_processed.pkl written by 01). Every stored number (shapes, both elbow curves, PCA variance ratios, cluster sizes stored inside the plotly figures) reproduces in the 2026 environment once KMeans n_init=10 (the 2020 default) is pinned; the notebook itself halts at cell [14] under pandas 2.x.

> [!warning] At a glance
> **12 findings**: 2 high · 5 medium · 5 low. Verifier verdicts: 12 confirmed · 0 partially · 0 refuted · 0 unverifiable. Verifier added 3 missed item(s). 9 deck/README claims checked.

## Findings at a glance

| ID | Severity | Category | Finding | Verifier |
|---|---|---|---|---|
| 02-F1 | high | methodology | k-means and the 'elbow at 4' run on unscaled features; transit depth carries 99.91% of the variance, so the clusters are transit-depth bins and no elbow exists at 4 | ✅ confirmed |
| 02-F2 | high | methodology | The clustering population silently drops every FALSE POSITIVE (5,023 rows) and 22 CONFIRMED planets via a derived 'KOI_Probability' filter; the code comment describes a different design | ✅ confirmed |
| 02-F3 | medium | leakage | The 'most important non-flag features' list is asserted without code; it comes from notebook 03's logistic-regression coefficient for the CANDIDATE class, trained with the four koi_fpflag_* leakage columns in X | ✅ confirmed |
| 02-F4 | medium | claim-vs-data | PCA to two components discards a third component (24.8%) almost as large as the second (25.3%); the four features are nearly uncorrelated, so '36% lost' reflects PCA being the wrong tool, not a finding | ✅ confirmed |
| 02-F5 | medium | methodology | Clusters are never evaluated against anything; they carry no disposition signal (ARI 0.0037 for k=4, 0.0006 for k=6) | ✅ confirmed |
| 02-F6 | medium | claim-vs-data | 'Elbow at 6' on the PCA branch is the more defensible elbow but still weak: silhouette prefers k=2, k=6 is two large halves plus four outlier groups, and the stored curve is not fully reproducible | ✅ confirmed |
| 02-F7 | medium | reproducibility | Notebook halts under pandas 2.x and its elbow numbers depend on an old scikit-learn default (n_init=10) | ✅ confirmed |
| 02-F8 | low | dead-code | Dead code: inert dendrogram cells reference undefined names and an interactive input(); unused import and variables | ✅ confirmed |
| 02-F9 | low | documentation | Comments and headers contradict the code, and stored outputs are not from a clean top-to-bottom run | ✅ confirmed |
| 02-F10 | low | other | The PCA dataframe throws away the kepoi_name index, so cluster labels cannot be traced back to objects | ✅ confirmed |
| 02-F11 | low | other | Plots use plotly's default blue and treat the integer cluster id as a continuous colour axis | ✅ confirmed |
| 02-F12 | low | methodology | Different random_state for the elbow sweeps (0) and the final models (5) | ✅ confirmed |

## Deck / README claims checked

| Verdict | Claim | Evidence |
|---|---|---|
| ❌ refuted | Deck / markdown [37]: 'elbow at 4' for k-means on the selected four features | From my run (repro_02_clustering.py): stored inertia reproduced exactly with n_init=10; successive ratios I(k)/I(k-1) = [0.367, 0.493, 0.548, 0.557, 0.691, 0.638, 0.623, 0.701, 0.745] show no kink at 4 (the first slow-down is after k=5); kneedle picks 3 (linear) or 5 (log); silhouette is highest at k=2 (0.989) and falls monotonically (k=4: 0.954); the k=4 solution is [3998, 2, 46, 5] objects, i.e. pure transit-depth bins, because transit depth is 99.91% of the unscaled variance. The curve is a smooth outlier-peeling decline, not an elbow. |
| 🟡 partially | Deck / markdown [51]: 'elbow at 6' for k-means on the 2-component PCA data | From my run: stored curve ratios [0.67, 0.71, 0.689, 0.592, 0.611, 0.831, ...] do slow sharply after k=6; kneedle gives 5 (linear) / 6 (log). But silhouette prefers k=2 (0.882) over k=6 (0.611); k=6 = [2137, 13, 4, 1815, 1, 81]; stored k=3 and k=5 inertia are not reproduced even with n_init=10 (ratios 1.0765, 0.9852), so the curve is partly a local-optimum artifact. |
| ✅ confirmed | Deck / markdown [48]: '36% of the information is lost reducing four dimensions to two' (PCA) | Arithmetic holds: cell [47] output array([0.386358, 0.25280254]) reproduced exactly in my run; sum 0.639161, so 36.08% of the VARIANCE (not 'information') is discarded. Caveat from my run: the discarded PC3 carries 24.83%, nearly equal to the kept PC2 (25.28%), and the features are nearly uncorrelated (only depth-SNR r = 0.543), so the 2-component cut is arbitrary. |
| ✅ confirmed | Deck: 'For the three most important features, most objects have: transit depth <20,000 ppm; transit signal-to-noise <2000; stellar radius <20 solar radii' | From my run, on the 4,051-row subset actually plotted (CANDIDATE+CONFIRMED only): depth < 20,000 ppm 98.84% (4004/4051); SNR < 2000 99.63% (4036/4051); stellar radius < 20 Rsun 99.85% (4045/4051); all three 98.47%. On all 9,201 KOIs with values: 86.93% / 96.27% / 99.51%; depth < 20,000 ppm holds for only 75.57% of FALSE POSITIVEs. 'Most' is true either way, but the 'three most important features' premise rests on 02-F3. |
| 🟡 partially | Deck: 'Confirmation that most of the data is consistent/homogeneous' | From my run: 98.7% of the clustered objects (3998/4051) fall in one k=4 cluster only because unscaled Euclidean distance is transit depth alone; after scaling, k-means splits the same core into two halves of 2137 and 1815 (k=6 on PCA), so 'homogeneous' is a property of the metric, not the data. The statement also covers only the planet-like 42% of the catalogue (all 5,023 FALSE POSITIVEs were removed before clustering, 02-F2). What is true: the non-FP objects form one dense core of shallow transits with 53 extreme-depth outliers. |
| 🟡 partially | Reviewer focus: the clustering used scaled data | By inspection of the code: the primary k-means (cells [34], [39]) and the 3D plot fit `cluster_bis_df` raw (my run: depth variance share 0.999146); only the PCA branch (cell [43] `StandardScaler().fit_transform(cluster_ter_df)`) is scaled, and my scaled first rows match the printed [[-0.0997984, -0.0849056, -0.77111141, -0.13246818], ...]. |
| ✅ confirmed | Reviewer focus: how feature importance was computed / whether leakage columns were included | Not computed in this notebook (cell [19] is markdown). Reproducing notebook 03's recipe on data/legacy/kepler_processed.pkl (8945 x 24; X includes the four *_FPF flags; Disposition_Score not in X) gives \|coef_[0]\| (CANDIDATE-class logit) excluding flags = Depth 1.394, SNR 0.941, Stellar_Radius 0.734, Impact 0.563 -- exactly the cell [19] order; the four flags have the largest magnitudes (-2.131 to -1.365), confirming leakage columns were in the model. |
| ❌ refuted | Reviewer focus: whether clusters relate to the disposition classes at all | From my run: ARI vs CANDIDATE/CONFIRMED = 0.0037 (k=4 unscaled) and 0.0006 (k=6 PCA); crosstabs show the same CANDIDATE:CONFIRMED mix in every cluster (e.g. 1753:2245 in the main k=4 cluster; 925:1212 and 823:992 in the two large k=6 clusters). With FALSE POSITIVEs included and features scaled (k=3, 9,201 rows): ARI -0.039; log-scaled k=3: ARI 0.0000. |
| ✅ confirmed | The notebook's stored outputs are reproducible in the 2026 environment | From my run: shapes (9564, 27), (9564, 15), (4051, 15); unscaled elbow ratios rerun/stored all 1.0000 (n_init=10); PCA ratios identical to 6 decimals; first five PCA rows identical; k=4 cluster sizes and depth ranges identical to the stored 3D figure; k=6 sizes identical up to label permutation. Requires patching cell [14]'s `.drop(name, 1)` and pinning n_init=10. |

## What the verifier added (missed by the reviewer)

> [!note] KOI_Probability mixes the project's two Ys: an archive-disposition (koi_disposition) indicator multiplied by koi_score, which tracks the Kepler pipeline verdict (koi_pdisposition) (low)
> CLAUDE.md 'Two Ys' guardrail distinguishes koi_pdisposition from koi_disposition; data/README.md quotes koi_score as 'A value between 0 and 1 that indicates the confidence in the KOI disposition.' In my run the score behaves as a Robovetter quantity, not an archive one: all 22 CONFIRMED planets with koi_score 0.0 have koi_pdisposition FALSE POSITIVE (cell [16] filter removes them), while 22 other CONFIRMED planets that survive have koi_pdisposition FALSE POSITIVE with koi_score 0.001-0.476 ('survivors with koi_pdisposition FP: 22 | their koi_disposition: {CONFIRMED: 22} | score range: 0.001 0.476'). So the derived column is neither an archive probability nor a pipeline probability; the reviewer's F2 recommendation ('do not filter through a derived product') is right but the reason should be stated as this conflation. Low because the column is only used as a filter.

> [!note] The 'nearly uncorrelated features' characterisation (F4) is a raw-scale artifact; on ranks or log scale depth-SNR and depth-stellar radius are clearly related, which matters for the rewrite advice to skip PCA (low)
> Extra check B, 4,051-row subset: Pearson depth-SNR 0.543 but Spearman 0.633; Spearman depth-srad -0.316 (physically expected: depth scales with (Rp/R*)^2); Pearson on log10(depth, srad, SNR) + impact: depth-SNR 0.726, depth-srad -0.211. PCA on the log-scaled, standardised features gives ratios [0.441, 0.261, 0.237, 0.061], so the PC2-vs-PC3 tie the reviewer identified survives a log transform and the conclusion holds; but the rewrite should say 'PCA after log transform still does not separate PC2 from PC3' rather than 'the features are uncorrelated'.

> [!note] The clustering inputs contain placeholder and unphysical values that the outlier clusters latch onto, and the notebook never screens for them (low)
> Extra check B on the 4,051 clustered rows: K00126.02 (CANDIDATE, koi_score 0.997, q1_q17_dr25_tce) has koi_depth 0.0 ppm and koi_model_snr 0.0 (the only such row); 100 objects (2.5%) have impact parameter > 1 (3 above 1.5, max 13.376 per verify_core feature summary); 6 objects have stellar radius > 20 Rsun and 3 above 100 Rsun (the k=6 cluster of 4 objects has median koi_srad 150.638). The reviewer mentions clipping b > 1 only in the rewrite recommendations; the depth-0 / SNR-0 candidate with score 0.997 is not mentioned anywhere and is a data-quality point worth a line in notes/Research Log/.


## Keep (what the rewrite should preserve)

- Physics-only feature set for clustering (no koi_fpflag_* columns, no koi_score as an input) -- this already matches the 2026 'physics-only' guardrail variant.
- Setting kepoi_name as the index and dropping the *_err columns explicitly, with a readable rename map; the shapes are printed after each step, which made auditing easy.
- Deterministic pipeline: every stored number (shapes, both elbow curves, PCA ratios, cluster sizes) reproduced exactly once n_init=10 was pinned -- keep the habit of fixed random_state, and add n_init.
- StandardScaler before PCA, and printing explained_variance_ratio_ rather than hiding it.
- Sweeping k=1..10 and plotting inertia, and inspecting clusters on named physical axes (the 3D depth/SNR/radius scatter with per-cluster symbols) rather than only in abstract PC space.
- Small, single-purpose cells with section headers; plotly figures that embed their data (this is what let the 2020 elbow values and cluster sizes be recovered for this review).

## Rewrite recommendations

- Declare the population in the first cell and justify it in notes/Decisions/: cluster all KOIs (recommended, so FALSE POSITIVE structure such as deep eclipsing-binary transits is visible) or planet-like only; never filter through a derived 'probability' column, and keep koi_score-null (non-DR25) rows unless a recorded reason says otherwise.
- Transform before any distance-based method: log10 of transit depth, SNR, stellar radius, period; clip or flag impact parameter > 1 (values up to 13.4 exist in the subset); then StandardScaler or RobustScaler. Print each feature's variance share as a guard against a repeat of 02-F1.
- Choose k with several criteria (silhouette, Calinski-Harabasz, Davies-Bouldin) plus stability across 5 or 7 seeds; pin `KMeans(n_init=10, random_state=...)` once at the top and reuse the same settings for the sweep and the final fit. Rich prefers 5 or 7 over 6 when the count is arbitrary; if k comes from a criterion, say so.
- Evaluate every clustering against koi_disposition (3 classes) and koi_pdisposition (2 classes) with crosstabs and ARI/NMI, plus per-cluster medians and koi_score distributions; write the null result (my ARI values were 0.004, 0.001, -0.039, 0.000) to notes/Research Log/ if it stands.
- Drop PCA-to-2D as a modelling step for four near-independent features; if a 2D picture is wanted, present it as visualization only with loadings on the axes and all component ratios reported, or use pair plots of the transformed features instead.
- Compute feature importance in the notebook with a stated model and target: permutation importance on a physics-only classifier (and the with-flags variant, per the guardrail), never a signed or single-class logistic coefficient; if a ranking from notebook 03 is reused, load it from a saved file and cite the model, target, and class.
- Replace the inert dendrogram cells with a real hierarchical run (scipy.cluster.hierarchy on a scaled subsample of a few hundred objects, fixed n_clusters, no input()) or delete them and their 'Research 1-4' headers.
- Modernize pandas/sklearn usage: `drop(columns=[...])`, `.copy()` after column selection or enable copy-on-write, `replace` with explicit dtype, keep kepoi_name as the index through PCA (`index=cluster_df.index`), and save cluster labels to data/processed/ as parquet.
- Charts: set a warm plotly template once (no blue), cast cluster labels to str/categorical for a discrete legend, save figures to reports/figures/clustering/, and use plain Markdown headers per CLAUDE.md.
- Fix the prose: describe the population and each filter next to the code, correct the copied comments (cells [12], [35], [53]), and restart-and-run-all before committing so execution counts and outputs are consistent.

## Finding details

### 02-F1 — k-means and the 'elbow at 4' run on unscaled features; transit depth carries 99.91% of the variance, so the clusters are transit-depth bins and no elbow exists at 4

> [!danger] high · methodology · cells [31, 33, 34, 36, 37, 39, 41]

**Evidence**

Cell [34]: `km = KMeans(n_clusters=i, random_state=0)` / `km.fit(cluster_bis_df)` on raw values (no scaler anywhere before cell [43]). Cell [39]: `model = KMeans(n_clusters=4, random_state=5)` / `model.fit(cluster_bis_df)`. Markdown [37]: "### => Elbow curve for 4 clusters". Stored elbow y-values quoted from the plotly JSON in cell [36]: [3.536e11, 1.299e11, 6.404e10, 3.508e10, 1.952e10, 1.349e10, 8.609e9, 5.368e9, 3.762e9, 2.803e9]. The 3D figure stored in cell [41] holds four traces with n = 3998 / 46 / 2 / 5 and x (depth) ranges 0-17219, 17859-71867, 253380-363130, 96134-157610 ppm.

**Reproduction**

cd /tmp/KeplerExoplanet && uv run python /tmp/review/scratch/02_clustering/repro_02_clustering.py  (key lines) -> `var = X.var(); (var/var.sum())` printed: Transit_Depth 0.999146, Stellar_Radius 0.0, Impact 0.0, SNR 0.000854. Inertia re-run with `KMeans(n_clusters=k, random_state=0, n_init=10)` -> rerun/stored ratios [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9999]. Successive ratios I(k)/I(k-1) of the stored curve: [0.367, 0.493, 0.548, 0.557, 0.691, 0.638, 0.623, 0.701, 0.745] (no kink at 4; the first slow-down is after k=5). Kneedle (max distance from chord) on the stored curve -> k=3 linear, k=5 on log(inertia). `silhouette_score` k=2..6: 0.989, 0.972, 0.954, 0.922, 0.922 with sizes [4046,5], [4023,26,2], [3998,2,46,5], [3903,2,21,5,120], ... `KMeans(n_clusters=4, random_state=5, n_init=10)` -> sizes [3998, 2, 46, 5]; per-cluster depth min/max: 0-17219, 253380-363130, 17859-71867, 96134-157610 (identical to the stored 2020 figure).

**Impact**

The headline k-means result in the deck ('elbow at 4', the 4-cluster 3D plot) describes the units of one column, not structure in four features. Three of the four 'clusters' are 53 extreme-depth outliers; 98.7% of objects sit in one cluster. Any interpretation built on it (including 'the data is homogeneous') is an artifact of not scaling.

**Recommendation**

Log-transform the heavy-tailed columns (depth, SNR, stellar radius), clip or flag impact parameter > 1, then StandardScaler/RobustScaler before any distance-based method; print each feature's share of variance as a sanity check; pick k with silhouette / Calinski-Harabasz / Davies-Bouldin plus seed stability rather than a visual elbow alone, and report the cluster sizes next to the chosen k.

**Verifier: ✅ confirmed**

*Corrected statement:* k-means in cells [34] and [39] runs on the four raw columns (no scaler before cell [43]); transit depth carries 99.91% of the unscaled variance, so the k=4 solution is four disjoint transit-depth intervals (0-17,219 / 17,859-71,867 / 96,134-157,610 / 253,380-363,130 ppm) holding 3,998 / 46 / 5 / 2 objects, i.e. 98.69% in one cluster and 53 extreme-depth outliers in the other three. The 'elbow at 4' is not singled out by the curve: the bend is spread over k=2..5 (slope-angle change 20.7, 22.8, 14.9, 13.0 degrees at k=2,3,4,5, then under 2.5 degrees), kneedle picks 3 (linear) or 5 (log), and silhouette is highest at k=2 (0.989) and non-increasing after. 'No elbow exists at 4' should read 'k=4 is one of several equally arbitrary visual readings'; the substantive point (clusters are depth bins, not structure in four features) stands.

*Verifier evidence:* verify_core.py (my run): unscaled variance share {'koi_depth': 0.999146, 'koi_srad': 0.0, 'koi_impact': 0.0, 'koi_model_snr': 0.000854}; elbow rerun/stored ratios with n_init=10 all 1.0 (0.9999 at k=10); stored successive ratios [0.367, 0.493, 0.548, 0.557, 0.691, 0.638, 0.623, 0.701, 0.745]; kneedle linear 3 / log 5; silhouette k=2..6 = 0.989, 0.972, 0.954, 0.922, 0.922; KMeans(4, random_state=5, n_init=10) depth min/max per cluster 0-17219 (3998), 253380-363130 (2), 17859-71867 (46), 96134-157610 (5), 'depth intervals disjoint & ordered: True', share in largest cluster 98.69%. Stored 3D figure in cell [41] (JSON inspection) has traces n=3998/46/2/5 with the same x ranges. Cell [34]/[39] code quoted in the view: `km = KMeans(n_clusters=i, random_state=0)` / `km.fit(cluster_bis_df)` and `model = KMeans(n_clusters=4, random_state=5)` on the raw frame.

### 02-F2 — The clustering population silently drops every FALSE POSITIVE (5,023 rows) and 22 CONFIRMED planets via a derived 'KOI_Probability' filter; the code comment describes a different design

> [!danger] high · methodology · cells [12, 13, 14, 16, 17]

**Evidence**

Cell [12] comment: "Build a indicator for y axis for kepler interest probability: koi_pdisposition -> 1 if candidate and -1 if false positive." Cell [13] code uses the other column and 0, not -1: `cluster_df["Exoplanet_Archive_Disposition"].replace(["CANDIDATE","CONFIRMED"],1)` / `.replace(["FALSE POSITIVE"],0)`. Cell [14]: `cluster_df["KOI_Probability"] = cluster_df["Exoplanet_Archive_Disposition"] * cluster_df["Disposition_Score"]`. Cell [16]: `cluster_df = cluster_df.dropna()` then `cluster_df=cluster_df[(cluster_df["KOI_Probability"] != 0) & ...]`. Cell [17] output: (4051, 15). Markdown [10] notes many null Disposition_Score values but nothing says FALSE POSITIVEs are being removed. KOI_Probability is never used again in executed code (only in the inert raw cells).

**Reproduction**

Same script; printed: `rows 9564 -> dropna 7994 (dropped 1570: {'FALSE POSITIVE': 1102, 'CANDIDATE': 456, 'CONFIRMED': 12}) -> KOI_Probability!=0 4051 (dropped 3943: {'FALSE POSITIVE': 3921, 'CONFIRMED': 22})`; `final subset by archive disposition: {'CONFIRMED': 2259, 'CANDIDATE': 1792}`; `KOI_Probability == koi_score for survivors: True`. Of the 1,570 dropna rows, 1,510 have null koi_score (step1_pipeline.txt: raw koi_score nulls 1510). The 22 confirmed planets removed all have koi_score == 0.0 and koi_pdisposition FALSE POSITIVE in the q1_q17_dr25_tce delivery; a direct look-up printed Kepler-10 b (K00072.01), Kepler-9 b (K00377.01), Kepler-42 c (K00961.02), Kepler-90 h (K00351.01) with koi_score 0.0.

**Impact**

Everything downstream ('most of the data is homogeneous', the threshold statements, both cluster solutions) refers to the planet-like half of the catalogue only. The clusters can never be compared with the FALSE POSITIVE class, which is exactly where the deep-transit structure lives (from my run: depth < 20,000 ppm holds for 99.52% of CONFIRMED but only 75.57% of FALSE POSITIVE). Genuine confirmed planets such as Kepler-10 b were discarded by a 'probability' that was never used by the analysis, and the filter is undocumented.

**Recommendation**

State the population explicitly at the top (all KOIs, or planet-like only, and why). Do not filter through a derived product; keep koi_score-null rows (they are the non-DR25 deliveries) unless a reason is recorded in notes/Decisions/. If the goal is label-free structure, cluster all rows and compare to koi_disposition afterwards (see 02-F5).

**Verifier: ✅ confirmed**

*Corrected statement:* Cells [13]-[16] build KOI_Probability = (1 if koi_disposition in {CANDIDATE, CONFIRMED} else 0) x koi_score, then dropna() (removes 1,570 rows: 1,102 FP, 456 CANDIDATE, 12 CONFIRMED; 1,510 of them because koi_score is null, which are the 796 q1_q16, 368 dr24 and 346 no-delivery rows) and `!= 0` (removes 3,943 rows: all 3,921 remaining FALSE POSITIVEs and 22 CONFIRMED planets with koi_score 0.0, all koi_pdisposition FALSE POSITIVE in q1_q17_dr25_tce, including Kepler-10 b, Kepler-9 b, Kepler-42 c, Kepler-90 h). 4,051 rows survive (2,259 CONFIRMED + 1,792 CANDIDATE, 0 FP). Nuance: even the commented '-1' design in cell [12] would have removed the 3,460 FALSE POSITIVEs whose koi_score is 0 and kept only the 516 with koi_score > 0, so the loss of the FP class comes from filtering on koi_score itself, not only from coding FP as 0 instead of -1. The comment in cell [16] ('Keep rows with non null koi probability') does not say the FP class is being removed.

*Verifier evidence:* verify_core.py: 'rows 9564 -> dropna 7994 -> !=0 4051'; 'dropna removed by koi_disposition: {FALSE POSITIVE: 1102, CANDIDATE: 456, CONFIRMED: 12}', 'of which koi_score null: 1510'; '!=0 filter removed: {FALSE POSITIVE: 3921, CONFIRMED: 22}'; 'survivors: {CONFIRMED: 2259, CANDIDATE: 1792}'; 'CONFIRMED removed by !=0: 22 | koi_score values: [0.0] | koi_pdisposition: {FALSE POSITIVE: 22} | delivery: {q1_q17_dr25_tce: 22}'; K00072.01 Kepler-10 b, K00377.01 Kepler-9 b, K00961.02 Kepler-42 c, K00351.01 Kepler-90 h all listed with score 0.0; 'KOI_Probability == koi_score for survivors: True'. Extra check B: FALSE POSITIVE rows 5023 | koi_score null 1047 | ==0 3460 | >0 516; koi_score-null rows by delivery {q1_q16_tce: 796, q1_q17_dr24_tce: 368, nan: 346}.

### 02-F3 — The 'most important non-flag features' list is asserted without code; it comes from notebook 03's logistic-regression coefficient for the CANDIDATE class, trained with the four koi_fpflag_* leakage columns in X

> [!warning] medium · leakage · cells [18, 19]

**Evidence**

Cells [18]-[19] (markdown only): "'Non-flag' features with the most importance / 1. Transit_Depth_[ppm] 2. Transit_Signal-to-Noise 3. Stellar_Radius_[Solar_radii] 4. Impact_Parameter". Notebook 03 view cell [16]: `x = sorted(zip(classifier.coef_[0], X.columns), reverse=True)` with stored output "1.4194 Transit_Depth_[ppm] / 0.7182 Stellar_Radius_[Solar_radii] / 0.5531 Impact_Parameter / 0.3203 Orbital_Period_[days] / 0.2749 Equilibrium_Temperature_[K] ...". That model is `LogisticRegression(solver='lbfgs', max_iter=200, random_state=1)` on the 3-class Exoplanet_Archive_Disposition.

**Reproduction**

Same script: `kp = pd.read_pickle('data/legacy/kepler_processed.pkl')` -> X columns include ['Not_Transit-Like_FPF','Stellar_Eclipse_FPF','Centroid_Offset_FPF','Ephemeris_Match_Indicates_Contamination_FPF']; Disposition_Score in X: False. Refit with 03's recipe (train_test_split random_state=1, stratify=y; StandardScaler fit on train; LR lbfgs max_iter=200) -> coef_[0] signed top 5: Depth +1.394, Stellar_Radius +0.734, Impact +0.563, Period +0.316, Teq +0.272; bottom 5: SNR -0.941, Stellar_Eclipse_FPF -1.365, Ephemeris_FPF -1.528, Not_Transit_FPF -2.025, Centroid_FPF -2.131. Ranking by |coef_[0]| with the flags excluded: Depth 1.394, SNR 0.941, Stellar_Radius 0.734, Impact 0.563 -- exactly the order in cell [19]. (Stored 2020 values 1.419/0.718/0.553 vs my 1.394/0.734/0.563: sklearn-version drift, same order.)

**Impact**

'Importance' here is the magnitude of a standardized coefficient for one logit (CANDIDATE vs {CONFIRMED, FALSE POSITIVE}) in a model where the leakage flags have the largest coefficients (which is why the team had to say 'non-flag'). It is not a measure of relevance to 'is this a planet', it is distorted by heavy-tailed features under StandardScaler, the provenance is undocumented in this notebook, and the deck's 'three most important features' rests on it.

**Recommendation**

Compute importance inside the notebook with a named model and target (e.g. permutation importance on a physics-only classifier, plus the with-flags variant as the guardrail requires), or load a saved ranking from notebook 03 explicitly and say which model, which class, and that flags were present. Never rank by signed coefficient.

**Verifier: ✅ confirmed**

*Corrected statement:* Cells [18]-[19] are markdown only; no importance is computed in this notebook. The stored 2020 output of notebook 03 cell [16] (`sorted(zip(classifier.coef_[0], X.columns), reverse=True)`, LogisticRegression lbfgs on the 3-class archive disposition with the four *_FPF flags in X) ranks by the signed CANDIDATE-class coefficient (class 0 = CANDIDATE; I verified the encoding 0/1/2 = CANDIDATE/CONFIRMED/FALSE POSITIVE against the raw table). Taking |coef_[0]| and excluding the flags gives, from the 2020 stored values themselves, Depth 1.4194, SNR 0.9505, Stellar_Radius 0.7182, Impact 0.5531 -- exactly the cell [19] order; my 2026 refit gives 1.394 / 0.941 / 0.734 / 0.563, same order. The flags have the largest magnitudes (2020: -2.005 to -1.363). Provenance is inferred from this exact match (no code links the two notebooks), but the match holds on the stored 2020 numbers, not just on a refit.

*Verifier evidence:* JSON dump of notebooks/03_sklearn_models.ipynb cell [16] stored output (full, not the truncated view): rows 0-2 Depth 1.4194370887669014, Stellar_Radius 0.7182450900781062, Impact 0.5530591539637524; row 18 Transit_Signal-to-Noise -0.9504916661153751; rows 19-22 Stellar_Eclipse_FPF -1.3632, Ephemeris_FPF -1.4429, Not_Transit-Like_FPF -1.9870, Centroid_Offset_FPF -2.0054. Extra check A: crosstab of kepler_processed.pkl target vs raw koi_disposition = {0: CANDIDATE 2136, 1: CONFIRMED 2285, 2: FALSE POSITIVE 4524}; X_train shape (6708, 23) matches 03's printed value; refit coef_[0] SNR -0.941; refit |coef_[0]| non-flag order Depth 1.394, SNR 0.941, Stellar_Radius 0.734, Impact 0.563, Period 0.316. A physics-only LR (flags dropped) reorders the list (class-0 |coef|: Depth 1.197, SNR 1.040, Stellar_Radius 1.018, Planetary_Radius 0.588, Impact 0.289), which supports the reviewer's point that the ranking depends on the flags being present.

### 02-F4 — PCA to two components discards a third component (24.8%) almost as large as the second (25.3%); the four features are nearly uncorrelated, so '36% lost' reflects PCA being the wrong tool, not a finding

> [!warning] medium · claim-vs-data · cells [43, 44, 45, 46, 47, 48]

**Evidence**

Cell [44]: `pca = PCA(n_components=2)`. Cell [47] output: `array([0.386358  , 0.25280254])`. Markdown [48]: "36% of the information is lost when the four-dimension data were reduced to a two one".

**Reproduction**

Same script: `PCA().fit(StandardScaler().fit_transform(X)).explained_variance_ratio_` -> [0.386358, 0.252803, 0.248257, 0.112582]; first two sum 0.639161 (1 - 0.639161 = 0.3608). Correlation matrix of the scaled features: depth-SNR 0.543; every other |r| <= 0.07. Loadings (step3_k4_and_pca.txt): PC1 = 0.708 depth + 0.703 SNR; PC2 = 0.620 stellar radius + 0.779 impact; PC3 = 0.784 stellar radius - 0.613 impact.

**Impact**

The 2D map is essentially (depth+SNR) versus (impact+radius) with a quarter of the variance thrown away by an arbitrary cut between two near-equal components. The k=6 clusters and 'elbow at 6' inherit this. Calling variance 'information' overstates what PCA measures.

**Recommendation**

For four near-independent features skip PCA as a modelling step; if a 2D picture is wanted, present it as a visualization only, label axes with loadings, and report all component ratios. Pair plots of the log-transformed features would show more.

**Verifier: ✅ confirmed**

*Corrected statement:* PCA(2) on the StandardScaled four features keeps [0.386358, 0.252803] and discards PC3 = 0.248257 and PC4 = 0.112582; 36.08% of the variance (not 'information') is dropped, and PC3 is within 0.5 percentage points of PC2, so the cut at two components is arbitrary. Loadings: PC1 = 0.708 depth + 0.703 SNR; PC2 = 0.620 stellar radius + 0.779 impact; PC3 = 0.784 stellar radius - 0.613 impact. Caveat on 'nearly uncorrelated': that is true for Pearson on the raw scale that the notebook uses (only depth-SNR r = 0.543, all other |r| <= 0.07), but on ranks depth-SNR is 0.633 and depth-stellar radius is -0.316, and on log10 features depth-SNR Pearson is 0.726; PCA on log-scaled features gives [0.441, 0.261, 0.237, 0.061], so the PC2-vs-PC3 tie persists even after a sensible transform and the recommendation stands.

*Verifier evidence:* verify_core.py: 'explained_variance_ratio_ all 4: [0.386358, 0.252803, 0.248257, 0.112582] | first two sum: 0.639161 | lost: 0.3608'; pca2 ratio [0.386358, 0.25280254] identical to cell [47]'s stored array; first five PCA rows identical to cell [46]; correlation matrix and loadings as quoted. Extra check B: Pearson depth-SNR 0.543 | Spearman 0.633; Spearman depth-srad -0.316; Pearson on log10(depth, srad, snr) + impact: depth-SNR 0.726, depth-srad -0.211; PCA on log-scaled features variance ratios [0.441, 0.261, 0.237, 0.061].

### 02-F5 — Clusters are never evaluated against anything; they carry no disposition signal (ARI 0.0037 for k=4, 0.0006 for k=6)

> [!warning] medium · methodology · cells [39, 41, 52, 53]

**Evidence**

Cells [39]-[41] and [52]-[53] add `class` labels and plot them; there is no crosstab, ARI, per-cluster summary, or comparison with koi_disposition / koi_pdisposition / koi_score anywhere. README research question: "Does EDA reveal interesting groupings?"

**Reproduction**

Same script: crosstab k=4 (unscaled) vs disposition -> cluster0 CANDIDATE 1753 / CONFIRMED 2245; cluster1 2/0; cluster2 32/14; cluster3 5/0; `adjusted_rand_score` = 0.0037; mean koi_score per cluster {0: 0.942, 1: 0.608, 2: 0.81, 3: 0.617}. k=6 on PCA: crosstab 925/1212, 9/4, 4/0, 823/992, 1/0, 30/51; ARI = 0.0006. Extra check (step4_claims_and_importance.txt), scaled k-means on all 9,201 KOIs with values, FALSE POSITIVEs included: k=3 sizes [8599, 15, 587], ARI -0.039; log-scaled k=3 sizes [4535, 3099, 1567], ARI 0.0000 against the 3-class disposition.

**Impact**

The notebook cannot answer its own research question, and the deck presents the clusters as if they were meaningful. Even the more careful variants I ran find no relationship between these four features' clusters and the archive dispositions -- a legitimate and reportable null result the 2020 work never stated.

**Recommendation**

Always report crosstab plus ARI/NMI against koi_disposition and koi_pdisposition, per-cluster medians of the input features, and the koi_score distribution; write the null result into notes/Research Log/ if it stands.

**Verifier: ✅ confirmed**

*Corrected statement:* No cell compares the clusters with any label. Re-running the notebook's two solutions: k=4 unscaled crosstab (CANDIDATE, CONFIRMED) = (1753, 2245), (2, 0), (32, 14), (5, 0), ARI 0.0037, NMI 0.0077 (ARI vs koi_pdisposition 0.0188); k=6 on PCA crosstab (925, 1212), (9, 4), (4, 0), (823, 992), (1, 0), (30, 51), ARI 0.0006, NMI 0.0025. Every cluster has the same roughly 45:55 CANDIDATE:CONFIRMED mix as the whole subset; the clusters carry no disposition signal within the planet-like population. (The reviewer's extra all-KOI variants -- ARI -0.039 scaled, 0.0000 log-scaled -- are in their step4 file; I did not re-run those.)

*Verifier evidence:* verify_core.py: crosstab k=4 and 'ARI k=4 vs koi_disposition: 0.0037 | NMI: 0.0077', 'ARI k=4 vs koi_pdisposition: 0.0188'; crosstab k=6 and 'ARI k=6 vs koi_disposition: 0.0006 | NMI: 0.0025'; mean koi_score per k=4 cluster {0: 0.942, 1: 0.608, 2: 0.81, 3: 0.617}. View cells [39]-[41], [52]-[53] contain only label assignment and plotting; no crosstab/ARI code anywhere in the view.

### 02-F6 — 'Elbow at 6' on the PCA branch is the more defensible elbow but still weak: silhouette prefers k=2, k=6 is two large halves plus four outlier groups, and the stored curve is not fully reproducible

> [!warning] medium · claim-vs-data · cells [49, 50, 51, 52]

**Evidence**

Cell [49]: `km = KMeans(n_clusters=i, random_state=0)` / `km.fit(cluster_ter_pca_df)`. Markdown [51]: "### => Elbow curve for 6 clusters". Cell [52]: `model = KMeans(n_clusters=6, random_state=5)`. Stored elbow y-values quoted from the plotly JSON in cell [50]: [10357.0, 6938.2, 4926.8, 3395.5, 2009.9, 1227.8, 1019.9, 825.2, 699.8, 613.5]. The scatter stored in cell [53] holds class counts {0: 2137, 1: 13, 2: 1815, 3: 81, 4: 1, 5: 4}.

**Reproduction**

Same script: re-run with n_init=10 -> rerun/stored ratios [1.0, 1.0, 1.0765, 1.0, 0.9852, 1.0, 1.0, 0.9999, 1.0002, 1.0013] (k=3 and k=5 land on different local optima). Successive ratios of the stored curve: [0.67, 0.71, 0.689, 0.592, 0.611, 0.831, 0.809, 0.848, 0.877] -- the clearest slow-down is after k=6. Kneedle: 5 (linear), 6 (log). Silhouette on the 2D PCA data k=2..7: 0.882, 0.563, 0.573, 0.599, 0.611, 0.510 with k=2 sizes [4001, 50]. `KMeans(n_clusters=6, random_state=5, n_init=10)` -> sizes [2137, 13, 4, 1815, 1, 81] (same partition as 2020 up to label numbering; my first five labels 0,3,3,3,3 vs notebook 0,2,2,2,2).

**Impact**

Six is a plausible reading of that particular curve, but the curve depends on local optima, the 'clusters' are the 3,952-object core split in two along PC2 (impact/radius) plus 99 outliers, and nothing in the split tracks disposition. Presenting it as a discovered structure overreaches.

**Recommendation**

Same as 02-F1; also use the same random_state (and n_init) for the sweep and the final fit so the plotted partition is the one the elbow was computed on.

**Verifier: ✅ confirmed**

*Corrected statement:* On the stored PCA elbow curve the sharpest bends are at k=5 and k=6 (slope-angle change 16.2 and 25.0 degrees, versus under 11 degrees elsewhere; successive ratios 0.67, 0.71, 0.689, 0.592, 0.611, 0.831, ...; kneedle 5 linear / 6 log), so 'elbow at 6' is a defensible visual reading. But silhouette prefers k=2 (0.882 vs 0.611 at k=6); the k=6 partition is a 3,952-object core split into 2,137 and 1,815 plus four outlier groups of 13, 4, 1 and 81; and the split of the core is essentially by impact parameter (median b = 0.129 vs 0.795, median stellar radius 0.954 vs 1.002 Rsun), so 'along PC2 (impact/radius)' should read 'by impact parameter'. Reproducibility: with n_init=10 and random_state=0 the stored k=3 and k=5 inertias are not recovered (ratios 1.0765 and 0.9852) because sklearn 1.9's initialisation stream differs from 2020's; the stored values are reachable with other seeds (k=3: seed 5 gives 4926.80; k=5: seeds 2,3,4,6 give 2009.87), confirming they are local optima. The final k=6 partition itself reproduces exactly (ARI 1.0 against the labels stored in the cell [53] figure).

*Verifier evidence:* verify_core.py: 'PCA elbow n_init=10 rerun/stored: [1.0, 1.0, 1.0765, 1.0, 0.9852, 1.0, 1.0, 0.9999, 1.0002, 1.0013]'; 'PCA k=3 inertia by seed: {0: 5303.52, 1: 5303.52, 2: 4934.08, ..., 5: 4926.8} stored=4926.80'; 'PCA k=5 inertia by seed: {0: 1980.09, ..., 2: 2009.87, 3: 2009.87, 4: 2009.87, 5: 1980.1, 6: 2009.87} stored=2009.87'; 'PCA: slope angle change at k=2..9 (deg): {2: 10.7, 3: 7.0, 4: 2.7, 5: 16.2, 6: 25.0, 7: 0.7, 8: 3.6, 9: 2.1}'; kneedle linear 5 / log 6; silhouette k=2..7 = 0.882, 0.563, 0.573, 0.599, 0.611, 0.510; 'k=6 PCA (rs=5, n_init=10) sizes: [2137, 13, 4, 1815, 1, 81]'; 'ARI(rerun k=6, stored figure k=6 labels): 1.0'; per-cluster medians koi_impact 0.129 (cluster 0, n=2137) vs 0.795 (cluster 3, n=1815), koi_srad 0.954 vs 1.002. Stored figure JSON of cell [53]: class counts {0: 2137, 1: 13, 2: 1815, 3: 81, 4: 1, 5: 4}, first five classes [0, 2, 2, 2, 2].

### 02-F7 — Notebook halts under pandas 2.x and its elbow numbers depend on an old scikit-learn default (n_init=10)

> [!warning] medium · reproducibility · cells [13, 14, 31, 34, 39, 49]

**Evidence**

Cell [14]: `cluster_df = cluster_df.drop("Exoplanet_Archive_Disposition",1)` (positional axis). Cell [13]: `.replace(["CANDIDATE","CONFIRMED"],1)`. Cell [31]: `cluster_bis_df=cluster_df[[...]]` then cell [39]: `cluster_bis_df["class"] = model.labels_`. Cells [34], [49]: `KMeans(n_clusters=i, random_state=0)` with no n_init. Kernel metadata: Python 3.7.6, kernel 'PythonData'.

**Reproduction**

Same script under pandas 2.3.3 / sklearn 1.9.0: `cdf.drop('Exoplanet_Archive_Disposition', 1)` -> `TypeError: DataFrame.drop() takes from 1 to 2 positional arguments but 3 were given`. step1_pipeline.txt: the replace call emits `FutureWarning: Downcasting behavior in replace is deprecated`; the [31]+[39] pattern emits `SettingWithCopyWarning`. Elbow with today's default `n_init='auto'`: unscaled rerun/stored ratios [1.0, 1.0099, 1.0, 1.1517, 1.1492, 1.0617, 1.0, 1.0957, 1.0, 1.0013] (k=4 inertia 4.040e10 vs stored 3.508e10); with n_init=10 all ratios 1.0000.

**Impact**

A naive re-run stops at cell [14]; after patching that line, the elbow curves come out different (up to 15% at k=4) and could change the chosen k, so the 2020 figures cannot be regenerated without knowing to pin n_init=10.

**Recommendation**

Use `drop(columns=[...])`, `.copy()` after column selection (or enable copy-on-write), pass `n_init=10` and `random_state` explicitly, and rely on uv.lock for versions; add a restart-and-run-all check before committing.

**Verifier: ✅ confirmed**

*Corrected statement:* Under pandas 2.3.3 the literal cell [14] call `cluster_df.drop("Exoplanet_Archive_Disposition",1)` raises TypeError ('DataFrame.drop() takes from 1 to 2 positional arguments but 3 were given'), so a top-to-bottom run halts there; cell [13]'s `.replace([...], 1)` emits a FutureWarning about downcasting; the cell [31]+[39] pattern emits SettingWithCopyWarning. With scikit-learn 1.9's default n_init='auto' the unscaled elbow differs from the stored curve by up to 15% (k=4: 4.040e10 vs stored 3.508e10; ratios [1.0, 1.0099, 1.0, 1.1517, 1.1492, 1.0617, 1.0, 1.0957, 1.0, 1.0013]) and the PCA curve by up to 14.6%; pinning n_init=10 reproduces the stored unscaled curve exactly.

*Verifier evidence:* verify_core.py: 'cell [14] .drop(name, 1) -> TypeError : DataFrame.drop() takes from 1 to 2 positional arguments but 3 were given'; 'unscaled elbow n_init=auto rerun/stored: [1.0, 1.0099, 1.0, 1.1517, 1.1492, 1.0617, 1.0, 1.0957, 1.0, 1.0013]' and n_init=10 all 1.0; 'PCA elbow n_init=auto rerun/stored: [1.0, 1.0028, 1.0765, 1.0, 1.067, 1.0963, 1.146, 1.0243, 1.0799, 1.1246]'. Extra check C (my run with warnings recorded): 'cell [13] replace warnings: FutureWarning: Downcasting behavior in `replace` is deprecated...'; 'cell [31]+[39] warnings: SettingWithCopyWarning'. Kernel metadata from the .ipynb: kernelspec 'PythonData', language_info version 3.7.6.

### 02-F8 — Dead code: inert dendrogram cells reference undefined names and an interactive input(); unused import and variables

> [!note] low · dead-code · cells [1, 12, 16, 21, 23, 25, 27, 29, 52]

**Evidence**

Cell [1]: `#import plotly.figure_factory as ff` (commented out) and `from sklearn.cluster import AgglomerativeClustering` (only used in raw cells). Raw cell [21]: `fig = ff.create_dendrogram(df, color_threshold=0)`, `param=input('Enter the number of clusters:')`, `return df.hvplot.scatter(...)` -- hvplot is never imported. Raw cells [23]-[29] call `plot_clusters(...)` under headings 'Research 1'-'Research 4'. Cell [52]: `predictions = model.predict(cluster_ter_pca_df)` never used (labels_ used instead). Cell [16]: `& (cluster_df["KOI_Probability"].notnull())` is redundant after `dropna()`. Cell [12] keeps `Kep_ID`, which nothing uses.

**Reproduction**

not run -- raw cells never execute; `ff` and `hvplot` are absent from the executed namespace by inspection of cell [1].

**Impact**

The 'Research 1-4' sections promise a dendrogram analysis that never ran and could not run as written; readers may believe hierarchical clustering was done.

**Recommendation**

Delete the raw cells, or implement them properly (scipy.cluster.hierarchy on a scaled subsample, no input() prompts, fixed n_clusters) and drop the unused import/variables.

**Verifier: ✅ confirmed**

*Corrected statement:* Raw cells [21], [23], [25], [27], [29] never executed and could not run as written: `ff` is only present as the commented-out `#import plotly.figure_factory as ff` in cell [1], hvplot is never imported, and `input()` would block a batch run. `AgglomerativeClustering` (cell [1]) is used only in raw cell [21]. `predictions` (cell [52]) is assigned and never read; `Kep_ID` appears only in cells [8] and [12]; the `.notnull()` term in cell [16] is redundant after `dropna()`. The notebook writes nothing to disk (no to_pickle / pickle.dump / savefig / write_html / to_csv in any cell).

*Verifier evidence:* JSON inspection of the .ipynb: raw cells [21, 23, 25, 27, 29]; cell [1] source has hvplot: False, '#import plotly.figure_factory as ff' present; 'Kep_ID' referenced in cells [8, 12] only; 'predictions' referenced in cell [52] only; no cell contains to_pickle, pickle.dump, savefig, write_html or to_csv. Code quoted from the view: cell [21] `fig = ff.create_dendrogram(df, color_threshold=0)`, `param=input('Enter the number of clusters:')`, `return df.hvplot.scatter(`; cell [52] `predictions = model.predict(cluster_ter_pca_df)` followed by `cluster_ter_pca_df["class"] = model.labels_`.

### 02-F9 — Comments and headers contradict the code, and stored outputs are not from a clean top-to-bottom run

> [!note] low · documentation · cells [12, 35, 39, 41, 53]

**Evidence**

Cell [12] comment says koi_pdisposition and -1; code uses Exoplanet_Archive_Disposition and 0 (see 02-F2). Cell [35] comment: "Define a DataFrame to plot the Elbow Curve using hvPlot" -- plotly is used. Cell [53] comment: "Plot Kepler field of view. Colors denote disposition" on a k-means/PCA scatter (copied from notebook 01). Cell [39] ends with `cluster_bis_df.head()` but its stored output is `KMeans(n_clusters=4, random_state=5)`. Execution counts run 19 at cell [39] then 24 at cell [41] (counts 20-23 belong to cells that no longer exist). HTML `<span style="color:...">` headers throughout, contrary to CLAUDE.md.

**Reproduction**

JSON inspection (uv run python: json.load of the .ipynb, printing execution_count per code cell) printed `[39] exec=19 ... [41] exec=24 ... [43] exec=25`; all numeric outputs nevertheless reproduce (see other findings).

**Impact**

Readers cannot trust the prose; the saved state shows the notebook was edited after execution. Low because every number was independently reproduced.

**Recommendation**

Fix the comments, use plain Markdown headers, and restart-and-run-all before committing.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell [12]'s comment describes koi_pdisposition and -1 while the code uses Exoplanet_Archive_Disposition and 0; cell [35]'s comment says hvPlot while plotly is used; cell [53]'s comment 'Plot Kepler field of view. Colors denote disposition' is copied from notebook 01 (its view line 884 has the identical comment). Cell [39] ends with `cluster_bis_df.head()` but its only stored output is the repr `KMeans(n_clusters=4, random_state=5)`, so the cell was edited after execution. Execution counts jump from 19 (cell [39]) to 24 (cell [41]); counts 20-23 belong to cells no longer in the file. HTML span headers throughout.

*Verifier evidence:* JSON dump: exec counts [(39, 19), (41, 24), (43, 25), ...]; cell [39] last source line 'cluster_bis_df.head()', outputs ['KMeans(n_clusters=4, random_state=5)']. grep of /tmp/review/views/01_cleaning_eda.md line 884: '# Plot Kepler field of view. Colors denote disposition'. View cells [12], [35], [53] quoted comments; headers like `# <span style="color:slateblue"><b>` in cells [0], [2], [5], [11], [18], [20], [30], [38], [40], [42].

### 02-F10 — The PCA dataframe throws away the kepoi_name index, so cluster labels cannot be traced back to objects

> [!note] low · other · cells [6, 46, 52]

**Evidence**

Cell [6] comment: "the 'kepoi_name' is the unique identified for each object of interest ... We make this the index to preserve the relationship through the processing". Cell [46]: `cluster_ter_pca_df=pd.DataFrame(data=cluster_ter_pca, columns=["Principal_component_1","Principal_component_2"])` (no index argument). Cell [52] output shows a 0..4050 RangeIndex.

**Reproduction**

Same script: `type(P.index).__name__` -> RangeIndex.

**Impact**

The k=6 labels can only be matched positionally; nothing is saved anyway, so the analysis leaves no reusable product.

**Recommendation**

Pass `index=cluster_ter_df.index`, and write labels to data/processed/ as parquet keyed by kepoi_name.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell [46] builds `pd.DataFrame(data=cluster_ter_pca, columns=[...])` without an index argument, so the PCA frame (and the k=6 labels attached in cell [52]) carries a 0..4050 RangeIndex and can only be matched to kepoi_name positionally; nothing is saved, so no reusable product exists either way.

*Verifier evidence:* verify_core.py: 'PCA df index type: RangeIndex'; cell [52] stored output shows integer index 0..4048 in the view. Cell [6] comment quoted in the view: 'We make this the index to preserve the relationship through the processing'.

### 02-F11 — Plots use plotly's default blue and treat the integer cluster id as a continuous colour axis

> [!note] low · other · cells [36, 41, 50, 53]

**Evidence**

Stored figure JSON: elbow traces in cells [36] and [50] have `line.color = '#636efa'` (template colorway default); cells [41] and [53] carry `layout.coloraxis` with the Plasma scale `#0d0887` -> `#f0f921` and a colorbar titled 'class' because `color="class"` is an int column; cell [41] shows discrete groups only because `symbol="class"` was also set.

**Reproduction**

uv run python: json.load of the .ipynb, printing each trace's line.color / layout.coloraxis; output as quoted.

**Impact**

Cosmetic; conflicts with the project palette rule (no blue except natural subjects) and a continuous colorbar for six discrete clusters is misleading.

**Recommendation**

Cast labels to str (or pd.Categorical) for a discrete legend and set a warm palette once per notebook via a plotly template.

**Verifier: ✅ confirmed**

*Corrected statement:* Both elbow traces (cells [36], [50]) are drawn with the plotly_dark template's first colorway entry '#636efa' (blue-indigo). Cells [41] and [53] set `color="class"` on an integer column, so plotly attaches a continuous coloraxis (Plasma scale '#0d0887' -> '#f0f921') with a colorbar titled 'class'; the 3D plot distinguishes clusters only because `symbol="class"` gives circle/diamond/square/x, and its legend is hidden (`showlegend=False`).

*Verifier evidence:* JSON inspection: cell [36] and [50] trace line.color '#636efa', template colorway[0] '#636efa'; cell [41] four scatter3d traces with symbols circle/diamond/square/x, marker.coloraxis 'coloraxis', layout.coloraxis colorscale starting [0, '#0d0887'] and colorbar title 'class', showlegend False; cell [53] one scattergl trace with marker.color array of 0-5 and the same coloraxis.

### 02-F12 — Different random_state for the elbow sweeps (0) and the final models (5)

> [!note] low · methodology · cells [34, 39, 49, 52]

**Evidence**

Cell [34]/[49]: `KMeans(n_clusters=i, random_state=0)`; cell [39]/[52]: `KMeans(n_clusters=4, random_state=5)` / `KMeans(n_clusters=6, random_state=5)`.

**Reproduction**

Same script: unscaled k=4 sizes are [3998, 2, 46, 5] with random_state=0 (silhouette loop) and with random_state=5 (final model), so it made no difference here; PCA k=6 sizes [1814, 13, 2137, 4, 82, 1] (seed 0) vs [2137, 13, 4, 1815, 1, 81] (seed 5) differ by one object.

**Impact**

Negligible in this data, but the plotted partition is not guaranteed to be the one the elbow was computed on.

**Recommendation**

Use one seed and n_init throughout, defined once at the top.

**Verifier: ✅ confirmed**

*Corrected statement:* Elbow sweeps use random_state=0 (cells [34], [49]); final fits use random_state=5 (cells [39], [52]). For the unscaled k=4 fit the two seeds give the identical partition (ARI 1.0); for the PCA k=6 fit they differ by one object (ARI 0.99954). Negligible here, but the plotted partition is not by construction the one the elbow was computed on.

*Verifier evidence:* verify_core.py: 'k=4 rs=0 vs rs=5 identical partition (ARI): 1.0'; 'k=6 rs=0 sizes: [1814, 13, 2137, 4, 82, 1] | ARI rs0 vs rs5: 0.99954 | n objects differing (best matching): 1'.
