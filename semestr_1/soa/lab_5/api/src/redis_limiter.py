import redis.asyncio as redis

class Limiter:
    def __init__(self) -> None:
        self.client = redis.Redis(host="redis-server")

    async def limiter(self, key, limit):
        req = await self.client.incr(key)
        if req == 1:
            await self.client.expire(key, 60)
        return req <= limit
