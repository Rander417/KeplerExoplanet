"""Habitable-zone screen: the Kopparapu limits and the 2020 comparison, pinned."""

import numpy as np
import pandas as pd
import pytest

from kepler.data import TARGET, load_kaggle_snapshot
from kepler.habitable import KOPPARAPU_2014, hz_table, legacy_2020_box, seff_limit, summarise
from kepler.paths import LEGACY_PICKLES


@pytest.fixture(scope="module")
def raw():
    return load_kaggle_snapshot()


@pytest.fixture(scope="module")
def hz(raw):
    return hz_table(raw)


def test_limits_reproduce_the_sun_and_respect_validity():
    for limit, (s0, *_) in KOPPARAPU_2014.items():
        assert float(seff_limit(5780.0, limit)) == pytest.approx(s0, abs=1e-12)
    inner, outer = (
        seff_limit(3500.0, "runaway_greenhouse"),
        seff_limit(3500.0, "maximum_greenhouse"),
    )
    assert 0 < outer < inner < 1.107  # cooler star: both limits move to lower flux
    assert np.isnan(seff_limit(2599.0, "early_mars")) and np.isnan(seff_limit(7201.0, "early_mars"))


def test_zone_flags_are_consistent(hz):
    assert hz["hz_conservative"].sum() <= hz["hz_optimistic"].sum()
    assert (hz["hz_conservative"] <= hz["hz_optimistic"]).all()  # conservative implies optimistic
    assert (hz["hz_conservative"] <= hz["hz_conservative_possible"]).all()
    assert hz["teff_in_range"].sum() == 8959


def test_snapshot_counts_2026_08_24(hz):
    confirmed = summarise(hz, "CONFIRMED")
    assert confirmed.loc["hz_conservative", "any radius"] == 31
    assert confirmed.loc["hz_conservative", "radius <= 2.0"] == 15
    assert confirmed.loc["hz_conservative", "radius <= 1.6"] == 8
    assert confirmed.loc["hz_conservative", "radius <= 2.0, Sun-like host"] == 1  # Kepler-452 b
    small = hz[(hz[TARGET] == "CONFIRMED") & hz["hz_conservative"] & hz["super_earth"]]
    assert "Kepler-452 b" in set(small["kepler_name"]) and "Kepler-442 b" in set(
        small["kepler_name"]
    )


def test_2020_box_reproduces_the_legacy_pickles(raw):
    joined, stats = legacy_2020_box(raw)
    assert stats["without stellar extra"] == 434
    box_confirmed = joined[joined["legacy_box"] & (joined[TARGET] == "CONFIRMED")]
    box_candidates = joined[joined["legacy_box"] & (joined[TARGET] == "CANDIDATE")]
    legacy_c = pd.read_pickle(LEGACY_PICKLES["habitable_confirmed"])
    legacy_k = pd.read_pickle(LEGACY_PICKLES["habitable_candidates"])
    assert set(box_confirmed.index) == set(legacy_c.index) and len(legacy_c) == 12
    assert set(box_candidates.index) == set(legacy_k.index) and len(legacy_k) == 37


def test_2020_survivors_are_not_in_the_conservative_zone(raw, hz):
    joined, _ = legacy_2020_box(raw)
    box12 = joined.index[joined["legacy_box"] & (joined[TARGET] == "CONFIRMED")]
    assert hz.loc[box12, "hz_conservative"].sum() == 0
    assert hz.loc[box12, "koi_prad"].min() > 3.0
