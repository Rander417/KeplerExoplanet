"""The numpy copy of the boosting model must reproduce scikit-learn exactly."""

import numpy as np
import pandas as pd
import pytest
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold

from kepler import data, preprocess
from kepler.models import add_missing_indicators, hgb_model
from kepler.portable import PortableHGB
from kepler.verdict import CLASSES, verdict, verdict_frame


@pytest.fixture(scope="module")
def table():
    snap = data.load_kaggle_snapshot()
    t = preprocess.model_table(preprocess.clean(snap), "physics_only", dropna=False)
    X = add_missing_indicators(t.X)
    return X, t.y


@pytest.fixture(scope="module")
def fitted(table):
    X, y = table
    small = {"max_iter": 30, "early_stopping": False, "max_leaf_nodes": 15}
    hgb = hgb_model(**small).fit(X, y)
    cal = CalibratedClassifierCV(
        hgb_model(**small),
        method="isotonic",
        cv=StratifiedKFold(3, shuffle=True, random_state=0),
        ensemble=False,
    ).fit(X, y)
    return hgb, cal


def test_plain_hgb_matches_sklearn(table, fitted):
    X, _ = table
    hgb, _ = fitted
    p = PortableHGB.from_sklearn(hgb, list(X.columns), list(data.CLASSES))
    assert p.n_iterations == hgb.n_iter_
    np.testing.assert_allclose(p.raw_predict(X), hgb.decision_function(X), rtol=0, atol=1e-12)
    np.testing.assert_allclose(p.predict_proba(X), hgb.predict_proba(X), rtol=0, atol=1e-12)


def test_calibrated_matches_sklearn_and_roundtrips(table, fitted, tmp_path):
    X, _ = table
    _, cal = fitted
    p = PortableHGB.from_sklearn(cal, list(X.columns), list(data.CLASSES), meta={"note": "test"})
    assert p.calibrators is not None and len(p.calibrators) == 3
    np.testing.assert_allclose(p.predict_proba(X), cal.predict_proba(X), rtol=0, atol=1e-12)

    q = PortableHGB.load(p.save(tmp_path / "model.json"))
    assert (
        q.columns == list(X.columns)
        and q.classes == list(data.CLASSES)
        and q.meta == {"note": "test"}
    )
    np.testing.assert_allclose(q.predict_proba(X), cal.predict_proba(X), rtol=0, atol=1e-12)
    frame = q.predict_frame(X.head())
    assert list(frame.columns) == list(data.CLASSES) and frame.index.equals(X.head().index)
    assert np.allclose(frame.sum(axis=1), 1.0)


def test_contract_is_enforced(table, fitted):
    X, _ = table
    hgb, _ = fitted
    p = PortableHGB.from_sklearn(hgb, list(X.columns), list(data.CLASSES))
    with pytest.raises(KeyError):
        p.predict_proba(X.drop(columns=["koi_period"]))
    # column order in the input does not matter: the contract reorders
    shuffled = X[list(reversed(X.columns))]
    np.testing.assert_allclose(p.predict_proba(shuffled), hgb.predict_proba(X), rtol=0, atol=1e-12)


def test_verdict_rule():
    proba = pd.DataFrame(
        [[0.2, 0.7, 0.1], [0.45, 0.10, 0.45], [0.3, 0.1, 0.6], [0.26, 0.25, 0.49]],
        columns=list(CLASSES),
        index=["a", "b", "c", "d"],
    )
    assert list(verdict(proba)) == ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE", "CANDIDATE"]
    assert list(verdict(proba, threshold=0.6)) == [
        "CONFIRMED",
        "FALSE POSITIVE",
        "FALSE POSITIVE",
        "FALSE POSITIVE",
    ]
    frame = verdict_frame(proba)
    assert list(frame.columns) == [*CLASSES, "p_planet_like", "model_verdict"]
    np.testing.assert_allclose(frame["p_planet_like"], [0.9, 0.55, 0.4, 0.51])
