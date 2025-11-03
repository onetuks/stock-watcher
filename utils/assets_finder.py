import base64
import logging
import mimetypes
from importlib import resources

ASSETS_DIR = "assets"
ICONS_DIR = "icons"
NATIONS_DIR = "markets"


def _file_to_uri(filename: str) -> str | None:
  try:
    candidate = resources.files(ASSETS_DIR) / filename
    with resources.as_file(candidate) as p:
      if p.exists():
        # Read bytes and return as data URI (works inside Streamlit tables)
        raw = p.read_bytes()
        mime, _ = mimetypes.guess_type(p.name)
        if not mime:
          mime = "image/png"
        b64 = base64.b64encode(raw).decode("ascii")
        return f"data:{mime};base64,{b64}"
      else:
        logging.warning(f"File {filename} not found in assets.")
        return None
  except FileNotFoundError:
    logging.warning(f"File {filename} not found")
    return None
  except Exception as e:
    logging.exception(f"Failed to load asset {filename}: {e}")
    return None


def icon_file_to_uri(filename: str) -> str:
  return _file_to_uri(ICONS_DIR + "/" + filename)


def market_file_to_uri(filename: str) -> str:
  return _file_to_uri(NATIONS_DIR + "/" + filename + ".png")
