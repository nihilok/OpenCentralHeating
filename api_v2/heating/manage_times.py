import calendar

from api_v2.utils import BritishTime
from api_v2.models import PHeatingPeriod, HeatingPeriod, HeatingPeriodModelCreator


async def get_times(household_id: int):
    return await HeatingPeriod.filter(household_id=household_id)


async def new_time(household_id: int, period: PHeatingPeriod, user_id: int):
    for p in await HeatingPeriod.filter(household_id=household_id):
        if p.heating_system_id == period.heating_system_id:
            if period.time_on <= p.time_on < period.time_off:
                for day in period.days.dict().items():
                    if day[1]:
                        if p.days[day[0]]:
                            raise ValueError("New period overlaps with another")
    new_period = await HeatingPeriod.create(
        household_id=household_id,
        created_by_id=user_id,
        **period.dict(exclude_unset=True),
    )
    return await HeatingPeriodModelCreator.from_tortoise_orm(new_period)


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
