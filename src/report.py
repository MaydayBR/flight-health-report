import os
import math


def _format_value(v):
    """Format a metric value for display; use 'N/A' for NaN or None."""
    if v is None:
        return "N/A"
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return "N/A"
    return str(v)


def generate_html_report(metrics, health_results, template_path, output_path):
    with open(template_path, "r") as file:
        html = file.read()

    replacements = {
        "{{ score }}": _format_value(health_results["overall_score"]),
        "{{ overall_status }}": str(health_results["overall_status"]),

        "{{ flight_duration_s }}": _format_value(metrics["flight_duration_s"]),
        "{{ altitude_max_m }}": _format_value(metrics.get("altitude_max_m")),
        "{{ battery_min_v }}": _format_value(metrics["battery_min_v"]),
        "{{ vibe_max }}": _format_value(metrics["vibe_max"]),
        "{{ gps_min_sats }}": _format_value(metrics["gps_min_sats"]),
        "{{ gps_avg_sats }}": _format_value(metrics["gps_avg_sats"]),
        "{{ mode_changes }}": _format_value(metrics.get("mode_changes")),
        "{{ altitude_error_mean_abs }}": _format_value(metrics["altitude_error_mean_abs"]),
        "{{ altitude_error_std }}": _format_value(metrics["altitude_error_std"]),

        "{{ battery_status }}": str(health_results["battery_status"]),
        "{{ gps_status }}": str(health_results["gps_status"]),
        "{{ vibe_status }}": str(health_results["vibe_status"]),
        "{{ altitude_status }}": str(health_results["altitude_status"]),
    }

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w") as file:
        file.write(html)