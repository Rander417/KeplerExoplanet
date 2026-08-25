# CLAUDE.md — working agreements for this repo

This file is read by Claude Code and by Cowork sessions that have this folder connected. It is the single source of truth for *how* we work here; the Claude project instructions point at it. Keep it short and current.

## What this project is

Analysis of the NASA Exoplanet Archive's **Kepler Objects of Interest (KOI) cumulative table**: cleaning and EDA, clustering, supervised models that predict a KOI's disposition (CONFIRMED / CANDIDATE / FALSE POSITIVE), and a habitable-zone screen of the survivors. It began in 2020 as a Columbia Engineering data-analytics bootcamp team project (Rich built the ML pipeline; teammates Damien Corr, Priscilla Lin, Tom Greff). In August 2026 Rich restarted it with modern tooling, an Obsidian vault, and a plan to correct the science. The original is frozen at git tag `v1-bootcamp-2020`; work happens on branch `refresh-2026`.

The plan, phase by phase, is in `notes/Roadmap.md`. Decisions are logged in `notes/Decisions/`. Findings go in `notes/Research Log/`.

## Layout

```
data/raw/          source files as downloaded (tracked)      data/README.md = provenance + column dictionary
data/processed/    regenerable parquet (ignored)
data/legacy/       2020 pickles, kept for regression checks
notebooks/         01_cleaning_eda  02_clustering  03_sklearn_models  04_neural_net  05_habitable_zone
src/kepler/        shared code: paths, data (load + column names), preprocess (clean, feature sets), models (2020 baselines, scoring, CV), clustering (sweep + agreement), habitable (Kopparapu limits, screen), viz (palette)
models/            trained artifacts (ignored)
notes/             Obsidian notes (the vault root is the repo root)
reports/           figures/<topic>/ (2020 figures kept under *_2020/), tables/, presentation/
archive/           2020 SQL schema + ERD (no credentials; the DB is retired for good), Flask web app, keras-tuner summaries, requirements_2020.txt
```

## Environment (uv)

