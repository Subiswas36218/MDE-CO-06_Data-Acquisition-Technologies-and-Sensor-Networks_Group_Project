"""Append parsed parking measurements to a durable CSV file."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from .protocol import ParkingRecord

OUTPUT_COLUMNS = [
    "received_at_utc",
    "arduino_timestamp_ms",
    "slot1_distance_cm",
    "slot1_status",
    "slot2_distance_cm",
    "slot2_status",
    "slot3_distance_cm",
    "slot3_status",
    "occupied_count",
    "vacant_count",
    "unknown_count",
]


def append_record(path: Path, record: ParkingRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0

    row: dict[str, object] = {
        "received_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="milliseconds"
        ),
        "arduino_timestamp_ms": record.arduino_timestamp_ms,
        "occupied_count": record.occupied_count,
        "vacant_count": record.vacant_count,
        "unknown_count": record.unknown_count,
    }

    for index, slot in enumerate(record.slots, start=1):
        row[f"slot{index}_distance_cm"] = slot.distance_cm
        row[f"slot{index}_status"] = slot.status

    with path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
        if needs_header:
            writer.writeheader()
        writer.writerow(row)
