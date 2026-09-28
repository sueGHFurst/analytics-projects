"""
00_enterprise_data_foundation_cloud.py
Enterprise Data Quality & Cloud Data Foundation Pipeline (Project 00)
=====================================================================================
Directory Structure: C:\\Users\\User\\00-cloud-framework
- Data Output: C:\\Users\\User\\00-cloud-framework\\data\\

Execution Mode: Cloud-Connected Production (Amazon Athena / S3) with Local Fallback
- Phase 1: Multi-Table Secure Cloud Extraction via Amazon Athena CTEs & S3
- Phase 2: 5-Step Data Hardening Sequence (Deduplication, Zero Imputation, Logical 
           Bounding, Statistical Winsorization [5% floor / 95% cap], and Campaign Filtering)
"""

import os
import logging
import numpy as np
import pandas as pd

try:
    from pyathena import connection
except ImportError:
    connection = None

# =====================================================================
# 1. Environment & Directory Configuration
# =====================================================================
BASE_DIR = r"C:\Users\User\00-cloud-framework"
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "enterprise-customer-data-lake")
ATHENA_RESULTS = os.getenv("ATHENA_RESULTS", f"s3://{S3_BUCKET}/athena_query_results/")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "enterprise_pipeline_execution.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# =====================================================================
# 2. Phase 1: Multi-Table Cloud Extraction & Consolidation
# =====================================================================
def establish_athena_connection():
    """Establish secure connection to Amazon Athena via PyAthena."""
    if connection is None:
        raise ImportError("pyathena module not installed.")
    try:
        conn = connection.connect(
            s3_staging_dir=ATHENA_RESULTS,
            region_name=AWS_REGION
        )
        logger.info("Successfully established connection to Amazon Athena in region %s.", AWS_REGION)
        return conn
    except Exception as exc:
        logger.exception("Failed to connect to Amazon Athena: %s", exc)
        raise

def extract_cloud_datasets(conn):
    """Execute multi-table CTE cloud extraction across credit bureau, transactions, and demographics."""
    
    # Pull 1: Demographics, UCI Features, and Consolidated Credit Profiles
    query_pull1 = """
        WITH base_demographics AS (
            SELECT household_id, age, job, marital, education, housing, loan
            FROM enterprise_customer_db.customer_demographic_info
        ),
        consolidated_credit AS (
            SELECT 
                COALESCE(hp.household_id, cb.household_id) AS household_id,
                COALESCE(hp.credit_score, cb.credit_score) AS credit_score,
                COALESCE(hp.debt_to_income_ratio, cb.debt_to_income_ratio) AS debt_to_income_ratio
            FROM enterprise_customer_db.household_credit_profile hp
            FULL OUTER JOIN enterprise_customer_db.credit_bureau_data cb 
                ON hp.household_id = cb.household_id
        )
        SELECT 
            m.household_id, d.age, d.job, d.marital, d.education, d.housing, d.loan,
            m.balance, m.campaign, m.pdays, m.previous, m.target,
            cr.credit_score, cr.debt_to_income_ratio
        FROM enterprise_customer_db.uci_bank_marketing_features m
        LEFT JOIN base_demographics d ON m.household_id = d.household_id
        LEFT JOIN consolidated_credit cr ON m.household_id = cr.household_id
    """
    logger.info("Executing Cloud Pull 1 (Demographics, Credit, & UCI Features)...")
    df_pull1 = pd.read_sql(query_pull1, conn)
    logger.info("Cloud Pull 1 complete: Ingested %d records.", len(df_pull1))

    # Pull 2: Transaction Aggregations and Digital Activity Telemetry (using FULL OUTER JOIN for full integrity)
    query_pull2 = """
        WITH transaction_summary AS (
            SELECT 
                household_id,
                COUNT(transaction_id) AS transaction_count,
                SUM(transaction_amount) AS total_transaction_volume,
                MAX(transaction_timestamp) AS last_transaction_timestamp
            FROM enterprise_customer_db.customer_transactions_data
            GROUP BY household_id
        ),
        digital_activity_summary AS (
            SELECT 
                household_id,
                COUNT(session_id) AS login_frequency,
                AVG(session_duration_minutes) AS avg_session_duration
            FROM enterprise_customer_db.household_digital_activity
            GROUP BY household_id
        )
        SELECT 
            COALESCE(t.household_id, d.household_id) AS household_id,
            COALESCE(t.transaction_count, 0) AS transaction_count,
            COALESCE(t.total_transaction_volume, 0.0) AS total_transaction_volume,
            t.last_transaction_timestamp,
            COALESCE(d.login_frequency, 0) AS login_frequency,
            COALESCE(d.avg_session_duration, 0.0) AS avg_session_duration
        FROM transaction_summary t
        FULL OUTER JOIN digital_activity_summary d ON t.household_id = d.household_id
    """
    logger.info("Executing Cloud Pull 2 (Transactions & Digital Telemetry)...")
    df_pull2 = pd.read_sql(query_pull2, conn)
    logger.info("Cloud Pull 2 complete: Ingested %d telemetry records.", len(df_pull2))

    # Merge datasets on household_id grain
    logger.info("Merging Cloud Pull 1 and Pull 2 datasets on household_id grain...")
    df_raw = pd.merge(df_pull1, df_pull2, on="household_id", how="left")
    logger.info("Consolidated raw cloud dataset shape: %d rows, %d columns.", len(df_raw), len(df_raw.columns))
    return df_raw


