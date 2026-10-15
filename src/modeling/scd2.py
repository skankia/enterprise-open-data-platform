"""
lecture 6 (დამატება): Slowly Changing Dimension (SCD) Type 2 - testable ლოგიკა.
Star Schema-ს (Step 1-7) dim_location-ისთვის - თუ ლოკაციის ატრიბუტი შეიცვალა,
ძველი row 'იხურება' (is_current=False), ახალი emerges (is_current=True) -
ისტორია არასდროს იშლება, ჩაწერის ნაცვლად ახალი ვერსია ემატება.

გაშვება (ტესტი):
    python src/modeling/scd2.py
"""


def scd2_upsert(existing_rows: list, new_version: dict, key_field: str,
                tracked_fields: list, effective_date: str) -> list:
    """
    SCD Type 2 upsert:
    - თუ key_field-ის მიხედვით row არ არსებობს -> პირველი ვერსია ემატება.
    - თუ არსებობს და tracked_fields არ შეცვლილა -> არაფერი იცვლება.
    - თუ არსებობს და tracked_fields შეიცვალა -> ძველი row იხურება
      (is_current=False, valid_to=effective_date), ახალი emerges
      (is_current=True, valid_from=effective_date).
    """
    key_value = new_version[key_field]
    current_row = next(
        (r for r in existing_rows if r[key_field] == key_value and r.get("is_current")),
        None,
    )

    if current_row is None:
        new_row = {**new_version, "valid_from": effective_date,
                   "valid_to": None, "is_current": True}
        return existing_rows + [new_row]

    changed = any(current_row.get(f) != new_version.get(f) for f in tracked_fields)
    if not changed:
        return existing_rows

    updated_rows = [
        {**r, "valid_to": effective_date, "is_current": False} if r is current_row else r
        for r in existing_rows
    ]
    new_row = {**new_version, "valid_from": effective_date,
               "valid_to": None, "is_current": True}
    return updated_rows + [new_row]


def run_scenarios():
    """3 სცენარის ტესტი: პირველი ვერსია, ცვლილების გარეშე, რეალური ცვლილება."""
    key = "city"
    tracked = ["population_category"]
    tbilisi = {"city": "Tbilisi", "country": "Georgia", "population_category": "large"}

    # Test 1: პირველი ვერსია (ცარიელი სიიდან)
    rows = scd2_upsert([], tbilisi, key, tracked, "2026-01-01")
    print("Test 1:", rows[0])
    assert len(rows) == 1
    assert rows[0]["is_current"] is True
    assert rows[0]["valid_from"] == "2026-01-01"
    assert rows[0]["valid_to"] is None

    # Test 2: იგივე მონაცემი - ცვლილება არ არის, არაფერი უნდა დაემატოს
    rows_same = scd2_upsert(rows, dict(tbilisi), key, tracked, "2026-02-01")
    print(f"Test 2: row-ების რაოდენობა = {len(rows_same)} "
          "(უცვლელია - ცვლილება არ დაფიქსირდა)")
    assert len(rows_same) == 1
    assert rows_same[0] == rows[0]

    # Test 3: tracked ველი შეიცვალა - ძველი იხურება, ახალი ემატება
    changed = {**tbilisi, "population_category": "mega"}
    rows_changed = scd2_upsert(rows_same, changed, key, tracked, "2026-09-01")
    print("Test 3:")
    for row in rows_changed:
        print(row)
    assert len(rows_changed) == 2

    old, new = rows_changed
    assert old["population_category"] == "large"
    assert old["is_current"] is False
    assert old["valid_from"] == "2026-01-01"
    assert old["valid_to"] == "2026-09-01"

    assert new["population_category"] == "mega"
    assert new["is_current"] is True
    assert new["valid_from"] == "2026-09-01"
    assert new["valid_to"] is None

    # ზუსტად ერთი მიმდინარე ვერსია გვაქვს ამ ქალაქისთვის
    assert sum(1 for r in rows_changed if r["is_current"]) == 1

    # შემავალი სია არ უნდა შეცვლილიყო (ისტორია იმუტაბელურია)
    assert rows_same[0]["is_current"] is True

    print("[OK] ყველა 3 სცენარი (პირველი ჩანაწერი, ცვლილების გარეშე, "
          "რეალური ცვლილება) სწორად მუშაობს")


if __name__ == "__main__":
    run_scenarios()