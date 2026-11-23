import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_validation_report(csv_path="data/simulated_idc_test_log.csv"):
    if not os.path.exists(csv_path):
        print(f"[ERROR] Log file not found: {csv_path}. Run drive_cycle_simulator.py first.")
        return

    df = pd.read_csv(csv_path)
    df["TIME_SEC"] = df["TIMESTAMP_MS"] / 1000.0

    # Summary Metrics
    max_speed = df["SPEED_KMH"].max()
    peak_temp = df["TEMP_C"].max()
    peak_current = df["CURRENT_A"].max()
    min_voltage = df["VOLTAGE_V"].min()
    fault_records = df[df["DIAGNOSTIC_STATUS"] != "OK"]

    print("\n" + "="*50)
    print(" POWERTRAIN CHASSIS DYNO VALIDATION SUMMARY")
    print("="*50)
    print(f"Total Samples Logged   : {len(df)}")
    print(f"Max Vehicle Speed      : {max_speed} km/h")
    print(f"Peak Component Temp    : {peak_temp} °C")
    print(f"Peak Current Draw      : {peak_current} A")
    print(f"Minimum Pack Voltage   : {min_voltage} V")
    print(f"Fault Events Detected  : {len(fault_records)}")
    if not fault_records.empty:
        print(f"Fault Types Triggered  : {fault_records['DIAGNOSTIC_STATUS'].unique().tolist()}")
    print("="*50 + "\n")

    # Generate Multi-Panel Engineering Plot
    os.makedirs("reports", exist_ok=True)
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    # Plot 1: Drive Cycle Speed & RPM
    axs[0].plot(df["TIME_SEC"], df["SPEED_KMH"], color="tab:blue", label="Speed (km/h)")
    axs[0].set_ylabel("Speed (km/h)")
    axs[0].set_title("Chassis Dyno Validation: IDC Drive Cycle Telemetry")
    axs[0].grid(True, linestyle="--", alpha=0.6)
    axs[0].legend(loc="upper left")

    # Plot 2: Thermal Profile with Threshold Line
    axs[1].plot(df["TIME_SEC"], df["TEMP_C"], color="tab:red", label="Component Temp (°C)")
    axs[1].axhline(115.0, color="black", linestyle="--", label="Max Thermal Limit (115°C)")
    axs[1].set_ylabel("Temp (°C)")
    axs[1].grid(True, linestyle="--", alpha=0.6)
    axs[1].legend(loc="upper left")

    # Plot 3: Electrical Load (Current & Voltage)
    axs[2].plot(df["TIME_SEC"], df["CURRENT_A"], color="tab:green", label="Current (A)")
    axs[2].plot(df["TIME_SEC"], df["VOLTAGE_V"], color="tab:orange", label="Voltage (V)")
    axs[2].set_ylabel("Electrical")
    axs[2].set_xlabel("Test Time (seconds)")
    axs[2].grid(True, linestyle="--", alpha=0.6)
    axs[2].legend(loc="upper left")

    plt.tight_layout()
    plot_path = "reports/dyno_validation_plots.png"
    plt.savefig(plot_path, dpi=300)
    print(f"[SUCCESS] Engineering validation plot saved to: {plot_path}")

if __name__ == "__main__":
    generate_validation_report()
  
