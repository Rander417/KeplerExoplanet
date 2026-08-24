"""Project-wide chart styling.

House rule: no blue except for natural subjects (sky, water). The three
disposition classes get a fixed hue each, in fixed order, plus a marker shape
so identity never rests on colour alone. Palette validated 2026-08-24 with the
dataviz palette checker (all-pairs, light surface): CVD separation 12.1,
normal-vision separation 27.5; amber is below 3:1 contrast on white, so charts
always carry a legend or direct labels.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler

CLASS_COLORS = {
    "CONFIRMED": "#1f7a1f",  # green
    "CANDIDATE": "#e08a00",  # amber
    "FALSE POSITIVE": "#8b1e5f",  # plum
}
CLASS_MARKERS = {"CONFIRMED": "o", "CANDIDATE": "^", "FALSE POSITIVE": "s"}
CLASS_ORDER = ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]

# Extra categorical slots for anything beyond the three classes (still no blue).
EXTRA_COLORS = ["#6b4c2a", "#c2452d", "#5a5a52", "#a86bb5"]

SEQUENTIAL_CMAP = "YlOrBr"  # one warm hue, light -> dark, for magnitudes
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e6e4dd"
SURFACE = "#fcfcfb"


def apply_style() -> None:
    """Set matplotlib defaults for the project (call once per notebook)."""
    colors = [CLASS_COLORS[c] for c in CLASS_ORDER] + EXTRA_COLORS
    mpl.rcParams.update(
        {
            "axes.prop_cycle": cycler(color=colors),
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "axes.edgecolor": GRID,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "axes.axisbelow": True,
            "text.color": TEXT_PRIMARY,
            "axes.labelcolor": TEXT_SECONDARY,
            "xtick.color": TEXT_SECONDARY,
            "ytick.color": TEXT_SECONDARY,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "legend.frameon": False,
            "legend.fontsize": 9,
            "lines.linewidth": 2,
            "lines.markersize": 5,
            "figure.dpi": 110,
            "savefig.dpi": 160,
            "savefig.bbox": "tight",
            "image.cmap": SEQUENTIAL_CMAP,
        }
    )


def class_color(disposition: str) -> str:
    return CLASS_COLORS[disposition]


def new_figure(width: float = 8, height: float = 4.5):
    """A figure/axes pair with the project style applied."""
    apply_style()
    return plt.subplots(figsize=(width, height))
