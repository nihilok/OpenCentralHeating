from dataclasses import dataclass
from typing import List, Optional

from fastapi import Depends, APIRouter
from pydantic import BaseModel

from ..central_heating import HeatingConf, Advance
from ..constants import WEATHER_URL, TEMPERATURE_URL, GPIO_PIN

from ...auth.constants import TESTING
from ...auth.authentication import get_current_active_user
from ...auth.models import HouseholdMemberPydantic
from ...cache.redis_funcs import get_weather, set_weather
from ...utils.async_requests import get_json


if not TESTING:
    from ..central_heating import HeatingSystem
else:
    @dataclass
    class HeatingSystem:
        gpio_pin: int
        temperature_url: str
        conf = HeatingConf(
            target="20",
            on_1="08:30",
            off_1="10:30",
            on_2="18:30",
            off_2="22:30",
            program_on=True,
        )

        @property
        def relay_state(self):
            return self.conf.program_on

        def program_on(self):
            self.conf.program_on = True

        def program_off(self):
            self.conf.program_on = False


hs = HeatingSystem(GPIO_PIN, TEMPERATURE_URL)
router = APIRouter()


class WeatherReport(BaseModel):
    # keys = ['dt', 'sunrise', 'sunset', 'temp', 'feels_like',
    #         'pressure', 'humidity', 'dew_point', 'uvi', 'clouds',
    #         'visibility', 'wind_speed', 'wind_deg', 'weather']
    current: dict
    daily: List[dict]


class ApiInfo(BaseModel):
    indoor_temp: str
    temp_float: float
    outdoor_temp: str = "- -" + "°C"
    outdoor_float: Optional[float] = None
    weather: str = "- -"
    last_updated: str = "--:--:--"
    on: bool = hs.relay_state
    program_on: bool = hs.conf.program_on
    advance: Optional[Advance] = None


class SensorReadings(BaseModel):
    temperature: float
    pressure: float
    humidity: float


class HeatingInfo(BaseModel):
    indoor_temperature: float
    sensor_readings: SensorReadings
    relay_on: bool
    advance: Optional[Advance] = None
    conf: Optional[HeatingConf] = None


@router.get("/weather/")
async def weather() -> WeatherReport:
    weather_dict = await get_weather()
    if not weather_dict:
        r = await get_json(WEATHER_URL)
        weather_dict = {"current": r["current"], "daily": r["daily"]}
        await set_weather(weather_dict)
    weather_report = WeatherReport(**weather_dict)
    return weather_report


@router.get("/heating/", response_model=HeatingInfo)
async def heating(conf: bool = False):
    context = {
        "indoor_temperature": hs.temperature,
        "sensor_readings": hs.measurements,
        "relay_on": hs.relay_state,
        "advance": hs.conf.advance or Advance(on=False),
    }
    if conf:
        context["conf"] = hs.conf
    return HeatingInfo(**context)


class ConfResponse(BaseModel):
    conf: HeatingConf


async def heating_conf():
    return ConfResponse(conf=hs.conf)


@router.post("/heating/", response_model=ConfResponse)
async def update_heating_conf(
    conf: HeatingConf, user: HouseholdMemberPydantic = Depends(get_current_active_user)
):
    if hs.conf != conf:
        hs.conf.__dict__.update(**conf.dict())
        hs.save_state()
        hs.main_loop()
    return await heating_conf()


@router.get("/heating/on_off/", response_model=ConfResponse)
async def heating_on_off(
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    if not hs.conf.program_on:
        hs.program_on()
    else:
        hs.program_off()
    return await heating_conf()


@router.get("/heating/advance/{mins}/", response_model=Advance)
async def override_advance(
    mins: int = 30,
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    """Starts override/advance task in running event loop"""
    started = await hs.start_advance(mins)
    return Advance(on=True, start=started, relay=hs.relay_state)


@router.get("/heating/cancel/")
async def cancel_advance(
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    """Cancels advance task"""
    hs.cancel_advance()
    return Advance(on=False, relay=hs.relay_state)
