# Digital Experimentation & Causal Uplift Modeling

## Overview
Framework for assessing campaign incrementality, running in-database hypothesis tests, and identifying persuadable customer segments.

## Tooling & Architecture
* **Database Testing:** SQL-driven $z$-score calculations and Sample Ratio Mismatch (SRM) checks
* **Core Language:** Python 3.11

## Analytical Environment & Frameworks
* **Causal Inference:** T-Learner Uplift Modeling with `LightGBM`
* **Evaluation Metrics:** Qini Curve Analysis ($Q$), Qini Score, and Uplift Decile Charts
