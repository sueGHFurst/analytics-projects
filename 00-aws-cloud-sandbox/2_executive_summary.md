### Python-Based SQL Analytics

- PyAthena
- Amazon Athena SQL
- Common Table Expressions (CTEs)
- Window Functions (`ROW_NUMBER`) for data-quality validation and record deduplication

```sql
ROW_NUMBER() OVER (
    PARTITION BY household_id
    ORDER BY last_update_timestamp DESC
) AS row_num
```

- Multi-Source Data Integration
- Athena External Table Management
- Data Quality Auditing
- Feature Engineering & Analytics Dataset Creation
