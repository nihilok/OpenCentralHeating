import asyncio
import json
import os
import time
from datetime import datetime
from typing import Optional

import pigpio
import requests
from fastapi.encoders import jsonable_encoder

from .custom_datetimes import BritishTime
from .models import HeatingConf, Advance
from .telegram_bot import send_message
from ..logger import get_logger

logger = get_logger(__name__)


class HeatingSystem:
    config_file = os.path.abspath(os.getcwd()) + "/api/heating/heating.conf"
    THRESHOLD = 0.2
    PROGRAM_LOOP_INTERVAL = 60

    def __init__(
        self, gpio_pin: int, temperature_url: str, raspberry_pi_ip: Optional[str] = None
    ):
        """Create connection with temperature api and load settings
        from config file"""
        if raspberry_pi_ip is None:
            self.pi = pigpio.pi()
        else:
            self.pi = pigpio.pi(raspberry_pi_ip)
        self.gpio_pin = gpio_pin
        self.temperature_url = temperature_url
        self.error: list[bool, bool] = [False, False]
        self.conf = self.get_or_create_config()
        self.measurements = self.get_measurements()
        self.advance_on = None
        self.thread = None
        if self.conf.program_on:
            self.program_on()
        else:
            self.program_off()

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
                send_message(log_msg)
                self.error[0] = True
        try:
            return self.measurements
        except AttributeError as e:
            if not self.error[1]:
                log_msg = f"{__name__}: {e.__class__.__name__}: No measurements found on first load"
                logger.error(log_msg)
                send_message(log_msg)
                self.error[1] = True
                logger.warning('Using default measurements')
            return {"temperature": 20, "pressure": 0, "humidity": 0}

    def get_or_create_config(self):
        try:
            with open(self.config_file, "r") as f:
                file_dict = json.load(f)
                conf = HeatingConf(**file_dict)
            logger.info('Config loaded from file')
        except Exception as e:
            logger.error(str(e))
            conf = HeatingConf(
                target=20,
                on_1="06:30",
                off_1="08:30",
                on_2="20:30",
                off_2="22:30",
                program_on=True,
                advance_on=Advance(on=False),
            )
            with open(self.config_file, "w") as f:
                json.dump(jsonable_encoder(conf), f)
            logger.warning('New config created from scratch')
        return conf

    @property
    def temperature(self) -> float:
        return float(self.get_measurements()["temperature"])

    @property
    def relay_state(self) -> bool:
        return not not self.pi.read(self.gpio_pin)

    @property
    def within_program_time(self) -> bool:
        if not self.conf.program_on:
            return False
        time_now = BritishTime.now().time()
        try:
            if (
                self.parse_time(self.conf.off_1)
                > time_now
                > self.parse_time(self.conf.on_1)
            ):
                return True
            elif not self.conf.on_2:
                return False
            elif (
                self.parse_time(self.conf.off_2)
                > time_now
                > self.parse_time(self.conf.on_2)
            ):
                return True
        except ValueError:
            logger.warning(
                f"ValueError while checking time (times: {self.conf.on_1, self.conf.off_1, self.conf.on_2, self.conf.off_2})"
            )
            return False

    @property
    def too_cold(self) -> Optional[bool]:
        target = float(self.conf.target)
        current = self.temperature
        msg = f"target: {target}, current: {current}"
        logger.debug(msg)
        if target - self.THRESHOLD > current:
            return True
        elif target <= current:
            return False

    @staticmethod
    def parse_time(time_: str) -> datetime.time:
        return datetime.strptime(time_, "%H:%M").time()

    def change_times(self, on1, off1, on2=None, off2=None):
        """Accept times in format HH:MM or None for set 2"""
        self.conf.on_1 = on1
        self.conf.off_1 = off1
        self.conf.on_2 = on2
        self.conf.off_2 = off2
        self.save_state()
        logger.info(
            f"Program changed: new time{'s' if on2 else ''} "
            f"{on1}->{off1}{f', {on2}->{off2}' if on2 else ''}"
        )

    def change_temp(self, temp: int):
        self.conf.target = temp
        self.save_state()
        logger.info(f"Target temperature changed: new temp: {temp}'C")

    def switch_on_relay(self):
        if not self.relay_state:
            logger.debug("Switching on relay")
            self.pi.write(self.gpio_pin, 1)

    def switch_off_relay(self):
        if self.relay_state:
            logger.debug("Switching off relay")
            self.pi.write(self.gpio_pin, 0)

    def save_state(self):
        with open(self.config_file, "w") as f:
            json.dump(jsonable_encoder(self.conf), f)

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
        if self.within_program_time:
            await self.thermostat_control()
        else:
            if not self.advance_on:
                self.switch_off_relay()

    async def backup_task(self):
        """Turns on heating if house is below 5'C to prevent ice damage"""
        temp = float(self.temperature)
        if temp < 5:
            logger.info("Frost stat warning (below 5`C)")
            self.switch_on_relay()
        elif temp > 6 and self.relay_state:
            logger.info("Frost stat warning resolved (above 6`C)")
            self.switch_off_relay()

    async def main_loop(self, interval: int = 60):
        logger.info("Main loop starting")
        while self.conf.program_on:
            await self.main_task()
            await asyncio.sleep(interval)
        await self.main_task()
        logger.info("Main loop ended (program off)")

    async def backup_loop(self, interval: int = 300):
        logger.info("Backup loop starting")
        while not self.conf.program_on and not self.advance_on:
            await self.backup_task()
            await asyncio.sleep(interval)
        logger.info("Backup loop ended")

    def program_on(self):
        self.conf.program_on = True
        loop = asyncio.get_running_loop()
        loop.create_task(self.main_loop(self.PROGRAM_LOOP_INTERVAL))
        self.save_state()

    def program_off(self):
        self.conf.program_on = False
        loop = asyncio.get_running_loop()
        loop.create_task(self.backup_loop())
        self.save_state()

    async def advance(self, mins: int = 30):
        if not self.advance_on:
            logger.info("Advance starting")
            self.advance_on = time.time()
            self.conf.advance = Advance(on=True, start=self.advance_on)
            self.save_state()
            check = self.advance_on
            while check > time.time() - (mins * 60):
                if self.within_program_time or not self.advance_on:
                    await self.cancel_advance()
                    break
                await self.thermostat_control()
                await asyncio.sleep(60)
        else:
            logger.info(
                f"Advance requested when already started (started at {BritishTime.fromtimestamp(self.advance_on)})"
            )

    async def start_advance(self, mins: int = 30):
        loop = asyncio.get_running_loop()
        loop.create_task(self.advance(mins))
        while not self.advance_on:
            await asyncio.sleep(0.1)
        logger.info(f"Advance started at {BritishTime.fromtimestamp(self.advance_on)}")
        return self.advance_on

    async def cancel_advance(self):
        self.thread = None
        self.advance_on = None
        self.conf.advance = Advance(on=False)
        await self.main_task()
        logger.info("Advance cancelled")
        self.save_state()
