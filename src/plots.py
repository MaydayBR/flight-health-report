# Plots (internal name -> ArduPilot source):
#   altitude vs time   <- altitude_m (BARO/AHR2/POS/QTUN.Alt)
#   battery vs time    <- battery_v (BAT/CURR.Volt)
#   roll/pitch vs time <- roll_deg, pitch_deg (ATT/AHR2)
#   vibration vs time  <- vibe (VIBE magnitude)
#   GPS path           <- gps_lat, gps_lng (GPS/POS)

import os
import numpy as np
import matplotlib.pyplot as plt


def _has_data(df, col):
    return col in df.columns and df[col].notna().any()


def _placeholder_figure(output_path, title):
    """Create a placeholder figure when no data is available."""
    plt.figure()
    plt.text(0.5, 0.5, f"No data: {title}", ha="center", va="center", fontsize=14)
    plt.axis("off")
    plt.savefig(output_path)
    plt.close()


def generate_plots(df, output_dir="reports"):
    os.makedirs(output_dir, exist_ok=True)
    time = df["timestamp_s"]

    # Altitude vs Time
    if _has_data(df, "altitude_m"):
        plt.figure()
        plt.plot(time, df["altitude_m"], label="Altitude")
        if _has_data(df, "target_altitude_m"):
            plt.plot(time, df["target_altitude_m"], label="Target Altitude")
        plt.xlabel("Time (s)")
        plt.ylabel("Altitude (m)")
        plt.title("Altitude vs Time")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{output_dir}/altitude.png")
        plt.close()

    # Battery vs Time
    if _has_data(df, "battery_v"):
        plt.figure()
        plt.plot(time, df["battery_v"])
        plt.xlabel("Time (s)")
        plt.ylabel("Battery Voltage (V)")
        plt.title("Battery vs Time")
        plt.grid(True)
        plt.savefig(f"{output_dir}/battery.png")
        plt.close()

    # Roll/Pitch vs Time
    if _has_data(df, "roll_deg") or _has_data(df, "pitch_deg"):
        plt.figure()
        if _has_data(df, "roll_deg"):
            plt.plot(time, df["roll_deg"], label="Roll")
        if _has_data(df, "pitch_deg"):
            plt.plot(time, df["pitch_deg"], label="Pitch")
        plt.xlabel("Time (s)")
        plt.ylabel("Angle (deg)")
        plt.title("Roll/Pitch vs Time")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{output_dir}/roll_pitch.png")
        plt.close()

    # Vibration vs Time
    if _has_data(df, "vibe"):
        plt.figure()
        plt.plot(time, df["vibe"])
        plt.xlabel("Time (s)")
        plt.ylabel("Vibration")
        plt.title("Vibration vs Time")
        plt.grid(True)
        plt.savefig(f"{output_dir}/vibration.png")
        plt.close()

    # GPS Path (lat vs lng)
    if _has_data(df, "gps_lat") and _has_data(df, "gps_lng"):
        lat = df["gps_lat"].dropna()
        lng = df["gps_lng"].dropna()
        # Align by index
        idx = lat.index.intersection(lng.index)
        if len(idx) > 0:
            lat = df.loc[idx, "gps_lat"]
            lng = df.loc[idx, "gps_lng"]
            plt.figure()
            plt.plot(lng, lat)
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            plt.title("GPS Path")
            plt.grid(True)
            plt.axis("equal")
            plt.savefig(f"{output_dir}/gps_path.png")
            plt.close()

    # GPS Satellites vs Time (kept for compatibility)
    if _has_data(df, "gps_sats"):
        plt.figure()
        plt.plot(time, df["gps_sats"])
        plt.xlabel("Time (s)")
        plt.ylabel("GPS Satellites")
        plt.title("GPS Satellites vs Time")
        plt.grid(True)
        plt.savefig(f"{output_dir}/gps.png")
        plt.close()