import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

from config.config import DD_PCT, RSI_MAX, TP_MIN, TP_MAX, TRAIL, PERIOD, \
  INTERVAL, LOOKBACK, RSI_LEN, TG_TOKEN, TG_CHAT, TG_ENABLED
from data.positions import save_positions, positions
from data.watchlist import watchlist
from notifier import send_telegram
from signals import (
  compute_indicators, entry_signal, calc_tp_band, trail_trigger,
  normalize_symbol
)

st.set_page_config(page_title="WatchDash (A안)", layout="wide")


# --------- Data fetch (with cache) ---------
@st.cache_data(show_spinner=True)
def fetch_price_df(sym: str, period: str, interval: str):
  ysym = normalize_symbol(sym)
  data = yf.download(ysym, period=period, interval=interval, auto_adjust=False,
                     progress=False)
  if data is None or data.empty:
    return pd.DataFrame()
  data = data.rename(columns=str.title)  # Open High Low Close Volume
  data.index = pd.to_datetime(data.index)
  return data


# --------- UI ---------
st.title("📈 WatchDash — 전략 신호 모니터 (A안)")
st.markdown(
  f"- 파라미터: DD≥**{DD_PCT}%**, RSI<{RSI_MAX}, TP **{TP_MIN}~{TP_MAX}%**, 트레일링 **-{TRAIL}%**")

colL, colR = st.columns([2, 1])

with colL:
  st.subheader("관심종목")
  st.dataframe(watchlist, use_container_width=True, hide_index=True)

with colR:
  st.subheader("수동 포지션 등록")
  symbol = st.selectbox("티커 선택", watchlist["ticker"].tolist())
  entry_price = st.number_input("진입가(체결가)", min_value=0.0, step=0.1,
                                format="%.4f")
  round_no = st.number_input("전략 라운드", min_value=1, step=1, value=1)
  if st.button("진입 기록"):
    if entry_price > 0:
      new = pd.DataFrame([{
        "symbol": symbol,
        "entry_date": pd.Timestamp.now(tz="Asia/Seoul").date().isoformat(),
        "entry_price": entry_price,
        "run_high": entry_price,
        "took_half": False,
        "closed": False,
        "close_date": "",
        "close_price": np.nan,
        "round": int(round_no)
      }])
      positions = pd.concat([positions, new], ignore_index=True)
      save_positions(positions)
      st.success(f"진입 기록 완료: {symbol} @ {entry_price}")
    else:
      st.error("진입가를 입력하세요.")

# --------- Main loop: compute signals per symbol ---------
rows = []
for _, row in watchlist.iterrows():
  sym = row["ticker"]
  name = row.get("name", "")
  df = fetch_price_df(sym, PERIOD, INTERVAL)
  if df.empty or len(df) < 30:
    rows.append({"ticker": sym, "name": name, "status": "NO DATA"})
    continue
  ind = compute_indicators(df, LOOKBACK, RSI_LEN)
  last = ind.iloc[-1]

  # entry signal (only informational)
  entry_ok = entry_signal(last, DD_PCT, RSI_MAX)

  # if we have an open manual position, compute TP band & trailing
  pos = positions[(positions["symbol"] == sym) & (positions["closed"] == False)]
  tp_hint, trail_hit, tp_hit = "", False, False
  dd_pct = float(last.get("dd_pct", np.nan))
  rsi = float(last.get("rsi", np.nan))

  if not pos.empty:
    # For simplicity, take the latest open row
    pos = pos.iloc[-1].copy()
    entry_price = float(pos["entry_price"])
    run_high = float(pos["run_high"]) if not pd.isna(
        pos["run_high"]) else entry_price
    # update run_high on the fly
    run_high = max(run_high, float(last["Close"]))
    tp_low, tp_high = calc_tp_band(entry_price, TP_MIN, TP_MAX)
    tp_hint = f"{tp_low:.2f} ~ {tp_high:.2f}"
    # Check TP "hit" range
    if last["Close"] >= tp_low and last["Close"] <= tp_high and (
    not bool(pos["took_half"])):
      tp_hit = True
    # Trailing
    trail_hit = trail_trigger(float(last["Close"]), run_high, TRAIL)

    # Update run_high in positions cache (in-memory)
    positions.loc[pos.name, "run_high"] = run_high

  status = []
  if entry_ok:
    status.append("ENTRY")
  if tp_hit:
    status.append("TP½")
  if trail_hit:
    status.append("TRAIL")
  if not status:
    status = ["-"]

  rows.append({
    "ticker": sym,
    "name": name,
    "dd_pct": round(dd_pct, 2) if not np.isnan(dd_pct) else None,
    "rsi": round(rsi, 2) if not np.isnan(rsi) else None,
    "close": float(last["Close"]),
    "entry?": "Y" if entry_ok else "",
    "tp_band": tp_hint,
    "tp_hit?": "Y" if tp_hit else "",
    "trail_hit?": "Y" if trail_hit else "",
    "status": " | ".join(status)
  })

