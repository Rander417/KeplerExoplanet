"""Kepler KOI explorer - the project's app.

Runs three ways from the same file:

* locally: double-click ``run_app.cmd`` (``uv run streamlit run app/app.py``)
* Streamlit Community Cloud: entrypoint ``app/app.py``, deps ``app/requirements.txt``
* in the browser via stlite (GitHub Pages): ``app/index.html`` mounts this file,
  the data, the model and the ``kepler`` modules it imports

Everything it shows is precomputed by ``python -m kepler.app_bundle`` into
``app/data`` and ``app/model``; the only live computation is the what-if panel,
which evaluates the exported model with numpy (``kepler.portable``).
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT / "src") not in sys.path:  # run without installing the package
    sys.path.insert(0, str(ROOT / "src"))

from kepler.habitable import TEFF_VALID, seff_limit
from kepler.palette import CLASS_COLORS, GRID, NEUTRAL, SURFACE, TEXT_PRIMARY, TEXT_SECONDARY
from kepler.portable import PortableHGB
from kepler.verdict import CLASSES, PLANET_LIKE_THRESHOLD, verdict

# --------------------------------------------------------------------------- setup
st.set_page_config(page_title="Kepler KOI explorer", page_icon="🔭", layout="wide")

CLASS_ORDER = ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]
SYMBOLS = {"CONFIRMED": "circle", "CANDIDATE": "triangle-up", "FALSE POSITIVE": "square"}
PHYSICS = {
    "koi_period": ("Orbital period", "days"),
    "koi_impact": ("Impact parameter", ""),
    "koi_duration": ("Transit duration", "hours"),
    "koi_depth": ("Transit depth", "ppm"),
    "koi_prad": ("Planet radius", "Earth radii"),
    "koi_teq": ("Equilibrium temperature", "K"),
    "koi_insol": ("Insolation", "Earth = 1"),
    "koi_model_snr": ("Transit signal-to-noise", ""),
    "koi_steff": ("Stellar temperature", "K"),
    "koi_slogg": ("Stellar surface gravity", "log g"),
    "koi_srad": ("Stellar radius", "Solar radii"),
    "koi_kepmag": ("Kepler magnitude", "mag"),
}
WHAT_IF = [  # the sliders in the explorer (log scale where the data spans decades)
    ("koi_prad", True),
    ("koi_model_snr", True),
    ("koi_period", True),
    ("koi_insol", True),
    ("koi_depth", True),
    ("koi_duration", False),
    ("koi_impact", False),
]
REPO = "https://github.com/Rander417/KeplerExoplanet"
NOTES = {  # verified literature notes for KOIs where the archive verdict has a story
    "K07016.01": (
        "**Kepler-452 b in the literature.** Mullally et al. 2018 (AJ 155, 210, "
        "[arXiv:1803.11307](https://arxiv.org/abs/1803.11307)) argue the planet "
        '"can not be confirmed using a purely statistical validation approach" and '
        '"should be considered a candidate planet" — a 50/50 physics verdict is not out of line.'
    ),
    "K03138.02": (
        "**Kepler-1649 c in the literature.** Vanderburg et al. 2020 (ApJL 893, L27, "
        '[arXiv:2004.06725](https://arxiv.org/abs/2004.06725)): "originally classified as a false '
        'positive by the Kepler pipeline, but was rescued as part of a systematic visual inspection"; '
        '1.06 R⊕ receiving "74 +/- 3 % the incident flux of Earth". The KOI table still carries the '
        "older stellar parameters (insolation 0.16), which is why it sits outside the zone here."
    ),
}
ARCHIVE = "https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html"


@st.cache_data(show_spinner="Loading the catalogue…")
def load_table() -> pd.DataFrame:
    df = pd.read_csv(HERE / "data" / "koi_table.csv", index_col="kepoi_name")
    df["label"] = [
        f"{k} · {n if isinstance(n, str) else 'unnamed'} · {d}"
        for k, n, d in zip(df.index, df["kepler_name"], df["koi_disposition"], strict=True)
    ]
    return df


@st.cache_data
def load_summary() -> dict:
    return json.loads((HERE / "data" / "summary.json").read_text(encoding="utf-8"))


@st.cache_resource(show_spinner="Loading the model…")
def load_model() -> PortableHGB:
    return PortableHGB.load(HERE / "model" / "hgb_physics_only.json")


def style(fig: go.Figure, height: int = 420) -> go.Figure:
    """House style for plotly: warm surface, recessive grid, title above a horizontal legend."""
    fig.update_layout(
        template="simple_white",
        height=height,
        margin={"l": 10, "r": 10, "t": 84, "b": 10},
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font={"color": TEXT_PRIMARY, "size": 13},
        title={
            "font": {"size": 15, "color": TEXT_PRIMARY},
            "x": 0,
            "xanchor": "left",
            "y": 0.98,
            "yanchor": "top",
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.0,
            "xanchor": "left",
            "x": 0,
            "title": None,
        },
        hoverlabel={"bgcolor": "white", "font_color": TEXT_PRIMARY},
    )
    fig.update_xaxes(gridcolor=GRID, showgrid=True, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, showgrid=True, zeroline=False, linecolor=GRID)
    return fig


def pct(x: float) -> str:
    return f"{100 * x:.0f}%"


def fmt(x, digits: int = 3) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{x:,.{digits}f}" if isinstance(x, float) else f"{x:,}"


table = load_table()
summary = load_summary()
model = load_model()
metrics = summary["metrics"]
live_src = summary["sources"]["live"]
pulled = (live_src.get("pulled_at_utc") or "")[:10]

# --------------------------------------------------------------------------- header
st.title("🔭 Kepler KOI explorer")
st.markdown(
    f"**{len(table):,} Kepler Objects of Interest**, their NASA Exoplanet Archive verdicts as of "
    f"**{pulled}**, a physics-only model that never sees the vetting flags, and the "
    f"habitable-zone screen. Every number here was computed by a script you can run; "
    f"nothing is trained in the app. [Source and notebooks]({REPO})."
)

tab_cat, tab_koi, tab_hz, tab_model, tab_about = st.tabs(
    ["Catalogue", "KOI explorer", "Habitable zone", "Model & honesty", "About"]
)

# --------------------------------------------------------------------------- 1 catalogue
with tab_cat:
    st.subheader("Browse the KOIs")
    f1, f2, f3, f4 = st.columns([2, 2, 2, 3])
    with f1:
        classes = st.multiselect("Archive verdict (today)", CLASS_ORDER, default=CLASS_ORDER)
    with f2:
        zone = st.selectbox(
            "Habitable zone",
            ["any", "conservative", "optimistic"],
            help="Kopparapu et al. 2014 limits",
        )
    with f3:
        radius_max = st.select_slider(
            "Max planet radius (Earth radii)",
            options=[1.0, 1.6, 2.0, 4.0, 10.0, 30.0, 1000.0],
            value=1000.0,
            format_func=lambda v: "no limit" if v == 1000.0 else f"≤ {v:g}",
        )
    with f4:
        changed_only = st.checkbox("Only KOIs whose verdict changed since 2020", value=False)
        search = st.text_input("Find by KOI or Kepler name", placeholder="K00752.01, Kepler-452…")

    view = table[table["koi_disposition"].isin(classes)]
    if zone == "conservative":
        view = view[view["hz_conservative"]]
    elif zone == "optimistic":
        view = view[view["hz_optimistic"]]
    if radius_max < 1000.0:
        view = view[view["koi_prad"] <= radius_max]
    if changed_only:
        view = view[view["koi_disposition"] != view["koi_disposition_2020"]]
    if search.strip():
        s = search.strip().lower()
        hit = view.index.str.lower().str.contains(s, regex=False) | view["kepler_name"].fillna(
            ""
        ).str.lower().str.contains(s, regex=False)
        view = view[hit]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("KOIs shown", f"{len(view):,}")
    for col, cls in zip((m2, m3, m4), CLASS_ORDER, strict=True):
        col.metric(cls.title(), f"{int((view['koi_disposition'] == cls).sum()):,}")

    if len(view):
        plot = view.reset_index()
        plot["Kepler name"] = plot["kepler_name"].fillna("—")
        fig = px.scatter(
            plot,
            x="koi_period",
            y="koi_prad",
            color="koi_disposition",
            symbol="koi_disposition",
            color_discrete_map=CLASS_COLORS,
            symbol_map=SYMBOLS,
            category_orders={"koi_disposition": CLASS_ORDER},
            log_x=True,
            log_y=True,
            hover_name="kepoi_name",
            hover_data={
                "Kepler name": True,
                "koi_disposition": True,
                "p_planet_like": ":.2f",
                "model_verdict": True,
                "koi_period": ":.3f",
                "koi_prad": ":.2f",
            },
            labels={
                "koi_period": "Orbital period (days, log)",
                "koi_prad": "Planet radius (Earth radii, log)",
                "koi_disposition": "verdict",
                "p_planet_like": "P(planet-like)",
                "model_verdict": "model verdict",
            },
            title="Period versus radius, coloured by today's archive verdict",
            opacity=0.55,
        )
        fig.update_traces(marker={"size": 7, "line": {"width": 0}})
        fig.data = fig.data[::-1]  # draw the 4,800 false positives first so planets stay visible
        fig.update_layout(legend_traceorder="reversed")
        st.plotly_chart(style(fig, 480), width="stretch")

        st.caption(
            "Probabilities are **out-of-fold**: the model that scored each KOI never saw its label. "
            "`model_verdict` applies the rule on the *Model & honesty* tab at the 0.5 threshold."
        )
        show_cols = [
            "kepler_name",
            "koi_disposition",
            "koi_disposition_2020",
            "model_verdict",
            "p_planet_like",
            "p_confirmed",
            "p_candidate",
            "p_false_positive",
            "koi_period",
            "koi_prad",
            "koi_insol",
            "koi_steff",
            "koi_model_snr",
            "hz_conservative",
            "hz_optimistic",
        ]
        st.dataframe(
            view[show_cols].rename(
                columns={
                    "kepler_name": "Kepler name",
                    "koi_disposition": "verdict (today)",
                    "koi_disposition_2020": "verdict (2020)",
                    "model_verdict": "model verdict",
                    "p_planet_like": "P(planet-like)",
                    "p_confirmed": "P(confirmed)",
                    "p_candidate": "P(candidate)",
                    "p_false_positive": "P(false positive)",
                    "koi_period": "period (d)",
                    "koi_prad": "radius (R⊕)",
                    "koi_insol": "insolation",
                    "koi_steff": "Teff (K)",
                    "koi_model_snr": "SNR",
                    "hz_conservative": "HZ cons.",
                    "hz_optimistic": "HZ opt.",
                }
            ),
            width="stretch",
            height=420,
        )
        buf = io.StringIO()
        view.drop(columns=["label"]).to_csv(buf)
        st.download_button(
            "Download these rows as CSV",
            data=buf.getvalue(),
            file_name=f"koi_selection_{pulled}.csv",
            mime="text/csv",
        )
    else:
        st.info("No KOIs match these filters.")

# --------------------------------------------------------------------------- 2 explorer
with tab_koi:
    st.subheader("One KOI, the model's view, and what-if sliders")
    default = "K07016.01" if "K07016.01" in table.index else table.index[0]  # Kepler-452 b
    options = list(table.index)
    choice = st.selectbox(
        "Pick a KOI (type to search)",
        options,
        index=options.index(default),
        format_func=lambda k: table.at[k, "label"],
    )
    row = table.loc[choice]

    c1, c2 = st.columns([1, 1])
    with c1:
        name = row["kepler_name"] if isinstance(row["kepler_name"], str) else "no Kepler name"
        st.markdown(f"### {choice} — {name}")
        st.markdown(
            f"- **Archive verdict today:** {row['koi_disposition']}  \n"
            f"- **Verdict in the 2020 snapshot:** {row['koi_disposition_2020']}  \n"
            f"- **Kepler pipeline verdict:** {row['koi_pdisposition']} "
            f"(score {fmt(row['koi_score'], 2)})  \n"
            f"- **Host star:** Teff {fmt(row['koi_steff'], 0)} K, radius {fmt(row['koi_srad'], 2)} R☉, "
            f"Kepler mag {fmt(row['koi_kepmag'], 1)}"
        )
        phys = pd.DataFrame(
            {
                "value": [row[c] for c in PHYSICS],
                "unit": [PHYSICS[c][1] for c in PHYSICS],
            },
            index=[PHYSICS[c][0] for c in PHYSICS],
        )
        st.dataframe(phys, width="stretch", height=460)

    with c2:
        st.markdown("#### The model's out-of-fold view (the honest number)")
        p_oof = pd.Series(
            {
                "CANDIDATE": row["p_candidate"],
                "CONFIRMED": row["p_confirmed"],
                "FALSE POSITIVE": row["p_false_positive"],
            }
        )
        thr = st.slider(
            "Planet-like threshold for the verdict rule",
            0.1,
            0.9,
            PLANET_LIKE_THRESHOLD,
            0.05,
            help="Below this P(planet-like) the rule says FALSE POSITIVE.",
        )
        oof_verdict = verdict(p_oof.to_frame().T[list(CLASSES)], thr)[0]
        k1, k2, k3 = st.columns(3)
        k1.metric("P(planet-like)", pct(row["p_planet_like"]))
        k2.metric("Rule verdict", oof_verdict)
        k3.metric("Archive says", row["koi_disposition"])
        bars = go.Figure(
            go.Bar(
                x=[p_oof[c] for c in CLASS_ORDER],
                y=CLASS_ORDER,
                orientation="h",
                marker_color=[CLASS_COLORS[c] for c in CLASS_ORDER],
                text=[pct(p_oof[c]) for c in CLASS_ORDER],
                textposition="outside",
                hovertemplate="%{y}: %{x:.3f}<extra></extra>",
            )
        )
        bars.update_layout(title="Calibrated probabilities (physics only)", xaxis_range=[0, 1.15])
        bars.update_xaxes(title="probability")
        bars.update_yaxes(autorange="reversed")
        st.plotly_chart(style(bars, 260), width="stretch")

        st.markdown("#### Habitable-zone check")
        if row["teff_in_range"]:
            inner, outer = row["seff_runaway_greenhouse"], row["seff_maximum_greenhouse"]
            inner_o, outer_o = row["seff_recent_venus"], row["seff_early_mars"]
            where = (
                "inside the **conservative** zone"
                if row["hz_conservative"]
                else "inside the **optimistic** zone only"
                if row["hz_optimistic"]
                else "outside the habitable zone"
            )
            size = (
                "plausibly rocky (≤ 1.6 R⊕)"
                if row["rocky"]
                else "super-Earth sized (≤ 2 R⊕)"
                if row["super_earth"]
                else "too large to be rocky (> 2 R⊕)"
            )
            st.markdown(
                f"Insolation **{fmt(row['koi_insol'], 2)}** Earth units → {where}; {size}.  \n"
                f"Zone edges for a {fmt(row['koi_steff'], 0)} K star: conservative "
                f"{fmt(inner, 3)} → {fmt(outer, 3)}, optimistic {fmt(inner_o, 3)} → {fmt(outer_o, 3)}."
            )
        else:
            st.markdown(
                "Host temperature is outside the 2,600–7,200 K range where the Kopparapu limits "
                "are defined, so no zone verdict."
            )

    if choice in NOTES:
        with st.container(border=True):
            st.markdown(NOTES[choice])

    st.markdown("---")
    st.markdown("#### What if the physics were different?")
    st.caption(
        "Move a slider and the exported model is re-evaluated with numpy. The starting point is "
        "the *full* model's estimate for the catalogue values (this KOI's label was in its "
        "training set, so read the **change**, not the level; the honest level is above). Fields "
        "are moved independently — this is a sensitivity probe, not a planet simulator."
    )
    base = table.loc[[choice], list(PHYSICS)].copy()
    edited = base.copy()
    slots = st.columns(4) + st.columns(3)
    for (col_name, is_log), widget in zip(WHAT_IF, slots, strict=True):
        label, unit = PHYSICS[col_name]
        value = row[col_name]
        title = f"{label} ({unit})" if unit else label
        with widget:
            if pd.isna(value):
                st.markdown(f"**{title}**  \nmissing in the catalogue")
                continue
            series = table[col_name].dropna()
            lo, hi = float(series.quantile(0.005)), float(series.quantile(0.995))
            if is_log and value > 0:
                grid = np.geomspace(max(lo, 1e-6), hi, 121)
            else:
                grid = np.linspace(lo, hi, 121)
            options = sorted({float(f"{g:.3g}") for g in grid} | {float(value)})
            picked = st.select_slider(
                title,
                options=options,
                value=float(value),
                format_func=lambda x: f"{x:,.3g}",
                key=f"whatif_{choice}_{col_name}",
            )
            edited.at[choice, col_name] = picked

    p_base = model.predict_frame(model.prepare(base)).iloc[0]
    p_new = model.predict_frame(model.prepare(edited)).iloc[0]
    v_base = verdict(p_base.to_frame().T[list(CLASSES)], thr)[0]
    v_new = verdict(p_new.to_frame().T[list(CLASSES)], thr)[0]
    planet_base = p_base["CANDIDATE"] + p_base["CONFIRMED"]
    planet_new = p_new["CANDIDATE"] + p_new["CONFIRMED"]
    change = 100 * (planet_new - planet_base)
    w1, w2, w3 = st.columns(3)
    w1.metric(
        "P(planet-like) with the edited values",
        pct(planet_new),
        delta=None if abs(change) < 0.5 else f"{change:+.0f} points vs the catalogue values",
    )
    w2.metric("Rule verdict, edited values", v_new)
    w3.metric("Rule verdict, catalogue values (full model)", v_base)
    comp = go.Figure()
    comp.add_bar(
        name="catalogue values",
        x=CLASS_ORDER,
        y=[p_base[c] for c in CLASS_ORDER],
        marker_color=NEUTRAL,
        hovertemplate="%{x}: %{y:.3f}<extra>catalogue</extra>",
    )
    comp.add_bar(
        name="edited values",
        x=CLASS_ORDER,
        y=[p_new[c] for c in CLASS_ORDER],
        marker_color=[CLASS_COLORS[c] for c in CLASS_ORDER],
        hovertemplate="%{x}: %{y:.3f}<extra>edited</extra>",
    )
    comp.update_layout(
        barmode="group", title="Calibrated probabilities before and after", yaxis_range=[0, 1]
    )
    st.plotly_chart(style(comp, 300), width="stretch")

    new_insol, teff = edited.at[choice, "koi_insol"], row["koi_steff"]
    if not pd.isna(new_insol) and not pd.isna(teff) and TEFF_VALID[0] <= teff <= TEFF_VALID[1]:
        inner, outer = (
            float(seff_limit(teff, "runaway_greenhouse")),
            float(seff_limit(teff, "maximum_greenhouse")),
        )
        inner_o, outer_o = (
            float(seff_limit(teff, "recent_venus")),
            float(seff_limit(teff, "early_mars")),
        )
        if outer <= new_insol <= inner:
            zone_msg = "inside the **conservative** habitable zone"
        elif outer_o <= new_insol <= inner_o:
            zone_msg = "inside the **optimistic** habitable zone only"
        else:
            zone_msg = "outside the habitable zone"
        st.markdown(
            f"With insolation {new_insol:,.3g} at this {teff:,.0f} K star the planet would sit {zone_msg} "
            f"(conservative {inner:.3f} → {outer:.3f})."
        )

# --------------------------------------------------------------------------- 3 habitable zone
with tab_hz:
    st.subheader("Small planets in the habitable zone")
    hz = summary["habitable_zone"]
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Confirmed, conservative zone, ≤ 2 R⊕", hz["confirmed_conservative_le_2"])
    h2.metric("…of which ≤ 1.6 R⊕ (plausibly rocky)", hz["confirmed_conservative_le_1_6"])
    h3.metric("Confirmed, optimistic zone, ≤ 2 R⊕", hz["confirmed_optimistic_le_2"])
    h4.metric("Candidates, conservative zone, ≤ 2 R⊕", hz["candidates_conservative_le_2"])
    st.markdown(
        "The zone is defined on **insolation** (how much starlight the planet receives) with the "
        "stellar-temperature-dependent limits of "
        "[Kopparapu et al. 2014](https://arxiv.org/abs/1404.5292) (Table 1, 1 Earth-mass planet): "
        "*conservative* = runaway greenhouse → maximum greenhouse, *optimistic* = recent Venus → "
        "early Mars. The radius ceiling follows [Rogers 2015](https://arxiv.org/abs/1407.4457): "
        "most planets above 1.6 R⊕ are not rocky. Limits are defined for 2,600–7,200 K hosts; "
        f"{hz['teff_out_of_range']} KOIs orbit stars outside that range and get no zone verdict."
    )

    small = table[
        table["super_earth"]
        & table["hz_optimistic"]
        & table["koi_disposition"].isin(["CONFIRMED", "CANDIDATE"])
    ]
    teff_grid = np.linspace(TEFF_VALID[0], TEFF_VALID[1], 120)
    fig = go.Figure()
    fills = [
        ("recent_venus", "early_mars", "optimistic zone", "rgba(224,138,0,0.12)"),
        ("runaway_greenhouse", "maximum_greenhouse", "conservative zone", "rgba(31,122,31,0.16)"),
    ]
    for inner_lim, outer_lim, label, color in fills:
        inner = seff_limit(teff_grid, inner_lim)
        outer = seff_limit(teff_grid, outer_lim)
        fig.add_trace(
            go.Scatter(
                x=np.concatenate([inner, outer[::-1]]),
                y=np.concatenate([teff_grid, teff_grid[::-1]]),
                fill="toself",
                fillcolor=color,
                line={"color": "rgba(0,0,0,0)"},
                name=label,
                hoverinfo="skip",
            )
        )
    for cls in ("CONFIRMED", "CANDIDATE"):
        sub = small[small["koi_disposition"] == cls].reset_index()
        sub["name"] = sub["kepler_name"].fillna(sub["kepoi_name"])
        fig.add_trace(
            go.Scatter(
                x=sub["koi_insol"],
                y=sub["koi_steff"],
                mode="markers",
                name=f"{cls.title()} (≤ 2 R⊕)",
                marker={
                    "color": CLASS_COLORS[cls],
                    "symbol": SYMBOLS[cls],
                    "size": 9,
                    "line": {"color": "white", "width": 1},
                },
                customdata=np.stack(
                    [sub["name"], sub["koi_prad"], sub["p_planet_like"], sub["koi_period"]], axis=1
                ),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>insolation %{x:.2f}, Teff %{y:.0f} K"
                    "<br>radius %{customdata[1]:.2f} R⊕, period %{customdata[3]:.1f} d"
                    "<br>P(planet-like) %{customdata[2]:.2f}<extra></extra>"
                ),
            )
        )
    fig.add_trace(
        go.Scatter(
            x=[1.0],
            y=[5772],
            mode="markers+text",
            marker={"color": TEXT_SECONDARY, "symbol": "star", "size": 12},
            text=["Earth"],
            textposition="middle right",
            name="Earth (for scale)",
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        title="Where the small confirmed planets and candidates sit in their stars' habitable zones",
        xaxis={
            "title": "Insolation (Earth = 1), hotter to the left",
            "type": "log",
            "autorange": "reversed",
        },
        yaxis={"title": "Host star temperature (K)"},
    )
    st.plotly_chart(style(fig, 520), width="stretch")

    st.markdown("#### Confirmed planets ≤ 2 R⊕ in the conservative zone")
    conf = table[
        (table["koi_disposition"] == "CONFIRMED") & table["hz_conservative"] & table["super_earth"]
    ].sort_values("koi_prad")
    hz_cols = {
        "kepler_name": "Kepler name",
        "koi_prad": "radius (R⊕)",
        "koi_insol": "insolation",
        "koi_steff": "Teff (K)",
        "koi_period": "period (d)",
        "koi_teq": "T_eq (K)",
        "rocky": "≤ 1.6 R⊕",
        "sunlike_host": "Sun-like host",
        "hz_conservative_possible": "in zone within errors",
    }
    st.dataframe(conf[list(hz_cols)].rename(columns=hz_cols), width="stretch")
    st.markdown("#### Candidates ≤ 2 R⊕ in the conservative zone, most planet-like first")
    cand = table[
        (table["koi_disposition"] == "CANDIDATE") & table["hz_conservative"] & table["super_earth"]
    ].sort_values("p_planet_like", ascending=False)
    cand_cols = {"p_planet_like": "P(planet-like)", "model_verdict": "model verdict"} | {
        k: v for k, v in hz_cols.items() if k != "kepler_name"
    }
    st.dataframe(cand[list(cand_cols)].rename(columns=cand_cols), width="stretch", height=360)
    st.caption(
        "A KOI's insolation and host temperature come from the KOI table's own stellar parameters "
        "(Kepler DR25). Discovery papers sometimes revise them: Kepler-1649 c, for example, is a "
        "confirmed habitable-zone planet in the literature but sits outside the zone on the KOI "
        "table's numbers."
    )

# --------------------------------------------------------------------------- 4 model & honesty
with tab_model:
    st.subheader("What the model is, and what it is not")
    cv = metrics["cv_macro_f1_physics_only"]
    cvf = metrics.get("cv_macro_f1_with_flags")
    oot = metrics["out_of_time"]
    a1, a2, a3, a4 = st.columns(4)
    a1.metric(
        "Physics-only macro f1",
        f"{cv['mean']:.3f} ± {cv['std']:.3f}",
        help="5-fold CV, today's labels",
    )
    if cvf:
        a2.metric(
            "…with the vetting flags",
            f"{cvf['mean']:.3f} ± {cvf['std']:.3f}",
            help="The flags are outputs of the vetting that produced the labels: target leakage.",
        )
    a3.metric(
        "Out-of-time AUC",
        f"{oot['auc_confirmed_vs_false_positive']:.3f}",
        help="2020 model vs later verdicts",
    )
    a4.metric(
        "Planet-like AUC",
        f"{metrics['planet_like']['auc']:.3f}",
        help="out-of-fold, today's labels",
    )

    st.markdown(
        f"""
