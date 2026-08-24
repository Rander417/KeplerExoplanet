"""Cleaning and feature-set definitions for the KOI table.

Two rules from the 2026 review drive this module:

* **Leakage is named, not hidden.** The four ``koi_fpflag_*`` columns, ``koi_score``,
  ``koi_pdisposition`` and ``kepler_name`` all encode the answer. They are kept in
  the cleaned table for analysis but only enter a model through an explicitly
  named feature set (``with_flags``), never by accident.
* **Rows are not thrown away silently.** ``clean`` keeps all 9,564 KOIs and adds
  missingness indicators; ``model_table`` reports how many rows it drops and
  from which classes when ``dropna=True``.

``legacy_2020_processed`` reproduces the 2020 pipeline bit-for-bit (tested
against ``data/legacy/kepler_processed.pkl``) so the old results stay reachable.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from kepler.data import (
    CLASS_CODES,
    LEGACY_NAMES,
    PIPELINE_VERDICT,
    TARGET,
    error_columns,
)

FLAG_COLUMNS = ["koi_fpflag_nt", "koi_fpflag_ss", "koi_fpflag_co", "koi_fpflag_ec"]
SCORE_COLUMN = "koi_score"
IDENTITY_COLUMNS = ["rowid", "kepid", "kepler_name"]
DELIVERY_COLUMN = "koi_tce_delivname"
DELIVERY_VALUES = ["q1_q16_tce", "q1_q17_dr24_tce", "q1_q17_dr25_tce"]

# Columns that leak the target and must never be silently used as features.
LEAKAGE_COLUMNS = [*FLAG_COLUMNS, SCORE_COLUMN, PIPELINE_VERDICT, "kepler_name"]

# Physical transit + stellar quantities: the "physics_only" feature set.
PHYSICS_COLUMNS = [
    "koi_period",
    "koi_impact",
    "koi_duration",
    "koi_depth",
    "koi_prad",
    "koi_teq",
    "koi_insol",
    "koi_model_snr",
    "koi_steff",
    "koi_slogg",
    "koi_srad",
    "koi_kepmag",
]

# Where/when the signal was found rather than what it is (position, epoch,
# catalogue delivery). Legitimate inputs for a *catalogue* model, not for physics.
PROVENANCE_COLUMNS = ["koi_time0bk", "koi_tce_plnt_num", "ra", "dec"]
DELIVERY_DUMMY_COLUMNS = [f"{DELIVERY_COLUMN}_{v}" for v in DELIVERY_VALUES]

# The exact 23 columns (and order) the 2020 models were trained on.
LEGACY_2020_FEATURES = [
    *FLAG_COLUMNS,
    "koi_period",
    "koi_time0bk",
    "koi_impact",
    "koi_duration",
    "koi_depth",
    "koi_prad",
    "koi_teq",
    "koi_insol",
    "koi_model_snr",
    "koi_tce_plnt_num",
    "koi_steff",
    "koi_slogg",
    "koi_srad",
    "ra",
    "dec",
    "koi_kepmag",
    *DELIVERY_DUMMY_COLUMNS,
]

FEATURE_SETS: dict[str, list[str]] = {
    "physics_only": PHYSICS_COLUMNS,
    "with_flags": [*PHYSICS_COLUMNS, *FLAG_COLUMNS],
    "with_flags_and_provenance": [
        *PHYSICS_COLUMNS,
        *FLAG_COLUMNS,
        *PROVENANCE_COLUMNS,
        *DELIVERY_DUMMY_COLUMNS,
    ],
    "legacy_2020": LEGACY_2020_FEATURES,
}


def null_report(df: pd.DataFrame) -> pd.DataFrame:
    """Null count and share per column, non-zero rows only, most-null first."""
    counts = df.isna().sum()
    out = pd.DataFrame({"nulls": counts, "share": counts / len(df)})
    return out[out["nulls"] > 0].sort_values("nulls", ascending=False)


def rows_with_nulls_by_class(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """How many rows per class would be lost by ``dropna`` on ``columns``.

    This is the "619 rows, not 363" table from the review: missingness in the
    KOI table is concentrated in false positives, so dropping rows shifts the
    class balance and discards a signal.
    """
    any_null = df[columns].isna().any(axis=1)
    by_class = df[TARGET].value_counts()
    dropped = df.loc[any_null, TARGET].value_counts().reindex(by_class.index, fill_value=0)
    out = pd.DataFrame({"rows": by_class, "dropped": dropped, "share_dropped": dropped / by_class})
    out.loc["ALL"] = [len(df), int(any_null.sum()), any_null.mean()]
    out["rows"] = out["rows"].astype(int)
    out["dropped"] = out["dropped"].astype(int)
    return out


def add_delivery_dummies(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot columns for the TCE delivery name, as integers, in a fixed order.

    Rows with a missing delivery name get zeros in all three columns.
    """
    out = df.copy()
    for value, column in zip(DELIVERY_VALUES, DELIVERY_DUMMY_COLUMNS, strict=True):
        out[column] = (out[DELIVERY_COLUMN] == value).astype("int64")
    return out


