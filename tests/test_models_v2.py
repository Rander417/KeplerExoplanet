"""Phase 3 helpers: missing indicators, NaN-native boosting, nested CV, calibration tables."""

import numpy as np
import pytest

from kepler.data import load_kaggle_snapshot
from kepler.models import (
    add_missing_indicators,
    brier_multiclass,
    hgb_model,
    nested_cv,
    reliability_table,
)
from kepler.preprocess import clean, model_table


@pytest.fixture(scope="module")
def physics_all_rows():
    table = model_table(clean(load_kaggle_snapshot()), "physics_only", dropna=False)
    return add_missing_indicators(table.X), table.y


def test_missing_indicators_only_for_columns_with_nans(physics_all_rows):
    X, _ = physics_all_rows
    indicators = [c for c in X.columns if c.endswith("_missing")]
    assert len(indicators) == 10  # koi_period and koi_duration have no nulls in the snapshot
    assert "koi_period_missing" not in X.columns
    assert X["koi_steff_missing"].sum() == 363 and X["koi_kepmag_missing"].sum() == 1
    assert X["koi_steff"].isna().sum() == 363  # NaNs stay in place


def test_hgb_fits_with_nans_and_predicts_all_classes(physics_all_rows):
    X, y = physics_all_rows
    model = hgb_model(max_iter=50).fit(X, y)
    pred = model.predict(X)
    assert set(np.unique(pred)) == {0, 1, 2}


def test_nested_cv_small_grid(physics_all_rows):
    X, y = physics_all_rows
    sub = X.iloc[:2000]
    res = nested_cv(
        hgb_model(max_iter=40),
        {"max_leaf_nodes": [15, 31]},
        sub,
        y.iloc[:2000],
        outer_splits=2,
        inner_splits=2,
    )
    assert len(res.folds) == 2 and len(res.params) == 2
    assert res.oof_proba.shape == (2000, 3)
    assert np.allclose(res.oof_proba.sum(axis=1), 1.0)
    assert 0.3 < res.folds["f1_macro"].mean() < 1.0


def test_reliability_and_brier_shapes(physics_all_rows):
    _, y = physics_all_rows
    rng = np.random.default_rng(0)
    proba = rng.dirichlet(np.ones(3), size=len(y))
    table = reliability_table(y, proba, n_bins=5)
    assert set(table["class"]) == {"CANDIDATE", "CONFIRMED", "FALSE POSITIVE"}
    assert table["count"].sum() == 3 * len(y)
    assert 0 < brier_multiclass(y, proba) < 2
