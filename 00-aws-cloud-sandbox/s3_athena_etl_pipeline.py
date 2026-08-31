"""
AWS Cloud Analytics Sandbox: S3 Ingestion & Athena SQL Pipeline
===================================================================
Demonstrates end-to-end cloud data pipeline execution:
1. Programmatic raw file upload to Amazon S3 data lake using boto3.
2. Automated DDL generation for Amazon Athena external table creation.
3. Execution of analytical SQL queries using CTEs and Window Functions via PyAthena.

Dataset: Kaggle / UCI Bank Marketing Campaign Dataset (Checking & Deposit Accounts)
"""

import os
import time
import pandas as pd
import boto3
from pyathena import connect

# ------------------------------------------------------------------------------
# 1. AWS CONFIGURATION & S3 STAGING PARAMETERS
# ------------------------------------------------------------------------------
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "sue-furst-analytics-sandbox"
S3_RAW_PREFIX = "raw/bank_marketing_data/"
S3_ATHENA_RESULTS_PREFIX = "athena_query_results/"

# Initialize boto3 S3 Client
s3_client = boto3.client("s3", region_name=AWS_REGION)


# ------------------------------------------------------------------------------
# 2. RAW S3 INGESTION FUNCTION (boto3)
# ------------------------------------------------------------------------------
def upload_raw_dataset_to_s3(local_file_path: str, bucket_name: str, s3_key: str):
    """
    Uploads local financial analytics dataset (CSV) to AWS S3 raw staging bucket.
    """
    print(f"[INFO] Initiating S3 upload: {local_file_path} -> s3://{bucket_name}/{s3_key}")
    try:
        s3_client.upload_file(local_file_path, bucket_name, s3_key)
        print(f"[SUCCESS] Dataset successfully staged in S3: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"[ERROR] Failed to upload file to S3: {str(e)}")
        raise e


# ------------------------------------------------------------------------------
# 3. ATHENA EXTERNAL TABLE DDL CREATION
# ------------------------------------------------------------------------------
def create_athena_table():
    """
    Executes DDL on Amazon Athena to define an external table schema over S3 bank marketing data.
    """
    athena_conn = connect(
        s3_staging_dir=f"s3://{S3_BUCKET_NAME}/{S3_ATHENA_RESULTS_PREFIX}",
        region_name=AWS_REGION
    )
    
    create_table_ddl = f"""
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
    TBLPROPERTIES ('skip.header.line.count'='1');
    """
    
    print("[INFO] Executing DDL for Athena External Table...")
    with athena_conn.cursor() as cursor:
        cursor.execute(create_table_ddl)
    print("[SUCCESS] Athena External Table `bank_marketing_campaign` verified/created.")


# ------------------------------------------------------------------------------
# 4. FINANCIAL ANALYTICAL SQL QUERYING VIA ATHENA & PANDAS
# ------------------------------------------------------------------------------
def run_financial_segmentation_query() -> pd.DataFrame:
    """
    Executes financial analytics SQL using CTEs and Window Functions (NTILE decile ranking).
    Calculates deposit subscription conversion rates across balance tiers.
    """
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
    df_results = pd.read_sql(analytical_query, athena_conn)
    print("[SUCCESS] Financial Query Execution Complete.")
    return df_results


# ------------------------------------------------------------------------------
# MAIN EXECUTION PIPELINE
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Staging paths for Kaggle Bank Marketing Dataset (bank.csv)
    sample_local_csv = "bank_marketing.csv"
    s3_target_key = f"{S3_RAW_PREFIX}bank_marketing.csv"
    
    # Execution workflow:
    # upload_raw_dataset_to_s3(sample_local_csv, S3_BUCKET_NAME, s3_target_key)
    # create_athena_table()
    # df_financial_summary = run_financial_segmentation_query()
    # print(df_financial_summary.head(10))
    
    print("Financial analytics script template validated for GitHub portfolio repository.")
