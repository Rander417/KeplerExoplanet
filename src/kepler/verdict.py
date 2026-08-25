"""The app's label rule, written down once so the app and the notebooks agree.

Notebook 07 found that calibrated probabilities are better *probabilities* (lower
log loss and Brier score) but that taking their argmax lowers macro f1. So the app
shows the calibrated probabilities and decides labels by an explicit rule instead
of a hidden argmax:

1. ``p_planet_like = P(CANDIDATE) + P(CONFIRMED)`` — "does the physics look like a
   planet at all?" This is the binary question the out-of-time test in notebook 08
   answers (AUC 0.937 on the 2020 candidates the archive later decided).
2. If ``p_planet_like < threshold`` (default 0.5) the verdict is FALSE POSITIVE.
3. Otherwise the verdict is whichever of CONFIRMED or CANDIDATE has the higher
   probability. Physics separates these two only moderately — confirmation is a
   follow-up-and-statistics process, not a measurement — so the app labels this
   second step as the weaker one.

Only numpy and pandas are imported, so the module runs inside the browser build.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

CANDIDATE, CONFIRMED, FALSE_POSITIVE = "CANDIDATE", "CONFIRMED", "FALSE POSITIVE"
CLASSES = (CANDIDATE, CONFIRMED, FALSE_POSITIVE)  # column order of every probability table
PLANET_LIKE_THRESHOLD = 0.5


def planet_like(proba) -> np.ndarray:
    """``P(CANDIDATE) + P(CONFIRMED)`` for an (n, 3) array or a DataFrame with class columns."""
    if isinstance(proba, pd.DataFrame):
        return (proba[CANDIDATE] + proba[CONFIRMED]).to_numpy()
    proba = np.asarray(proba, dtype=float)
    return proba[:, 0] + proba[:, 1]


def verdict(proba, threshold: float = PLANET_LIKE_THRESHOLD) -> np.ndarray:
    """Apply the rule above; returns an object array of class names, one per row."""
    p = proba.to_numpy(dtype=float) if isinstance(proba, pd.DataFrame) else np.asarray(proba, float)
    planet = p[:, 0] + p[:, 1]
    confirmed_first = p[:, 1] >= p[:, 0]
    out = np.where(
        planet < threshold, FALSE_POSITIVE, np.where(confirmed_first, CONFIRMED, CANDIDATE)
    )
    return out.astype(object)


def verdict_frame(proba: pd.DataFrame, threshold: float = PLANET_LIKE_THRESHOLD) -> pd.DataFrame:
    """The three probabilities plus ``p_planet_like`` and ``model_verdict``, same index."""
    out = proba[list(CLASSES)].copy()
    out["p_planet_like"] = planet_like(proba)
    out["model_verdict"] = verdict(proba, threshold)
    return out
