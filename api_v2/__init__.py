from fastapi import FastAPI
from tortoise import Tortoise
from fastapi.middleware.cors import CORSMiddleware
from . import settings
from .heating.heating_system import HeatingSystem
from .heating.systems_in_memory import systems_in_memory
from .models import HeatingSystemModel

from .routes import auth_router, heating_v2_router, secrets_router, weather_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(heating_v2_router)
app.include_router(secrets_router)
app.include_router(weather_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def init_db():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def init_heating_systems():
    systems = await HeatingSystemModel.all()
    for system in systems:
        if system.activated:
            systems_in_memory[system.system_id] = HeatingSystem(
                gpio_pin=system.gpio_pin,
                temperature_url=system.sensor_url,
                raspberry_pi_ip=system.raspberry_pi,
                household_id=system.household_id,
                system_id=system.system_id,
            )


@app.on_event("startup")
async def run_init():
    await init_db()
    await init_heating_systems()


@app.on_event("shutdown")
async def close_down():
    await Tortoise.close_connections()
