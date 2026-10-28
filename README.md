# COT Data Pipeline – Soybeans Positioning

An automated ETL pipeline that fetches weekly Commitments of Traders (COT) data from the CFTC, calculates positioning metrics and stores them in a SQLite database.

COT data shows how different groups of traders are positioned in futures markets. The positioning of speculators (Non-Commercials) versus hedgers (Commercials) is widely used as an indicator of market sentiment. This project currently focuses on Soybeans traded at the Chicago Board of Trade.

This is a hand-coded learning project, built step by step to develop practical skills in Python, pandas and SQL.

## Features

- Fetches the latest data from the CFTC public API, with a timeout and automatic retries on failure
- Converts raw API values into correct data types (numbers and dates)
- Calculates net positions of Non-Commercials and Commercials, and Non-Commercial net positioning as a share of open interest
- Idempotent loading: a primary key and a duplicate check ensure that only new weeks are written to the database
- Logs every run with timestamps to a log file
- Modular structure following the Extract–Transform–Load pattern
- Path handling independent of where the pipeline is started

## Data Source

- **Provider:** U.S. Commodity Futures Trading Commission (CFTC), Public Reporting Environment
- **Report:** Legacy, Futures Only (dataset `6dca-aqww`)
- **Market:** Soybeans – Chicago Board of Trade (contract market code `005602`)
- **Frequency:** weekly, positions as of Tuesday, published on Friday

## Project Structure

```
modules/
├── config.py      # settings: API parameters, column lists, paths, retry options
├── extract.py     # fetches data from the CFTC API
├── transform.py   # converts data types, calculates metrics, selects columns
├── load.py        # writes new rows to the SQLite database
└── main.py        # sets up logging and runs the pipeline
```

The folders `data/` and `logs/` are created automatically on the first run and are not part of the repository.

## Getting Started

```
pip install -r requirements.txt
python modules/main.py
```

After a run, the database is located at `data/processed/cot_cleandata.db` and the log file at `logs/status.log`.

## Roadmap

- Extend the pipeline to multiple markets
- SQL queries for analysis directly on the database
- Charts with matplotlib
- COT Index as a positioning indicator using NumPy
- Scheduled weekly execution

## Versions

- `v0.1` – first working API pipeline
- `v0.2` – pipeline split into functions
- `v0.3` – error handling and retries
- `v0.4` – logging
- `v0.5` – modular structure