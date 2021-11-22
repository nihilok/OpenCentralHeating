import json
from .redis_funcs import cache, get_item


async def set_weather(weather_dict: dict):
    await cache.execute('set', 'weather', json.dumps(weather_dict), 'ex', 900)


async def get_weather():
    w = await get_item('weather')
    if w:
        return json.loads(w)