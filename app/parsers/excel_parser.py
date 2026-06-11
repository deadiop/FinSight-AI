import pandas as pd


def extract_excel_text(file_path):

    df = pd.read_excel(file_path)

    return df.to_string(index=False)