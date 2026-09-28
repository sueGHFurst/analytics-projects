"""
01_household_analytics_engine.py
Exploratory Data Analysis & Business Intelligence Engine (Project 01 Consumer)
=====================================================================================
Directory Structure: C:\\Users\\User\\00-cloud-framework
- Data Input: C:\\Users\\User\\00-cloud-framework\\data\\bank-full.csv
- Output Folder: C:\\Users\\User\\00-cloud-framework\\output\\

Execution Mode: Downstream Consumer
- Loads pre-hardened enterprise datasets (`bank-full.csv`).
- Executes Household-Level Decile Segmentations, Churn Variance Analyses, and Risk-Tier Scoring.
- Generates publication-quality empirical validation charts in `output/`.
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================================================
# 1. Environment & Directory Configuration
# =====================================================================
BASE_DIR = r"C:\Users\User\00-cloud-framework"
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "analytics_engine_execution.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# =====================================================================
# 2. Household Analytics & Business Case Engine
# =====================================================================
class HouseholdAnalyticsEngine:
    """Encapsulates household decile segmentation, risk tiering, and variance analysis."""
    def __init__(self, df_base):
        self.df_base = df_base

    def compute_household_deciles(self):
        """Compute balance and credit score deciles at the household level using NTILE logic."""
        self.df_base['balance_decile'] = pd.qcut(self.df_base['balance'], q=10, labels=False, duplicates='drop') + 1
        self.df_base['credit_score_decile'] = pd.qcut(self.df_base['credit_score'], q=10, labels=False, duplicates='drop') + 1
        
        balance_summary = self.df_base.groupby('balance_decile')['balance'].agg(['count', 'mean', 'sum']).reset_index()
        logger.info("Computed Household Balance Deciles successfully.")
        return balance_summary

    def segment_risk_tiers(self):
        """Segment household risk based on credit score and DTI thresholds."""
        conditions = [
            (self.df_base['credit_score'] >= 720) & (self.df_base['debt_to_income_ratio'] < 0.35),
            (self.df_base['credit_score'] >= 680) & (self.df_base['debt_to_income_ratio'] < 0.50),
            (self.df_base['credit_score'] >= 620),
            (self.df_base['credit_score'] < 620)
        ]
        tiers = ['Prime', 'Medium-Low Risk', 'Medium-High Risk', 'High Risk']
        self.df_base['risk_tier'] = np.select(conditions, tiers, default='High Risk')
        return self.df_base['risk_tier'].value_counts()

    def analyze_login_variance(self):
        """Analyze login frequency variance across active vs churn risk cohorts."""
        self.df_base['dormancy_risk'] = np.where(self.df_base['login_frequency'] <= 2, 1, 0)
        cohort_summary = self.df_base.groupby('dormancy_risk')['login_frequency'].agg(
            ['count', 'mean', 'median', 'std', 'min', 'max']
        ).reset_index()
        return cohort_summary

    def generate_visualizations(self):
        """Generate publication-quality empirical validation charts in output/."""
        
        # 1. Acquisition Pareto Skew Histogram
        plt.figure(figsize=(10, 6))
        sns.histplot(self.df_base['balance'].dropna(), bins=50, kde=True, color="#1f4e79")
        plt.axvline(self.df_base['balance'].median(), color='red', linestyle='--', label=f"Median: ${self.df_base['balance'].median():.2f}")
        plt.axvline(self.df_base['balance'].mean(), color='green', linestyle=':', label=f"Mean: ${self.df_base['balance'].mean():.2f}")
        plt.title("Account Balance Distribution - Acquisition Pareto Skew", fontsize=14, fontweight='bold')
        plt.xlabel("Account Balance ($)")
        plt.ylabel("Household Count")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "acquisition_balance_skew.png"), dpi=300)
        plt.close()

        # 2. Churn Login Variance Boxplot
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='dormancy_risk', y='login_frequency', data=self.df_base, palette=['#2ca02c', '#d62728'])
        plt.title("Monthly Login Frequency Variance Across Dormancy Risk Cohorts", fontsize=14, fontweight='bold')
        plt.xlabel("Customer Dormancy Risk Status (0 = Active, 1 = High Churn Risk)")
        plt.ylabel("Monthly Login Frequency")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "churn_login_variance.png"), dpi=300)
        plt.close()

        # 3. Risk-Adjusted CLV Scatterplot
        plot_df = self.df_base.sample(min(5000, len(self.df_base)), random_state=42).copy()
        custom_palette = {
            'Prime': '#2ca02c',
            'Medium-Low Risk': '#9467bd',
            'Medium-High Risk': '#1f77b4',
            'High Risk': '#d62728'
        }

        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='credit_score', y='debt_to_income_ratio', hue='risk_tier', data=plot_df, alpha=0.7, palette=custom_palette)
        plt.title("Credit Score vs. Debt-to-Income Risk Segmentation", fontsize=14, fontweight='bold')
        plt.xlabel("Credit Score", fontweight='bold')
        plt.ylabel("Debt-to-Income (DTI) Ratio", fontweight='bold')
        plt.legend(title="Risk Tier", loc='upper right')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "risk_adjusted_clv_segments.png"), dpi=300)
        plt.close()
        
        # Export Descriptive Statistics Summary
        numeric_cols = self.df_base.select_dtypes(include=[np.number]).columns
        stats = [
            {
                'feature': col, 'count': len(self.df_base), 'mean': self.df_base[col].mean(),
                'median': self.df_base[col].median(), 'std': self.df_base[col].std(),
                'min': self.df_base[col].min(), 'max': self.df_base[col].max()
            } for col in numeric_cols
        ]
        pd.DataFrame(stats).to_csv(os.path.join(OUTPUT_DIR, 'descriptive_statistics.csv'), index=False)
        logger.info("Generated all empirical validation charts and statistics in %s.", OUTPUT_DIR)


# =====================================================================
# 3. Main Execution Controller
# =====================================================================
def main():
    logger.info("Starting Downstream Analytics Engine (Project 01)...")
    
    input_path = os.path.join(DATA_DIR, "bank-full.csv")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Hardened dataset not found at '{input_path}'. Run Project 00 first.")
    
    df_base = pd.read_csv(input_path)
    logger.info("Successfully loaded hardened baseline dataset: %s (%d records).", input_path, len(df_base))
    
    analytics = HouseholdAnalyticsEngine(df_base)
    analytics.compute_household_deciles()
    analytics.segment_risk_tiers()
    analytics.analyze_login_variance()
    analytics.generate_visualizations()
    
    logger.info("Project 01 analytics execution completed successfully from end to end.")

if __name__ == "__main__":
    main()