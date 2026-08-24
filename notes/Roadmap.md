---
tags: [plan]
updated: 2026-08-24
---

# Roadmap — 2026 refresh

Agreed 2026-08-24 (see [decision](Decisions/2026-08-24%20Restart,%20layout,%20and%20tooling.md)). Scope: a **faithful refresh first** (reproduce the 2020 results on modern tooling and scrutinize every notebook), then **v2 science**.

## Phase 1 — Foundation

- [x] Tag the original as `v1-bootcamp-2020`; work on branch `refresh-2026`
- [x] New directory layout, files moved with `git mv` so history follows
- [x] `pyproject.toml` + `uv.lock` (Python 3.12, pandas 2.x, scikit-learn 1.x, mlxtend, plotly, JupyterLab)
- [x] `.gitignore` / `.gitattributes` for a folder edited from Windows and Linux
- [x] `CLAUDE.md` shared by Cowork and Claude Code
- [x] Obsidian vault at the repo root: index, glossary, decisions, research log, references, templates
- [ ] Rich: push `refresh-2026` and the tag to GitHub; open the folder as an Obsidian vault
- [ ] Rich: paste the new project instructions into the Claude project settings

## Phase 2 — Reproduce and scrutinize

- [ ] Repoint every notebook to `kepler.paths`; plain-Markdown headers; run top-to-bottom on Python 3.12
- [ ] Reproduce the 2020 f1 scores (83 / 90 / 90 for LogReg / GBT / balanced RF; NN 84 deferred to Phase 4) and compare outputs against `data/legacy/` pickles
- [ ] Notebook-by-notebook review for bugs, hidden assumptions, and copy-paste drift — Rich found several on his own pass after the class; every finding goes in the Research Log
- [ ] Extract shared code into `src/kepler/` (`data.py`, `preprocess.py`, `features.py`, `habitable.py`) with tests
- [ ] Reconcile the "11 vs 12 habitable confirmed planets" discrepancy (README vs PDF/pickle)

## Phase 3 — Fresh data and honest models

- [ ] `fetch_koi.py`: pull `cumulative` via the archive TAP service, save as `data/raw/cumulative_tap_YYYY-MM-DD.csv`
- [ ] Two model variants: *with flags* and *physics-only*; calibrated comparison, leakage-free feature importance
- [ ] Decide on pandas 3 migration
- [ ] Retire Postgres/ERD formally (already in `archive/database/`)

## Phase 4 — Habitable zone done properly, and the neural net

- [ ] Kopparapu-based insolation limits (conservative + optimistic) with stellar-temperature dependence; planet-radius ceiling; carry `_err1/_err2` columns
- [ ] Re-run on the live table; cross-check survivors against the archive's own listings
- [ ] Rebuild the neural net in PyTorch (`uv sync --extra nn` on Rich's machine, CUDA index config added to `pyproject.toml`)

## Phase 5 — Ship

- [ ] Streamlit app replacing the 2020 Flask/Heroku app
- [ ] Rewrite README and refresh the presentation
- [ ] Stretch: run the same pipeline on the TESS Objects of Interest (TOI) table
