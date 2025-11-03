import requests


def send_telegram(bot_token: str, chat_id: str, text: str):
  url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
  try:
    resp = requests.post(url, data={"chat_id": chat_id, "text": text})
    return resp.ok
  except Exception as e:
    return False
