WITH base_demographics AS (
    SELECT 
        household_id, 
        age, 
        job, 
        marital, 
        education, 
        housing, 
        loan
    FROM enterprise_customer_db.customer_demographic_info
),
consolidated_credit AS (
    SELECT 
        COALESCE(hp.household_id, cb.household_id) AS household_id,
        COALESCE(hp.credit_score, cb.credit_score) AS credit_score,
        COALESCE(hp.debt_to_income_ratio, cb.debt_to_income_ratio) AS debt_to_income_ratio
    FROM enterprise_customer_db.household_credit_profile hp
    FULL OUTER JOIN enterprise_customer_db.credit_bureau_data cb 
        ON hp.household_id = cb.household_id
),
macro_economic_factors AS (
    SELECT 
        household_id,
        emp_var_rate,
        cons_price_idx,
        cons_conf_idx,
        euribor3m,
        nr_employed
    FROM enterprise_customer_db.macro_economic_indicators
)
SELECT 
    m.household_id,
    d.age,
    d.job,
    d.marital,
    d.education,
    d.housing,
    d.loan,
    m.balance,
    m.campaign,
    m.pdays,
    m.previous,
    m.target,
    cr.credit_score,
    cr.debt_to_income_ratio,
    me.emp_var_rate,
    me.cons_price_idx,
    me.cons_conf_idx,
    me.euribor3m,
    me.nr_employed
FROM enterprise_customer_db.uci_bank_marketing_features m
LEFT JOIN base_demographics d 
    ON m.household_id = d.household_id
LEFT JOIN consolidated_credit cr 
    ON m.household_id = cr.household_id
LEFT JOIN macro_economic_factors me 
    ON m.household_id = me.household_id;