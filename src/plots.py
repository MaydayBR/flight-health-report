# Create graphs and save them as PNG files in reports/
    # Battery vs time
    # GPS satellites vs time
    # Vibration vs time
    # Altitude and target altitude vs time

import os
import matplotlib.pyplot as plt


def generate_plots(df, output_dir="reports"):
    
    # Ensure the reports directory exists
    os.makedirs(output_dir, exist_ok=True)

    time = df["timestamp_s"]

    # -----------------------------
    # Battery vs Time
    # -----------------------------
    plt.figure()
    plt.plot(time, df["battery_v"])
    plt.xlabel("Time (s)")
    plt.ylabel("Battery Voltage (V)")
    plt.title("Battery Voltage vs Time")
    plt.grid(True)

    plt.savefig(f"{output_dir}/battery.png")
    plt.close()

    # -----------------------------
    # GPS Satellites vs Time
    # -----------------------------
    plt.figure()
    plt.plot(time, df["gps_sats"])
    plt.xlabel("Time (s)")
    plt.ylabel("GPS Satellites")
    plt.title("GPS Satellites vs Time")
    plt.grid(True)

    plt.savefig(f"{output_dir}/gps.png")
    plt.close()

    # -----------------------------
    # Vibration vs Time
    # -----------------------------
    plt.figure()
    plt.plot(time, df["vibe"])
    plt.xlabel("Time (s)")
    plt.ylabel("Vibration")
    plt.title("Vibration vs Time")
    plt.grid(True)

    plt.savefig(f"{output_dir}/vibration.png")
    plt.close()

    # -----------------------------
    # Altitude vs Target Altitude
    # -----------------------------
    plt.figure()
    plt.plot(time, df["altitude_m"], label="Altitude")
    plt.plot(time, df["target_altitude_m"], label="Target Altitude")

    plt.xlabel("Time (s)")
    plt.ylabel("Altitude (m)")
    plt.title("Altitude vs Target Altitude")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"{output_dir}/altitude.png")
    plt.close()