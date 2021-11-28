from typing import Optional

from fastapi import Depends, APIRouter, HTTPException
from pydantic import ValidationError

from ..heating.constants import (
    WEATHER_URL,
    TEMPERATURE_URL,
    GPIO_PIN,
    RASPBERRY_PI_IP,
)
from ..models import WeatherReport, HeatingPeriodModel, HouseholdMemberPydantic, HeatingInfo, Advance, ConfResponse

from ..heating import HeatingSystem
from ..heating.constants import TESTING
from ..routes.authentication import get_current_active_user
from ..cache import get_weather, set_weather
from ..utils import get_json

hs = None
router = APIRouter()


@router.on_event('startup')
async def init_heating():
    global hs
    hs = HeatingSystem(GPIO_PIN, TEMPERATURE_URL, TESTING, RASPBERRY_PI_IP, 1)


@router.get("/heating/", response_model=HeatingInfo)
async def heating():
    """Gets current system information, including live indoor temperature"""
    context = {
        "indoor_temperature": hs.temperature,
        "sensor_readings": hs.measurements,
        "relay_on": hs.relay_state,
        "advance": Advance(on=bool(hs.advance_on), start=hs.advance_on),
    }
    return HeatingInfo(**context)

@router.get("/heating/on_off/", response_model=HeatingInfo)
async def heating_on_off(
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    """Switches heating program on or off"""
    if not hs.program_on:
        hs.turn_program_on()
    else:
        hs.turn_program_off()
    return await heating()


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


@router.get("/heating/times/")
async def get_heating_periods(
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    return await hs.get_times()


@router.post("/heating/times/")
async def new_period(
    period: HeatingPeriodModel,
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    try:
        return await hs.new_time(period, user.id)
    except ValueError as f:
        return HTTPException(status_code=422, detail=str(f))


@router.delete("/heating/times/")
async def delete_time(
    period_id: int,
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    return await hs.remove_time(period_id=period_id)


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
