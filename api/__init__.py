from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise
from fastapi.middleware.cors import CORSMiddleware
from . import settings
from .auth.constants import origins
from .auth import router as auth_router
from .secrets import router as secrets_router
from .heating import router as heating_router


# Create ASGI app:
app = FastAPI()


# CORS Permissions:
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Tortoise.init_models(settings.TORTOISE_MODELS_LIST, "models")

# Register tortoise-orm models:
register_tortoise(
    app,
    config=settings.TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

app.include_router(auth_router)
app.include_router(secrets_router)
app.include_router(heating_router)
