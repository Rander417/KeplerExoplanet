"""Project-wide chart styling for matplotlib.

The colours themselves live in ``kepler.palette`` (no plotting imports, so the
app can use them in a browser) and are re-exported here; this module adds the
matplotlib rcParams. House rule: no blue except for natural subjects.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler

from kepler.palette import (  # noqa: F401  (re-exported for the notebooks)
    CLASS_COLORS,
    CLASS_MARKERS,
    CLASS_ORDER,
    EXTRA_COLORS,
    FEATURE_SET_COLORS,
    GRID,
    NEUTRAL,
    SEQUENTIAL_CMAP,
    SURFACE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


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
