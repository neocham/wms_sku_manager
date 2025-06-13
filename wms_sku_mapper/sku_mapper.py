# sku_mapper.py

import pandas as pd
from difflib import get_close_matches

def load_file(file_path):
    """
    Load CSV or Excel files into a DataFrame.
    """
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")

def fuzzy_map_skus(sales_df, msku_df, threshold=0.8):
    """
    Map SKUs from the sales data to MSKUs using fuzzy matching.
    """
    msku_list = msku_df['MSKU'].dropna().astype(str).tolist()
    title_list = msku_df['Title'].dropna().astype(str).tolist()

    def match_sku(sku):
        sku = str(sku).strip()
        match = get_close_matches(sku, msku_list, n=1, cutoff=threshold)
        if match:
            return match[0]
        match = get_close_matches(sku, title_list, n=1, cutoff=threshold)
        if match:
            return match[0]
        return 'UNMAPPED'

    sales_df['MSKU'] = sales_df['SKU'].apply(match_sku)
    return sales_df
