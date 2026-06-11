import pandas as pd


def extract_csv_text(file_path):

    df = pd.read_csv(file_path)

    return df.to_string(index=False)