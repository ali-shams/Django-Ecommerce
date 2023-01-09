import os
from pathlib import Path

import pandas as pd

path = os.path.normpath(f'{Path(__file__).parent}/ecommerce_dataset.xlsx')


class ReadDataset:
    @staticmethod
    def read_excel_file(sheet_name):
        df = pd.read_excel(path, sheet_name=sheet_name)
        count_not_null_rows = len(df[df['id'].notnull()])
        header = list(df.columns.values)
        return [dict(zip(header, [int(data) if not isinstance(data, str)
                                  else data.replace('\u200c', '').strip() if data != 'None' else None
                                  for data in df.iloc[row]])) for row in range(count_not_null_rows)]

    @staticmethod
    def get_sheet_names():
        return pd.ExcelFile(path).sheet_names
