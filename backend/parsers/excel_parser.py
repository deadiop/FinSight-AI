import pandas as pd


def parse_excel(file_path):

    df = pd.read_excel(file_path)

    return df.to_dict(
        orient="records"
    )