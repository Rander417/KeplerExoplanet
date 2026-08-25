---
tags: [decision, app, deployment, phase-5]
date: 2026-08-25
status: accepted
---

# 2026-08-25 App architecture — portable model, stlite on GitHub Pages

## Decisions

1. **The app never trains and never imports scikit-learn.** `python -m kepler.app_bundle` trains the notebook-07 physics-only model on the live labels, calibrates it, scores every KOI out-of-fold, and writes three tracked files: `app/data/koi_table.csv`, `app/data/summary.json`, `app/model/hgb_physics_only.json`. The model file is the fitted trees and isotonic maps as plain numbers; `kepler.portable` evaluates it with numpy, and `tests/test_portable.py` checks it reproduces scikit-learn's `predict_proba` to 1e-12 (the bundle build re-checks this against `CalibratedClassifierCV(ensemble=False)` and refuses to write if they differ).
2. **Primary deployment: stlite on GitHub Pages** (`app/index.html`, `.github/workflows/pages.yml`, `app/build_site.py`). Streamlit runs inside the visitor's browser on Pyodide; the site is static files under Rich's own `github.io` address, so there is no server, no account, nothing to download, and nothing that sleeps. **Optional: Streamlit Community Cloud** (`app/requirements.txt` sits next to the entrypoint so it takes precedence over the repo-root `uv.lock`, per the [Community Cloud dependency rules](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies): "Community Cloud will search the directory where your entrypoint file is, then it will search the root of your repository"). Rich deploys that one himself if he wants it.
3. **Locally:** `run_app.cmd` at the repo root runs `uv run streamlit run app/app.py`. `streamlit` joins the main dependencies so one `uv sync --group dev` covers everything.
4. **The label rule lives in code** (`kepler.verdict`): `P(planet-like) = P(CANDIDATE) + P(CONFIRMED)`; below 0.5 the verdict is FALSE POSITIVE, otherwise the larger of CONFIRMED / CANDIDATE. The app shows the calibrated probabilities and the rule; the threshold is a slider.
5. **Catalogue probabilities are out-of-fold**, from the live-label model; the what-if panel uses the full model and says so (its starting level is in-sample for that KOI; the change is what to read).
6. **Browser-safe modules.** `kepler.palette` was split out of `kepler.viz` (which imports matplotlib) so the app can share the palette; `tests/test_app.py` imports every module that `index.html` mounts with scikit-learn, matplotlib, imbalanced-learn and scipy blocked.
7. **Dark mode is a paired theme, not a toggle we maintain.** `[theme.light]` / `[theme.dark]` in `.streamlit/config.toml` (and the same keys in `app/index.html`) follow the visitor's system preference; the charts read `st.context.theme.type` and use `kepler.palette.THEMES`, whose dark set was validated on its own surface (2026-08-25). Streamlit's blue `st.info` callout is avoided (house rule).

## Context

Phase 5 of the [Roadmap](../Roadmap.md); the deliverable shape was agreed 2026-08-24 ([decision](2026-08-24%20Tag%20team,%20git%20autonomy,%20and%20how%20the%20app%20ships.md)). Pyodide 0.29.3 (what stlite 1.8.1 loads) ships numpy 2.2.5 and pandas 2.3.3 but a different scikit-learn than the one that trains our models, and training in WebAssembly would take minutes per visit — so the model had to travel as numbers. Verified in a headless Chromium with stlite 1.8.1 + Pyodide 0.29.3 served locally: the app renders in 27 s, all five tabs run, plotly installs from PyPI, the CSV download works ([research log](../Research%20Log/2026-08-25%20Phase%205%20—%20the%20app.md)).

## Alternatives considered

- **Ship the joblib pickle** — breaks or warns across scikit-learn versions, and cannot run where scikit-learn is absent; rejected.
- **Train in the app at start-up** — minutes in Pyodide, seconds locally, and the result would differ by environment; rejected.
- **ONNX export** — needs onnxruntime, unavailable in Pyodide; rejected.
- **`CalibratedClassifierCV(ensemble=True)`** (notebook 07's saved model) — five models to export; `ensemble=False` gives one model plus three maps at the same recipe; chosen.
- **Streamlit Community Cloud as the primary link** — simplest, but needs Rich's account, sleeps after inactivity, and runs on a third party's server; kept optional.
- **Unsigned `.exe`** — SmartScreen/antivirus flags; ruled out on 2026-08-24.

## Consequences

- Two one-time repository settings need Rich's OK: Pages source = GitHub Actions, and `refresh-2026` allowed in the `github-pages` environment (GitHub protects that environment with the default branch by default — [community discussion](https://github.com/orgs/community/discussions/39054): "Any environment you deploy GitHub Pages to must be protected. By default we protect it with your repository's default branch."). Claude Code can do both with `gh api` once Rich says yes.
- `app/data` and `app/model` are tracked (about 4 MB) and must be rebuilt (`python -m kepler.app_bundle`) whenever the live pull or the model recipe changes; `tests/test_app.py` checks the shipped bundle's hash matches the live pull it claims.
- The Phase 4 neural net, when built, can join the app only as exported weights evaluated in numpy (no PyTorch in the browser).
