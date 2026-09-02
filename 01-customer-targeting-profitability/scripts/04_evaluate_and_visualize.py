import os
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve

data_dir = r"C:\Users\User\01-customer-targeting-profitability\data"

print("[INFO] Loading modeled master dataset for evaluation...")
df = pd.read_csv(os.path.join(data_dir, "modeled_master_dataset.csv"))

# ---------------------------------------------------------------------------
# [AWS CLOUD CONTEXT / MIGRATION NOTE]:
# In an enterprise architecture, evaluation metrics and scored master tables 
# are queried via Amazon Athena and published directly to Amazon QuickSight 
# or exported to an S3 reporting bucket for Power BI ingestion.
# ---------------------------------------------------------------------------

print("[INFO] Calculating risk-adjusted CLV and segmentation summaries...")

# Calculate Risk-Adjusted CLV proxy metric
# Formula: (Total Spend * (1 - Default Probability Risk Weight)) - Acquisition Costs
df['risk_adjusted_clv'] = (
    df['total_spend'] * (1.0 - (df['debt_to_income_ratio'] * 0.5))
) - (df['campaign'] * 15.0)

# Aggregate Segment Profiles for Executive Reporting
segment_summary = df.groupby('segment_cluster').agg(
    customer_count=('household_id', 'count'),
    avg_total_spend=('total_spend', 'mean'),
    avg_credit_score=('credit_score', 'mean'),
    avg_risk_adjusted_clv=('risk_adjusted_clv', 'mean'),
    avg_delinquency_rate=('delinquency_flag_90d', 'mean')
).reset_index()

print("\n----------------- SEGMENT PROFITABILITY SUMMARY -----------------")
print(segment_summary.to_string(index=False))

# Export Dashboard-Ready Dataset
dashboard_output_path = os.path.join(data_dir, "dashboard_export_schema.csv")
df.to_csv(dashboard_output_path, index=False)
print(f"\n[SUCCESS] Final dashboard-ready dataset exported to {dashboard_output_path}")
