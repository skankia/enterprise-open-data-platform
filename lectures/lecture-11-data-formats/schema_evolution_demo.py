"""
lecture 11 lab: Avro schema evolution.
პრობლემა: ძველი ფაილი V1 schema-ით დაიწერა, მერე schema-ს ახალი ველი დაემატა (V2).
Avro-ში default მნიშვნელობით ორივე მიმართულებით წაკითხვა მუშაობს.
გაშვება პროექტის root-იდან:
    python lectures/lecture-11-data-formats/schema_evolution_demo.py
"""

import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from generate_synthetic_data import generate_weather_records  # noqa: E402
from src.ingestion.format_writer import (  # noqa: E402
    WEATHER_AVRO_SCHEMA,
    read_avro,
    write_avro,
)

OUT_DIR = ROOT / "data" / "format_comparison"

# V2 = V1 + ახალი ველი default-ით (default-ის გარეშე ძველ ფაილს ვერ წაიკითხავს)
WEATHER_AVRO_SCHEMA_V2 = deepcopy(WEATHER_AVRO_SCHEMA)
WEATHER_AVRO_SCHEMA_V2["fields"].append(
    {"name": "wind_speed_kmh", "type": "double", "default": 0.0}
)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # სცენარი A: ძველი ფაილი (V1), ახალი კოდი (V2)
    v1_records = generate_weather_records(3)
    v1_path = OUT_DIR / "weather_v1.avro"
    write_avro(v1_records, v1_path)  # ნაგულისხმევი schema = V1

    print("A) V1 ფაილი, წაკითხვა V2 schema-ით:")
    for rec in read_avro(v1_path, reader_schema=WEATHER_AVRO_SCHEMA_V2):
        print("  ", rec)

    # სცენარი B: ახალი ფაილი (V2), ძველი კოდი (V1)
    v2_records = [dict(r, wind_speed_kmh=12.5) for r in generate_weather_records(3)]
    v2_path = OUT_DIR / "weather_v2.avro"
    write_avro(v2_records, v2_path, schema=WEATHER_AVRO_SCHEMA_V2)

    print("\nB) V2 ფაილი, წაკითხვა V1 schema-ით:")
    for rec in read_avro(v2_path, reader_schema=WEATHER_AVRO_SCHEMA):
        print("  ", rec)


if __name__ == "__main__":
    main()