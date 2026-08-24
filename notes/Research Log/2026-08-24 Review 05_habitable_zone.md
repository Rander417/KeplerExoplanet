---
tags: [research-log, review, notebook-05]
date: 2026-08-24
source: multi-agent review workflow wf_29148ee0-552 (reviewer + adversarial verifier)
---

# 2026-08-24 Review: Notebook 05 habitable zone

> [!abstract] What the notebook does (reviewer's summary)
> The notebook loads the 9,564-row KOI cumulative snapshot from Pickles/kepler_RAW.pkl (written by notebook 01; identical to data/raw/cumulative_kaggle_snapshot.csv to 1e-13), inner-joins it on kepid with data/raw/stellar_info_final.csv (7,810 stars, koi_smet and koi_smass with errors), sets kepoi_name as the index, drops every *_err column and rowid, and renames columns with a map that differs from notebook 01's. It then splits archive CONFIRMED (2,291 after the join) and CANDIDATE (2,186 after the join) rows and applies one box filter: 200 < koi_period < 400 days, 5500 < koi_steff < 6500 K, koi_srad <= 2.0 solar radii, koi_smet > 0. Cells 16-19 print each criterion applied alone (32, 1325, 1104, 2226 confirmed rows); cells 20-23 apply all four and report 12 confirmed and 37 candidate survivors, which are pickled to habitable_Confirmed_exoplanets.pkl and habitable_Candidate_Objects.pkl. I reproduced every printed count and both pickle index sets exactly from the raw CSVs. The central problem is scientific rather than software: no planet property (koi_prad, koi_insol, koi_teq) is used, so the 12 "habitable" confirmed planets are 3.3-11.7 Earth-radius objects receiving 1.5-4.9 times Earth's insolation, and none falls inside a Kopparapu-style insolation habitable zone; an insolation-plus-radius screen selects a completely disjoint set of 13 (radius <= 2.0) or 7 (radius <= 1.6) confirmed planets, provisional. The deck's five criteria, the README's numbers (11 planets, 30/1304/1085/2189) and the notebook's numbers (12, 32/1325/1104/2226) are three different things; the README numbers trace exactly to the superseded 2020-10-30 version of the notebook that also required koi_pdisposition == CANDIDATE.

> [!warning] At a glance
> **10 findings**: 3 high · 4 medium · 3 low. Verifier verdicts: 9 confirmed · 1 partially · 0 refuted · 0 unverifiable. Verifier added 3 missed item(s). 9 deck/README claims checked.

## Findings at a glance

| ID | Severity | Category | Finding | Verifier |
|---|---|---|---|---|
| 05-F1 | high | methodology | The habitability filter never looks at the planet; the 12 survivors are warm Neptunes and Jupiters | ✅ confirmed |
| 05-F2 | high | methodology | The 200-400 day period window sits inside the inner edge of the habitable zone for the stars it selects | ✅ confirmed |
| 05-F3 | high | claim-vs-data | Deck criteria (5, incl. logg > 4 and radius 1-2) do not match the notebook (4, no logg, radius only <= 2), and applying the deck's criteria literally gives 11 / 27, not 12 / 37 | ✅ confirmed |
| 05-F4 | medium | claim-vs-data | README numbers (11 planets; 2248 / 30 / 1304 / 1085 / 2189) come from the superseded 2020-10-30 notebook that also required koi_pdisposition == CANDIDATE; Kepler-90 h is the 12th | ✅ confirmed |
| 05-F5 | medium | bug | Inner join with stellar_info_final.csv silently drops 434 KOIs (62 candidates, 2 confirmed) | ✅ confirmed |
| 05-F6 | medium | methodology | 'Metallicity > 0' is not a habitability criterion and is mostly within measurement noise; it removes Kepler-452 b and Kepler-22 b | ✅ confirmed |
| 05-F7 | medium | methodology | No data-quality gate on candidates: the 37 include two 30-35 Earth-radius, grazing (impact > 1) signals and three below the 7.1-sigma detection threshold | ✅ confirmed |
| 05-F8 | low | documentation | Comments and README describe stellar cuts as planet properties ('Habitable temperature', 'Super-Earth size', 'super-earth like planets') | ✅ confirmed |
| 05-F9 | low | reproducibility | Reproducibility and hygiene: pickle dependency instead of the CSV, unused path, discarded uncertainties, inconsistent rename map, display-only sort | ✅ confirmed |
| 05-F10 | low | other | Git history of this notebook contains a plaintext database password (commit 359e7de) in a public repository | 🟡 partially (severity questioned) |

## Deck / README claims checked

| Verdict | Claim | Evidence |
|---|---|---|
| 🟡 partially | Deck: criteria are orbital period 200~400 days, stellar Teff > 5500 ~ 6500 K, stellar radius 1~2 solar radii, stellar surface gravity > 4, stellar metallicity > 0 | Deck text extracted with pdftotext lists all five. Notebook cells 20/21 implement only four: period 200-400 (strict), Teff 5500-6500 (strict), stellar radius <= 2.0 with no lower bound, metallicity > 0; no logg term anywhere. Applying the deck's five literally (reproduce_05.py): confirmed 11 (Kepler-1625 b fails logg = 3.964), candidates 27 (10 have stellar radius < 1.0). |
| 🟡 partially | Deck: Confirmed Exoplanets 2293 -> Habitable Zone 12 | 12 reproduced exactly from the raw CSVs with the notebook's four criteria (`box survivors: confirmed 12`; pickle has 12 rows with the same index). But the filter ran on 2,291 confirmed rows after the inner join (`merged ... 'CONFIRMED': 2291`), not 2,293, and the deck's own five criteria give 11. |
| 🟡 partially | Deck: Candidate Objects 2248 -> Habitable Zone 37 | 37 reproduced exactly (`candidate 37`; pickle 37 rows, same index). The filter ran on 2,186 candidates after the join (`'CANDIDATE': 2186`), 62 candidates were never evaluated; the deck's five criteria give 27. |
| 🟡 partially | README: only 11 kepler exoplanets satisfied all the habitable conditions: Kepler-111 c, Kepler-849 b, Kepler-1085 b, Kepler-90 g, Kepler-1550 b, Kepler-1514 b, Kepler-1515 b, Kepler-1519 b, Kepler-1533 b, Kepler-1625 b, Kepler-1634 b | The 11 names are exactly the current notebook's 12 minus Kepler-90 h (`12 minus README 11: {'Kepler-90 h'}`). The 11 reproduces only with the 2020-10-30 version's extra condition koi_pdisposition == 'CANDIDATE' (`README variant, with join: ... box 11`); Kepler-90 h is archive CONFIRMED but pipeline FALSE POSITIVE (koi_score 0.000, koi_fpflag_ss 1, cell 20 output). The current notebook, its printed output (cell 22: `12`) and the pickle all say 12. |
| ❌ refuted | README: 30 planets met the requirement for orbital period; 1304 within the temperature range; 1085 with sufficient natural resources (metallicity); 2189 super-earth like planets (and 2248 'confirm candidate') | For the current notebook the per-criterion counts are 32 / 1325 / 1104 / 2226 (cell 16-19 outputs `KepID 32`, `1325`, `1104`, `2226`; reproduced exactly). The README's numbers reproduce only under the superseded variant CONFIRMED & koi_pdisposition == CANDIDATE with no join loss: `README variant, no join: n 2248 period 30 teff 1304 srad<=2 2189` and `smet>0 1085`. The '2248 confirm candidate' figure is that pre-join population, which coincidentally equals the CANDIDATE class size. '2189 super-earth like planets' describes a cut on stellar radius <= 2 solar radii, not planet radius. |
| ✅ confirmed | Notebook's own printed results: 32 / 1325 / 1104 / 2226 per criterion; 12 confirmed and 37 candidate survivors; pickles of 12 and 37 rows | reproduce_05.py from the raw CSVs: `per-criterion (confirmed, each alone): period 32 teff 1325 smet>0 1104 srad<=2 2226`; `box survivors: confirmed 12 candidate 37`; `habitable_Confirmed_exoplanets (12, 28) index matches reproduction: True`; `habitable_Candidate_Objects (37, 28) index matches reproduction: True`. |
| ✅ confirmed | Guardrail comparison: how many confirmed planets pass an insolation-based screen (Kopparapu 2013 Sun-like limits 0.99 AU / 1.70 AU, i.e. ~1.02 to 0.35 Earth flux) plus a radius ceiling | PROVISIONAL. Flat Sun-like limits 1/0.99^2 = 1.020 and 1/1.70^2 = 0.346 Earth flux on all 2,293 confirmed rows (1 NaN koi_insol): 27 any radius; 7 with koi_prad <= 1.5 or <= 1.6; 10 with <= 1.75; 13 with <= 2.0; 17 with <= 2.5. The <= 2.0 list: Kepler-1229 b, Kepler-1410 b, Kepler-1544 b, Kepler-1649 b, Kepler-283 c, Kepler-296 e, Kepler-296 f, Kepler-309 c, Kepler-440 b, Kepler-442 b, Kepler-452 b, Kepler-62 f, Kepler-705 b (two of them, Kepler-62 f and Kepler-283 c, have koi_pdisposition FALSE POSITIVE). Candidates: 101 any radius, 41 with <= 2.0. Overlap between the flat-HZ confirmed set (27) and the 2020 box-12: none. A Teff-dependent variant using Kopparapu-2013 polynomial coefficients recalled from memory (NOT verified offline; must be checked against the paper and its erratum before use) gave 28 / 14 (<= 2.0) / 7 (<= 1.6). Caveat: koi_insol inherits the snapshot's DR25 stellar parameters, which for the coolest hosts look suspect (e.g. Kepler-1649 b's host is listed at Teff 2703 K, R 0.118 R_sun); cross-check against Gaia-era stellar catalogues before publishing any list. |
| ✅ confirmed | Join check: how many KOIs lose metallicity/mass; duplicate kepid rows in stellar_info_final.csv | stellar_info_final.csv: 7,810 rows, 7,810 unique kepid, 0 duplicates, 0 NaN, 0 kepid absent from the cumulative table. Cumulative table has 8,214 unique kepid, so 404 stars / 434 KOIs (370 FP, 62 CANDIDATE, 2 CONFIRMED: Kepler-1185 b, Kepler-1629 b) are dropped by the inner join; merged shape (9130, 55/56). |
| ✅ confirmed | Whether any criterion uses the planet itself (koi_prad, koi_insol, koi_teq) versus only the star and the period | None does: cells 16-21 reference only orbital_period[days], stellar_effective_temperature, stellar_radius[solar_radii], stellar_metallicity. Side observation from the data: koi_teq / koi_insol**0.25 has median 255.0 K (5th-95th percentile 254.7-255.3) over all KOIs, so koi_teq in this table is a deterministic transform of koi_insol and carries no extra information. |

