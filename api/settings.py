import os

DATABASE_URL = f"sqlite://{os.path.abspath(os.getcwd())}/db.sqlite3"

TORTOISE_MODELS_LIST = ["api.heating.models", "api.auth.models", "aerich.models"]

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": TORTOISE_MODELS_LIST,
            "default_connection": "default",
        },
    },
}