**Target.** `koi_disposition`, the archive's verdict (CONFIRMED / CANDIDATE / FALSE POSITIVE) —
not `koi_pdisposition`, the Kepler pipeline's two-class verdict.

**Features.** Twelve physical columns only (period, impact, duration, depth, radius, equilibrium
temperature, insolation, transit SNR, stellar temperature, gravity, radius, magnitude) plus
"is this value missing" indicators. **No vetting flags, no `koi_score`.** The four `koi_fpflag_*`
columns are written by the same vetting that decides the label; between the 2020 snapshot and
today they were rewritten wherever the verdict changed, which is why a model that uses them
scores {cvf["mean"]:.2f} on today's labels and looks brilliant while learning nothing about planets.

**Model.** Histogram gradient boosting (scikit-learn {summary["versions"]["scikit-learn"]}),
hyperparameters chosen by nested cross-validation in notebook 07, trained on all
{metrics["n_rows"]:,} KOIs with today's labels, then calibrated with isotonic maps fit on
out-of-fold scores. Exported to plain numbers and evaluated here with numpy; the export is checked
to reproduce scikit-learn exactly (max difference {summary["model"]["export_check_max_abs_diff_vs_sklearn"]:.0e}).

**The label rule** (instead of a hidden argmax): `P(planet-like) = P(CANDIDATE) + P(CONFIRMED)`;
below the threshold the verdict is FALSE POSITIVE, otherwise the larger of CONFIRMED and CANDIDATE.
Physics separates planets from false positives well; it separates *confirmed* from *candidate* only
moderately, because confirmation is a follow-up-and-statistics process rather than a measurement.
"""
    )

    r1, r2 = st.columns(2)
    with r1:
        conf_m = np.array(metrics["rule_confusion"]["matrix"])
        classes = metrics["rule_confusion"]["classes"]
        heat = go.Figure(
            go.Heatmap(
                z=conf_m,
                x=[f"rule: {c}" for c in classes],
                y=[f"true: {c}" for c in classes],
                colorscale="YlOrBr",
                text=conf_m,
                texttemplate="%{text:,}",
                showscale=False,
                hovertemplate="%{y} → %{x}: %{z:,}<extra></extra>",
            )
        )
        heat.update_layout(title="Out-of-fold confusion matrix of the rule (threshold 0.5)")
        heat.update_yaxes(autorange="reversed")
        st.plotly_chart(style(heat, 380), width="stretch")
        per = metrics["rule_per_class_f1"]
        st.markdown(
            "Per-class f1: " + ", ".join(f"**{c}** {per[c]:.2f}" for c in CLASS_ORDER) + "."
        )
    with r2:
        rel = pd.DataFrame(metrics["calibration"]["reliability_planet_like"])
        relfig = go.Figure()
        relfig.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                line={"color": GRID, "width": 2, "dash": "dot"},
                name="perfect calibration",
                hoverinfo="skip",
            )
        )
        relfig.add_trace(
            go.Scatter(
                x=rel["mean_predicted"],
                y=rel["observed"],
                mode="lines+markers",
                marker={"size": np.clip(rel["n"] / 60, 6, 22), "color": CLASS_COLORS["CONFIRMED"]},
                line={"color": CLASS_COLORS["CONFIRMED"], "width": 2},
                name="P(planet-like), out-of-fold",
                customdata=rel["n"],
                hovertemplate="predicted %{x:.2f} → observed %{y:.2f} (n = %{customdata:,})<extra></extra>",
            )
        )
        relfig.update_layout(
            title="Reliability: predicted P(planet-like) versus what happened",
            xaxis={"title": "mean predicted probability", "range": [0, 1]},
            yaxis={"title": "fraction that are planets", "range": [0, 1]},
        )
        st.plotly_chart(style(relfig, 380), width="stretch")
        cal = metrics["calibration"]
        st.markdown(
            f"Calibration lowers log loss {cal['log_loss_uncalibrated']:.3f} → "
            f"**{cal['log_loss_calibrated']:.3f}** and the Brier score "
            f"{cal['brier_uncalibrated']:.3f} → **{cal['brier_calibrated']:.3f}**; the argmax "
            f"macro f1 moves {metrics['oof_macro_f1']['uncalibrated_argmax']:.3f} → "
            f"{metrics['oof_macro_f1']['calibrated_argmax']:.3f} (rule: "
            f"{metrics['oof_macro_f1']['rule']:.3f}). Marker size = KOIs in the bin."
        )

    st.markdown("#### Choosing the threshold")
    thr_tab = pd.DataFrame(metrics["planet_like"]["thresholds"]).rename(
        columns={
            "threshold": "P(planet-like) ≥",
            "precision": "precision (planet-like)",
            "recall": "recall (planet-like)",
            "f1": "f1",
            "n_planet_like": "KOIs called planet-like",
        }
    )
    st.dataframe(thr_tab.round(3), width="stretch", hide_index=True)

    st.markdown("#### The out-of-time test (2020 question 3: can future observers use this?)")
    st.markdown(
        f"The same model trained on the **2020 labels only**, out-of-fold, scored the "
        f"{oot['n_candidates_2020']:,} KOIs that were CANDIDATEs in 2020. Since then the archive has "
        f"confirmed **{oot['later']['CONFIRMED']}** of them and dismissed **{oot['later']['FALSE POSITIVE']}**; "
        f"{oot['later']['CANDIDATE']:,} are still open. The model never saw those later verdicts, "
        f"yet it had rated the later-confirmed ones far more planet-like (median "
        f"{oot['median_p_planet_like']['CONFIRMED']:.2f}) than the later-dismissed ones (median "
        f"{oot['median_p_planet_like']['FALSE POSITIVE']:.2f}): **AUC {oot['auc_confirmed_vs_false_positive']:.3f}**. "
        f"The vetting flags could not have passed this test — they were rewritten along with the verdicts."
    )
    was = table[table["koi_disposition_2020"] == "CANDIDATE"].reset_index()
    was["later"] = was["koi_disposition"].map(
        {
            "CONFIRMED": "later CONFIRMED",
            "CANDIDATE": "still CANDIDATE",
            "FALSE POSITIVE": "later FALSE POSITIVE",
        }
    )
    order = ["later CONFIRMED", "still CANDIDATE", "later FALSE POSITIVE"]
    colors = {
        "later CONFIRMED": CLASS_COLORS["CONFIRMED"],
        "still CANDIDATE": CLASS_COLORS["CANDIDATE"],
        "later FALSE POSITIVE": CLASS_COLORS["FALSE POSITIVE"],
    }
    oot_fig = px.histogram(
        was,
        x="p_planet_like_2020model",
        color="later",
        color_discrete_map=colors,
        category_orders={"later": order},
        nbins=20,
        barmode="group",
        histnorm="percent",
        labels={
            "p_planet_like_2020model": "P(planet-like) from the model trained on 2020 labels",
            "later": "",
        },
        title="What the 2020-trained model thought of the 2020 candidates, split by what happened next",
    )
    oot_fig.update_yaxes(title="share of the group (%)")
    st.plotly_chart(style(oot_fig, 380), width="stretch")

    tr = summary["transitions"]
    trm = pd.DataFrame(
        tr["matrix"],
        index=[f"2020: {c}" for c in tr["classes"]],
        columns=[f"today: {c}" for c in tr["classes"]],
    )
    st.markdown("#### What the archive changed since the 2020 snapshot")
    st.dataframe(trm, width="stretch")
    st.caption(
        "Rows: verdict in the 2020 (Kaggle-era) snapshot; columns: verdict today. Off-diagonal cells are "
        "the changes. The physics columns are identical in both tables."
    )

# --------------------------------------------------------------------------- 5 about
with tab_about:
    st.subheader("Provenance, method, credits")
    snap_src = summary["sources"]["snapshot"]
    st.markdown(
        f"""
