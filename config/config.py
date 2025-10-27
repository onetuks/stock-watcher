import os

import yaml

with open("config/config.yaml", "r", encoding="utf-8") as f:
  CFG = yaml.safe_load(f)

PARAMS = CFG.get("params", {})
LOOKBACK = int(PARAMS.get("lookback_bars", 252))
DD_PCT = float(PARAMS.get("dd_entry_pct", 15.0))
RSI_LEN = int(PARAMS.get("rsi_len", 14))
RSI_MAX = float(PARAMS.get("rsi_entry_max", 35.0))
TP_MIN = float(PARAMS.get("tp_min", 12.0))
TP_MAX = float(PARAMS.get("tp_max", 15.0))
TRAIL = float(PARAMS.get("trail_drop", 5.0))

DATA_CFG = CFG.get("data", {"period": "3y", "interval": "1d"})
PERIOD = DATA_CFG.get("period", "3y")
INTERVAL = DATA_CFG.get("interval", "1d")

NOTIFY = CFG.get("notify", {}).get("telegram", {})
TG_ENABLED = bool(NOTIFY.get("enabled", False))
TG_TOKEN = NOTIFY.get("bot_token", "")
TG_CHAT = NOTIFY.get("chat_id", "")

DATA_DIR = CFG.get("data_cache", {}).get("dir", "./data")
os.makedirs(DATA_DIR, exist_ok=True)
