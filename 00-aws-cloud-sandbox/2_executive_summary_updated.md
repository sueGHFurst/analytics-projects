# Executive Summary

## Python-Based SQL Analytics

The AWS Cloud Analytics Sandbox leverages Python and Amazon Athena to execute cloud-native data engineering workflows that integrate multiple enterprise data domains into a consolidated analytics-ready dataset.

### Core Technologies

- PyAthena
- Amazon Athena SQL
- Common Table Expressions (CTEs)
- Multi-Source Data Integration using LEFT JOIN operations
- Athena External Table Management
- Data Quality Auditing and Validation
- Data Cleansing and Preparation
- Feature Engineering and Analytics Dataset Creation

### Source Data Domains

The Athena consolidation layer integrates the following enterprise data sources:

- Customer Data
- Credit Bureau Data
- Digital Activity Data
- Banking Transactions Data

### Data Engineering Workflow

```text
Amazon S3 Data Lake
        ↓
Athena External Tables
        ↓
Athena Consolidation Query
(CTEs + LEFT JOIN Integration)
        ↓
bank-full.csv
        ↓
Data Quality Audit
        ↓
Data Cleaning & Preparation
        ↓
Feature Engineering
        ↓
final_analytics_ready_dataset.csv
```

### Data Quality Controls

The ETL framework incorporates:

- Athena connection validation
- Idempotent DDL execution (`CREATE EXTERNAL TABLE IF NOT EXISTS`)
- Header offset sanitization (`skip.header.line.count='1'`)
- Null filtering and business-rule validation
- Numeric data-type validation
- Duplicate household detection
- Missing-value assessment
- Credit-score validation (300–850)
- Negative balance monitoring
- Descriptive statistics generation
- Operational logging

### Engineered Variables

The analytics-ready dataset includes:

- Credit Risk Tier
- Credit Score Decile
- High Debt-to-Income Flag
- Balance Decile
- Spend Per Transaction
- Engagement Score
- Risk-Adjusted CLV
- ETL Run Date

### Deliverables

Primary outputs include:

```text
bank-full.csv
final_analytics_ready_dataset.csv
```

Supporting artifacts include:

```text
data_quality_audit_summary.csv
data_quality_column_summary.csv
descriptive_statistics.csv
feature_engineering_summary.csv
pipeline_execution.log
```

### Portfolio Progression

This repository represents the foundational AWS cloud engineering and data integration phase of the analytics portfolio.

Next-phase analytical initiatives include:

- Customer Segmentation
- Risk Analytics
- Risk-Adjusted CLV Modeling
- Churn Prediction
- Predictive Modeling
- Uplift Modeling
- Advanced Customer Analytics
