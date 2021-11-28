import configparser
import os
from pathlib import Path

config = configparser.ConfigParser()
path = Path(__file__)
ROOT_DIR = path.parent.absolute()
config_path = os.path.join(ROOT_DIR, "secrets.ini")
config.read(config_path)
initialized_config = config