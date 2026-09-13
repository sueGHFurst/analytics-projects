# AWS Cloud Analytics Sandbox

## Overview

Cloud-native ETL pipeline designed to integrate customer, credit bureau, digital activity, and banking transaction data into a consolidated, analytics-ready dataset with built-in data quality auditing, variable inventory management, and exploratory data profiling.

## Business Objective

Build a scalable AWS-based data engineering framework that:

- Consolidates multiple enterprise data domains using PyAthena and Common Table Expressions (CTEs)
- Performs rigorous join validation and anomaly monitoring across key data attributes
- Generates a comprehensive variable inventory (data dictionary) and descriptive statistics
- Cleanses, standardizes, and executes exploratory feature engineering on source data
- Produces automated exploratory data visualizations using Matplotlib and Seaborn
- Outputs protected consolidated and analytics-ready datasets for downstream machine learning and business intelligence initiatives

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
- Risk-Adjusted CLV

---

## Data Architecture

```text
                    AWS CLOUD ANALYTICS SANDBOX

                     Amazon S3 Data Lake
                          (Raw Layer)

        Customer Data
        Credit Bureau Data
        Digital Activity Data
        Banking Transactions Data

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

                               │
                               ▼

             final_analytics_ready_dataset.csv
```

---

## Python-Based SQL Analytics

The AWS Cloud Analytics Sandbox leverages Python and Amazon Athena to execute cloud-native data engineering workflows, including:

- PyAthena connectivity and Amazon Athena SQL execution
- Common Table Expressions (CTEs)
- Multi-source data integration using `LEFT JOIN` operations
- Athena External Table management
- Data quality auditing and validation
- Data cleaning and preparation workflows
- Exploratory data profiling and visualization
- Feature engineering and analytics-ready dataset creation

### SQL Design Patterns

The Athena consolidation layer uses:

```sql
WITH lending_source AS (...),
     credit_source AS (...),
     digital_source AS (...),
     transaction_source AS (...),
     consolidated_customer_data AS (...)

SELECT *
FROM consolidated_customer_data
```

Key capabilities include:

- Schema-on-read processing
- Multi-domain integration
- Business-rule filtering
- Data enrichment through SQL-based transformations

---

## Engineered Variables

The ETL workflow generates the following analytical variables:

| Variable | Description |
|----------|-------------|
| `credit_risk_tier` | Credit score categorized into risk bands |
| `credit_score_decile` | Credit score grouped into 10 customer deciles |
| `high_dti_flag` | Binary debt-to-income threshold indicator |
| `balance_decile` | Account balance grouped into 10 customer deciles |
| `spend_per_transaction` | Customer spending efficiency metric |
| `engagement_score` | Normalized digital engagement metric |
| `risk_adjusted_clv` | Risk-adjusted customer lifetime value |
| `etl_run_date` | ETL execution timestamp |

---

## Data Quality Controls

The ETL framework incorporates:

- Athena connection validation and exception handling
- Environment-driven configuration management
- Idempotent Athena DDL deployment
- Header offset sanitization using:

```sql
TBLPROPERTIES (
    'skip.header.line.count'='1'
)
```

- Null filtering and business-rule validation
- Numeric data-type coercion (`pd.to_numeric`)
- Duplicate household detection
- Missing-value assessment
- Credit-score validation (300–850)
- Negative balance monitoring
- Join reconciliation checks
- Distinct household tracking
- Descriptive statistics generation
- Export validation and protection
- Operational logging

### Example Data Validation Rules

```sql
WHERE household_id IS NOT NULL
  AND balance IS NOT NULL
```

```python
df["credit_score"].between(
    300,
    850
)
```

---

## Exploratory Data Profiling

The pipeline generates automated validation visualizations to help analysts understand source data characteristics.

### Generated Visualizations

```text
credit_score_distribution.png
balance_distribution.png
missing_values_heatmap.png
credit_risk_tier_distribution.png
balance_decile_distribution.png
```

Visualization objectives include:

- Distribution analysis
- Missing-value assessment
- Feature validation
- Outlier inspection
- Risk-segment understanding

---

## Deliverables

### Consolidated Base Dataset

```text
bank-full.csv
```

Contains:

- Multi-source integrated data
- Customer-level observations
- Pre-cleaning consolidated records

### Analytics Dataset

```text
final_analytics_ready_dataset.csv
```

Contains:

- Cleansed records
- Validated attributes
- Engineered features
- Analytics-ready variables

### Data Quality Outputs

```text
data_quality_audit_summary.csv
```

Contains:

- Total rows
- Total columns
- Duplicate households
- Missing values
- Invalid credit scores
- Negative balances
- Distinct households

```text
data_quality_column_summary.csv
```

Contains:

- Column names
- Missing counts
- Missing percentages

```text
variable_inventory.csv
```

Contains:

- Variable names
- Data types
- Missing-value percentages
- Population counts

```text
descriptive_statistics.csv
```

Contains:

- Count
- Mean
- Standard deviation
- Minimum
- Maximum
- Quartiles

### Feature Documentation

```text
feature_engineering_summary.csv
```

Contains:

- Feature names
- Source attributes
- Transformation logic
- Feature classifications

### Operational Logging

```text
pipeline_execution.log
```

Contains:

- Execution status
- Runtime events
- Validation results
- Export notifications
- Exception messages

---

## Technology Stack

### AWS Services

- Amazon S3
- Amazon Athena

### Python Technologies

- Pandas
- NumPy
- PyAthena
- Matplotlib
- Seaborn
- Boto3

### SQL Techniques

- Common Table Expressions (CTEs)
- Multi-Source Data Integration
- Data Filtering
- Aggregations
- Schema Standardization
- Business Rule Enforcement

---

## Repository Deliverables Summary

```text
bank-full.csv

final_analytics_ready_dataset.csv

data_quality_audit_summary.csv

data_quality_column_summary.csv

variable_inventory.csv

descriptive_statistics.csv

feature_engineering_summary.csv

credit_score_distribution.png

balance_distribution.png

missing_values_heatmap.png

credit_risk_tier_distribution.png

balance_decile_distribution.png

pipeline_execution.log
```

---

## Future Roadmap

The scope of this repository concludes with the creation of a validated analytics-ready dataset.

Future projects may leverage these outputs for:

- Customer Segmentation & Profiling
- Risk Analytics & Credit Scoring Models
- Risk-Adjusted CLV Modeling
- Churn Prediction & Retention Campaigns
- Uplift Modeling
- Advanced Predictive Analytics
- Enterprise Reporting & Dashboarding

These initiatives are intentionally separated from the AWS Cloud Analytics Sandbox to maintain a clear distinction between data engineering and downstream analytical workflows.
