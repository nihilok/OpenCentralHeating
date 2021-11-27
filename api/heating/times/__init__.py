import calendar
import time
from datetime import datetime

from api.heating.times.models import HeatingPeriodModel, HeatingPeriod, HeatingPeriodModelCreator


async def _new_time(household_id: int, period: HeatingPeriodModel):
    new_period = await HeatingPeriod.create(**period.dict(exclude_unset=True), household_id=household_id)
    return HeatingPeriodModelCreator.from_tortoise_orm(new_period)


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
