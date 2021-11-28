import asyncio
import json
import time
import calendar
from datetime import datetime
from typing import Optional

import pigpio
import requests

from .custom_datetimes import BritishTime
from .fake_pi import fake_pi
from ..utils import send_telegram_message
from ..models import HeatingPeriod, HeatingPeriodModelCreator, HeatingPeriodModel
from ..logger import get_logger
from ..secrets import initialized_config as config


logger = get_logger(__name__)


async def _new_time(household_id: int, period: HeatingPeriodModel, user_id: int):
    query = HeatingPeriod.filter(household_id=household_id)
    for p in await HeatingPeriodModelCreator.from_queryset(query):
        if period.time_on <= p.time_on < period.time_off:
            for day in period.days.items():
                if day[1]:
                    if p.days[day[0]]:
                        raise ValueError("New period overlaps with another")
    new_period = await HeatingPeriod.create(household_id=household_id, created_by_id=user_id, **period.dict(exclude_unset=True))
    return await HeatingPeriodModelCreator.from_tortoise_orm(new_period)


async def _delete_time(period_id: int):
    period = await HeatingPeriod.get(period_id=period_id)
    await period.delete()
    return {}


def get_weekday():
    weekday = BritishTime.today().weekday()
    return calendar.day_name[weekday].lower()


async def _check_times(times):
    weekday = get_weekday()
    now = datetime.now().time()
    logger.debug(f'{len(times)} found')
    for _time in sorted(times, key=lambda x: x.time_on):
        for day, checked in _time.days.items():
            if checked and day == weekday:
                time_on = datetime.strptime(_time.time_on, '%H:%M').time()
                time_off = datetime.strptime(_time.time_off, '%H:%M').time()
                if time_on < now < time_off:
                    return _time


class HeatingSystem:
    config = config['HEATING']
    THRESHOLD = 0.2
    PROGRAM_LOOP_INTERVAL = 60
    MINIMUM_TEMP = 5

    def __init__(
        self,
        gpio_pin: int,
        temperature_url: str,
        test: bool = False,
        raspberry_pi_ip: Optional[str] = None,
        household_id: Optional[int] = None,
    ):
        """Create connection with temperature api and load settings
        from config file"""
        logger.info(
            f"Creating new instance of HeatingSystem\n(GPIO_PIN: {gpio_pin}, TEMPERATURE_URL: {temperature_url})"
        )
        if test:
            self.pi = fake_pi()
        elif raspberry_pi_ip is None:
            self.pi = pigpio.pi()
        else:
            self.pi = pigpio.pi(raspberry_pi_ip)
        self.gpio_pin = gpio_pin
        self.temperature_url = temperature_url
        self.error: list[bool, bool] = [False, False]
        self.measurements = self.get_measurements()
        self.program_on = json.loads(self.config.get('program_on', 'false'))
        self.advance_on = None
        self.advance_end: int = 0
        self.thread = None
        self.household_id = household_id
        self.current_period = None
        loop = asyncio.get_running_loop()
        loop.create_task(self.main_loop(self.PROGRAM_LOOP_INTERVAL))

    def get_measurements(self) -> dict:
        """Gets measurements from temperature sensor and handles errors,
        by returning the last known set of measurements or a default"""
        try:
            req = requests.get(self.temperature_url)
            if req.status_code == 200 and any(self.error):
                self.error = [False, False]
            self.measurements = req.json()
        except Exception as e:
            if not self.error[0]:
                log_msg = f"{__name__}: {e.__class__.__name__}: {str(e)}"
                logger.error(log_msg)
                send_telegram_message(log_msg)
                self.error[0] = True
        try:
            return self.measurements
        except AttributeError as e:
            if not self.error[1]:
                log_msg = f"{__name__}: {e.__class__.__name__}: No measurements found on first load"
                logger.error(log_msg)
                send_telegram_message(log_msg)
                self.error[1] = True
                logger.warning("Using default measurements")
            return {"temperature": 20, "pressure": 0, "humidity": 0}

    @property
    def temperature(self) -> float:
        return float(self.get_measurements()["temperature"])

    @property
    def relay_state(self) -> bool:
        return not not self.pi.read(self.gpio_pin)

    async def within_time_period(self):
        if not self.program_on:
            return False
        return await self.complex_check_time()

    @property
    def too_cold(self) -> Optional[bool]:
        if self.current_period is not None:
            target = self.current_period.target
        else:
            target = self.MINIMUM_TEMP
        current = self.temperature
        msg = f"target: {target}, current: {current}"
        logger.debug(msg)
        if target - self.THRESHOLD > current:
            return True
        elif target <= current:
            return False

    def switch_on_relay(self):
        if not self.relay_state:
            logger.debug("Switching on relay")
            self.pi.write(self.gpio_pin, 1)

    def switch_off_relay(self):
        if self.relay_state:
            logger.debug("Switching off relay")
            self.pi.write(self.gpio_pin, 0)

    async def thermostat_control(self):
        check = self.too_cold
        if check is True:
            logger.debug("too cold")
            self.switch_on_relay()
        elif check is False:
            logger.debug("warm enough")
            self.switch_off_relay()

    async def main_task(self):
        """If time is within range, turn on relay if temp is below range,
        turn off if above range."""
        logger.debug('Performing main task')
        time = await self.within_time_period()
        if time is not None:
            if self.advance_on:
                await self.cancel_advance()
            await self.thermostat_control()

    async def main_loop(self, interval: int = 60):
        logger.info("Main loop starting")
        while True:
            await self.main_task()
            await asyncio.sleep(interval)

    def turn_program_on(self):
        self.program_on = True

    def turn_program_off(self):
        self.program_on = False
        self.current_period = None
        if not self.advance_on:
            self.switch_off_relay()

    async def advance(self, mins: int = 30):
        self.advance_on = time.time()
        self.advance_end = self.advance_on + mins * 60
        while self.advance_end > time.time():
            if await self.within_time_period() or not self.advance_on:
                await self.cancel_advance()
                break
            await self.thermostat_control()
            await asyncio.sleep(60)

    async def start_advance(self, mins: int = 30):
        if self.advance_on:
            logger.info(
                f"Advance requested when already started "
                f"(started at {BritishTime.fromtimestamp(self.advance_on).strftime('%Y-%m-%d %H:%M:%S')})"
            )
            return self.advance_on
        loop = asyncio.get_running_loop()
        loop.create_task(self.advance(mins))
        while not self.advance_on and not self.advance_end:
            await asyncio.sleep(0.1)
        logger.info(
            f"Advance started (scheduled until {BritishTime.fromtimestamp(self.advance_end).strftime('%H:%M:%S')})"
        )
        return self.advance_on

    async def cancel_advance(self):
        if self.advance_on:
            self.advance_on = None
            self.advance_end = 0
            logger.info("Advance cancelled")
        await self.main_task()

    async def complex_check_time(self):
        logger.debug('Checking times')
        times = await self.get_times()
        self.current_period = await _check_times(times)
        if self.current_period is not None:
            logger.debug(f"{self.current_period.time_on}->{self.current_period.time_off} ({self.current_period.target}'C)")
            return True
        return False

    async def new_time(self, period: HeatingPeriodModel, user_id: int):
        return await _new_time(self.household_id, period, user_id)

    @staticmethod
    async def remove_time(period_id: int):
        return await _delete_time(period_id)

    async def get_times(self):
        return await HeatingPeriodModelCreator.from_queryset(
            HeatingPeriod.filter(household_id=self.household_id)
        )
