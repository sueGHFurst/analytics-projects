# Repository Checklist

- **README.md**
  - Project overview
  - Visual ASCII architecture diagram
  - Technical tooling and dependencies
  - Dual-mode execution instructions (local and cloud)

- **executive_summary.md**
  - Core business insights
  - Peak decile conversion analysis
  - DENSE_RANK optimization strategies
  - Key recommendations and outcomes

- **requirements.txt**
  - Pinned production library versions for reproducibility:
    - pandas
    - boto3
    - pyathena
    - scikit-learn
    - lightgbm
    - statsmodels

- **s3_athena_etl_pipeline.py**
  - Clean, modular ETL pipeline
  - Local pandas-based processing
  - AWS S3 data staging
  - Amazon Athena querying
  - Enterprise cloud data engineering workflow simulation
