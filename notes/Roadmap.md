---
tags: [plan]
updated: 2026-08-25
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
- [x] Rich: ran the bootstrap script; folder is on `refresh-2026` with the tag; Obsidian vault open; project instructions updated
- [x] Claude Code: first-time setup on the new desktop (uv 0.12.5, Python 3.12.11, tests, VS Code extensions); branch + tag pushed
- [x] Decide the tag-team protocol, git autonomy, and the deliverable shape ([decision](Decisions/2026-08-24%20Tag%20team,%20git%20autonomy,%20and%20how%20the%20app%20ships.md))

## Phase 2 — Reproduce and scrutinize ✅ (complete 2026-08-24)

- [x] Rewrite notebooks 01, 02, 03 on the package; plain-Markdown headers; run top-to-bottom on Python 3.12 (04 and 05 are rebuilt in Phase 4, not repointed)
- [x] Reproduce the 2020 numbers — done inside the review: 83 / 90 / 90 are accuracy / weighted f1 (macro f1 0.77 / 0.87 / 0.87); every legacy pickle reproduces from the raw CSV
- [x] Notebook-by-notebook review — done 2026-08-24 as a multi-agent workflow (59 findings, 56 confirmed by adversarial verifiers): [summary](Research%20Log/2026-08-24%20Phase%202%20review%20summary.md), per-notebook notes in the Research Log. Notebook 01 pre-review: [entry](Research%20Log/2026-08-24%20Notebook%2001%20pre-review.md)
- [x] Redact the 2020 database password from the tracked archive notebook
- [x] Claude Code: one-time history rewrite (purge password, noreply email), force-push, commit map saved — [decision](Decisions/2026-08-24%20History%20rewrite,%20HZ%20scope,%20clustering%20fate.md)
- [x] Cowork: re-cloned and independently verified the purge (29 commits, 0 hits, private email absent)
- [x] Rewrite notebook 01 per the review — done 2026-08-24: [research log](Research%20Log/2026-08-24%20Notebook%2001%20rewrite.md)
- [x] Reproduce 03's numbers as macro + per-class f1 and compare feature sets with 5-fold CV — done 2026-08-24: [research log](Research%20Log/2026-08-24%20Notebook%2003%20rewrite%20—%20honest%20baseline.md)
- [x] Extract shared code: `data.py`, `preprocess.py`, `viz.py` with tests (2026-08-24)
- [x] Extract `models.py` (with notebook 03)
- [x] Extract `habitable.py` (with notebook 05)
- [x] Reconcile the "11 vs 12 habitable confirmed planets" discrepancy — resolved in the review: README numbers came from the superseded 2020-10-30 notebook version (extra `koi_pdisposition == CANDIDATE` condition); Kepler-90 h is the 12th

## Phase 3 — Fresh data and honest models ✅ (complete 2026-08-25)

- [x] `kepler.fetch` (CLI `uv run python -m kepler.fetch`): pulls `cumulative` via TAP, saves `data/raw/cumulative_tap_YYYY-MM-DD.csv` + provenance JSON (2026-08-24)
- [x] Claude Code ran the pull 2026-08-25: `data/raw/cumulative_tap_2026-08-25.csv` (9,564 × 153) + provenance
- [x] Notebook 08: live vs snapshot — 925 verdicts changed, flags rewritten with them; out-of-time AUC 0.937 for the physics-only model; HZ list 15 → 16 ([research log](Research%20Log/2026-08-25%20Notebook%2008%20—%20live%20archive%20vs%20snapshot.md))
- [x] Two model variants with calibrated probabilities and leakage-free permutation importance — notebook 07 ([research log](Research%20Log/2026-08-24%20Notebook%2007%20—%20models%20v2%20and%20the%20live-data%20fetcher.md)): physics-only ceiling ≈ 0.72 macro f1
- [x] Evaluation upgrade: macro + per-class f1 always; 5-fold stratified CV with error bars (done in notebook 03)
- [x] Hyperparameters chosen on validation folds (nested CV) in notebook 07
- [x] log1p on heavy-tailed columns (`models.log1p_scaled`; LR macro f1 0.53 → 0.67 physics-only)
- [x] Missingness indicators + NaN-native `HistGradientBoostingClassifier` on all 9,564 rows (notebook 07); gain over dropna ≈ 0.007, i.e. none
- [x] Clustering: rerun scaled, on all classes, ARI/NMI reported — null result recorded: [research log](Research%20Log/2026-08-24%20Notebook%2002%20rewrite%20—%20clustering%20null%20result.md)
- [ ] Decide on pandas 3 migration (no blocker found so far)
- [x] No external databases — connection notebook deleted, schema/ERD kept as history ([decision](Decisions/2026-08-24%20Column%20names,%20palette,%20no%20external%20databases.md))

## Phase 4 — Habitable zone done properly, and the neural net

- [x] Kopparapu-based insolation limits (conservative + optimistic) with stellar-temperature dependence; planet-radius ceiling; uncertainties carried — done 2026-08-24: [research log](Research%20Log/2026-08-24%20Notebook%2005%20rebuild%20—%20insolation%20habitable%20zone.md) (15 confirmed ≤ 2 R⊕ in the conservative zone; 2020's 12 share none)
- [x] Host-star scope **decided: all stars**, with a `sunlike_host` flag column (12 of the 13 small flat-HZ planets orbit stars cooler than 5,500 K)
- [x] Left join for stellar columns with join losses reported (434 KOIs); metallicity dropped as a criterion
- [x] Re-run on the live table — 16 confirmed ≤ 2 R⊕ in the conservative zone (Kepler-1652 b entered); Kepler-1649 c confirmed but outside with the KOI table's DR25 parameters
- [ ] Later: pull the archive's planetary-systems table for confirmed planets' revised parameters
- [ ] Rebuild the neural net in PyTorch (`uv sync --extra nn` on Rich's machine, CUDA index config added to `pyproject.toml`): validation split, early stopping, calibration check, scaler + column contract exported with the model

## Phase 5 — Ship

- [x] Streamlit app replacing the 2020 Flask/Heroku app (`app/app.py`, five tabs); `run_app.cmd`; physics-only calibrated probabilities trained on live labels, explicit label rule (`kepler.verdict`), out-of-fold catalogue — done 2026-08-25: [research log](Research%20Log/2026-08-25%20Phase%205%20—%20the%20app.md), [decision](Decisions/2026-08-25%20App%20architecture%20—%20portable%20model,%20stlite%20on%20GitHub%20Pages.md)
- [x] Model exported as plain numbers and evaluated with numpy (`kepler.portable`), verified equal to scikit-learn; bundle builder `kepler.app_bundle`
- [x] Browser build (stlite on GitHub Pages): `app/index.html`, `app/build_site.py`, `.github/workflows/pages.yml`; verified in headless Chromium with stlite 1.8.1 + Pyodide 0.29.3
- [ ] Rich: approve the two one-time Pages settings (source = GitHub Actions; allow `refresh-2026` in the `github-pages` environment) → Claude Code applies them → README placeholder becomes the live link
- [ ] Optional: Rich deploys to Streamlit Community Cloud from his account (entrypoint `app/app.py`; `app/requirements.txt` is in place)
- [x] README rewritten (2020 text preserved in `archive/README_2020.md`)
- [x] Dark mode (paired themes, validated dark palette) and the layperson layer (Start-here panel, per-tab guides, tooltips, glossary) — Rich's first-run feedback, done 2026-08-25
- [ ] Refresh the presentation
- [ ] Stretch: run the same pipeline on the TESS Objects of Interest (TOI) table
