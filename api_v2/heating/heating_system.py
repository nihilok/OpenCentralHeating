import asyncio
import json
from json import JSONDecodeError

from typing import Optional

import pigpio
import os
from pathlib import Path
from .fake_pi import fake_pi
from .manage_times import check_times, get_times, new_time
from ..models import PHeatingPeriod
from ..utils import get_json
from ..logger import get_logger
from api_v2.settings import GLOBAL_LOG_LEVEL

logger = get_logger(__name__, level=GLOBAL_LOG_LEVEL)


CONFIG_PATH = Path(os.path.dirname(__file__))
CONFIG_FILE = CONFIG_PATH / "config.json"
DEFAULT_CONFIG = {"program_on": []}
DEFAULT_PROGRAM_LOOP_INTERVAL = 60


class HeatingSystem:
    THRESHOLD = 0.2
    MINIMUM_TEMP = 5
    PIN_ON_STATE = 0

    def __init__(
        self,
        gpio_pin: int,
        temperature_url: str,
        system_id: int,
        household_id: int,
        interval: int = DEFAULT_PROGRAM_LOOP_INTERVAL,
        test: bool = False,
        raspberry_pi_ip: Optional[str] = None,
    ):
        logger.info(
            f"Creating new instance of HeatingSystem\n"
            f"(GPIO_PIN: {gpio_pin}, TEMPERATURE_URL: {temperature_url})"
        )
        if test:
            self.pi = fake_pi()
        elif raspberry_pi_ip is None:
            self.pi = pigpio.pi()
        else:
            self.pi = pigpio.pi(raspberry_pi_ip)
        self.gpio_pin = gpio_pin
        self.temperature_url = temperature_url
        self.system_id = system_id
        self.household_id = household_id
        self.measurements = None
        self.current_period = None
        self.thermostat_logging_flag = None
        self.errors = {"temporary": False, "initial": False}
        self.config = self.init_config()
        self.program_on = self.system_was_on()
        loop = asyncio.get_running_loop()
        loop.create_task(self.main_loop(interval))

    @staticmethod
    def init_config():
        try:
            with open(CONFIG_FILE, "r") as c:
                config = json.load(c)
        except (FileNotFoundError, JSONDecodeError):
            with open(CONFIG_FILE, "w") as c:
                json.dump(DEFAULT_CONFIG, c)
        return config

    def system_was_on(self):
        return self.system_id in map(int, self.config["program_on"])

    async def get_measurements(self) -> dict:
        try:
            res = await get_json(self.temperature_url)
            if res.get("temperature"):
                self.reset_error_state()
            return res
        except Exception as e:
            self.handle_request_errors(e)
        return {}

    def handle_request_errors(self, e):
        log_msg = None
        self.switch_off_relay()
        if self.measurements == {}:
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

    def reset_error_state(self):
        previous = False
        for key in self.errors.keys():
            if self.errors[key]:
                previous = True
                self.errors[key] = False
        if previous:
            logger.warning(f"Contact with {self.temperature_url} resumed")

    @property
    def temperature(self) -> [float]:
        temp = self.measurements.get("temperature")
        return float(temp) if temp is not None else None

    @property
    def relay_state(self) -> bool:
        state = self.pi.read(self.gpio_pin)
        return not state if self.PIN_ON_STATE == 0 else not not state

    @property
    def too_cold(self) -> Optional[bool]:
        if self.temperature is None:
            raise Exception(f"No temperature measurement available {self.gpio_pin}")
        if self.current_period is None:
            return self.temperature <= self.MINIMUM_TEMP
        logger.debug(
            f"target: {self.current_period.target}, current: {self.temperature}"
        )
        return self.temperature <= self.current_period.target - self.THRESHOLD

    def switch_on_relay(self):
        if not self.relay_state:
            logger.debug(f"Switching on relay {self.gpio_pin=}")
            self.pi.write(self.gpio_pin, self.PIN_ON_STATE)

    def switch_off_relay(self):
        if self.relay_state:
            logger.debug(f"Switching off relay {self.gpio_pin=}")
            self.pi.write(self.gpio_pin, 1 if self.PIN_ON_STATE == 0 else 0)

    async def thermostat_control(self):
        self.measurements = await self.get_measurements()
        try:
            check = self.too_cold
        except Exception as e:
            logger.warning(e)
            self.switch_off_relay()
            logger.info(f"Error getting temperature {self.gpio_pin=}")
            return
        if self.thermostat_logging_flag is None:
            self.thermostat_logging_flag = not check
        if check is True:
            if self.thermostat_logging_flag is False:
                if self.current_period is not None:
                    logger.info(
                        f"Too cold ({self.measurements['temperature']}°C/{self.current_period.target}°C), "
                        f"switching on relay [pin {self.gpio_pin}]"
                    )
                self.thermostat_logging_flag = True
            self.switch_on_relay()
        elif not check:
            if self.thermostat_logging_flag is True:
                if self.current_period is not None:
                    logger.info(
                        f"Warm enough ({self.measurements['temperature']}°C/{self.current_period.target}°C), "
                        f"switching off relay [pin {self.gpio_pin}]"
                    )
                self.thermostat_logging_flag = False
            self.switch_off_relay()

    async def main_task(self):
        logger.debug(f"Performing main task {self.gpio_pin=}")
        if self.program_on:
            await self.get_current_time_period()
        else:
            self.current_period = None
        await self.thermostat_control()

    async def main_loop(self, interval: int = 60):
        logger.debug(f"Main loop starting {self.gpio_pin=}")
        while True:
            await self.main_task()
            await asyncio.sleep(interval)

    async def turn_program_on(self):
        self.program_on = True
        self.update_config()
        logger.info(f"Program on [pin {self.gpio_pin}]")
        self.thermostat_logging_flag = None
        await self.main_task()

    async def turn_program_off(self):
        self.program_on = False
        self.update_config()
        self.current_period = None
        logger.info(f"Program off [pin {self.gpio_pin}]")
        await self.main_task()

    async def get_current_time_period(self):
        logger.debug("Checking times")
        times = await get_times(self.household_id)
        self.current_period = await check_times(times, self.system_id)
        if self.current_period is not None:
            logger.debug(
                f"{self.current_period.time_on}->{self.current_period.time_off} ({self.current_period.target}°C)"
            )

    async def new_time(self, period: PHeatingPeriod, user_id: int):
        _time = await new_time(self.household_id, period, user_id)
        _check = await check_times([_time], self.system_id)
        if _check:
            self.current_period = _check
        return _time

    def update_config(self):
        if self.program_on and not self.system_was_on:
            self.config["program_on"].append(self.system_id)
        elif not self.program_on and self.system_was_on:
            self.config["program_on"].remove(self.system_id)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)
