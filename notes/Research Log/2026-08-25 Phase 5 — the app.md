---
tags: [research-log, app, phase-5, deployment]
date: 2026-08-25
---

# 2026-08-25 Phase 5 — the app

> [!success] Outcome
> A five-tab Streamlit app (`app/app.py`) that runs locally, on Streamlit Community Cloud, and **inside the browser** via stlite on GitHub Pages, from one file. The model travels as plain numbers (`kepler.portable`), the catalogue carries out-of-fold calibrated probabilities from a model trained on **today's labels**, and the label rule is explicit (`kepler.verdict`). 41 tests pass. Architecture: [decision](../Decisions/2026-08-25%20App%20architecture%20—%20portable%20model,%20stlite%20on%20GitHub%20Pages.md).

## The bundle (`python -m kepler.app_bundle`, ~2.5 min)

Physics-only HGB, notebook-07 parameters (`learning_rate 0.05, max_leaf_nodes 31, min_samples_leaf 20`), live labels from `cumulative_tap_2026-08-25.csv` (SHA-256 `37fffa14…`), 96 boosting iterations, 17,568 tree nodes, 640 KB JSON. Export check against `CalibratedClassifierCV(method="isotonic", cv=5, ensemble=False)`: max |Δp| = **0.0**.

| quantity (5-fold, live labels) | value |
|---|---|
| macro f1, physics only | **0.747 ± 0.012** (same as notebook 08) |
| macro f1, physics + the four vetting flags | **0.901 ± 0.007** — on the snapshot labels it was 0.862; the flags were rewritten with the verdicts, so the leak grew |
| out-of-fold macro f1: uncalibrated argmax / calibrated argmax / rule | 0.747 / 0.741 / **0.744** |
| rule per-class f1 | CANDIDATE 0.55 · CONFIRMED 0.84 · FALSE POSITIVE 0.84 |
| log loss, uncalibrated → calibrated | 0.534 → **0.512** |
| Brier (multiclass), uncalibrated → calibrated | 0.315 → **0.297** |
| P(planet-like) AUC (planet vs false positive) | **0.921** |
| P(planet-like) ≥ 0.5: precision / recall | 0.848 / 0.823 (4,586 KOIs called planet-like) |
| out-of-time AUC (2020-label model, later-confirmed vs later-dismissed 2020 candidates) | **0.937** (same as notebook 08) |
| HZ, confirmed ≤ 2 R⊕ conservative / ≤ 1.6 / optimistic | 16 / 9 / 25; candidates ≤ 2 R⊕ conservative 65 |

The reliability curve of P(planet-like) is close to the diagonal (bins 0.5–1.0 within 0.04; the lowest bins predict slightly high: 0.04 predicted vs 0.02 observed). The isotonic maps were fit on the same out-of-fold scores, so those calibrated numbers are mildly optimistic for the calibrator itself — stated in the app.

## Famous cases the app now annotates (verified sources)

- **Kepler-452 b** (K07016.01): the model says 50/50 (rule: CANDIDATE) while the archive says CONFIRMED. Mullally et al. 2018, AJ 155, 210 ([arXiv:1803.11307](https://arxiv.org/abs/1803.11307)): the planet "can not be confirmed using a purely statistical validation approach" and "should be considered a candidate planet". Chosen as the explorer's default KOI for exactly that reason.
- **Kepler-1649 c** (K03138.02): Vanderburg et al. 2020, ApJL 893, L27 ([arXiv:2004.06725](https://arxiv.org/abs/2004.06725)): "originally classified as a false positive by the Kepler pipeline, but was rescued as part of a systematic visual inspection"; 1.06 R⊕ receiving "74 +/- 3 % the incident flux of Earth". The KOI table still says insolation 0.16, so it sits outside the zone in our screen.

## Browser verification (headless Chromium, everything served locally)

stlite `@stlite/browser` **1.8.1** (npm latest; the README's 0.85.1 is stale) bundles Streamlit **1.57.0** and loads **Pyodide 0.29.3** (Python 3.13; numpy 2.2.5, pandas 2.3.3 — the same pandas as our lock file). The sandbox blocks jsDelivr, so the stlite package (npm tarball) and the Pyodide distribution (392 MB GitHub release) were served from `localhost`, with the `?pyodide=` override in `index.html`; plotly came from PyPI through micropip.

- App rendered **27 s** after page load; all five tabs, **0 exceptions**; plotly 6 installed without the altair conflict the stlite README warns about.
- The what-if panel works in the browser as locally (SNR 12.3 → 841 moves Kepler-452 b's P(planet-like) 47% → 70%, verdict → CONFIRMED).
- `st.download_button` delivered the 3.4 MB CSV (checked with an actual download). A harmless `stlite.invalid/media` prefetch error appears in the console.
- Local Streamlit 1.62.0 renders the same; `width="stretch"` is used everywhere (both versions post-date the 1.49 API change).

Real visitors download about 30 MB from jsDelivr on the first visit (Pyodide core + numpy + pandas + Streamlit); expect roughly a minute.

## What Rich has to approve (one time)

1. Settings → Pages → Source: **GitHub Actions**.
2. Settings → Environments → `github-pages` → Deployment branches: add **`refresh-2026`** (or merge to `main`). Claude Code can do both via `gh api`.

Then the workflow `.github/workflows/pages.yml` publishes on every push that touches `app/` or `src/kepler/`, and the README placeholder becomes `https://rander417.github.io/KeplerExoplanet/`.

## Built

- `src/kepler/portable.py` (+ `tests/test_portable.py`, 4 tests), `src/kepler/verdict.py`, `src/kepler/palette.py` (split from `viz.py`), `src/kepler/app_bundle.py`
- `app/app.py`, `app/index.html`, `app/build_site.py`, `app/requirements.txt`, `app/data/*`, `app/model/*`
- `.streamlit/config.toml`, `run_app.cmd`, `.github/workflows/pages.yml`, `tests/test_app.py` (5 tests incl. Streamlit `AppTest` and a quick end-to-end bundle build)
- README rewritten; the 2020 text moved to `archive/README_2020.md`
