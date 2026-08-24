"""Project paths, resolved relative to this file so notebooks and scripts
work no matter which directory they are launched from.

Usage in a notebook:
    from kepler.paths import DATA_RAW
    df = pd.read_csv(DATA_RAW / "cumulative_kaggle_snapshot.csv")
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA = PROJECT_ROOT / "data"

# Source files exactly as downloaded (tracked in git)
DATA_RAW = DATA / "raw"

# Regenerable outputs (ignored by git)
DATA_PROCESSED = DATA / "processed"

# Pickles produced by the 2020 notebooks, kept for regression checks
DATA_LEGACY = DATA / "legacy"

# Trained artifacts (ignored by git)
MODELS = PROJECT_ROOT / "models"

REPORTS = PROJECT_ROOT / "reports"
FIGURES = REPORTS / "figures"

# The Obsidian vault is the repo root; notes/ is its notes folder
NOTES = PROJECT_ROOT / "notes"

# Legacy artifact names produced by the 2020 pipeline (see data/README.md)
LEGACY_PICKLES = {
    "raw": DATA_LEGACY / "kepler_RAW.pkl",
    "clean_full": DATA_LEGACY / "kepler_clean_full.pkl",
    "processed": DATA_LEGACY / "kepler_processed.pkl",
    "habitable_confirmed": DATA_LEGACY / "habitable_Confirmed_exoplanets.pkl",
    "habitable_candidates": DATA_LEGACY / "habitable_Candidate_Objects.pkl",
}
