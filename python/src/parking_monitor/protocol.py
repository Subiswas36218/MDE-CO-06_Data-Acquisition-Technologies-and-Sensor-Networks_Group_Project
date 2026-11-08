"""CSV serial protocol shared with the Arduino firmware."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

SERIAL_HEADER: Final[tuple[str, ...]] = (
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
)

VALID_STATUSES: Final[frozenset[str]] = frozenset(
    {"OCCUPIED", "VACANT", "UNKNOWN"}
)


@dataclass(frozen=True, slots=True)
class SlotReading:
    distance_cm: float
    status: str


@dataclass(frozen=True, slots=True)
class ParkingRecord:
    arduino_timestamp_ms: int
    slots: tuple[SlotReading, SlotReading, SlotReading]
    occupied_count: int
    vacant_count: int
    unknown_count: int


def parse_serial_line(line: str) -> ParkingRecord | None:
    """Parse one firmware CSV line.

    Returns None for blank lines, the CSV header, or non-data diagnostic text.
    Raises ValueError for malformed data records.
    """

    cleaned = line.strip()
    if not cleaned or cleaned.startswith("#"):
        return None

    fields = [field.strip() for field in cleaned.split(",")]
    if tuple(fields) == SERIAL_HEADER:
        return None
    if len(fields) != len(SERIAL_HEADER):
        # Tinkercad Serial Monitor captures can include unrelated UI text.
        # Ignore obvious non-CSV output, but reject CSV-shaped bad records.
        if len(fields) < 2:
            return None
        raise ValueError(
            f"Expected {len(SERIAL_HEADER)} CSV fields, received {len(fields)}"
        )

    try:
        uptime = int(fields[0])
        readings = tuple(
            SlotReading(
                distance_cm=float(fields[1 + slot * 2]),
                status=fields[2 + slot * 2].upper(),
            )
            for slot in range(3)
        )
        occupied = int(fields[7])
        vacant = int(fields[8])
        unknown = int(fields[9])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric field in serial record: {cleaned}") from exc

    for index, reading in enumerate(readings, start=1):
        if reading.status not in VALID_STATUSES:
            raise ValueError(
                f"Slot {index} has unsupported status {reading.status!r}"
            )
        if reading.distance_cm < 0 and reading.distance_cm != -1.0:
            raise ValueError(
                f"Slot {index} distance must be >= 0 or -1 for no echo"
            )

    if min(occupied, vacant, unknown) < 0:
        raise ValueError("Occupancy counts cannot be negative")
    if occupied + vacant + unknown != 3:
        raise ValueError("occupied_count + vacant_count + unknown_count must equal 3")

    expected_counts = {
        "OCCUPIED": sum(r.status == "OCCUPIED" for r in readings),
        "VACANT": sum(r.status == "VACANT" for r in readings),
        "UNKNOWN": sum(r.status == "UNKNOWN" for r in readings),
    }
    if (occupied, vacant, unknown) != (
        expected_counts["OCCUPIED"],
        expected_counts["VACANT"],
        expected_counts["UNKNOWN"],
    ):
        raise ValueError("Summary counts do not match the three slot statuses")

    return ParkingRecord(
        arduino_timestamp_ms=uptime,
        slots=(readings[0], readings[1], readings[2]),
        occupied_count=occupied,
        vacant_count=vacant,
        unknown_count=unknown,
    )
