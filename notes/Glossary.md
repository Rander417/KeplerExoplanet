---
tags: [reference]
updated: 2026-08-24
---

# Glossary

The 2020 deck called this "the 382-page problem": Kepler's documentation is dense and the acronyms are cryptic. This note is the running decoder ring. Column definitions in quotation marks are quoted from the archive's [Data Columns in Kepler Objects of Interest Table](https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html); the full column-by-column mapping to the 2020 names lives in the [data README](../data/README.md).

## Mission and catalog terms

**Kepler** — NASA space telescope (2009–2018) that stared at one field in Cygnus/Lyra and measured stellar brightness continuously to find planets by the transit method. Its photometer had 21 CCD modules with two 2200x1024-pixel CCDs each (the 2020 deck cites the [Kepler Science Center](https://keplerscience.arc.nasa.gov/the-kepler-space-telescope.html) for this).

**KIC — Kepler Input Catalog** — the catalog of stars in the Kepler field. `kepid` is the KIC number: "Target identification number, as listed in the Kepler Input Catalog (KIC)."

**TCE — Threshold Crossing Event** — a periodic transit-like signal found by the Kepler pipeline that exceeds its detection threshold. KOIs are promoted from TCEs. `koi_tce_delivname` records which pipeline delivery (e.g. `q1_q17_dr25_tce`) the KOI's TCE came from; `koi_tce_plnt_num` is the planet number within that star's TCEs.

**KOI — Kepler Object of Interest** — a TCE that passed initial vetting and is tracked as a possible planet. `kepoi_name` looks like `K00752.01` (star K00752, first candidate). "A number used to identify and track a Kepler Object of Interest (KOI)."

**Kepler-N b** — the name a KOI receives once confirmed as a planet, e.g. Kepler-90 g. Stored in `kepler_name`; empty for candidates and false positives.

**Q1–Q17, DR24, DR25** — Kepler observed in ~90-day *quarters* (Q1–Q17). *Data Release 25* is the final processing of all 17 quarters and the basis of the final KOI catalog; most rows in our table (8,054 of 9,564) come from the DR25 delivery, the rest from the earlier Q1–Q16 and DR24 runs.

**Robovetter** — the automated vetting software that turned DR24/DR25 TCEs into planet candidates or false positives and recorded *why* (the four flags below). Its Monte-Carlo variant produces the disposition score.

**Cumulative KOI table** — the archive's merged, continuously updated table of all KOIs from every delivery, with the current best disposition for each. This is the table the whole project uses. Live access: [TAP service](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html), table name `cumulative`.

**TAP / ADQL** — Table Access Protocol, the archive's query interface; queries are written in ADQL (an SQL dialect). Example: `select+*+from+cumulative&format=csv`.

## The dispositions ("a tale of two Ys")

**`koi_pdisposition` — Disposition Using Kepler Data** — "The pipeline flag that designates the most probable physical explanation of the KOI." Two values: CANDIDATE or FALSE POSITIVE. This is the Robovetter's verdict from Kepler data alone.

**`koi_disposition` — Exoplanet Archive Disposition** — "The category of this KOI from the Exoplanet Archive." Three values in our data: CONFIRMED, CANDIDATE, FALSE POSITIVE. Adds follow-up observations and published confirmations on top of the pipeline verdict. **This is the project's target variable.**

**`koi_score` — Disposition Score** — "A value between 0 and 1 that indicates the confidence in the KOI disposition." In the Kaggle snapshot the median is 0.000 for FALSE POSITIVE and 1.000 for CONFIRMED, so it is essentially a second copy of the label; the 2020 pipeline dropped it from the features (correctly).

**False-positive flags** — the Robovetter's four reasons. Any one of them set means the pipeline called it a false positive:

| Column | Meaning (quoted) |
|---|---|
| `koi_fpflag_nt` Not Transit-Like | "A KOI whose light curve is not consistent with that of a transiting planet." |
| `koi_fpflag_ss` Stellar Eclipse | "A KOI that is observed to have a significant secondary event, transit shape, or out-of-eclipse variability." |
| `koi_fpflag_co` Centroid Offset | "The source of the signal is from a nearby star, as inferred by measuring the centroid location." |
| `koi_fpflag_ec` Ephemeris Match | "The KOI shares the same period and epoch as another object and is judged to result from flux contamination." |

Because these flags *are* the vetting logic, feeding them to a classifier is [target leakage](#machine-learning-terms). See the [reconnaissance entry](Research%20Log/2026-08-24%20Restart%20reconnaissance.md) for the numbers.

## Transit and planet quantities

**Transit** — a planet passing in front of its star as seen from the telescope, dimming the star slightly and periodically.

**Transit depth (`koi_depth`, ppm)** — "The fraction of stellar flux lost at the minimum of the planetary transit," in parts per million. To first order depth ≈ (R_planet / R_star)²; Earth crossing the Sun gives (6,371 km / 695,700 km)² ≈ 84 ppm, which is why Kepler needed such precise photometry.

**Orbital period (`koi_period`, days)** — "The interval between consecutive planetary transits."

**Transit epoch (`koi_time0bk`, BKJD)** — time of the first detected transit centre. BKJD is *Barycentric Kepler Julian Date* = BJD − 2,454,833.0, a Kepler-specific offset that keeps the numbers small.

**Transit duration (`koi_duration`, hours)** — "The duration of the observed transits, measured from first contact until last contact."

**Impact parameter (`koi_impact`)** — "The sky-projected distance between the center of the stellar disc and center of planet disc," in units of the stellar radius: 0 is a central crossing, values near 1 are grazing.

**Planetary radius (`koi_prad`, Earth radii)** — "The radius of the planet, calculated as the product of planet-star radius ratio and stellar radius." Note the dependence on the *stellar* radius: if the star's radius is revised, so is the planet's.

**Insolation flux (`koi_insol`, Earth flux)** — "Insolation flux given in units relative to those measured for Earth from the Sun." The stellar energy the planet receives; 1.0 means Earth-like. This, not orbital period, is the quantity habitable-zone limits are defined on.

**Equilibrium temperature (`koi_teq`, K)** — "Approximation for the temperature of the planet based on incident stellar flux equilibrium." A no-atmosphere estimate; Earth's is about 255 K versus a real surface mean near 288 K.

**Transit signal-to-noise (`koi_model_snr`)** — "Transit depth normalized by the mean uncertainty in the flux during the transits."

## Stellar quantities

**Effective temperature (`koi_steff`, K)** — "The photospheric temperature of the star." The Sun is about 5,772 K.

**Surface gravity (`koi_slogg`, log10 cm/s²)** — "The base-10 logarithm of the acceleration due to gravity at the surface of the star." Around 4.4 for the Sun; low values indicate giants.

**Stellar radius (`koi_srad`, solar radii)** and **mass (`koi_smass`, solar masses)** — "The photospheric radius of the star." / "The mass of the star."

**Metallicity (`koi_smet`, dex)** — "The base-10 logarithm of the Fe to H ratio at the star surface, normalized by solar ratio." 0 means solar; positive is metal-rich.

**Kepler magnitude (`koi_kepmag`)** — brightness in Kepler's bandpass; larger numbers are fainter.

**RA / Dec** — right ascension and declination, the sky's longitude and latitude, in decimal degrees.

## Habitable zone

**Habitable zone (HZ)** — the range of distances from a star where an Earth-like planet could keep liquid water on its surface. The standard modern reference is [Kopparapu et al. 2013](https://arxiv.org/abs/1301.6674), whose abstract states: "the water loss (inner HZ) and maximum greenhouse (outer HZ) limits for our Solar System are at 0.99 AU and 1.70 AU, respectively." Converted to insolation (flux ∝ 1/distance²) that is ≈1.02 and ≈0.35 Earth-flux for a Sun-like star; the paper gives temperature-dependent coefficients for other stars, and *optimistic* limits based on "recent Venus" and "early Mars". The 2020 project used a box filter on period, temperature, radius, gravity and metallicity instead, which finds Sun-like stars with Earth-like years rather than temperate planets; Phase 4 replaces it.

**Goldilocks zone** — the same thing, for slide titles.

## Machine-learning terms used in this project

**f1 score** — harmonic mean of precision and recall for a class; the project's headline metric (macro/weighted variants must be stated).

**Class imbalance** — FALSE POSITIVE outnumbers each of the other two classes roughly 2:1 in the snapshot; the 2020 work used a *balanced* random forest (`imbalanced-learn`) partly for this reason.

**Target leakage** — when a feature contains information that is only available *because* the label is known. The FP flags are the textbook case here.

**SFS — Sequential Feature Selection** — greedily adds (or removes) features one at a time, scoring each subset; the 2020 notebooks used `mlxtend`'s implementation.

**PCA** — Principal Component Analysis, a rotation of the features onto directions of maximum variance; the 2020 deck noted "36% of the information is lost reducing four dimensions to two".

**k-means / elbow curve** — clustering into k groups; the elbow is where adding clusters stops reducing within-cluster variance much. The 2020 deck reported elbows at 4 (raw features) and, separately, after PCA.

**Balanced random forest / gradient-boosted trees / logistic regression** — the three scikit-learn-family models in `03_sklearn_models.ipynb`.
