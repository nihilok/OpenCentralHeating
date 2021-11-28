import os

DATABASE_URL = f"sqlite://{os.path.abspath(os.getcwd())}/db.sqlite3"

TORTOISE_MODELS_LIST = ["api_v2.models", "aerich.models"]

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "api_v2": {"models": TORTOISE_MODELS_LIST, "default_connection": "default"}
    },
    'routers': ['api_v2.routes.authentication.router', 'api_v2.routes.heating.router'],
    'use_tz': False,
    'timezone': 'UTC'
}
