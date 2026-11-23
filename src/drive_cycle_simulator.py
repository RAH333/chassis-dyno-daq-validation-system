"""
(Allows you to run and demonstrate the entire project on any laptop without hardware connected)
"""
import csv
import json
import os
import random
import numpy as np
from datetime import datetime
from daq_logger import load_thresholds, check_faults

def generate_idc_profile(duration_sec=108):
    """Generates a simplified 108-second Indian Driving Cycle (IDC) speed profile."""
    time_steps = np.arange(0, duration_sec, 0.1) # 10Hz sampling
    speeds = []
    for t in time_steps:
        if t < 15:
            v = 0.0  # Idle
        elif t < 35:
            v = (t - 15) * 1.5  # Acceleration to 30 km/h
        elif t < 60:
            v = 30.0 + np.sin(t) * 2.0  # Cruise
        elif t < 85:
            v = 30.0 + (t - 60) * 1.2  # Highway acceleration to 60 km/h
        else:
            v = max(0.0, 60.0 - (t - 85) * 2.6)  # Deceleration to stop
        speeds.append(round(v, 2))
    return time_steps, speeds

def run_simulation():
    limits = load_thresholds()
    os.makedirs("data", exist_ok=True)
    output_file = "data/simulated_idc_test_log.csv"
    
    time_steps, speeds = generate_idc_profile()
    temp = 35.0
    voltage = 51.2

    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        headers = ["TIMESTAMP_MS", "SPEED_KMH", "RPM", "TEMP_C", "CURRENT_A", "VOLTAGE_V", "DIAGNOSTIC_STATUS"]
        writer.writerow(headers)

        for idx, (t, speed) in enumerate(zip(time_steps, speeds)):
            timestamp_ms = int(t * 1000)
            rpm = int(850 + (speed * 75) + random.uniform(-30, 30)) if speed > 0 else 800
            current = round(5.0 + (speed * 1.8) + random.uniform(-1.5, 2.5), 2)
            
            # Simulate thermal rise under high load & intentional fault injection near peak load
            temp += (current * 0.0025) - 0.03
            if 78 <= t <= 83:
                temp = 117.5  # Simulated thermal spike to validate diagnostic flagging
            
            voltage = round(51.2 - (current * 0.04) - (idx * 0.0005), 2)

            row_dict = {
                "SPEED_KMH": speed,
                "RPM": rpm,
                "TEMP_C": round(temp, 2),
                "CURRENT_A": current,
                "VOLTAGE_V": voltage
            }
            status = check_faults(row_dict, limits)
            writer.writerow([timestamp_ms, speed, rpm, round(temp, 2), current, voltage, status])

    print(f"[SUCCESS] Simulated 108-sec IDC Dyno Run complete. Log saved to: {output_file}")

if __name__ == "__main__":
    run_simulation()
  
