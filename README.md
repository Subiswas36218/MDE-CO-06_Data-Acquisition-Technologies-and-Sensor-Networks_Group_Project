# Intelligent Parking Space Monitoring System

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Arduino%20Uno-00979D?logo=arduino&logoColor=white" alt="Arduino Uno">
  <img src="https://img.shields.io/badge/Firmware-C%2B%2B-00599C?logo=cplusplus&logoColor=white" alt="C++">
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Data-Pandas%20%7C%20NumPy-150458?logo=pandas&logoColor=white" alt="Pandas and NumPy">
  <img src="https://img.shields.io/badge/Visualisation-Matplotlib%20%7C%20Seaborn-11557C" alt="Matplotlib and Seaborn">
  <img src="https://img.shields.io/badge/Notebook-Jupyter-F37626?logo=jupyter&logoColor=white" alt="Jupyter">
  <img src="https://img.shields.io/badge/Hardware-Tinkercad%20%7C%20Arduino-FF6F00" alt="Tinkercad and Arduino">
</p>

<p align="center">
  <a href="https://github.com/Subiswas36218/MDE-CO-06_Data-Acquisition-Technologies-and-Sensor-Networks_Group_Project/actions/workflows/ci.yml">
    <img src="https://github.com/Subiswas36218/MDE-CO-06_Data-Acquisition-Technologies-and-Sensor-Networks_Group_Project/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI workflow">
  </a>
  <a href="https://github.com/Subiswas36218/MDE-CO-06_Data-Acquisition-Technologies-and-Sensor-Networks_Group_Project/actions/workflows/arduino-firmware.yml">
    <img src="https://github.com/Subiswas36218/MDE-CO-06_Data-Acquisition-Technologies-and-Sensor-Networks_Group_Project/actions/workflows/arduino-firmware.yml/badge.svg?branch=main" alt="Arduino firmware workflow">
  </a>
</p>

An Arduino-based, three-slot parking-space monitoring prototype that acquires distance measurements from Parallax PING))) ultrasonic sensors, classifies each slot as **OCCUPIED**, **VACANT**, or **UNKNOWN**, and makes the captured readings available for analysis with Python.

> **Project status:** Educational prototype / data-acquisition project. The workflows included in this repository validate Python code, notebook structure and Arduino firmware compilation. They do not verify physical sensor calibration or prove that the Tinkercad simulation matches real-world performance.

## Contents

