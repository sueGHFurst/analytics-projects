import os
import pandas as pd
import numpy as np

data_dir = r"C:\Users\User\01-customer-targeting-profitability\data"

print("[INFO] Loading raw data files for preprocessing...")
df_primary = pd.read_csv(os.path.join(data_dir, "bank-full.csv"))
df_transactions = pd.read_csv(os.path.join(data_dir, "household_transactions.csv"))
df_digital = pd.read_csv(os.path.join(data_dir, "household_digital_activity.csv"))
df_credit = pd.read_csv(os.path.join(data_dir, "household_credit_profile.csv"))

# Aggregate behavioral transaction metrics per household
tx_agg = df_transactions.groupby("household_id").agg(
    total_spend=("transaction_amount", "sum"),
    avg_transaction_amount=("transaction_amount", "mean"),
    transaction_count=("transaction_amount", "count")
).reset_index()

# Relational Merging
df_master = df_primary.merge(tx_agg, on="household_id", how="left")
df_master = df_master.merge(df_digital, on="household_id", how="left")
df_master = df_master.merge(df_credit, on="household_id", how="left")

# ---------------------------------------------------------------------------
# [AWS CLOUD CONTEXT / MIGRATION NOTE]:
# In enterprise cloud architectures, exploratory profiling and anomaly detection 
# are typically executed via automated data quality monitors (e.g., AWS Glue 
# Data Quality or Amazon Deequ) rather than interactive console logs.
# ---------------------------------------------------------------------------

print("\n----------------- DATA STRUCTURE INSPECTION -----------------")
print(df_master.info())

print("\n----------------- STATISTICAL SUMMARY -----------------")
print(df_master.describe(include='all'))

print("\n----------------- ANOMALY & EXTREME VALUE CHECK -----------------")
# Identify extreme outliers using the 3.0 * IQR rule for continuous variables
numeric_check_cols = ['balance', 'total_spend', 'credit_score', 'debt_to_income_ratio', 'age']
for col in numeric_check_cols:
    if col in df_master.columns:
        Q1 = df_master[col].quantile(0.25)
        Q3 = df_master[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 3.0 * IQR
        upper_bound = Q3 + 3.0 * IQR
        
        extreme_mask = (df_master[col] < lower_bound) | (df_master[col] > upper_bound)
        extreme_count = extreme_mask.sum()
        print(f"[OUTLIER SCAN] Column '{col}': Found {extreme_count} extreme rows outside bounds [{lower_bound:.2f}, {upper_bound:.2f}]")
        
        if 0 < extreme_count <= 5:
            print(df_master.loc[extreme_mask, ['household_id', col]])

print("\n[INFO] Applying industry-standard missing value imputation...")

# Categorical variables -> Impute with "Missing"
categorical_cols = df_master.select_dtypes(include=['object', 'category']).columns.tolist()
for col in categorical_cols:
    if col != 'household_id':
        df_master[col] = df_master[col].fillna('Missing')

# Count, dummy, and binary indicator variables -> Impute with 0
count_dummy_cols = [
    'transaction_count', 'login_frequency_monthly', 'mobile_app_sessions', 
    'customer_service_calls_30d', 'delinquency_flag_90d', 'previous'
]
for col in count_dummy_cols:
    if col in df_master.columns:
        df_master[col] = df_master[col].fillna(0)

# Continuous numeric variables -> Impute with median
continuous_cols = [
    'age', 'balance', 'day', 'duration', 'campaign', 'pdays', 
    'total_spend', 'avg_transaction_amount', 'debt_to_income_ratio', 'credit_score'
]
for col in continuous_cols:
    if col in df_master.columns:
        median_val = df_master[col].median()
        df_master[col] = df_master[col].fillna(median_val)

# Automated validation assertions
assert len(df_master) == len(df_primary), "Row count mismatch after relational join!"
assert df_master["household_id"].isnull().sum() == 0, "Null household IDs detected!"
assert df_master.isnull().sum().sum() == 0, "Unresolved missing values remain in master dataset!"

output_path = os.path.join(data_dir, "processed_master_dataset.csv")
df_master.to_csv(output_path, index=False)
print(f"\n[SUCCESS] Processed master dataset saved to {output_path}")
