---
tags: [decision]
date: 2026-08-24
status: accepted
---

# 2026-08-24 Restart, layout, and tooling

## Decisions

1. **Restart on a branch in the existing fork.** `main` is tagged `v1-bootcamp-2020`; all refresh work happens on `refresh-2026` and merges to `main` when Rich is happy. Full history preserved, easy rollback.
2. **Repo root is the Obsidian vault.** Notes live in `notes/`; README, `CLAUDE.md`, and `data/README.md` are reachable from the graph. `.obsidian/app.json` and `templates.json` are committed (shared settings); `workspace.json` and caches are ignored. Links are written as Markdown links so they render on GitHub too.
3. **Scope = faithful refresh first, then v2 science.** Rich already found several issues in the teammates' work (and a few in his own) on an earlier pass; Phase 2 reproduces the 2020 numbers and scrutinizes every notebook before Phase 3–4 change the science. See [Roadmap](../Roadmap.md).
4. **Neural net will be rebuilt in PyTorch** (Phase 4), not carried over from Keras/TensorFlow 2.3.
5. **Tooling: `uv` + `pyproject.toml` + committed `uv.lock`, Python 3.12.** `pandas` pinned `<3` until Phase 3 (pandas 3 changes copy-on-write and string dtype defaults, which would muddy the reproduction).
6. **PyTorch is not in `pyproject.toml` yet.** Its CUDA wheel index (`download.pytorch.org`) is unreachable from the Cowork sandboxes, so a lock including it could not be generated or verified. Phase 4 adds an optional extra `nn = ["torch>=2.4"]` with `[tool.uv.sources] torch = [{ index = "pytorch-cu128", marker = "sys_platform == 'win32'" }]` and a matching `[[tool.uv.index]]`; Rich runs `uv sync --extra nn` on his own machine.
7. **Layout** (moves done with `git mv`): notebooks → `notebooks/01…05`; CSVs → `data/raw/` (the Kaggle file renamed `cumulative_kaggle_snapshot.csv`); 2020 pickles → `data/legacy/` (kept, 7 MB, for regression checks); images → `reports/figures/`; deck → `reports/presentation/`; Postgres/ERD, Flask app, `requirements.txt` → `archive/`.
8. **Dropped from the tree:** 52 MB of keras-tuner checkpoints (`tuningOutput/`), keeping only `oracle.json` and `tuner0.json` in `archive/keras_tuner_2020/`; the stray `.Rhistory`. They remain in git history at the v1 tag.
9. **Web app:** the Heroku URL returns 404 (Heroku ended free plans in November 2022). Phase 5 replaces Flask with Streamlit; the 2020 app is archived, not deleted.

## Context

Reconnaissance findings that drove these choices are in the [research log](../Research%20Log/2026-08-24%20Restart%20reconnaissance.md).

## Alternatives considered

- *Fresh repository* — cleaner, but loses the commit trail and the fork relationship to the team repo.
- *Restructure directly on `main`* — simpler, but no parallel branch to diff against while reproducing results.
- *`notes/` as its own vault* — smaller graph, but Obsidian could not link to README or the data dictionary, and Cowork/Claude Code would still see the notes either way.
- *Keep TensorFlow* — closest to the original, but native Windows GPU support ended with TF 2.10 and the neural net is being rebuilt anyway.
- *Git LFS for the 25 MB pptx and model files* — deferred; the files are already in history so LFS would not shrink the repo without a rewrite.

## Consequences

- The legacy notebooks reference 2020 paths and will not run until Phase 2 repoints them (deliberate: Phase 1 is structure only, so every diff is a rename).
- Anyone cloning needs `uv`; `CLAUDE.md` has the one-line install.
- Rich pushes the branch and tag himself (Claude never pushes).
