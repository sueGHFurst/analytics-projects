# Cloud Analytics Framework Architecture

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Data Domains](#data-domains)
- [Pipeline](#pipeline)
- [Core90 Schema](#core90-schema)
- [Governance](#governance)
- [Outputs](#outputs)
- [Project 01 Integration](#project-01-integration)
- [Outcomes](#outcomes)

---

# Overview

This document describes the analytics architecture used to create governed customer intelligence datasets for segmentation, profitability analysis, credit risk analytics, and predictive modeling.

Project 00 serves as the foundational data layer for Project 01: Customer Targeting & Profitability Engine.

> This project demonstrates a cloud-compatible analytics framework that can be deployed to AWS, Azure, Snowflake, Databricks, or similar analytical environments while remaining fully reproducible in a local portfolio setting.

---

# Architecture

## High-Level Flow

```text
+------------------+
| Bank Marketing   |
+------------------+
          |
+------------------+
| Credit Bureau    |
+------------------+
          |
+------------------+
| Digital Activity |
+------------------+
          |
+------------------+
| Transactions     |
+------------------+
          |
          v
+----------------------+
| Data Quality & QA    |
+----------------------+
          |
          v
+----------------------+
| Customer Master      |
+----------------------+
          |
          v
+----------------------+
| Household Analytics  |
+----------------------+
          |
          v
+----------------------+
| Feature Engineering  |
+----------------------+
          |
          v
+----------------------+
| bank_full.csv        |
| 299,332 Customers    |
| Core90 Schema        |
+----------------------+
          |
          v
+----------------------+
| Analytics Dataset    |
| 226,534 Households   |
+----------------------+
        |
        v
+----------------------+
| Project 01           |
| Targeting & Profit   |
+----------------------+
--------
#Data Domains
##Bank Marketing
###Purpose

*Demographics
*Campaign activity
*Contact history
*Response outcomes

##Credit Bureau
###Purpose

*Creditworthiness
*Delinquency indicators
*Utilization metrics
*Risk assessment

##Digital Activity
###Purpose

*Login activity
*Web engagement
*Channel interactions
*Customer behavior

##Transaction Data
###Purpose

*Spending activity
*Deposits
*Account balances
*Profitability analysis
-----
#Pipeline
##1. Data Integration
Combine customer, credit, behavioral, and transaction domains.

###Activities
*Source consolidation
*Key alignment
*Relationship validation
*Customer matching
---
##2. Data Quality
Validation controls include:

*Duplicate detection
*Missing value treatment
*Range validation
*Business rule validation
###Example Rules

----------------|-----------------------|
*Variable*      |    *Validation Rule*  |
Credit Score    |	         300–850    |       
DTI Ratio	      |          0.00–1.00    |
Utilization     |	       0.00–1.00    |
Balance	      |       Non-negative    |
----------------|-----------------------|
----
##3. Feature Engineering

Examples include:

*Credit Score Deciles
*Balance Deciles
*Engagement Scores
*Propensity Scores
*Retention Indicators
*Risk Scores
*Risk-Adjusted CLV
----
##4. Feature Store

## Output

*bank_full.csv*

|---------|------------------|
|*Metric* |         *Value*  |
------------------------------
|Records  |         299,332  |
|Grain	|        Customer  |
|Schema	|          Core90  |
|Purpose	|Customer Analytics|
------------------------------
##5. Analytics Dataset

##Output

*final_analytics_ready_dataset.csv*

|--------- |----------------------------------|
| *Metric* |	                *Value*   |
|---------------------------------------------|
| Records  |	                226,534   |
| Grain    |	              Household   |
| Purpose  |          Modeling & Segmentation |
-----------------------------------------------

----
#Core90 Schema

##Feature Domains
* Customer Demographics
* Account & Balance Information
* Credit & Lending Attributes
* Behavioral & Transaction Activity
* Product Holdings
* Risk & Compliance Indicators

##Engineered Features
* Credit Score Deciles
* Balance Deciles
* Engagement Scores
* Risk Scores
* Propensity Scores
* Retention Indicators
* Risk-Adjusted CLV
----
#Governance

##Validation Controls
* Schema validation
* Row-count validation
* Feature-count validation
* Duplicate detection
* Range validation
* Null-threshold monitoring
* Business-rule verification

##Reproducibility Controls
* Fixed random seed
* Deterministic processing
* Versioned schema definitions
* Hash verification
* Run metadata capture

###Artifacts
* validation_report.csv
* hash_manifest.csv
* run_metadata.json
---
#Outputs

##Customer Feature Store

**bank_full.csv**

*299,332 customer records
*Core90 enterprise schema
*Customer-level analytical foundation

##Analytics Dataset

*final_analytics_ready_dataset.csv*

*226,534 active customer households
*Modeling-ready analytical dataset

##Supporting Artifacts

*data_dictionary.csv
*validation_report.csv
*hash_manifest.csv
*run_metadata.json
*project01_handoff.json
*Project 01 Integration

---

#Project 00 provides:

*Customer demographics
*Campaign history
*Credit risk indicators
*Digital engagement features
*Transaction metrics
*Household analytics
*Risk-adjusted CLV

These assets support:

*Customer Segmentation
*Response Propensity Modeling
*Profitability Modeling
*Credit Risk-Aware Marketing
*Targeting Optimization

--

#Outcomes

##Technical Skills Demonstrated Applications
*Customer Analytics
*Credit Risk Analytics
*Profitability Analysis
*Marketing Analytics
*Predictive Modeling

##Key Deliverables
*299,332 Validated Customer Records
*226,534 Active Customer Households
*Core90 Enterprise Feature Schema
*Reproducible Analytics Pipeline
*Validation & Audit Framework
*Project 01 Handoff Package
