---
tags: [reference]
updated: 2026-08-25
---

# References

One line each: what it is and what we use it for. "Verified" means the link was opened during the session that added it.

## Data and documentation

- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/) — home of the KOI cumulative table. (Verified 2026-08-24)
- [KOI table column definitions](https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html) — source of every quoted column definition in the Glossary and data README. (Verified 2026-08-24)
- [Retrieving Exoplanet Archive Data With TAP](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html) — how to pull the live table; table name `cumulative`. (Verified 2026-08-24)
- [Kaggle: Kepler Exoplanet Search Results](https://www.kaggle.com/nasa/kepler-exoplanet-search-results) — origin of the 2020 snapshot, as cited in the 2020 README. (Not re-opened in 2026; snapshot date unverified)
- [Kepler Science Center: the Kepler space telescope](https://keplerscience.arc.nasa.gov/the-kepler-space-telescope.html) — instrument facts cited in the 2020 deck. (As cited in the deck)

## Science

- Kopparapu, R. K. et al. 2013, *Habitable Zones Around Main-Sequence Stars: New Estimates*, ApJ 765, 131 — [arXiv:1301.6674](https://arxiv.org/abs/1301.6674) — the habitable-zone limits Phase 4 implements. (Verified 2026-08-24)
- Kopparapu, R. K. et al. 2014, *Habitable Zones Around Main-Sequence Stars: Dependence on Planetary Mass*, ApJ 787, L29 — [IOPscience](https://iopscience.iop.org/article/10.1088/2041-8205/787/2/L29) — the update with mass dependence. (Link from search results; to read in Phase 4)

- Mullally, F. et al. 2018, *Kepler's Earth-like Planets Should Not Be Confirmed without Independent Detection: The Case of Kepler-452b*, AJ 155, 210 — [arXiv:1803.11307](https://arxiv.org/abs/1803.11307) — quoted in the app's Kepler-452 b note. (Verified 2026-08-25)
- Vanderburg, A. et al. 2020, *A Habitable-zone Earth-sized Planet Rescued from False Positive Status*, ApJL 893, L27 — [arXiv:2004.06725](https://arxiv.org/abs/2004.06725) — Kepler-1649 c; quoted in the app. (Verified 2026-08-25)

## Project history

- [Rander417/KeplerExoplanet](https://github.com/Rander417/KeplerExoplanet) — this repo (Rich's fork). (Verified 2026-08-24)
- [tom-jj-G/KeplerExoplanets](https://github.com/tom-jj-G/KeplerExoplanets) — the original team repo. (As cited in the deck)
- `reports/presentation/Kepler_Analysis_Presentation.pdf` — the 2020 deck, updated 2022.

## Tooling

- [uv installation](https://docs.astral.sh/uv/getting-started/installation/) — the Windows one-liner in `CLAUDE.md`.
- [whitphx/stlite](https://github.com/whitphx/stlite) — Streamlit in the browser on Pyodide; `@stlite/browser` 1.8.1 bundles Streamlit 1.57.0 and loads Pyodide 0.29.3 (read from the npm package, 2026-08-25). The README's `mount()` options (`entrypoint`, `files` with `url`, `requirements`, `streamlitConfig`, `pyodideUrl`) are what `app/index.html` uses. (Verified 2026-08-25)
- [Streamlit Community Cloud: app dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) — "Community Cloud will search the directory where your entrypoint file is, then it will search the root of your repository"; precedence `uv.lock` > `Pipfile` > `environment.yml` > `requirements.txt` > `pyproject.toml`. (Verified 2026-08-25)
- [GitHub Pages: configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) and the [community discussion on the `github-pages` environment rule](https://github.com/orgs/community/discussions/39054) — why a non-default branch must be allowed explicitly. (Verified 2026-08-25)
- [Pyodide 0.29.3 release](https://github.com/pyodide/pyodide/releases/tag/0.29.3) — the distribution used for the local browser test (Python 3.13, numpy 2.2.5, pandas 2.3.3). (Downloaded 2026-08-25)
- [Heroku: removal of free product plans FAQ](https://help.heroku.com/RSBRUH58/removal-of-heroku-free-product-plans-faq) — why the 2020 web app URL is dead. (Verified 2026-08-24)
- [TensorFlow pip install guide](https://www.tensorflow.org/install/pip) and [forum note that 2.10 was the last native-Windows GPU release](https://discuss.ai.google.dev/t/2-10-last-version-to-support-native-windows-gpu/32465) — background for the PyTorch decision. (Verified 2026-08-24)
