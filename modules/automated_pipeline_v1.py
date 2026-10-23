import requests
import pandas as pd
import sqlite3
from pathlib import Path

from cot_pipeline_umeyr.modules.pipeline import soybeans_df, soybeans_positions_cot

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

request = requests.get(API_URL, params = API_PARAMS).json()
cot_df = (pd.json_normalize(request))


for object_soon_int in OBJECTS_TO_INT:
    cot_df[object_soon_int] = pd.to_numeric(cot_df[object_soon_int])

for objects_soon_datetime in OBJECTS_TO_DATETIME:
    cot_df[objects_soon_datetime] = pd.to_datetime(cot_df[objects_soon_datetime], format="ISO8601")


cot_df["noncomm_positions_net_all"] = cot_df["noncomm_positions_long_all"] - cot_df["noncomm_positions_short_all"]
cot_df["comm_positions_net_all"] = cot_df["comm_positions_long_all"] - cot_df["comm_positions_short_all"]
cot_df["noncomm_positions_net_ratio_to_open_interest"] = cot_df["noncomm_positions_net_all"] / cot_df["open_interest_all"]

soybeans_positions_cot = (cot_df[["id",
                                  "cftc_contract_market_code",
                                  "market_and_exchange_names",
                                  "report_date_as_yyyy_mm_dd",
                                  "noncomm_positions_net_all",
                                  "comm_positions_net_all",
                                  "noncomm_positions_net_ratio_to_open_interest"]])

DATABASE_PATH.parent.mkdir(parents = True, exist_ok = True)
conn = sqlite3.connect(DATABASE_PATH)
conn.execute(
    ("CREATE TABLE IF NOT EXISTS COT_DATA(id "
     "TEXT PRIMARY KEY, "
     "cftc_contract_market_code TEXT, "
     "market_and_exchange_names TEXT, "
     "report_date_as_yyyy_mm_dd TEXT, "
     "noncomm_positions_net_all INTEGER, "
     "comm_positions_net_all INTEGER, "
     "noncomm_positions_net_ratio_to_open_interest REAL)"))
existing_ids = pd.read_sql_query("SELECT id FROM COT_DATA", con = conn)
new_data = soybeans_positions_cot[~soybeans_positions_cot["id"].isin(existing_ids["id"])]
df_to_sql = new_data.to_sql(name = TABLE_NAME, con = conn, if_exists = "append", index = False)
conn.close()


