"""
lecture 11 lab: JSON / CSV / Parquet / Avro შედარება.
ზომა, ჩაწერის დრო, წაკითხვის დრო - 10,000 ამინდის ჩანაწერზე.
გაშვება პროექტის root-იდან:
    python lectures/lecture-11-data-formats/compare_formats.py
"""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))  # რომ src.ingestion მოიძებნოს

from generate_synthetic_data import generate_weather_records  # noqa: E402
from src.ingestion import format_writer as fw  # noqa: E402

OUT_DIR = ROOT / "data" / "format_comparison"

FORMATS = {
    "json": (fw.write_json, fw.read_json),
    "csv": (fw.write_csv, fw.read_csv),
    "parquet": (fw.write_parquet, fw.read_parquet),
    "avro": (fw.write_avro, fw.read_avro),
}


def timed(func, *args):
    start = time.perf_counter()
    result = func(*args)
    return result, (time.perf_counter() - start) * 1000  # მილიწამებში


def main() -> None:
    records = generate_weather_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for name, (write_fn, read_fn) in FORMATS.items():
        path = OUT_DIR / f"weather.{name}"
        _, write_ms = timed(write_fn, records, path)
        _, read_ms = timed(read_fn, path)
        results.append((name, path.stat().st_size, write_ms, read_ms))

    json_size = results[0][1]
    print(f"\n{len(records):,} ჩანაწერი\n")
    print(f"{'ფორმატი':<10}{'ზომა (KB)':>12}{'JSON-თან %':>13}{'ჩაწერა (ms)':>14}{'წაკითხვა (ms)':>16}")
    print("-" * 65)
    for name, size, w_ms, r_ms in results:
        print(f"{name:<10}{size / 1024:>12.1f}{size / json_size * 100:>12.0f}%{w_ms:>14.1f}{r_ms:>16.1f}")


if __name__ == "__main__":
    main()