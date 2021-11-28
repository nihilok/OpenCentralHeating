import json
from . import initialized_config as config

LOCAL = True

superusers = json.loads(config['SUPERUSERS'].get('superuser_list', '[]'))
SUPERUSERS = superusers
GUEST_IDS = []

origins = ["https://example.app"]

origins = origins + ["*"] if LOCAL else origins
SECRET_KEY = "SoMeThInG_-sUp3Rs3kREt!!"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 5
