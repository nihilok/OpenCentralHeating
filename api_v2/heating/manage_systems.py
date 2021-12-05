from typing import Iterable

from fastapi import HTTPException

from .heating_system import HeatingSystem
from .systems_in_memory import systems_in_memory
from ..models import HeatingSystemModel, PHeatingSystemIn


async def _get_system(system_id: int) -> HeatingSystemModel:
    return await HeatingSystemModel.get_by_system_id(system_id)


async def create_system(system: PHeatingSystemIn, household_id: int) -> HeatingSystemModel:
    return await HeatingSystemModel.create(
        household_id=household_id, **system.dict(exclude_unset=True)
    )


async def create_instance(system_id: int) -> bool:
    model = await _get_system(system_id)
    if not systems_in_memory.get(system_id):
        systems_in_memory[system_id] = HeatingSystem(
            gpio_pin=model.gpio_pin,
            temperature_url=model.sensor_url,
            raspberry_pi_ip=model.raspberry_pi,
            household_id=model.household_id,
            system_id=system_id,
        )
    model.activated = True
    await model.save()
    return True


async def get_system_instance_from_memory(system_id: int, household_id: int) -> HeatingSystem:
    system = systems_in_memory.get(system_id)
    if system:
        if system.household_id == household_id:
            return system
        raise ValueError('Household ID does not match system')
    raise ValueError('System instance does not exist')


async def get_system_from_memory_http(system_id: int, household_id: int):
    try:
        return await get_system_instance_from_memory(system_id, household_id)
    except ValueError as e:
        raise HTTPException(422, str(e))


async def get_all_systems_in_memory() -> Iterable[int]:
    return systems_in_memory.keys()


async def kill_system(system_id: int) -> bool:
    model = await _get_system(system_id)
    model.activated = False
    del systems_in_memory[system_id]
    await model.save()
    return True
