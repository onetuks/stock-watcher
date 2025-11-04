import os

import numpy
import pandas

DATA_FILE_PATH = "data/positions/positions.csv"

COL_SYMBOL = "symbol"  # 매매 대상 티커 (선택 종목 심볼)
COL_ENTRY_DATE = "entry_date"  # 진입 날짜
COL_ENTRY_PRICE = "entry_price"  # 진입가
COL_QUANTITY = "quantity"  # 주문량
COL_RUN_HIGH = "run_high"  # 진입 후 최고가 (default: 진입값)
COL_TOOK_HALF = "took_half"  # 절반 청산 여부
COL_CLOSED = "closed"  # 포지션 종료 여부
COL_CLOSED_DATE = "closed_date"  # 청산 날짜
COL_CLOSED_PRICE = "closed_price"  # 청산가
COL_ROUND_NO = "round_no"  # 전략 라운드 번호

POSITION_UNIQUE_KEYS = [COL_SYMBOL, COL_ROUND_NO, COL_ENTRY_DATE]


def _init_positions_header():
  if not os.path.exists(DATA_FILE_PATH):
    with open(DATA_FILE_PATH, "w") as f:
      f.write(
          f"{COL_SYMBOL},{COL_ENTRY_DATE},{COL_ENTRY_PRICE},{COL_QUANTITY},"
          f"{COL_RUN_HIGH},{COL_TOOK_HALF},{COL_CLOSED},{COL_CLOSED_DATE},"
          f"{COL_CLOSED_PRICE},{COL_ROUND_NO}\n")


def _ensure_columns(df: pandas.DataFrame, cols):
  for c in cols:
    if c not in df.columns:
      df[c] = numpy.nan
  return df


def get_positions():
  _init_positions_header()

  position = pandas.read_csv(DATA_FILE_PATH)
  position = _ensure_columns(position, [
    COL_SYMBOL, COL_ENTRY_DATE, COL_ENTRY_PRICE,
    COL_QUANTITY, COL_RUN_HIGH, COL_TOOK_HALF, COL_CLOSED,
    COL_CLOSED_DATE, COL_CLOSED_PRICE, COL_ROUND_NO
  ])
  return position


def save_positions(symbol: str, entry_price: int, quantity: float,
    run_high: int, round_no: int):
  new_position = pandas.DataFrame([{
    "symbol": symbol,
    "entry_date": pandas.Timestamp.now(tz="Asia/Seoul").date().isoformat(),
    "entry_price": entry_price,
    "quantity": quantity,
    "run_high": run_high,
    "took_half": False,
    "closed": False,
    "close_date": "",
    "close_price": numpy.nan,
    "round_no": round_no
  }])

  if positions is not None and not positions.empty:
    new_positions = pandas.concat([positions, new_position], ignore_index=True)
  else:
    new_positions = new_position
  new_positions = new_positions.drop_duplicates(subset=POSITION_UNIQUE_KEYS,
                                                keep="last")

  new_positions.to_csv(DATA_FILE_PATH, index=False)


positions = get_positions()
