# flight-health-report

Process ArduPilot DataFlash binary logs (`.bin`) to generate flight health reports.

## Setup

```bash
pip install -r requirements.txt
```

Requires `pymavlink` for reading `.bin` logs.

## Usage

```bash
python -m src.main <path/to/flight.bin>
```

Example:

```bash
python -m src.main "data/raw/2021-08-13 13-31-13.bin"
```

Report and plots are written to `reports/`.
