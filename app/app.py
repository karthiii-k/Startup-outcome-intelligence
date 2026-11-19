import sys
from html import escape
from pathlib import Path

# let this file find the src/ package, whatever folder Streamlit was launched from
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from src.counterfactual import CAVEAT, scenarios, what_if
from src.explain import explain
from src.input_schema import StartupInput
from src.predict import META, predict
from src.utils import COUNTRY_NAMES, STAGES

st.set_page_config(page_title="Startup failure risk", page_icon="📉", layout="wide")

M = META["metrics"]
BAND_COLORS = {"Lower": "#3A9D7A", "Moderate": "#E0A83A", "Elevated": "#C0473A"}

# ------------------------------------------------------------------ styling
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap');
</style>
<style>
.block-container, [data-testid="stMainBlockContainer"] { max-width: 1120px; padding-top: 4.2rem; }
#MainMenu, footer { visibility: hidden; }

.stApp .sfr-title { display: block; font-family: Georgia, 'Times New Roman', serif; font-size: 2.6rem;
             font-weight: 700; line-height: 1.25; letter-spacing: -0.01em; color: #17202A; margin: 0 0 .5rem; padding: 0; }
.sfr-lede  { font-size: 1.08rem; color: #3E4A59; max-width: 62ch; margin: 0 0 .9rem; }
.sfr-note  { border-left: 3px solid #C9D1DC; padding: .1rem 0 .1rem .8rem; color: #5A6675;
             font-size: .88rem; max-width: 84ch; margin: 0 0 1.5rem; }
.stApp .sfr-h { font-family: 'Newsreader', Georgia, serif !important; font-size: 1.4rem !important; font-weight: 600 !important;
             color: #17202A; margin: 1.6rem 0 .4rem; }
.sfr-muted { color: #5A6675; font-size: .88rem; }

[data-testid="stForm"] { background: #FFFFFF; border: 1px solid #D9DEE5; border-radius: 12px;
                         padding: 1.1rem 1.2rem; }

.sfr-result { background: #FFFFFF; border: 1px solid #D9DEE5; border-left: 6px solid var(--c);
              border-radius: 12px; padding: 1.3rem 1.5rem 1.2rem; }
.stApp .sfr-result p.sfr-band { font-family: 'Newsreader', Georgia, serif !important; font-size: 2.6rem !important;
              font-weight: 600 !important; line-height: 1.05 !important; color: var(--c) !important; margin: 0 !important; }
.stApp .sfr-result p.sfr-band.sm { font-size: 2rem !important; }
.stApp .sfr-result p.sfr-sub { color: #2B3644; font-size: 1.02rem !important; margin: .6rem 0 0 !important; max-width: 54ch; }

.sfr-gauge  { position: relative; margin: 2.3rem 0 .2rem; }
.sfr-track  { display: flex; height: 14px; border-radius: 7px; overflow: hidden; }
.sfr-zone   { height: 100%; }
.sfr-zone.dim { opacity: .28; }
.sfr-marker { position: absolute; top: -6px; width: 3px; height: 26px; background: #17202A;
              border-radius: 2px; transform: translateX(-1px); }
.sfr-pill   { position: absolute; top: -26px; left: 50%; transform: translateX(-50%); background: #17202A;
              color: #FFFFFF; font-size: .78rem; font-weight: 600; padding: 1px 9px; border-radius: 10px; }
.sfr-zonelabels { display: flex; font-size: .82rem; color: #5A6675; margin-top: .5rem; }
.sfr-zonelabels span { text-align: center; }
.sfr-flag   { font-size: .92rem; color: #2B3644; margin-top: .9rem; }

.sfr-drv     { margin: .75rem 0; }
.sfr-drv-top { display: flex; justify-content: space-between; gap: 1rem; font-size: .94rem; color: #17202A; }
.sfr-drv-top .v { color: #5A6675; white-space: nowrap; }
.sfr-drv-bar { position: relative; height: 8px; background: #E9EDF2; border-radius: 4px; margin-top: .35rem; }
.sfr-drv-bar .axis { position: absolute; left: 50%; top: -3px; bottom: -3px; width: 1px; background: #8E99A8; }
.sfr-drv-bar .fill { position: absolute; top: 0; bottom: 0; border-radius: 4px; }
.fill.up   { background: #C0473A; }
.fill.down { background: #3A9D7A; }
.sfr-legend { display: flex; justify-content: space-between; font-size: .78rem; color: #7A8696; margin-top: .15rem; }

.sfr-empty { border: 1.5px dashed #BAC4D1; border-radius: 12px; padding: 2.2rem 1.5rem; color: #4A5666; }
.sfr-empty b { font-family: 'Newsreader', Georgia, serif; font-size: 1.3rem; font-weight: 600; color: #17202A; }
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ form state
market_options = ["Unknown"] + META["markets"] + ["Other / not listed"]
NAME_TO_CODE = {COUNTRY_NAMES.get(c, c): c for c in META["countries"]}
country_options = ["Unknown"] + sorted(NAME_TO_CODE) + ["Other / not listed"]

DEFAULTS = {
    "total": 5_000_000.0, "total_unknown": False, "rounds": 2, "stage": 1, "vc": False,
    "days": 365, "days_unknown": False, "market": "Unknown", "country": "Unknown",
    "angel": 0.0, "debt": 0.0, "grant": 0.0, "note": 0.0, "undisc": 0.0,
}
EXAMPLES = {
    "Well-funded": dict(total=60_000_000.0, rounds=5, stage=3, vc=True, days=300,
                                  market="Software", country="United States"),
    "Thin funding": dict(total=50_000.0, rounds=1, stage=0, vc=False, days=1500,
                               market="Web Development", country="India"),
    "Flagged": dict(total=100_000.0, rounds=1, stage=1, vc=False, days=500,
                                 market="Games", country="United Kingdom"),
}

for k, v in DEFAULTS.items():
    st.session_state.setdefault(f"f_{k}", v)


def read_form() -> StartupInput:
    """Turn the form's current values into a validated StartupInput."""
    g = lambda k: st.session_state[f"f_{k}"]

    market_choice, country_choice = g("market"), g("country")
    market = None if market_choice == "Unknown" else "other" if market_choice == "Other / not listed" else market_choice
    if country_choice == "Unknown":
        country = None
    elif country_choice == "Other / not listed":
        country = "other"
    else:
        country = NAME_TO_CODE[country_choice]                          # "United States" -> "USA"

    return StartupInput(
        funding_rounds=int(g("rounds")),
        funding_stage=int(g("stage")),
        funding_total_usd=None if g("total_unknown") else float(g("total")),
        days_to_funding=None if g("days_unknown") else float(g("days")),
        market=market,
        country=country,
        has_institutional_vc=bool(g("vc")),
        angel=float(g("angel")), debt_financing=float(g("debt")), grant=float(g("grant")),
        convertible_note=float(g("note")), undisclosed=float(g("undisc")),
    )


def score_form():
    """Validate the form and store the result (or the error message)."""
    try:
        st.session_state["startup"] = read_form()
        st.session_state.pop("form_error", None)
    except ValueError as e:                       # the bouncer in input_schema.py
        st.session_state.pop("startup", None)
        st.session_state["form_error"] = str(e)


def load_example(name: str):
    for k, v in {**DEFAULTS, **EXAMPLES[name]}.items():
        st.session_state[f"f_{k}"] = v
    score_form()


# ------------------------------------------------------------------ html builders
def gauge_html(score: float, band: str) -> str:
    low, high = META["low_cut_raw"] * 100, META["threshold_raw"] * 100
    widths = {"Lower": low, "Moderate": high - low, "Elevated": 100 - high}
    zones = "".join(
        f'<div class="sfr-zone{"" if name == band else " dim"}" '
        f'style="width:{w:.2f}%;background:{BAND_COLORS[name]}"></div>'
        for name, w in widths.items()
    )
    labels = "".join(f'<span style="width:{w:.2f}%">{name}</span>' for name, w in widths.items())
    pos = min(max(score * 100, 1.5), 98.5)
    return (
        '<div class="sfr-gauge">'
        f'<div class="sfr-track">{zones}</div>'
        f'<div class="sfr-marker" style="left:{pos:.2f}%"><div class="sfr-pill">{score * 100:.0f}</div></div>'
        f'<div class="sfr-zonelabels">{labels}</div>'
        '</div>'
        '<div class="sfr-muted">Model score from 0 to 100. A relative ranking, not a probability.</div>'
    )


def drivers_html(drivers: list[dict]) -> str:
    biggest = max(abs(d["effect"]) for d in drivers)
    rows = []
    for d in drivers:
        share = abs(d["effect"]) / biggest * 50                    # up to half the bar, either side
        if d["effect"] > 0:
            fill = f'<div class="fill up" style="left:50%;width:{share:.1f}%"></div>'
        else:
            fill = f'<div class="fill down" style="left:{50 - share:.1f}%;width:{share:.1f}%"></div>'
        rows.append(
            '<div class="sfr-drv">'
            f'<div class="sfr-drv-top"><span>{escape(d["label"])}</span><span class="v">{escape(d["value_text"])}</span></div>'
            f'<div class="sfr-drv-bar"><div class="axis"></div>{fill}</div>'
            '</div>'
        )
    legend = '<div class="sfr-legend"><span>Lowers risk</span><span>Raises risk</span></div>'
    return "".join(rows) + legend


# ------------------------------------------------------------------ header
st.markdown(
    '<div class="sfr-title">Startup failure risk</div>'
    '<p class="sfr-lede">Describe a startup\'s funding. See which historical risk band it falls into, '
    'and which factors push it there.</p>'
    '<div class="sfr-note">Trained on about 13.7k startups first funded before 2010 (Crunchbase, outcomes as of 2015). '
    'A demonstration of historical patterns, not investment advice.</div>',
    unsafe_allow_html=True,
)

left, right = st.columns([6, 5], gap="large")

# ------------------------------------------------------------------ left: inputs
with left:
    st.markdown('<div class="sfr-muted">Load an example</div>', unsafe_allow_html=True)
    ex_cols = st.columns(len(EXAMPLES))
    for col, name in zip(ex_cols, EXAMPLES):
        col.button(name, key=f"ex_{name}", on_click=load_example, args=(name,), width="stretch")

    with st.form("inputs"):
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Total funding raised (USD)", min_value=0.0, step=100_000.0, format="%.0f", key="f_total")
            st.checkbox("Total funding unknown", key="f_total_unknown")
            st.number_input("Funding rounds", min_value=1, max_value=30, step=1, key="f_rounds")
            st.selectbox("Furthest stage reached", list(STAGES), format_func=STAGES.get, key="f_stage")
            st.checkbox("Backed by institutional VC", key="f_vc")
        with c2:
            st.number_input("Days to first funding", min_value=0, step=30, key="f_days")
            st.checkbox("Days to first funding unknown", key="f_days_unknown")
            st.selectbox("Market", market_options, key="f_market")
            st.selectbox("Country", country_options, key="f_country")

        with st.expander("Funding by type (optional)"):
            a, b = st.columns(2)
            a.number_input("Angel (USD)", min_value=0.0, step=50_000.0, format="%.0f", key="f_angel")
            a.number_input("Debt financing (USD)", min_value=0.0, step=50_000.0, format="%.0f", key="f_debt")
            a.number_input("Grants (USD)", min_value=0.0, step=50_000.0, format="%.0f", key="f_grant")
            b.number_input("Convertible notes (USD)", min_value=0.0, step=50_000.0, format="%.0f", key="f_note")
            b.number_input("Undisclosed (USD)", min_value=0.0, step=50_000.0, format="%.0f", key="f_undisc")

        st.form_submit_button("Score this startup", type="primary", on_click=score_form, key="score")

    if "form_error" in st.session_state:
        st.error(st.session_state["form_error"])

# ------------------------------------------------------------------ right: results
startup = st.session_state.get("startup")

with right:
    if startup is None:
        st.markdown(
            '<div class="sfr-empty"><b>Your result appears here.</b><br>'
            'Fill in the form and press Score this startup, or load an example to see how it works.</div>',
            unsafe_allow_html=True,
        )
    else:
        result = predict(startup)
        band, color = result["band"], BAND_COLORS[result["band"]]

        flag_text = ("Above the model's flag line: it would flag this startup as likely to fail."
                     if result["flagged"] else "Below the model's flag line.")
        st.markdown(
            f'<div class="sfr-result" style="--c:{color}">'
            f'<p class="sfr-band">{band} risk</p>'
            f'<p class="sfr-sub">{result["band_fail_rate"]:.0%} of startups in this band really failed in held-out '
            f'historical data. Across all startups, {result["base_rate"]:.1%} did.</p>'
            f'{gauge_html(result["score"], band)}'
            f'<div class="sfr-flag">{flag_text}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sfr-h">What drives the score</div>', unsafe_allow_html=True)
        drivers = explain(startup)
        if drivers:
            st.markdown(drivers_html(drivers), unsafe_allow_html=True)
            st.markdown('<div class="sfr-muted" style="margin-top:.6rem">Bar lengths compare factors with each '
                        'other on the model\'s internal scale. They are not percentages.</div>',
                        unsafe_allow_html=True)
        else:
            st.write("No single factor stands out.")


# ------------------------------------------------------------------ what-if (full width, under the two columns)
if startup is not None:
    st.markdown('<div class="sfr-h">What-if scenarios</div>', unsafe_allow_html=True)
    st.info(CAVEAT)

    w_left, w_right = st.columns([6, 5], gap="large")

    with w_left:
        rows = scenarios(startup)
        st.caption(f"Current model score: {rows[0]['before'] * 100:.0f} ({rows[0]['band_before']})")
        table = pd.DataFrame([
            {"Scenario": r["label"],
             "New score": f"{r['after'] * 100:.0f}",
             "Change": f"{r['delta'] * 100:+.0f}",
             "Band": r["band_after"]}
            for r in rows
        ])
        st.dataframe(table, hide_index=True, width="stretch")

        st.markdown("**Try your own change**")
        extra_money = st.slider("Extra funding (USD)", 0, 10_000_000, 0, step=250_000, format="$%d")
        extra_rounds = st.slider("Extra rounds", 0, 3, 0)

    with w_right:
        mine = what_if(startup, extra_money, extra_rounds)
        after_band = mine["band_after"]
        if extra_money == 0 and extra_rounds == 0:
            sub = "Move the sliders to see how the score shifts."
        else:
            band_text = (f"Band stays {after_band}." if mine["band_before"] == after_band
                         else f"Band moves from {mine['band_before']} to {after_band}.")
            sub = (f"Model score {mine['before'] * 100:.0f} to {mine['after'] * 100:.0f} "
                   f"({mine['delta'] * 100:+.0f}). {band_text}")
        st.markdown(
            f'<div class="sfr-result" style="--c:{BAND_COLORS[after_band]}">'
            f'<p class="sfr-band sm">{after_band} risk</p>'
            f'<p class="sfr-sub">{sub}</p>'
            f'{gauge_html(mine["after"], after_band)}'
            '</div>',
            unsafe_allow_html=True,
        )

# ------------------------------------------------------------------ limitations
with st.expander("How reliable is this?"):
    low, high = M["roc_auc_ci95"]
    st.markdown(
        f"- **Data:** startups first funded before 2010; failure means closed as of 2015; dollars are nominal. "
        f"Modern markets look different.\n"
        f"- **Ranking power:** ROC-AUC **{M['roc_auc']:.2f}** (95% CI {low:.2f}-{high:.2f}) on "
        f"{M['n_test']:,} held-out startups. Better than chance, far from perfect.\n"
        f"- **Flagging:** at the flag line the model catches about **{M['flag_recall']:.0%}** of failures, "
        f"and about **{M['flag_precision']:.0%}** of flagged startups really failed "
        f"(base rate {M['base_fail_rate']:.1%}).\n"
        f"- **The score isn't a probability:** class weighting inflates the raw score, so the app reports the "
        f"risk band and the failure rate that band really had on held-out data instead.\n"
        f"- **Cumulative funding:** total funding and rounds are measured up to 2015, so they partly reflect "
        f"how long a startup survived. That's why the what-if isn't causal.\n"
        f"- **Not** investment, legal, or business advice."
    )