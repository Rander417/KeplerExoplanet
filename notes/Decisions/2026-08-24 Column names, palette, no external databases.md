---
tags: [decision, code, style]
date: 2026-08-24
status: accepted
---

# 2026-08-24 Column names, palette, no external databases

> [!abstract] Three conventions set while rewriting notebook 01
> 1. **Archive column names are canonical in code** (`koi_period`, `koi_prad`, …); readable labels are for charts only.
> 2. **Project palette:** green / amber / plum for CONFIRMED / CANDIDATE / FALSE POSITIVE, with marker shapes; no blue anywhere; single warm hue for magnitudes; purple–green for diverging.
> 3. **No external databases.** The 2020 Postgres/AWS layer is retired for good; the connection notebook is deleted from the tree.

## 1. Column names

**Decision.** `src/kepler/data.py` keeps the NASA Exoplanet Archive names exactly. `LABELS` maps them to readable labels with units for charts and tables; `LEGACY_NAMES` maps them to the 2020 names so the old pickles can still be compared (`preprocess.to_legacy_names`).

**Why.** The archive's column documentation, the TAP service (Phase 3), and every paper use the archive names; the 2020 renames (`Orbital_Period_[days]`, `Kepler_band [mag]`) contain brackets and spaces that make code awkward and differ between notebooks (01 and 05 used different maps). One vocabulary, documented once in `data/README.md`.

## 2. Palette (house rule: no blue except natural subjects)

**Decision.** `src/kepler/viz.py` defines the palette and `apply_style()`; every notebook calls it.

| Class | Colour | Marker |
|---|---|---|
| CONFIRMED | `#1f7a1f` green | ● |
| CANDIDATE | `#e08a00` amber | ▲ |
| FALSE POSITIVE | `#8b1e5f` plum | ■ |

- Validated 2026-08-24 with the dataviz palette checker (all pairs, light surface): colour-vision-deficiency separation ΔE 12.1 (target ≥ 8), normal-vision separation 27.5 (floor 15). Amber sits below 3:1 contrast on white, so charts always carry a legend or direct labels, and the marker shapes carry identity without colour.
- Magnitudes use one warm hue (`YlOrBr`); diverging scales use purple–white–green (`PRGn`); neutral bars use `#5a5a52`.
- matplotlib's default cycle starts with blue, so `apply_style()` replaces it.

## 3. No external databases

**Decision.** Rich does not intend to use external databases for this project. `archive/database/Connect to AWS postgres.ipynb` is deleted from the tree (its password was purged from history separately); the SQL schema files and ERD stay in `archive/database/` as a record of the 2020 design. Data lives in `data/raw/` (tracked) and `data/processed/` (regenerated), and Phase 3 pulls fresh tables straight from the archive's TAP service.

## Consequences

- Notebook 01 (rewritten 2026-08-24) uses these conventions; notebooks 02–05 adopt them as they are rewritten.
- `data/README.md` documents the naming rule and `data/processed/koi_clean.parquet`.
- The Roadmap item "Retire Postgres/ERD formally" is closed.
