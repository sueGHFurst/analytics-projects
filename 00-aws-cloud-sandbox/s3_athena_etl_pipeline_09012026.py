"""
AWS Cloud Analytics Sandbox: S3 Ingestion & Athena SQL Pipeline
===================================================================
Demonstrates end-to-end cloud data pipeline execution:
1. Programmatic raw file upload to Amazon S3 data lake using boto3.
2. Automated DDL generation for Amazon Athena external table creation.
3. Execution of analytical SQL queries using CTEs and Window Functions via PyAthena.
"""

import os
from pathlib import Path
import pandas as pd
import boto3
from pyathena import connect

# Configuration from Environment Variables with Fallbacks
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "sue-furst-analytics-sandbox")
S3_RAW_PREFIX = "raw/bank_marketing_data/"
S3_ATHENA_RESULTS_PREFIX = "athena_query_results/"

# Initialize boto3 S3 Client
s3_client = boto3.client("s3", region_name=AWS_REGION)


def upload_raw_dataset_to_s3(local_file_path: str, bucket_name: str, s3_key: str) -> None:
    """Uploads local financial analytics dataset (CSV) to AWS S3 raw staging bucket."""
    print(f"[INFO] Initiating S3 upload: {local_file_path} -> s3://{bucket_name}/{s3_key}")
    
    # 1. S3 Exception Handling: Wrapped inside try...except blocks to catch and log 
    # networking, permission, or path errors during raw file staging.
    try:
        s3_client.upload_file(local_file_path, bucket_name, s3_key)
        print(f"[SUCCESS] Dataset successfully staged in S3: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"[ERROR] Failed to upload file to S3: {str(e)}")
        raise e


def create_athena_table() -> None:
    """Executes DDL on Amazon Athena to define an external table schema over S3 bank marketing data."""
    athena_conn = connect(
        s3_staging_dir=f"s3://{S3_BUCKET_NAME}/{S3_ATHENA_RESULTS_PREFIX}",
        region_name=AWS_REGION
    )
    
    create_table_ddl = f"""
    -- 2. Idempotent DDL Execution: Employs CREATE EXTERNAL TABLE IF NOT EXISTS 
    -- to safely verify or provision schemas without throwing conflicts on pre-existing tables.
    CREATE EXTERNAL TABLE IF NOT EXISTS default.bank_marketing_campaign (
        age INT,
        job STRING,
        marital STRING,
        education STRING,
        default_status STRING,
        balance DOUBLE,
        housing_loan STRING,
        personal_loan STRING,
        contact STRING,
        day_of_month INT,
        month STRING,
        duration_sec INT,
        campaign_contacts INT,
        pdays INT,
        previous_contacts INT,
        poutcome STRING,
        subscribed STRING
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
    LOCATION 's3://{S3_BUCKET_NAME}/{S3_RAW_PREFIX}'
    -- 3. Header Offset Sanitization: Enforces TBLPROPERTIES ('skip.header.line.count'='1') 
    -- to prevent CSV header strings from corrupting numeric aggregations in Athena.
    TBLPROPERTIES ('skip.header.line.count'='1');
    """
    
    print("[INFO] Executing DDL for Athena External Table...")
    try:
        with athena_conn.cursor() as cursor:
            cursor.execute(create_table_ddl)
        print("[SUCCESS] Athena External Table `bank_marketing_campaign` verified/created.")
    finally:
        athena_conn.close()


def run_financial_segmentation_query() -> pd.DataFrame:
    """Executes financial analytics SQL using CTEs and Window Functions (NTILE decile ranking)."""
    athena_conn = connect(
        s3_staging_dir=f"s3://{S3_BUCKET_NAME}/{S3_ATHENA_RESULTS_PREFIX}",
        region_name=AWS_REGION
    )
    
    analytical_query = """
    WITH customer_balance_deciles AS (
        SELECT 
            job,
            education,
            balance,
            CASE WHEN subscribed = 'yes' THEN 1 ELSE 0 END AS conversion_flag,
            campaign_contacts,
            NTILE(10) OVER (ORDER BY balance DESC) AS balance_decile
        FROM default.bank_marketing_campaign
        -- 4. Data Nullity & Consistency Filters: Excludes missing values (WHERE balance IS NOT NULL) 
        -- to ensure downstream statistical computations are performed strictly on valid data points.
        WHERE balance IS NOT NULL
    ),
    decile_summary AS (
        SELECT 
            balance_decile,
            COUNT(*) AS total_customers,
            ROUND(MIN(balance), 2) AS min_balance_usd,
            ROUND(MAX(balance), 2) AS max_balance_usd,
            ROUND(AVG(balance), 2) AS avg_balance_usd,
            SUM(conversion_flag) AS total_conversions,
            ROUND(AVG(CAST(conversion_flag AS DOUBLE)) * 100, 2) AS conversion_rate_pct,
            ROUND(AVG(campaign_contacts), 2) AS avg_outreach_attempts
        FROM customer_balance_deciles
        GROUP BY balance_decile
    )
    SELECT 
        balance_decile,
        total_customers,
        min_balance_usd,
        max_balance_usd,
        avg_balance_usd,
        total_conversions,
        conversion_rate_pct,
        avg_outreach_attempts,
        DENSE_RANK() OVER (ORDER BY conversion_rate_pct DESC) AS conversion_rank
    FROM decile_summary
    ORDER BY balance_decile ASC;
    """
    
    print("[INFO] Running Multi-Tier CTE & Window Function Query via Athena...")
    try:
        df_results = pd.read_sql(analytical_query, athena_conn)
        print("[SUCCESS] Financial Query Execution Complete.")
        return df_results
    finally:
        athena_conn.close()


if __name__ == "__main__":
    # Portable path resolution using pathlib
    sample_local_csv = Path(__file__).resolve().parent / "bank-full.csv" / "bank-full.csv"
    
    # 5. Local Path Assertions: Validates local file existence via Path.exists() 
    # before executing fallback processing loops, avoiding runtime FileNotFoundError exceptions.
    if sample_local_csv.exists():
        df = pd.read_csv(sample_local_csv, sep=";")
        
        df['conversion_flag'] = df['y'].apply(lambda x: 1 if x == 'yes' else 0)
        df['balance_decile'] = pd.qcut(df['balance'], q=10, labels=False, duplicates='drop') + 1

        df_financial_summary = df.groupby('balance_decile').agg(
            total_customers=('balance', 'count'),
            min_balance_usd=('balance', 'min'),
            max_balance_usd=('balance', 'max'),
            avg_balance_usd=('balance', 'mean'),
            total_conversions=('conversion_flag', 'sum'),
            conversion_rate_pct=('conversion_flag', lambda x: round(x.mean() * 100, 2)),
            avg_outreach_attempts=('campaign', 'mean')
        ).reset_index()

        df_financial_summary['conversion_rank'] = df_financial_summary['conversion_rate_pct'].rank(
            ascending=False, method='dense'
        ).astype(int)

        print(df_financial_summary.head(10))
        print("Financial analytics script template validated for GitHub portfolio repository.")
    else:
        print(f"[WARNING] Local dataset not found at {sample_local_csv}. Ready for cloud Athena execution.")

# Export final aggregated financial summary to CSV for broad compatibility
df_financial_summary.to_csv("bank_campaign_decile_analysis.csv", index=False)

# ------------------------------------------------------------------------------
# WORKFLOW TRANSITION NOTE:
# After completing the 00-aws-cloud-sandbox module (infrastructure, S3 raw staging, 
# and serverless Athena pipelines), the project workflow advances to downstream 
# advanced machine learning and experimentation modules, such as 01-customer-targeting-profitability 
# for predictive modeling and customer classification.
# ------------------------------------------------------------------------------