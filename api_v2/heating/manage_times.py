import calendar
from typing import Optional

from api_v2.utils import BritishTime
from api_v2.models import PHeatingPeriod, HeatingPeriod, HeatingPeriodModelCreator


async def get_times(household_id: int, checking_period: Optional[int] = None):
    qs = HeatingPeriod.filter(household_id=household_id)
    if checking_period is not None:
        qs = qs.exclude(period_id=checking_period)

    return await HeatingPeriodModelCreator.from_queryset(qs)


async def check_conflicts(household_id: int, period: PHeatingPeriod):
    for p in [period for period in await get_times(household_id, period.period_id) if p.heating_system.system_id == period.heating_system_id]:
        start_1, start_2 = p.time_on, period.time_on
        end_1, end_2 = p.time_off, period.time_off
        if (start_1 < end_2) and (end_1 > start_2):
            if len([day for day in period.days.dict().items() if day[1] and p.days[day[0]]]):
                raise ValueError(f"Period overlaps with another")


async def new_time(household_id: int, period: PHeatingPeriod, user_id: int):
    await check_conflicts(household_id, period)
    new_period = await HeatingPeriod.create(
        household_id=household_id,
        created_by_id=user_id,
        **period.dict(exclude_unset=True),
    )
    return await HeatingPeriodModelCreator.from_tortoise_orm(new_period)


async def update_time(household_id: int, period: PHeatingPeriod):
    await check_conflicts(household_id, period)
    p = await HeatingPeriod.get(period_id=period.period_id)
    p.__dict__.update(**period.dict(exclude_unset=True))
    await p.save()
    return p


async def delete_time(period_id: int):
    period = await HeatingPeriod.get(period_id=period_id)
    await period.delete()
    return {}


def get_weekday():
    weekday = BritishTime.today().weekday()
    return calendar.day_name[weekday].lower()


async def check_times(times, system_id):
    weekday = get_weekday()
    now = BritishTime.now().time()
    for _time in sorted(times, key=lambda x: x.time_on):
        if _time.heating_system.system_id == system_id or _time.all_systems:
            for day, checked in _time.days.items():
                if checked and day == weekday:
                    time_on = BritishTime.strptime(_time.time_on, "%H:%M").time()
                    time_off = BritishTime.strptime(_time.time_off, "%H:%M").time()
                    if time_on < now < time_off:
                        return _time
