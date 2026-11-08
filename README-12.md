# Intelligent Parking Space Monitoring System

A three-slot parking monitoring prototype based on the **exact component family shown in the supplied Tinkercad exports**: Arduino Uno R3, three Parallax PING))) ultrasonic distance sensors, three red LEDs, three green LEDs, six 220 Ω resistors and a breadboard.

The system uses:

- **Arduino firmware (C/C++)** for PING))) triggering, echo-pulse timing, distance calculation, threshold-based occupancy classification and LED control.
- **Python** for USB serial data acquisition, CSV logging, validation, statistical summaries and plots.

> **Hardware-source alignment:** The user-provided design contains three Parallax PING))) sensors, not four HC-SR04 modules. The original uploaded `.ino` was an onboard LED blink test; it is retained unchanged under `assets/tinkercad_original/` and is not the system firmware. The implemented firmware is in `firmware/IntelligentParkingSystem/`.

## Repository contents

```text
intelligent-parking-space-monitoring-system/
├── assets/
│   └── tinkercad_original/
│       ├── circuit.png                  # Original supplied circuit image
│       ├── circuit_schematic.pdf        # Original supplied one-page schematic
│       ├── bom.csv                      # Original supplied Tinkercad BOM
│       └── original_blink_test.ino      # Original supplied blink-test sketch
├── firmware/
│   └── IntelligentParkingSystem/
│       └── IntelligentParkingSystem.ino # Three PING))) sensor firmware
├── python/
│   ├── pyproject.toml
│   └── src/parking_monitor/
│       ├── protocol.py                  # Serial CSV parser and validation
│       ├── storage.py                   # Persistent CSV logger
│       ├── monitor.py                   # Live Arduino serial receiver
│       ├── import_capture.py             # Import saved Tinkercad Serial Monitor text
│       └── analyze.py                   # Pandas analysis and Matplotlib plots
├── notebooks/
│   └── parking_data_visualization.ipynb # Jupyter data visualization and analysis
├── tests/
│   └── test_protocol.py
├── docs/
│   ├── PIN_MAPPING.md
│   ├── DATA_FORMAT.md
│   └── EXPERIMENTS_AND_REPORT.md
├── data/                                # Generated parking_data.csv goes here
├── reports/                             # Generated summaries and PNG plots go here
├── .github/workflows/python-tests.yml
├── .gitignore
└── README.md
```

## 1. Supplied Tinkercad design and bill of materials

The exported schematic is a one-page Tinkercad circuit drawing dated 7 November 2026. It labels the three sensors `PING3`, `PING2` and `PING1` from left to right, shows shared 5 V and ground connections, and includes six LED indicator branches.

| Component | Quantity | Notes |
|---|---:|---|
| Arduino Uno R3 | 1 | Main controller |
| Breadboard | 1 | Circuit assembly |
| Parallax PING))) ultrasonic distance sensor | 3 | One per parking bay |
| 220 Ω resistor | 6 | One per LED |
| Red LED | 3 | Occupied indication |
| Green LED | 3 | Vacant indication |
| **Total component units** | **17** | Sum of BOM quantities |

The original BOM has six line items; the component quantities sum to **17 units**. The original files are retained, not rewritten.

## 2. Pin mapping

The mapping below was read visually from the supplied circuit PNG and schematic. It is a carefully inferred mapping rather than a generated electrical netlist. Check the live Tinkercad endpoints before uploading the sketch.

### PING))) sensor SIG connections

| Parking slot | Sensor in supplied schematic | Arduino Uno SIG pin |
|---|---|---:|
| 1 (left) | PING3 | D7 |
| 2 (centre) | PING2 | D4 |
| 3 (right) | PING1 | D2 |

All sensors share Arduino 5 V and GND. Each PING))) uses one bidirectional `SIG` pin for trigger and echo.

### LED connections

| Slot | Red LED — occupied | Green LED — vacant |
|---|---:|---:|
| 1 | D12 | D13 |
| 2 | D10 | D11 |
| 3 | A0 (digital GPIO use) | D9 |

