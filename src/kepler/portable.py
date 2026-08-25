"""A scikit-learn-free copy of a fitted gradient-boosting model, for the app.

Why this exists
---------------
The app has to run in places where scikit-learn is either absent or a different
version from the one that trained the model: Streamlit running *inside a browser*
(stlite on Pyodide) and Streamlit Community Cloud. Loading a pickle across
versions is fragile and slow to debug, and retraining in a browser takes minutes.

So the trained model is exported once, as plain numbers: every tree's split
features, thresholds, child indices and leaf values, plus the isotonic
calibration maps. This module evaluates that export with numpy only.
``tests/test_portable.py`` proves the copy reproduces scikit-learn's
probabilities on every KOI, so the app is the same model as the notebooks.

What is reproduced
------------------
* ``HistGradientBoostingClassifier`` prediction: start from the baseline score,
  add every tree's leaf value, softmax across classes. The tree-walk rule is the
  library's own: a NaN follows ``missing_go_to_left``; otherwise ``x <= threshold``
  goes left. (See ``sklearn/ensemble/_hist_gradient_boosting/_predictor.pyx``.)
* ``CalibratedClassifierCV(method="isotonic", ensemble=False)``: one isotonic map
  per class applied to the raw (decision-function) score, then the rows are
  normalised to sum to one. (See ``_CalibratedClassifier.predict_proba``.)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

FORMAT_VERSION = 1
MISSING_SUFFIX = "_missing"  # same convention as kepler.models.add_missing_indicators


@dataclass(frozen=True)
class Tree:
    """One decision tree as parallel arrays indexed by node; leaves have ``left == -1``."""

    feature: np.ndarray  # int, split feature index (ignored at leaves)
    threshold: np.ndarray  # float, go left when x <= threshold
    left: np.ndarray  # int, child index, -1 at leaves
    right: np.ndarray  # int, child index, -1 at leaves
    value: np.ndarray  # float, leaf value (learning rate already folded in)
    missing_left: np.ndarray  # bool, where a NaN goes

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Leaf value for every row of ``X`` (float array, NaN allowed), vectorised.

        All rows walk the tree together: at each step every row that has not
        reached a leaf moves to its left or right child.
        """
        n = X.shape[0]
        rows = np.arange(n)
        node = np.zeros(n, dtype=np.int64)
        while True:
            at_leaf = self.left[node] < 0
            if at_leaf.all():
                return self.value[node]
            x = X[rows, self.feature[node]]
            go_left = np.where(np.isnan(x), self.missing_left[node], x <= self.threshold[node])
            step = np.where(go_left, self.left[node], self.right[node])
            node = np.where(at_leaf, node, step)

    def to_dict(self) -> dict:
        return {
            "feature": self.feature.tolist(),
            "threshold": self.threshold.tolist(),
            "left": self.left.tolist(),
            "right": self.right.tolist(),
            "value": self.value.tolist(),
            "missing_left": self.missing_left.astype(int).tolist(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> Tree:
        return cls(
            feature=np.asarray(d["feature"], dtype=np.int64),
            threshold=np.asarray(d["threshold"], dtype=float),
            left=np.asarray(d["left"], dtype=np.int64),
            right=np.asarray(d["right"], dtype=np.int64),
            value=np.asarray(d["value"], dtype=float),
            missing_left=np.asarray(d["missing_left"], dtype=bool),
        )

    @classmethod
    def from_sklearn_nodes(cls, nodes: np.ndarray) -> Tree:
        """Convert a ``TreePredictor.nodes`` structured array."""
        is_leaf = nodes["is_leaf"].astype(bool)
        left = nodes["left"].astype(np.int64)  # unsigned in sklearn; widen before using -1
        right = nodes["right"].astype(np.int64)
        return cls(
            feature=nodes["feature_idx"].astype(np.int64),
            threshold=nodes["num_threshold"].astype(float),
            left=np.where(is_leaf, -1, left),
            right=np.where(is_leaf, -1, right),
            value=nodes["value"].astype(float),
            missing_left=nodes["missing_go_to_left"].astype(bool),
        )


@dataclass(frozen=True)
class IsotonicMap:
    """A fitted isotonic regression: clip to the fitted range, then interpolate linearly."""

    x: np.ndarray
    y: np.ndarray

    def __call__(self, t: np.ndarray) -> np.ndarray:
        t = np.clip(np.asarray(t, dtype=float), self.x[0], self.x[-1])
        return np.interp(t, self.x, self.y)

    def to_dict(self) -> dict:
        return {"x": self.x.tolist(), "y": self.y.tolist()}

    @classmethod
    def from_dict(cls, d: dict) -> IsotonicMap:
        return cls(x=np.asarray(d["x"], dtype=float), y=np.asarray(d["y"], dtype=float))

    @classmethod
    def from_sklearn(cls, iso) -> IsotonicMap:
        return cls(x=np.asarray(iso.X_thresholds_, float), y=np.asarray(iso.y_thresholds_, float))


@dataclass
class PortableHGB:
    """Gradient-boosted trees + optional per-class isotonic calibration, numpy only.

    ``columns`` is the input contract: ``predict_proba`` takes a DataFrame and
    selects exactly these columns, in this order, so callers cannot feed the
    model the wrong thing. ``classes`` names the probability columns.
    """

    columns: list[str]
    classes: list[str]
    baseline: np.ndarray  # shape (n_classes,)
    trees: list[list[Tree]]  # [iteration][class]
    calibrators: list[IsotonicMap] | None = None
    meta: dict = field(default_factory=dict)  # provenance, params, metrics: free-form

    # ------------------------------------------------------------------ predict
    def _matrix(self, X) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            missing = [c for c in self.columns if c not in X.columns]
            if missing:
                raise KeyError(f"input is missing contract columns: {missing}")
            X = X[self.columns]
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or X.shape[1] != len(self.columns):
            raise ValueError(f"expected {len(self.columns)} columns, got shape {X.shape}")
        return X

    def raw_predict(self, X) -> np.ndarray:
        """Baseline plus the sum of every tree's leaf value: shape (n, n_classes)."""
        X = self._matrix(X)
        raw = np.tile(self.baseline, (X.shape[0], 1))
        for iteration in self.trees:
            for k, tree in enumerate(iteration):
                raw[:, k] += tree.predict(X)
        return raw

    def predict_proba(self, X, *, calibrated: bool = True) -> np.ndarray:
        """Class probabilities, rows sum to one. ``calibrated=False`` gives the plain softmax."""
        raw = self.raw_predict(X)
        if not calibrated or self.calibrators is None:
            z = raw - raw.max(axis=1, keepdims=True)
            e = np.exp(z)
            return e / e.sum(axis=1, keepdims=True)
        proba = np.column_stack([cal(raw[:, k]) for k, cal in enumerate(self.calibrators)])
        denominator = proba.sum(axis=1, keepdims=True)
        uniform = np.full_like(proba, 1 / proba.shape[1])
        proba = np.divide(proba, denominator, out=uniform, where=denominator != 0)
        proba[(1.0 < proba) & (proba <= 1.0 + 1e-5)] = 1.0
        return proba

    def predict_frame(self, X, *, calibrated: bool = True) -> pd.DataFrame:
        """``predict_proba`` as a DataFrame with the class names as columns."""
        index = X.index if isinstance(X, pd.DataFrame) else None
        return pd.DataFrame(
            self.predict_proba(X, calibrated=calibrated), columns=self.classes, index=index
        )

    def prepare(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Build the contract columns from a frame that has the raw physics columns.

        Contract columns named ``<col>_missing`` are derived from the NaNs in
        ``<col>`` when the frame does not already carry them, mirroring
        ``kepler.models.add_missing_indicators`` without importing scikit-learn.
        """
        out = pd.DataFrame(index=frame.index)
        for c in self.columns:
            if c in frame.columns:
                out[c] = frame[c].astype(float)
            elif c.endswith(MISSING_SUFFIX) and c[: -len(MISSING_SUFFIX)] in frame.columns:
                out[c] = frame[c[: -len(MISSING_SUFFIX)]].isna().astype(float)
            else:
                raise KeyError(f"cannot build contract column {c!r} from the given frame")
        return out

    @property
    def n_iterations(self) -> int:
        return len(self.trees)

    @property
    def n_nodes(self) -> int:
        return sum(len(t.value) for it in self.trees for t in it)

    # ------------------------------------------------------------------ export
    @classmethod
    def from_sklearn(cls, model, columns: list[str], classes: list[str], meta: dict | None = None):
        """Export a fitted ``HistGradientBoostingClassifier`` or a
        ``CalibratedClassifierCV(..., ensemble=False)`` wrapped around one."""
        calibrators = None
        hgb = model
        if hasattr(model, "calibrated_classifiers_"):
            if len(model.calibrated_classifiers_) != 1:
                raise ValueError(
                    "export needs CalibratedClassifierCV(ensemble=False): one estimator"
                )
            cc = model.calibrated_classifiers_[0]
            if cc.method != "isotonic":
                raise ValueError(f"only isotonic calibration is exported, got {cc.method!r}")
            hgb = cc.estimator
            calibrators = [IsotonicMap.from_sklearn(iso) for iso in cc.calibrators]
        if not hasattr(hgb, "_predictors"):
            raise TypeError("expected a fitted HistGradientBoostingClassifier")
        if len(classes) != hgb.n_trees_per_iteration_:
            raise ValueError(
                "this export is written for the multiclass (3 trees per iteration) case"
            )
        baseline = np.asarray(hgb._baseline_prediction, dtype=float).reshape(-1)
        trees = [
            [Tree.from_sklearn_nodes(p.nodes) for p in iteration] for iteration in hgb._predictors
        ]
        return cls(
            columns=list(columns),
            classes=list(classes),
            baseline=baseline,
            trees=trees,
            calibrators=calibrators,
            meta=dict(meta or {}),
        )

    def to_dict(self) -> dict:
        return {
            "format": "kepler.portable.PortableHGB",
            "format_version": FORMAT_VERSION,
            "columns": self.columns,
            "classes": self.classes,
            "baseline": self.baseline.tolist(),
            "trees": [[t.to_dict() for t in it] for it in self.trees],
            "calibrators": None
            if self.calibrators is None
            else [c.to_dict() for c in self.calibrators],
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, d: dict) -> PortableHGB:
        if d.get("format") != "kepler.portable.PortableHGB":
            raise ValueError("not a PortableHGB export")
        if d.get("format_version") != FORMAT_VERSION:
            raise ValueError(f"unsupported format_version {d.get('format_version')!r}")
        cal = d.get("calibrators")
        return cls(
            columns=list(d["columns"]),
            classes=list(d["classes"]),
            baseline=np.asarray(d["baseline"], dtype=float),
            trees=[[Tree.from_dict(t) for t in it] for it in d["trees"]],
            calibrators=None if cal is None else [IsotonicMap.from_dict(c) for c in cal],
            meta=dict(d.get("meta", {})),
        )

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.write_text(json.dumps(self.to_dict(), separators=(",", ":")), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str | Path) -> PortableHGB:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    @classmethod
    def loads(cls, text: str) -> PortableHGB:
        return cls.from_dict(json.loads(text))
