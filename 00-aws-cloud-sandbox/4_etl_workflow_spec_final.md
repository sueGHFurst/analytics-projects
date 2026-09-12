# ETL Workflow Specification: AWS Cloud Analytics Sandbox

## Overview

This document outlines the end-to-end Extract, Transform, Load (ETL) workflow implemented within the AWS Cloud Analytics Sandbox.

The solution leverages Amazon S3, Amazon Athena, PyAthena, and Pandas to integrate multiple enterprise data domains into a consolidated analytics-ready dataset suitable for downstream analytics and machine learning workflows.

---

## Core Logic & Execution

### Pipeline Architecture

The ETL framework provides:

- Environment-driven configuration management
- Athena External Table management
- Amazon Athena query execution using PyAthena
- SQL-based multi-source integration using CTEs
- Data quality auditing
- Data cleansing and preparation
- Feature engineering
- Analytics-ready dataset creation

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

## ETL Processing Flow

### Step 1: Amazon S3 Data Lake

Raw source datasets reside in Amazon S3.

Example structure:

```text
s3://analytics-sandbox/raw/customer_lending/
s3://analytics-sandbox/raw/credit_bureau/
s3://analytics-sandbox/raw/digital_activity/
s3://analytics-sandbox/raw/customer_transactions/
```

### Step 2: Athena Schema Provisioning

External table definitions are provisioned using:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS
```

Benefits:

- Schema-on-read architecture
- Repeatable deployments
- Environment reproducibility
- Serverless analytics enablement

### Step 3: Athena Consolidation Query

Multiple source systems are integrated through Common Table Expressions (CTEs).

Source CTEs include:

- `lending_source`
- `credit_source`
- `digital_source`
- `transaction_source`

The final integration layer creates:

```sql
consolidated_customer_data
```

using SQL-based `LEFT JOIN` integration.

### Step 4: Consolidated Base Dataset

Athena produces a consolidated customer-level dataset:

```text
bank-full.csv
```

### Step 5: Data Quality Audit

Validation procedures verify:

- Record counts
- Duplicate households
- Missing values
- Invalid credit scores
- Negative balances
- Distinct household counts

Outputs:

```text
data_quality_audit_summary.csv
```

```text
data_quality_column_summary.csv
```

```text
descriptive_statistics.csv
```

### Step 6: Data Cleaning & Preparation

Data preparation procedures include:

- Numeric type validation (`pd.to_numeric`)
- Credit-score validation (300–850)
- Missing-value remediation
- Debt-to-income imputation
- Business-rule filtering

### Step 7: Feature Engineering

#### Credit Features

- Credit Risk Tier
- Credit Score Decile
- High Debt-to-Income Flag

#### Financial Features

- Balance Decile
- Spend Per Transaction
- Risk-Adjusted CLV

#### Digital Activity Features

- Engagement Score

#### Operational Features

- ETL Run Date

### Step 8: Analytics Dataset Creation

Final output:

```text
final_analytics_ready_dataset.csv
```

Suitable for:

- Reporting
- Exploratory Data Analysis (EDA)
- Feature validation
- Customer analytics
- Machine learning preparation

---

## Quality Control & Data Validation

### Athena Connection Validation

```python
try:
    conn = get_athena_connection()
except Exception as e:
    ...
```

### Idempotent DDL Execution

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS
```

### Header Offset Sanitization

```sql
TBLPROPERTIES (
    'skip.header.line.count'='1'
)
```

### Data Nullity Controls

```sql
WHERE household_id IS NOT NULL
  AND balance IS NOT NULL
```

### Data Type Validation

```python
pd.to_numeric(errors='coerce')
```

### Audit Controls

- Duplicate household validation
- Missing-value analysis
- Invalid credit-score checks
- Negative balance checks
- Descriptive statistics generation

### Operational Logging

```text
pipeline_execution.log
```

---

## Engineered Variables

| Variable | Description |
|----------|-------------|
| credit_risk_tier | Credit score grouped into risk bands |
| credit_score_decile | Credit score grouped into deciles |
| high_dti_flag | DTI threshold indicator |
| balance_decile | Balance grouped into deciles |
| spend_per_transaction | Spend efficiency metric |
| engagement_score | Normalized engagement metric |
| risk_adjusted_clv | Customer value metric |
| etl_run_date | ETL execution timestamp |

---

## Technology Stack

### AWS Services

- Amazon S3
- Amazon Athena

### Python Technologies

- Pandas
- NumPy
- PyAthena

### SQL Techniques

- Common Table Expressions (CTEs)
- Multi-Source Data Integration
- Data Filtering
- Aggregations
- Schema Standardization

---

## Final Deliverables

### Consolidated Base Dataset

```text
bank-full.csv
```

### Analytics Dataset

```text
final_analytics_ready_dataset.csv
```

### Data Quality Outputs

```text
data_quality_audit_summary.csv
```

```text
data_quality_column_summary.csv
```

```text
descriptive_statistics.csv
```

### Feature Documentation

```text
feature_engineering_summary.csv
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

Focus Areas:

- Amazon S3
- Athena SQL Engineering
- Data Integration
- Data Quality Management
- Feature Engineering
- Analytics Dataset Creation

### Phase 2

```text
01-customer-targeting-profitability
```

Focus Areas:

- Customer Segmentation
- Risk Analytics
- Risk-Adjusted CLV Modeling
- Churn Prediction
- Predictive Modeling
- Uplift Modeling

---

## End-to-End Workflow

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

                    Data Quality Audit

                               │
                               ▼

                 Data Cleaning & Preparation

                               │
                               ▼

                     Feature Engineering

                               │
                               ▼

                      Analytics Data Mart

                               │
                               ▼

             final_analytics_ready_dataset.csv

                               │
                               ▼

                       Upcoming Analysis
```
