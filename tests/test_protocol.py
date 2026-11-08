import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python" / "src"))

from parking_monitor.protocol import parse_serial_line  # noqa: E402


class ProtocolTests(unittest.TestCase):
    def test_header_is_ignored(self):
        header = (
            "arduino_timestamp_ms,slot1_distance_cm,slot1_status,"
            "slot2_distance_cm,slot2_status,slot3_distance_cm,slot3_status,"
            "occupied_count,vacant_count,unknown_count"
        )
        self.assertIsNone(parse_serial_line(header))

    def test_valid_record(self):
        line = "1250,12.50,OCCUPIED,42.00,VACANT,18.25,OCCUPIED,2,1,0"
        record = parse_serial_line(line)
        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.arduino_timestamp_ms, 1250)
        self.assertEqual(record.slots[0].status, "OCCUPIED")
        self.assertAlmostEqual(record.slots[1].distance_cm, 42.0)
        self.assertEqual((record.occupied_count, record.vacant_count, record.unknown_count), (2, 1, 0))

    def test_no_echo_and_unknown_are_valid(self):
        line = "2000,-1.00,UNKNOWN,35.00,VACANT,10.00,OCCUPIED,1,1,1"
        record = parse_serial_line(line)
        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.slots[0].distance_cm, -1.0)
        self.assertEqual(record.unknown_count, 1)

    def test_inconsistent_counts_are_rejected(self):
        line = "1250,12.50,OCCUPIED,42.00,VACANT,18.25,OCCUPIED,1,2,0"
        with self.assertRaises(ValueError):
            parse_serial_line(line)

    def test_malformed_record_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_serial_line("1250,12.5,OCCUPIED")

    def test_blank_and_diagnostic_lines_are_ignored(self):
        self.assertIsNone(parse_serial_line(""))
        self.assertIsNone(parse_serial_line("# SMART PARKING SYSTEM"))


if __name__ == "__main__":
    unittest.main()