# Persist run_high updates if any
save_positions(positions)

st.markdown("### 오늘의 신호")
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# --------- Detail chart for a selected symbol ---------
st.markdown("---")
sel = st.selectbox("차트 보기", watchlist["ticker"].tolist(), index=0,
                   key="chart_sel")
df = fetch_price_df(sel, PERIOD, INTERVAL)
if not df.empty:
  ind = compute_indicators(df, LOOKBACK, RSI_LEN)
  st.line_chart(ind[["Close", "recent_high"]], height=300,
                use_container_width=True)
  st.area_chart(ind[["rsi"]], height=150, use_container_width=True)
  st.caption("Close & RecentHigh(252), RSI(14)")

# --------- Actions for open position (half TP / close) ---------
st.markdown("---")
st.subheader("포지션 관리(수동 기록)")
open_pos = positions[(positions["closed"] == False)]
st.dataframe(open_pos, use_container_width=True, hide_index=True)

col1, col2 = st.columns(2)
with col1:
  tgt_symbol = st.selectbox("대상 심볼", positions[
    "symbol"].unique().tolist() if not positions.empty else [], key="act_sym")
  if st.button("절반 익절 기록(수동)"):
    if positions.empty or tgt_symbol not in positions["symbol"].values:
      st.error("대상 포지션이 없습니다.")
    else:
      # mark took_half=True (단순 기록)
      idx = positions[(positions["symbol"] == tgt_symbol) & (
            positions["closed"] == False)].index
      if len(idx) > 0:
        positions.loc[idx[-1], "took_half"] = True
        save_positions(positions)
        st.success(f"{tgt_symbol} 절반 익절 기록 완료")

with col2:
  tgt_symbol2 = st.selectbox("전량 청산 심볼", positions[
    "symbol"].unique().tolist() if not positions.empty else [], key="act_sym2")
  close_price = st.number_input("청산가(체결가)", min_value=0.0, step=0.1,
                                format="%.4f")
  if st.button("전량 청산 기록(수동)"):
    idx = positions[(positions["symbol"] == tgt_symbol2) & (
          positions["closed"] == False)].index
    if len(idx) > 0 and close_price > 0:
      positions.loc[idx[-1], "closed"] = True
      positions.loc[idx[-1], "close_date"] = pd.Timestamp.now(
        tz="Asia/Seoul").date().isoformat()
      positions.loc[idx[-1], "close_price"] = close_price
      save_positions(positions)
      st.success(f"{tgt_symbol2} 전량 청산 기록 완료")

# --------- Optional notifications ---------
if TG_ENABLED:
  st.info("텔레그램 알림이 활성화되어 있습니다. ENTRY/TP/Trail 시 수동으로 보내려면 아래 버튼 사용.")
  msg = st.text_input("전송할 메시지:", value="[TEST] WatchDash is running.")
  if st.button("텔레그램 전송"):
    ok = send_telegram(TG_TOKEN, TG_CHAT, msg)
    st.success("전송 완료" if ok else "전송 실패")
else:
  st.caption("설정(config.yaml)에서 telegram.enabled=true로 바꾸면 알림 가능.")
