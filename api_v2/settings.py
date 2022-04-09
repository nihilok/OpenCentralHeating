import logging
import os

DATABASE_URL = f"sqlite://{os.path.abspath(os.getcwd())}/db.sqlite3"

TORTOISE_MODELS_LIST = ["api_v2.models", "aerich.models"]

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {"models": TORTOISE_MODELS_LIST, "default_connection": "default"}
    },
    'use_tz': False,
    'timezone': 'UTC'
}

GLOBAL_LOG_LEVEL = logging.INFO