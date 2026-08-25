---
tags: [research-log, notebook-05, habitable-zone]
date: 2026-08-24
---

# 2026-08-24 Notebook 05 rebuild — insolation habitable zone

> [!success] Outcome
> `notebooks/05_habitable_zone.ipynb` rebuilt on `kepler.habitable`: stellar-temperature-dependent insolation limits from Kopparapu et al. 2014 (coefficients read from Table 1 of the paper this session), a planet-radius ceiling (Rogers 2015), all host stars in scope with a `sunlike_host` flag, catalogue uncertainties carried. 24 tests pass, including exact reproduction of the 2020 habitable-zone pickles (12 and 37) for comparison.

## Method (verified sources)

- Limits: [Kopparapu et al. 2014, ApJL 787, L29 (arXiv:1404.5292)](https://arxiv.org/abs/1404.5292), Table 1, 1 Earth-mass planet, valid 2,600–7,200 K. `S_eff = S_eff☉ + aT + bT² + cT³ + dT⁴`, `T = Teff − 5780 K`. Sun-like values: recent Venus 1.776, runaway greenhouse 1.107, maximum greenhouse 0.356, early Mars 0.320 Earth flux. Coefficients in `kepler.habitable.KOPPARAPU_2014`; `seff_limit(5780, ·)` reproduces the table exactly (tested).
- Radius: [Rogers 2015, ApJ 801, 41 (arXiv:1407.4457)](https://arxiv.org/abs/1407.4457): "the majority of 1.6 Earth-radius planets are too low density to be comprised of Fe and silicates alone" → ≤ 1.6 R⊕ "plausibly rocky"; ≤ 2.0 R⊕ as the looser cut.
- Uncertainty: `hz_conservative_possible` uses `koi_insol ± err`.
- Validity: 8,959 of the 9,201 KOIs with a stellar temperature are inside 2,600–7,200 K; the 242 hotter than 7,200 K get no zone flags (no extrapolation).

## Results on the Kaggle-era snapshot

| Population | Conservative zone, any radius | ≤ 2.0 R⊕ | ≤ 1.6 R⊕ | ≤ 2.0 R⊕, Sun-like host | ≤ 2.0 R⊕, cooler host |
|---|---|---|---|---|---|
| CONFIRMED | 31 | **15** | 8 | 1 (Kepler-452 b) | 14 |
| CANDIDATE | 117 | 49 | 27 | 36 | 13 |

- Optimistic zone: 57 / 23 / 11 confirmed; 173 / 62 / 34 candidates.
- With the insolation uncertainty, 15 → **18** confirmed (adds Kepler-186 f, Kepler-1512 b, Kepler-560 b).
- The 15 (outer → inner): Kepler-1593 b, 441 b, 1229 b, 296 f, 309 c, 62 f, 1649 b, 452 b, 440 b, 705 b, 283 c, 442 b, 1544 b, 1410 b, 296 e. Two (Kepler-62 f, Kepler-283 c) are archive-CONFIRMED but pipeline FALSE POSITIVE.
- Candidates: the 49 are mostly long-period (300–650 d) objects around Sun-like stars with low signal-to-noise (only 15 have SNR ≥ 10; 27 lack a vetting score). Listed with SNR and score; no further gate applied.

## The 2020 filter, compared

- Reproduced with a left join (434 KOIs lack the stellar file): 12 confirmed / 37 candidates, identical index sets to the 2020 pickles.
- Of the 12: **0** in the conservative zone, 2 in the optimistic zone, **0** with radius ≤ 2 R⊕ (all > 3 R⊕). Overlap with the new 15: **none**.

## Built

- `src/kepler/habitable.py`: `seff_limit`, `hz_table`, `summarise`, `legacy_2020_box`.
- `tests/test_habitable.py`: 5 tests (Sun values, validity NaNs, flag consistency, snapshot counts, 2020 pickle reproduction, 2020 survivors outside the zone).
- Figures: `reports/figures/habitable_zone/hz_limits_vs_teff.png`, `hz_diagram_confirmed.png` (full + labelled zoom). The 2020 image moved to `reports/figures/habitable_zone_2020/`.
- Tables: `reports/tables/05_hz_confirmed.csv` (15 rows), `05_hz_candidates.csv` (49 rows).

## Caveats and next

- Snapshot-era dispositions and DR25 parameters. K03138.02 is FALSE POSITIVE here; it was later published as the Earth-sized habitable-zone planet Kepler-1649 c (Vanderburg et al. 2020) — **to verify against the live table in Phase 3**, which will move several rows.
- Limits are for a 1 Earth-mass planet; radius uncertainties are not applied to the radius cut.
- Phase 3 re-runs the screen on `cumulative_tap_YYYY-MM-DD.csv`.
