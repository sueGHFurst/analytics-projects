# ETL Workflow Specification: AWS Cloud Analytics Sandbox

## Core Logic & Execution
* **Pipeline Architecture:** Implements a clean, modular structure managing environment variables, `boto3` cloud storage clients, and `PyAthena` connection handlers.
* **Dual-Environment Processing:** Executes multi-tier CTEs and window functions in cloud-based Amazon Athena, with local fallback execution handled via pandas (`pd.qcut`, group-by aggregations, and dense ranking).

## Quality Control Documentation
The pipeline includes numbered inline comments detailing five core data validation and fault-tolerance safeguards:
* **S3 Exception Handling:** Wrapped inside `try...except` blocks to catch and log networking, permission, or path errors during raw file staging[cite: 3].
* **Idempotent DDL Execution:** Employs `CREATE EXTERNAL TABLE IF NOT EXISTS` statements that can be executed repeatedly against a data catalog without raising errors or creating duplicate schema definitions, ensuring environment reproducibility[cite: 3].
* **Header Offset Sanitization:** Enforces `TBLPROPERTIES ('skip.header.line.count'='1')` to prevent CSV header strings from corrupting numeric aggregations in Athena[cite: 3].
* **Data Nullity & Consistency Filters:** Excludes missing values (`WHERE balance IS NOT NULL`) to ensure downstream statistical computations are performed strictly on valid data points[cite: 3].
* **Local Path Assertions:** Validates local file existence via `Path.exists()` before executing fallback processing loops, avoiding runtime `FileNotFoundError` exceptions[cite: 3].

## Workflow Transition Notes
* **Lifecycle Progression:** Features an appended block explicitly documenting the project transition from foundational cloud infrastructure and serverless staging (`00-aws-cloud-sandbox`) to downstream machine learning and experimentation modules (e.g., `01-customer-targeting-profitability`)[cite: 3].
