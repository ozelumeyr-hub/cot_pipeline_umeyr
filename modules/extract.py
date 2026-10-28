import pandas as pd
import requests

def get_data(url, params):
    response = requests.get(url, params = params, timeout = 15)
    response.raise_for_status()
    cot_df = pd.json_normalize(response.json())
    return cot_df