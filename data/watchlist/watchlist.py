import os

import pandas
import streamlit

DATA_FILE_PATH = "data/watchlist/watchlist.csv"

COL_ICON = "icon"
COL_TICKER = "ticker"
COL_MARKET = "market"
COL_NAME = "name"
COL_QUANTITY = "quantity"
COL_RATIO = "ratio"


@streamlit.cache_data
def load_watchlist(version: float) -> pandas.DataFrame:
  return pandas.read_csv(DATA_FILE_PATH)


def get_watchlist() -> pandas.DataFrame:
  try:
    version = os.path.getmtime(DATA_FILE_PATH)
  except OSError:
    version = 0.0
  return load_watchlist(version)


watchlist = get_watchlist()


def get_ticker(idx: int) -> str:
  return watchlist[COL_TICKER][idx]


def _calculate_ratio(quantity: float) -> float:
  df = get_watchlist()

  total_quantity = df[COL_QUANTITY].sum()
  if total_quantity == 0:
    return 0.0

  q = quantity.iloc[0] if hasattr(quantity, "iloc") else quantity
  return float(q) / float(total_quantity)


def add_quantity(ticker: str, quantity: float) -> None:
  df = get_watchlist()

  mask = df[COL_TICKER] == ticker
  if not mask.any():
    return

  df.loc[mask, COL_QUANTITY] = df.loc[mask, COL_QUANTITY] + quantity
  df.loc[mask, COL_RATIO] = _calculate_ratio(df.loc[mask, COL_QUANTITY])
  df.to_csv(DATA_FILE_PATH, index=False)
