from copy import deepcopy

import pandas
import streamlit

from utils.file_chooser import icon_file_to_uri


def render_interested(container, watchlist: pandas.DataFrame):
  if "icon" in watchlist.columns:
    _watchlist = deepcopy(watchlist)
    _watchlist["icon"] = _watchlist["icon"].apply(lambda p: icon_file_to_uri(p))

    container.dataframe(
        _watchlist,
        width="stretch",
        hide_index=True,
        column_config={
          "icon": streamlit.column_config.ImageColumn(
              "아이콘",
              width="small"
          )
        }
    )
