import asyncio
import json

# import time
import logging
from typing import Optional

import pigpio
import requests

from .fake_pi import fake_pi
from .manage_times import check_times, get_times, new_time
from ..models import PHeatingPeriod
from ..utils import send_telegram_message  # , BritishTime
from ..logger import get_logger
from ..secrets import initialized_config as config


logger = get_logger(__name__, level=logging.INFO)


class HeatingSystem:
    config = config["HEATING"]
    THRESHOLD = 0.2
    PROGRAM_LOOP_INTERVAL = 60
    MINIMUM_TEMP = 5
    PIN_STATE_ON = 0

    def __init__(
        self,
        gpio_pin: int,
        temperature_url: str,
        system_id: int,
        household_id: int,
        test: bool = False,
        raspberry_pi_ip: Optional[str] = None,
    ):
        logger.info(
            f"Creating new instance of HeatingSystem\n"
            f"\t  (GPIO_PIN: {gpio_pin}, TEMPERATURE_URL: {temperature_url})"
        )
        if test:
            self.pi = fake_pi()
        elif raspberry_pi_ip is None:
            self.pi = pigpio.pi()
        else:
            self.pi = pigpio.pi(raspberry_pi_ip)
        self.gpio_pin = gpio_pin
        self.temperature_url = temperature_url
        self.errors = {"temporary": False, "initial": False}
        self.system_id = system_id
        self.measurements = None
        self.program_on = json.loads(self.config.get("program_on", "false"))
        # self.advance_on = None
        # self.advance_end: int = 0
        self.household_id = household_id
        self.current_period = None
        loop = asyncio.get_running_loop()
        loop.create_task(self.main_loop(self.PROGRAM_LOOP_INTERVAL))

    def get_measurements(self) -> dict:
        try:
            res = requests.get(self.temperature_url, timeout=5)
            if res.status_code == 200:
                self.reset_error_state()
            return res.json()
        except Exception as e:
            self.handle_request_errors(e)

    def handle_request_errors(self, e):
        log_msg = None
        if self.measurements is None:
            if self.errors["initial"]:
                return
            self.errors["initial"] = True
            log_msg = (
                f"{__name__}: {e.__class__.__name__}: {str(e)} ({self.temperature_url})"
            )
        elif not self.errors["temporary"]:
            self.errors["temporary"] = True
            log_msg = (
                f"{__name__}: {e.__class__.__name__}: {str(e)} ({self.temperature_url})"
            )
        if log_msg is not None:
            logger.error(log_msg)
            send_telegram_message(log_msg)
            self.switch_off_relay()
            raise e

    def reset_error_state(self):
        previous = False
        for key in self.errors.keys():
            if self.errors[key]:
                previous = True
                self.errors[key] = False
        if previous:
            send_telegram_message(f"Contact with {self.temperature_url} resumed")
            logger.warning(f"Contact with {self.temperature_url} resumed")

    @property
    def temperature(self) -> float:
        self.measurements = self.get_measurements()
        if self.measurements is not None:
            return float(self.measurements.get("temperature", 0))

    @property
    def relay_state(self) -> bool:
        state = self.pi.read(self.gpio_pin)
        return not state if self.PIN_STATE_ON == 0 else not not state

    @property
    def too_cold(self) -> Optional[bool]:
        if self.current_period is not None:
            target = self.current_period.target
        else:
            target = self.MINIMUM_TEMP
        try:
            current = self.temperature
            if target - self.THRESHOLD > current:
                return True
            elif target <= current:
                return False
        except requests.exceptions.ConnectTimeout:
            return

        msg = f"target: {target}, current: {current}"
        logger.debug(msg)

    def switch_on_relay(self):
        if not self.relay_state:
            logger.debug("Switching on relay")
            self.pi.write(self.gpio_pin, self.PIN_STATE_ON)

    def switch_off_relay(self):
        if self.relay_state:
            logger.debug("Switching off relay")
            self.pi.write(self.gpio_pin, 1 if self.PIN_STATE_ON == 0 else 0)

    async def thermostat_control(self):
        check = self.too_cold
        if check is True:
            logger.debug("too cold")
            self.switch_on_relay()
        elif not check:
            logger.debug("warm enough")
            self.switch_off_relay()

    async def main_task(self):
        logger.debug("Performing main task")
        if self.program_on:
            await self.get_current_time_period()
        await self.thermostat_control()

    async def main_loop(self, interval: int = 60):
        logger.info("Main loop starting")
        while True:
            await self.main_task()
            await asyncio.sleep(interval)

    async def turn_program_on(self):
        self.program_on = True
        await self.main_task()

    async def turn_program_off(self):
        self.program_on = False
        self.current_period = None
        await self.main_task()

    # async def advance(self, mins: int = 30):
    #     self.advance_on = time.time()
    #     self.advance_end = self.advance_on + mins * 60
    #     while self.advance_end > time.time():
    #         if await self.within_time_period() or not self.advance_on:
    #             await self.cancel_advance()
    #             break
    #         await self.thermostat_control()
    #         await asyncio.sleep(60)
    #
    # async def start_advance(self, mins: int = 30):
    #     if self.advance_on:
    #         logger.info(
    #             f"Advance requested when already started "
    #             f"(started at {BritishTime.fromtimestamp(self.advance_on).strftime('%Y-%m-%d %H:%M:%S')})"
    #         )
    #         return self.advance_on
    #     loop = asyncio.get_running_loop()
    #     loop.create_task(self.advance(mins))
    #     while not self.advance_on and not self.advance_end:
    #         await asyncio.sleep(0.1)
    #     logger.info(
    #         f"Advance started (scheduled until {BritishTime.fromtimestamp(self.advance_end).strftime('%H:%M:%S')})"
    #     )
    #     return self.advance_on
    #
    # async def cancel_advance(self):
    #     if self.advance_on:
    #         self.advance_on = None
    #         self.advance_end = 0
    #         logger.info("Advance cancelled")
    #     await self.main_task()

    async def get_current_time_period(self):
        logger.debug("Checking times")
        times = await get_times(self.household_id)
        self.current_period = await check_times(times, self.system_id)
        if self.current_period is not None:
            logger.debug(
                f"{self.current_period.time_on}->{self.current_period.time_off} ({self.current_period.target}'C)"
            )
            # if self.advance_on:
            #     await self.cancel_advance()

    async def new_time(self, period: PHeatingPeriod, user_id: int):
        _time = await new_time(self.household_id, period, user_id)
        _check = await check_times([_time], self.system_id)
        if _check:
            self.current_period = _check
        return _time
