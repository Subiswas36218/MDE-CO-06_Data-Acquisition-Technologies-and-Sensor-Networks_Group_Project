/*
  Intelligent Parking Space Monitoring System
  Tinkercad-compatible firmware for Arduino Uno R3
  Sensors: 3 x Parallax PING))) ultrasonic distance sensors
  Indicators: 3 red LEDs (occupied), 3 green LEDs (vacant)
  Serial protocol: CSV at 9600 baud

  Pin mapping inferred from the supplied Tinkercad circuit export:
    PING))) SIG pins, left/centre/right: D7, D4, D2
    Slot 1 red/green LEDs: D12/D13
    Slot 2 red/green LEDs: D10/D11
    Slot 3 red/green LEDs: A0/D9 (A0 is digital pin 14 on Uno)

  Tinkercad compatibility notes:
  - Keep this as the ONLY sketch in the Tinkercad code editor.
  - This version intentionally avoids custom enums, uint8_t, structs,
    and helper functions because Tinkercad's sketch preprocessor may
    generate prototypes before those custom types are declared.
  - Arduino automatically provides the core declarations; no Arduino.h
    include is needed in a normal .ino sketch.
*/

const int SLOT_COUNT = 3;

const int PING_PINS[SLOT_COUNT] = {7, 4, 2};
const int RED_LED_PINS[SLOT_COUNT] = {12, 10, 14};  // A0 = digital pin 14
const int GREEN_LED_PINS[SLOT_COUNT] = {13, 11, 9};

const int STATUS_UNKNOWN = 0;
const int STATUS_OCCUPIED = 1;
const int STATUS_VACANT = 2;

const float OCCUPIED_THRESHOLD_CM = 25.0;
const float VACANT_THRESHOLD_CM = 30.0;

const unsigned long ECHO_TIMEOUT_US = 19000UL;
const unsigned long INTER_SENSOR_GAP_MS = 60UL;
const unsigned long SCAN_INTERVAL_MS = 300UL;

float slotDistanceCm[SLOT_COUNT] = {-1.0, -1.0, -1.0};
int slotStatus[SLOT_COUNT] = {
  STATUS_UNKNOWN, STATUS_UNKNOWN, STATUS_UNKNOWN
};

void setup() {
  int i;

  for (i = 0; i < SLOT_COUNT; i++) {
    pinMode(PING_PINS[i], INPUT);
    pinMode(RED_LED_PINS[i], OUTPUT);
    pinMode(GREEN_LED_PINS[i], OUTPUT);

    digitalWrite(RED_LED_PINS[i], LOW);
    digitalWrite(GREEN_LED_PINS[i], LOW);
  }

  Serial.begin(9600);
  delay(250);

  Serial.println(F(
    "arduino_timestamp_ms,"
    "slot1_distance_cm,slot1_status,"
    "slot2_distance_cm,slot2_status,"
    "slot3_distance_cm,slot3_status,"
    "occupied_count,vacant_count,unknown_count"
  ));
}

void loop() {
  int i;
  int occupiedCount = 0;
  int vacantCount = 0;
  int unknownCount = 0;

  // Acquire each PING))) sensor sequentially.
  for (i = 0; i < SLOT_COUNT; i++) {
    int signalPin = PING_PINS[i];
    unsigned long echoDuration;
    float distanceCm;

    // PING))) uses the same SIG pin for trigger and echo.
    pinMode(signalPin, OUTPUT);
    digitalWrite(signalPin, LOW);
    delayMicroseconds(2);
    digitalWrite(signalPin, HIGH);
    delayMicroseconds(5);
    digitalWrite(signalPin, LOW);

    pinMode(signalPin, INPUT);
    echoDuration = pulseIn(signalPin, HIGH, ECHO_TIMEOUT_US);

    if (echoDuration == 0) {
      distanceCm = -1.0;
      slotStatus[i] = STATUS_UNKNOWN;
    } else {
      distanceCm = (echoDuration * 0.0343) / 2.0;

      // Hysteresis: retain the previous stable state between 25 and 30 cm.
      if (distanceCm <= OCCUPIED_THRESHOLD_CM) {
        slotStatus[i] = STATUS_OCCUPIED;
      } else if (distanceCm >= VACANT_THRESHOLD_CM) {
        slotStatus[i] = STATUS_VACANT;
      }
      // If distance is in the hysteresis band, keep the previous status.
    }

    slotDistanceCm[i] = distanceCm;

    // Drive the two indicators for this parking slot.
    if (slotStatus[i] == STATUS_OCCUPIED) {
      digitalWrite(RED_LED_PINS[i], HIGH);
      digitalWrite(GREEN_LED_PINS[i], LOW);
      occupiedCount++;
    } else if (slotStatus[i] == STATUS_VACANT) {
      digitalWrite(RED_LED_PINS[i], LOW);
      digitalWrite(GREEN_LED_PINS[i], HIGH);
      vacantCount++;
    } else {
      digitalWrite(RED_LED_PINS[i], LOW);
      digitalWrite(GREEN_LED_PINS[i], LOW);
      unknownCount++;
    }

    // Separate pings to reduce acoustic cross-talk.
    if (i < SLOT_COUNT - 1) {
      delay(INTER_SENSOR_GAP_MS);
    }
  }

  // Emit one ten-field CSV record for the Python capture importer.
  Serial.print(millis());

  for (i = 0; i < SLOT_COUNT; i++) {
    Serial.print(',');
    if (slotDistanceCm[i] < 0.0) {
      Serial.print(-1.0, 2);
    } else {
      Serial.print(slotDistanceCm[i], 2);
    }

    Serial.print(',');
    if (slotStatus[i] == STATUS_OCCUPIED) {
      Serial.print(F("OCCUPIED"));
    } else if (slotStatus[i] == STATUS_VACANT) {
      Serial.print(F("VACANT"));
    } else {
      Serial.print(F("UNKNOWN"));
    }
  }

  Serial.print(',');
  Serial.print(occupiedCount);
  Serial.print(',');
  Serial.print(vacantCount);
  Serial.print(',');
  Serial.println(unknownCount);

  delay(SCAN_INTERVAL_MS);
}
