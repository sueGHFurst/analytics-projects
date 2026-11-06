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
| Project
