import config as conf
import extract
import transform
import load
import pandas as pd
import time
import logging
import requests

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

def setup_logging(logging_path):
    logging_path.parent.mkdir(parents = True, exist_ok = True)

    logging.basicConfig(
        filename = logging_path,
        level = logging.INFO,
        format = "%(asctime)s | %(levelname)s | %(message)s"
    )

def run_pipeline():
    setup_logging(conf.LOGGING_PATH)
    cot_df = None
    for attempt in range(1, conf.MAX_ATTEMPTS + 1):
        try:
            cot_df = extract.get_data(conf.API_URL, conf.API_PARAMS)
            logging.info(f"Connection Successful after Attempt No.: {attempt}")
            break
        except requests.exceptions.RequestException as error:
            logging.warning(f"Attempt {attempt} of {conf.MAX_ATTEMPTS} failed: {error}")
            if attempt < conf.MAX_ATTEMPTS:
                time.sleep(conf.RETRY_WAIT_SECONDS)
    if cot_df is None:
        logging.error(f"No Connection after {conf.MAX_ATTEMPTS} Attempts")
        return
    cot_df = transform.transform_data(cot_df, conf.OBJECTS_TO_INT, conf.OBJECTS_TO_DATETIME)
    cot_df = transform.aggregate_data(cot_df)
    soybeans_position_cot = transform.soybeans_data(cot_df)
    rows_written = load.load_data(soybeans_position_cot, conf.DATABASE_PATH, conf.TABLE_NAME)
    logging.info(f"Number of rows written to database: {rows_written}")

if __name__ == "__main__":
    run_pipeline()


