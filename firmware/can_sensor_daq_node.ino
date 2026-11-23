/*
 * Embedded DAQ Node Firmware (ESP32 / Arduino)
 * Reads CAN-Bus ECU parameters (RPM, Speed) + Peripheral Sensors (Temp, Current, Voltage)
 * Outputs synchronized CSV telemetry over Serial at 10Hz
 */

#include <SPI.h>
#include <mcp2515.h>
#include "max6675.h"

// Pin Definitions
const int CAN_CS_PIN = 5;
const int THERMO_SO = 19;
const int THERMO_CS = 23;
const int THERMO_CLK = 18;
const int CURRENT_SENSOR_PIN = 34;
const int VOLTAGE_SENSOR_PIN = 35;

MCP2515 mcp2515(CAN_CS_PIN);
MAX6675 thermocouple(THERMO_CLK, THERMO_CS, THERMO_SO);
struct can_frame canMsg;

// Telemetry Variables
int vehicle_rpm = 0;
int vehicle_speed_kmh = 0;
float component_temp_c = 0.0;
float battery_current_a = 0.0;
float battery_voltage_v = 48.0;

unsigned long lastSampleTime = 0;
const unsigned long sampleInterval = 100; // 100ms = 10Hz

void setup() {
  Serial.begin(115200);
  
  // Initialize CAN Bus at 500kbps (Standard Automotive OBD-II)
  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  
  Serial.println("TIMESTAMP_MS,SPEED_KMH,RPM,TEMP_C,CURRENT_A,VOLTAGE_V");
}

void loop() {
  // 1. Read incoming CAN frames from Vehicle ECU
  if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    if (canMsg.can_id == 0x7E8) { // Standard OBD-II Response ID
      uint8_t pid = canMsg.data[2];
      if (pid == 0x0C) { // Engine/Motor RPM
        vehicle_rpm = ((canMsg.data[3] * 256) + canMsg.data[4]) / 4;
      } else if (pid == 0x0D) { // Vehicle Speed
        vehicle_speed_kmh = canMsg.data[3];
      }
    }
  }

  // 2. Sample Peripheral Sensors & Transmit at fixed 10Hz interval
  if (millis() - lastSampleTime >= sampleInterval) {
    lastSampleTime = millis();

    // Read K-Type Thermocouple
    component_temp_c = thermocouple.readCelsius();

    // Read Hall-Effect Current Sensor (Calibrated for 30A/150A module)
    int rawCurrent = analogRead(CURRENT_SENSOR_PIN);
    float voltageOut = (rawCurrent / 4095.0) * 3.3;
    battery_current_a = (voltageOut - 1.65) / 0.022;

    // Read Voltage Divider for Pack Voltage
    int rawVoltage = analogRead(VOLTAGE_SENSOR_PIN);
    battery_voltage_v = ((rawVoltage / 4095.0) * 3.3) * 18.0;

    // Output Synchronized Data Frame
    Serial.print(lastSampleTime); Serial.print(",");
    Serial.print(vehicle_speed_kmh); Serial.print(",");
    Serial.print(vehicle_rpm); Serial.print(",");
    Serial.print(component_temp_c, 2); Serial.print(",");
    Serial.print(battery_current_a, 2); Serial.print(",");
    Serial.println(battery_voltage_v, 2);
  }
}
