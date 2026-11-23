# Standard Operating Procedure (SOP): Chassis Dyno Test Setup & DAQ Validation

## 1. Purpose
To establish a standardized, safe, and repeatable procedure for preparing test vehicles, calibrating Data Acquisition (DAQ) sensors, executing chassis dynamometer drive cycles, and completing post-test validation documentation.

## 2. Pre-Test Safety & Vehicle Preparation
* **Vehicle Restraint:** Verify front/rear wheel chocks and tie-down straps are tensioned and inspected prior to roller engagement.
* **Cooling & Ventilation:** Confirm exhaust extraction hoses (for ICE) and frontal cooling blowers are active and aligned with the radiator/battery pack.
* **Emergency Stop:** Test the cell E-Stop circuit and verify fire suppression equipment is accessible.

## 3. Instrumentation & Sensor Calibration
* **CAN-Bus Interface:** Connect the OBD-II transceiver to the vehicle DLC port; verify 500 kbps baud rate communication and zero bus-off errors.
* **Thermal Sensors:** Verify K-Type thermocouple cold-junction compensation at ambient temperature (±1.0°C tolerance).
* **Current/Voltage Sensors:** Perform zero-current offset calibration prior to powering on the high-voltage/12V powertrain bus.

## 4. Test Execution & Data Logging
1. Launch `daq_logger.py` and confirm live 10Hz data streaming across all channels.
2. Execute warm-up cycle until powertrain fluids reach nominal operating temperature.
3. Initiate the target drive cycle (e.g., IDC) while monitoring real-time diagnostic alerts.

## 5. Post-Test Shutdown & Documentation
* Gradually bring dyno rollers to a complete stop before releasing vehicle restraints.
* Run `report_generator.py` to archive raw CSV logs and attach performance plots to the Test Sign-Off Sheet.
* 
