"""Analyse parking CSV data and create plots plus a text summary."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "parking_data.csv"
DEFAULT_REPORTS = PROJECT_ROOT / "reports"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(
            f"No data file found at {args.input}. Run the monitor or import a capture first."
        )

    df = pd.read_csv(args.input)
    if df.empty:
        parser.error("The parking data CSV contains no measurements.")

    required = {
        "received_at_utc", "occupied_count", "vacant_count", "unknown_count",
        "slot1_distance_cm", "slot1_status",
        "slot2_distance_cm", "slot2_status",
        "slot3_distance_cm", "slot3_status",
    }
    missing = required.difference(df.columns)
    if missing:
        parser.error(f"CSV is missing required columns: {', '.join(sorted(missing))}")

    args.reports_dir.mkdir(parents=True, exist_ok=True)
    df["received_at_utc"] = pd.to_datetime(df["received_at_utc"], errors="coerce", utc=True)
    df = df.dropna(subset=["received_at_utc"]).copy()
    if df.empty:
        parser.error("No valid timestamps found in the CSV.")

    for column in ("occupied_count", "vacant_count", "unknown_count"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    total_records = len(df)
    average_occupied = float(df["occupied_count"].mean())
    average_vacant = float(df["vacant_count"].mean())
    average_unknown = float(df["unknown_count"].mean())
    average_utilization = float((df["occupied_count"] / 3.0 * 100.0).mean())

    slot_stats: list[tuple[str, float, int]] = []
    distance_stats: list[tuple[str, float, float, int]] = []
    for slot in range(1, 4):
        status_col = f"slot{slot}_status"
        distance_col = f"slot{slot}_distance_cm"
        known = df[status_col].isin(["OCCUPIED", "VACANT"])
        known_count = int(known.sum())
        occupied_pct = (
            float((df.loc[known, status_col] == "OCCUPIED").mean() * 100.0)
            if known_count else float("nan")
        )
        slot_stats.append((f"Slot {slot}", occupied_pct, known_count))

        distances = pd.to_numeric(df[distance_col], errors="coerce")
        valid_distances = distances[distances >= 0]
        mean_distance = float(valid_distances.mean()) if not valid_distances.empty else float("nan")
        std_distance = float(valid_distances.std(ddof=1)) if len(valid_distances) > 1 else 0.0
        distance_stats.append((f"Slot {slot}", mean_distance, std_distance, len(valid_distances)))

    lines = [
        "INTELLIGENT PARKING SPACE MONITORING — ANALYSIS SUMMARY",
        "=" * 60,
        f"Records analysed: {total_records}",
        f"Average occupied slots: {average_occupied:.2f} / 3",
        f"Average vacant slots: {average_vacant:.2f} / 3",
        f"Average unknown slots: {average_unknown:.2f} / 3",
        f"Mean occupancy/utilization: {average_utilization:.2f}%",
        "",
        "SLOT-WISE OCCUPANCY (unknown readings excluded)",
        "-" * 60,
    ]
    for name, percentage, count in slot_stats:
        value = "n/a" if np.isnan(percentage) else f"{percentage:.2f}%"
        lines.append(f"{name}: {value} across {count} known readings")
    lines += ["", "DISTANCE MEASUREMENT SUMMARY", "-" * 60]
    for name, mean_value, std_value, count in distance_stats:
        if count:
            lines.append(
                f"{name}: mean={mean_value:.2f} cm, std={std_value:.2f} cm, n={count}"
            )
        else:
            lines.append(f"{name}: no valid distance readings")

    summary_path = args.reports_dir / "analysis_summary.txt"
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Plot 1: total occupied/vacant/unknown spaces over time.
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["received_at_utc"], df["occupied_count"], marker=".", label="Occupied")
    ax.plot(df["received_at_utc"], df["vacant_count"], marker=".", label="Vacant")
    ax.plot(df["received_at_utc"], df["unknown_count"], marker=".", label="Unknown")
    ax.set(title="Parking Occupancy Over Time", xlabel="Received time (UTC)", ylabel="Number of slots")
    ax.set_ylim(-0.1, 3.1)
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=mdates.UTC))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(args.reports_dir / "occupancy_over_time.png", dpi=180)
    plt.close(fig)

    # Plot 2: occupancy percentage by slot, excluding UNKNOWN readings.
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = [item[0] for item in slot_stats]
    values = [0.0 if np.isnan(item[1]) else item[1] for item in slot_stats]
    bars = ax.bar(labels, values)
    ax.set(title="Parking Slot Utilization", xlabel="Parking slot", ylabel="Occupied readings (%)", ylim=(0, 100))
    ax.grid(axis="y", alpha=0.3)
    for bar, item in zip(bars, slot_stats):
        if np.isnan(item[1]):
            ax.text(bar.get_x() + bar.get_width() / 2, 2, "No known data", ha="center", va="bottom", rotation=90, fontsize=8)
    fig.tight_layout()
    fig.savefig(args.reports_dir / "slot_utilization.png", dpi=180)
    plt.close(fig)

    # Plot 3: distance trends. No-echo sentinel values (-1) are excluded.
    fig, ax = plt.subplots(figsize=(11, 5))
    for slot in range(1, 4):
        column = f"slot{slot}_distance_cm"
        distances = pd.to_numeric(df[column], errors="coerce")
        valid = distances >= 0
        ax.plot(df.loc[valid, "received_at_utc"], distances[valid], marker=".", label=f"Slot {slot}")
    ax.set(title="Ultrasonic Distance Measurements", xlabel="Received time (UTC)", ylabel="Distance (cm)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=mdates.UTC))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(args.reports_dir / "distance_measurements.png", dpi=180)
    plt.close(fig)

    print("\n".join(lines))
    print(f"\nSaved summary and plots in: {args.reports_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
