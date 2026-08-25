"""Unsupervised structure in the physical KOI quantities, and whether it tracks the labels.

The 2020 clustering ran k-means on four unscaled columns (transit depth carried
99.9% of the variance), on the planet-like half of the catalogue only, and never
compared the clusters with anything. This module does the honest version:
log1p on heavy-tailed columns, standard scaling, every class kept, and an
explicit agreement score (adjusted Rand index, normalised mutual information)
between clusters and archive dispositions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from kepler.models import HEAVY_TAILED
from kepler.preprocess import PHYSICS_COLUMNS


def cluster_matrix(
    cleaned: pd.DataFrame, columns: list[str] | None = None
) -> tuple[pd.DataFrame, pd.Series]:
    """Complete-case rows of ``columns`` (default: the physics set), log1p'd where
    heavy-tailed and standardised. Returns the scaled matrix (as a DataFrame that
    keeps the KOI index) and the archive disposition for the same rows.
    """
    columns = list(columns or PHYSICS_COLUMNS)
    table = cleaned.dropna(subset=columns)
    values = table[columns].astype(float).copy()
    for c in columns:
        if c in HEAVY_TAILED:
            values[c] = np.log1p(values[c].clip(lower=0))
    scaled = StandardScaler().fit_transform(values)
    X = pd.DataFrame(scaled, index=table.index, columns=columns)
    return X, table["koi_disposition"]


def kmeans_sweep(
    X: pd.DataFrame,
    labels: pd.Series,
    ks: range = range(2, 11),
    *,
    random_state: int = 0,
    silhouette_sample: int = 3000,
) -> pd.DataFrame:
    """Fit k-means for each k; report inertia, silhouette, and agreement with ``labels``."""
    rows = []
    rng_labels = labels.to_numpy()
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(X)
        pred = km.labels_
        rows.append(
            {
                "k": k,
                "inertia": float(km.inertia_),
                "silhouette": float(
                    silhouette_score(
                        X, pred, sample_size=silhouette_sample, random_state=random_state
                    )
                ),
                "ari": float(adjusted_rand_score(rng_labels, pred)),
                "nmi": float(normalized_mutual_info_score(rng_labels, pred)),
                "largest_cluster_share": float(np.bincount(pred).max() / len(pred)),
            }
        )
    return pd.DataFrame(rows).set_index("k")


def fit_kmeans(X: pd.DataFrame, k: int, *, random_state: int = 0) -> KMeans:
    return KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(X)


def pca_map(
    X: pd.DataFrame, n_components: int = 2, *, random_state: int = 0
) -> tuple[pd.DataFrame, PCA]:
    """Principal-component coordinates for plotting, plus the fitted PCA (for variance ratios)."""
    pca = PCA(n_components=n_components, random_state=random_state).fit(X)
    coords = pd.DataFrame(
        pca.transform(X), index=X.index, columns=[f"PC{i + 1}" for i in range(n_components)]
    )
    return coords, pca