* Install uv on Windows (once): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` — from the [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/).
* Create/refresh the environment: `uv sync --group dev` (reads `pyproject.toml` + `uv.lock`, installs `src/kepler` in editable mode).
* Run things inside it: `uv run jupyter lab`, `uv run python script.py`, `uv run ruff check src tests`, `uv run pytest`.
* Python 3.12 is pinned in `.python-version`; uv downloads it if missing.
* PyTorch is added in Phase 4 as an optional extra (`uv sync --extra nn`). Its CUDA index is unreachable from the Cowork sandboxes, so that step runs on Rich's machine.
* Notebooks 01, 02, 03 and 05 are rewritten on the package (2026-08-24) and run top to bottom. Notebook 04 is the 2020 original (legacy paths) until its Phase 4 PyTorch rebuild.
* No external databases: data lives in `data/raw/` (tracked) and `data/processed/` (regenerated); Phase 3 pulls from the archive's TAP service.

### First-time setup on a new machine (Claude Code does this; Rich watches)

1. Confirm `git --version` works and `git config user.name` / `user.email` are set.
2. Install uv with the one-liner above, then open a new terminal so `uv` is on PATH.
3. In the repo root: `uv sync --group dev` (downloads Python 3.12 the first time; a few minutes).
4. `uv run pytest` — all tests must pass (24 as of 2026-08-24). `uv run ruff check src tests` must be clean.
5. VS Code: install the `ms-python.python` and `ms-toolsai.jupyter` extensions (`code --install-extension <id>`), open the repo folder, and pick `.venv\Scripts\python.exe` as the interpreter/kernel.
6. Push whatever is unpushed on `refresh-2026` (see git autonomy below).

## Tag team: Cowork authors, Claude Code commits

Cowork (cloud) cannot run git against this folder (the mount forbids deleting lock files) and has no GitHub credentials, so the two Claudes split the work:

* **Cowork** does analysis, notebook and code authoring, and research notes in its own clone, then writes finished files directly into this folder. It leaves a **`.cowork-handoff.md`** at the repo root (gitignored) listing the changed files and a suggested commit message.
* **Claude Code**, at the start of any session and whenever asked to sync: if `.cowork-handoff.md` exists, read it, review the listed changes (`git status`, `git diff`), commit with the suggested message (edit it if the diff says otherwise), delete `.cowork-handoff.md`, push (see autonomy), and note anything surprising in `notes/Research Log/`.
* After a push, Cowork resyncs from GitHub. GitHub is the source of truth; Cowork's clone is scratch.
* Both read this file and `notes/00_Index.md` at session start.

### Git autonomy (agreed 2026-08-24)

* Claude Code may **commit and push to `refresh-2026` freely**: its own work and Cowork handoffs, in small logical commits with plain-English messages.
* **Ask Rich before**: merging or pushing to `main`, creating or moving tags, force-pushing, rebasing shared history, or deleting branches.
* Cowork never pushes (it cannot), and never asks Rich to relay pushes by hand when Claude Code can do it.
* Commit identity: Rich Anderson <29640136+Rander417@users.noreply.github.com>; never the private address (GitHub blocks the push).

## Deliverable shape (agreed 2026-08-24)

Rich runs the results, he does not build them. Every phase ends with something he can open without a terminal:

* Locally: a double-click launcher (`.cmd`) that starts the Streamlit app in the browser via `uv run`.
* Publicly: **a link from the GitHub README that anyone can click and use, with no download and nothing that trips SmartScreen or antivirus.** Unsigned `.exe` packaging is therefore out. Candidates, decided in Phase 5: Streamlit Community Cloud (free hosting of a public repo) or stlite (Streamlit running in the browser on Pyodide, hostable as static files on GitHub Pages). To keep the static option open, app code must stay pure-Python with Pyodide-available packages (pandas, numpy, scikit-learn are built in; plotly installs from PyPI at load; PyTorch is not available, so any neural-net demo needs exported weights or precomputed predictions).

## Science guardrails (read before modelling)

* **Target leakage.** The four `koi_fpflag_*` columns nearly determine `koi_pdisposition` (98% agreement measured on the Kaggle snapshot) and hand any model the FALSE POSITIVE class. Report two model variants: *with flags* (reproduces the vetting logic) and *physics-only* (no flags, no `koi_score`). Never quote a single f1 without saying which variant.
* **Habitable zone.** `kepler.habitable` implements the Kopparapu et al. 2014 stellar-temperature-dependent insolation limits on `koi_insol` plus the Rogers 2015 radius ceiling (1.6 R⊕; 2.0 as the loose cut); all host stars are in scope with a `sunlike_host` flag. The 2020 period/Teff/radius/metallicity box is kept only as `legacy_2020_box` for comparison.
* **Data provenance.** Every table has a dated origin recorded in `data/README.md`. Live pulls are named `cumulative_tap_YYYY-MM-DD.csv`. The 2020 Kaggle snapshot stays in `data/raw/` for reproducibility.
* **Two Ys.** `koi_pdisposition` (Kepler pipeline verdict, 2 classes) vs `koi_disposition` (archive verdict, 3 classes). The project's target is `koi_disposition`; say so explicitly in every model notebook.

## How Claude works with Rich

* Rich is an engineer with limited software-development experience: explain commands and choices plainly, prefer small verifiable steps, and show the exact command to run.
* Thoughts before action on substantive prompts; short answers for quick ones.
* **Never fabricate** data, results, numbers, or references. Mark any placeholder `[PLACEHOLDER]` in a way that cannot be missed. Cite factual and scientific claims with links and quotes.
* Be clear when Rich, or the 2020 work, is off track — kindly and specifically.
* Flag operations that will be heavy on tokens or runtime before starting them.
* Git: work on `refresh-2026` under the autonomy rules above; **never touch `main`, tags, or history without Rich saying so**.
* Notebooks: plain Markdown headers (no HTML `<span>` styling), one purpose per notebook, load data through `kepler.data` / `kepler.preprocess`, name the feature set used, write outputs to `data/processed/` or `models/`, save figures to `reports/figures/<topic>/`. Column names are the archive's (`koi_period`); `kepler.data.label()` gives readable labels for charts.
* Charts: no blue except for natural subjects (sky, water, sapphire). Call `kepler.viz.apply_style()` once per notebook: CONFIRMED green `#1f7a1f` ●, CANDIDATE amber `#e08a00` ▲, FALSE POSITIVE plum `#8b1e5f` ■ (validated palette, see notes/Decisions); `YlOrBr` for magnitudes, `PRGn` for diverging, `#5a5a52` for neutral bars.
* When a count is arbitrary (bullets, example rows, clusters to display), Rich prefers 5 or 7 over 6.
* Record every non-obvious decision as a short note in `notes/Decisions/` (date, decision, why, alternatives). Record findings with numbers in `notes/Research Log/`.