Each LED must be connected in series with its own 220 Ω resistor. Arduino Uno analog pin A0 can also operate as a digital I/O pin; in this circuit it is used as the third red-LED output. Full notes are in [`docs/PIN_MAPPING.md`](docs/PIN_MAPPING.md).

## 3. How the system works

1. Arduino drives a PING))) sensor's single `SIG` line HIGH for approximately 5 µs.
2. The sensor emits an ultrasonic burst and returns an echo pulse on that same `SIG` line.
3. Arduino measures the echo pulse width using `pulseIn()`.
4. The approximate distance is calculated as `distance_cm = echo_duration_us × 0.0343 / 2`.
5. A distance at or below **25 cm** is classified as occupied; a distance at or above **30 cm** is classified as vacant.
6. Between 25 cm and 30 cm, the last stable state is retained (hysteresis) to reduce LED/status flicker.
7. No echo or an unresolved first reading is reported as `UNKNOWN`; both LEDs for that bay remain OFF. Unknown is not counted as vacant.
8. The Arduino emits one CSV row per scan at 9600 baud. Python validates the row, prints slot status and appends it to `data/parking_data.csv`.
9. The analysis script calculates occupancy statistics and writes plots to `reports/`.

The threshold values are initial calibration values only. They must be validated against the actual parking model dimensions, sensor mounting position and target shape.

## 4. Important distinction: PING))) is not HC-SR04

The Parallax PING))) module has three physical connections: `GND`, `5V` and `SIG`. Its one `SIG` line is switched between output (trigger) and input (echo). Do not wire or program it as an HC-SR04 with separate `TRIG` and `ECHO` pins.

The PING))) product documentation describes a single I/O pin, a typical 5 µs trigger pulse, an echo pulse representing round-trip travel time, and an approximate 3 cm–3 m measurement range:

