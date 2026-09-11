"""
AWS Cloud Analytics Sandbox
========================================================

Repository Workflow

Amazon S3 Data Lake
        ↓
Athena External Tables
        ↓
Athena Consolidation Query
(CTEs + LEFT JOIN Integration)
        ↓
Consolidated Base Dataset

bank-full.csv

        ↓

Pandas Data Quality Audit
        ↓
Data Cleaning & Preparation
        ↓
Feature Engineering
        ↓
Analytics Data Mart
        ↓

final_analytics_ready_dataset.csv
"""

import os
import logging
import numpy as np
import pandas as pd

from pyathena import connect


# ==========================================================
# CONFIGURATION
# ==========================================================

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1"
)

S3_BUCKET = os.getenv(
    "S3_BUCKET",
    "analytics-sandbox"
)

ATHENA_DATABASE = os.getenv(
    "ATHENA_DATABASE",
    "analytics_sandbox"
)

ATHENA_RESULTS = os.getenv(
    "ATHENA_RESULTS",
    f"s3://{S3_BUCKET}/athena_query_results/"
)

HOUSEHOLD_KEY = "household_id"


# ==========================================================
# TABLE MACROS
# ==========================================================

CUSTOMER_LENDING_TABLE = (
    f"{ATHENA_DATABASE}.customer_lending"
)

CREDIT_BUREAU_TABLE = (
    f"{ATHENA_DATABASE}.credit_bureau"
)

DIGITAL_ACTIVITY_TABLE = (
    f"{ATHENA_DATABASE}.digital_activity"
)

CUSTOMER_TRANSACTIONS_TABLE = (
    f"{ATHENA_DATABASE}.customer_transactions"
)


# ==========================================================
# LOGGING
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


# ==========================================================
# ATHENA CONNECTION
# ==========================================================

def get_athena_connection():

    return connect(
        s3_staging_dir=ATHENA_RESULTS,
        region_name=AWS_REGION
    )


# ==========================================================
# ATHENA MULTI-SOURCE CONSOLIDATION
# ==========================================================

def run_athena_consolidation() -> pd.DataFrame:

    logger.info(
        "Executing Athena multi-source consolidation query..."
    )

    sql = f"""

    WITH lending_source AS (

        SELECT

            household_id,
            age,
            job,
            marital,
            education,
            delinquency_flag_90D,
            churn_event,
            target

        FROM {CUSTOMER_LENDING_TABLE}

        WHERE household_id IS NOT NULL

    ),

    credit_source AS (

        SELECT

            household_id,
            credit_score,
            debt_to_income_ratio

        FROM {CREDIT_BUREAU_TABLE}

        WHERE household_id IS NOT NULL

    ),

    digital_source AS (

        SELECT

            household_id,
            login_frequency,
            mobile_app_active,
            digital_engagement_score

        FROM {DIGITAL_ACTIVITY_TABLE}

        WHERE household_id IS NOT NULL

    ),

    transaction_source AS (

        SELECT

            household_id,
            balance,
            transaction_count,
            avg_transaction_amount,
            total_spend

        FROM {CUSTOMER_TRANSACTIONS_TABLE}

        WHERE household_id IS NOT NULL

    ),

    consolidated_customer_data AS (

        SELECT

            l.household_id,

            /* Customer Data */

            l.age,
            l.job,
            l.marital,
            l.education,

            /* Credit Bureau Data */

            c.credit_score,
            c.debt_to_income_ratio,

            /* Digital Activity */

            d.login_frequency,
            d.mobile_app_active,
            d.digital_engagement_score,

            /* Banking Transactions */

            t.balance,
            t.transaction_count,
            t.avg_transaction_amount,
            t.total_spend,

            /* Outcome Variables */

            l.delinquency_flag_90D,
            l.churn_event,
            l.target

        FROM lending_source l

        LEFT JOIN credit_source c
            ON l.household_id = c.household_id

        LEFT JOIN digital_source d
            ON l.household_id = d.household_id

        LEFT JOIN transaction_source t
            ON l.household_id = t.household_id

    ),

    duplicate_check AS (

        SELECT

            *,

            ROW_NUMBER() OVER (

                PARTITION BY household_id

                ORDER BY household_id

            ) AS row_num

        FROM consolidated_customer_data

    )

    SELECT *

    FROM duplicate_check

    WHERE row_num = 1

    """

    conn = get_athena_connection()

    try:

        df = pd.read_sql(
            sql,
            conn
        )

        logger.info(
            f"Consolidation Complete. Shape: {df.shape}"
        )

        return df

    finally:

        conn.close()


# ==========================================================
# DATA QUALITY AUDIT
# ==========================================================

def run_data_quality_audit(
    df: pd.DataFrame
) -> pd.DataFrame:

    logger.info(
        "Running Data Quality Audit..."
    )

    audit_results = pd.DataFrame({

        "metric_name": [

            "total_rows",
            "total_columns",
            "duplicate_records",
            "missing_values"

        ],

        "metric_value": [

            len(df),

            len(df.columns),

            int(df.duplicated().sum()),

            int(
                df.isnull()
                .sum()
                .sum()
            )

        ]

    })

    audit_results.to_csv(
        "data_quality_audit_summary.csv",
        index=False
    )

    logger.info(
        "Data quality audit exported."
    )

    return audit_results


