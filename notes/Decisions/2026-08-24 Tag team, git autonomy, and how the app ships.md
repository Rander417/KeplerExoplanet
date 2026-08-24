---
tags: [decision, workflow, deployment]
date: 2026-08-24
status: accepted
---

# 2026-08-24 Tag team, git autonomy, and how the app ships

## Decisions

1. **Cowork and Claude Code tag-team; Rich runs the results.** Cowork (cloud) authors notebooks, code, and notes and writes them into the shared folder; Claude Code (on Rich's Windows machine) commits and pushes. The handshake is a gitignored `.cowork-handoff.md` at the repo root with the changed-file list and a suggested commit message. Details in `CLAUDE.md` → "Tag team".
2. **Git autonomy:** Claude Code commits and pushes to `refresh-2026` without asking. Anything touching `main`, tags, or history waits for Rich.
3. **Environment setup happens in a Claude Code session on the new desktop**, following the "First-time setup" checklist in `CLAUDE.md`, because Cowork cannot run commands in Rich's Windows environment.
4. **The Phase 2 notebook review runs as a multi-agent workflow** (one reviewer per notebook, one adversarial verifier per notebook), with findings merged into the Research Log. Rich opted in knowing the token cost.
5. **The app must be reachable by a click from GitHub with nothing to download.** That rules out an unsigned executable (SmartScreen/antivirus flags are exactly the "cybersecurity concern" to avoid). Phase 5 chooses between:
   - **Streamlit Community Cloud** — free hosting for a public GitHub repo; the app runs on Streamlit's servers ([docs](https://docs.streamlit.io/deploy/streamlit-community-cloud)).
   - **stlite on GitHub Pages** — "Serverless Streamlit Running Entirely in Your Browser" on Pyodide ([whitphx/stlite](https://github.com/whitphx/stlite)); static files, no server, no third-party account beyond GitHub. Constraint: only Pyodide-available packages run. Per the [Pyodide package list](https://pyodide.org/en/stable/usage/packages-in-pyodide.html), `scikit-learn` and `pandas` are built in; `plotly` is not built in (pure-Python, expected installable from PyPI at load — verify in Phase 5); `torch` is not available.
   - Either way the app is built with Streamlit and runs locally via `uv run streamlit run app/app.py`, with a `.cmd` launcher for Rich.

## Context

Rich moved to a new desktop with no environment for this project, wants to consume results rather than build them, and wants the capstone to be shareable safely. The mount that Cowork sees forbids deletes, which breaks git's lock protocol, so Cowork cannot commit here (tested 2026-08-24: `git clone` failed on `config.lock`).

## Alternatives considered

- *Rich as the relay* (push files by hand) — what he explicitly wants to stop doing.
- *Giving Cowork GitHub credentials* — not appropriate; Claude Code already has them via Rich's login.
- *PyInstaller executable* — unsigned binaries trip SmartScreen; code-signing certificates cost money and effort for no user benefit over a browser link.
- *Binder / Codespaces for notebooks* — fine for demos, but requires an account (Codespaces) or is slow to start (Binder); kept as a secondary option for the notebooks themselves.

## Consequences

- `CLAUDE.md` gains the setup checklist, handoff protocol, autonomy rules, and the Pyodide-compatibility constraint for app code.
- `tests/test_smoke.py` gives a fresh machine a pass/fail signal.
- Phase 4's PyTorch network is a modelling exercise; the shipped app will demo the scikit-learn models (or precomputed NN outputs).
