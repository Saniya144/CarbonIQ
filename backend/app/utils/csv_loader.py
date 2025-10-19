
import pandas as pd
from io import StringIO

REQUIRED_COLUMNS = ["date", "description", "category", "unit", "quantity"]

def read_transactions_csv(file_bytes: bytes) -> pd.DataFrame:
    s = file_bytes.decode("utf-8")
    df = pd.read_csv(StringIO(s))
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {missing}")
    return df
