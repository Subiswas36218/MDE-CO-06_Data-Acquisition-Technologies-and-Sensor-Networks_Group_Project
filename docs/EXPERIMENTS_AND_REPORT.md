# Laboratory experiments and report plan

## Suggested report structure

1. Introduction and problem statement
2. Objectives and system requirements
3. Theoretical background: ultrasonic time-of-flight, pulse timing and distance conversion
4. Hardware description and circuit schematic
5. Arduino firmware and sensor acquisition
6. USB serial protocol and Python data acquisition
7. Experimental methodology
8. Results and discussion
9. Error sources, limitations and future improvements
10. Conclusion
11. Appendix: complete Arduino and Python source code

## Recommended experiments

### Experiment 1 — Empty-bay baseline

Keep all three bays empty. Record distance and status for each slot. Confirm that the sensors see a stable background distance and that the green LEDs illuminate once valid readings exceed the vacant threshold.

### Experiment 2 — Single-slot detection

Place a vehicle-shaped object in Slot 1, then Slot 2, then Slot 3. Record the distance and confirm that only the corresponding red LED is active.

### Experiment 3 — Multiple occupancy combinations

Test combinations such as 1 occupied / 2 vacant, 2 occupied / 1 vacant and all 3 occupied. Compare the hardware indicators, Arduino counts and Python console output.

### Experiment 4 — Threshold and hysteresis test

Move a target gradually across the 25 cm and 30 cm decision thresholds. Observe whether the retained state in the 25–30 cm band reduces rapid status switching. Tune thresholds to the geometry of the model.

### Experiment 5 — Repeatability and measurement error

Place a flat target at a known reference distance. Capture at least 30 valid readings. Calculate mean, standard deviation and absolute error:

- Mean: `mean = sum(readings) / N`
- Sample standard deviation: `s = sqrt(sum((x_i - mean)^2) / (N - 1))`
- Absolute error: `abs(measured_mean - reference_distance)`

Do not claim an accuracy value until you have collected measurements against a known reference distance.

### Experiment 6 — Data acquisition and integrity

Run the Python serial receiver, confirm that every valid Arduino row is appended to CSV, then run the analysis module. Compare record counts and status totals with the serial output.

## Report evidence to collect

- Screenshot of the complete Tinkercad circuit.
- Screenshot of each sensor and LED wiring area.
- Arduino Serial Monitor showing the CSV header and live records.
- Python terminal output showing slot status and counts.
- The actual CSV dataset generated from your experiment.
- Plots produced by `parking_monitor.analyze`.
- A table of known reference distances versus measured values.

**Academic integrity:** clearly distinguish simulated readings, illustrative examples and physical measurements. Do not present sample/test data as experimental results.
