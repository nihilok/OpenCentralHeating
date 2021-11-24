from typing import Optional

from fastapi import Depends, APIRouter, HTTPException

from api.heating.constants import WEATHER_URL, TEMPERATURE_URL, GPIO_PIN
from .models import Advance, HeatingConf, HeatingInfo, ConfResponse, WeatherReport

from ..auth.constants import TESTING
from ..auth.authentication import get_current_active_user
from ..auth.models import HouseholdMemberPydantic
from ..cache import get_weather, set_weather
from ..utils.async_requests import get_json


if not TESTING:
    from .central_heating import HeatingSystem
else:
    from .fake_central_heating import HeatingSystem


hs = HeatingSystem(GPIO_PIN, TEMPERATURE_URL)
router = APIRouter()


@router.get("/heating/", response_model=HeatingInfo)
async def heating(conf: bool = False):
    """Gets current system information, including live indoor temperature"""
    context = {
        "indoor_temperature": hs.temperature,
        "sensor_readings": hs.measurements,
        "relay_on": hs.relay_state,
        "advance": Advance(on=bool(hs.advance_on), start=hs.advance_on),
    }
    if conf:
        context["conf"] = hs.conf
    return HeatingInfo(**context)


async def heating_conf():
    """Returns the current heating configuration"""
    return ConfResponse(conf=hs.conf)


@router.post("/heating/", response_model=ConfResponse)
async def update_heating_conf(
    conf: HeatingConf, user: HouseholdMemberPydantic = Depends(get_current_active_user)
):
    """Updates the times and target temperature for heating system"""
    if hs.conf != conf:
        hs.conf.__dict__.update(**conf.dict())
        hs.save_state()
        await hs.main_task()
    return await heating_conf()


@router.get("/heating/on_off/", response_model=ConfResponse)
async def heating_on_off(
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    """Switches heating program on or off"""
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
    await hs.cancel_advance()
    return Advance(on=False, relay=hs.relay_state)


# Weather endpoint:
@router.get("/weather/", response_model=Optional[WeatherReport])
async def weather():
    """Gets weather info from OpenWeatherMap API or from local cache"""
    weather_dict = await get_weather()
    try:
        if not weather_dict:
            r = await get_json(WEATHER_URL)
            weather_dict = {"current": r["current"], "daily": r["daily"]}
            await set_weather(weather_dict)
        weather_report = WeatherReport(**weather_dict)
        return weather_report
    except KeyError:
        raise HTTPException(
            status_code=500, detail="OpenWeatherMap API not setup or not responding"
        )