# =====================================================================
# 3. Phase 2: The 5-Step Data Hardening Sequence
# =====================================================================
def execute_data_hardening(df_raw):
    """Apply rigorous data quality, cleaning, and transformation rules."""
    logger.info("Initiating 5-Step Data Hardening Sequence...")
    
    # Step 1: Structural Deduplication on household_id grain (keeping latest record)
    df = df_raw.drop_duplicates(subset=["household_id"], keep="last").copy()
    logger.info("Step 1 (Deduplication) complete. Records remaining: %d", len(df))

    # Step 2: Zero Imputation for missing transaction and login counts
    for col in ["transaction_count", "login_frequency"]:
        if col in df.columns:
            missing_count = df[col].isnull().sum()
            df[col] = df[col].fillna(0)
            logger.info("Step 2 (Zero Imputation): Imputed %d missing values in '%s' to 0.", missing_count, col)

    # Step 3: Logical Bounding & Preservation of Valid Negative Balances
    if "credit_score" in df.columns:
        df["credit_score"] = df["credit_score"].clip(lower=300, upper=850)
        
    if "debt_to_income_ratio" in df.columns:
        valid_dti = df.loc[(df["debt_to_income_ratio"] >= 0.0) & (df["debt_to_income_ratio"] <= 1.0), "debt_to_income_ratio"]
        median_dti = valid_dti.median() if not valid_dti.empty else 0.25
        df.loc[(df["debt_to_income_ratio"] < 0.0) | (df["debt_to_income_ratio"] > 1.0), "debt_to_income_ratio"] = median_dti
        logger.info("Step 3 (Logical Bounding DTI): Bounded DTI [0.0, 1.0] using median substitution (%.4f).", median_dti)

    if "balance" in df.columns:
        negative_count = (df["balance"] < 0).sum()
        logger.info("Step 3 (Logical Bounding Balance): Retained %d negative balances as raw transmission error codes.", negative_count)

    # Step 4: Statistical Winsorization (5% lower floor, 95% upper cap)
    logger.info("Step 4: Applying statistical Winsorization across continuous financial features...")
    winsor_cols = [c for c in ["balance", "credit_score", "debt_to_income_ratio", "transaction_count"] if c in df.columns]
    for col in winsor_cols:
        lower_cap = df[col].quantile(0.05)
        upper_cap = df[col].quantile(0.95)
        df[col] = df[col].clip(lower=lower_cap, upper=upper_cap)
        logger.info("Winsorized '%s': 5th percentile floor = %.4f, 95th percentile cap = %.4f", col, lower_cap, upper_cap)
    
    # Save base hardened dataset to data/ folder
    bank_full_path = os.path.join(DATA_DIR, "bank-full.csv")
    df.to_csv(bank_full_path, index=False)
    logger.info("Base hardened dataset saved: '%s' (%d records).", bank_full_path, len(df))

    # Step 5: Active Campaign Response Filtering (target == 1)
    if "target" in df.columns:
        df_final = df[df["target"] == 1].reset_index(drop=True)
    else:
        df_final = df.copy()
    
    final_dataset_path = os.path.join(DATA_DIR, "final_analytics_ready_dataset.csv")
    df_final.to_csv(final_dataset_path, index=False)
    logger.info("Final modeling dataset saved: '%s' (%d records).", final_dataset_path, len(df_final))
    
    return df, df_final


# =====================================================================
# 4. Main Execution Controller
# =====================================================================
def main():
    logger.info("Starting Enterprise Data Foundation Pipeline Execution (Project 00)...")
    
    try:
        conn = establish_athena_connection()
        df_raw = extract_cloud_datasets(conn)
    except Exception as exc:
        logger.warning("Athena connection unavailable (%s). Loading local hardened dataset from data/...", exc)
        fallback_path = os.path.join(DATA_DIR, "bank-full.csv")
        if os.path.exists(fallback_path):
            df_raw = pd.read_csv(fallback_path)
            logger.info("Successfully loaded local fallback dataset: '%s'.", fallback_path)
        else:
            logger.info("No local dataset found. Generating synthetic fallback simulation baseline...")
            np.random.seed(42)
            n = 10000
            df_raw = pd.DataFrame({
                'household_id': [f"HH_{i:07d}" for i in range(n)],
                'age': np.random.randint(18, 85, n),
                'job': np.random.choice(['admin.', 'blue-collar', 'technician', 'management'], n),
                'marital': np.random.choice(['single', 'married', 'divorced'], n),
                'education': np.random.choice(['secondary', 'tertiary', 'primary'], n),
                'housing': np.random.choice(['yes', 'no'], n),
                'loan': np.random.choice(['yes', 'no'], n),
                'balance': np.clip(np.random.exponential(scale=2500, size=n) + 1500, -500, 50000),
                'campaign': np.random.poisson(2, n),
                'pdays': np.random.choice([-1, 30, 90], n),
                'previous': np.random.poisson(1, n),
                'credit_score': np.clip(np.random.normal(680, 55, n), 300, 850),
                'debt_to_income_ratio': np.random.beta(2, 5, n),
                'transaction_count': np.random.poisson(12, n),
                'total_transaction_volume': np.random.exponential(2500, n),
                'login_frequency': np.random.poisson(8, n),
                'target': np.random.binomial(1, 0.756, n)
            })

    # Execute Hardening & Save Canonical Outputs
    execute_data_hardening(df_raw)
    logger.info("Project 00 data engineering pipeline execution completed successfully.")

if __name__ == "__main__":
    main()