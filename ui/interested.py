from copy import deepcopy

import pandas

from utils.assets_finder import icon_file_to_uri, market_file_to_uri


def render_interested(container, watchlist: pandas.DataFrame):
  _watchlist = deepcopy(watchlist).drop(columns=["ticker"])

  if "icon" in watchlist.columns:
    _watchlist["icon"] = _watchlist["icon"].apply(
        lambda p: icon_file_to_uri(p))
  if "market" in watchlist.columns:
    _watchlist["market"] = _watchlist["market"].apply(
        lambda p: market_file_to_uri(p))

  container.dataframe(
      _watchlist,
      width="stretch",
      hide_index=True,
      column_config={
        "icon": container.column_config.ImageColumn(
            "아이콘",
            width="small",
            pinned=True,
        ),
        "market": container.column_config.ImageColumn(
            "시장",
            width="small",
            pinned=True,
        ),
        "name": container.column_config.TextColumn(
            "종목명",
            width="small",
        ),
        "count": container.column_config.NumberColumn(
            "보유수량",
            width="small",
        ),
        "portion": container.column_config.NumberColumn(
            "포트폴리오 비율",
            width="small",
            format="percent",
        )
      }
  )
