import sqlite3
import pandas as pd

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