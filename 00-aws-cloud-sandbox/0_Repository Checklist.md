**Repository Checklist & Asset Index**

**README.md**

* **Project Overview**: Enterprise-grade cloud data engineering and validation pipeline designed for the AWS Cloud Analytics Sandbox.
* **Visual ASCII Architecture**:
```text
[Amazon S3 Data Lake] 
        ↓ (External DDL Tables)
[Amazon Athena SQL Engine] (CTEs + LEFT JOIN Integration)
        ↓ 
[bank-full.csv] (Raw Consolidated Snapshot)
        ↓
[Data Quality Audit & Variable Inventory] + [Exploratory Visualizations]
        ↓
[Data Cleaning & Feature Engineering]
        ↓
[final_analytics_ready_dataset.csv]

```


* **Technical Tooling**: Cloud-native stack leveraging Amazon S3, Athena, PyAthena, Pandas, NumPy, Matplotlib, and Seaborn.
* **Execution Instructions**: Dual-mode support for local testing via mock data frames and cloud-native AWS Athena execution using environment variables (`AWS_REGION`, `S3_BUCKET`, `ATHENA_DATABASE`).

**executive_summary.md**

* **Core Business Insights**: Summary of multi-source customer integration across lending, credit bureau, digital activity, and transaction domains.
* **Data Profiling Findings**: Key distributions, outlier monitoring metrics (invalid credit scores, negative balances, extreme DTI ratios), and join reconciliation coverage.
* **Feature Engineering Overview**: Documentation of risk tiers (`credit_risk_tier`), decile segmentations (`credit_score_decile`, `balance_decile`), threshold flags (`high_dti_flag`), behavioral ratios (`spend_per_transaction`), and normalized engagement scores.
* **Key Deliverables**: Verification of all generated artifacts, data dictionaries, and exploratory diagnostic charts.

**requirements.txt**

* **Pinned Production Libraries**:
* `pandas==2.2.0`
* `numpy==1.26.4`
* `pyathena==3.8.0`
* `boto3==1.34.0`
* `matplotlib==3.8.2`
* `seaborn==0.13.2`
* `jupyterlab==4.1.0`



**s3_athena_etl_pipeline.py**

* **Modular Pipeline Architecture**: Clean, production-ready Python script incorporating automated table creation, CTE-based SQL execution, anomaly detection, join validation, Seaborn/Matplotlib visualization generation, and protected artifact exports.
* **Generated Outputs**:
* `bank-full.csv`
* `final_analytics_ready_dataset.csv`
* `data_quality_audit_summary.csv`
* `data_quality_column_summary.csv`
* `variable_inventory.csv`
* `descriptive_statistics.csv`
* `feature_engineering_summary.csv`
* `pipeline_execution.log`
* `credit_score_distribution.png`
* `balance_distribution.png`
* `missing_values_heatmap.png`
* `credit_risk_tier_distribution.png`
* `balance_decile_distribution.png`
