import os
import numpy as np
import pandas as pd

# Define local project paths
target_dir = r"C:\Users\User\01-customer-targeting-profitability\data"
os.makedirs(target_dir, exist_ok=True)

# ---------------------------------------------------------------------------
# [AWS CLOUD CONTEXT / MIGRATION NOTE]: 
# In an enterprise AWS architecture, raw files would bypass local downloads 
# and be ingested directly into an Amazon S3 bucket path:
# e.g., s3://your-aws-sandbox-bucket/raw/bank-full.csv
# Followed by registering them as external tables in the AWS Glue Data Catalog 
# to allow serverless querying via Amazon Athena.
# ---------------------------------------------------------------------------

# Download primary UCI Bank Marketing dataset directly into the local project
url = "https://raw.githubusercontent.com/selva86/datasets/master/bank-full.csv"
print("[INFO] Downloading primary bank-full.csv dataset...")
df_primary = pd.read_csv(url)

# Assign unique household identifiers
df_primary["household_id"] = [f"HH_{i:05d}" for i in range(len(df_primary))]

# Save primary file locally
primary_path = os.path.join(target_dir, "bank-full.csv")
df_primary.to_csv(primary_path, index=False)

# Generate synchronized secondary behavioral datasets
np.random.seed(42)
n_rows = len(df_primary)

df_transactions = pd.DataFrame({
    "household_id": df_primary["household_id"],
    "transaction_amount": np.random.exponential(scale=150.0, size=n_rows),
    "transaction_type": np.random.choice(["Credit", "Debit"], size=n_rows, p=[0.4, 0.6])
})

df_digital = pd.DataFrame({
    "household_id": df_primary["household_id"],
    "login_frequency_monthly": np.random.poisson(lam=12, size=n_rows),
    "mobile_app_sessions": np.random.poisson(lam=5, size=n_rows),
    "customer_service_calls_30d": np.random.poisson(lam=1, size=n_rows)
})

df_credit = pd.DataFrame({
    "household_id": df_primary["household_id"],
    "credit_score": np.random.randint(580, 820, size=n_rows),
    "debt_to_income_ratio": np.random.uniform(0.1, 0.6, size=n_rows),
    "delinquency_flag_90d": np.random.choice([0, 1], size=n_rows, p=[0.92, 0.08])
})

# Save secondary files locally
df_transactions.to_csv(os.path.join(target_dir, "household_transactions.csv"), index=False)
df_digital.to_csv(os.path.join(target_dir, "household_digital_activity.csv"), index=False)
df_credit.to_csv(os.path.join(target_dir, "household_credit_profile.csv"), index=False)

# ---------------------------------------------------------------------------
# [AWS CLOUD CONTEXT / MIGRATION NOTE]:
# Locally, pandas joins these CSV files together in memory. In the cloud model, 
# this equivalent relational aggregation would be executed via a SQL SELECT 
# statement across partitioned tables inside the Athena query editor.
# ---------------------------------------------------------------------------

print("[SUCCESS] All self-contained data files successfully generated in 01-customer-targeting-profitability\\data\\.")
