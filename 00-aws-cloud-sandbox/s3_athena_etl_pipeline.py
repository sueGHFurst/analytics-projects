"""
AWS Cloud Analytics Sandbox
========================================================

Repository Workflow

Amazon S3 Data Lake
        ↓
Athena External Tables
        ↓
Athena Consolidation Query
(LEFT JOIN Integration)
        ↓
Consolidated Analytics Dataset
        ↓
Pandas Data Quality Audit
        ↓
Data Cleaning & Preparation
        ↓
Feature Engineering
        ↓
Final Analytics Dataset

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
    "midwest-lending-analytics"
)

ATHENA_DATABASE = os.getenv(
    "ATHENA_DATABASE",
    "midwest_lending_analytics"
)

ATHENA_RESULTS = os.getenv(
    "ATHENA_RESULTS",
    f"s3://{S3_BUCKET}/athena_query_results/"
)

HOUSEHOLD_KEY = "household_id"


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
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
# ATHENA CONSOLIDATION
# ==========================================================

def run_athena_consolidation() -> pd.DataFrame:

    logger.info(
        "Executing Athena multi-source data consolidation..."
    )

    sql = f"""

    WITH lending_source AS (

        SELECT *
        FROM {ATHENA_DATABASE}.customer_lending

    ),

    credit_source AS (

        SELECT *
        FROM {ATHENA_DATABASE}.credit_bureau

    ),

    digital_source AS (

        SELECT *
        FROM {ATHENA_DATABASE}.digital_activity

    ),

    transaction_source AS (

        SELECT *
        FROM {ATHENA_DATABASE}.customer_transactions

    ),

    marketing_source AS (

        SELECT *
        FROM {ATHENA_DATABASE}.marketing_campaigns

    ),

    consolidated_customer_data AS (

        SELECT

            l.household_id,

            /* Demographics */

            l.age,
            l.job,
            l.marital,
            l.education,

            /* Credit Bureau */

            c.credit_score,
            c.debt_to_income_ratio,

            /* Digital Activity */

            d.login_frequency,
            d.mobile_app_active,
            d.digital_engagement_score,

            /* Banking Transactions */

            t.transaction_count,
            t.avg_transaction_amount,
            t.total_spend,

            /* Marketing */

            m.campaign,
            m.previous,

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

        LEFT JOIN marketing_source m
            ON l.household_id = m.household_id

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

        df = pd.read_sql(sql, conn)

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

    audit_results = {

        "total_rows": len(df),

        "total_columns": len(df.columns),

        "duplicate_records":
            int(df.duplicated().sum())
    }

    audit_df = pd.DataFrame(
        audit_results.items(),
        columns=["metric_name", "metric_value"]
    )

    audit_df.to_csv(
        "data_quality_audit_summary.csv",
        index=False
    )

    return audit_df


# ==========================================================
# DATA CLEANING
# ==========================================================

def clean_and_prepare_data(
    df: pd.DataFrame
) -> pd.DataFrame:

    logger.info(
        "Data Cleaning & Preparation..."
    )

    df = df.copy()

    if "credit_score" in df.columns:

        df = df[
            df["credit_score"].between(
                300,
                850
            )
        ]

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
        "Feature Engineering..."
    )

    df = df.copy()

    # Credit Bureau Features

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

    # Transaction Features

    if (
        "total_spend" in df.columns
        and
        "transaction_count" in df.columns
    ):

        df["spend_per_transaction"] = (

            df["total_spend"]

            /

            df["transaction_count"]
            .replace(0, np.nan)

        )

    # Digital Activity Features

    if (
        "login_frequency" in df.columns
        and
        "mobile_app_active" in df.columns
    ):

        df["engagement_score"] = (

            df["login_frequency"]

            *

            (
                df["mobile_app_active"]
                + 1
            )

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
            "Risk Tier"
        ],

        [
            "high_dti_flag",
            "debt_to_income_ratio",
            "DTI Flag"
        ],

        [
            "spend_per_transaction",
            "total_spend / transaction_count",
            "Transaction Efficiency"
        ],

        [
            "engagement_score",
            "digital activity",
            "Engagement Metric"
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

    consolidated_df = run_athena_consolidation()

    run_data_quality_audit(
        consolidated_df
    )

    cleaned_df = clean_and_prepare_data(
        consolidated_df
    )

    final_df = engineer_features(
        cleaned_df
    )

    create_feature_summary()

    final_df.to_csv(

        "final_analytics_ready_dataset.csv",

        index=False

    )

    logger.info(
        "Final Analytics Dataset Created."
    )

    logger.info(
        "Outputs:"
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