# ==========================================================
# DATA CLEANING
# ==========================================================

def clean_and_prepare_data(
    df: pd.DataFrame
) -> pd.DataFrame:

    logger.info(
        "Running Data Cleaning & Preparation..."
    )

    df = df.copy()

    # Credit Score Validation

    if "credit_score" in df.columns:

        df = df[
            df["credit_score"].between(
                300,
                850
            )
        ]

    # DTI Imputation

    if "debt_to_income_ratio" in df.columns:

        median_dti = (
            df["debt_to_income_ratio"]
            .median()
        )

        df["debt_to_income_ratio"] = (

            df["debt_to_income_ratio"]
            .fillna(median_dti)

        )

    return df


# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

def engineer_features(
    df: pd.DataFrame
) -> pd.DataFrame:

    logger.info(
        "Running Feature Engineering..."
    )

    df = df.copy()

    # ---------------------------------------
    # Credit Features
    # ---------------------------------------

    if "credit_score" in df.columns:

        df["credit_risk_tier"] = pd.cut(

            df["credit_score"],

            bins=[
                300,
                580,
                670,
                740,
                850
            ],

            labels=[
                "Poor",
                "Fair",
                "Good",
                "Excellent"
            ],

            include_lowest=True

        )

    if "debt_to_income_ratio" in df.columns:

        df["high_dti_flag"] = np.where(

            df["debt_to_income_ratio"] > 0.43,

            1,

            0

        )

    # ---------------------------------------
    # Balance Features
    # ---------------------------------------

    if "balance" in df.columns:

        df["balance_decile"] = pd.qcut(

            df["balance"],

            q=10,

            labels=False,

            duplicates="drop"

        ) + 1

    # ---------------------------------------
    # Transaction Features
    # ---------------------------------------

    if (
        "total_spend" in df.columns
        and
        "transaction_count" in df.columns
    ):

        df["spend_per_transaction"] = (

            df["total_spend"]

            /

            df["transaction_count"]
            .replace(
                0,
                np.nan
            )

        )

    # ---------------------------------------
    # Digital Activity Features
    # ---------------------------------------

    if (
        "login_frequency" in df.columns
        and
        "digital_engagement_score" in df.columns
    ):

        df["engagement_score"] = (

            df["login_frequency"]

            *

            df["digital_engagement_score"]

        )

    logger.info(
        f"Feature Engineering Complete. Shape: {df.shape}"
    )

    return df


# ==========================================================
# FEATURE DOCUMENTATION
# ==========================================================

def create_feature_summary():

    feature_df = pd.DataFrame([

        [

            "credit_risk_tier",
            "credit_score",
            "Credit score grouped into risk bands"

        ],

        [

            "high_dti_flag",
            "debt_to_income_ratio",
            "Debt-to-income threshold indicator"

        ],

        [

            "balance_decile",
            "balance",
            "Account balance grouped into 10 equal-size deciles"

        ],

        [

            "spend_per_transaction",
            "total_spend / transaction_count",
            "Average spend per transaction"

        ],

        [

            "engagement_score",
            "login_frequency * digital_engagement_score",
            "Customer engagement metric"

        ]

    ],

    columns=[

        "feature_name",
        "source_attribute",
        "description"

    ])

    feature_df.to_csv(
        "feature_engineering_summary.csv",
        index=False
    )


# ==========================================================
# MAIN EXECUTION
# ==========================================================

if __name__ == "__main__":

    logger.info(
        "Starting AWS Cloud Analytics Sandbox ETL..."
    )

    # --------------------------------------------------
    # Athena Consolidation
    # --------------------------------------------------

    consolidated_df = run_athena_consolidation()

    # Intermediate Consolidated Dataset

    consolidated_df.to_csv(
        "bank-full.csv",
        index=False
    )

    logger.info(
        "bank-full.csv created."
    )

    # --------------------------------------------------
    # Data Quality Audit
    # --------------------------------------------------

    run_data_quality_audit(
        consolidated_df
    )

    # --------------------------------------------------
    # Data Cleaning
    # --------------------------------------------------

    cleaned_df = clean_and_prepare_data(
        consolidated_df
    )

    # --------------------------------------------------
    # Feature Engineering
    # --------------------------------------------------

    final_df = engineer_features(
        cleaned_df
    )

    create_feature_summary()

    # --------------------------------------------------
    # Final Analytics Dataset
    # --------------------------------------------------

    final_df.to_csv(
        "final_analytics_ready_dataset.csv",
        index=False
    )

    logger.info(
        "ETL completed successfully."
    )

    logger.info(
        "Outputs generated:"
    )

    logger.info(
        " - bank-full.csv"
    )

    logger.info(
        " - final_analytics_ready_dataset.csv"
    )

    logger.info(
        " - data_quality_audit_summary.csv"
    )

    logger.info(
        " - feature_engineering_summary.csv"
    )

    logger.info(
        " - pipeline_execution.log"
    )
