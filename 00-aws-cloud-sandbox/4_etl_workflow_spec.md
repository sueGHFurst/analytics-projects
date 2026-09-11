# ETL Workflow Specification: AWS Cloud Analytics Sandbox

## Overview

This document outlines the end-to-end Extract, Transform, Load (ETL) workflow implemented within the AWS Cloud Analytics Sandbox. The pipeline is designed to support both cloud-native and local execution modes, enabling scalable data ingestion, transformation, validation, and preparation of model-ready analytical datasets.

---

## Core Logic & Execution

### Pipeline Architecture

The ETL framework follows a modular architecture responsible for:

- Environment variable management
- Amazon S3 connectivity using `boto3`
- Amazon Athena query execution through `PyAthena`
- SQL transformation orchestration
- Local Pandas-based fallback processing
- Data validation and quality control

### Dual-Environment Processing

The workflow supports both cloud and local execution modes.

#### Cloud Execution Mode

Analytical processing occurs within Amazon Athena using advanced SQL techniques:

- Common Table Expressions (CTEs)
- Multi-stage SQL transformation pipelines
- Window Functions
  - `NTILE()`
  - `DENSE_RANK()`
- Customer segmentation logic
- Dataset enrichment workflows

#### Local Execution Mode (Fallback)

When cloud resources are unavailable, equivalent processing can be performed using Pandas.

Supported local transformations include:

- `pd.qcut()` decile segmentation
- Group-by aggregations
- Dense-ranking methodologies
- Statistical summaries
- Dataset validation

---

## ETL Processing Flow

### Step 1: Raw Data Ingestion

The workflow ingests the UCI Bank Marketing Campaign Dataset.

```text
bank-full.csv
```

Primary ingestion activities:

- File discovery
- Schema inspection
- Local validation
- Cloud upload preparation

### Step 2: Amazon S3 Staging

The source dataset is uploaded to Amazon S3 using `boto3`.

```text
s3://bucket/raw/bank_marketing_data/
```

Key staging objectives:

- Durable cloud storage
- Centralized data access
- Athena query compatibility
- Downstream analytics enablement

### Step 3: Athena Schema Provisioning

External table definitions are created in Amazon Athena.

Example:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS
default.bank_marketing_campaign
```

Benefits:

- Schema-on-read architecture
- Repeatable deployment
- Environment reproducibility

### Step 4: Dataset Transformation

Transformation workflows leverage advanced SQL processing.

Key techniques include:

```sql
WITH customer_deciles AS (
    SELECT
        *,
        NTILE(10) OVER (
            ORDER BY balance
        ) AS balance_decile
    FROM bank_marketing_campaign
)
SELECT *
FROM customer_deciles;
```

Processing activities include:

- Customer segmentation
- Feature engineering
- Balance decile creation
- Data enrichment
- Aggregation logic

### Step 5: Analytical Ranking

Customer cohorts are prioritized using ranking methodologies such as:

```sql
DENSE_RANK()
```

Ranking outputs support:

- Segment prioritization
- Campaign targeting analysis
- Customer value classification
- Financial-tier identification
- Customer performance benchmarking

### Step 6: Validation & Output Generation

The final transformation layer produces a clean analytical dataset suitable for:

- Reporting
- Ad hoc analysis
- Predictive modeling
- Risk analysis
- Customer segmentation initiatives

---

## Quality Control & Data Validation

The ETL workflow incorporates multiple safeguards to improve reliability, data integrity, and reproducibility.

### S3 Exception Handling

Cloud storage operations are wrapped within:

```python
try:
    ...
except Exception as e:
    ...
```

Protection includes:

- Network failures
- Permission issues
- Invalid paths
- Upload errors
- Unexpected cloud exceptions

### Idempotent DDL Execution

Athena schema deployment uses:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS
```

Benefits include:

- Repeatable execution
- Prevention of duplicate schemas
- Simplified environment provisioning
- Consistent deployments

### Header Offset Sanitization

CSV headers are ignored during Athena ingestion.

```sql
TBLPROPERTIES (
    'skip.header.line.count'='1'
)
```

This prevents:

- Header contamination
- Incorrect numerical aggregations
- Invalid analytical outputs

### Data Nullity Controls

Data integrity checks exclude missing values.

```sql
WHERE balance IS NOT NULL
```

Benefits include:

- Improved data quality
- Consistent calculations
- Stable analytical outputs
- Reliable segmentation results

### Local Path Verification

Local execution validates file availability before processing.

```python
from pathlib import Path

Path(file_path).exists()
```

This prevents:

- Missing file exceptions
- Failed local executions
- Runtime interruptions

---

## Transformed Variables & Analytical Outputs

The ETL process generates transformation-ready variables that support campaign analysis, customer segmentation, and future risk analytics initiatives.

### Customer Segmentation Variables

- Balance Decile (`NTILE`)
- Customer Ranking (`DENSE_RANK`)
- Financial-Tier Classification
- Segment-Level Performance Metrics

### Campaign Analysis Variables

- Customer Contact Frequency
- Campaign Success Indicators
- Historical Response Behavior
- Conversion Metrics

### Analytical Outputs

Generated outputs support:

- Customer targeting analysis
- Campaign optimization
- Conversion propensity studies
- Profitability segmentation
- Risk-adjusted customer analysis
- Feature engineering for machine learning

---

## Workflow Transition Notes

### Project Lifecycle Progression

This repository serves as the foundational AWS cloud engineering phase of a broader analytics portfolio.

#### Phase 1: AWS Cloud Analytics Sandbox

```text
00-aws-cloud-sandbox
```

Focus Areas:

- Amazon S3 Data Lake staging
- Athena-based analytics
- SQL engineering
- ETL automation
- Data validation

#### Phase 2: Customer Analytics & Modeling

```text
01-customer-targeting-profitability
```

Future analytical initiatives include:

- Customer targeting
- Churn prediction
- Risk-adjusted CLV segmentation
- Predictive modeling
- Uplift modeling
- Advanced customer analytics

---

## Technology Stack

### AWS Services

- Amazon S3
- Amazon Athena
- AWS Lambda
- boto3

### Python Technologies

- Pandas
- NumPy
- PyAthena

### SQL Techniques

- Common Table Expressions (CTEs)
- Window Functions
  - `NTILE()`
  - `DENSE_RANK()`
- Aggregations
- Ranking Functions
- Multi-Source Data Integration

---

## End-to-End Workflow

```text
                    AWS CLOUD ANALYTICS SANDBOX

                  Raw Marketing Source Data
                                │
                                ▼
                     Local File Validation
                                │
                                ▼
                       Amazon S3 Data Lake
                                │
                                ▼
                        Amazon Athena SQL
                                │
                                ▼
                    Schema Provisioning Layer
                                │
                                ▼
                    Advanced SQL Processing
                  (CTEs, NTILE, DENSE_RANK)
                                │
                                ▼
                    Feature Engineering Layer
                                │
                                ▼
                     Analytical Data Mart
                                │
                                ▼
                      Data Quality Checks
                                │
                                ▼
                    Customer Segmentation
                                │
                                ▼
                     Predictive Modeling
                                │
                                ▼
             Campaign Analysis & Risk Analytics
