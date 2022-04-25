import json

from .cache import RedisCache, cache_singleton


async def check_create_cache():
    if cache_singleton is None:
        global cache
        cache = RedisCache()


async def set_weather(weather_dict: dict):
    await check_create_cache()
    await cache.execute("set", "weather", json.dumps(weather_dict), "ex", 900)


async def get_weather():
    await check_create_cache()
    w = await cache.get_item("weather")
    if w:
        return json.loads(w)
