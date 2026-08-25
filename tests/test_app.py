"""The shipped app bundle, the browser-safe modules, and the app script itself."""

import importlib
import json
import re
import sys

import numpy as np
import pandas as pd
import pytest

from kepler.paths import PROJECT_ROOT
from kepler.portable import PortableHGB
from kepler.preprocess import PHYSICS_COLUMNS
from kepler.verdict import CLASSES, verdict

APP = PROJECT_ROOT / "app"
BROWSER_MODULES = [
    "kepler.paths",
    "kepler.data",
    "kepler.habitable",
    "kepler.palette",
    "kepler.portable",
    "kepler.verdict",
]


@pytest.fixture(scope="module")
def bundle():
    table = pd.read_csv(APP / "data" / "koi_table.csv", index_col="kepoi_name")
    summary = json.loads((APP / "data" / "summary.json").read_text(encoding="utf-8"))
    model = PortableHGB.load(APP / "model" / "hgb_physics_only.json")
    return table, summary, model


def test_bundle_is_complete_and_consistent(bundle):
    table, summary, model = bundle
    assert len(table) == 9564 and table.index.is_unique
    assert summary["quick"] is False and model.meta["quick"] is False, "never ship a --quick bundle"
    assert summary["table"]["rows"] == len(table)
    assert list(table.columns) == summary["table"]["columns"]
    assert model.classes == list(CLASSES)
    assert model.calibrators is not None and len(model.calibrators) == 3
    assert model.meta["trained_on"]["sha256"] == summary["sources"]["live"]["sha256"]
    assert model.meta["export_check_max_abs_diff_vs_sklearn"] < 1e-9

    probs = table[["p_candidate", "p_confirmed", "p_false_positive"]].to_numpy()
    assert np.allclose(probs.sum(axis=1), 1.0, atol=2e-5)
    assert np.allclose(table["p_planet_like"], probs[:, 0] + probs[:, 1], atol=2e-5)
    assert list(table["model_verdict"].unique()) and set(table["model_verdict"]) <= set(CLASSES)
    assert (table["model_verdict"] == verdict(probs)).mean() > 0.999  # rounding to 5 decimals only

    # the contract can be built from the physics columns alone (what the what-if panel does)
    X = model.prepare(table[PHYSICS_COLUMNS])
    assert list(X.columns) == model.columns
    p = model.predict_proba(X.head(50))
    assert p.shape == (50, 3) and np.allclose(p.sum(axis=1), 1.0)

    hz = summary["habitable_zone"]
    assert hz["confirmed_conservative_le_2"] == int(
        (
            table["hz_conservative"]
            & table["super_earth"]
            & (table["koi_disposition"] == "CONFIRMED")
        ).sum()
    )


def test_site_file_list_matches_index_html():
    sys.path.insert(0, str(APP))
    try:
        build_site = importlib.import_module("build_site")
    finally:
        sys.path.remove(str(APP))
    html = (APP / "index.html").read_text(encoding="utf-8")
    block = html[
        html.index("const APP_FILES = [") : html.index("];", html.index("const APP_FILES = ["))
    ]
    in_html = re.findall(r'"([^"]+)"', block)
    assert in_html == build_site.APP_FILES
    for rel in build_site.APP_FILES:
        assert (PROJECT_ROOT / rel).exists(), rel


def test_browser_modules_do_not_need_sklearn_or_matplotlib(monkeypatch):
    """Everything app/index.html mounts must import with the heavy libraries absent."""
    for name in list(sys.modules):
        if name.split(".")[0] in {"sklearn", "matplotlib", "imblearn", "kepler"}:
            monkeypatch.delitem(sys.modules, name)
    for blocked in ("sklearn", "matplotlib", "imblearn", "scipy"):
        monkeypatch.setitem(sys.modules, blocked, None)  # makes `import x` raise ImportError
    for mod in BROWSER_MODULES:
        importlib.import_module(mod)


def test_app_script_runs_headless(bundle):
    """Execute app/app.py with Streamlit's AppTest (no browser) and check for exceptions."""
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(APP / "app.py"), default_timeout=120)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert any("Kepler KOI explorer" in t.value for t in at.title)
    labels = [m.label for m in at.metric]
    assert "KOIs shown" in labels and "Out-of-time AUC" in labels


def test_quick_bundle_builds(tmp_path):
    """The whole build pipeline runs end to end (small model; takes ~40 s)."""
    from kepler import app_bundle

    summary = app_bundle.build(tmp_path, quick=True)
    assert summary["quick"] is True
    table = pd.read_csv(tmp_path / "data" / "koi_table.csv", index_col="kepoi_name")
    model = PortableHGB.load(tmp_path / "model" / "hgb_physics_only.json")
    assert len(table) == 9564 and model.n_iterations == 20
    m = summary["metrics"]
    assert 0.6 < m["cv_macro_f1_physics_only"]["mean"] < 0.9
    assert 0.85 < m["out_of_time"]["auc_confirmed_vs_false_positive"] < 1.0
    assert summary["transitions"]["matrix"][1][0] == 0  # no CONFIRMED -> CANDIDATE
