import pickle
import asyncio
import logging
import aiomcache

from .settings import Settings

settings = Settings()

from .decorators import DummyValue

loop = asyncio.get_event_loop()
log = logging.getLogger('application')

try:
    from io import BytesIO
except ImportError:
    from io import StringIO as BytesIO


class Cache:
    mc = None

    @classmethod
    async def connect(cls):
        log.info('Connecting to memcache')
        cls.mc = aiomcache.Client(host=settings.CACHE_HOST,
                                  port=int(settings.CACHE_PORT),
                                  loop=asyncio.get_event_loop())
        if settings.DEBUG:
            log.info('Debug mode for cache: dummyfying all methods.')
            cls.set = lambda x, y, z: None
            cls.get = lambda x: None
            cls.add = lambda x, y, z: None
            cls.delete = lambda x: None
        log.info('Connected to memcache')

    @classmethod
    async def set(cls, key, value, expired_time=0):
        key = str(key).encode()
        value = pickle.dumps(value)
        res = await cls.mc.set(key, value, exptime=expired_time)
        if not res:
            log.exception("Error setting cache")

    @classmethod
    async def add(cls, key, value, expired_time=0):
        key = str(key).encode()
        value = pickle.dumps(value)
        res = await cls.mc.add(key, value, expired_time)
        return res

    @classmethod
    async def delete(cls, key):
        key = str(key).encode()
        res = await cls.mc.delete(key)
        if not res:
            log.exception("Error deleting cache")

    @classmethod
    async def get(cls, key):
        key = str(key).encode()
        res = await cls.mc.get(key)
        if res:
            res = pickle.loads(res)
        return res

