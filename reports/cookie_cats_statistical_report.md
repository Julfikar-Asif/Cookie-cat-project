# Cookie Cats Statistical and Quality Report

Generated from `data/cookie_cats.csv` by `scripts/analyze_cookie_cats.py`.

## Data quality

- Status: **PASS**
- Source rows: 90,189
- Clean rows: 90,188
- Removed outlier rows: 1
- Duplicate user IDs: 0
- Missing values: 0
- Invalid versions: 0
- Invalid retention values: 0
- Negative rounds: 0

## Statistical tests

The tests compare `gate_30 - gate_40` using a two-sided two-proportion z-test.

| Metric | Difference | 95% CI | p-value | Result |
|---|---:|---:|---:|---|
| D1 retention | 0.59 pp | [-0.06, 1.24] pp | 0.073921 | not statistically significant |
| D7 retention | 0.82 pp | [0.31, 1.33] pp | 0.001592 | statistically significant |

## Recommendation

Keep gate_30 as the recommended default. It has higher observed D7 retention, and the overall difference is statistically significant. Validate this decision with a future experiment that also captures revenue and long-term retention.

This recommendation is limited because the dataset has no revenue, acquisition, device, country, or long-term retention fields.