**Data.** NASA Exoplanet Archive, [KOI cumulative table]({ARCHIVE}), pulled with the archive's
TAP service on **{live_src.get("pulled_at_utc", "—")}** (`{live_src["file"]}`, SHA-256
`{(live_src.get("sha256") or "")[:16]}…`). The 2020 comparison uses the Kaggle-era snapshot
(`{snap_src["file"]}`, SHA-256 `{snap_src["sha256"][:16]}…`). Both files are tracked in the repository,
so every number here can be regenerated.

**How this app is built.** `uv run python -m kepler.app_bundle` trains the model, scores every
KOI out-of-fold, runs the out-of-time test and the habitable-zone screen, and writes
`app/data/koi_table.csv`, `app/data/summary.json` and `app/model/hgb_physics_only.json`
(built {summary["built_at_utc"]}, Python {summary["versions"]["python"]}, scikit-learn
{summary["versions"]["scikit-learn"]}, pandas {summary["versions"]["pandas"]}). The app reads
those files and nothing else; when it runs in your browser it does so entirely on your machine.

**Science references.**
[Kopparapu et al. 2014, *ApJL* 787, L29](https://arxiv.org/abs/1404.5292) — habitable-zone
insolation limits as a function of stellar temperature (Table 1).
[Rogers 2015, *ApJ* 801, 41](https://arxiv.org/abs/1407.4457) — "the majority of 1.6 Earth-radius
planets are too low density to be comprised of Fe and silicates alone".
[NASA Exoplanet Archive KOI table documentation]({ARCHIVE}) — column definitions and the meaning of
the dispositions and flags.

**Project.** Started in 2020 as a Columbia Engineering data-analytics bootcamp team project
(Rich Anderson — ML pipeline; Damien Corr, Priscilla Lin, Tom Greff). Restarted in 2026 with
corrected science: leakage-free models, an insolation-based habitable zone, live archive data,
and this app. Code, notebooks and the research log: [{REPO.replace("https://", "")}]({REPO}).

*This is an educational analysis of public data, not a product of NASA or the Exoplanet Archive.
Verdicts are the archive's; probabilities are ours.*
"""
    )
