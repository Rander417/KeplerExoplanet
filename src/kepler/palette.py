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


# --- Theme-aware sets for the app (plotly) -----------------------------------------------
# Both validated with the dataviz palette checker on their own surface (2026-08-25):
#   light: surface #fcfcfb, CVD separation 12.1, normal-vision 27.5 (amber needs labels: 2.6:1)
#   dark:  surface #15140f, CVD separation 8.6, normal-vision 23.5, every colour >= 3:1
# The dark set keeps the same three hues, re-stepped for the dark surface; marker shapes
# (circle / triangle / square) remain the secondary encoding in both.
THEMES = {
    "light": {
        "surface": SURFACE,
        "surface_secondary": "#f3f1ea",
        "text": TEXT_PRIMARY,
        "text_secondary": TEXT_SECONDARY,
        "grid": GRID,
        "classes": dict(CLASS_COLORS),
        "neutral": NEUTRAL,
        "link": "#8b1e5f",
        "primary": "#b86200",
        "fill_optimistic": "rgba(224,138,0,0.12)",
        "fill_conservative": "rgba(31,122,31,0.16)",
        "sequential": "YlOrBr",
    },
    "dark": {
        "surface": "#15140f",
        "surface_secondary": "#23211a",
        "text": "#f2f0e8",
        "text_secondary": "#b8b4a6",
        "grid": "#33302a",
        "classes": {"CONFIRMED": "#1f7a1f", "CANDIDATE": "#cc8016", "FALSE POSITIVE": "#b8489a"},
        "neutral": "#8a877c",
        "link": "#e6a4d2",
        "primary": "#e08a00",
        "fill_optimistic": "rgba(204,128,22,0.22)",
        "fill_conservative": "rgba(31,122,31,0.30)",
        "sequential": "YlOrBr",
    },
}
