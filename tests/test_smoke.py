"""Smoke tests: does the environment and repository layout work at all?

Run with:  uv run pytest
These are deliberately tiny; they exist so a fresh machine has a pass/fail signal.
"""

import pandas as pd

from kepler.paths import DATA_LEGACY, DATA_RAW, LEGACY_PICKLES, NOTES, PROJECT_ROOT


def test_layout_exists():
    for path in (
        DATA_RAW,
        DATA_LEGACY,
        NOTES,
        PROJECT_ROOT / "notebooks",
        PROJECT_ROOT / "CLAUDE.md",
    ):
        assert path.exists(), f"missing: {path}"


def test_kaggle_snapshot_loads():
    df = pd.read_csv(DATA_RAW / "cumulative_kaggle_snapshot.csv")
    assert df.shape == (9564, 50)
    assert df["koi_disposition"].value_counts().to_dict() == {
        "FALSE POSITIVE": 5023,
        "CONFIRMED": 2293,
        "CANDIDATE": 2248,
    }


def test_legacy_pickles_load():
    processed = pd.read_pickle(LEGACY_PICKLES["processed"])
    assert processed.shape == (8945, 24)
    # LabelEncoder mapping recorded in the 2026-08-24 notebook-01 pre-review
    assert processed["Exoplanet_Archive_Disposition"].value_counts().sort_index().tolist() == [
        2136,
        2285,
        4524,
    ]


def test_live_pull_loads_and_matches_snapshot_index():
    from kepler.data import load_kaggle_snapshot, load_tap_pull, tap_pulls

    assert tap_pulls(), "no live pull committed"
    live = load_tap_pull()
    snap = load_kaggle_snapshot()
    assert len(live) == 9564 and live.shape[1] >= 150
    assert set(live.index) == set(snap.index)
    assert set(snap.columns) - set(live.columns) == {"rowid"}
