"""Lightweight pose classification helper.

Provides functions to train/load a model (if scikit-learn available) and a safe fallback heuristic
to classify poses as 'good' or 'bad' using numeric joint positions. Designed to run fully locally.
"""
from typing import Dict, List
import math

HAS_ML = True
try:
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from joblib import dump, load
except Exception:
    HAS_ML = False


def _vector_from_joints(joints: Dict[str, float]) -> List[float]:
    # Expect joints as a flat dict {'nose_x':..., 'nose_y':..., 'left_shoulder_x':...}
    # Sort keys for deterministic order
    keys = sorted(joints.keys())
    return [float(joints[k]) for k in keys]


def train_from_csv(csv_path: str, model_out_path: str) -> None:
    """Train a simple logistic regression model from a CSV.

    CSV must have numeric columns for joints and a column named 'label' with 0/1 (0=bad,1=good).
    Saves a joblib model to model_out_path.
    Requires pandas and scikit-learn.
    """
    if not HAS_ML:
        raise RuntimeError("ML dependencies (pandas, scikit-learn, joblib) not installed")

    df = pd.read_csv(csv_path)
    if 'label' not in df.columns:
        raise ValueError("CSV must contain 'label' column with 0/1 values")
    X = df.drop(columns=['label']).values
    y = df['label'].values

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    clf = LogisticRegression(max_iter=200)
    clf.fit(Xs, y)

    dump({'scaler': scaler, 'clf': clf}, model_out_path)


def load_model(path: str):
    if not HAS_ML:
        raise RuntimeError("ML dependencies not installed")
    return load(path)


def predict_from_joints(model, joints: Dict[str, float]) -> Dict:
    """Predict using loaded model (if provided) or fallback heuristic.

    Returns: {'label': 'good'|'bad', 'score': float(0..1)}
    """
    vec = _vector_from_joints(joints)

    if HAS_ML and model is not None:
        scaler = model['scaler']
        clf = model['clf']
        import numpy as np

        Xs = scaler.transform([vec])
        prob = float(clf.predict_proba(Xs)[0, 1])
        label = 'good' if prob >= 0.5 else 'bad'
        return {'label': label, 'score': prob}

    # Fallback heuristic: compute normalized dispersion of limbs; low movement or extremely skewed positions -> bad
    # Simple heuristic: compute standard deviation across coordinates; normalize by mean magnitude
    xs = [v for i, v in enumerate(vec) if i % 2 == 0]
    ys = [v for i, v in enumerate(vec) if i % 2 == 1]
    if len(xs) == 0 or len(ys) == 0:
        return {'label': 'bad', 'score': 0.0}

    def _std(lst):
        mean = sum(lst) / len(lst)
        return math.sqrt(sum((x - mean) ** 2 for x in lst) / len(lst))

    std_x = _std(xs)
    std_y = _std(ys)
    mean_mag = (sum(abs(x) for x in xs) + sum(abs(y) for y in ys)) / (len(xs) + len(ys))
    if mean_mag == 0:
        score = 0.0
    else:
        dispersion = (std_x + std_y) / 2.0 / mean_mag
        # map dispersion to score 0..1 (clamp)
        score = max(0.0, min(1.0, dispersion * 2.0))

    label = 'good' if score >= 0.35 else 'bad'
    return {'label': label, 'score': score}
