"""The TAP pull helper, tested without the network."""

from datetime import UTC, datetime

import pandas as pd

from kepler.fetch import COUNTS_QUERY, FULL_QUERY, read_tap_csv, save_pull, tap_url


def test_tap_url_matches_the_archive_format():
    assert tap_url(FULL_QUERY) == (
        "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select%20*%20from%20cumulative&format=csv"
    )
    assert "group%20by%20koi_disposition" in tap_url(COUNTS_QUERY)


def test_read_tap_csv_handles_quoted_strings():
    text = 'koi_disposition,n\n"CONFIRMED",2747\n"CANDIDATE",1978\n"FALSE POSITIVE",4839\n'
    df = read_tap_csv(text)
    assert df["n"].sum() == 9564
    assert list(df["koi_disposition"]) == ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]


def test_save_pull_writes_csv_and_provenance(tmp_path):
    df = pd.DataFrame(
        {"kepoi_name": ["K1.01", "K2.01"], "koi_disposition": ["CONFIRMED", "CANDIDATE"]}
    )
    when = datetime(2026, 8, 24, 12, 0, tzinfo=UTC)
    path = save_pull(df, when=when, out_dir=tmp_path)
    assert path.name == "cumulative_tap_2026-08-24.csv"
    prov = path.with_suffix(".provenance.json")
    assert prov.exists()
    text = prov.read_text()
    assert '"rows": 2' in text and '"sha256"' in text and '"CONFIRMED": 1' in text
