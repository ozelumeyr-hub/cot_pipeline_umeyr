import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

#static Variables

FILE_PATH = "../data/raw/future_agriculture.csv"
DATE_FORMAT = "%Y %b %d %I:%M:%S %p"
DATES = "Report_Date_as_YYYY_MM_DD"

#Extract

cot_df = pd.read_csv(FILE_PATH, thousands = ".", decimal = ",", date_format = DATE_FORMAT, parse_dates = [DATES])

#Transform

cot_df["NonComm_Positions_Net_All"] = cot_df["NonComm_Positions_Long_All"] - cot_df["NonComm_Positions_Short_All"]
cot_df["Comm_Positions_Net_All"] = cot_df["Comm_Positions_Long_All"] - cot_df["Comm_Positions_Short_All"]
cot_df["NonComm_Positions_Net_Ratio"] = cot_df["NonComm_Positions_Net_All"] / cot_df["Open_Interest_All"]

soybeans_df = (cot_df.loc
        [cot_df["Market_and_Exchange_Names"] == "SOYBEANS - CHICAGO BOARD OF TRADE",
    [DATES,
     "NonComm_Positions_Net_All",
     "Comm_Positions_Net_All",
     "NonComm_Positions_Net_Ratio"]]).sort_values(DATES, ascending = False).reset_index(drop = True)

y_axis = soybeans_df["NonComm_Positions_Net_All"]
x_axis = soybeans_df[DATES]

plt.plot(x_axis, y_axis)

#Load Data to SQLite Database

conn = sqlite3.connect("../data/soybeans_positions.db")
soybeans_positions_cot = soybeans_df.to_sql("soybeans_positions", con = conn, if_exists = "replace", index = False)
query_sql = pd.read_sql_query("SELECT * from soybeans_positions", conn, parse_dates = [DATES])
conn.close()

print(query_sql.dtypes)

