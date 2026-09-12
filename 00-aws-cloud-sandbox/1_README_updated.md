# AWS Cloud Analytics Sandbox

## Overview

Cloud-native ETL pipeline designed to integrate customer, credit bureau, digital activity, and banking transaction data into a consolidated analytics-ready dataset.

## Business Objective

Build a scalable AWS-based data engineering framework that:

- Consolidates multiple enterprise data domains
- Performs data quality auditing and validation
- Cleanses and standardizes source data
- Engineers analytics-ready variables
- Produces a reusable dataset for downstream analytics and machine learning initiatives

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
```

---

## Python-Based SQL Analytics

- PyAthena
- Amazon Athena SQL
- Common Table Expressions (CTEs)
- Multi-Source Data Integration using LEFT JOIN operations
- Athena External Table Management
- Data Quality Auditing
- Data Cleaning & Preparation
- Feature Engineering & Analytics Dataset Creation

---

## Engineered Variables

- Credit Risk Tier
- Credit Score Decile
- High Debt-to-Income Flag
- Balance Decile
- Spend Per Transaction
- Engagement Score
- Risk-Adjusted CLV
- ETL Run Date

---

## Data Quality Controls

The ETL pipeline incorporates:

- Athena connection validation
- Idempotent DDL execution
- Header offset sanitization
- Null filtering and business-rule validation
- Numeric data-type validation
- Duplicate household detection
- Missing-value assessment
- Credit-score validation (300–850)
- Negative balance monitoring
- Descriptive statistics generation
- Operational logging

---

## Deliverables

### Base Dataset

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
data_quality_column_summary.csv
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

## Future Roadmap

The scope of this repository ends with creation of an analytics-ready dataset.

Future projects may leverage these outputs for:

- Customer Segmentation
- Risk Analytics
- Risk-Adjusted CLV Modeling
- Churn Prediction
- Predictive Modeling
- Uplift Modeling
- Advanced Customer Analytics
