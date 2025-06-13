# sku_mapper.py
import pandas as pd

class SKUMapper:
    def __init__(self, mapping_file):
        self.mapping_df = pd.read_csv(mapping_file)
        self.mapping_dict = self._create_mapping()

    def _create_mapping(self):
        return {
            str(row['SKU']).strip().upper(): str(row['MSKU']).strip().upper()
            for _, row in self.mapping_df.iterrows()
        }

    def map_skus(self, sales_df, sku_col='SKU'):
        sales_df['MSKU'] = sales_df[sku_col].apply(
            lambda x: self.mapping_dict.get(str(x).strip().upper(), 'UNMAPPED')
        )
        return sales_df

    def get_unmapped(self, mapped_df):
        return mapped_df[mapped_df['MSKU'] == 'UNMAPPED']

