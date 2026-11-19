# Startup Outcome Intelligence

Predicts whether a startup is likely to fail, using funding history from the Crunchbase 2015 snapshot, and explains the prediction. Built end to end: data cleaning, modelling, a leakage audit, explainability and a deployed Streamlit app.

LIVE LINK : https://startup-outcome-intelligence.streamlit.app/

<img width="1280" height="900" alt="app-top" src="https://github.com/user-attachments/assets/5ebc6e57-d876-416a-8725-1ecb7876d88f" />
<img width="1280" height="900" alt="app-whatif" src="https://github.com/user-attachments/assets/06a5d6c1-c9a2-4611-a8e4-b9a96ab1c7a5" />



## What the app does

Enter a startup's funding profile (total raised, rounds, stage, VC backing, market, country, ...) and get:

- a **risk band** (Lower / Moderate / Elevated) with the failure rate that band really had on held-out data
- a relative 0 to 100 **model score** and whether the model would flag the startup
- the **top factors** pushing the score up or down (SHAP)
- **what-if scenarios** (extra funding, extra rounds, VC backing), clearly labelled as association, not causation

## Data and label

- Crunchbase `investments_VC.csv` (2015 snapshot). Raw data is not included in this repo.
- Kept only startups **first funded before 2010**, so every one has a known 5-year outcome (14,011 labelled, 89% survived / 11% failed). After cleaning: 13,677 startups, 90 features.
- Label: `closed` = failure, anything else (operating, acquired, ...) = survived.
- Engineered features: days to first funding, funding stage reached (capped at Series B), institutional VC flag, single funding event, missing-value flags, one-hot market and country.

## Notebooks

| # | Notebook | What happens |
|---|---|---|
| 01 | data understanding | missingness, duplicates, label design |
| 02 | data preparation | drop empty rows and useless columns, feature engineering |
| 03 | data finalising | 5-year window filter, label, encoding |
| 04 | initial training | baselines: Logistic Regression (AUC 0.700), Decision Tree (0.685), Random Forest (0.709) |
| 05 | model training and tuning | XGBoost (0.737) and LightGBM with class weighting and an out-of-fold threshold |
| 06 | SHAP | explainability and the leakage audit |
| 07 | counterfactual analysis | what-if analysis |
| 08 | retrain v3 | final model |

## Decisions that mattered

- **Outcome window.** Restricted the dataset to startups first funded before 2010, ensuring a five-year outcome window within the 2015 snapshot. This avoids treating younger startups with unknown outcomes as successful.

- **Leakage audit.** SHAP revealed `funding_duration_days` dominating the model. Since startups that fail early cannot accumulate long funding histories, this feature indirectly encoded survival. Removed it in v2.

- **Historical feature dependencies.** Removed `Startup_age` and `founded_year` in v3 because they were anchored to the 2015 snapshot and could not be reliably used for startups evaluated at a different point in time. AUC decreased from 0.737 to 0.707, but the resulting model was more suitable for future inputs.

- **Class imbalance.** With only 11% failures, accuracy is misleading (a model predicting survival for every startup achieves 89%). Used class weighting and evaluated ROC-AUC, PR-AUC, recall and precision instead.

- **Threshold selection.** Selected the failure threshold using out-of-fold predictions from the training set, avoiding threshold optimization on the test set.

- **Score interpretation.** Class weighting inflates raw model scores relative to the actual failure rate. Rather than presenting them as probabilities, the app reports risk bands and their observed failure rates on held-out data.

- **Survivorship bias.** Funding totals and round counts are measured up to the 2015 snapshot, meaning they partly reflect how long a startup survived. What-if scenarios are therefore presented as associations, not causal effects.

- **Model selection.** Compared Logistic Regression, Decision Tree, Random Forest, XGBoost and LightGBM. LightGBM offered the strongest performance among the evaluated models, while the final model prioritized feature validity over maximizing historical test performance.


## Results (held-out test set: 2,736 startups, 10.9% failed)

| Metric | Value |
|---|---|
| ROC-AUC | 0.707 (95% CI 0.68 to 0.74) |
| Failure PR-AUC | 0.248 (base rate 0.109) |
| At the flag line: recall / precision | 44% / 22% |

| Risk band | Share of startups | Actual failure rate |
|---|---|---|
| Lower | 48% | 5.4% |
| Moderate | 30% | 11.7% |
| Elevated | 22% | 21.8% |

A modest ranking signal, not a crystal ball.

## How the app works

```
form -> StartupInput (validation) -> preprocess (8 inputs -> 90 model columns)
     -> predict (LightGBM booster -> score, band, flag)
     -> explain (SHAP drivers)  and  counterfactual (what-if)
     -> Streamlit UI
```

```
app/app.py              Streamlit UI
src/input_schema.py     what a user can enter, with validation
src/preprocess.py       inputs to the model's 90 columns (mirrors the training notebooks)
src/predict.py          score, band and flag
src/explain.py          top factors behind a score
src/counterfactual.py   what-if scenarios
src/utils.py            friendly names and formatting
models/                 lgbm_v3.txt, meta_v3.json
notebooks/              01 to 08
screenshots/            README images
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

Python 3.12 recommended. Deployed on Streamlit Community Cloud with `app/app.py` as the main file.

## Limitations

- Trained on startups from the 2000s with nominal dollars. Modern markets look different.
- Failure means "closed as of 2015", and says nothing about what happened after.
- Only funding and basic profile features, no team, traction or revenue data.
- Demonstration of historical patterns, not investment advice.

## Tooling note

The modelling, analysis and decisions in the notebooks are my own. The deployment layer (`app/` and `src/`) was built with AI assistance.
