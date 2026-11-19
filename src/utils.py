"""Shared helpers: friendly names and number formatting for the UI."""

STAGES = {0: "None / pre-seed", 1: "Seed", 2: "Series A", 3: "Series B or later"}

COUNTRY_NAMES = {
    "AUS": "Australia", "BEL": "Belgium", "BRA": "Brazil", "CAN": "Canada", "CHE": "Switzerland",
    "CHN": "China", "DEU": "Germany", "DNK": "Denmark", "ESP": "Spain", "FIN": "Finland",
    "FRA": "France", "GBR": "United Kingdom", "IND": "India", "IRL": "Ireland", "ISR": "Israel",
    "ITA": "Italy", "JPN": "Japan", "NLD": "Netherlands", "NOR": "Norway", "SGP": "Singapore",
    "SWE": "Sweden", "USA": "United States",
}

USD_FEATURES = {
    "funding_total_usd", "funding_per_round", "angel", "debt_financing", "grant",
    "convertible_note", "undisclosed", "equity_crowdfunding", "product_crowdfunding",
}

_NICE = {
    "funding_total_usd": "Total funding raised",
    "funding_rounds": "Number of funding rounds",
    "funding_per_round": "Average funding per round",
    "days_to_funding": "Time from founding to first funding",
    "funding_stage_reached": "Funding stage reached",
    "has_institutional_vc": "Institutional VC backing",
    "single_funding_event": "Only one funding event",
    "debt_financing": "Debt financing",
    "angel": "Angel funding",
    "grant": "Grants",
    "convertible_note": "Convertible notes",
    "undisclosed": "Undisclosed funding",
    "category_missing": "Category unknown",
    "market_mising": "Market unknown",
    "market_missing": "Market unknown",
    "country_missing": "Country unknown",
    "country_code_missing": "Country unknown",
}


def nice_name(feature: str) -> str:
    """Model column name -> something a human would say."""
    if feature in _NICE:
        return _NICE[feature]
    if feature.startswith("market_"):
        return "Market: " + feature[len("market_"):]
    if feature.startswith("country_code_"):
        return "Country: " + feature[len("country_code_"):]
    return feature.replace("_", " ").capitalize()


def format_value(feature: str, value) -> str:
    """A feature's value as text for display."""
    if value is None:
        return "unknown"
    if feature in USD_FEATURES:
        return f"${value:,.0f}"
    if feature == "days_to_funding":
        return f"{value:,.0f} days"
    if feature == "funding_stage_reached":
        return STAGES.get(int(value), str(value))
    if feature.startswith(("market_", "country_code_")) or feature in (
        "has_institutional_vc", "single_funding_event", "category_missing", "country_missing"
    ):
        return "yes" if value >= 0.5 else "no"
    return f"{value:,.0f}"
