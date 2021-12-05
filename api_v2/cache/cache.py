import asyncio

import aioredis

from api_v2.logger import get_logger

cache_singleton = None

logger = get_logger(__name__)


class RedisCache:

    cache = None

    def __init__(self):
        if cache_singleton is not None:
            logger.debug("Cache already exists")
            self.cache = cache_singleton
            self.ready = True
            return
        self.ready = False
        loop = asyncio.get_running_loop()
        task = loop.create_task(self.__async_init__())
        task.add_done_callback(self.set_ready)

    async def __async_init__(self):
        self.cache = await aioredis.create_redis_pool("redis://localhost")

    def set_ready(self, *args):
        global cache_singleton
        self.ready = True
        cache_singleton = self.cache

    async def set_item(self, key, value):
        await self.cache.set(key, value)

    async def get_item(self, key):
        return await self.cache.get(key, encoding="utf-8")

    async def get_keys(self):
        return await self.cache.keys("*", encoding="utf-8")

    async def delete_key(self, key):
        await self.cache.delete(key)

    async def execute(self, *args, **kwargs):
        self.cache.execute(*args, **kwargs)


async def init_cache():
    if cache_singleton is None:
        RedisCache()
