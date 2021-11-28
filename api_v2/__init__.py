from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise
from fastapi.middleware.cors import CORSMiddleware
from . import settings

from .routes import auth_router, heating_router, secrets_router




# Create ASGI app:
app = FastAPI()
app.include_router(auth_router)
app.include_router(heating_router)
app.include_router(secrets_router)

# CORS Permissions:
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Tortoise.init_models(settings.TORTOISE_MODELS_LIST, "models")

# Register tortoise-orm models:
# register_tortoise(
#     app,
#     # db_url=settings.DATABASE_URL,
#     # modules={'models': settings.TORTOISE_MODELS_LIST},
#     config=settings.TORTOISE_ORM,
#     generate_schemas=True,
#     add_exception_handlers=True,
# )
async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['api_v2.models']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()

@app.on_event('startup')
async def run_init():
    await init()
