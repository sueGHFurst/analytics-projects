
# Customer Targeting, Churn & Risk-Adjusted CLV Segmentation

## Overview
End-to-end predictive analytics framework designed to optimize checking and deposit account acquisition, mitigate customer churn risk, and calculate risk-adjusted Customer Lifetime Value (CLV). Built with a local-first development architecture mirroring enterprise cloud data pipelines.

## Project Structure
```text
analytic-projects/
├── 00-aws-cloud-sandbox/
└── 01-customer-targeting-profitability/
    ├── data/
    │   ├── bank-full.csv
    │   ├── household_transactions.csv
    │   ├── household_digital_activity.csv
    │   └── household_credit_profile.csv
    ├── scripts/
    │   ├── 01_ingest_and_aggregate.py
    │   ├── 02_preprocess_and_validate.py
    │   ├── 03_train_models.py
    │   └── 04_evaluate_and_visualize.py
    └── README.md
```

## Execution Pipeline

* **Step 1 (Ingestion & Synchronization):** Ingest raw UCI Bank Marketing records and generate synchronized behavioral, digital activity, and credit profiles using consistent `household_id` relational keys.
* **Step 2 (Preprocessing & Validation):** Execute relational joins, handle missing values, engineer RFM transactional features, and run automated data integrity checks.
* **Step 3 (Predictive Modeling & Segmentation):** Train classification algorithms (Logistic Regression, Random Forest, `XGBoost`) for cross-sell targeting, run K-Means clustering on behavioral segments, and apply Cox Proportional Hazards for multi-month retention tracking.
* **Step 4 (Evaluation & Visualization):** Generate evaluation metrics (ROC-AUC, Precision-Recall curves) and format outputs for downstream business intelligence and dashboarding.

## Tooling & Technical Stack

* **Core Language:** Python 3.11 (`pandas`, `NumPy`, `scikit-learn`, `xgboost`, `lifelines`)
* **Data Engineering & Querying:** Advanced SQL patterns (CTEs, Window Functions `NTILE`/`LAG`) and relational data staging
* **Visualization:** Seaborn, Matplotlib, and Power BI integration
