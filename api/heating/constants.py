import configparser
import os
from pathlib import Path

config = configparser.ConfigParser()
path = Path(os.getcwd())
config_path = os.path.join(path, "api/secrets/secrets.ini")
config.read(config_path)


WEATHER_URL = "https://api.openweathermap.org/data/2.5/onecall?lat=51.6862" \
              "&lon=-1.4129&exclude=minutely,hourly&units=metric" \
              "&appid=<<OpenWeatherMap APP_IP>>"    # CHANGE THIS FOR WEATHER

TEMPERATURE_URL = config['HEATING'].get('temperature_url', None) or 'https://api.example.com'

RASPBERRY_PI_IP = config['HEATING'].get('raspberry_pi_ip', None)

GPIO_PIN = 27

TESTING = not bool(RASPBERRY_PI_IP) or True
