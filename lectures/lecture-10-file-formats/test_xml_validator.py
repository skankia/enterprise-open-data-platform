"""
lecture 10: xml_validator.py-ის გადამოწმება - სწორი და არასრული XML.
გაშვება (პროექტის ძირეული საქაღალდიდან):
    python lectures/lecture-10-file-formats/test_xml_validator.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.ingestion.xml_validator import XMLSchemaValidationError, validate_against_schema

XSD_PATH = "data/sample/weather_forecast.xsd"
VALID_XML = "data/sample/weather_forecast_2026-08-27.xml"
INCOMPLETE_XML = "/tmp/weather_forecast_incomplete.xml"


def test_valid_xml():
    assert validate_against_schema(VALID_XML, XSD_PATH) is True
    print("[OK] სწორი XML გავიდა ვალიდაციას")


def test_incomplete_xml():
    # temperature_c ველი გამოტოვებულია
    Path(INCOMPLETE_XML).write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        "<forecasts><forecast><city>Tbilisi</city>"
        "<forecast_time>2026-08-27T12:00:00+00</forecast_time>"
        "</forecast></forecasts>",
        encoding="utf-8",
    )
    try:
        validate_against_schema(INCOMPLETE_XML, XSD_PATH)
        raise AssertionError("უნდა ატყორცნოს XMLSchemaValidationError")
    except XMLSchemaValidationError as exc:
        print(f"[OK] სწორად დაიჭირა არასრული XML: {exc}")


if __name__ == "__main__":
    test_valid_xml()
    test_incomplete_xml()