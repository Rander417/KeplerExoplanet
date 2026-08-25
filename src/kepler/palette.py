"""The project palette, with no plotting-library imports so the app can use it in a browser.

House rule: no blue except for natural subjects (sky, water). The three
disposition classes get a fixed hue each, in fixed order, plus a marker shape
so identity never rests on colour alone. Palette validated 2026-08-24 with the
dataviz palette checker (all-pairs, light surface): CVD separation 12.1,
normal-vision separation 27.5; amber is below 3:1 contrast on white, so charts
always carry a legend or direct labels. ``kepler.viz`` re-exports these for
matplotlib and adds the rcParams styling.
"""

CLASS_COLORS = {
    "CONFIRMED": "#1f7a1f",  # green
    "CANDIDATE": "#e08a00",  # amber
    "FALSE POSITIVE": "#8b1e5f",  # plum
}
CLASS_MARKERS = {"CONFIRMED": "o", "CANDIDATE": "^", "FALSE POSITIVE": "s"}
CLASS_ORDER = ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]

# Extra categorical slots for anything beyond the three classes (still no blue).
EXTRA_COLORS = ["#6b4c2a", "#c2452d", "#5a5a52", "#a86bb5"]

# Feature sets are ordinal by how much of the answer they contain, so they get one
# warm hue in three lightness steps (validated as an ordinal ramp): the honest set is
# darkest.
FEATURE_SET_COLORS = {
    "legacy_2020": "#d9a066",
    "with_flags": "#b86200",
    "physics_only": "#5c3300",
}
NEUTRAL = "#5a5a52"

SEQUENTIAL_CMAP = "YlOrBr"  # one warm hue, light -> dark, for magnitudes
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e6e4dd"
SURFACE = "#fcfcfb"
