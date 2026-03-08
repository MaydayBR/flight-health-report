import os
import sys

from src.loader import load_flight_data
from src.metrics import compute_metrics
from src.rules import evaluate_health
from src.plots import generate_plots
from src.report import generate_html_report


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <input_bin_file>")
        print("  input_bin_file: path to an ArduPilot DataFlash .bin log")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = "reports"
    report_path = os.path.join(output_dir, "flight_report.html")

    df, extras = load_flight_data(input_file)

    metrics = compute_metrics(df, extras=extras)

    health_results = evaluate_health(metrics)

    generate_plots(df, output_dir=output_dir)

    generate_html_report(
        metrics=metrics,
        health_results=health_results,
        template_path="templates/report.html",
        output_path=report_path
    )

    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()