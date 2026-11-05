"""
lecture 10: pandas_transform.py-ის გადამოწმება.
გაშვება (პროექტის ძირეული საქაღალდიდან):
    python lectures/lecture-10-file-formats/test_pandas_transform.py

ტესტი თავად ქმნის მრავალდღიან CSV-ს (3 დღე x 2 ვალუტა), რადგან
data/sample/currency_rates_2026-08-27.csv მხოლოდ ერთი დღის მონაცემს შეიცავს.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.ingestion.pandas_transform import compute_daily_currency_stats

CSV_PATH = "/tmp/test_currency_multiday.csv"

ROWS = [
    ("USD", "2026-08-18", "2.6480"),
    ("USD", "2026-08-19", "2.6502"),
    ("USD", "2026-08-20", "2.6455"),
    ("EUR", "2026-08-18", "2.9150"),
    ("EUR", "2026-08-19", "2.9180"),
    ("EUR", "2026-08-20", "2.9210"),
]


def build_multiday_csv() -> None:
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["currency_code", "rate_date", "rate"])
        writer.writerows(ROWS)


def manual_stats() -> dict:
    """იგივე გამოთვლა stdlib csv-ით, ხელით loop-ით."""
    rates = defaultdict(list)
    with open(CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rates[row["currency_code"]].append(float(row["rate"]))
    return {
        code: (round(sum(v) / len(v), 4), min(v), max(v))
        for code, v in rates.items()
    }


def test_compute_daily_currency_stats():
    build_multiday_csv()
    stats = compute_daily_currency_stats(CSV_PATH)

    assert set(stats.columns) == {"currency_code", "avg_rate", "min_rate", "max_rate"}
    assert len(stats) == 2

    usd = stats[stats["currency_code"] == "USD"].iloc[0]
    assert usd["avg_rate"] == 2.6479
    assert usd["min_rate"] == 2.6455
    assert usd["max_rate"] == 2.6502

    # pandas-ის შედეგი უნდა ემთხვეოდეს ხელნაწერ გამოთვლას
    manual = manual_stats()
    for _, row in stats.iterrows():
        assert (row["avg_rate"], row["min_rate"], row["max_rate"]) == manual[row["currency_code"]]

    print("[OK] pandas_transform.py - ტესტი გავლილია")
    print(stats.to_string(index=False))
    print("[OK] pandas groupby().agg() ემთხვევა stdlib csv-ით ხელნაწერ გამოთვლას")


if __name__ == "__main__":
    test_compute_daily_currency_stats()