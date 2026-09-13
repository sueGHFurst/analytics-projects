# ETL Workflow Specification: AWS Cloud Analytics Sandbox

## Overview

This document outlines the end-to-end Extract, Transform, Load (ETL) workflow implemented within the AWS Cloud Analytics Sandbox.

The solution leverages Amazon S3, Amazon Athena, PyAthena, Pandas, Matplotlib, and Seaborn to integrate multiple enterprise data domains into a consolidated, analytics-ready dataset with built-in data quality auditing, variable inventory management, and exploratory data profiling.

---

## Core Logic & Execution

### Pipeline Architecture

The ETL framework provides:

- Environment-driven configuration management
- Athena External Table management
- Amazon Athena query execution using PyAthena[cite: 5]
- SQL-based multi-source integration using Common Table Expressions (CTEs)[cite: 5]
- Automated join reconciliation tracking unmatched records across domains[cite: 5]
- Data quality auditing[cite: 5] and variable inventory generation
- Exploratory data profiling and visualization generation
- Data cleansing[cite: 5] and feature engineering
- Protected artifact export handling[cite: 5]

---

## Source Data Domains

### Customer Data
- Age
- Job
- Marital Status
- Education
- Delinquency Indicators
- Churn Indicators

### Credit Bureau Data
- Credit Score
- Debt-to-Income Ratio

### Digital Activity Data
- Login Frequency
- Mobile Application Activity
- Digital Engagement Score

### Banking Transactions Data
- Account Balance
- Transaction Count
- Average Transaction Amount
- Total Spend
- Risk-Adjusted CLV[cite: 5]

---

## ETL Processing Flow

### Step 1: Amazon S3 Data Lake
Raw source datasets reside in Amazon S3 under structured paths.

```text
s3://analytics-sandbox/raw/customer_lending/
s3://analytics-sandbox/raw/credit_bureau/
s3://analytics-sandbox/raw/digital_activity/
s3://analytics-sandbox/raw/customer_transactions/
```

### Step 2: Athena Schema Provisioning
External table definitions are provisioned using idempotent DDL:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS
```

### Step 3: Athena Consolidation Query
Multiple source systems are integrated through Common Table Expressions (CTEs) utilizing `LEFT JOIN` operations and domain filtering[cite: 5].

### Step 4: Consolidated Base Dataset Snapshot
Athena produces a raw customer-level base snapshot exported securely[cite: 5]:

```text
bank-full.csv
```

### Step 5: Data Quality Audit & Variable Inventory
Validation procedures verify record counts, duplicate households, missing values, invalid credit scores (300–850), and negative balances[cite: 5], alongside generating a complete variable inventory dictionary.

### Step 6: Exploratory Data Profiling Visualizations
Automated generation of diagnostic plots using Matplotlib and Seaborn with a non-interactive backend (`Agg`):

- `credit_score_distribution.png`
- `balance_distribution.png`
- `missing_values_heatmap.png`
- `credit_risk_tier_distribution.png`
- `balance_decile_distribution.png`

### Step 7: Data Cleaning & Feature Engineering
Data preparation and feature engineering execute domain transformations including credit risk tiers, decile segmentations, debt-to-income flags, and normalized engagement scores.

### Step 8: Analytics Dataset Creation
Final output protection and export[cite: 5]:

```text
final_analytics_ready_dataset.csv
```

---

## Quality Control & Data Validation

### Athena Connection Validation
```python
try:
    conn = get_athena_connection()
except Exception as e:
    ...
```

### Join Reconciliation Monitoring
Tracks and logs unmatched records across key domain attributes (`credit_score`, `login_frequency`, `balance`)[cite: 5].

### Data Type & Anomaly Controls
- Numeric coercion via `pd.to_numeric(errors='coerce')`[cite: 5]
- Credit score validation bounds (300–850)
- Negative balance monitoring and DTI ratio threshold checks[cite: 5]

---

## Engineered Variables

| Variable | Description |
|----------|-------------|
| credit_risk_tier | Credit score grouped into standard risk bands |
| credit_score_decile | Credit score grouped into deciles (1–10) |
| high_dti_flag | Binary DTI threshold indicator (>43%) |
| balance_decile | Account balance grouped into deciles (1–10) |
| spend_per_transaction | Behavioral spend efficiency ratio |
| engagement_score | Normalized multi-factor digital activity score |
| risk_adjusted_clv | Customer profitability metric[cite: 5] |
| etl_run_date | ETL execution timestamp |

---

## Technology Stack

### AWS Services
- Amazon S3
- Amazon Athena

### Python Technologies
- Pandas[cite: 5]
- NumPy
- PyAthena[cite: 5]
- Matplotlib
- Seaborn
- Boto3

### SQL Techniques
- Common Table Expressions (CTEs)[cite: 5]
- Multi-Source Join Reconciliation[cite: 5]
- Data Filtering & Aggregations[cite: 5]
- Schema Standardization

---

## Final Deliverables

### Datasets
```text
bank-full.csv
final_analytics_ready_dataset.csv
```

### Audit & Inventory Outputs
```text
data_quality_audit_summary.csv
data_quality_column_summary.csv
variable_inventory.csv
descriptive_statistics.csv
feature_engineering_summary.csv
```

### Exploratory Visualizations
```text
credit_score_distribution.png
balance_distribution.png
missing_values_heatmap.png
credit_risk_tier_distribution.png
balance_decile_distribution.png
```

### Operational Logging
```text
pipeline_execution.log
```

---

## Workflow Transition Notes

### Phase 1
```text
00-aws-cloud-sandbox
```
Focus Areas: Amazon S3, Athena SQL Engineering, Data Integration[cite: 5], Data Quality Management[cite: 5], Feature Engineering, and Exploratory Profiling.

### Phase 2
```text
01-customer-targeting-profitability
```
Focus Areas: Customer Segmentation, Risk Analytics, Risk-Adjusted CLV Modeling, Churn Prediction, and Predictive Modeling.

---

## End-to-End Workflow

```text
                        AWS CLOUD ANALYTICS SANDBOX

                       Amazon S3 Data Lake
                          (Raw Layer)

        Customer Data | Credit Bureau Data | Digital Activity Data | Banking Transactions Data
                               │
                               ▼
                    Athena External Tables
                               │
                               ▼
                   Athena Consolidation Query
                    (CTEs + LEFT JOIN Logic)
                               │
                               ▼
                   Consolidated Base Dataset
                         bank-full.csv
                               │
                               ▼
                Data Quality Audit & Variable Inventory
                               │
                               ▼
               Exploratory Data Profiling Charts
                               │
                               ▼
               Data Cleaning & Feature Engineering
                               │
                               ▼
                      Analytics Data Mart
               final_analytics_ready_dataset.csv
                               │
                               ▼
                       Upcoming Analysis
```
>>>>></markdown>
