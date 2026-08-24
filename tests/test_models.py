"""Regression anchors for the 2020 baseline and the leakage rule.

Numbers come from the 2026-08-24 review (notebook 03) and were reproduced with
kepler.models on 2026-08-24; tolerances allow for scikit-learn version drift.
"""

import warnings

import pytest

from kepler.data import load_kaggle_snapshot
from kepler.models import (
    cv_macro_f1,
    fit_and_score,
    flag_rule,
    legacy_models,
    log1p_scaled,
    scaled,
    score,
    split,
)
from kepler.preprocess import FEATURE_SETS, clean, model_table


@pytest.fixture(scope="module")
def legacy_split():
    table = model_table(clean(load_kaggle_snapshot()), "legacy_2020")
    return split(table.X, table.y)


def test_split_reproduces_2020_test_classes(legacy_split):
    _, X_test, _, y_test = legacy_split
    assert len(X_test) == 2237
    assert y_test.value_counts().sort_index().tolist() == [534, 572, 1131]


def test_2020_gradient_boosting_numbers(legacy_split):
    X_train, X_test, y_train, y_test = legacy_split
    s = fit_and_score(
        scaled(legacy_models()["gradient_boosting"]), X_train, y_train, X_test, y_test
    )
    assert s.accuracy == pytest.approx(0.9021, abs=0.005)
    assert s.f1_weighted == pytest.approx(0.9015, abs=0.005)
    assert s.f1_macro == pytest.approx(0.8706, abs=0.01)
    assert s.f1_per_class["FALSE POSITIVE"] == pytest.approx(0.99, abs=0.005)


def test_flag_rule_matches_models_on_false_positives(legacy_split):
    _, X_test, _, y_test = legacy_split
    s = score(y_test, flag_rule(X_test))
    assert s.accuracy == pytest.approx(0.7550, abs=0.001)
    assert s.f1_per_class["FALSE POSITIVE"] == pytest.approx(0.9908, abs=0.001)
    assert s.f1_per_class["CANDIDATE"] == 0.0


def test_physics_only_loses_the_flag_lookup(legacy_split):
    X_train, X_test, y_train, y_test = legacy_split
    cols = FEATURE_SETS["physics_only"]
    gbt = legacy_models()["gradient_boosting"]
    with_flags = fit_and_score(scaled(gbt), X_train, y_train, X_test, y_test)
    physics = fit_and_score(scaled(gbt), X_train[cols], y_train, X_test[cols], y_test)
    assert with_flags.f1_macro - physics.f1_macro > 0.10
    assert physics.f1_per_class["FALSE POSITIVE"] < 0.90


def test_log1p_pipeline_and_cv_run(legacy_split):
    X_train, X_test, y_train, y_test = legacy_split
    cols = FEATURE_SETS["physics_only"]
    pipe = log1p_scaled(legacy_models()["logistic_regression"], cols)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s = fit_and_score(pipe, X_train[cols], y_train, X_test[cols], y_test)
        mean, std, folds = cv_macro_f1(pipe, X_train[cols], y_train, n_splits=3)
    assert 0 < s.f1_macro < 1
    assert len(folds) == 3 and 0 < mean < 1 and std >= 0
