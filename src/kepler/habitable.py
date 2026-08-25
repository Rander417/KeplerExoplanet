"""Habitable-zone screening on insolation, the way the literature defines it.

The 2020 project filtered on orbital period and stellar properties and never
looked at the planet. This module implements the stellar-temperature-dependent
insolation limits of Kopparapu et al. (2014, ApJL 787, L29; arXiv:1404.5292),
Table 1, for a 1 Earth-mass planet::

    S_eff = S_eff_sun + a*T + b*T**2 + c*T**3 + d*T**4,   T = Teff - 5780 K

valid for 2600 K <= Teff <= 7200 K. A planet is inside a limit pair when its
``koi_insol`` (stellar flux at the planet, Earth = 1) lies between the inner and
outer S_eff. "Conservative" = runaway greenhouse .. maximum greenhouse;
"optimistic" = recent Venus .. early Mars.

Planet-radius ceiling: Rogers (2015, ApJ 801, 41; arXiv:1407.4457) finds that
"the majority of 1.6 Earth-radius planets are too low density to be comprised of
Fe and silicates alone", so 1.6 R_earth is the "plausibly rocky" cut and 2.0 the
looser super-Earth cut used for comparison.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from kepler.data import TARGET, load_stellar_extra

TEFF_SUN = 5780.0  # the reference temperature used by Kopparapu et al.
TEFF_VALID = (2600.0, 7200.0)

# limit -> (S_eff_sun, a, b, c, d), Kopparapu et al. 2014 Table 1, 1 Earth-mass planet
KOPPARAPU_2014 = {
    "recent_venus": (1.776, 2.136e-4, 2.533e-8, -1.332e-11, -3.097e-15),
    "runaway_greenhouse": (1.107, 1.332e-4, 1.580e-8, -8.308e-12, -1.931e-15),
    "maximum_greenhouse": (0.356, 6.171e-5, 1.698e-9, -3.198e-12, -5.575e-16),
    "early_mars": (0.320, 5.547e-5, 1.526e-9, -2.874e-12, -5.011e-16),
}
CONSERVATIVE = ("runaway_greenhouse", "maximum_greenhouse")
OPTIMISTIC = ("recent_venus", "early_mars")

ROCKY_RADIUS = 1.6  # Earth radii, Rogers 2015
SUPER_EARTH_RADIUS = 2.0
SUNLIKE_TEFF = (5500.0, 6500.0)  # the 2020 project's "Sun-like" window, kept as a flag


def seff_limit(teff, limit: str):
    """Effective flux at ``limit`` for stars of temperature ``teff`` (array-friendly).

    Returns NaN outside the 2600-7200 K validity range instead of extrapolating.
    """
    s0, a, b, c, d = KOPPARAPU_2014[limit]
    teff = np.asarray(teff, dtype=float)
    t = teff - TEFF_SUN
    s = s0 + a * t + b * t**2 + c * t**3 + d * t**4
    return np.where((teff >= TEFF_VALID[0]) & (teff <= TEFF_VALID[1]), s, np.nan)


def hz_table(raw: pd.DataFrame) -> pd.DataFrame:
    """Per-KOI habitable-zone flags computed from the raw snapshot (needs the error columns).

    Columns added:
      seff_<limit>            the four Kopparapu limits at the host star's Teff
      teff_in_range           Teff inside 2600-7200 K (limits are NaN otherwise)
      hz_conservative         runaway greenhouse >= koi_insol >= maximum greenhouse
      hz_optimistic           recent Venus >= koi_insol >= early Mars
      hz_conservative_possible  same test using koi_insol +/- its catalogue errors
      rocky                   koi_prad <= 1.6
      super_earth             koi_prad <= 2.0
      sunlike_host            5500 <= Teff <= 6500
      grazing                 koi_impact >= 1 (radius unreliable)
    """
    df = raw.copy()
    teff = df["koi_steff"]
    for limit in KOPPARAPU_2014:
        df[f"seff_{limit}"] = seff_limit(teff, limit)
    df["teff_in_range"] = teff.between(*TEFF_VALID)
    insol = df["koi_insol"]
    inner_c, outer_c = df[f"seff_{CONSERVATIVE[0]}"], df[f"seff_{CONSERVATIVE[1]}"]
    inner_o, outer_o = df[f"seff_{OPTIMISTIC[0]}"], df[f"seff_{OPTIMISTIC[1]}"]
    df["hz_conservative"] = (insol <= inner_c) & (insol >= outer_c)
    df["hz_optimistic"] = (insol <= inner_o) & (insol >= outer_o)
    # err1 is the upper (positive) uncertainty, err2 the lower (negative) one
    insol_high = insol + df["koi_insol_err1"].fillna(0)
    insol_low = insol + df["koi_insol_err2"].fillna(0)
    df["hz_conservative_possible"] = (insol_low <= inner_c) & (insol_high >= outer_c)
    df["rocky"] = df["koi_prad"] <= ROCKY_RADIUS
    df["super_earth"] = df["koi_prad"] <= SUPER_EARTH_RADIUS
    df["sunlike_host"] = teff.between(*SUNLIKE_TEFF)
    df["grazing"] = df["koi_impact"] >= 1.0
    for col in (
        "hz_conservative",
        "hz_optimistic",
        "hz_conservative_possible",
        "rocky",
        "super_earth",
        "sunlike_host",
        "grazing",
    ):
        df[col] = df[col].fillna(False).astype(bool)
    return df


def summarise(hz: pd.DataFrame, disposition: str = "CONFIRMED") -> pd.DataFrame:
    """Counts of KOIs of one disposition inside each zone, by radius cut and host type."""
    sub = hz[hz[TARGET] == disposition]
    rows = {}
    for zone in ("hz_conservative", "hz_optimistic"):
        z = sub[sub[zone]]
        rows[zone] = {
            "any radius": len(z),
            f"radius <= {SUPER_EARTH_RADIUS}": int(z["super_earth"].sum()),
            f"radius <= {ROCKY_RADIUS}": int(z["rocky"].sum()),
            f"radius <= {SUPER_EARTH_RADIUS}, Sun-like host": int(
                (z["super_earth"] & z["sunlike_host"]).sum()
            ),
            f"radius <= {SUPER_EARTH_RADIUS}, cooler host": int(
                (z["super_earth"] & ~z["sunlike_host"]).sum()
            ),
        }
    return pd.DataFrame(rows).T


def legacy_2020_box(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """The 2020 notebook-05 filter, reproduced: 200 < period < 400 d, 5500 < Teff < 6500 K,
    stellar radius <= 2 R_sun, metallicity > 0, applied after an inner join with the
    stellar file. Returns the joined table with a ``legacy_box`` flag and join statistics.
    """
    stellar = load_stellar_extra()
    joined = raw.join(stellar[["koi_smet", "koi_smass"]], on="kepid", how="left")
    stats = {
        "kois": len(joined),
        "without stellar extra": int(joined["koi_smet"].isna().sum()),
    }
    joined["legacy_box"] = (
        joined["koi_period"].between(200, 400, inclusive="neither")
        & joined["koi_steff"].between(5500, 6500, inclusive="neither")
        & (joined["koi_srad"] <= 2.0)
        & (joined["koi_smet"] > 0)
    ).fillna(False)
    return joined, stats
