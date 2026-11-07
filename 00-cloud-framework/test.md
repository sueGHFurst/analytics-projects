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

## Overview

This document describes the analytics architecture used to create governed customer intelligence datasets for segmentation, profitability analysis, credit risk analytics, and predictive modeling.

Project 00 serves as the foundational data layer for Project 01: Customer Targeting & Profitability Engine.

> This project demonstrates a cloud-compatible analytics framework that can be deployed to AWS, Azure, Snowflake, Databricks, or similar analytical environments while remaining fully reproducible in a local portfolio setting.

---

## Architecture

### High-Level Flow

```text
Bank Marketing Data
Credit Bureau Data
Digital Activity Data
Transaction Data
        │
        ▼
Data Quality & Validation
        │
        ▼
Customer Master Dataset
        │
        ▼
Household Analytics Engine
        │
        ▼
Feature Engineering
        │
        ▼
Customer Feature Store
(bank_full.csv)
299,332 Records
Core90 Enterprise Feature Schema
        │
        ▼
Analytics Ready Dataset
(final_analytics_ready_dataset.csv)
226,534 Active Customer Households
        │
        ▼
Project 01
Customer Targeting & Profitability Engine
```
