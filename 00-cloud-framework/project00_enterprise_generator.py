"""
PROJECT 00
Cloud Analytics Framework & Customer Intelligence Platform

Outputs
-------
bank_full.csv
final_analytics_ready_dataset.csv
data_dictionary.csv
validation_report.csv
hash_manifest.csv
project01_handoff.json

Author: Susan Furst
Version: 1.0
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42

RAW_RECORDS = 310_245
BANK_FULL_ROWS = 299_332
ANALYTICS_ROWS = 226_534

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

np.random.seed(RANDOM_SEED)

# ============================================================
# CORE90 FEATURE CATALOG
# ============================================================

FEATURE_GROUPS = {

    "Demographics": [
        "customer_id",
        "household_id",
        "age",
        "gender",
        "marital_status",
        "annual_income",
        "employment_status",
        "occupation",
        "education",
        "state",
        "region",
        "zipcode",
    ],

    "AccountBalance": [
        "checking_balance",
        "savings_balance",
        "avg_daily_balance",
        "balance_volatility",
        "deposit_count",
        "withdrawal_count",
        "monthly_balance",
        "quarterly_balance",
        "annual_balance",
        "balance_decile",
        "overdraft_count",
        "overdraft_amount",
        "cash_reserve_ratio",
        "liquidity_ratio",
        "household_net_worth",
        "investment_balance",
        "retirement_balance",
        "household_assets",
        "household_liabilities",
    ],

    "CreditLending": [
        "credit_score",
        "credit_score_decile",
        "credit_limit",
        "credit_card_balance",
        "utilization_ratio",
        "mortgage_balance",
        "auto_loan_balance",
        "student_loan_balance",
        "debt_to_income_ratio",
        "hard_inquiries_6m",
        "delinquency_flag_30d",
        "delinquency_flag_60d",
        "delinquency_flag_90d",
        "bankruptcy_flag",
        "risk_tier",
        "risk_score",
    ],

    "Behavioral": [
        "txn_count_30d",
        "txn_count_90d",
        "txn_count_365d",
        "digital_login_count_30d",
        "digital_login_count_90d",
        "mobile_app_active",
        "avg_session_duration",
        "website_visits",
        "page_views",
        "engagement_score",
        "engagement_decile",
        "channel_diversity_score",
        "email_opens",
        "email_clicks",
        "sms_clicks",
        "push_clicks",
        "response_rate",
        "campaign_contacts",
        "campaign_success_rate",
        "interaction_velocity",
        "application_starts",
        "application_completions",
    ],

    "Products": [
        "has_checking",
        "has_savings",
        "has_credit_card",
        "has_mortgage",
        "has_auto_loan",
        "has_investment",
        "num_products",
        "cross_sell_score",
        "upsell_score",
        "product_diversity_score",
    ],

    "RiskCompliance": [
        "aml_risk_score",
        "customer_risk_score",
        "risk_adjusted_clv",
        "attrition_risk_score",
        "default_probability",
        "propensity_score",
        "retention_probability",
        "customer_lifetime_value",
        "high_dti_flag",
        "high_utilization_flag",
        "compliance_review_flag",
        "analytics_ready_flag",
    ]
}

# ============================================================
# DATA GENERATION
# ============================================================

def generate_core_dataset(n_rows=RAW_RECORDS):

    df = pd.DataFrame()

    df["customer_id"] = np.arange(1, n_rows + 1)

    df["household_id"] = np.random.randint(
        1,
        int(n_rows * 0.75),
        n_rows
    )

    df["age"] = np.random.randint(18, 85, n_rows)

    df["annual_income"] = np.random.lognormal(
        mean=11,
        sigma=.5,
        size=n_rows
    )

    df["credit_score"] = np.random.normal(
        700,
        75,
        n_rows
    ).clip(300, 850)

    df["checking_balance"] = np.random.gamma(
        5,
        1000,
        n_rows
    )

    df["savings_balance"] = np.random.gamma(
        6,
        2500,
        n_rows
    )

    df["credit_limit"] = np.random.randint(
        1000,
        50000,
        n_rows
    )

    df["credit_card_balance"] = (
        df["credit_limit"] *
        np.random.uniform(.05, .95, n_rows)
    )

    df["utilization_ratio"] = (
        df["credit_card_balance"] /
        df["credit_limit"]
    )

    df["debt_to_income_ratio"] = np.random.uniform(
        0,
        1,
        n_rows
    )

    df["txn_count_30d"] = np.random.poisson(
        12,
        n_rows
    )

    df["txn_count_90d"] = (
        df["txn_count_30d"] *
        np.random.randint(2, 5, n_rows)
    )

    df["digital_login_count_30d"] = np.random.poisson(
        8,
        n_rows
    )

    df["campaign_contacts"] = np.random.poisson(
        3,
        n_rows
    )

    df["engagement_score"] = np.random.uniform(
        0,
        100,
        n_rows
    )

    df["target"] = np.random.choice(
        [0, 1],
        n_rows,
        p=[0.28, 0.72]
    )

    return df

# ============================================================
# FEATURE ENGINEERING
# ============================================================

def engineer_features(df):

    df["credit_score_decile"] = pd.qcut(
        df["credit_score"],
        10,
        labels=False,
        duplicates="drop"
    )

    df["balance_decile"] = pd.qcut(
        df["checking_balance"],
        10,
        labels=False,
        duplicates="drop"
    )

    df["high_dti_flag"] = (
        df["debt_to_income_ratio"] > .43
    ).astype(int)

    df["high_utilization_flag"] = (
        df["utilization_ratio"] > .75
    ).astype(int)

    df["risk_score"] = (
        850 - df["credit_score"]
    )

    df["risk_tier"] = pd.cut(
        df["credit_score"],
        bins=[300,580,670,740,800,850],
        labels=[
            "Very High",
            "High",
            "Medium",
            "Low",
            "Very Low"
        ],
        include_lowest=True
    )

    df["propensity_score"] = np.random.uniform(
        0,
        1,
        len(df)
    )

    df["default_probability"] = np.random.uniform(
        0,
        .6,
        len(df)
    )

    df["retention_probability"] = np.random.uniform(
        .4,
        1,
        len(df)
    )

    df["customer_lifetime_value"] = (
        df["annual_income"] *
        np.random.uniform(.3, 3, len(df))
    )

    df["risk_adjusted_clv"] = (
        df["customer_lifetime_value"] *
        (1 - df["default_probability"])
    )

    return df

# ============================================================
# WATERFALL
# ============================================================

def run_waterfall(df):

    df = df.drop_duplicates(
        subset=["customer_id"]
    )

    df = df[
        df["credit_score"].between(300,850)
    ]

    df["checking_balance"] = (
        df["checking_balance"]
        .clip(
            lower=df["checking_balance"].quantile(.05),
            upper=df["checking_balance"].quantile(.95)
        )
    )

    df = df.head(BANK_FULL_ROWS)

    return df

# ============================================================
# HOUSEHOLD AGGREGATION
# ============================================================

def build_household_dataset(df):

    household = (

        df.groupby("household_id")
          .agg({
              "annual_income":"sum",
              "checking_balance":"sum",
              "credit_score":"mean",
              "txn_count_90d":"sum",
              "customer_lifetime_value":"sum",
              "risk_adjusted_clv":"sum",
              "target":"max"
          })
          .reset_index()

    )

    household = household.head(
        ANALYTICS_ROWS
    )

    return household

# ============================================================
# VALIDATION
# ============================================================

def validate(df):

    results = []

    results.append([
        "credit_score_range",
        df["credit_score"]
          .between(300,850)
          .all()
    ])

    results.append([
        "dti_range",
        df["debt_to_income_ratio"]
          .between(0,1)
          .all()
    ])

    results.append([
        "utilization_range",
        df["utilization_ratio"]
          .between(0,1)
          .all()
    ])

    results.append([
        "unique_customer",
        df["customer_id"]
          .is_unique
    ])

    report = pd.DataFrame(
        results,
        columns=[
            "validation",
            "passed"
        ]
    )

    report.to_csv(
        OUTPUT /
        "validation_report.csv",
        index=False
    )

# ============================================================
# DATA DICTIONARY
# ============================================================

def generate_dictionary():

    rows = []

    for domain, features in FEATURE_GROUPS.items():

        for feature in features:

            rows.append([
                domain,
                feature
            ])

    pd.DataFrame(
        rows,
        columns=[
            "domain",
            "feature"
        ]
    ).to_csv(
        OUTPUT /
        "data_dictionary.csv",
        index=False
    )

# ============================================================
# HASH MANIFEST
# ============================================================

def sha256sum(path):

    h = hashlib.sha256()

    with open(path,"rb") as f:

        while True:

            chunk = f.read(8192)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()

def build_manifest():

    files = [
        "bank_full.csv",
        "final_analytics_ready_dataset.csv",
        "data_dictionary.csv"
    ]

    manifest = []

    for f in files:

        p = OUTPUT / f

        manifest.append([
            f,
            sha256sum(p)
        ])

    pd.DataFrame(
        manifest,
        columns=["file","sha256"]
    ).to_csv(
        OUTPUT /
        "hash_manifest.csv",
        index=False
    )

# ============================================================
# PROJECT01 HANDOFF
# ============================================================

def build_handoff():

    metadata = {

        "project":"00",

        "version":"1.0",

        "consumer_project":"01",

        "customer_records":
            BANK_FULL_ROWS,

        "analytics_records":
            ANALYTICS_ROWS,

        "feature_domains":
            list(FEATURE_GROUPS.keys())

    }

    with open(
        OUTPUT /
        "project01_handoff.json",
        "w"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=2
        )

# ============================================================
# MAIN
# ============================================================

def main():

    df = generate_core_dataset()

    df = engineer_features(df)

    df = run_waterfall(df)

    df.to_csv(
        OUTPUT /
        "bank_full.csv",
        index=False
    )

    household = build_household_dataset(df)

    household.to_csv(
        OUTPUT /
        "final_analytics_ready_dataset.csv",
        index=False
    )

    validate(df)

    generate_dictionary()

    build_manifest()

    build_handoff()

    print("Project 00 Complete.")

if __name__ == "__main__":

    main()
