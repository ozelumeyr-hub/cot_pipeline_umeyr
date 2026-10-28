import pandas as pd

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