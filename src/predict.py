import json
from pathlib import Path

import lightgbm as lgb

from src.input_schema import StartupInput
from src.preprocess import preprocess

MODEL_DIR = Path(__file__).parent.parent / "models"

# --- load everything once, when the file is first imported ---
BOOSTER = lgb.Booster(model_file=str(MODEL_DIR / "lgbm_v3.txt"))

with open(MODEL_DIR / "meta_v3.json") as f:
    META = json.load(f)


def get_band(score: float) -> str:
    if score >= META["threshold_raw"]:      # the flag line tuned in notebook 08
        return "Elevated"
    if score >= META["low_cut_raw"]:
        return "Moderate"
    return "Lower"


def predict(s: StartupInput) -> dict:
    X = preprocess(s)                              # 1 row, 90 columns

    success_prob = BOOSTER.predict(X)[0]           # the model outputs P(success)
    score = float(1 - success_prob)                # we care about failure

    # NOTE: this score ranks startups well but is NOT a real probability
    # (class weighting inflates it), so the app shows the band and the failure rate
    # that band really had in held-out data, not this number as a percentage.
    band = get_band(score)
    return {
        "score": score,
        "band": band,
        "flagged": bool(score >= META["threshold_raw"]),
        "base_rate": META["metrics"]["base_fail_rate"],
        "band_fail_rate": META["band_stats"][band]["actual_fail_rate"],
    }
