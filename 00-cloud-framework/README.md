# 00-cloud-data-foundation

## Overview & Architecture

Cloud-native analytics foundation designed to ingest, integrate, validate, and engineer multi-source financial and digital behavior data directly from cloud catalogs. Operating under the assumption that **ALL DATA IS ALREADY IN THE CLOUD**, the pipeline queries pre-existing Amazon Athena external tables rather than uploading or processing local source files.

The solution utilizes a two-tier cloud extraction strategy consisting of:

- **Pull 1:** Campaign Execution Logs
- **Pull 2:** Response & Behavioral Telemetry

These cloud-native datasets are integrated through Amazon Athena Common Table Expressions (CTEs), multi-domain LEFT JOIN logic, and Python-based data preparation workflows to create enterprise feature stores supporting:

- Customer Segmentation
- Propensity Modeling
- Churn Prediction
- Risk-Adjusted Customer Lifetime Value (CLV)
- Campaign Optimization & ROI Measurement

---

## Solution Architecture

```text
Raw Cloud Data Sources
        │
        ▼
Amazon S3 Data Lake
        │
        ▼
Amazon Athena
(SQL Extraction & Consolidation)
        │
        ▼
Python
(Data Preparation & Feature Engineering)
        │
        ▼
Analytics Feature Store
(226,534 Active Customer Households | 65+ Attributes)
        │
        ▼
Advanced Analytics
├── Customer Segmentation
├── Propensity Modeling
├── Churn Risk Prediction
├── Risk-Adjusted CLV
└── Campaign ROI Optimization
```

---

## Technologies

### Cloud Platform

- Amazon S3
- Amazon Athena

### Data Engineering & Analytics

- Python
- Pandas
- NumPy

### Data Integration

- SQL
- Common Table Expressions (CTEs)
- Multi-Domain LEFT JOIN Logic

### Statistical Processing

- Missing Value Treatment
- Logical Bounds Validation
- Statistical Winsorization
- Data Quality Validation
- Feature Engineering

### Advanced Analytics