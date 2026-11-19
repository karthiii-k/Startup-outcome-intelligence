from dataclasses import replace

from src.input_schema import StartupInput
from src.predict import predict
from src.preprocess import DEFAULT_FUNDING_TOTAL

CAVEAT = (
    "This shows what the model ASSOCIATES with more funding, not what would happen if a founder "
    "raised it. In the training data, startups that survived longer had more time to raise more "
    "rounds, so a big part of this effect is survivorship, not cause and effect."
)

# ready-made scenarios shown in the app
SCENARIOS = [
    ("Add 1 funding round", dict(extra_rounds=1)),
    ("Add $2M in funding", dict(extra_money=2_000_000)),
    ("Add $2M and 1 round", dict(extra_money=2_000_000, extra_rounds=1)),
    ("Add institutional VC backing", dict(add_vc=True)),
]


def what_if(s: StartupInput, extra_money: float = 0.0, extra_rounds: int = 0,
            add_vc: bool = False) -> dict:
    """Copy the startup, change a few things, and score both versions."""
    base_total = DEFAULT_FUNDING_TOTAL if s.funding_total_usd is None else s.funding_total_usd

    # replace() makes a modified copy and re-runs our validation checks
    changed = replace(
        s,
        funding_total_usd=base_total + extra_money,
        funding_rounds=s.funding_rounds + extra_rounds,
        has_institutional_vc=s.has_institutional_vc or add_vc,
    )

    before, after = predict(s), predict(changed)
    return {
        "before": before["score"],
        "after": after["score"],
        "delta": after["score"] - before["score"],
        "band_before": before["band"],
        "band_after": after["band"],
    }


def scenarios(s: StartupInput) -> list[dict]:
    """Run every ready-made scenario that makes sense for this startup."""
    rows = []
    for label, changes in SCENARIOS:
        if changes.get("add_vc") and s.has_institutional_vc:
            continue                                   # already has VC, nothing to add
        result = what_if(s, **changes)
        result["label"] = label
        rows.append(result)
    return rows
