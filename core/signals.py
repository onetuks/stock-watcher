import pandas as pd
import numpy as np
import ta

def compute_indicators(df: pd.DataFrame, lookback_bars: int = 252, rsi_len: int = 14) -> pd.DataFrame:
  """
  df는 yfinance가 반환한 일봉 DataFrame.
  MultiIndex(필드,티커) 형태일 수도 있으므로 OHLCV 단일 컬럼으로 표준화한다.
  """
  out = df.copy()

  # 1) MultiIndex면 티커 레벨 제거 → 'Open','High','Low','Close','Adj Close','Volume'
  if isinstance(out.columns, pd.MultiIndex):
    # 보통 (필드,티커) 순서. 티커가 1개뿐이면 그 레벨을 드롭.
    if out.columns.nlevels == 2 and len(out.columns.get_level_values(1).unique()) == 1:
      out.columns = out.columns.get_level_values(0)
    else:
      # (희소) 여러 티커가 섞여 들어온 경우 – 여기서는 사용하지 않으므로 첫 번째 티커만 선택
      first_ticker = out.columns.get_level_values(1).unique().tolist()[0]
      out = out.xs(first_ticker, axis=1, level=1)

  # 2) 컬럼이 'Open_Googl'처럼 접미사가 붙어있다면 언더스코어 앞만 취해 표준화
  std_map = {}
  for c in out.columns:
    base = str(c)
    if "_" in base:
      base = base.split("_", 1)[0]
    base = base.title().strip()
    if base in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
      std_map[c] = base
  if std_map:
    out = out.rename(columns=std_map)

  # 3) 대소문자 표준화(예방차원)
  out = out.rename(columns=str.title)

  # 4) 필요한 컬럼 확인
  needed = ["Open", "High", "Low", "Close"]
  for c in needed:
    if c not in out.columns:
      raise ValueError(f"compute_indicators: required column '{c}' missing. columns={list(out.columns)}")

  # 5) Series 강제
  def ensure_series(x):
    return x.iloc[:, 0] if isinstance(x, pd.DataFrame) else x

  high  = pd.to_numeric(ensure_series(out["High"]), errors="coerce")
  close = pd.to_numeric(ensure_series(out["Close"]), errors="coerce")

  # 6) 최근 고점(rolling max)
  recent_high = high.rolling(int(lookback_bars), min_periods=1).max()
  out["recent_high"] = recent_high

  # 7) DD% 계산(0/NaN 방지)
  safe_recent_high = recent_high.replace(0, np.nan)
  out["dd_pct"] = (recent_high - close) / safe_recent_high * 100.0

  # 8) RSI(ta 라이브러리)
  rsi_indicator = ta.momentum.RSIIndicator(close=close, window=int(rsi_len))
  out["rsi"] = rsi_indicator.rsi()

  return out


def entry_signal(row, dd_entry_pct: float, rsi_entry_max: float) -> bool:
  if np.isnan(row.get("dd_pct", np.nan)) or np.isnan(row.get("rsi", np.nan)):
    return False
  return (row["dd_pct"] >= dd_entry_pct) and (row["rsi"] < rsi_entry_max)

def calc_tp_band(entry_price: float, tp_min: float, tp_max: float):
  return entry_price*(1.0+tp_min/100.0), entry_price*(1.0+tp_max/100.0)

def trail_trigger(current_close: float, run_high: float, trail_drop: float) -> bool:
  if run_high is None or np.isnan(run_high) or run_high <= 0:
    return False
  return current_close <= run_high * (1.0 - trail_drop/100.0)

def update_run_high(prev_run_high, current_close):
  if prev_run_high is None or np.isnan(prev_run_high) or prev_run_high <= 0:
    return current_close
  return max(prev_run_high, current_close)

def normalize_symbol(raw: str) -> str:
  # Accept "NASDAQ:TSLA" or "TSLA" — yfinance uses "TSLA" (US), "005930.KS" (KR)
  # We'll convert KRX prefix to ".KS" suffix if numeric code. Manual mapping may be needed.
  if raw.startswith("KRX:"):
    code = raw.split(":")[1]
    # naive mapping: assume Korea Exchange ".KS"
    return f"{code}.KS"
  if ":" in raw:
    return raw.split(":")[1]
  return raw

def now_str():
  return pd.Timestamp.now(tz="Asia/Seoul").strftime("%Y-%m-%d %H:%M:%S")
