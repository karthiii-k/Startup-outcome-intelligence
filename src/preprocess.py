import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.input_schema import StartupInput

MODEL_DIR = Path(__file__).parent.parent / "models"

# the exact 90 columns, in the exact order the model was trained on
with open(MODEL_DIR / "meta_v3.json") as f:
    COLUMNS = json.load(f)["columns"]

# lets us match "software", "Software" or " SOFTWARE " to the real column name
LOOKUP = {c.lower(): c for c in COLUMNS}

# the training median; training filled unknown funding totals with this
DEFAULT_FUNDING_TOTAL = 5_000_000.0


def _set_one_hot(row: dict, prefix: str, value):
    """Switch on exactly one column in a group (prefix is 'market_' or 'country_code_')."""
    if value is None:                      # user doesn't know
        row[prefix + "missing"] = 1
        return

    col = LOOKUP.get((prefix + value.strip()).lower())
    if col is not None:                    # a market/country the model knows
        row[col] = 1
    else:                                  # one it has never seen
        row[prefix + "other"] = 1


def to_row(s: StartupInput) -> dict:
    row = dict.fromkeys(COLUMNS, 0.0)      # every column starts at 0

    # --- funding numbers ---
    total = DEFAULT_FUNDING_TOTAL if s.funding_total_usd is None else s.funding_total_usd
    row["funding_total_usd"] = total
    row["funding_rounds"] = s.funding_rounds
    row["funding_per_round"] = total / s.funding_rounds
    row["single_funding_event"] = 1 if s.funding_rounds == 1 else 0
    row["funding_stage_reached"] = s.funding_stage
    row["has_institutional_vc"] = int(s.has_institutional_vc)

    # unknown stays NaN on purpose: training left it NaN and LightGBM handles that natively
    row["days_to_funding"] = np.nan if s.days_to_funding is None else s.days_to_funding

    # --- funding by type ---
    row["angel"] = s.angel
    row["debt_financing"] = s.debt_financing
    row["grant"] = s.grant
    row["convertible_note"] = s.convertible_note
    row["undisclosed"] = s.undisclosed

    # --- market and country (one-hot) ---
    _set_one_hot(row, "market_", s.market)
    _set_one_hot(row, "country_code_", s.country)

    # extra "missing" flags that training created alongside the one-hot columns
    if s.market is None:
        row["market_mising"] = 1           # typo'd twin of market_missing, exists in training data
        row["category_missing"] = 1
    if s.country is None:
        row["country_missing"] = 1

    return row


def preprocess(s: StartupInput) -> pd.DataFrame:
    """StartupInput -> one-row DataFrame with the model's 90 columns in the right order."""
    return pd.DataFrame([to_row(s)])[COLUMNS].astype(float)
