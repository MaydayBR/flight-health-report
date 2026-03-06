import os


def generate_html_report(metrics, health_results, template_path, output_path):
    with open(template_path, "r") as file:
        html = file.read()

    replacements = {
        "{{ score }}": str(health_results["overall_score"]),
        "{{ overall_status }}": str(health_results["overall_status"]),

        "{{ flight_duration_s }}": str(metrics["flight_duration_s"]),
        "{{ battery_min_v }}": str(metrics["battery_min_v"]),
        "{{ gps_min_sats }}": str(metrics["gps_min_sats"]),
        "{{ gps_avg_sats }}": str(metrics["gps_avg_sats"]),
        "{{ vibe_max }}": str(metrics["vibe_max"]),
        "{{ altitude_error_mean_abs }}": str(metrics["altitude_error_mean_abs"]),
        "{{ altitude_error_std }}": str(metrics["altitude_error_std"]),

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