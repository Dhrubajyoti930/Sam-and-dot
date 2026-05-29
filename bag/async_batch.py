import asyncio
import time
from google import genai

class AsyncWorkerPool:
    def __init__(self, concurrency=3):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.queue = asyncio.Queue()

    async def run_task(self, coro):
        async with self.semaphore:
            return await coro

    async def batch_execute(self, tasks):
        return await asyncio.gather(*[self.run_task(t) for t in tasks], return_exceptions=True)