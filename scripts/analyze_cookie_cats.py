"""Reproducible Cookie Cats cleaning, validation, and A/B analysis."""

import csv
import json
import math
import random
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "cookie_cats.csv"
DASHBOARD = ROOT / "dashboard"
REPORTS = ROOT / "reports"

SEGMENTS = (
    ("0 rounds", 1),
    ("1-10", 2),
    ("11-50", 3),
    ("51-200", 4),
    ("200+", 5),
)


def segment_for(rounds: int) -> tuple[str, int]:
    if rounds == 0:
        return "0 rounds", 1
    if rounds <= 10:
        return "1-10", 2
    if rounds <= 50:
        return "11-50", 3
    if rounds <= 200:
        return "51-200", 4
    return "200+", 5


def proportion_interval(successes: int, total: int) -> tuple[float, float]:
    estimate = successes / total
    margin = 1.96 * math.sqrt(estimate * (1 - estimate) / total)
    return estimate - margin, estimate + margin


def compare_proportions(
    first_successes: int,
    first_total: int,
    second_successes: int,
    second_total: int,
) -> dict[str, float | int | str]:
    first = first_successes / first_total
    second = second_successes / second_total
    difference = first - second
    pooled = (first_successes + second_successes) / (first_total + second_total)
    standard_error = math.sqrt(
        pooled * (1 - pooled) * (1 / first_total + 1 / second_total)
    )
    z_score = difference / standard_error if standard_error else 0.0
    p_value = math.erfc(abs(z_score) / math.sqrt(2))
    low, high = proportion_interval(first_successes, first_total)
    second_low, second_high = proportion_interval(second_successes, second_total)
    difference_margin = 1.96 * math.sqrt(
        first * (1 - first) / first_total
        + second * (1 - second) / second_total
    )
    return {
        "first_rate": first,
        "second_rate": second,
        "difference": difference,
        "difference_pp": difference * 100,
        "ci_low": difference - difference_margin,
        "ci_high": difference + difference_margin,
        "first_ci_low": low,
        "first_ci_high": high,
        "second_ci_low": second_low,
        "second_ci_high": second_high,
        "z_score": z_score,
        "p_value": p_value,
        "result": "statistically significant" if p_value < 0.05 else "not statistically significant",
    }


