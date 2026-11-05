"""
ამინდის ჩანაწერების ჩაწერა/წაკითხვა 4 ფორმატში: JSON, CSV, Parquet, Avro.
ყველა write_* ფუნქცია იღებს records (dict-ების სიას) და path-ს,
ყველა read_* ფუნქცია აბრუნებს იგივე სტრუქტურის dict-ების სიას.
"""

import csv
import json
from pathlib import Path

import fastavro
import pyarrow as pa
import pyarrow.parquet as pq

# Avro schema ფაილშივე ინახება (self-describing ფორმატი)
WEATHER_AVRO_SCHEMA = {
    "type": "record",
    "name": "WeatherRecord",
    "namespace": "eodp.weather",
    "fields": [
        {"name": "city", "type": "string"},
        {"name": "latitude", "type": "double"},
        {"name": "longitude", "type": "double"},
        {"name": "forecast_time", "type": "string"},
        {"name": "temperature_c", "type": "double"},
        {"name": "humidity_pct", "type": "double"},
    ],
}


def _ensure_parent(path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# ---------- JSON ----------
def write_json(records: list, path) -> None:
    path = _ensure_parent(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f)


def read_json(path) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------- CSV ----------
def write_csv(records: list, path) -> None:
    path = _ensure_parent(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def read_csv(path) -> list:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))  # ყველა მნიშვნელობა ტექსტად (str) მოდის


# ---------- Parquet ----------
def write_parquet(records: list, path) -> None:
    path = _ensure_parent(path)
    table = pa.Table.from_pylist(records)
    pq.write_table(table, path, compression="snappy")


def read_parquet(path) -> list:
    return pq.read_table(path).to_pylist()


# ---------- Avro ----------
def write_avro(records: list, path, schema: dict = WEATHER_AVRO_SCHEMA) -> None:
    path = _ensure_parent(path)
    with open(path, "wb") as f:
        fastavro.writer(f, fastavro.parse_schema(schema), records)


def read_avro(path, reader_schema: dict = None) -> list:
    with open(path, "rb") as f:
        parsed = fastavro.parse_schema(reader_schema) if reader_schema else None
        return list(fastavro.reader(f, reader_schema=parsed))