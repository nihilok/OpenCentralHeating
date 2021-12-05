from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from api_v2.heating.manage_systems import (
    get_system_from_memory_http,
    get_system_instance_from_memory,
    create_system,
    get_system,
    create_instance,
    kill_system,
)
from api_v2.heating.manage_times import get_times, new_time, delete_time
from api_v2.models import (
    HouseholdMember,
    HeatingPeriod,
    Household,
    HeatingV2Response,
    SystemInfo,
    PHeatingPeriod,
    HeatingPeriodModelCreator,
    PHeatingSystemIn,
    HeatingSystemModelCreator,
    ProgramOnlyResponse,
    TimesResponse,
)
from api_v2.routes.authentication import get_current_active_user, get_current_user

router = APIRouter(prefix="/v2")


@router.get("/heating")
async def get_heating_info(
    system_id: Optional[int] = None, user: HouseholdMember = Depends(get_current_user)
):
    if system_id is not None:
        hs = await get_system_from_memory_http(system_id, user.household_id)
        system_info = SystemInfo(
            sensor_readings=hs.get_measurements(),
            relay_on=hs.relay_state,
            program_on=hs.program_on,
            target=hs.current_period.target if hs.current_period else 5,
        )
        return system_info
    response = HeatingV2Response()
    household = await Household.get(id=user.household_id)
    await household.fetch_related("heating_systems")
    for system_from_db in household.heating_systems:
        if system_from_db.activated:
            system = await get_system_instance_from_memory(
                system_from_db.system_id, user.household_id
            )
            system_info = SystemInfo(
                sensor_readings=system.get_measurements(),
                relay_on=system.relay_state,
                program_on=system.program_on,
                target=system.current_period.target if system.current_period else 5,
            )
            response.systems.append(system_info)
    return response


@router.get("/heating/program")
async def heating_on_off(
    system_id: int, user: HouseholdMember = Depends(get_current_active_user)
):
    hs = await get_system_from_memory_http(system_id, user.household_id)

    if not hs.program_on:
        await hs.turn_program_on()
    else:
        await hs.turn_program_off()
    return ProgramOnlyResponse(program_on=hs.program_on, relay_on=hs.relay_state)


@router.get("/heating/times")
async def get_heating_periods(
    user: HouseholdMember = Depends(get_current_active_user),
):
    return TimesResponse(
        periods=[
            PHeatingPeriod(**period.dict(exclude_unset=True))
            for period in await get_times(user.household_id)
        ]
    )


@router.post("/heating/times")
async def new_period(
    period: PHeatingPeriod,
    user: HouseholdMember = Depends(get_current_active_user),
):
    try:
        return await new_time(user.household_id, period, user.id)
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.delete("/heating/times")
async def delete_period(
    period_id: int,
    user: HouseholdMember = Depends(get_current_active_user),
):
    return await delete_time(period_id=period_id)


@router.put("/heating/times")
async def update_time(
    period_id: int,
    period: PHeatingPeriod,
    user: HouseholdMember = Depends(get_current_active_user),
):
    p = await HeatingPeriod.get(period_id=period_id)
    p.__dict__.update(**period.dict(exclude_unset=True))
    await p.save()
    return await HeatingPeriodModelCreator.from_tortoise_orm(p)


@router.post("/heating/system")
async def new_heating_system(
    system: PHeatingSystemIn,
    user: HouseholdMember = Depends(get_current_active_user),
):
    system = await create_system(system, user.household_id)
    return await HeatingSystemModelCreator.from_tortoise_orm(system)


@router.put("/heating/system")
async def update_heating_system(
    system_id: int,
    system_in: PHeatingSystemIn,
    user: HouseholdMember = Depends(get_current_active_user),
):
    system = await get_system(system_id)
    system.__dict__.update(
        **system_in.dict(exclude_unset=True), household_id=user.household_id
    )
    await system.save()
    return await HeatingSystemModelCreator.from_tortoise_orm(system)


@router.get("/heating/system/start")
async def start_system(
    system_id: int, user: HouseholdMember = Depends(get_current_active_user)
):
    if await create_instance(system_id):
        return {"started": system_id}
    raise HTTPException(404)


@router.get("/heating/system/stop")
async def stop_system(
    system_id: int, user: HouseholdMember = Depends(get_current_active_user)
):
    if await kill_system(system_id):
        return {"deleted": system_id}
    raise HTTPException(404)
