import requests
import pandas as pd
import sqlite3
from pathlib import Path
import time
import logging

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

API_PARAMS = {"$order":"report_date_as_yyyy_mm_dd DESC",
               "$limit": "52",
               "$where": "market_and_exchange_names = 'SOYBEANS - CHICAGO BOARD OF TRADE'"}
API_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
OBJECTS_TO_INT = ["comm_positions_long_all", "comm_positions_short_all", "traders_noncomm_long_all", "traders_noncomm_short_all", "traders_comm_long_all", "traders_comm_short_all", "noncomm_positions_long_all", "noncomm_positions_short_all", "open_interest_all"]
OBJECTS_TO_DATETIME = ["report_date_as_yyyy_mm_dd"]
DATABASE_PATH = Path("../data/processed/cot_cleandata.db")
TABLE_NAME = "COT_DATA"
RETRY_WAIT_SECONDS = 5
MAX_ATTEMPTS = 3
LOGGING_PATH = Path("../logs/status.log")
def setup_logging(logging_path):
    logging_path.parent.mkdir(parents = True, exist_ok = True)

    logging.basicConfig(
        filename = logging_path,
        level = logging.INFO,
        format = "%(asctime)s | %(levelname)s | %(message)s"
    )

def get_data(url, params):
    response = requests.get(url, params = params, timeout = 15)
    response.raise_for_status()
    cot_df = pd.json_normalize(response.json())
    return cot_df



def transform_data(cot_df, to_int, to_datetime):
    for object_soon_int in to_int:
        cot_df[object_soon_int] = pd.to_numeric(cot_df[object_soon_int])

    for objects_soon_datetime in to_datetime:
        cot_df[objects_soon_datetime] = pd.to_datetime(cot_df[objects_soon_datetime], format="ISO8601")
    return cot_df


def aggregate_data(cot_df):
    cot_df["noncomm_positions_net_all"] = cot_df["noncomm_positions_long_all"] - cot_df["noncomm_positions_short_all"]
    cot_df["comm_positions_net_all"] = cot_df["comm_positions_long_all"] - cot_df["comm_positions_short_all"]
    cot_df["noncomm_positions_net_ratio_to_open_interest"] = cot_df["noncomm_positions_net_all"] / cot_df["open_interest_all"]
    return cot_df

def soybeans_data(cot_df):
    soybeans = (cot_df[["id",
                                      "cftc_contract_market_code",
                                      "market_and_exchange_names",
                                      "report_date_as_yyyy_mm_dd",
                                      "noncomm_positions_net_all",
                                      "comm_positions_net_all",
                                      "noncomm_positions_net_ratio_to_open_interest"]])
    return soybeans

def load_data(soybeans,path, table):
    path.parent.mkdir(parents = True, exist_ok = True)
    conn = sqlite3.connect(path)
    conn.execute(
        (f"CREATE TABLE IF NOT EXISTS {table}(id "
         "TEXT PRIMARY KEY, "
         "cftc_contract_market_code TEXT, "
         "market_and_exchange_names TEXT, "
         "report_date_as_yyyy_mm_dd TEXT, "
         "noncomm_positions_net_all INTEGER, "
         "comm_positions_net_all INTEGER, "
         "noncomm_positions_net_ratio_to_open_interest REAL)"))
    existing_ids = pd.read_sql_query(f"SELECT id FROM {table}", con = conn)
    new_data = soybeans[~soybeans["id"].isin(existing_ids["id"])]
    df_to_sql = new_data.to_sql(name = table, con = conn, if_exists = "append", index = False)
    conn.close()
    return df_to_sql

def run_pipeline():
    setup_logging(LOGGING_PATH)
    cot_df = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            cot_df = get_data(API_URL, API_PARAMS)
            logging.info(f"Connection Successful after Attempt No.: {attempt}")
            break
        except requests.exceptions.RequestException as error:
            logging.warning(f"Attempt {attempt} of {MAX_ATTEMPTS} failed: {error}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_WAIT_SECONDS)
    if cot_df is None:
        logging.error(f"No Connection after {MAX_ATTEMPTS} Attempts")
        return
    cot_df = transform_data(cot_df, OBJECTS_TO_INT, OBJECTS_TO_DATETIME)
    cot_df = aggregate_data(cot_df)
    soybeans_position_cot = soybeans_data(cot_df)
    rows_written = load_data(soybeans_position_cot, DATABASE_PATH, TABLE_NAME)
    logging.info(f"Number of rows written to database: {rows_written}")

if __name__ == "__main__":
    run_pipeline()


