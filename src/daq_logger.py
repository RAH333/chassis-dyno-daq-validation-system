import serial
import csv
import json
import argparse
import os
from datetime import datetime

def load_thresholds(config_path="config/test_thresholds.json"):
    with open(config_path, "r") as f:
        return json.load(f)["limits"]

def check_faults(row, limits):
    faults = []
    if float(row["TEMP_C"]) > limits["max_motor_exhaust_temp_c"]:
        faults.append("OVER_TEMP")
    if float(row["VOLTAGE_V"]) < limits["min_battery_voltage_v"]:
        faults.append("UNDER_VOLTAGE")
    if float(row["CURRENT_A"]) > limits["max_battery_current_a"]:
        faults.append("OVER_CURRENT")
    if int(row["RPM"]) > limits["max_engine_rpm"]:
        faults.append("OVER_RPM")
    return "|".join(faults) if faults else "OK"

def run_logger(port, baudrate=115200):
    limits = load_thresholds()
    os.makedirs("data", exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/dyno_test_log_{timestamp_str}.csv"

    print(f"[INFO] Connecting to DAQ Node on {port} at {baudrate} baud...")
    ser = serial.Serial(port, baudrate, timeout=1)
    
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        headers = ["TIMESTAMP_MS", "SPEED_KMH", "RPM", "TEMP_C", "CURRENT_A", "VOLTAGE_V", "DIAGNOSTIC_STATUS"]
        writer.writerow(headers)
        print(f"[INFO] Logging started. Saving to {output_file}. Press Ctrl+C to stop.")

        try:
            while True:
                line = ser.readline().decode("utf-8").strip()
                if not line or line.startswith("TIMESTAMP"):
                    continue
                
                parts = line.split(",")
                if len(parts) == 6:
                    row_dict = dict(zip(headers[:6], parts))
                    status = check_faults(row_dict, limits)
                    writer.writerow(parts + [status])
                    
                    if status != "OK":
                        print(f"[FAULT ALERT] Time: {parts[0]}ms | Status: {status} | Temp: {parts[3]}C | Volt: {parts[5]}V")
        except KeyboardInterrupt:
            print(f"\n[INFO] Test stopped by operator. Data saved to {output_file}")
        finally:
            ser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chassis Dyno DAQ Serial Logger")
    parser.add_argument("--port", type=str, required=True, help="Serial COM port (e.g., COM3 or /dev/ttyUSB0)")
    args = parser.parse_args()
    run_logger(args.port)
  
