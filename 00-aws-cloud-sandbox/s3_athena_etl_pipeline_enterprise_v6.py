"""
AWS Cloud Analytics Sandbox - Enterprise ETL Pipeline v6

Workflow
Amazon S3 Data Lake
 -> Athena External Tables
 -> Athena Consolidation Query (CTEs + LEFT JOIN Integration)
 -> bank-full.csv
 -> Data Quality Audit
 -> Data Cleaning & Preparation
 -> Feature Engineering
 -> final_analytics_ready_dataset.csv
"""

import os
import logging
import numpy as np
import pandas as pd
from pyathena import connect

# Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "analytics-sandbox")
ATHENA_DATABASE = os.getenv("ATHENA_DATABASE", "analytics_sandbox")
ATHENA_RESULTS = os.getenv("ATHENA_RESULTS", f"s3://{S3_BUCKET}/athena_query_results/")
CREATE_TABLES = os.getenv("CREATE_TABLES", "Y")

CUSTOMER_LENDING_TABLE = f"{ATHENA_DATABASE}.customer_lending"
CREDIT_BUREAU_TABLE = f"{ATHENA_DATABASE}.credit_bureau"
DIGITAL_ACTIVITY_TABLE = f"{ATHENA_DATABASE}.digital_activity"
CUSTOMER_TRANSACTIONS_TABLE = f"{ATHENA_DATABASE}.customer_transactions"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("pipeline_execution.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def get_athena_connection():
    """Create Athena connection."""
    try:
        return connect(s3_staging_dir=ATHENA_RESULTS, region_name=AWS_REGION)
    except Exception as exc:
        logger.exception("Athena connection failed: %s", exc)
        raise


def create_athena_tables():
    """Create Athena external tables when enabled."""
    if CREATE_TABLES != "Y":
        logger.info("Skipping DDL creation.")
        return

    ddl_statements = [
        f"""CREATE EXTERNAL TABLE IF NOT EXISTS {CUSTOMER_LENDING_TABLE} (household_id STRING, age INT, job STRING, marital STRING, education STRING, delinquency_flag_90D INT, churn_event INT, target INT) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION 's3://{S3_BUCKET}/raw/customer_lending/' TBLPROPERTIES ('skip.header.line.count'='1')""",
        f"""CREATE EXTERNAL TABLE IF NOT EXISTS {CREDIT_BUREAU_TABLE} (household_id STRING, credit_score INT, debt_to_income_ratio DOUBLE) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION 's3://{S3_BUCKET}/raw/credit_bureau/' TBLPROPERTIES ('skip.header.line.count'='1')""",
        f"""CREATE EXTERNAL TABLE IF NOT EXISTS {DIGITAL_ACTIVITY_TABLE} (household_id STRING, login_frequency DOUBLE, mobile_app_active INT, digital_engagement_score DOUBLE) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION 's3://{S3_BUCKET}/raw/digital_activity/' TBLPROPERTIES ('skip.header.line.count'='1')""",
        f"""CREATE EXTERNAL TABLE IF NOT EXISTS {CUSTOMER_TRANSACTIONS_TABLE} (household_id STRING, balance DOUBLE, transaction_count INT, avg_transaction_amount DOUBLE, total_spend DOUBLE, risk_adjusted_clv DOUBLE) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION 's3://{S3_BUCKET}/raw/customer_transactions/' TBLPROPERTIES ('skip.header.line.count'='1')"""
    ]

    conn = get_athena_connection()
    try:
        cur = conn.cursor()
        for ddl in ddl_statements:
            cur.execute(ddl)
        logger.info("Athena external tables verified/created.")
    except Exception as exc:
        logger.exception("DDL creation failed: %s", exc)
        raise
    finally:
        conn.close()


def run_athena_consolidation():
    """Consolidate source domains into a single customer dataset."""
    sql = f"""
    WITH lending_source AS (
        SELECT household_id, age, job, marital, education, delinquency_flag_90D, churn_event, target
        FROM {CUSTOMER_LENDING_TABLE}
        WHERE household_id IS NOT NULL
    ),
    credit_source AS (
        SELECT household_id, credit_score, debt_to_income_ratio
        FROM {CREDIT_BUREAU_TABLE}
        WHERE household_id IS NOT NULL
    ),
    digital_source AS (
        SELECT household_id, login_frequency, mobile_app_active, digital_engagement_score
        FROM {DIGITAL_ACTIVITY_TABLE}
        WHERE household_id IS NOT NULL
    ),
    transaction_source AS (
        SELECT household_id, balance, transaction_count, avg_transaction_amount, total_spend, risk_adjusted_clv
        FROM {CUSTOMER_TRANSACTIONS_TABLE}
        WHERE household_id IS NOT NULL AND balance IS NOT NULL
    ),
    consolidated_customer_data AS (
        SELECT l.household_id, l.age, l.job, l.marital, l.education,
               c.credit_score, c.debt_to_income_ratio,
               d.login_frequency, d.mobile_app_active, d.digital_engagement_score,
               t.balance, t.transaction_count, t.avg_transaction_amount, t.total_spend, t.risk_adjusted_clv,
               l.delinquency_flag_90D, l.churn_event, l.target
        FROM lending_source l
        LEFT JOIN credit_source c ON l.household_id = c.household_id
        LEFT JOIN digital_source d ON l.household_id = d.household_id
        LEFT JOIN transaction_source t ON l.household_id = t.household_id
    )
    SELECT * FROM consolidated_customer_data
    """
    conn = get_athena_connection()
    try:
        df = pd.read_sql(sql, conn)
        logger.info("Rows after consolidation: %s", len(df))
        logger.info("Distinct households: %s", df["household_id"].nunique())
        return df
    except Exception as exc:
        logger.exception("Athena query failed: %s", exc)
        raise
    finally:
        conn.close()


def run_data_quality_audit(df):
    duplicate_households = int(df["household_id"].duplicated().sum())
    invalid_credit_scores = int((~df["credit_score"].between(300,850)).fillna(False).sum()) if 'credit_score' in df.columns else 0
    negative_balances = int((df['balance'] < 0).sum()) if 'balance' in df.columns else 0

    audit = pd.DataFrame({
        'metric_name':['total_rows','total_columns','duplicate_households','missing_values','invalid_credit_scores','negative_balances','distinct_households'],
        'metric_value':[len(df),len(df.columns),duplicate_households,int(df.isnull().sum().sum()),invalid_credit_scores,negative_balances,df['household_id'].nunique()]
    })

    audit.to_csv('data_quality_audit_summary.csv', index=False)
    pd.DataFrame({'column_name':df.columns,'missing_count':df.isnull().sum().values}).to_csv('data_quality_column_summary.csv', index=False)
    df[[c for c in ['credit_score','balance','total_spend','risk_adjusted_clv'] if c in df.columns]].describe(include='all').to_csv('descriptive_statistics.csv')


def clean_and_prepare_data(df):
    df = df.copy()
    numeric_cols=['credit_score','debt_to_income_ratio','balance','transaction_count','avg_transaction_amount','total_spend','risk_adjusted_clv','login_frequency','digital_engagement_score']
    for col in numeric_cols:
        if col in df.columns:
            df[col]=pd.to_numeric(df[col], errors='coerce')
    if 'credit_score' in df.columns:
        df=df[df['credit_score'].notna()]
        df=df[df['credit_score'].between(300,850)]
    if 'debt_to_income_ratio' in df.columns:
        df['debt_to_income_ratio']=df['debt_to_income_ratio'].fillna(df['debt_to_income_ratio'].median())
    return df


def engineer_features(df):
    df=df.copy()
    df['credit_risk_tier']=pd.cut(df['credit_score'], bins=[300,580,670,740,850], labels=['Poor','Fair','Good','Excellent'], include_lowest=True)
    try:
        df['credit_score_decile']=pd.qcut(df['credit_score'],10,labels=False,duplicates='drop')+1
    except Exception as exc:
        logger.warning('credit_score_decile skipped: %s', exc)
    df['high_dti_flag']=np.where(df['debt_to_income_ratio']>0.43,1,0)
    try:
        df['balance_decile']=pd.qcut(df['balance'],10,labels=False,duplicates='drop')+1
    except Exception as exc:
        logger.warning('balance_decile skipped: %s', exc)
    df['spend_per_transaction']=np.where(df['transaction_count']>0,df['total_spend']/df['transaction_count'],np.nan)
    max_login=max(df['login_frequency'].max(),1)
    df['engagement_score']=(df['login_frequency']/max_login)*df['digital_engagement_score']
    df['etl_run_date']=pd.Timestamp.utcnow()
    return df


def create_feature_summary():
    feature_df=pd.DataFrame([
        ['credit_risk_tier','credit_score','pd.cut','Risk'],
        ['credit_score_decile','credit_score','pd.qcut','Risk'],
        ['high_dti_flag','debt_to_income_ratio','np.where','Risk'],
        ['balance_decile','balance','pd.qcut','Segmentation'],
        ['spend_per_transaction','transactions','ratio','Behavioral'],
        ['engagement_score','digital_activity','normalized formula','Behavioral'],
        ['risk_adjusted_clv','transactions','source variable','Value']],
        columns=['feature_name','source_attribute','transformation_logic','feature_type'])
    feature_df.to_csv('feature_engineering_summary.csv', index=False)


if __name__ == '__main__':
    try:
        create_athena_tables()
        df=run_athena_consolidation()
        try:
            df.to_csv('bank-full.csv',index=False)
            logger.info('bank-full.csv created: %s', df.shape)
        except Exception as exc:
            logger.exception('bank-full export failed: %s', exc)
            raise
        run_data_quality_audit(df)
        final_df=engineer_features(clean_and_prepare_data(df))
        create_feature_summary()
        try:
            final_df.to_csv('final_analytics_ready_dataset.csv',index=False)
            logger.info('final_analytics_ready_dataset.csv created: %s', final_df.shape)
        except Exception as exc:
            logger.exception('final export failed: %s', exc)
            raise
        logger.info('ETL completed successfully')
    except Exception as exc:
        logger.exception('Pipeline execution failed: %s', exc)
        raise
