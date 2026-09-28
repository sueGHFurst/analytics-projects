# Analytics Feature Store Data Dictionary

## Overview

This document describes key fields contained within the analytics feature store.

---

## Core Identifiers

### household_id

Type:

```text
String
```

Description:

Unique household-level identifier used to define the analytical grain.

Source:

Customer Master Data

---

## Financial Variables

### balance

Type:

```text
Numeric
```

Description:

Current customer account balance.

Transformations:

- Logical bounds validation
- Winsorization

---

### balance_decile

Type:

```text
Integer
```

Description:

Balance ranking grouped into deciles.

Purpose:

Customer asset segmentation.

---

### debt_to_income_ratio

Type:

```text
Numeric
```

Description:

Customer debt-to-income ratio.

Transformations:

- Range validation
- Median substitution
- Winsorization

---

## Credit Variables

### credit_score

Type:

```text
Numeric
```

Description:

Customer credit score.

Range:

```text
300–850
```

Transformations:

- Boundary validation
- Winsorization

---

### credit_score_decile

Type:

```text
Integer
```

Description:

Decile representation of customer credit score.

Purpose:

Risk segmentation.

---

## Digital Engagement Variables

### login_frequency

Type:

```text
Numeric
```

Description:

Number of system logins during observation period.

Transformations:

- Missing value treatment
- Zero imputation

---

### mobile_app_active

Type:

```text
Binary
```

Description:

Indicates active mobile application usage.

Values:

```text
0 = No
1 = Yes
```

---

## Campaign Variables

### campaign_clicks

Type:

```text
Numeric
```

Description:

Campaign engagement click count.

Transformations:

- Missing value treatment
- Zero imputation

---

### poutcome

Type:

```text
Categorical
```

Description:

Outcome of prior campaign activity.

Example Values:

```text
success
failure
unknown
```

---

## Target Variable

### target

Type:

```text
Binary
```

Description:

Model target variable.

Values:

```text
0 = Non-response
1 = Response
```

Quality Assessment:

- 0% missing values

Purpose:

Propensity modeling and campaign analytics.

---

## Engineered Features

Examples include:

- Credit Score Deciles
- Balance Deciles
- Digital Engagement Indicators
- Customer Response Metrics
- Financial Risk Signals
- Asset Tier Indicators
- Behavioral Engagement Metrics

Purpose:

Support customer segmentation, propensity modeling, and campaign optimization.