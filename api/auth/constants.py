import configparser
import json
import os
from pathlib import Path

config = configparser.ConfigParser()
path = Path(os.getcwd())
print(path)
config_path = os.path.join(path, "api/secrets/secrets.ini")
config.read(config_path)
superusers = json.loads(config['SUPERUSERS'].get('superuser_list', '[]'))
SUPERUSERS = superusers
GUEST_IDS = []
TESTING = True  # Uses benign heating system when True
# API will fail if no heating system in place when False

origins = ["https://example.app"]

origins = origins + ["*"] if TESTING else origins
SECRET_KEY = "SoMeThInG_-sUp3Rs3kREt!!"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 5
