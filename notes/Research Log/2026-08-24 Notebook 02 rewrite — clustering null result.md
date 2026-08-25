---
tags: [research-log, notebook-02, clustering, null-result]
date: 2026-08-24
---

# 2026-08-24 Notebook 02 rewrite — clustering null result

> [!success] Outcome
> `notebooks/02_clustering.ipynb` rewritten on `kepler.clustering`: scaled `log1p` physics columns, **all three classes**, k = 2…10, and an explicit agreement score against the archive dispositions. Result: **no discrete groups track planet-ness** (ARI ≤ 0.05, NMI ≤ 0.13 for every k). 19 tests pass, including one that pins this null result.

## Numbers (9,200 complete-case KOIs, 12 physics columns, log1p + StandardScaler)

| k | silhouette | ARI vs dispositions | NMI | largest cluster |
|---|---|---|---|---|
| 2 | **0.328** | −0.003 | 0.123 | 75.7% |
| 3 | 0.216 | 0.026 | 0.081 | 43.0% |
| 4 | 0.240 | 0.013 | 0.084 | 43.7% |
| 5 | 0.248 | 0.012 | 0.087 | 44.8% |
| 7 | 0.196 | 0.040 | 0.085 | 30.6% |
| 10 | 0.194 | 0.035 | 0.097 | 20.5% |

- Silhouette picks k = 2; inertia has no elbow. The k = 2 split separates big/deep/hot signals from small/shallow/cool ones (centroid heat-map in the notebook) and carries the catalogue's overall class mix on both sides.
- PCA: PC1 30%, PC2 22%, PC3 18% of variance (first two = 52%). In PCA space planets form a dense core with false positives spread around it: a **gradient the supervised models exploit, not groups** that k-means recovers.
- Contrast with 2020: unscaled four-column k-means had transit depth carrying 99.9% of the variance, the "elbow at 4" was four depth bins with 98.7% of objects in one, and every FALSE POSITIVE had been removed beforehand (see the [review](2026-08-24%20Review%2002_clustering.md)).

## Built

- `src/kepler/clustering.py`: `cluster_matrix` (complete cases, log1p, scaling, labels kept), `kmeans_sweep` (inertia, silhouette on a 3,000-row sample, ARI, NMI, largest-cluster share), `fit_kmeans`, `pca_map`.
- `tests/test_clustering.py`: 3 tests, including `test_clusters_do_not_track_dispositions` (ARI < 0.15 for k = 2…6, no one-cluster artifact).
- Figures: `reports/figures/clustering/kmeans_sweep.png`, `centroids_k2.png`, `pca_map.png`. The 2020 figures moved to `reports/figures/clustering_2020/`.

## Housekeeping in the same batch

- `reports/tables/03_baseline_metrics.csv` no longer lists the three legacy models twice for the 2020 split (Claude Code's catch): 19 rows now.

## Answer to the 2020 question

*"Does EDA reveal interesting groupings?"* — **No.** The physics has continuous structure and a dense planet core, but unsupervised clustering does not find planet-ness; that is a supervised problem, and notebook 03's physics-only ceiling (macro f1 ≈ 0.72) is its honest difficulty.
