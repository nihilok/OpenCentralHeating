from fastapi import Depends, APIRouter

from ..heating.manage_systems import get_system_from_memory_http

from ..models import (
    HouseholdMemberPydantic,
    HeatingInfo,
    Advance,
    HeatingConf,
)
from ..routes.authentication import get_current_active_user

router = APIRouter()


@router.get("/heating/", response_model=HeatingInfo)
async def heating(
    system_id: int,
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    """Gets current system information, including live indoor temperature"""
    hs = await get_system_from_memory_http(system_id, user.household.id)

    context = {
        "sensor_readings": hs.get_measurements(),
        "relay_on": hs.relay_state,
        "advance": Advance(on=bool(hs.advance_on), start=hs.advance_on),
        "conf": HeatingConf(
            program_on=hs.program_on,
            target=hs.current_period.target if hs.current_period else hs.MINIMUM_TEMP,
        ),
    }
    return HeatingInfo(**context)


@router.get("/heating/advance/{mins}/", response_model=Advance)
async def override_advance(
    system_id: int,
    mins: int = 30,
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    """Starts override/advance task in running event loop"""
    hs = await get_system_from_memory_http(system_id, user.household.id)

    started = await hs.start_advance(mins)
    return Advance(on=True, start=started, relay=hs.relay_state)


@router.get("/heating/advance/cancel/")
async def cancel_advance(
    system_id: int,
    user: HouseholdMemberPydantic = Depends(get_current_active_user),
):
    """Cancels advance task"""
    hs = await get_system_from_memory_http(system_id, user.household.id)

    await hs.cancel_advance()
    return Advance(on=False, relay=hs.relay_state)