def clean(raw: pd.DataFrame, *, drop_errors: bool = True) -> pd.DataFrame:
    """The cleaned full table: every KOI kept, leakage columns present but labelled.

    Steps (each one visible):
      1. drop the ``*_err1/_err2`` uncertainty columns (the classifier does not
         use them; the habitable-zone work reads them from the raw table instead);
      2. keep ``koi_score`` numeric and add ``koi_score_missing``;
      3. add ``has_kepler_name`` (a CONFIRMED proxy, kept for reporting only);
      4. add the three delivery dummies.
    No rows are dropped here.
    """
    df = raw.copy()
    if drop_errors:
        df = df.drop(columns=error_columns(df))
    df["koi_score_missing"] = df[SCORE_COLUMN].isna()
    df["has_kepler_name"] = df["kepler_name"].notna()
    df = add_delivery_dummies(df)
    return df


@dataclass(frozen=True)
class ModelTable:
    """Features, target codes, and an honest account of what was dropped."""

    X: pd.DataFrame
    y: pd.Series
    feature_set: str
    dropped: pd.DataFrame  # rows_with_nulls_by_class on the feature columns

    @property
    def n_dropped(self) -> int:
        return int(self.dropped.loc["ALL", "dropped"])


def model_table(cleaned: pd.DataFrame, feature_set: str, *, dropna: bool = True) -> ModelTable:
    """Select a named feature set and encode the target as 0/1/2.

    ``dropna=True`` reproduces the 2020 choice of discarding incomplete rows and
    records exactly what went; ``dropna=False`` keeps NaNs for models that
    handle them natively (``HistGradientBoostingClassifier``).
    """
    if feature_set not in FEATURE_SETS:
        raise KeyError(f"unknown feature set {feature_set!r}; choose from {sorted(FEATURE_SETS)}")
    columns = FEATURE_SETS[feature_set]
    missing = [c for c in columns if c not in cleaned.columns]
    if missing:
        raise KeyError(f"cleaned table lacks columns {missing}; call clean() first")
    dropped = rows_with_nulls_by_class(cleaned, columns)
    table = cleaned.dropna(subset=columns) if dropna else cleaned
    X = table[columns].copy()
    y = table[TARGET].map(CLASS_CODES).astype("int64").rename("target")
    if y.isna().any():
        raise ValueError("target contains a class outside CANDIDATE/CONFIRMED/FALSE POSITIVE")
    return ModelTable(X=X, y=y, feature_set=feature_set, dropped=dropped)


def legacy_2020_processed(raw: pd.DataFrame) -> pd.DataFrame:
    """Re-run the 2020 notebook-01 pipeline on the raw snapshot, archive names kept.

    Mirrors ``Kepler_Cleaning_EDA.ipynb`` step for step: drop error columns; treat
    ``kepler_name`` and ``koi_score`` as never-null (the notebook filled them with
    placeholder strings); drop every other row with a null; drop identity and
    leakage columns except the four flags; one-hot the delivery name; encode the
    target 0/1/2. The result matches ``data/legacy/kepler_processed.pkl`` exactly
    (see ``tests/test_preprocess.py``).
    """
    df = raw.drop(columns=error_columns(raw))
    subset = [c for c in df.columns if c not in ("kepler_name", SCORE_COLUMN)]
    df = df.dropna(subset=subset)
    df = df.drop(columns=["rowid", "kepid", "kepler_name", PIPELINE_VERDICT, SCORE_COLUMN])
    df = add_delivery_dummies(df).drop(columns=[DELIVERY_COLUMN])
    df[TARGET] = df[TARGET].map(CLASS_CODES).astype("int64")
    return df[[TARGET, *LEGACY_2020_FEATURES]]


def to_legacy_names(df: pd.DataFrame) -> pd.DataFrame:
    """Rename archive columns to the 2020 names, for comparisons with the old pickles."""
    mapping = dict(LEGACY_NAMES)
    for value, column in zip(DELIVERY_VALUES, DELIVERY_DUMMY_COLUMNS, strict=True):
        mapping[column] = f"TCE_Delivery_{value}"
    return df.rename(columns=mapping)
