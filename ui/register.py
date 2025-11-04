import pandas

from data.positions.positions import save_positions
from data.watchlist.watchlist import get_ticker, add_quantity


def render_register(container, watchlist: pandas.DataFrame):
  stock = container.selectbox("종목 선택", watchlist["name"].tolist())
  symbol = get_ticker(watchlist["name"].tolist().index(stock))
  entry_price = container.number_input("진입가", min_value=0, step=1)
  quantity = container.number_input("주문량", min_value=0.0, step=1.0,
                                    format="%.4f")
  round_no = container.number_input("전략 라운드", min_value=1, step=1, value=1)

  if container.button("진입 기록"):
    if entry_price <= 0:
      container.error("진입가를 입력하세요.")
      return

    add_quantity(ticker=symbol, quantity=quantity)
    save_positions(symbol=symbol, entry_price=entry_price, quantity=quantity,
                   run_high=entry_price, round_no=int(round_no))

    container.success(f"진입 기록 완료: {stock} @구매액 = {entry_price * quantity}")
