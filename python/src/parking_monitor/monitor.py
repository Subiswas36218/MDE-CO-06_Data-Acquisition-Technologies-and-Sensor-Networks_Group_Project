"""Read Arduino serial records and append them to a CSV log."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import serial
from serial.tools import list_ports

from .protocol import parse_serial_line
from .storage import append_record

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "parking_data.csv"


def show_ports() -> None:
    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports detected.")
        return
    for port in ports:
        description = port.description or "Unknown device"
        print(f"{port.device}\t{description}")


def print_status(record) -> None:
    print("\n" + "=" * 46)
    print("INTELLIGENT PARKING SPACE MONITOR")
    print("=" * 46)
    for index, slot in enumerate(record.slots, start=1):
        distance = "NO ECHO" if slot.distance_cm < 0 else f"{slot.distance_cm:.2f} cm"
        print(f"Slot {index}: {slot.status:8} | {distance}")
    known_slots = record.occupied_count + record.vacant_count
    availability = (
        record.vacant_count / known_slots * 100.0 if known_slots else 0.0
    )
    print("-" * 46)
    print(
        f"Occupied: {record.occupied_count} | Vacant: {record.vacant_count} "
        f"| Unknown: {record.unknown_count}"
    )
    print(f"Availability among known slots: {availability:.1f}%")
    print("=" * 46)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Receive three-slot PING))) parking data from an Arduino Uno."
    )
    parser.add_argument("--port", help="Serial port, e.g. /dev/cu.usbmodem1101")
    parser.add_argument("--baud", type=int, default=9600)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--list-ports", action="store_true", help="List serial ports and exit"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.list_ports:
        show_ports()
        return 0
    if not args.port:
        print("Error: provide --port or run with --list-ports first.", file=sys.stderr)
        return 2

    print(f"Opening {args.port} at {args.baud} baud...")
    print(f"CSV output: {args.output}")
    try:
        with serial.Serial(args.port, args.baud, timeout=args.timeout) as connection:
            # Opening a USB serial connection often resets an Uno.
            connection.reset_input_buffer()
            print("Connected. Press Ctrl+C to stop.")
            while True:
                raw_line = connection.readline().decode("utf-8", errors="replace")
                if not raw_line:
                    continue
                try:
                    record = parse_serial_line(raw_line)
                except ValueError as exc:
                    print(f"Skipping malformed serial line: {exc}", file=sys.stderr)
                    continue
                if record is None:
                    continue
                append_record(args.output, record)
                print_status(record)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
        return 0
    except serial.SerialException as exc:
        print(f"Serial communication failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