## What the verifier added (missed by the reviewer)

> [!warning] The 5500-6500 K stellar-temperature window, not the period window, is what excludes almost the entire real habitable-zone population (medium)
> verify_05.py on the 2,293 confirmed rows: of the 13 planets inside the flat insolation HZ (0.346-1.020 Earth flux) with koi_prad <= 2.0, 12 orbit stars cooler than 5500 K (snapshot Teff 2703-4926 K: Kepler-1649 b, 296 e/f, 1229 b, 705 b, 1410 b, 309 c, 440 b, 283 c, 442 b, 1544 b, 62 f) and only Kepler-452 b (5579 K) is inside the window; only 2 of the 13 have periods in 200-400 d. For all 27 flat-HZ confirmed planets, the 2020 criteria applied alone keep: Teff 2, period 8, [Fe/H] > 0 8, stellar radius <= 2 all 27. The reviewer's mechanism story (F2 period, F6 metallicity) omits that the Teff cut alone discards 25 of 27, so the rewrite decision should state explicitly whether K- and M-dwarf hosts are in scope; in this snapshot that is where Kepler's small HZ planets are.

> [!warning] The 2020 database password is in the current tracked tree, not only in git history (medium)
> verify_05.py compared the password string parsed from commit 359e7de against current files without printing it: 'archive/database/Connect to AWS postgres.ipynb: same password present: True | rds endpoint present: True'; git ls-files shows that file is tracked at HEAD of refresh-2026. notebooks/01_cleaning_eda.ipynb also still contains the RDS endpoint (password=''). The reviewer's F10 says commit 9b2415e 'removed the DB code but not the history', which understates the situation; redacting the archived notebook in an ordinary commit removes the live copy without any history rewrite (which CLAUDE.md forbids without Rich's say-so).

> [!note] Positive check not run by the reviewer: stellar_info_final.csv is the same DR25 vintage as the snapshot, and koi_insol is already derivable from the snapshot's own stellar parameters (low)
> verify_05.py: recomputing logg from koi_smass and koi_srad (4.438 + log10(M/R^2)) reproduces the snapshot's koi_slogg with median absolute difference 0.0004 dex and within 0.01 dex for 98.4% of the 9,075 joined rows, so the join mixes no catalogue vintages and the kept rows are physically consistent. For the 12 survivors, flux computed from L = R^2 (Teff/5772)^4 and Kepler's third law matches koi_insol to within 1.2% ('max |S_calc/koi_insol - 1|: 0.012'). Consequence for the rewrite: F2's suggestion to compute flux from L and a would only reproduce koi_insol; use koi_insol with koi_insol_err1/err2 directly, and record the vintage check in the Research Log so the stellar file can be kept for the snapshot comparison without a re-pull.


## Keep (what the rewrite should preserve)

- Using kepoi_name as the row index with a comment explaining why (it is unique: 9,564 distinct values), so survivors stay traceable to KOIs.
- Bringing stellar metallicity and mass into the analysis from the archive, with their error columns present in the source file (the rewrite should keep the errors rather than drop them).
- Readable, explicit boolean-mask filters with each criterion on its own line, and per-criterion counts printed before the combined filter, which made the audit trivial to reproduce.
- Separating archive CONFIRMED from CANDIDATE populations and reporting both, and pickling both survivor tables for downstream use.
- A small, single-purpose notebook with no randomness: the 2020 pickles reproduce bit-for-bit (same index sets) from the raw CSVs six years later.
- The idea of a comparison list of 'candidates worth a second look' alongside confirmed planets is sound and worth keeping once data-quality gates are added.

