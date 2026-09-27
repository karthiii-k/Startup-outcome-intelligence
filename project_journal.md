# Startup Outcome Intelligence Platform

## Project Vision

Build a startup outcome intelligence platform that predicts a startup's future trajectory using its current characteristics and early-stage information.

Possible outcomes:

- Closed
- Acquired
- IPO
- Operating

The goal is not only to predict outcomes, but also to explain why the prediction was made and provide actionable insights through explainability and startup comparison tools.

---

## Core Analysis Components

### 1. Outcome Prediction
Predict the most likely startup outcome using structured startup, funding, and market data.

### 2. SHAP Explanations
Explain individual predictions and identify the factors driving each outcome.

### 3. Similar Startup Retrieval
Find historically similar startups and compare their outcomes.

### 4. Counterfactual Analysis
Show how changing specific startup characteristics could alter predicted outcomes.

### 5. Global Insights
Generate dataset-level insights about the factors most associated with startup success, acquisition, IPO, and failure.

---

## Dataset

Crunchbase Startup Dataset (`investments_VC.csv`)

Approximate size after cleaning:
- ~49k startup records
- Startup, location, funding, and market information
- Multiple startup outcome categories

---

Target Definition Notes

Wanted to predict whether a startup succeeds or fails within 5 years. Problem was the dataset doesn't contain closure or acquisition dates, only a current status column.

To work around this, I treated the dataset as a snapshot from around 2015 and only kept startups that received their first funding before 2010. This ensures each startup had at least 5 years to prove itself.

Target definition:

Success = Operating or Acquired
Failure = Closed

After filtering:

Started with 54,294 startups
Retained 14,011 startups with usable labels

The resulting dataset is highly imbalanced (89% success, 11% failure). This is likely due to reporting bias in Crunchbase, where failed startups are underreported compared to acquisitions and active companies.

Because of this, accuracy will not be the main metric. Evaluation will focus on Recall, F1-score, ROC-AUC and PR-AUC, with class weighting used during training.

A quick baseline Logistic Regression achieved ROC-AUC ≈ 0.64 and ~35% recall on failures, showing that the dataset contains meaningful signal and is worth pursuing further.

Decision: Proceed with this target definition and continue to data cleaning, feature engineering, XGBoost, SHAP explanations, similar startup retrieval and counterfactual analysis.