- [Overview](#overview)
- [System architecture](#system-architecture)
- [Hardware](#hardware)
- [Technology stack](#technology-stack)
- [Repository layout](#repository-layout)
- [Getting started](#getting-started)
- [Firmware and serial data](#firmware-and-serial-data)
- [Data analysis notebook](#data-analysis-notebook)
- [GitHub Actions](#github-actions)
- [Testing and validation](#testing-and-validation)
- [Limitations](#limitations)
- [Contributing](#contributing)

## Overview

The system monitors three parking slots using one ultrasonic sensor per slot. The Arduino reads the sensors, applies distance-based occupancy logic and controls red/green LED indicators. Serial output provides a row-oriented record that can be captured and imported into the Python analysis pipeline.

### Core capabilities

- Three independent parking-slot distance measurements.
- Slot classification into `OCCUPIED`, `VACANT` and `UNKNOWN`.
- LED indicators for slot state.
- CSV-style serial telemetry from the Arduino.
- Python parsing, validation and storage of captured readings.
- Jupyter-based exploratory analysis and visualisation, including distance distributions, occupancy summaries, sensor comparisons, state transitions and an optional interactive Plotly dashboard.

## Circuit visualisation

The circuit below is the supplied Tinkercad wiring diagram for the three-slot prototype. It shows the Arduino Uno R3, three Parallax PING))) sensors, and the red/green LED indicators on the breadboard.

<p align="center">
  <a href="assets/tinkercad_original/circuit.png">
    <img src="assets/tinkercad_original/circuit.png" alt="Tinkercad circuit: Arduino Uno connected to three Parallax PING ultrasonic sensors and six LED indicators" width="100%">
  </a>
</p>

<sub>Tip: select the circuit image to open the full-resolution version. The accompanying <a href="assets/tinkercad_original/circuit_schematic.pdf">circuit schematic PDF</a>, <a href="assets/tinkercad_original/bom.csv">bill of materials</a>, and <a href="docs/PIN_MAPPING.md">pin-mapping notes</a> are also available in this repository.</sub>

## System architecture

The architecture diagram follows the data from the physical/simulated sensors through Arduino firmware and serial acquisition to the Python analysis and visualisation layer. GitHub renders this Mermaid diagram directly in the README.

```mermaid
flowchart TB
    subgraph HW[Hardware and circuit]
        S1[Slot 1 · PING sensor]
        S2[Slot 2 · PING sensor]
        S3[Slot 3 · PING sensor]
        UNO[Arduino Uno R3]
        LED[3 red + 3 green status LEDs]
        S1 --> UNO
        S2 --> UNO
        S3 --> UNO
        UNO --> LED
    end

    subgraph FW[Firmware · Arduino C++]
        ACQ[Sequential distance acquisition]
        VALID[Echo timeout and validity checks]
        STATE[Occupancy state machine
OCCUPIED · VACANT · UNKNOWN]
        CSV[CSV telemetry at 9600 baud]
        ACQ --> VALID --> STATE --> CSV
    end

    UNO --> ACQ
    STATE --> LED

    subgraph INGEST[Data acquisition paths]
        USB[Physical Arduino USB serial]
        TINK[Tinkercad Serial Monitor
copy output to text capture]
        MON[PySerial monitor]
        IMPORT[Text-capture importer]
        USB --> MON
        TINK --> IMPORT
    end
    CSV --> USB
    CSV --> TINK

    subgraph DATA[Data and analytics · Python]
        STORE[Validated records and CSV storage]
        NOTEBOOK[Jupyter analysis notebook]
        STATS[Statistics and sensor comparisons]
        VIZ[Static plots and interactive Plotly dashboard]
        REPORT[Analysis summaries and exported reports]
        STORE --> NOTEBOOK --> STATS --> VIZ --> REPORT
    end
    MON --> STORE
    IMPORT --> STORE

    subgraph QA[Project quality checks]
        PYCI[GitHub Actions · Python tests and notebook validation]
        ARDUINO[GitHub Actions · Arduino Uno firmware build]
    end
    PYCI -. validates .-> DATA
    ARDUINO -. compiles .-> FW

    classDef hardware fill:#e8f3ff,stroke:#2878b5,color:#123;
    classDef firmware fill:#e9f7ef,stroke:#23834a,color:#123;
    classDef ingest fill:#fff4df,stroke:#b87916,color:#321;
    classDef analytics fill:#f2eaff,stroke:#8152b5,color:#213;
    classDef quality fill:#f2f2f2,stroke:#777,color:#222;
    class S1,S2,S3,UNO,LED hardware;
    class ACQ,VALID,STATE,CSV firmware;
    class USB,TINK,MON,IMPORT ingest;
    class STORE,NOTEBOOK,STATS,VIZ,REPORT analytics;
    class PYCI,ARDUINO quality;
```

### Interactive architecture explorer

Expand a component below to see its responsibility and jump directly to the relevant implementation. The links make this section navigable from GitHub's rendered README; the Mermaid diagram above provides the end-to-end view.

<details>
<summary><strong>1. Hardware and circuit</strong> — three parking slots, sensors and indicators</summary>

- **Inputs:** three Parallax PING))) sensors, one per parking slot.
- **Controller:** Arduino Uno R3.
- **Outputs:** one red (occupied) and one green (vacant) LED per slot. Unknown readings turn both indicators off.
- **Circuit files:** [Tinkercad circuit image](assets/tinkercad_original/circuit.png) · [schematic PDF](assets/tinkercad_original/circuit_schematic.pdf) · [bill of materials](assets/tinkercad_original/bom.csv) · [pin mapping](docs/PIN_MAPPING.md).

</details>

<details>
<summary><strong>2. Firmware and occupancy logic</strong> — acquire, validate, classify and emit telemetry</summary>

- Reads the three sensors sequentially to reduce acoustic cross-talk.
- Treats a missing echo as `UNKNOWN` rather than a valid distance.
- Uses the configured 25 cm occupied and 30 cm vacant thresholds; the band between them retains the previous stable state (hysteresis).
- Emits a CSV header and records over serial at 9600 baud.
- **Implementation:** [Arduino sketch](firmware/IntelligentParkingSystem/IntelligentParkingSystem.ino) · [data format](docs/DATA_FORMAT.md) · [Tinkercad compilation notes](docs/TINKERCAD_COMPILATION_FIX.md).

</details>

<details>
<summary><strong>3. Data acquisition and import</strong> — physical USB or Tinkercad capture</summary>

- **Physical board:** PySerial reads the Arduino USB serial stream and appends validated records to the project CSV.
- **Tinkercad:** copy Serial Monitor output to a text file, then import the captured lines. Tinkercad's simulated serial monitor is not normally exposed as a host USB serial port.
- **Implementation:** [serial monitor](python/src/parking_monitor/monitor.py) · [capture importer](python/src/parking_monitor/import_capture.py) · [protocol parser](python/src/parking_monitor/protocol.py) · [CSV storage](python/src/parking_monitor/storage.py).

</details>

<details>
<summary><strong>4. Analytics and visualisation</strong> — inspect sensor readings and parking states</summary>

- The analysis module generates summary statistics and plots from captured CSV data.
- The notebooks add slot comparisons, distance distributions, state transitions and an optional interactive Plotly dashboard.
- **Implementation:** [analysis module](python/src/parking_monitor/analyze.py) · [notebooks directory](notebooks/) · [experiment and reporting guide](docs/EXPERIMENTS_AND_REPORT.md).

</details>

<details>
<summary><strong>5. Automated validation</strong> — Python CI and Arduino firmware compilation</summary>

- **Python CI:** runs tests and validates notebook structure.
- **Arduino build:** compiles the sketch for the Arduino Uno (`arduino:avr:uno`).
- **Workflows:** [Python CI workflow](.github/workflows/ci.yml) · [Arduino firmware workflow](.github/workflows/arduino-firmware.yml).

</details>

## Hardware

| Component | Quantity | Purpose |
|---|---:|---|
| Arduino Uno R3 | 1 | Main controller |
| Parallax PING))) ultrasonic sensor | 3 | Distance measurement for each slot |
| Red LED | 3 | Occupancy indicator |
| Green LED | 3 | Vacancy indicator |
| 220 Ω resistor | 6 | LED current limiting |
| Breadboard | 1 | Prototyping and connections |
| Jumper wires | As required | Electrical connections |

The project circuit and bill of materials are retained in `assets/tinkercad_original/` where present.

### Sensor note

This project uses **Parallax PING)))** sensors. Each sensor uses one bidirectional signal pin for trigger and echo; it is not wired or read like a four-pin HC-SR04 module.

