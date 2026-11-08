# Hardware pin mapping

This table is a **visual interpretation of the supplied Tinkercad circuit PNG and one-page PDF schematic**. It is not a machine-generated netlist. Verify each endpoint in the live Tinkercad design before uploading firmware.

## Sensor SIG pins

| Parking bay (left to right in the circuit image) | Tinkercad label | Arduino Uno pin |
|---|---|---:|
| Slot 1 | PING3 / left sensor | D7 |
| Slot 2 | PING2 / centre sensor | D4 |
| Slot 3 | PING1 / right sensor | D2 |

All three PING))) modules share 5V and GND. Each module's SIG pin is a single bidirectional trigger/echo connection.

## LED pins

| Slot | Red LED (occupied) | Green LED (vacant) | Resistor |
|---|---:|---:|---:|
| Slot 1 | D12 | D13 | 220 ohm per LED |
| Slot 2 | D10 | D11 | 220 ohm per LED |
| Slot 3 | A0 used as a digital output | D9 | 220 ohm per LED |

A0 on an Arduino Uno can be used as a digital GPIO pin as well as an analogue input. This project uses it as a digital LED output, matching the apparent brown wire in the supplied circuit image.

## How this mapping was read

- The board header in the PNG shows three blue signal wires at the D7, D4 and D2 positions.
- The other visible output wires appear at D13, D12, D11, D10, D9 and A0.
- The breadboard groups one red and one green indicator per parking bay.
- The schematic labels the sensors PING3, PING2 and PING1 from left to right.

If your live Tinkercad endpoints differ, change `PING_PINS`, `RED_LED_PINS` and `GREEN_LED_PINS` near the top of `firmware/IntelligentParkingSystem/IntelligentParkingSystem.ino`.
