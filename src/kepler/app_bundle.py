"""Build everything the app ships with, from the latest live pull.

    uv run python -m kepler.app_bundle          # writes app/data/* and app/model/*

The app never trains anything. This script trains the notebook-07 physics-only
model on **today's labels**, calibrates it out-of-fold, exports it as plain
numbers (``kepler.portable``), scores every KOI out-of-fold, runs the notebook-08
out-of-time test, computes the habitable-zone flags, and writes:

    app/data/koi_table.csv        one row per KOI: identity, physics, HZ flags,
                                  out-of-fold probabilities and the rule's verdict
    app/data/summary.json         provenance (sources, hashes, versions) + every
                                  number the app quotes (metrics, transitions, HZ)
    app/model/hgb_physics_only.json   the exported model with its column contract

"Out-of-fold" means each KOI's probability comes from a model that never saw its
label (5 stratified folds, fixed seed), so the catalogue is not an in-sample fit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold

from kepler import data, habitable, preprocess
from kepler.data import CLASS_CODES, CLASSES, TARGET
from kepler.models import add_missing_indicators, brier_multiclass, hgb_model
from kepler.paths import DATA_RAW, PROJECT_ROOT
from kepler.portable import IsotonicMap, PortableHGB
from kepler.preprocess import FLAG_COLUMNS, PHYSICS_COLUMNS
from kepler.verdict import PLANET_LIKE_THRESHOLD, planet_like, verdict

APP_DIR = PROJECT_ROOT / "app"
TABLE_NAME = "data/koi_table.csv"
SUMMARY_NAME = "data/summary.json"
MODEL_NAME = "model/hgb_physics_only.json"

# Notebook 07's most-chosen hyperparameters (nested CV, physics-only)
BEST_PARAMS = {"learning_rate": 0.05, "max_leaf_nodes": 31, "min_samples_leaf": 20}
N_FOLDS = 5
SEED = 0

IDENTITY_COLUMNS = ["kepid", "kepler_name", "koi_pdisposition", "koi_score", "ra", "dec"]
ERROR_COLUMNS = ["koi_prad_err1", "koi_prad_err2", "koi_insol_err1", "koi_insol_err2"]
HZ_COLUMNS = [
    "seff_recent_venus",
    "seff_runaway_greenhouse",
    "seff_maximum_greenhouse",
    "seff_early_mars",
    "teff_in_range",
    "hz_conservative",
    "hz_optimistic",
    "hz_conservative_possible",
    "rocky",
    "super_earth",
    "sunlike_host",
    "grazing",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def folds(y: pd.Series) -> list[tuple[np.ndarray, np.ndarray]]:
    return list(StratifiedKFold(N_FOLDS, shuffle=True, random_state=SEED).split(y, y))


def oof_raw(X: pd.DataFrame, y: pd.Series, params: dict) -> tuple[np.ndarray, list[float]]:
    """Out-of-fold decision-function scores and the per-fold macro f1 of their argmax."""
    raw = np.zeros((len(X), len(CLASSES)))
    fold_f1 = []
    for train, test in folds(y):
        model = hgb_model(**params).fit(X.iloc[train], y.iloc[train])
        raw[test] = model.decision_function(X.iloc[test])
        fold_f1.append(float(f1_score(y.iloc[test], raw[test].argmax(axis=1), average="macro")))
    return raw, fold_f1


def softmax(raw: np.ndarray) -> np.ndarray:
    z = raw - raw.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def fit_isotonic(raw: np.ndarray, y: pd.Series) -> list[IsotonicMap]:
    """One isotonic map per class on the out-of-fold scores (what CalibratedClassifierCV does)."""
    from sklearn.isotonic import IsotonicRegression

    maps = []
    for k in range(len(CLASSES)):
        iso = IsotonicRegression(out_of_bounds="clip").fit(raw[:, k], (y.to_numpy() == k))
        maps.append(IsotonicMap.from_sklearn(iso))
    return maps


def apply_calibration(raw: np.ndarray, maps: list[IsotonicMap]) -> np.ndarray:
    proba = np.column_stack([m(raw[:, k]) for k, m in enumerate(maps)])
    denominator = proba.sum(axis=1, keepdims=True)
    uniform = np.full_like(proba, 1 / proba.shape[1])
    return np.divide(proba, denominator, out=uniform, where=denominator != 0)


def reliability(p: np.ndarray, hit: np.ndarray, n_bins: int = 10) -> list[dict]:
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, n_bins - 1)
    rows = []
    for b in range(n_bins):
        m = idx == b
        if m.any():
            rows.append(
                {
                    "bin_low": float(edges[b]),
                    "bin_high": float(edges[b + 1]),
                    "n": int(m.sum()),
                    "mean_predicted": float(p[m].mean()),
                    "observed": float(hit[m].mean()),
                }
            )
    return rows


def binary_at(p: np.ndarray, is_planet: np.ndarray, thr: float) -> dict:
    pred = p >= thr
    return {
        "threshold": thr,
        "precision": float(precision_score(is_planet, pred, zero_division=0)),
        "recall": float(recall_score(is_planet, pred, zero_division=0)),
        "f1": float(f1_score(is_planet, pred, zero_division=0)),
        "n_planet_like": int(pred.sum()),
    }


def build(out_dir: Path = APP_DIR, live_path: Path | None = None, *, quick: bool = False) -> dict:
    """Train, export, score, and write the bundle. Returns the summary dict.

    ``quick=True`` shrinks the model (for tests); never ship a quick bundle.
    """
    params = dict(BEST_PARAMS)
    if quick:
        params.update(max_iter=20, early_stopping=False, max_leaf_nodes=15)

    # ------------------------------------------------------------ data
    live_path = live_path or data.tap_pulls()[-1]
    live = data.load_tap_pull(live_path)
    snap = data.load_kaggle_snapshot()
    if set(live.index) != set(snap.index):
        raise ValueError("live pull and snapshot do not cover the same KOIs")
    live = live.loc[snap.index]
    prov_path = live_path.with_suffix(".provenance.json")
    live_prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}

    table = preprocess.model_table(preprocess.clean(live), "physics_only", dropna=False)
    X = add_missing_indicators(table.X)
    y_live = table.y
    y_snap = snap.loc[X.index, TARGET].map(CLASS_CODES).astype("int64")
    columns = list(X.columns)

    # ------------------------------------------------------------ live-label model
    raw_live, fold_f1_live = oof_raw(X, y_live, params)
    maps = fit_isotonic(raw_live, y_live)
    final = hgb_model(**params).fit(X, y_live)
    model = PortableHGB.from_sklearn(final, columns, list(CLASSES))
    model.calibrators = maps

    # cross-check against scikit-learn's own implementation of the same recipe
    reference = CalibratedClassifierCV(
        hgb_model(**params),
        method="isotonic",
        cv=StratifiedKFold(N_FOLDS, shuffle=True, random_state=SEED),
        ensemble=False,
    ).fit(X, y_live)
    ref_export = PortableHGB.from_sklearn(reference, columns, list(CLASSES))
    max_diff = float(np.abs(model.predict_proba(X) - reference.predict_proba(X)).max())
    if max_diff > 1e-9:
        raise RuntimeError(f"export disagrees with CalibratedClassifierCV by {max_diff:.2e}")
    del ref_export

    # ------------------------------------------------------------ out-of-fold scores
    p_uncal = softmax(raw_live)
    p_cal = apply_calibration(raw_live, maps)
    y_arr = y_live.to_numpy()
    is_planet = y_arr != CLASS_CODES["FALSE POSITIVE"]
    p_planet = planet_like(p_cal)
    rule = verdict(p_cal)
    rule_codes = np.array([CLASS_CODES[v] for v in rule])
    class_names = list(CLASSES)

    metrics = {
        "labels": "koi_disposition (live pull)",
        "n_rows": len(X),
        "class_counts": {c: int((y_arr == CLASS_CODES[c]).sum()) for c in class_names},
        "cv_macro_f1_physics_only": {
            "mean": float(np.mean(fold_f1_live)),
            "std": float(np.std(fold_f1_live)),
            "folds": fold_f1_live,
        },
        "oof_macro_f1": {
            "uncalibrated_argmax": float(f1_score(y_arr, p_uncal.argmax(axis=1), average="macro")),
            "calibrated_argmax": float(f1_score(y_arr, p_cal.argmax(axis=1), average="macro")),
            "rule": float(f1_score(y_arr, rule_codes, average="macro")),
        },
        "rule_per_class_f1": dict(
            zip(class_names, f1_score(y_arr, rule_codes, average=None).tolist(), strict=True)
        ),
        "rule_confusion": {
            "rows": "true class",
            "columns": "rule verdict",
            "classes": class_names,
            "matrix": confusion_matrix(y_arr, rule_codes, labels=[0, 1, 2]).tolist(),
        },
        "calibration": {
            "log_loss_uncalibrated": float(log_loss(y_arr, p_uncal, labels=[0, 1, 2])),
            "log_loss_calibrated": float(log_loss(y_arr, p_cal, labels=[0, 1, 2])),
            "brier_uncalibrated": float(brier_multiclass(y_live, p_uncal)),
            "brier_calibrated": float(brier_multiclass(y_live, p_cal)),
            "reliability_planet_like": reliability(p_planet, is_planet),
            "note": (
                "Isotonic maps are fit on these same out-of-fold scores, so the "
                "calibrated numbers are mildly optimistic for the calibrator itself."
            ),
        },
        "planet_like": {
            "auc": float(roc_auc_score(is_planet, p_planet)),
            "thresholds": [binary_at(p_planet, is_planet, t) for t in (0.3, 0.5, 0.7, 0.9)],
            "default_threshold": PLANET_LIKE_THRESHOLD,
        },
    }

    # ------------------------------------------------------------ flags on live labels (leakage)
    if not quick:
        Xf = add_missing_indicators(X[PHYSICS_COLUMNS].join(live.loc[X.index, FLAG_COLUMNS]))
        _, fold_f1_flags = oof_raw(Xf, y_live, params)
        metrics["cv_macro_f1_with_flags"] = {
            "mean": float(np.mean(fold_f1_flags)),
            "std": float(np.std(fold_f1_flags)),
            "folds": fold_f1_flags,
        }

    # ------------------------------------------------------------ out-of-time (2020 labels)
    raw_snap, fold_f1_snap = oof_raw(X, y_snap, params)
    p_planet_2020 = planet_like(softmax(raw_snap))
    was_cand = (y_snap == CLASS_CODES["CANDIDATE"]).to_numpy()
    later = y_live.to_numpy()[was_cand]
    p20 = p_planet_2020[was_cand]
    decided = later != CLASS_CODES["CANDIDATE"]
    metrics["out_of_time"] = {
        "description": (
            "Physics-only model trained on 2020 labels (out-of-fold) scored the 2020 "
            "CANDIDATEs; the archive decided some of them later."
        ),
        "cv_macro_f1_snapshot_labels": {
            "mean": float(np.mean(fold_f1_snap)),
            "std": float(np.std(fold_f1_snap)),
        },
        "n_candidates_2020": int(was_cand.sum()),
        "later": {
            "CONFIRMED": int((later == CLASS_CODES["CONFIRMED"]).sum()),
            "CANDIDATE": int((later == CLASS_CODES["CANDIDATE"]).sum()),
            "FALSE POSITIVE": int((later == CLASS_CODES["FALSE POSITIVE"]).sum()),
        },
        "median_p_planet_like": {
            c: float(np.median(p20[later == CLASS_CODES[c]])) for c in class_names
        },
        "auc_confirmed_vs_false_positive": float(
            roc_auc_score((later[decided] == CLASS_CODES["CONFIRMED"]), p20[decided])
        ),
    }

    # ------------------------------------------------------------ transitions + HZ
    trans = pd.crosstab(snap.loc[X.index, TARGET], live.loc[X.index, TARGET]).reindex(
        index=class_names, columns=class_names, fill_value=0
    )
    hz = habitable.hz_table(live.loc[X.index])
    confirmed = hz[hz[TARGET] == "CONFIRMED"]
    candidates = hz[hz[TARGET] == "CANDIDATE"]
    hz_summary = {
        "confirmed_conservative_le_2": int(
            (confirmed.hz_conservative & confirmed.super_earth).sum()
        ),
        "confirmed_conservative_le_1_6": int((confirmed.hz_conservative & confirmed.rocky).sum()),
        "confirmed_optimistic_le_2": int((confirmed.hz_optimistic & confirmed.super_earth).sum()),
        "candidates_conservative_le_2": int(
            (candidates.hz_conservative & candidates.super_earth).sum()
        ),
        "candidates_optimistic_le_2": int(
            (candidates.hz_optimistic & candidates.super_earth).sum()
        ),
        "teff_out_of_range": int((~hz.teff_in_range).sum()),
    }

    # ------------------------------------------------------------ the table
    out = pd.DataFrame(index=X.index)
    for c in IDENTITY_COLUMNS:
        out[c] = live.loc[X.index, c]
    out[TARGET] = live.loc[X.index, TARGET]
    out[TARGET + "_2020"] = snap.loc[X.index, TARGET]
    for c in PHYSICS_COLUMNS + ERROR_COLUMNS:
        out[c] = live.loc[X.index, c]
    for c in HZ_COLUMNS:
        out[c] = hz.loc[X.index, c]
    out["p_candidate"] = p_cal[:, 0]
    out["p_confirmed"] = p_cal[:, 1]
    out["p_false_positive"] = p_cal[:, 2]
    out["p_planet_like"] = p_planet
    out["model_verdict"] = rule
    out["p_planet_like_2020model"] = p_planet_2020
    for c in (
        "p_candidate",
        "p_confirmed",
        "p_false_positive",
        "p_planet_like",
        "p_planet_like_2020model",
    ):
        out[c] = out[c].round(5)

    # ------------------------------------------------------------ write
    out_dir = Path(out_dir)
    (out_dir / "data").mkdir(parents=True, exist_ok=True)
    (out_dir / "model").mkdir(parents=True, exist_ok=True)
    built_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    snapshot_path = DATA_RAW / "cumulative_kaggle_snapshot.csv"
    model.meta = {
        "name": "physics-only HistGradientBoosting, isotonic calibration (ensemble=False)",
        "feature_set": "physics_only",
        "params": {k: (float(v) if isinstance(v, float) else v) for k, v in params.items()},
        "n_iterations": model.n_iterations,
        "n_nodes": model.n_nodes,
        "trained_on": {"file": live_path.name, "sha256": live_prov.get("sha256"), "rows": len(X)},
        "labels": TARGET,
        "calibration": f"isotonic on {N_FOLDS}-fold out-of-fold decision scores",
        "sklearn_version": sklearn.__version__,
        "built_at_utc": built_at,
        "quick": quick,
        "export_check_max_abs_diff_vs_sklearn": max_diff,
    }
    model.save(out_dir / MODEL_NAME)
    out.to_csv(out_dir / TABLE_NAME)

    summary = {
        "built_at_utc": built_at,
        "quick": quick,
        "sources": {
            "live": {
                "file": live_path.name,
                "sha256": live_prov.get("sha256") or sha256(live_path),
                "pulled_at_utc": live_prov.get("pulled_at_utc"),
                "source": live_prov.get("source"),
            },
            "snapshot": {"file": snapshot_path.name, "sha256": sha256(snapshot_path)},
        },
        "versions": {
            "python": platform.python_version(),
            "scikit-learn": sklearn.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "table": {"rows": len(out), "columns": list(out.columns)},
        "model": {k: v for k, v in model.meta.items() if k != "params"}
        | {"params": model.meta["params"]},
        "metrics": metrics,
        "transitions": {
            "rows": "2020 snapshot",
            "columns": "live",
            "classes": class_names,
            "matrix": trans.to_numpy().tolist(),
        },
        "habitable_zone": hz_summary,
    }
    (out_dir / SUMMARY_NAME).write_text(json.dumps(summary, indent=1), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--out", type=Path, default=APP_DIR, help="app directory (default: app/)")
    ap.add_argument(
        "--live", type=Path, default=None, help="a specific data/raw/cumulative_tap_*.csv"
    )
    ap.add_argument("--quick", action="store_true", help="tiny model for smoke tests; never ship")
    args = ap.parse_args(argv)
    summary = build(args.out, args.live, quick=args.quick)
    m = summary["metrics"]
    print(
        f"wrote {args.out / TABLE_NAME} ({summary['table']['rows']:,} rows), {args.out / MODEL_NAME}, {args.out / SUMMARY_NAME}"
    )
    print(
        f"physics-only, live labels: CV macro f1 {m['cv_macro_f1_physics_only']['mean']:.3f} "
        f"± {m['cv_macro_f1_physics_only']['std']:.3f}; rule macro f1 {m['oof_macro_f1']['rule']:.3f}; "
        f"planet-like AUC {m['planet_like']['auc']:.3f}; out-of-time AUC "
        f"{m['out_of_time']['auc_confirmed_vs_false_positive']:.3f}"
    )


if __name__ == "__main__":
    main()
