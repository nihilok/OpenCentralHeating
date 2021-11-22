from dataclasses import dataclass

from .models import HeatingConf


@dataclass
class HeatingSystem:
    gpio_pin: int
    temperature_url: str
    conf = HeatingConf(
        target="20",
        on_1="08:30",
        off_1="10:30",
        on_2="18:30",
        off_2="22:30",
        program_on=True,
    )
    advance_on = None

    @property
    def temperature(self):
        return float(self.conf.target)

    @property
    def measurements(self):
        return {'temperature': self.temperature, 'pressure': 0, 'humidity': 0}

    @property
    def relay_state(self):
        return self.conf.program_on

    def program_on(self):
        self.conf.program_on = True

    def program_off(self):
        self.conf.program_on = False