## Rewrite recommendations

- Replace the box with a planet-centred screen per the CLAUDE.md guardrail: koi_insol inside Kopparapu et al. (2013; erratum; 2014 update) limits evaluated at each star's Teff (verify the polynomial coefficients from the paper before coding them), plus a planet-radius ceiling for 'plausibly rocky' (state the choice, e.g. 1.6 or 2.0 R_earth, and show both), and report 'nominal' and 'within 1-sigma' membership using koi_insol_err1/err2 and koi_prad_err1/err2. Provisional expectation from this session: 27 confirmed any radius, 13 at <= 2.0, 7 at <= 1.6.
- Keep the 2020 box only as a labelled comparison column (`legacy_box_2020`) and state plainly that it selects a disjoint set (0 overlap with the insolation set) consisting of 3-12 R_earth planets at 1.5-4.9 Earth flux.
- Drop period, metallicity and logg as hard cuts. If a period view is wanted, plot the HZ period band as a function of stellar mass; carry [Fe/H] and logg as descriptive columns with errors.
- Add printed data-quality gates for both populations: koi_prad sanity, koi_impact < 1, koi_model_snr >= 7.1 (or koi_score where present), DR25 delivery, and a koi_pdisposition-disagreement flag (Kepler-90 h, Kepler-62 f, Kepler-283 c are examples) instead of silently filtering on it.
- Take koi_smet and koi_smass from one dated TAP pull (or, for the snapshot comparison, a left join that prints the 434 missing KOIs); never inner-join silently. Pass `on='kepid'` once.
- Use one shared rename map from src/kepler so notebook 01 and notebook 05 outputs share column names; load through kepler.paths; write parquet to data/processed/; plain Markdown headers; no HTML spans; warm palette for any insolation-vs-radius figure with the HZ band drawn.
- Do not use koi_teq as an independent criterion: in this table koi_teq = 255 K x koi_insol^0.25 exactly, so say so and use insolation only.
- Before trusting any insolation-based list, cross-check the snapshot's stellar parameters for the coolest hosts against Gaia-era catalogues (the Kepler-1649 host at Teff 2703 K / 0.118 R_sun looks suspect; unverified offline) and prefer the live cumulative table's current stellar values.
- Update README and deck text together from generated numbers: retire the '11 planets' and '2189 super-earth' sentences, or at least replace them with the notebook's 12 / 32 / 1325 / 1104 / 2226 and name the population and criteria.
- Record decisions in notes/Decisions (insolation limits chosen, radius ceiling, treatment of pdisposition disagreement) and the numbers above in notes/Research Log; note the credential in commit 359e7de and confirm the RDS instance is gone, without rewriting history unless Rich asks.

## Finding details

### 05-F1 — The habitability filter never looks at the planet; the 12 survivors are warm Neptunes and Jupiters

> [!danger] high · methodology · cells [12, 16, 17, 18, 19, 20, 21]

**Evidence**

Cell 20: `habitable_confirmed_df = Confirmed_Exoplanets_df.loc[(...['orbital_period[days]']>200) & (...['orbital_period[days]']<400) & (...['stellar_effective_temperature']>5500) & (...['stellar_effective_temperature']<6500) & (...['stellar_radius[solar_radii]']<= 2.0) & (...['stellar_metallicity']>0)]`. Cell 12 renames `'koi_prad' : 'planetary_radius[earth_radii]'`, `'koi_teq' : 'equilibrium_temperature[k]'`, `'koi_insol' : 'insolation_flux[earth_flux]'` but none of the three columns appears in any filter. Cell 20 output (full notebook output, not the truncated view) lists the survivors' planetary_radius[earth_radii] as 10.89, 7.70, 7.79, 4.27, 11.67, 3.71, 3.28, 10.31, 9.17, 11.17, 7.67, 6.11 and insolation_flux[earth_flux] as 1.76, 3.22, 2.65, 1.49, 3.56, 3.48, 2.81, 3.22, 4.93, 3.29, 2.92, 2.27.

**Reproduction**

cd /tmp/KeplerExoplanet && uv run python /tmp/review/scratch/05_habitable_zone/reproduce_05.py -> `confirmed survivors prad 3.28 11.67 insol 1.49 4.93 teq 282.0 380.0 prad<=2: 0 insol in [0.35,1.02]: 0`. An earlier ad-hoc run additionally printed `prad>=6 (Neptune/Jupiter-ish): 9` and `insol in optimistic [0.32,1.78]: 2` for the same 12 rows.

**Impact**

The headline result of the notebook, deck and README ("12 habitable confirmed exoplanets", "11 ... satisfied all the habitable conditions") is not defensible. 0 of the 12 are small enough to be plausibly rocky (none <= 2 Earth radii; 9 of 12 are >= 6 Earth radii, i.e. Neptune to Jupiter size), and 0 of 12 sit inside the conservative insolation habitable zone (0.35-1.02 Earth flux); only 2 reach even the optimistic 0.32-1.78 band. Kepler-90 h (10.9 R_earth) and Kepler-1625 b (11.7 R_earth) are gas giants.

**Recommendation**

Screen on the planet, per the CLAUDE.md guardrail: koi_insol inside Kopparapu et al. (2013, and 2014 update) limits with stellar-Teff dependence, plus a planet-radius ceiling for 'plausibly rocky', carrying koi_insol_err1/err2. Keep the 2020 box only as a comparison column. Provisional counts from this session (flat Sun-like limits 1/0.99^2 = 1.020 to 1/1.70^2 = 0.346 Earth flux, on the 2,293 confirmed rows, no stellar join needed): 27 any radius, 13 with koi_prad <= 2.0, 7 with koi_prad <= 1.6 (see claims_checked).

**Verifier: ✅ confirmed**

