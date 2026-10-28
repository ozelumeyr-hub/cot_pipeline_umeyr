from pathlib import Path

API_PARAMS = {"$order":"report_date_as_yyyy_mm_dd DESC",
               "$limit": "52",
               "$where": "market_and_exchange_names = 'SOYBEANS - CHICAGO BOARD OF TRADE'"}
API_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
OBJECTS_TO_INT = ["comm_positions_long_all", "comm_positions_short_all", "traders_noncomm_long_all", "traders_noncomm_short_all", "traders_comm_long_all", "traders_comm_short_all", "noncomm_positions_long_all", "noncomm_positions_short_all", "open_interest_all"]
OBJECTS_TO_DATETIME = ["report_date_as_yyyy_mm_dd"]
TABLE_NAME = "COT_DATA"
RETRY_WAIT_SECONDS = 5
MAX_ATTEMPTS = 3
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGGING_PATH = PROJECT_ROOT / "logs" / "status.log"
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "cot_cleandata.db"