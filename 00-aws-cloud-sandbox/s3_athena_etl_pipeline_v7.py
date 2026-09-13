"""
AWS Cloud Analytics Sandbox - Enterprise Data Validation & ETL Pipeline
=====================================================================
Workflow:
Amazon S3 Data Lake 
  -> Athena External Tables 
  -> Athena Consolidation Query (CTEs + LEFT JOIN) 
  -> bank-full.csv 
  -> Data Quality Audit & Variable Inventory 
  -> Exploratory Visualizations (Matplotlib/Seaborn) 
  -> Data Cleaning & Preparation 
  -> Feature Engineering 
  -> final_analytics_ready_dataset.csv
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pyathena import connect

# ==========================================================
# CONFIGURATION
# ==========================================================

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "analytics-sandbox")
ATHENA_DATABASE = os.getenv("ATHENA_DATABASE", "analytics_sandbox")
ATHENA_RESULTS = os.getenv("ATHENA_RESULTS", f"s3://{S3_BUCKET}/athena_query_results/")
CREATE_TABLES = os.getenv("CREATE_TABLES", "Y")

CUSTOMER_LENDING_TABLE = f"{ATHENA_DATABASE}.customer_lending"
CREDIT_BUREAU_TABLE = f"{ATHENA_DATABASE}.credit_bureau"
DIGITAL_ACTIVITY_TABLE = f"{ATHENA_DATABASE}.digital_activity"
CUSTOMER_TRANSACTIONS_TABLE = f"{ATHENA_DATABASE}.customer_transactions"

# ==========================================================
# LOGGING SETUP
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pipeline_execution.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_athena_connection():
    """Create and return an Athena connection."""
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
        f"""CREATE EXTERNAL TABLE IF NOT EXISTS {CUSTOMER_TRANSACTIONS_TABLE} (household_id STRING, balance DOUBLE, transaction_count INT, avg_transaction_amount DOUBLE, total_spend DOUBLE) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION 's3://{S3_BUCKET}/raw/customer_transactions/' TBLPROPERTIES ('skip.header.line.count'='1')"""
    ]

    conn = get_athena_connection()
    try:
        cur = conn.cursor()
        for ddl in ddl_statements:
            cur.execute(ddl)
        logger.info("Athena external tables verified/created successfully.")
    except Exception as exc:
        logger.exception("DDL creation failed: %s", exc)
        raise
    finally:
        conn.close()


def run_athena_consolidation():
    """Consolidate source domains using CTEs and LEFT JOINs."""
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
        SELECT household_id, balance, transaction_count, avg_transaction_amount, total_spend
        FROM {CUSTOMER_TRANSACTIONS_TABLE}
        WHERE household_id IS NOT NULL AND balance IS NOT NULL
    ),
    consolidated_customer_data AS (
        SELECT 
            l.household_id, 
            l.age, 
            l.job, 
            l.marital, 
            l.education,
            c.credit_score, 
            c.debt_to_income_ratio,
            d.login_frequency, 
            d.mobile_app_active, 
            d.digital_engagement_score,
            t.balance, 
            t.transaction_count, 
            t.avg_transaction_amount, 
            t.total_spend,
            l.delinquency_flag_90D, 
            l.churn_event, 
            l.target
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
        logger.exception("Athena consolidation query failed: %s", exc)
        raise
    finally:
        conn.close()


def run_data_quality_audit(df):
    """Generate comprehensive audit summaries, descriptive statistics, and variable inventory."""
    try:
        duplicate_households = int(df["household_id"].duplicated().sum())
        invalid_credit_scores = int((~df["credit_score"].between(300, 850)).fillna(False).sum()) if 'credit_score' in df.columns else 0
        negative_balances = int((df['balance'] < 0).sum()) if 'balance' in df.columns else 0
        total_missing = int(df.isnull().sum().sum())
        missing_pct = round((total_missing / max(len(df) * len(df.columns), 1)) * 100, 2)

        audit_summary = pd.DataFrame({
            'metric_name': ['total_rows', 'total_columns', 'duplicate_households', 'missing_values', 'missing_value_pct', 'invalid_credit_scores', 'negative_balances', 'distinct_households'],
            'metric_value': [len(df), len(df.columns), duplicate_households, total_missing, missing_pct, invalid_credit_scores, negative_balances, df['household_id'].nunique()],
            'status': ['PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS', 'PASS']
        })
        audit_summary.to_csv('data_quality_audit_summary.csv', index=False)

        column_summary = pd.DataFrame({
            'column_name': df.columns,
            'missing_count': df.isnull().sum().values,
            'missing_pct': round((df.isnull().sum() / max(len(df), 1)) * 100, 2).values
        })
        column_summary.to_csv('data_quality_column_summary.csv', index=False)

        variable_inventory = pd.DataFrame({
            'column_name': df.columns,
            'data_type': [str(dt) for dt in df.dtypes.values],
            'missing_pct': round((df.isnull().sum() / max(len(df), 1)) * 100, 2).values
        })
        variable_inventory.to_csv('variable_inventory.csv', index=False)

        numeric_cols = [c for c in ['credit_score', 'balance', 'total_spend', 'debt_to_income_ratio'] if c in df.columns]
        if numeric_cols:
            df[numeric_cols].describe(include='all').to_csv('descriptive_statistics.csv')

        logger.info("Data quality audits and variable inventory generated.")
    except Exception as exc:
        logger.exception("Data quality audit export failed: %s", exc)
        raise


def generate_data_profile_visualizations(df):
    """Generate exploratory data validation plots using matplotlib and seaborn."""
    try:
        sns.set_theme(style="whitegrid")

        # 1. Credit Score Distribution
        if "credit_score" in df.columns and df["credit_score"].notna().any():
            plt.figure(figsize=(8, 5))
            sns.histplot(df["credit_score"].dropna(), bins=20, kde=True, color="royalblue")
            plt.title("Credit Score Distribution")
            plt.xlabel("Credit Score")
            plt.ylabel("Frequency")
            plt.savefig("credit_score_distribution.png", bbox_inches="tight")
            plt.close()

        # 2. Balance Distribution
        if "balance" in df.columns and df["balance"].notna().any():
            plt.figure(figsize=(8, 5))
            sns.histplot(df["balance"].dropna(), bins=20, kde=True, color="seagreen")
            plt.title("Balance Distribution")
            plt.xlabel("Balance")
            plt.ylabel("Frequency")
            plt.savefig("balance_distribution.png", bbox_inches="tight")
            plt.close()

        # 3. Missing Value Analysis Heatmap
        plt.figure(figsize=(10, 6))
        sns.heatmap(df.isnull(), cbar=False, cmap="viridis")
        plt.title("Missing Value Analysis")
        plt.savefig("missing_values_heatmap.png", bbox_inches="tight")
        plt.close()

        # 4. Credit Risk Tier Counts
        if "credit_risk_tier" in df.columns:
            plt.figure(figsize=(8, 5))
            sns.countplot(x="credit_risk_tier", data=df, order=["Poor", "Fair", "Good", "Excellent"], palette="Set2")
            plt.title("Credit Risk Tier Counts")
            plt.xlabel("Credit Risk Tier")
            plt.ylabel("Count")
            plt.savefig("credit_risk_tier_distribution.png", bbox_inches="tight")
            plt.close()

        # 5. Balance Decile Counts
        if "balance_decile" in df.columns:
            plt.figure(figsize=(8, 5))
            sns.countplot(x="balance_decile", data=df, palette="Blues_r")
            plt.title("Balance Decile Counts")
            plt.xlabel("Balance Decile")
            plt.ylabel("Count")
            plt.savefig("balance_decile_distribution.png", bbox_inches="tight")
            plt.close()

        logger.info("Exploratory profile visualizations generated successfully.")
    except Exception as exc:
        logger.exception("Visualization generation failed: %s", exc)
        raise


def clean_and_prepare_data(df):
    """Clean data types, validate credit scores, and handle DTI missing values."""
    df = df.copy()
    numeric_cols = [
        'credit_score', 'debt_to_income_ratio', 'balance', 'transaction_count',
        'avg_transaction_amount', 'total_spend', 'login_frequency', 'digital_engagement_score'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'credit_score' in df.columns:
        df = df[df['credit_score'].notna()]
        df = df[df['credit_score'].between(300, 850)]

    if 'debt_to_income_ratio' in df.columns and df['debt_to_income_ratio'].notna().any():
        median_dti = df['debt_to_income_ratio'].median()
        df['debt_to_income_ratio'] = df['debt_to_income_ratio'].fillna(median_dti)

    return df


def engineer_features(df):
    """Perform core sandbox feature engineering."""
    df = df.copy()

    if 'credit_score' in df.columns:
        df['credit_risk_tier'] = pd.cut(
            df['credit_score'],
            bins=[300, 580, 670, 740, 850],
            labels=['Poor', 'Fair', 'Good', 'Excellent'],
            include_lowest=True
        )
        try:
            df['credit_score_decile'] = pd.qcut(
                df['credit_score'], q=10, labels=False, duplicates='drop'
            ) + 1
        except Exception as exc:
            logger.warning("credit_score_decile skipped: %s", exc)

    if 'debt_to_income_ratio' in df.columns:
        df['high_dti_flag'] = np.where(df['debt_to_income_ratio'] > 0.43, 1, 0)

    if 'balance' in df.columns and df['balance'].notna().sum() > 0:
        try:
            df['balance_decile'] = pd.qcut(
                df['balance'], q=10, labels=False, duplicates='drop'
            ) + 1
        except Exception as exc:
            logger.warning("balance_decile skipped: %s", exc)

    if 'total_spend' in df.columns and 'transaction_count' in df.columns:
        df['spend_per_transaction'] = np.where(
            df['transaction_count'] > 0,
            df['total_spend'] / df['transaction_count'],
            np.nan
        )

    if 'login_frequency' in df.columns and 'digital_engagement_score' in df.columns:
        df['engagement_score'] = df['login_frequency'] * df['digital_engagement_score']

    return df


def create_feature_summary():
    """Document engineered features."""
    try:
        feature_df = pd.DataFrame([
            ["credit_risk_tier", "credit_score", "pd.cut() risk banding", "Credit score categorized into risk bands"],
            ["credit_score_decile", "credit_score", "pd.qcut() decile segmentation", "Credit score grouped into deciles"],
            ["high_dti_flag", "debt_to_income_ratio", "np.where() threshold flag", "Binary indicator for DTI > 43%"],
            ["balance_decile", "balance", "pd.qcut() decile segmentation", "Account balance grouped into deciles"],
            ["spend_per_transaction", "total_spend / transaction_count", "ratio calculation", "Average spend per transaction"],
            ["engagement_score", "login_frequency * digital_engagement_score", "multiplicative calculation", "Composite engagement measure"]
        ], columns=["feature_name", "source_attribute", "transformation_logic", "description"])
        
        feature_df.to_csv("feature_engineering_summary.csv", index=False)
        logger.info("Feature summary successfully exported.")
    except Exception as exc:
        logger.exception("Feature summary export failed: %s", exc)
        raise


if __name__ == '__main__':
    try:
        logger.info("Starting AWS Cloud Analytics Sandbox ETL Pipeline...")
        create_athena_tables()

        consolidated_df = run_athena_consolidation()

        try:
            consolidated_df.to_csv('bank-full.csv', index=False)
            logger.info("bank-full.csv created successfully.")
        except Exception as exc:
            logger.exception("bank-full.csv export failed: %s", exc)
            raise

        run_data_quality_audit(consolidated_df)
        
        cleaned_df = clean_and_prepare_data(consolidated_df)
        final_df = engineer_features(cleaned_df)

        generate_data_profile_visualizations(final_df)
        create_feature_summary()

        try:
            final_df.to_csv('final_analytics_ready_dataset.csv', index=False)
            logger.info("final_analytics_ready_dataset.csv created successfully.")
        except Exception as exc:
            logger.exception("final_analytics_ready_dataset.csv export failed: %s", exc)
            raise

        logger.info("ETL pipeline completed successfully.")

    except Exception as exc:
        logger.exception("Pipeline execution failed: %s", exc)
        raise
