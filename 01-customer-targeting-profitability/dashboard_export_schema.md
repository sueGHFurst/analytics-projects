| Field Name | Data Type | Description / Calculation |
| :--- | :--- | :--- |
| `household_id` | String | Unique relational key linking households to banking transactions. |
| `segment_cluster` | Integer | K-Means clustering assignment (0–3) based on RFM behavioral patterns. |
| `risk_adjusted_clv` | Float | $(\text{Total Spend} \times (1 - \text{DTI} \times 0.5)) - (\text{Campaign Count} \times 15)$ |
| `delinquency_flag_90d` | Integer | Binary indicator (0/1) denoting 90-day past-due credit status. |
| `login_frequency_monthly` | Integer | Monthly digital app engagement count. |
