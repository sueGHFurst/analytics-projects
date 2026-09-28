WITH transaction_summary AS (
    SELECT 
        household_id,
        COUNT(transaction_id) AS transaction_count,
        SUM(transaction_amount) AS total_transaction_volume,
        MAX(transaction_timestamp) AS last_transaction_timestamp
    FROM enterprise_customer_db.customer_transactions_data
    GROUP BY household_id
),
digital_activity_summary AS (
    SELECT 
        household_id,
        COUNT(session_id) AS login_frequency,
        AVG(session_duration_minutes) AS avg_session_duration
    FROM enterprise_customer_db.household_digital_activity
    GROUP BY household_id
)
SELECT 
    COALESCE(t.household_id, d.household_id) AS household_id,
    COALESCE(t.transaction_count, 0) AS transaction_count,
    COALESCE(t.total_transaction_volume, 0.0) AS total_transaction_volume,
    t.last_transaction_timestamp,
    COALESCE(d.login_frequency, 0) AS login_frequency,
    COALESCE(d.avg_session_duration, 0.0) AS avg_session_duration
FROM transaction_summary t
FULL OUTER JOIN digital_activity_summary d 
    ON t.household_id = d.household_id;