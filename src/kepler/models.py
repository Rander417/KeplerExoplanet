"""Supervised baselines for the KOI disposition, stated honestly.

Everything here reports **macro f1 and per-class f1** alongside accuracy, and every
result names the feature set it used (see ``kepler.preprocess.FEATURE_SETS``).

``legacy_models`` rebuilds the three 2020 classifiers with their original
hyperparameters so the 2020 numbers can be reproduced on the 2020 split; the
cross-validation helpers are the honest version (scaler inside the pipeline,
folds instead of one lucky split).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from imblearn.ensemble import BalancedRandomForestClassifier
from sklearn.base import BaseEstimator, clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from kepler.data import CLASS_CODES, CLASSES
from kepler.preprocess import FLAG_COLUMNS

# The 2020 split: default 25% test, stratified, random_state=1 (notebook 03, cell 10).
LEGACY_SPLIT = {"test_size": 0.25, "random_state": 1}

# Columns whose distributions span decades; log1p before scaling helps linear models.
HEAVY_TAILED = [
    "koi_period",
    "koi_depth",
    "koi_prad",
    "koi_insol",
    "koi_model_snr",
    "koi_srad",
    "koi_duration",
]


def split(X: pd.DataFrame, y: pd.Series, **kwargs):
    """Stratified train/test split; defaults reproduce the 2020 split exactly."""
    params = {**LEGACY_SPLIT, **kwargs}
    return train_test_split(X, y, stratify=y, **params)


def legacy_models() -> dict[str, BaseEstimator]:
    """The three 2020 classifiers with their 2020 hyperparameters (without scalers).

    * Logistic regression: notebook 03 cell 14.
    * Gradient boosted trees: cell 25 (the final settings, not the sweep's).
    * Balanced random forest: cell 31, with imbalanced-learn 0.7's defaults spelled
      out because 0.13+ changed them (``sampling_strategy='all'``,
      ``replacement=True``, ``bootstrap=False``).
    """
    return {
        "logistic_regression": LogisticRegression(solver="lbfgs", max_iter=200, random_state=1),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=20, learning_rate=0.5, max_features=0.5, max_depth=3, random_state=0
        ),
        "balanced_random_forest": BalancedRandomForestClassifier(
            n_estimators=100,
            random_state=1,
            sampling_strategy="auto",
            replacement=False,
            bootstrap=True,
        ),
    }


def scaled(estimator: BaseEstimator) -> Pipeline:
    """StandardScaler fit inside the pipeline (so folds never see test statistics)."""
    return make_pipeline(StandardScaler(), clone(estimator))


def log1p_scaled(estimator: BaseEstimator, columns: list[str]) -> Pipeline:
    """log1p on the heavy-tailed columns present in ``columns``, then scale, then fit."""
    heavy = [c for c in columns if c in HEAVY_TAILED]
    other = [c for c in columns if c not in HEAVY_TAILED]
    transform = ColumnTransformer(
        [
            ("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one"), heavy),
            ("keep", "passthrough", other),
        ]
    )
    return make_pipeline(transform, StandardScaler(), clone(estimator))


@dataclass(frozen=True)
class Scores:
    accuracy: float
    balanced_accuracy: float
    f1_macro: float
    f1_weighted: float
    f1_per_class: dict[str, float]
    confusion: np.ndarray

    def as_row(self) -> dict[str, float]:
        row = {
            "accuracy": self.accuracy,
            "balanced_accuracy": self.balanced_accuracy,
            "f1_macro": self.f1_macro,
            "f1_weighted": self.f1_weighted,
        }
        row.update({f"f1_{name}": v for name, v in self.f1_per_class.items()})
        return row


def score(y_true, y_pred) -> Scores:
    """Every metric the 2020 project quoted, plus the ones it should have."""
    labels = [CLASS_CODES[c] for c in CLASSES]
    per_class = f1_score(y_true, y_pred, labels=labels, average=None)
    return Scores(
        accuracy=float(accuracy_score(y_true, y_pred)),
        balanced_accuracy=float(balanced_accuracy_score(y_true, y_pred)),
        f1_macro=float(f1_score(y_true, y_pred, average="macro")),
        f1_weighted=float(f1_score(y_true, y_pred, average="weighted")),
        f1_per_class={name: float(v) for name, v in zip(CLASSES, per_class, strict=True)},
        confusion=confusion_matrix(y_true, y_pred, labels=labels),
    )


def fit_and_score(pipeline: Pipeline, X_train, y_train, X_test, y_test) -> Scores:
    model = clone(pipeline).fit(X_train, y_train)
    return score(y_test, model.predict(X_test))


def flag_rule(X: pd.DataFrame, else_class: str = "CONFIRMED") -> np.ndarray:
    """The zero-parameter baseline: any vetting flag set -> FALSE POSITIVE, else ``else_class``.

    On the 2020 split this rule matches the full models' FALSE POSITIVE f1 (0.99),
    which is the leakage finding in one line of code.
    """
    any_flag = X[FLAG_COLUMNS].max(axis=1).to_numpy() > 0
    return np.where(any_flag, CLASS_CODES["FALSE POSITIVE"], CLASS_CODES[else_class])


def cv_macro_f1(
    pipeline: Pipeline, X, y, *, n_splits: int = 5, random_state: int = 0
) -> tuple[float, float, np.ndarray]:
    """Mean, std, and per-fold macro f1 from stratified k-fold CV."""
    folds = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    per_fold = cross_val_score(clone(pipeline), X, y, cv=folds, scoring="f1_macro")
    return float(per_fold.mean()), float(per_fold.std()), per_fold


# ---------------------------------------------------------------------------
# Phase 3: NaN-native gradient boosting on every row, tuned on validation folds
# ---------------------------------------------------------------------------

MISSING_SUFFIX = "_missing"


def add_missing_indicators(X: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Append ``<column>_missing`` (0/1) for every column that has any NaN.

    The NaNs themselves stay in place: ``HistGradientBoostingClassifier`` routes
    them natively, and the indicator lets the model use *that a value is missing*
    as information (in this table, missingness tracks the label).
    """
    out = X.copy()
    for c in columns or [c for c in X.columns if X[c].isna().any()]:
        out[f"{c}{MISSING_SUFFIX}"] = X[c].isna().astype("int64")
    return out


def hgb_model(random_state: int = 0, **params):
    """A histogram gradient-boosting classifier with sensible, NaN-friendly defaults."""
    from sklearn.ensemble import HistGradientBoostingClassifier

    defaults = {
        "learning_rate": 0.1,
        "max_iter": 500,
        "early_stopping": True,
        "validation_fraction": 0.15,
        "n_iter_no_change": 25,
        "class_weight": "balanced",
        "random_state": random_state,
    }
    return HistGradientBoostingClassifier(**{**defaults, **params})


HGB_GRID = {
    "learning_rate": [0.05, 0.1],
    "max_leaf_nodes": [15, 31, 63],
    "min_samples_leaf": [20, 50],
}


@dataclass(frozen=True)
class NestedCVResult:
    """Outer-fold metrics, the parameters each outer fold chose, and out-of-fold probabilities."""

    folds: pd.DataFrame
    params: list[dict]
    oof_proba: np.ndarray  # rows aligned with X, columns = class codes 0,1,2
    oof_pred: np.ndarray

    @property
    def summary(self) -> pd.Series:
        return self.folds.agg(["mean", "std"]).T.apply(
            lambda r: f"{r['mean']:.3f} ± {r['std']:.3f}", axis=1
        )


def nested_cv(
    estimator,
    grid: dict,
    X: pd.DataFrame,
    y: pd.Series,
    *,
    outer_splits: int = 5,
    inner_splits: int = 3,
    random_state: int = 0,
    scoring: str = "f1_macro",
) -> NestedCVResult:
    """Honest model selection: hyperparameters are chosen on inner folds of the
    training data only; every reported number comes from the outer test folds.
    """
    from sklearn.metrics import log_loss
    from sklearn.model_selection import GridSearchCV

    outer = StratifiedKFold(n_splits=outer_splits, shuffle=True, random_state=random_state)
    inner = StratifiedKFold(n_splits=inner_splits, shuffle=True, random_state=random_state)
    labels = [CLASS_CODES[c] for c in CLASSES]
    oof_proba = np.zeros((len(X), len(labels)))
    rows, params = [], []
    for fold, (tr, te) in enumerate(outer.split(X, y)):
        search = GridSearchCV(clone(estimator), grid, cv=inner, scoring=scoring, n_jobs=-1)
        search.fit(X.iloc[tr], y.iloc[tr])
        proba = search.predict_proba(X.iloc[te])
        oof_proba[te] = proba
        pred = np.asarray(labels)[proba.argmax(axis=1)]
        s = score(y.iloc[te], pred)
        rows.append(
            {
                "fold": fold,
                "f1_macro": s.f1_macro,
                "balanced_accuracy": s.balanced_accuracy,
                "accuracy": s.accuracy,
                **{f"f1_{name}": v for name, v in s.f1_per_class.items()},
                "log_loss": float(log_loss(y.iloc[te], proba, labels=labels)),
            }
        )
        params.append(search.best_params_)
    folds = pd.DataFrame(rows).set_index("fold")
    oof_pred = np.asarray(labels)[oof_proba.argmax(axis=1)]
    return NestedCVResult(folds=folds, params=params, oof_proba=oof_proba, oof_pred=oof_pred)


def reliability_table(y: pd.Series, proba: np.ndarray, n_bins: int = 10) -> pd.DataFrame:
    """One-vs-rest reliability points per class: predicted probability vs observed frequency."""
    rows = []
    edges = np.linspace(0, 1, n_bins + 1)
    for code, name in enumerate(CLASSES):
        p = proba[:, code]
        hit = (y.to_numpy() == code).astype(float)
        which = np.clip(np.digitize(p, edges) - 1, 0, n_bins - 1)
        for b in range(n_bins):
            m = which == b
            if m.sum() == 0:
                continue
            rows.append(
                {
                    "class": name,
                    "bin": b,
                    "predicted": float(p[m].mean()),
                    "observed": float(hit[m].mean()),
                    "count": int(m.sum()),
                }
            )
    return pd.DataFrame(rows)


def brier_multiclass(y: pd.Series, proba: np.ndarray) -> float:
    """Mean squared error between one-hot truth and probabilities, averaged over classes."""
    onehot = np.eye(proba.shape[1])[y.to_numpy()]
    return float(((proba - onehot) ** 2).sum(axis=1).mean())
