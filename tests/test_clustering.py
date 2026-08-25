"""The clustering null result, pinned so it cannot silently become a positive one."""

import pytest

from kepler.clustering import cluster_matrix, kmeans_sweep, pca_map
from kepler.data import load_kaggle_snapshot
from kepler.preprocess import clean


@pytest.fixture(scope="module")
def matrix():
    return cluster_matrix(clean(load_kaggle_snapshot()))


def test_cluster_matrix_keeps_all_classes_and_is_scaled(matrix):
    X, labels = matrix
    assert len(X) == 9200  # complete cases on the 12 physics columns
    assert set(labels.unique()) == {"CANDIDATE", "CONFIRMED", "FALSE POSITIVE"}
    assert abs(X.mean()).max() < 1e-6 and abs(X.std(ddof=0) - 1).max() < 1e-6


def test_clusters_do_not_track_dispositions(matrix):
    X, labels = matrix
    sweep = kmeans_sweep(X, labels, ks=range(2, 7))
    assert (sweep["ari"] < 0.15).all()  # 2026-08-24: max ARI over k=2..6 was well below this
    assert (sweep["largest_cluster_share"] < 0.98).all()  # not the 2020 one-cluster artifact


def test_pca_map_shapes(matrix):
    X, _ = matrix
    coords, pca = pca_map(X)
    assert coords.shape == (len(X), 2)
    assert 0 < pca.explained_variance_ratio_.sum() < 1