The signal-pin mapping inferred from the supplied circuit drawing is:

| Slot | PING))) signal pin |
|---|---:|
| Slot 1 | D7 |
| Slot 2 | D4 |
| Slot 3 | D2 |

The LED pin mapping inferred from the drawing is:

| Slot | Red LED | Green LED |
|---|---:|---:|
| Slot 1 | D12 | D13 |
| Slot 2 | D10 | D11 |
| Slot 3 | A0 | D9 |

**Verify these pin assignments against the actual circuit/netlist before wiring physical hardware.** They are visual inferences from the drawing, not a machine-verified netlist.

## Technology stack

| Layer | Technologies |
|---|---|
| Microcontroller | Arduino Uno R3 |
| Firmware | Arduino C++ |
| Distance sensing | Parallax PING))) ultrasonic sensors |
| Simulation / circuit design | Tinkercad Circuits |
| Data acquisition | Arduino Serial |
| Serial interface (physical board) | PySerial |
| Data processing | Python, Pandas, NumPy |
| Visualisation | Matplotlib, Seaborn, Plotly (optional) |
| Statistical analysis | SciPy (where used by the analysis environment) |
| Notebooks | JupyterLab, IPython, nbformat |
| Testing | pytest |
| Continuous integration | GitHub Actions |
| Firmware build validation | Arduino CLI + Arduino AVR core |

## Repository layout

The paths below describe the intended project organisation. Some folders may be absent in a checkout if their files have not yet been added.

```text
.
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── arduino-firmware.yml
├── assets/
│   └── tinkercad_original/
├── data/
├── docs/
├── firmware/
│   └── IntelligentParkingSystem/
│       └── IntelligentParkingSystem.ino
├── notebooks/
│   ├── parking_data_visualization.ipynb
│   └── parking_data_visualization_updated.ipynb
├── python/
│   └── src/
│       └── parking_monitor/
├── reports/
├── tests/
├── requirements.txt
└── README.md
```

## Getting started

### Prerequisites

- Python 3.12 or later
- Git
- JupyterLab or the VS Code Jupyter extension
- Arduino IDE or Arduino CLI for firmware upload/build
- Arduino Uno and the listed components for physical testing

### 1. Clone the repository

```bash
git clone https://github.com/Subiswas36218/MDE-CO-06_Data-Acquisition-Technologies-and-Sensor-Networks_Group_Project.git
cd REPOSITORY
```

Replace `Subiswas36218/MDE-CO-06_Data-Acquisition-Technologies-and-Sensor-Networks_Group_Project` with the actual GitHub path.

### 2. Create and activate a virtual environment

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 3. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

If the repository keeps its Python package under `python/` and has a `pyproject.toml`, install it in editable mode as well:

```bash
python -m pip install -e ./python
```

