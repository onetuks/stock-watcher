import numpy
import pandas

from data.positions import save_positions, positions
from data.watchlist import get_ticker


def validate_entry_price(container, entry_price: float):
  if entry_price <= 0:
    container.error("진입가를 입력하세요.")


def render_register(container, watchlist: pandas.DataFrame):
  stock = container.selectbox("종목 선택", watchlist["name"].tolist())
  symbol = get_ticker(watchlist["name"].tolist().index(stock))
  entry_price = container.number_input(
      "진입가(체결가)", min_value=0.0, step=0.1, format="%.4f")
  round_no = container.number_input("전략 라운드", min_value=1, step=1, value=1)

  # todo: 각 항목이 어떤 의미인지 파악하기
  if container.button("진입 기록"):
    validate_entry_price(container, entry_price)
    new = pandas.DataFrame([{
      "symbol": symbol,
      "entry_date": pandas.Timestamp.now(tz="Asia/Seoul").date().isoformat(),
      "entry_price": entry_price,
      "run_high": entry_price,
      "took_half": False,
      "closed": False,
      "close_date": "",
      "close_price": numpy.nan,
      "round": int(round_no)
    }])
    _positions = pandas.concat([positions, new], ignore_index=True)
    save_positions(_positions)
    container.success(f"진입 기록 완료: {symbol} @ {entry_price}")
