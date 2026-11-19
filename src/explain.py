import numpy as np

from src.input_schema import StartupInput
from src.predict import BOOSTER
from src.preprocess import COLUMNS, preprocess
from src.utils import format_value, nice_name


def explain(s: StartupInput, top_n: int = 5) -> list[dict]:
    """The top factors pushing this startup's score toward failure or toward survival."""
    X = preprocess(s)

    # LightGBM can compute exact SHAP values itself (pred_contrib=True).
    # Result: one number per column, plus a baseline in the last slot, which we drop.
    # These numbers push toward SUCCESS, so we flip the sign to talk about failure.
    contrib = BOOSTER.predict(X, pred_contrib=True)[0][:-1]
    fail_push = -contrib

    biggest = np.argsort(-np.abs(fail_push))[:top_n]   # indices of the biggest pushes

    drivers = []
    for i in biggest:
        if abs(fail_push[i]) < 1e-9:                   # skip factors that did nothing
            continue
        feature = COLUMNS[i]
        raw_value = X.iloc[0, i]
        value = None if np.isnan(raw_value) else float(raw_value)
        drivers.append({
            "feature": feature,
            "label": nice_name(feature),
            "value_text": format_value(feature, value),
            "effect": float(fail_push[i]),             # + = raises risk, - = lowers it
            "direction": "raises risk" if fail_push[i] > 0 else "lowers risk",
        })
    return drivers
