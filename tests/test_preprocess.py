"""Regression and leakage tests for kepler.data / kepler.preprocess.

The numbers asserted here were measured in the 2026-08-24 review and recorded in
notes/Research Log; if a data change moves them, the note is where to look.
"""

import numpy as np
import pandas as pd
import pytest

from kepler.data import CLASS_CODES, CLASSES, TARGET, error_columns, load_kaggle_snapshot
from kepler.paths import LEGACY_PICKLES
from kepler.preprocess import (
    FEATURE_SETS,
    LEAKAGE_COLUMNS,
    LEGACY_2020_FEATURES,
    clean,
    legacy_2020_processed,
    model_table,
    null_report,
    rows_with_nulls_by_class,
    to_legacy_names,
)


@pytest.fixture(scope="module")
def raw():
    return load_kaggle_snapshot()


@pytest.fixture(scope="module")
def cleaned(raw):
    return clean(raw)


def test_snapshot_indexed_by_unique_koi(raw):
    assert raw.shape == (9564, 49)
    assert raw.index.name == "kepoi_name"
    assert raw.index.is_unique
    assert len(error_columns(raw)) == 22


def test_class_codes_match_2020_label_encoder():
    assert CLASSES == ("CANDIDATE", "CONFIRMED", "FALSE POSITIVE")
    assert CLASS_CODES == {"CANDIDATE": 0, "CONFIRMED": 1, "FALSE POSITIVE": 2}


def test_clean_keeps_every_row_and_numeric_score(raw, cleaned):
    assert len(cleaned) == len(raw) == 9564
    assert pd.api.types.is_float_dtype(cleaned["koi_score"])
    assert cleaned["koi_score_missing"].sum() == 1510
    # Every CONFIRMED planet has a Kepler name, plus one named FALSE POSITIVE
    # (K00126.01, Kepler-469 b, retracted after naming), so the name is a
    # near-perfect CONFIRMED proxy and never a feature.
    assert cleaned["has_kepler_name"].sum() == 2294
    named = cleaned.loc[cleaned["has_kepler_name"], TARGET].value_counts().to_dict()
    assert named == {"CONFIRMED": 2293, "FALSE POSITIVE": 1}


def test_null_report_matches_review(cleaned):
    report = null_report(cleaned[[c for c in cleaned.columns if c.startswith("koi_")]])
    assert report.loc["koi_steff", "nulls"] == 363
    assert report.loc["koi_insol", "nulls"] == 321
    assert report.loc["koi_tce_delivname", "nulls"] == 346


def test_dropna_loses_619_rows_mostly_false_positives(cleaned):
    table = rows_with_nulls_by_class(cleaned, FEATURE_SETS["legacy_2020"])
    assert table.loc["ALL", "dropped"] == 619
    assert table.loc["FALSE POSITIVE", "dropped"] == 499
    assert table.loc["CANDIDATE", "dropped"] == 112
    assert table.loc["CONFIRMED", "dropped"] == 8


def test_physics_only_has_no_leakage_columns():
    physics = FEATURE_SETS["physics_only"]
    assert not set(physics) & set(LEAKAGE_COLUMNS)
    assert "koi_tce_delivname" not in physics and "ra" not in physics


def test_model_table_shapes(cleaned):
    # The physics/flags sets need fewer columns, so dropna loses 364 rows, not 619:
    # the extra 255 drops in 2020 came from the provenance columns.
    with_flags = model_table(cleaned, "with_flags")
    assert with_flags.X.shape == (9200, 16)
    assert with_flags.n_dropped == 364
    assert with_flags.y.value_counts().sort_index().tolist() == [2185, 2292, 4723]

    legacy = model_table(cleaned, "legacy_2020")
    assert legacy.X.shape == (8945, 23)
    assert legacy.n_dropped == 619
    assert legacy.y.value_counts().sort_index().tolist() == [2136, 2285, 4524]

    keep_nan = model_table(cleaned, "physics_only", dropna=False)
    assert len(keep_nan.X) == 9564
    assert keep_nan.X.isna().any().any()


def test_legacy_pipeline_reproduces_2020_pickle(raw):
    ours = to_legacy_names(legacy_2020_processed(raw))
    theirs = pd.read_pickle(LEGACY_PICKLES["processed"])
    assert list(ours.columns) == list(theirs.columns)
    assert ours.index.equals(theirs.index)
    np.testing.assert_allclose(
        ours.to_numpy(dtype=float), theirs.to_numpy(dtype=float), rtol=0, atol=1e-9
    )
    assert len(LEGACY_2020_FEATURES) == 23
