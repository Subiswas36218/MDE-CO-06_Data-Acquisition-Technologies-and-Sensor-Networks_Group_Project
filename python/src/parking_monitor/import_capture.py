"""Convert a saved Tinkercad/Serial-Monitor text capture into the project CSV."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from .protocol import parse_serial_line
from .storage import append_record


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import CSV-formatted Arduino lines from a text capture."
    )
    parser.add_argument("input", type=Path, help="Text file copied from Serial Monitor")
    parser.add_argument(
        "--output", type=Path, default=Path("data/parking_data.csv")
    )
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Input file does not exist: {args.input}")

    imported = 0
    skipped = 0
    for line_number, line in enumerate(
        args.input.read_text(encoding="utf-8", errors="replace").splitlines(),
        start=1,
    ):
        try:
            record = parse_serial_line(line)
        except ValueError as exc:
            print(f"Line {line_number}: skipped ({exc})")
            skipped += 1
            continue
        if record is None:
            skipped += 1
            continue
        append_record(args.output, record)
        imported += 1

    print(f"Imported {imported} records; skipped {skipped} non-data/invalid lines.")
    print(f"Output: {args.output}")
    return 0 if imported else 1


if __name__ == "__main__":
    raise SystemExit(main())
