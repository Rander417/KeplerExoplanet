"""Pull the live KOI cumulative table from the NASA Exoplanet Archive (TAP service).

Documentation: https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html
Table name: ``cumulative``. The service returns CSV for
``.../TAP/sync?query=<ADQL>&format=csv``.

Run on a machine that can reach the archive (the Cowork sandbox cannot):

    uv run python -m kepler.fetch            # full pull -> data/raw/cumulative_tap_YYYY-MM-DD.csv
    uv run python -m kepler.fetch --counts   # just the disposition counts, nothing written
    uv run python -m kepler.fetch --dry-run  # print the URL and exit

Every pull writes a ``.provenance.json`` next to the CSV (URL, UTC timestamp, rows,
columns, SHA-256) so a result can always be tied to the exact file.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

import pandas as pd

from kepler.paths import DATA_RAW

TAP_SYNC = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
TABLE = "cumulative"
FULL_QUERY = f"select * from {TABLE}"
COUNTS_QUERY = f"select koi_disposition, count(*) as n from {TABLE} group by koi_disposition"


def tap_url(query: str = FULL_QUERY, fmt: str = "csv") -> str:
    """The sync-TAP URL for an ADQL query (spaces become ``+`` as in the archive's examples)."""
    return f"{TAP_SYNC}?query={quote(query, safe='*(),=')}&format={fmt}"


def read_tap_csv(text: str) -> pd.DataFrame:
    """Parse the CSV text the service returns (quoted strings, plain numbers)."""
    return pd.read_csv(io.StringIO(text))


def fetch(query: str = FULL_QUERY, timeout: int = 300) -> pd.DataFrame:
    import requests

    response = requests.get(tap_url(query), timeout=timeout)
    response.raise_for_status()
    return read_tap_csv(response.text)


def save_pull(df: pd.DataFrame, when: datetime | None = None, out_dir: Path = DATA_RAW) -> Path:
    when = when or datetime.now(UTC)
    stamp = when.strftime("%Y-%m-%d")
    path = out_dir / f"cumulative_tap_{stamp}.csv"
    df.to_csv(path, index=False)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    provenance = {
        "source": tap_url(FULL_QUERY),
        "table": TABLE,
        "pulled_at_utc": when.isoformat(timespec="seconds"),
        "rows": len(df),
        "columns": int(df.shape[1]),
        "sha256": digest,
        "koi_disposition_counts": df["koi_disposition"].value_counts().to_dict()
        if "koi_disposition" in df
        else None,
    }
    path.with_suffix(".provenance.json").write_text(json.dumps(provenance, indent=2))
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--counts", action="store_true", help="only print disposition counts")
    parser.add_argument("--dry-run", action="store_true", help="print the URL and exit")
    args = parser.parse_args(argv)
    if args.dry_run:
        print(tap_url(COUNTS_QUERY if args.counts else FULL_QUERY))
        return 0
    if args.counts:
        print(fetch(COUNTS_QUERY).to_string(index=False))
        return 0
    df = fetch()
    path = save_pull(df)
    print(f"wrote {path} ({len(df):,} rows x {df.shape[1]} columns)")
    print(df["koi_disposition"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
