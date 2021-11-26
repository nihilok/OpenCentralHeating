import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from .auth.constants import origins
from .auth import router as auth_router
from .secrets import router as secrets_router
from .heating import router as heating_router


# Create ASGI app:
app = FastAPI()
app.include_router(auth_router)
app.include_router(secrets_router)
app.include_router(heating_router)


# CORS Permissions:
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register tortoise-orm models:
register_tortoise(
    app,
    db_url=f"sqlite://{os.path.abspath(os.getcwd())}/db.sqlite3",
    modules={"models": ["api.auth.models", "api.heating.times.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
