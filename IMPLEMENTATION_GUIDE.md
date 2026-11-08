# Implementation guide

This guide follows the supplied Tinkercad design: **three Parallax PING))) sensors**, one Arduino Uno R3, three red LEDs, three green LEDs and six 220 Ω resistors. The original circuit exports are preserved in `assets/tinkercad_original/`.

## Stage 1 — Extract and inspect the repository

1. Extract `intelligent-parking-space-monitoring-system.zip`.
2. Open the extracted `intelligent-parking-space-monitoring-system` folder in VS Code.
3. Review `docs/PIN_MAPPING.md` and compare every wire endpoint in the live Tinkercad circuit.
4. Do not assume a pin assignment if the live circuit differs. The mapping in this project was inferred visually from the PNG/PDF export, not generated from an electrical netlist.

## Stage 2 — Verify the circuit

The current inferred mapping is:

| Circuit element | Arduino Uno pin |
|---|---:|
| Slot 1 / left sensor SIG (PING3) | D7 |
| Slot 2 / centre sensor SIG (PING2) | D4 |
| Slot 3 / right sensor SIG (PING1) | D2 |
| Slot 1 red / green LEDs | D12 / D13 |
| Slot 2 red / green LEDs | D10 / D11 |
| Slot 3 red / green LEDs | A0 / D9 |

All sensors share 5V and GND. Each LED requires its own 220 Ω series resistor. The PING))) sensor has a single bidirectional `SIG` pin; it is not an HC-SR04 and must not be wired using separate TRIG and ECHO pins.

## Stage 3 — Upload the Arduino firmware

1. Install/open Arduino IDE.
2. Open `firmware/IntelligentParkingSystem/IntelligentParkingSystem.ino`.
3. Verify the `PING_PINS`, `RED_LED_PINS` and `GREEN_LED_PINS` constants against the live circuit.
4. Select **Arduino Uno** under Tools → Board.
5. Select the correct board/serial port, then click **Verify** and **Upload**.
6. Open Serial Monitor at **9600 baud**.
7. Confirm the header appears and that each record contains three distances, three statuses and the occupied/vacant/unknown counts.
8. Test one slot at a time by placing/removing a flat target in front of the corresponding sensor. Verify that only the matching red/green LED pair changes.

The initial decision thresholds are 25 cm for occupied and 30 cm for vacant. The 25–30 cm band retains the last stable classification (hysteresis). Calibrate these values for the physical dimensions and sensor placement of the model.

## Stage 4A — Python setup on macOS

From the repository root in Terminal or the VS Code terminal:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "./python[notebook]"
```

The optional `notebook` extra installs JupyterLab and the notebook kernel as well as the project's Python packages.

## Stage 4B — Run the live Python receiver (physical Arduino)

This workflow requires a physical Arduino connected to the Mac by USB. Tinkercad's browser Serial Monitor is not exposed as a normal local USB serial device.

1. Close Arduino IDE Serial Monitor before opening the same serial port in Python; usually only one application can own the port at a time.
2. List ports:

   ```bash
   python -m parking_monitor.monitor --list-ports
   ```

3. Start monitoring (replace the example path with the port listed on your Mac):

   ```bash
   python -m parking_monitor.monitor \
     --port /dev/cu.usbmodem1101 \
     --baud 9600 \
     --output data/parking_data.csv
   ```

4. Move targets in and out of the three slots. Observe the Python terminal output and confirm that `data/parking_data.csv` grows.
5. Stop with `Ctrl+C`.

## Stage 4C — Tinkercad simulation workflow

Tinkercad's simulated Serial Monitor cannot be opened by `pyserial` as if it were a physical USB serial port. For the simulation-only path:

1. Run the circuit in Tinkercad and open its Serial Monitor.
2. Copy the complete CSV header and data rows into `data/tinkercad_capture.txt`.
3. Import the captured text into the same project CSV schema:

   ```bash
   python -m parking_monitor.import_capture data/tinkercad_capture.txt \
     --output data/parking_data.csv
   ```

4. Check the import count. The importer reports how many records it accepted and skipped.

## Stage 5 — Open the Jupyter visualization notebook

From the repository root, with the virtual environment active:

```bash
jupyter lab notebooks/parking_data_visualization.ipynb
```

Alternatively, open the `.ipynb` file directly in VS Code after installing the recommended Python and Jupyter extensions.

Run the notebook cells from top to bottom. It automatically loads `data/parking_data.csv` when present. If no collected CSV exists, it uses a small deterministic **synthetic demonstration dataset** so the charts can be previewed. The notebook marks this data as synthetic; do not use demo charts as experimental results. After acquiring real Tinkercad-capture or physical-hardware data, rerun the notebook to analyse the actual CSV.

The notebook saves its charts and analysis tables under `reports/notebook/`.

## Stage 6 — Validate and analyse

Run automated protocol tests:

```bash
python -m unittest discover -s tests -v
```

Run the command-line analysis as an additional check:

```bash
python -m parking_monitor.analyze \
  --input data/parking_data.csv \
  --reports-dir reports
```

The analysis excludes `UNKNOWN` from occupied/vacant percentages and excludes `-1` no-echo values from distance statistics. A sensor timeout is not automatically considered a vacant parking space.

## Stage 7 — Conduct experiments and prepare the report

Use the experiments in `docs/EXPERIMENTS_AND_REPORT.md`:

1. Empty-bay baseline.
2. Single-slot vehicle detection.
3. Multiple-slot occupancy combinations.
4. Threshold/hysteresis behaviour.
5. Repeatability against a known reference distance (at least 30 readings).
6. Data-transfer and CSV integrity.

Keep the provenance clear in the report: distinguish Tinkercad simulation records, physical sensor measurements, and synthetic notebook demonstration data. Do not claim a detection accuracy or measurement error until it has been calculated from a documented reference test.

## Troubleshooting

- **No serial port listed:** reconnect the Arduino, try another USB data cable/port and check macOS System Information → USB.
- **Port busy:** close Arduino Serial Monitor and any other serial-terminal application before launching the Python receiver.
- **All readings are UNKNOWN:** check 5V/GND, each PING))) SIG wire, the selected pins, sensor orientation and target placement.
- **A sensor responds to another slot's target:** increase the inter-sensor delay in the firmware and reposition sensors to reduce acoustic cross-talk.
- **LED indicators do not match the slot:** recheck the actual LED signal pin and polarity; compare with `docs/PIN_MAPPING.md`.
- **Notebook cannot find the CSV:** confirm that `data/parking_data.csv` exists at the repository root, or change `DATA_FILE` in the notebook configuration cell.