def bootstrap_median(values: list[int], seed: int = 42, iterations: int = 2000) -> tuple[float, float]:
    rng = random.Random(seed)
    medians = [
        statistics.median(rng.choices(values, k=len(values)))
        for _ in range(iterations)
    ]
    medians.sort()
    return medians[int(iterations * 0.025)], medians[int(iterations * 0.975)]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    raw_rows: list[dict[str, str]] = []
    with SOURCE.open(newline="", encoding="utf-8") as file:
        raw_rows = list(csv.DictReader(file))

    required = {"userid", "version", "sum_gamerounds", "retention_1", "retention_7"}
    missing_columns = sorted(required - set(raw_rows[0]))
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    duplicate_ids = len(raw_rows) - len({row["userid"] for row in raw_rows})
    missing_values = sum(
        1
        for row in raw_rows
        for column in required
        if row[column].strip() == ""
    )
    invalid_versions = sum(row["version"] not in {"gate_30", "gate_40"} for row in raw_rows)
    invalid_booleans = sum(
        row[column].lower() not in {"true", "false"}
        for row in raw_rows
        for column in ("retention_1", "retention_7")
    )
    negative_rounds = sum(int(row["sum_gamerounds"]) < 0 for row in raw_rows)
    outlier_rows = sum(int(row["sum_gamerounds"]) >= 40000 for row in raw_rows)

    rows: list[dict[str, object]] = []
    for row in raw_rows:
        rounds = int(row["sum_gamerounds"])
        if rounds >= 40000:
            continue
        segment, segment_order = segment_for(rounds)
        rows.append(
            {
                "userid": int(row["userid"]),
                "version": row["version"],
                "sum_gamerounds": rounds,
                "retention_1": row["retention_1"].lower() == "true",
                "retention_7": row["retention_7"].lower() == "true",
                "Segment": segment,
                "SegmentOrder": segment_order,
            }
        )

    write_csv(DASHBOARD / "cookie_cats_powerbi.csv", rows)
    write_csv(
        DASHBOARD / "segment_summary_powerbi.csv",
        [
            {
                "Segment": segment,
                "SegmentOrder": order,
                "Players": sum(row["Segment"] == segment for row in rows),
            }
            for segment, order in SEGMENTS
        ],
    )
    write_csv(
        DASHBOARD / "version_summary_powerbi.csv",
        [
            {
                "version": version,
                "Players": sum(row["version"] == version for row in rows),
            }
            for version in ("gate_30", "gate_40")
        ],
    )

    quality = {
        "source_rows": len(raw_rows),
        "clean_rows": len(rows),
        "removed_outlier_rows": outlier_rows,
        "duplicate_userids": duplicate_ids,
        "missing_values": missing_values,
        "invalid_versions": invalid_versions,
        "invalid_retention_values": invalid_booleans,
        "negative_rounds": negative_rounds,
        "max_rounds_after_filter": max(row["sum_gamerounds"] for row in rows),
        "quality_status": "PASS"
        if not any(
            (duplicate_ids, missing_values, invalid_versions, invalid_booleans, negative_rounds)
        )
        else "FAIL",
    }
    (REPORTS / "data_quality_report.json").write_text(
        json.dumps(quality, indent=2) + "\n", encoding="utf-8"
    )

    tests: list[dict[str, object]] = []
    for metric, column in (("D1 retention", "retention_1"), ("D7 retention", "retention_7")):
        first = [row for row in rows if row["version"] == "gate_30"]
        second = [row for row in rows if row["version"] == "gate_40"]
        result = compare_proportions(
            sum(row[column] for row in first),
            len(first),
            sum(row[column] for row in second),
            len(second),
        )
        tests.append({"metric": metric, **result})
    write_csv(REPORTS / "statistical_tests.csv", tests)

    version_rows = []
    for version in ("gate_30", "gate_40"):
        subset = [row for row in rows if row["version"] == version]
        low, high = bootstrap_median([row["sum_gamerounds"] for row in subset])
        version_rows.append(
            {
                "version": version,
                "players": len(subset),
                "median_rounds": statistics.median(row["sum_gamerounds"] for row in subset),
                "median_rounds_ci_low": low,
                "median_rounds_ci_high": high,
            }
        )
    write_csv(REPORTS / "median_bootstrap.csv", version_rows)

    d7_test = tests[1]
    decision = (
        "Keep gate_30 as the recommended default. It has higher observed D7 retention, "
        "and the overall difference is statistically significant. Validate this decision "
        "with a future experiment that also captures revenue and long-term retention."
        if d7_test["p_value"] < 0.05 and d7_test["difference"] > 0
        else "Do not make a definitive gate decision from D7 retention alone; run a larger or richer experiment."
    )
    report = f"""# Cookie Cats Statistical and Quality Report

Generated from `data/cookie_cats.csv` by `scripts/analyze_cookie_cats.py`.

## Data quality

- Status: **{quality["quality_status"]}**
- Source rows: {quality["source_rows"]:,}
- Clean rows: {quality["clean_rows"]:,}
- Removed outlier rows: {quality["removed_outlier_rows"]:,}
- Duplicate user IDs: {quality["duplicate_userids"]}
- Missing values: {quality["missing_values"]}
- Invalid versions: {quality["invalid_versions"]}
- Invalid retention values: {quality["invalid_retention_values"]}
- Negative rounds: {quality["negative_rounds"]}

## Statistical tests

The tests compare `gate_30 - gate_40` using a two-sided two-proportion z-test.

| Metric | Difference | 95% CI | p-value | Result |
|---|---:|---:|---:|---|
| D1 retention | {tests[0]["difference_pp"]:.2f} pp | [{tests[0]["ci_low"] * 100:.2f}, {tests[0]["ci_high"] * 100:.2f}] pp | {tests[0]["p_value"]:.6f} | {tests[0]["result"]} |
| D7 retention | {tests[1]["difference_pp"]:.2f} pp | [{tests[1]["ci_low"] * 100:.2f}, {tests[1]["ci_high"] * 100:.2f}] pp | {tests[1]["p_value"]:.6f} | {tests[1]["result"]} |

## Recommendation

{decision}

This recommendation is limited because the dataset has no revenue, acquisition, device, country, or long-term retention fields.
"""
    (REPORTS / "cookie_cats_statistical_report.md").write_text(report, encoding="utf-8")
    print(json.dumps({"quality": quality, "d7_test": d7_test}, indent=2))


if __name__ == "__main__":
    main()