*Corrected statement:* None of the four filter terms in cells 16-21 references a planet property (only orbital_period[days], stellar_effective_temperature, stellar_radius[solar_radii], stellar_metallicity). The 12 confirmed survivors have koi_prad 3.28-11.67 R_earth (9 of 12 >= 6 R_earth; 0 <= 2 R_earth; only Kepler-1625 b at 11.67 exceeds Jupiter's 11.2 R_earth, Kepler-90 h at 10.89 is just under but still Jupiter-class) and koi_insol 1.49-4.93 Earth flux; 0 of 12 fall in the flat conservative band 0.346-1.020 and only 2 in the optimistic 0.32-1.78 band. The flat insolation screen selects a disjoint set (27 any radius, 13 with R <= 2.0, 7 with R <= 1.6; overlap with the box-12: none); those counts are provisional.

*Verifier evidence:* Re-read cells 16-21 in the view (quoted filters use only star + period columns). Dumped the full cell 20 output from the .ipynb: planetary_radius column reads 10.89, 7.70, 7.79, 4.27, 11.67, 3.71, 3.28, 10.31, 9.17, 11.17, 7.67, 6.11 and insolation_flux reads 1.76, 3.22, 2.65, 1.49, 3.56, 3.48, 2.81, 3.22, 4.93, 3.29, 2.92, 2.27, exactly as the reviewer quoted. Re-ran reproduce_05.py: 'confirmed survivors prad 3.28 11.67 insol 1.49 4.93 teq 282.0 380.0 prad<=2: 0 insol in [0.35,1.02]: 0'. My own verify_05.py: '12 survivors: prad>=6 9 | prad>=11.2 1 | insol min/max 1.49 4.93 | optimistic [0.32,1.78] 2' and 'flat HZ [0.346,1.020] confirmed: 27 | prad<=1.6 7 | <=2.0 13 | overlap with box-12 []'.

### 05-F2 — The 200-400 day period window sits inside the inner edge of the habitable zone for the stars it selects

> [!danger] high · methodology · cells [16, 20, 21]

**Evidence**

Cell 16: `period_exoplanets_df = Confirmed_Exoplanets_df.loc[(Confirmed_Exoplanets_df['orbital_period[days]']>200) & (Confirmed_Exoplanets_df['orbital_period[days]']<400)]` combined in cell 20 with `stellar_effective_temperature` 5500-6500 K. Cell 20 output: stellar_mass[solar_mass] 1.029-1.303, stellar_radius[solar_radii] 1.012-1.793, stellar_effective_temperature 5548-6471 for the 12 survivors.

**Reproduction**

Kepler's third law for a 1 M_sun star (P = 365.25 * a**1.5, run in-session): `Sun-like star: a=0.99 AU -> P = 360 d` and `a=1.7 AU -> P = 810 d`. So the conservative HZ of a Sun-like star spans roughly 360-810 days, entirely above the notebook's 200-400 day window except for a sliver. The survivors' stars are at least as luminous as the Sun (masses 1.03-1.30 M_sun, radii 1.01-1.79 R_sun from cell 20 output), so their HZ periods are longer still. Consistent with this, reproduce_05.py prints minimum survivor insolation 1.49 Earth flux (all 12 hotter than the water-loss limit ~1.02).

**Impact**

The period window is a proxy for 'Earth-like orbit' that ignores stellar luminosity, so by construction it selects orbits that are too hot for the Sun-like and slightly evolved stars chosen by the Teff and radius cuts. This is the mechanism behind F1: the box cannot find a Sun-like-star HZ planet unless it orbits at 360-400 days. Kepler-452 b (384.8 d, 0.56 Earth flux) is the one such case in the snapshot, and it is then removed by the metallicity cut (F6).

**Recommendation**

Replace the period window with insolation (or compute semi-major axis from period and stellar mass, then flux from stellar luminosity L = R^2 (Teff/5772)^4, and compare to Teff-dependent limits). If a period plot is wanted for the deck, draw the HZ period band as a function of stellar mass rather than a fixed 200-400 window.

**Verifier: ✅ confirmed**

*Corrected statement:* The 200-400 day window is a luminosity-blind proxy that, combined with the 5500-6500 K and R <= 2 R_sun cuts, selects orbits interior to the habitable zone. Stronger than the reviewer stated: computing each survivor's own conservative HZ (L = R^2 (Teff/5772)^4 from the snapshot's koi_srad/koi_steff; a = 0.99 AU x sqrt(L); Kepler's third law with koi_smass) gives host luminosities 1.25-3.28 L_sun and inner-edge periods of 402-812 days, and all 12 survivors orbit with P shorter than their own inner-edge period. For the Sun, 0.99 AU -> 360 d and 1.70 AU -> 810 d. Kepler-452 b (384.8 d, 0.56 Earth flux) is the only confirmed row that passes the period/Teff/radius cuts and sits inside the flat HZ, and it is then removed by the metallicity cut.

*Verifier evidence:* verify_05.py: 'Sun: P(0.99 AU) = 360 d; P(1.70 AU) = 810 d'; '12 survivors: L/Lsun min 1.25 max 3.28 | P_HZin min 402 max 812 | all P < own P_HZin: True | max |S_calc/koi_insol - 1|: 0.012' (my luminosity-based flux reproduces the catalogue koi_insol to within 1.2%, so the two lines of evidence are consistent). Separate in-session run: of the 21 confirmed rows passing period/Teff/srad without the metallicity term, exactly one is in the flat HZ: [['Kepler-452 b', 384.847556, 0.56, -0.22, 1.09]]. Host masses 1.029-1.303 and radii 1.012-1.793 confirmed from the full cell 20 output.

### 05-F3 — Deck criteria (5, incl. logg > 4 and radius 1-2) do not match the notebook (4, no logg, radius only <= 2), and applying the deck's criteria literally gives 11 / 27, not 12 / 37

> [!danger] high · claim-vs-data · cells [7, 14, 15, 20, 21, 22, 23]

**Evidence**

Deck (reports/presentation/Kepler_Analysis_Presentation.pdf, extracted with pdftotext): `Habitable Criteria: Orbital_period[days]: 200 ~ 400 / Stellar_effective_temperature: > 5500 ~ 6500 / Stellar_radius[solar_radii]: 1 ~ 2 / Stellar_surface_gravity[log10(cm/s**2)]: > 4 / Stellar_metallicity: > 0 ... Confirmed Exoplanets: 2293 Candidate Objects: 2248 ... Habitable Zone: 12 Habitable Zone: 37`. Notebook cell 20/21 filters contain no `stellar_surface_gravity` term and only `['stellar_radius[solar_radii]']<= 2.0` (no lower bound). Cell 20 output: Kepler-1625 b has stellar_surface_gravity 3.964. Cell 21 output: ten candidates have stellar_radius[solar_radii] < 1 (0.969, 0.931, 0.903, 0.917, 0.912, 0.965, 0.924, 0.946, 0.940, 0.855).

**Reproduction**

reproduce_05.py: `deck criteria literally (box + logg>4 + srad>=1): confirmed 11 candidate 27`; `merged (9130, 55) {'FALSE POSITIVE': 4653, 'CONFIRMED': 2291, 'CANDIDATE': 2186}`. Ad-hoc run: `box + slogg>4 (deck): 11` (drops Kepler-1625 b), `box + srad>=1: 12` for confirmed; `box + srad>=1 (deck '1~2'): 27` for candidates.

**Impact**

The slide states criteria that were not the ones run, and starting counts (2293 / 2248) that are the pre-join totals, whereas the filter actually ran on 2,291 confirmed and 2,186 candidates after the inner join. Anyone re-implementing the slide's criteria will get 11 and 27 and conclude the notebook is wrong (or vice versa).

**Recommendation**

In the rewrite, generate the criteria text and the counts from the same code (e.g. a dict of named criteria rendered into the notebook's markdown and into any slide), and state the population the filter ran on. Decide explicitly whether logg and a lower radius bound are wanted; with an insolation screen they are unnecessary.

**Verifier: ✅ confirmed**

*Corrected statement:* The deck slide lists five criteria (period 200~400, Teff >5500~6500, stellar radius 1~2, logg > 4, metallicity > 0) and starting populations 2293/2248, but the notebook (cells 20/21) runs four criteria with no logg term and no lower radius bound, on the post-join populations of 2,291 confirmed and 2,186 candidates. Applying the slide's five criteria literally yields 11 confirmed (Kepler-1625 b fails with logg 3.964) and 27 candidates (10 have stellar radius < 1 R_sun), and this 11/27 result is the same under every inequality interpretation (>, >= for logg and radius).

*Verifier evidence:* pdftotext -layout on reports/presentation/Kepler_Analysis_Presentation.pdf, lines 164-169: 'Habitable Criteria: Orbital_period[days]: 200 ~ 400 ... Confirmed Exoplanets: 2293 Candidate Objects: 2248 / Stellar_effective_temperature: > 5500 ~ 6500 / Stellar_radius[solar_radii]: 1 ~ 2 Habitable Zone: 12 Habitable Zone: 37 / Stellar_surface_gravity[log10(cm/s**2)]: > 4 / Stellar_metallicity: > 0'. Full .ipynb outputs: cell 14 ends '[2291 rows x 28 columns]', cell 15 ends '[2186 rows x 28 columns]'. verify_05.py: all four combinations 'deck literal logg>4 & srad>=1 ... logg>=4 & srad>=1: confirmed 11 candidate 27'; 'survivor failing logg>4: [[Kepler-1625 b, 3.964]]'; 'srad<1 10' among the 37 candidates, matching the ten values 0.969, 0.931, 0.903, 0.917, 0.912, 0.965, 0.924, 0.946, 0.940, 0.855 read from the full cell 21 output.

### 05-F4 — README numbers (11 planets; 2248 / 30 / 1304 / 1085 / 2189) come from the superseded 2020-10-30 notebook that also required koi_pdisposition == CANDIDATE; Kepler-90 h is the 12th

> [!warning] medium · claim-vs-data · cells [14, 20, 22]

**Evidence**

Current cell 14 selects only `['exoplanet_archive_disposition'] == 'CONFIRMED'`. Cell 20 output row 1: `K00351.01 11442793 Kepler-90 h CONFIRMED` with `disposition_using_kepler_data FALSE POSITIVE`, `disposition_score 0.000`, `stellar_eclipse_fpf 1`. Git history (git show 359e7de:Habitable_Zone_Analysis.ipynb, cell 18): `Confirmed_Exoplanets_df = Kepler_Exoplanets_df.loc[(Kepler_Exoplanets_df['exoplanet_archive_disposition'] == 'CONFIRMED') & (Kepler_Exoplanets_df['disposition_using_kepler_data'] == 'CANDIDATE')]`, and its cell 19 output `KepID 30`. README: `There are 2248 kepler exoplanets are confirm candidate. 30 planets met the requirement for orbital period[days]; 1304 ... 1085 ... 2189 ... only 11 kepler exoplanets ...`. Commit b67a3cc (2020-11-03, 'Major refactoring of habitable analysis') removed the pdisposition condition; d9212e8 'Updated habitable slides' updated the deck; README.md was last touched for this text in 359e7de.

**Reproduction**

reproduce_05.py: `README variant, no join: n 2248 period 30 teff 1304 srad<=2 2189` and `README variant, with join: smet>0 1085 box 11`; `box survivors: confirmed 12`; ad-hoc run: `12 minus README 11: {'Kepler-90 h'}` and `CONFIRMED with pdisposition==FALSE POSITIVE (raw): 45`. All five README numbers and the 11-name list reproduce exactly under (a) CONFIRMED & koi_pdisposition == CANDIDATE and (b) no join loss (the module20 version read a Postgres table `kepler_habitable` that covered every KOI; its merge produced 13,450 rows and was then de-duplicated on kepler_name).

**Impact**

README and deck disagree (11 vs 12) because they describe different versions of the filter. The README also mislabels 2,248 as the number of 'confirm candidate' exoplanets; 2,248 is the count of CONFIRMED rows whose pipeline verdict is CANDIDATE, and only coincidentally equals the CANDIDATE class size (2,248). Kepler-90 h is a genuine 'two Ys' case: archive CONFIRMED, DR25 pipeline FALSE POSITIVE via the stellar-eclipse flag.

**Recommendation**

Retire both number sets in favour of the insolation-based result, or at minimum update the README to the notebook's 12 / 32 / 1325 / 1104 / 2226 and say which population and criteria they refer to. In the rewrite, report koi_pdisposition disagreement as a flag column rather than silently filtering on it (the insolation screen below also contains two such cases: Kepler-62 f and Kepler-283 c).

**Verifier: ✅ confirmed**

*Corrected statement:* Every README number (2248 / 30 / 1304 / 1085 / 2189 and the 11-name list) is the literal printed output of the 2020-10-30 revision (commit 359e7de, Habitable_Zone_Analysis.ipynb), which selected CONFIRMED & disposition_using_kepler_data == CANDIDATE and read a Postgres table covering all 9,564 KOIs (its merge produced 13,450 rows, then drop_duplicates on kepler_name left 2,295). Commit b67a3cc (2020-11-03) is the first revision without the pdisposition condition; README line 108 was last changed in 359e7de. Kepler-90 h (archive CONFIRMED, pipeline FALSE POSITIVE, koi_score 0.000, koi_fpflag_ss 1) is the 12th.

*Verifier evidence:* Dumped outputs of git show 359e7de:Habitable_Zone_Analysis.ipynb (byte-identical to the reviewer's scratch copy): cell 8 '[9564 rows x 7 columns]', cell 9 '[13450 rows x 56 columns]', cell 14 '[2295 rows x 29 columns]', cell 18 '[2248 rows x 10 columns]', cell 19 'KepID 30', cell 20 '[1304 rows x 10 columns]', cell 21 '[1085 rows x 10 columns]', cell 22 '[2189 rows x 10 columns]'; cell 18 code contains the pdisposition == 'CANDIDATE' condition. grep across revisions: occurrences of the condition are 2 in 52b2060, 359e7de, 9b2415e, d9212e8 and 0 in b67a3cc; commit dates 359e7de 2020-10-30, 9b2415e 2020-10-31, d9212e8 2020-11-01, b67a3cc 2020-11-03. git blame README.md -L 108: 359e7dea 2020-10-30. verify_05.py: 'README variant: n 2248 period 30 teff 1304 srad<=2 2189 smet>0 (joined) 1085 box 11 | 12 minus box(cc): [Kepler-90 h]'. Cell 20 full output for K00351.01: disposition_using_kepler_data FALSE POSITIVE, disposition_score 0.000, stellar_eclipse_fpf 1.

### 05-F5 — Inner join with stellar_info_final.csv silently drops 434 KOIs (62 candidates, 2 confirmed)

> [!warning] medium · bug · cells [6, 7]

**Evidence**

Cell 7: `rawStellar_df = pd.merge(keplerRAW_df, stellar_df, on=["kepid", "kepid"])` (default how='inner'; 'kepid' listed twice). Cell 7 output ends at index `9127`+ vs cell 5's `9561`+, but the row loss is never counted or mentioned. Cell 6 output: stellar_df has 7,806+ rows.

**Reproduction**

reproduce_05.py: `raw (9564, 50) stellar (7810, 7) stellar dup kepid: 0`; `KOIs lost by inner join: 434 {'FALSE POSITIVE': 370, 'CANDIDATE': 62, 'CONFIRMED': 2}`; `merged (9130, 55)`. Ad-hoc run: raw has 8,214 unique kepid vs 7,810 in the stellar file; stellar file has 0 NaN and 0 kepid not present in raw; lost confirmed planets are Kepler-1185 b (K02311.03, koi_pdisposition CANDIDATE) and Kepler-1629 b (K05447.02).

**Impact**

The candidate population used for the 37 is 2,186, not the 2,248 quoted on the slide; 62 candidates were never evaluated. No duplicate-kepid inflation occurs in the CSV version (unlike the 2020-10-30 DB version), so the join is correct for the rows it keeps, but the loss is invisible.

**Recommendation**

Use a left join and print the number of KOIs lacking stellar metallicity/mass, or better, take koi_smet/koi_smass from a single TAP pull of the cumulative table (data/README.md already notes the separate file is unnecessary). Pass `on='kepid'` once.

**Verifier: ✅ confirmed**

*Corrected statement:* pd.merge(..., on=['kepid','kepid']) is an inner join that silently drops 434 of 9,564 KOIs (370 FALSE POSITIVE, 62 CANDIDATE, 2 CONFIRMED: Kepler-1185 b K02311.03 and Kepler-1629 b K05447.02) because stellar_info_final.csv covers 7,810 of the 8,214 distinct kepids; the file has no duplicate kepids and no NaNs, so kept rows are correct. Two proportionality notes the reviewer did not give: (a) the duplicated key name is harmless, the exact call still runs under pandas 2.3.3 and returns (9130, 56); (b) the effect on the results is at most one row: of the 62 lost candidates only K05718.01 (5.2 R_earth, 1.8 Earth flux) passes the three non-metallicity criteria, and neither lost confirmed planet does. Medium is defensible as a silent-data-loss/reproducibility issue, not for its numerical impact.

*Verifier evidence:* verify_05.py: 'raw unique kepid 8214 | stellar rows 7810 unique 7810 NaN 0'; 'pd.merge(on=[kepid,kepid]) in pandas 2.3.3 -> (9130, 56)'; 'lost by inner join: 434 {FALSE POSITIVE: 370, CANDIDATE: 62, CONFIRMED: 2} | lost CONFIRMED: [[K02311.03, Kepler-1185 b, CANDIDATE], [K05447.02, Kepler-1629 b, FALSE POSITIVE]]'; 'lost-by-join KOIs passing 3 non-smet criteria: [... [K05718.01, CANDIDATE, 5.2, 1.8]]' (the other four are FALSE POSITIVE rows). Full .ipynb cell 7 output ends '[9130 rows x 56 columns]'.

### 05-F6 — 'Metallicity > 0' is not a habitability criterion and is mostly within measurement noise; it removes Kepler-452 b and Kepler-22 b

> [!warning] medium · methodology · cells [18, 20, 21]

**Evidence**

Cell 18: `# Metallicity: the proportion of the material of a star ... in elements other than hydrogen or helium. # Resources in exoplanets` then `metal_exoplanets_df = Confirmed_Exoplanets_df.loc[(Confirmed_Exoplanets_df['stellar_metallicity']>0)]`. data/README.md quotes the archive definition of koi_smet: "The base-10 logarithm of the Fe to H ratio at the star surface, normalized by solar ratio." So > 0 means 'more iron-rich than the Sun', not 'has resources'. Cell 20 output: survivor stellar_metallicity values 0.07-0.42.

**Reproduction**

reproduce_05.py: `share of stars with |[Fe/H]| <= err1: 0.632 | stars with [Fe/H]==0.00 exactly: 295`; `smet consistent with 0 (smet+err2<=0): 8` of the 12 survivors. Ad-hoc run: `Kepler-452 b pdisp=CANDIDATE P=384.8 d Teff=5579 Rs=0.798 logg=4.580 [Fe/H]=-0.22 (+0.3/-0.3) Rp=1.09 S=0.56 Teq=220.0` and `Kepler-22 b ... P=289.9 d Teff=5516 Rs=0.886 ... [Fe/H]=-0.26 (+0.15/-0.15) Rp=2.34 S=1.03` -- both pass period, Teff and stellar radius and fail only metallicity. Also 138 confirmed rows have koi_smet exactly 0.000 and fail a strict > 0 (origin of the exact zeros unverified offline; plausibly catalogue defaults).

**Impact**

A threshold at exactly 0 on a quantity whose 1-sigma error is 0.15-0.30 dex for most stars acts as a coin flip: 63% of stars are consistent with solar within 1 sigma, and 8 of the 12 'habitable' survivors are consistent with [Fe/H] <= 0. The cut discards the snapshot's best Sun-like-star HZ planet (Kepler-452 b).

**Recommendation**

Drop the criterion. If planet-formation context is wanted, report [Fe/H] with its error as a descriptive column, never as a hard cut; the same goes for logg.

**Verifier: ✅ confirmed**

*Corrected statement:* koi_smet is log10([Fe/H]) relative to solar (data/README.md line 66), so '> 0' means 'more iron-rich than the Sun', not 'has resources'. The cut sits inside the measurement noise: 63.2% of stars in stellar_info_final.csv have |[Fe/H]| <= err1, 138 of the 2,291 joined confirmed rows have koi_smet exactly 0.000 and fail a strict > 0, and 8 of the 12 survivors have koi_smet + koi_smet_err2 <= 0. It removes Kepler-452 b (P 384.8 d, Teff 5579, R_s 0.798, [Fe/H] -0.22 +0.3/-0.3, R_p 1.09, S 0.56) and Kepler-22 b (P 289.9 d, Teff 5516, R_s 0.886, [Fe/H] -0.26 +/-0.15, R_p 2.34, S 1.03), both of which pass the other three criteria. Addition: among the 27 confirmed planets in the flat insolation HZ only 8 have [Fe/H] > 0. The 295 exact-zero rows in the stellar file do not share one error-bar pattern (161 have +/-0.15, 64 have +0.25/-0.30, 6 have 0/0), so 'catalogue defaults' remains unverified.

*Verifier evidence:* verify_05.py: 'confirmed joined smet==0: 138 | survivors smet+err2<=0: 8 | stellar |smet|<=err1 share: 0.632'; 'Kepler-452 b P 384.8 Teff 5579.0 Rs 0.798 [Fe/H] -0.22 0.3 -0.3 Rp 1.09 S 0.56 | passes 3 non-smet criteria: True'; 'Kepler-22 b P 289.9 Teff 5516.0 Rs 0.886 [Fe/H] -0.26 0.15 -0.15 Rp 2.34 S 1.03 | passes 3 non-smet criteria: True'; 'flat-HZ-27 passing each 2020 criterion alone: ... smet>0 8 of 27'. Separate in-session run of error-bar combos for the 295 zero rows: {(0.15,-0.15): 161, (0.25,-0.3): 64, (0.1,-0.1): 14, (0.3,-0.3): 8, (0.0,0.0): 6, ...}. Cell 18 comment and filter quoted from the view.

### 05-F7 — No data-quality gate on candidates: the 37 include two 30-35 Earth-radius, grazing (impact > 1) signals and three below the 7.1-sigma detection threshold

> [!warning] medium · methodology · cells [21, 23, 25]

**Evidence**

Cell 21 output (full): `K07073.01 ... planetary_radius[earth_radii] 30.25 ... impact_parameter 1.1980`, `K08279.01 ... 35.30 ... 1.2420`; `K05707.01 ... transit_signal-to-noise 4.9`, `K00492.02 ... 5.9`, `K04418.01 ... 7.0` with `tce_delivery NaN`; 14 rows with `disposition_score NaN`; 13 rows with `tce_delivery q1_q16_tce`.

**Reproduction**

reproduce_05.py: `candidate survivors prad>=20: 2 impact>1: 2 snr<7.1: 3 score NaN: 14 srad<1: 10 insol in [0.35,1.02]: 6`. Ad-hoc run: candidate survivors koi_prad range 1.2-35.3, koi_insol 0.64-6.71; `insol in [0.35,1.02] AND prad<=2.0: 0`.

**Impact**

Objects larger than Jupiter (~11.2 R_earth) with grazing geometry are far more likely eclipsing binaries or poor fits than planets; sub-threshold SNR signals are marginal detections. Presenting them as 'habitable candidates' overstates the result, and the pickled list feeds nothing downstream that would catch this (no notebook or the Flask app reads the habitable pickles; grep found references only in src/kepler/paths.py and the notes).

**Recommendation**

Add explicit gates with a printed count for each: koi_prad sanity ceiling, koi_impact < 1, koi_model_snr >= 7.1 (or koi_score where present), DR25 delivery (q1_q17_dr25_tce), and report how many rows each gate removes.

**Verifier: ✅ confirmed**

*Corrected statement:* The 37 candidate survivors pass no data-quality gate: two are 30.25 and 35.30 R_earth with impact parameters 1.198 and 1.242 (grazing; K07073.01, K08279.01), three have koi_model_snr below 7.1 (K05707.01 4.9, K00492.02 5.9, K04418.01 7.0, the last with NaN tce_delivery), 14 have NaN koi_score, and 13 were delivered by q1_q16_tce rather than DR25. Precision note: the Kepler pipeline's 7.1-sigma threshold is defined on the multiple-event statistic, while koi_model_snr is the archive's transit-model SNR ('Transit depth normalized by the mean uncertainty in the flux during the transits', data/README.md line 60); a related but distinct statistic, so say 'model SNR < 7.1' rather than 'below the detection threshold'. The point that these are marginal detections stands. Nothing downstream reads the habitable pickles.

*Verifier evidence:* Full cell 21 output (dumped from the .ipynb) shows K07073.01 planetary_radius 30.25 / impact 1.1980, K08279.01 35.30 / 1.2420, K04418.01 tce_delivery NaN, 14 NaN disposition_score rows and 13 q1_q16_tce rows (counted by hand from the output). verify_05.py: 'cand snr<7.1: [[K04418.01, 7.0, nan], [K05707.01, 4.9, q1_q16_tce], [K00492.02, 5.9, q1_q16_tce]] | prad>=20: [[K07073.01, 30.25, 1.198], [K08279.01, 35.3, 1.242]] | score NaN 14 | q1_q16 13 | srad<1 10'; reproduce_05.py re-run: 'candidate survivors prad>=20: 2 impact>1: 2 snr<7.1: 3 score NaN: 14 srad<1: 10 insol in [0.35,1.02]: 6'. grep -rl for the pickle names outside notebook 05 returns only ./src/kepler/paths.py and ./notes/Research Log/2026-08-24 Restart reconnaissance.md.

### 05-F8 — Comments and README describe stellar cuts as planet properties ('Habitable temperature', 'Super-Earth size', 'super-earth like planets')

> [!note] low · documentation · cells [17, 18, 19]

**Evidence**

Cell 17: `# Habitable temperature on these exoplanets` filters `stellar_effective_temperature` 5500-6500 K. Cell 19: `# Super-Earth size plant` filters `['stellar_radius[solar_radii]']<= 2.0`. README: `2189 planets are super-earth like planets`. Cell 18 comment defines metallicity as a mass fraction while koi_smet is log10 [Fe/H] relative to solar.

**Reproduction**

reproduce_05.py: among the 12 survivors `prad<=2: 0` (planet radii 3.28-11.67 R_earth), so the 'super-Earth' label is contradicted by the data the notebook itself carries. The four per-criterion counts in cells 16-19 are each applied alone to the confirmed set (independent, not sequential): 32 / 1325 / 1104 / 2226 reproduced.

**Impact**

Readers (and the README author, evidently) took 'temperature' and 'size' to be about the planet. This mislabelling is how a stellar-radius cut became '2189 super-earth like planets'.

**Recommendation**

Name variables and comments by what they filter (`star_teff_ok`, `star_radius_ok`), quote the archive definition next to each criterion, and state that per-criterion counts are independent.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell 17's comment '# Habitable temperature on these exoplanets' labels a cut on stellar_effective_temperature, cell 19's '# Super-Earth size plant' labels a cut on stellar_radius[solar_radii] <= 2.0, and cell 18 defines metallicity as a mass fraction although koi_smet is log10 [Fe/H] relative to solar; the README's '2189 planets are super-earth like planets' inherited the mislabel. The survivors' own planet radii (3.28-11.67 R_earth) contradict the 'super-Earth' label, and the per-criterion counts 32 / 1325 / 1104 / 2226 are independent (each applied alone to the 2,291 confirmed rows), not sequential.

*Verifier evidence:* Comments quoted from view cells 17, 18, 19; README line 108 (grep) contains '2189 planets are super-earth like planets'. reproduce_05.py re-run: 'per-criterion (confirmed, each alone): period 32 teff 1325 smet>0 1104 srad<=2 2226', matching cell 16-19 outputs 'KepID 32', '1325', '1104', '2226' in the view. Survivor radii from the full cell 20 output (3.28 minimum, 11.67 maximum).

### 05-F9 — Reproducibility and hygiene: pickle dependency instead of the CSV, unused path, discarded uncertainties, inconsistent rename map, display-only sort

> [!note] low · reproducibility · cells [3, 4, 10, 12, 20, 21]

**Evidence**

Cell 3 defines `file_path_Raw = "./Resources/cumulative.csv"` but cell 4 loads `pickle.load(... 'kepler_RAW.pkl')` (written by notebooks/01_cleaning_eda.ipynb), so `file_path_Raw` is dead code and the notebook depends on notebook 01 having run. Cell 10: `columns_to_drop = [col for col in keplerProcessed_df.columns if '_err' in col]` removes koi_insol_err1/2, koi_prad_err1/2, koi_smet_err1/2 that an HZ analysis needs. Cell 12 rename map uses `'KepID'`, `'kepler_name'`, `'exoplanet_archive_disposition'`, `'orbital_period[days]'` whereas notebook 01's pickle uses `'Kep_ID'`, `'Kepler_Name'`, `'Exoplanet_Archive_Disposition'`, `'Orbital_Period_[days]'` (data/README.md documents only the latter). Cells 20/21: `habitable_confirmed_df.sort_values(by=['kepler_name'], ascending = False)` is not assigned, so pickles are saved unsorted (harmless). Kernel metadata: Python 3.7.6, kernelspec 'PythonData'.

**Reproduction**

Ad-hoc run: `kepler_RAW.pkl shape (9564, 50) | equals CSV: False ... max abs diff numeric: 1.1368683772161603e-13 | object cols equal: True` (so the pickle is the CSV up to float parsing). Legacy pickle columns: kepler_clean_full first cols `['rowid', 'Kep_ID', 'Kepler_Name', 'Exoplanet_Archive_Disposition', ...]` vs habitable_Confirmed_exoplanets `['KepID', 'kepler_name', 'exoplanet_archive_disposition', ...]`. reproduce_05.py: both habitable pickles' index sets match the CSV-based reproduction (`index matches reproduction: True`).

**Impact**

Nothing here changes the numbers, but the rewrite would inherit a hidden dependency, a second naming convention (outputs of notebooks 01 and 05 cannot be joined by column name), and no error bars for the one analysis where they matter most.

**Recommendation**

Load through kepler.paths from the raw CSV or a dated TAP pull; keep the *_err columns for koi_insol, koi_prad, koi_smet; use one shared rename map in src/kepler; write parquet to data/processed/; remove dead variables.

**Verifier: ✅ confirmed**

*Corrected statement:* Cell 3's file_path_Raw is dead code; cell 4 loads Pickles/kepler_RAW.pkl, which notebook 01 writes and which equals the raw CSV up to float parsing (max abs numeric difference 1.14e-13, identical dtypes and object columns). Cell 10 drops every *_err column including koi_insol/koi_prad/koi_smet errors. Cell 12's rename map ('KepID', 'kepler_name', 'exoplanet_archive_disposition', 'orbital_period[days]') differs from notebook 01's ('Kep_ID', 'Kepler_Name', 'Exoplanet_Archive_Disposition', 'Orbital_Period_[days]'), and its 'kepoi_name' -> 'koi_name' entry is inert because kepoi_name became the index in cell 9 (the pickles carry no koi_name column and an unnamed index). The sort_values calls in cells 20/21 are unassigned, so the pickles are unsorted. Kernel metadata: Python 3.7.6, kernelspec PythonData.

*Verifier evidence:* verify_05.py: 'kepler_RAW.pkl equals CSV: False | max abs numeric diff: 1.1368683772161603e-13'; in-session run: 'columns equal: True ... object cols equal: True | dtypes equal: True'; 'habitable pickle cols[:3] [KepID, kepler_name, exoplanet_archive_disposition] | index set == reproduction: True | sorted desc: False'; kepler_clean_full.pkl first columns ['rowid', 'Kep_ID', 'Kepler_Name', 'Exoplanet_Archive_Disposition', 'Disposition_Using_Kepler_Data']; habitable pickle '_err' columns: [] and 'koi_name' in columns: False; index name None. grep in notebooks/01_cleaning_eda.ipynb: "kepler_RAW.pkl', 'wb') as pickle_file" and "'koi_period' : 'Orbital_Period_[days]'", "'kepid' : 'Kep_ID'". .ipynb metadata: kernelspec {'display_name': 'PythonData', 'name': 'pythondata'}, language_info version 3.7.6.

### 05-F10 — Git history of this notebook contains a plaintext database password (commit 359e7de) in a public repository

> [!note] low · other · cells [3]

**Evidence**

git show 359e7de:Habitable_Zone_Analysis.ipynb, code cell 2 builds `db_string = f"postgres://{userID}:{password}@{endpoint}:{port}/{dbinstance}"` with a literal password and an AWS RDS endpoint (kepler-exoplanet.cotbxoedtrfv.us-east-1.rds.amazonaws.com), and the cell's printed output repeats the full connection string. The current notebook (cells 3-4) reads pickles only and contains no credentials; commit 9b2415e ('Refactored notebooks to use pickles, including removing all database calls') removed the DB code but not the history.

**Reproduction**

cd /tmp/KeplerExoplanet && git log --oneline --follow --all -- notebooks/05_habitable_zone.ipynb -> `... 9b2415e Refactored notebooks to use pickles ... 359e7de module20 version 52b2060 Updates: ... habitable zone draft`; the credential text was confirmed by dumping that revision (password deliberately not reproduced here).

**Impact**

The credential is public. The RDS instance is probably long gone (the README says the Heroku app already 404s), but if the password was reused anywhere it should be treated as compromised.

**Recommendation**

Verify the RDS instance is deleted and the password is not reused; do not rewrite history unless Rich explicitly asks (CLAUDE.md rule). Record the observation in notes/Decisions or the Research Log so it is not rediscovered.

**Verifier: 🟡 partially** — severity questioned

*Corrected statement:* Confirmed: commit 359e7de's Habitable_Zone_Analysis.ipynb (code cell 2) contains a literal 12-character password and the RDS endpoint kepler-exoplanet.cotbxoedtrfv.us-east-1.rds.amazonaws.com, and the cell's printed output repeats the full connection string; the current notebook 05 contains neither. Correction: the credential is not only in history. The identical password (with the endpoint) is present in the tracked file archive/database/Connect to AWS postgres.ipynb at HEAD of refresh-2026, and notebooks/01_cleaning_eda.ipynb still carries the RDS endpoint (with an empty password). So removing it from the tree needs only an ordinary commit that redacts the archived notebook, no history rewrite. 'Public repository' is plausible (origin is https://github.com/Rander417/KeplerExoplanet.git) but unverified offline. Severity should be medium rather than low because the secret is live in the branch that is about to be worked on and pushed, not merely buried in 2020 history.

*Verifier evidence:* git log --follow --all on the notebook lists 9b2415e, 359e7de, 52b2060 as the reviewer said; git show 359e7de:Habitable_Zone_Analysis.ipynb is byte-identical (cmp) to the reviewer's scratch copy; parsing its code cell 2 with the password regex-redacted shows 'password = "[REDACTED]"', the endpoint line, 'db_string = f"postgres://[REDACTED]"', 'print(db_string)' and an output line beginning 'postgres://'. verify_05.py (password compared in memory, never printed): 'archive/database/Connect to AWS postgres.ipynb: same password present: True | rds endpoint present: True'; 'notebooks/01_cleaning_eda.ipynb: same password present: False | rds endpoint present: True'; 'notebooks/05_habitable_zone.ipynb: same password present: False | rds endpoint present: False'. git ls-files confirms archive/database/Connect to AWS postgres.ipynb is tracked; git remote -v shows the GitHub origin.
