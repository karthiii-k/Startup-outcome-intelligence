# Startup Outcome Intelligence Platform

## Project Vision

Build a startup outcome intelligence platform that predicts a startup's future trajectory using its current characteristics and early-stage information.

Possible outcomes:

* Closed
* Acquired
* IPO
* Operating

## Core Analysis Components

1. Outcome Prediction
2. SHAP Explanations
3. Similar Startup Retrieval
4. Counterfactual Analysis
5. Global Insights

## Dataset

Crunchbase Startup Dataset (`investments_VC.csv`)

## Current Stage

Stage 0 - Dataset Understanding, Feature Selection, and Project Planning


Features to engineer:

days_to_first_funding = first_funding_at - founded_at
startup_age
market_missing
category_missing
country_missing
single_funding_event = (first_funding_at == last_funding_at)
funding_stage_reached (ordinal: none → seed → A → B) — capped deliberately at B. This replaces raw round_B amount and stops the model from treating "reached B" as a crystal ball.
has_institutional_vc (binary, derived from venture being nonzero) — captures "professional investors are in" without leaking the cumulative dollar amount.