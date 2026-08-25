"""Assemble the static site that GitHub Pages serves (Streamlit-in-the-browser via stlite).

    python app/build_site.py site            # writes ./site (only the standard library is used)

The site is index.html plus the files app/index.html mounts, at the same relative
paths as in the repository. Keep APP_FILES in sync with the list in index.html;
``tests/test_app.py`` checks that they match.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

APP_FILES = [
    "app/app.py",
    "app/data/koi_table.csv",
    "app/data/summary.json",
    "app/model/hgb_physics_only.json",
    "src/kepler/__init__.py",
    "src/kepler/paths.py",
    "src/kepler/data.py",
    "src/kepler/habitable.py",
    "src/kepler/palette.py",
    "src/kepler/portable.py",
    "src/kepler/verdict.py",
]


def build(out: Path) -> list[Path]:
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    written = []
    for rel in ["app/index.html", *APP_FILES]:
        src = ROOT / rel
        if not src.exists():
            raise FileNotFoundError(f"{rel} is missing; run `python -m kepler.app_bundle` first?")
        dest = out / ("index.html" if rel == "app/index.html" else rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        written.append(dest)
    (out / ".nojekyll").write_text("")  # serve __init__.py and friends verbatim
    return written


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    files = build(target)
    total = sum(f.stat().st_size for f in files)
    print(f"wrote {len(files)} files ({total / 1e6:.1f} MB) to {target}/")
