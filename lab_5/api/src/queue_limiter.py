import time
import threading
import asyncio

from queue import Queue
import aiohttp

limit = 0


class QueueLimiter:
    def __init__(self, requests_per_minute):
        self.requests_per_minute = requests_per_minute
        
        self.request_queue = Queue()
        self.results = {}
        self.last_reset_time = time.time()
        self.lock = threading.Lock()

        threading.Thread(target=asyncio.run, args=(self._process_queue(),)).start()
        threading.Thread(target=asyncio.run, args=(self._reset_limit(),)).start()

    async def _reset_limit(self):
        global limit
        while True:
            if time.time() - self.last_reset_time >= 60:
                limit = 0
                self.last_reset_time = time.time()
            await asyncio.sleep(1)

    async def _process_queue(self):
        global limit
        while True:
            if limit >= self.requests_per_minute:
                await asyncio.sleep(1)
            else:
                with self.lock:
                    if not self.request_queue.empty():
                        limit += 1
                        request = self.request_queue.get()
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'http://nginx:8080/calculate', params=request['params']) as resp:
                                self.results[request['id']] = await resp.json()
                    else:
                        await asyncio.sleep(1)

    def make_request(self, request):
        self.request_queue.put(request)
        request_id = request['id']

        while True:
            result = self.results.get(request_id)
            if result:
                break
            else: time.sleep(1)

        del self.results[request_id]

        return result
