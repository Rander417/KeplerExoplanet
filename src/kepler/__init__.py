"""Kepler Objects of Interest analysis package.

Phase 1 (2026 refresh) only establishes the package and project paths.
Shared loading / preprocessing / habitable-zone code is extracted from the
notebooks in Phase 2 -> see notes/Roadmap.md.
"""

from kepler.paths import (
    DATA_LEGACY,
    DATA_PROCESSED,
    DATA_RAW,
    FIGURES,
    MODELS,
    NOTES,
    PROJECT_ROOT,
    REPORTS,
)

__all__ = [
    "DATA_LEGACY",
    "DATA_PROCESSED",
    "DATA_RAW",
    "FIGURES",
    "MODELS",
    "NOTES",
    "PROJECT_ROOT",
    "REPORTS",
]
