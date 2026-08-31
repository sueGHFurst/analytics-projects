# Media Mix Modeling (MMM) & Omni-Channel Budget Optimization

## Overview
Statistical modeling pipeline to evaluate advertising channels, estimate adstock decay, and reallocate spend to lower acquisition costs.

## Tooling & Architecture
* **Core Language:** Python 3.11
* **Data Pipeline:** SEMMA framework with median imputation (`SimpleImputer`)

## Analytical Environment & Frameworks
* **Feature Engineering:** Geometric Adstock Decay & Hill Saturation Curves
* **Statistical Modeling:** Ridge Regression ($L_2$ Regularization) with `StandardScaler`
* **Optimization Engine:** `scipy.optimize.minimize` for ROI budget allocation
