# Serial and CSV data format

The Arduino firmware sends one CSV header at startup and then one row for each scan. Serial speed is **9600 baud**.

## Arduino serial header

```csv
arduino_timestamp_ms,slot1_distance_cm,slot1_status,slot2_distance_cm,slot2_status,slot3_distance_cm,slot3_status,occupied_count,vacant_count,unknown_count
```

Example protocol row (illustrative test data, not a measurement from the user's circuit):

```csv
1250,12.50,OCCUPIED,42.00,VACANT,18.25,OCCUPIED,2,1,0
```

Statuses:

- `OCCUPIED`: valid measured distance at or below 25 cm.
- `VACANT`: valid measured distance at or above 30 cm.
- `UNKNOWN`: the distance falls in the 25–30 cm hysteresis band before a stable state has been established.
- The firmware reports no echo with distance `-1.00` and status `UNKNOWN`.

The 25 cm occupied threshold and 30 cm vacant threshold are starting calibration values, not universal parking standards. Adjust them after testing with the actual mounting geometry. The gap between thresholds prevents flicker close to the decision boundary.

## Python output CSV

The Python logger adds `received_at_utc` and stores the Arduino uptime, all three distances and statuses, and the three summary counts. The generated file is `data/parking_data.csv`.

`unknown_count` is deliberately separate. A sensor timeout is not automatically treated as a confirmed vacant slot, because it may also indicate an alignment, wiring, range or sensor problem.
