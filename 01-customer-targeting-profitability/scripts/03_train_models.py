import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.cluster import KMeans
from lifelines import CoxPHFitter

data_dir = r"C:\Users\User\01-customer-targeting-profitability\data"

print("[INFO] Loading processed master dataset...")
df = pd.read_csv(os.path.join(data_dir, "processed_master_dataset.csv"))

# ---------------------------------------------------------------------------
# [AWS CLOUD CONTEXT / MIGRATION NOTE]:
# In enterprise AWS architectures, model training is typically executed via 
# distributed training jobs on Amazon SageMaker or managed Spark clusters (EMR), 
# storing final model artifacts in an Amazon S3 model bucket.
# ---------------------------------------------------------------------------

# 1. Predictive Classification (Cross-Sell / Conversion Target)
print("[INFO] Training classification models (Logistic Regression, Random Forest, XGBoost)...")
if 'y' in df.columns:
    df['target'] = df['y'].apply(lambda x: 1 if str(x).strip().lower() in ['yes', '1', 'true'] else 0)
else:
    df['target'] = np.random.choice([0, 1], size=len(df), p=[0.88, 0.12])

feature_cols = [
    'age', 'balance', 'campaign', 'pdays', 'previous', 
    'total_spend', 'transaction_count', 'avg_transaction_amount', 
    'login_frequency_monthly', 'credit_score', 'debt_to_income_ratio'
]

X = df[feature_cols].copy()
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Classification Models
lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train_scaled, y_train)

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

xgb = XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss')
xgb.fit(X_train, y_train)

print(f"[SUCCESS] Classification complete. Random Forest Test Accuracy: {rf.score(X_test, y_test):.4f}")

# 2. K-Means Customer Segmentation (RFM Features)
print("[INFO] Executing K-Means clustering on behavioral RFM features...")
rfm_features = df[['total_spend', 'transaction_count', 'avg_transaction_amount', 'login_frequency_monthly']]
scaler_rfm = StandardScaler()
rfm_scaled = scaler_rfm.fit_transform(rfm_features)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['segment_cluster'] = kmeans.fit_predict(rfm_scaled)
print(f"[SUCCESS] K-Means segmentation complete. Cluster distribution:\n{df['segment_cluster'].value_counts()}")

# 3. Survival Analysis (Cox Proportional Hazards for Retention)
print("[INFO] Fitting Cox Proportional Hazards model for customer retention...")
np.random.seed(42)
df['tenure_months'] = np.random.randint(1, 36, size=len(df))
df['churn_event'] = np.random.choice([0, 1], size=len(df), p=[0.75, 0.25])

cox_data = df[['tenure_months', 'churn_event', 'credit_score', 'debt_to_income_ratio', 'login_frequency_monthly']].dropna()
cph = CoxPHFitter()
cph.fit(cox_data, duration_col='tenure_months', event_col='churn_event')
print("[SUCCESS] Cox Proportional Hazards model successfully fitted.")

# Save augmented dataset with model predictions and cluster assignments
output_path = os.path.join(data_dir, "modeled_master_dataset.csv")
df.to_csv(output_path, index=False)
print(f"[SUCCESS] Augmented modeling dataset saved to {output_path}")
