"""
lecture 10: sample CSV/XML ფაილების გენერაცია (File Naming Conventions-ის დემონსტრაცია).
"""

import csv
import xml.etree.ElementTree as ET
from pathlib import Path

SAMPLE_DIR = Path("data/sample")

CURRENCY_ROWS = [
    {"currency_code": "USD", "quantity": "1", "rate": "2.6512", "rate_date": "2026-08-27"},
    {"currency_code": "EUR", "quantity": "1", "rate": "2.9284", "rate_date": "2026-08-27"},
]

WEATHER_ROWS = [
    {"city": "Tbilisi", "forecast_time": "2026-08-27T12:00:00+00", "temperature_c": "28.3"},
    {"city": "Tbilisi", "forecast_time": "2026-08-27T13:00:00+00", "temperature_c": "29.2"},
]


def build_currency_csv() -> Path:
    path = SAMPLE_DIR / "currency_rates_2026-08-27.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(CURRENCY_ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(CURRENCY_ROWS)
    return path


def build_weather_xml() -> Path:
    path = SAMPLE_DIR / "weather_forecast_2026-08-27.xml"
    root = ET.Element("forecasts")
    for row in WEATHER_ROWS:
        record = ET.SubElement(root, "forecast")
        for key, value in row.items():
            field = ET.SubElement(record, key)
            field.text = value
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


if __name__ == "__main__":
    csv_path = build_currency_csv()
    xml_path = build_weather_xml()
    print(f"[OK] {csv_path}")
    print(f"[OK] {xml_path}")