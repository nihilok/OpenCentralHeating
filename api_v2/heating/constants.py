from ..secrets import initialized_config as config

WEATHER_URL = (
    "https://api.openweathermap.org/data/2.5/onecall?lat=51.6862"
    "&lon=-1.4129&exclude=minutely,hourly&units=metric"
    f"&appid={config['HEATING'].get('openweathermap_api_key', '')}"
)  # CHANGE THIS FOR WEATHER

TESTING = False
