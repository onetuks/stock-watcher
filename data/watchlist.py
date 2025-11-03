import pandas
import streamlit


@streamlit.cache_data
def load_watchlist(path="data/watchlist.csv"):
  return pandas.read_csv(path)


watchlist = load_watchlist()


def get_ticker(idx: int) -> str:
  return watchlist["ticker"][idx]
