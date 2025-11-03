import logging
from importlib import resources


ASSETS_DIR = "assets"
ICONS_DIR = "icons"
NATIONS_DIR = "nations"


def file_to_uri(filename: str) -> str | None:
  try:
    candidate = resources.files(ASSETS_DIR) / filename
    with resources.as_file(candidate) as p:
      if p.exists():
        return p.resolve().as_uri()
  except FileNotFoundError:
    logging.warning(f"File {filename} not found")

def icon_file_to_uri(filename: str) -> str:
  return file_to_uri(ICONS_DIR + "/" + filename)


def nation_file_to_uri(filename: str) -> str:
  return file_to_uri(NATIONS_DIR + "/" + filename)
