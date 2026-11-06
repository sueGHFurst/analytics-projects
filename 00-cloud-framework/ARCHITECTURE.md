# Cloud Analytics Framework Architecture

## Purpose

This document describes the logical analytics architecture supporting the creation of enterprise analytical datasets used for customer intelligence, segmentation, credit risk analysis, propensity modeling, profitability optimization, and Project 01 downstream modeling.

> This architecture represents a cloud-compatible analytics framework developed for portfolio and educational purposes. The workflow can be deployed to AWS, Azure, Snowflake, Databricks, or similar cloud analytics environments while being demonstrated locally for reproducibility and governance validation.

---

## Architecture Overview

```text
Bank Marketing Data
Credit Bureau Data
Digital Activity Data
Transaction Data
        │
        ▼
Data Quality & Validation
        │
        ▼
Customer Master Dataset
        │
        ▼
Household Analytics Engine
        │
        ▼
Feature Engineering
        │
        ▼
Customer Feature Store
(bank_full.csv)
299,332 Records
Core90 Enterprise Feature Schema
        │
        ▼
Analytics Ready Dataset
(final_analytics_ready_dataset.csv)
226,534 Active Customer Households
        │
        ▼
Project 01
Customer Targeting &
Profitability Engine
```

---

# Data Domains

## Bank Marketing Data

### Purpose

Provide customer demographic information and campaign response history.

### Examples

- Age
- Job
- Marital Status
- Education
- Contact History
- Campaign Activity
- Previous Outcome
- Response Flag

### Business Contribution

- Customer segmentation
- Campaign effectiveness analysis
- Response propensity modeling

---

## Credit Bureau Data

### Purpose

Provide creditworthiness and financial risk indicators.

### Examples

- Credit Score
- Debt-to-Income Ratio
- Delinquency Indicators
- Credit Utilization
- Inquiry Counts
- Risk Segments

### Business Contribution

- Credit risk analysis
- Customer qualification
- Risk-adjusted marketing strategies

---

## Digital Activity Data

### Purpose

Measure customer engagement and channel behavior.

### Examples

- Login Frequency
- Website Sessions
- Mobile Application Usage
- Communication Responses
- Digital Engagement Scores

### Business Contribution

- Customer intelligence
- Channel optimization
- Customer engagement analysis

---

## Transaction Data

### Purpose

Provide financial behavior and profitability information.

### Examples

- Transaction Counts
- Spending Activity
- Deposit Activity
- Account Balances
- Revenue Metrics

### Business Contribution

- Profitability analysis
- Customer value measurement
- Customer lifetime value modeling

---

# Data Processing Framework

## Step 1 — Data Integration

Combine customer, credit, behavioral, and transaction domains into a consolidated analytics framework.

### Activities

- Source consolidation
- Key alignment
- Relationship validation
- Customer matching

---

## Step 2 — Data Quality Validation

Apply governance and quality-control procedures.

### Controls

- Duplicate detection
- Missing value treatment
- Range validation
- Business-rule validation
- Consistency checks

### Examples

| Variable | Rule |
|-----------|-----------|
| Credit Score | 300–850 |
| Debt-to-Income Ratio | 0.00–1.00 |
| Utilization 
