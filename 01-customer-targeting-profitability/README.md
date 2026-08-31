# Customer Targeting, Churn & Risk-Adjusted CLV Segmentation

## Overview
Targeted modeling framework to identify high-value checking and deposit accounts, segment churn risk, and calculate risk-adjusted Customer Lifetime Value (CLV).

## Tooling & Architecture
* **Database Engine & Querying:** Advanced SQL (CTEs, Window Functions `NTILE`/`LAG`)
* **Core Language:** Python 3.11 (`pandas`, `NumPy`)
* **Visualization:** Power BI / Seaborn Dashboarding

## Analytical Environment & Frameworks
* **Predictive Modeling:** Logistic Regression, Random Forest, `XGBoost`
* **Segmentation:** K-Means Clustering on RFM transactional features
* **Survival Analysis:** Cox Proportional Hazards for multi-month retention tracking
