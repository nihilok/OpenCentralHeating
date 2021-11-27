import calendar
import time
from datetime import datetime

from api.heating.times.models import HeatingPeriodModel, HeatingPeriod, HeatingPeriodModelCreator


async def _new_time(household_id: int, period: HeatingPeriodModel):
    query = HeatingPeriod.filter(household_id=household_id)
    for p in await HeatingPeriodModelCreator.from_queryset(query):
        if period.time_on <= p.time_on < period.time_off:
            for day in period.days.dict().items():
                if day[1]:
                    if p.days[day[0]]:
                        raise ValueError("New period overlaps with another")
    new_period = await HeatingPeriod.create(household_id=household_id, **period.dict(exclude_unset=True))
    return await HeatingPeriodModelCreator.from_tortoise_orm(new_period)


async def _delete_time(period_id: int):
    period = await HeatingPeriod.get(period_id=period_id)
    await period.delete()
    return {}


def get_weekday():
    weekday = datetime.today().weekday()
    return calendar.day_name[weekday].lower()


def _check_times(times):
    weekday = get_weekday()
    now = time.time()
    for _time in sorted(times, key=lambda x: x.time_on):
        for day, checked in _time.days.dict().items():
            if checked and day == weekday:
                if _time.time_on < now < _time.time_off:
                    return True
    return False