If no `pyproject.toml` exists, use the repository's documented `PYTHONPATH` or run the scripts from the configured project environment.

### 4. Open the notebook

```bash
jupyter lab notebooks/parking_data_visualization_updated.ipynb
```

If only the original notebook is present, open that file instead. Run the notebook from the repository root so relative data and report paths resolve as intended.

## Firmware and serial data

1. Open `firmware/IntelligentParkingSystem/IntelligentParkingSystem.ino` in Arduino IDE.
2. Select **Arduino Uno** and the correct serial port.
3. Compile and upload the sketch.
4. Open Serial Monitor at the baud rate configured by the firmware (expected project setting: `9600`).
5. Confirm that the serial header and subsequent records are emitted.
6. Test all three slots at multiple distances and check LED/state behavior.

The expected telemetry schema is:

```text
arduino_timestamp_ms,slot1_distance_cm,slot1_status,slot2_distance_cm,slot2_status,slot3_distance_cm,slot3_status,occupied_count,vacant_count,unknown_count
```

A sensor timeout/no-echo reading should remain distinguishable from a real distance measurement. Do not silently convert missing readings into occupied or vacant observations.

### Tinkercad capture

Tinkercad's simulated Serial Monitor is not normally exposed as a USB serial device to the host operating system. For a Tinkercad run, copy the Serial Monitor output into a text capture file and use the project's capture importer, if present. For a physical Arduino connected over USB, the PySerial-based acquisition path can be used.

Example importer command (adjust the module path if your checkout differs):

```bash
python -m parking_monitor.import_capture data/tinkercad_capture.txt \
  --output data/parking_data.csv
```

Do not treat illustrative or synthetic fallback data as experimental measurements.

## Data analysis notebook

The advanced notebook is designed to extend the original exploratory analysis with additional views, such as:

- Overall occupied / vacant / unknown composition.
- Per-sensor distance distributions and violin plots.
- Moving-average distance trends.
- Correlation between sensor distance readings.
- Mean distance with standard-deviation error bars.
- State-transition timelines and transition matrices.
- IQR-based candidate outlier inspection.
- Interactive Plotly distance dashboard (optional).
- Normalized slot-indicator radar chart.

Install optional interactive plotting support if needed:

```bash
python -m pip install plotly
```

If Plotly cannot render inside the notebook, the notebook can save an HTML dashboard for opening in a browser. Ensure `nbformat` and `ipython` are installed in the same virtual environment as the Jupyter kernel:

```bash
python -m pip install --upgrade nbformat ipython
```

## GitHub Actions

Two workflow files are included under `.github/workflows/`.

### Python and notebook CI

`ci.yml` runs on pushes and pull requests to `main` and `develop`. It:

- Sets up Python 3.12.
- Installs `requirements.txt`.
- Runs pytest when a `tests/` directory exists.
- Validates notebook JSON/structure with `nbformat` when notebooks are present.

### Arduino firmware build

`arduino-firmware.yml` runs on pushes and pull requests and manually via **Actions → Arduino Firmware Build → Run workflow**. It installs Arduino CLI, installs the Arduino AVR core and compiles the Uno sketch.

> GitHub Actions badges show their actual status after these workflow files are committed to this repository and the first run has completed.

## Testing and validation

Run Python tests locally:

```bash
python -m pytest -q
```

Validate notebook files locally:

```bash
python -m pip install nbformat
python - <<'PY'
from pathlib import Path
import nbformat

for path in Path("notebooks").glob("*.ipynb"):
    nbformat.validate(nbformat.read(path, as_version=4))
    print(f"Valid notebook: {path}")
PY
```

Compile firmware locally with Arduino CLI:

```bash
arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli compile --fqbn arduino:avr:uno \
  firmware/IntelligentParkingSystem
```

## Limitations

- A successful CI build checks source/build validity; it does not validate sensor readings or physical wiring.
- Pin mappings inferred from a diagram must be checked before connecting real hardware.
- Ultrasonic readings depend on sensor orientation, target surface, environmental conditions and sensor cross-talk.
- Occupancy thresholds and hysteresis should be calibrated experimentally for the intended parking geometry.
- Tinkercad simulation output and physical USB serial acquisition are different collection paths.
- Synthetic fallback data is useful for demonstrating notebook functionality, not for drawing experimental conclusions.
- The project is a prototype, not a certified parking-control or safety system.

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-change`.
3. Add or update tests for Python changes.
4. Validate notebook structure and compile firmware when relevant.
5. Commit your changes and open a pull request.

Please include the hardware/simulation setup and data provenance when contributing measurements or screenshots.

---

<p align="center">
  Built as an educational data-acquisition and sensor-network project.
</p>