- [Parallax PING))) product page and specifications](https://www.parallax.com/products/ping-ultrasonic-distance-sensor/)
- [Parallax Learn: Arduino wiring and PING))) example](https://learn.parallax.com/kickstarts/ping-ultrasonic-distance-sensor/)
- [PING))) (#28015) datasheet PDF](https://www.digikey.com/htmldatasheets/production/1253021/0/0/1/28015.pdf)

## 5. Arduino firmware setup

1. Open Arduino IDE.
2. Open `firmware/IntelligentParkingSystem/IntelligentParkingSystem.ino`.
3. Select **Arduino Uno** as the board.
4. Select the correct serial port.
5. Verify the pin assignments in the constants near the top of the sketch.
6. Upload the sketch.
7. Open Serial Monitor at **9600 baud**. The first line is a CSV header followed by measurement rows.

The active sketch has no third-party Arduino library dependency.

### Serial output format

```csv
arduino_timestamp_ms,slot1_distance_cm,slot1_status,slot2_distance_cm,slot2_status,slot3_distance_cm,slot3_status,occupied_count,vacant_count,unknown_count
1250,12.50,OCCUPIED,42.00,VACANT,18.25,OCCUPIED,2,1,0
```

The example row is an **illustrative protocol example**, not a reading from the supplied circuit.

## 6. Python setup

Python 3.10 or newer is recommended. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\\Scripts\\activate       # Windows PowerShell

python -m pip install --upgrade pip
python -m pip install -e ./python
```

### Identify the Arduino serial port

```bash
python -m parking_monitor.monitor --list-ports
```

Typical macOS port names look like `/dev/cu.usbmodem...` or `/dev/cu.usbserial...`; Windows commonly uses `COM3`, `COM4`, etc. Use the actual port reported on your computer.

### Run live monitoring (physical Arduino over USB)

```bash
python -m parking_monitor.monitor --port /dev/cu.usbmodem1101
```

Replace the example port with the one detected above. Optional parameters:

```bash
python -m parking_monitor.monitor \
  --port /dev/cu.usbmodem1101 \
  --baud 9600 \
  --output data/parking_data.csv
```

The Python logger adds a UTC receive timestamp and stores the parsed sensor readings and counts. Stop with `Ctrl+C`.

## 7. Tinkercad-only workflow

Tinkercad's simulated serial monitor is not exposed to your Mac as a normal USB serial port, so `pyserial` cannot connect directly to the browser simulation. For a simulation-only run:

1. Start the Tinkercad simulation and open its Serial Monitor.
2. Copy the CSV header and data rows from the Serial Monitor into a text file, for example `data/tinkercad_capture.txt`.
3. Keep the Arduino CSV header and data rows intact. Other console text is ignored where possible; malformed CSV-like rows are reported.
4. Run:

```bash
python -m parking_monitor.import_capture data/tinkercad_capture.txt \
  --output data/parking_data.csv
```

For continuous live Python serial monitoring, use a physical Arduino Uno connected by USB, or a simulator that explicitly provides a serial bridge.

## 8. Analyse the acquired dataset

After the CSV has been created:

```bash
python -m parking_monitor.analyze
```

Or specify paths:

```bash
python -m parking_monitor.analyze \
  --input data/parking_data.csv \
  --reports-dir reports
```

The analysis produces:

- `reports/analysis_summary.txt`
- `reports/occupancy_over_time.png`
- `reports/slot_utilization.png`
- `reports/distance_measurements.png`

Unknown readings are excluded from slot-specific occupied/vacant utilization calculations. Distance values of `-1` (no echo) are excluded from distance statistics.

## 9. Jupyter data visualization notebook

Open `notebooks/parking_data_visualization.ipynb` in JupyterLab or VS Code. It loads `data/parking_data.csv` and creates occupancy, utilization, distance, state-heatmap and data-quality visualizations. If no collected CSV exists yet, it uses a clearly labelled synthetic demonstration dataset for preview only. It saves notebook outputs under `reports/notebook/`.

Install the optional notebook dependencies with:

```bash
python -m pip install -e "./python[notebook]"
jupyter lab notebooks/parking_data_visualization.ipynb
```

See [`docs/IMPLEMENTATION_GUIDE.md`](docs/IMPLEMENTATION_GUIDE.md) for the complete staged setup, Tinkercad import workflow and physical Arduino serial workflow.

## 10. Tests

From the repository root, with the virtual environment active:

```bash
python -m unittest discover -s tests -v
```

The tests validate the serial protocol parser, including header handling, valid records, no-echo/unknown readings, malformed rows and occupancy-count consistency.

## 11. Experimental evaluation

Suggested laboratory tests and report sections are listed in [`docs/EXPERIMENTS_AND_REPORT.md`](docs/EXPERIMENTS_AND_REPORT.md). In brief:

- Empty-bay baseline.
- Single-slot vehicle detection.
- Multiple occupied-slot combinations.
- Threshold and hysteresis behaviour.
- Repeatability and error against a known reference distance.
- Serial transfer and CSV data integrity.

Do not state a numerical accuracy or detection rate until you have collected and analysed actual measurements. Distinguish Tinkercad simulation data from measurements made with physical hardware.

## 12. Limitations and cautions

- Ultrasonic cross-talk is possible; the firmware scans sensors sequentially with a gap between readings.
- Soft, angled or narrow surfaces may reflect sound away from a sensor and cause a timeout.
- A timeout is recorded as `UNKNOWN`, not automatically `VACANT`.
- The fixed thresholds require calibration for the model's sensor-to-vehicle geometry.
- Tinkercad simulation does not guarantee the same sensor behaviour, noise or timing as a physical installation.
- This is a laboratory prototype, not a safety-certified or commercial parking-control system.

## Original source files

The four supplied exports are preserved under `assets/tinkercad_original/`. The active firmware is a new implementation based on the observed circuit and the PING))) protocol. The original blink test has not been silently overwritten.
