"""Loading the Kepler Objects of Interest (KOI) cumulative table.

Column names follow the NASA Exoplanet Archive exactly (``koi_period``,
``koi_prad``, ...), so code lines up with the archive documentation and with
future TAP pulls. Readable labels with units live in ``LABELS`` and are for
charts and tables only. The 2020 notebooks renamed columns instead; that map
is kept in ``LEGACY_NAMES`` so the old pickles can still be compared.

Definitions of every column are quoted from the archive in ``data/README.md``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from kepler.paths import DATA_RAW

KAGGLE_SNAPSHOT = DATA_RAW / "cumulative_kaggle_snapshot.csv"
STELLAR_EXTRA = DATA_RAW / "stellar_info_final.csv"

INDEX = "kepoi_name"  # unique per KOI; kepid is not (one star can host several KOIs)
TARGET = "koi_disposition"  # the archive verdict: the project's target ("two Ys" decision)
PIPELINE_VERDICT = "koi_pdisposition"  # the Kepler-pipeline verdict: the *other* Y, never a feature

# Alphabetical order, which is what the 2020 LabelEncoder produced: 0, 1, 2.
CLASSES = ("CANDIDATE", "CONFIRMED", "FALSE POSITIVE")
CLASS_CODES = {name: code for code, name in enumerate(CLASSES)}
CODE_CLASSES = {code: name for name, code in CLASS_CODES.items()}

EXPECTED_SNAPSHOT_SHAPE = (9564, 50)

LABELS = {
    "kepid": "KIC ID",
    "kepoi_name": "KOI name",
    "kepler_name": "Kepler name",
    "koi_disposition": "Archive disposition",
    "koi_pdisposition": "Pipeline disposition",
    "koi_score": "Disposition score",
    "koi_fpflag_nt": "Not transit-like flag",
    "koi_fpflag_ss": "Stellar eclipse flag",
    "koi_fpflag_co": "Centroid offset flag",
    "koi_fpflag_ec": "Ephemeris match flag",
    "koi_period": "Orbital period [days]",
    "koi_time0bk": "Transit epoch [BKJD]",
    "koi_impact": "Impact parameter",
    "koi_duration": "Transit duration [hours]",
    "koi_depth": "Transit depth [ppm]",
    "koi_prad": "Planet radius [Earth radii]",
    "koi_teq": "Equilibrium temperature [K]",
    "koi_insol": "Insolation [Earth flux]",
    "koi_model_snr": "Transit signal-to-noise",
    "koi_tce_plnt_num": "TCE planet number",
    "koi_tce_delivname": "TCE delivery",
    "koi_steff": "Stellar effective temperature [K]",
    "koi_slogg": "Stellar surface gravity [log10 cm/s^2]",
    "koi_srad": "Stellar radius [Solar radii]",
    "koi_smet": "Stellar metallicity [dex]",
    "koi_smass": "Stellar mass [Solar masses]",
    "ra": "Right ascension [deg]",
    "dec": "Declination [deg]",
    "koi_kepmag": "Kepler magnitude",
}

# What the 2020 notebooks called each column (see data/legacy/*.pkl).
LEGACY_NAMES = {
    "rowid": "rowid",
    "kepid": "Kep_ID",
    "kepler_name": "Kepler_Name",
    "koi_disposition": "Exoplanet_Archive_Disposition",
    "koi_pdisposition": "Disposition_Using_Kepler_Data",
    "koi_score": "Disposition_Score",
    "koi_fpflag_nt": "Not_Transit-Like_FPF",
    "koi_fpflag_ss": "Stellar_Eclipse_FPF",
    "koi_fpflag_co": "Centroid_Offset_FPF",
    "koi_fpflag_ec": "Ephemeris_Match_Indicates_Contamination_FPF",
    "koi_period": "Orbital_Period_[days]",
    "koi_time0bk": "Transit_Epoch_[BKJD]",
    "koi_impact": "Impact_Parameter",
    "koi_duration": "Transit_Duration_[hrs]",
    "koi_depth": "Transit_Depth_[ppm]",
    "koi_prad": "Planetary_Radius_[Earth radii]",
    "koi_teq": "Equilibrium_Temperature_[K]",
    "koi_insol": "Insolation_Flux_[Earth flux]",
    "koi_model_snr": "Transit_Signal-to-Noise",
    "koi_tce_plnt_num": "TCE_Planet_Number",
    "koi_tce_delivname": "TCE_Delivery",
    "koi_steff": "Stellar_Effective_Temperature_[K]",
    "koi_slogg": "Stellar_Surface_Gravity",
    "koi_srad": "Stellar_Radius_[Solar_radii]",
    "ra": "right_ascension",
    "dec": "declination",
    "koi_kepmag": "Kepler_band [mag]",
}


def load_kaggle_snapshot(path: Path = KAGGLE_SNAPSHOT) -> pd.DataFrame:
    """The 2017-era Kaggle export of the cumulative KOI table, indexed by KOI name.

    Nothing is cleaned here: 9,564 rows x 49 columns after the index is set,
    nulls intact, so every later step is visible and testable.
    """
    df = pd.read_csv(path)
    if df.shape != EXPECTED_SNAPSHOT_SHAPE:
        raise ValueError(
            f"unexpected snapshot shape {df.shape}, expected {EXPECTED_SNAPSHOT_SHAPE}"
        )
    df = df.set_index(INDEX)
    if not df.index.is_unique:
        raise ValueError("kepoi_name is not unique; the snapshot is not the file we expect")
    return df


def load_stellar_extra(path: Path = STELLAR_EXTRA) -> pd.DataFrame:
    """Stellar metallicity and mass (with errors) for 7,810 host stars, indexed by kepid.

    These columns exist in the archive's cumulative table; this file only exists
    because the 2020 project pulled them separately. A TAP pull makes it redundant.
    """
    df = pd.read_csv(path).set_index("kepid")
    if not df.index.is_unique:
        raise ValueError("kepid is not unique in the stellar file")
    return df


def error_columns(df: pd.DataFrame) -> list[str]:
    """The ``*_err1`` / ``*_err2`` uncertainty columns (22 in the snapshot)."""
    return [c for c in df.columns if c.endswith(("_err1", "_err2"))]


def label(column: str) -> str:
    """Readable label for a column, falling back to the archive name."""
    return LABELS.get(column, column)
