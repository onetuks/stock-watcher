import os
import numpy
import pandas


def load_positions():
  if not os.path.exists("data/positions.csv"):
    with open("data/positions.csv", "w") as f:
      f.write(
          "symbol,entry_date,entry_price,run_high,took_half,closed,close_date,close_price,round\n")
  position = pandas.read_csv("data/positions.csv")
  position = ensure_columns(position, ["symbol", "entry_date", "entry_price", "run_high",
                                       "took_half", "closed", "close_date", "close_price",
                                       "round"])
  return position


def save_positions(df: pandas.DataFrame):
  df.to_csv("data/positions.csv", index=False)


def ensure_columns(df: pandas.DataFrame, cols):
  for c in cols:
    if c not in df.columns:
      df[c] = numpy.nan
  return df


positions = load_positions()
