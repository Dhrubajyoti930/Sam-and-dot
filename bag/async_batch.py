import asyncio
import time
from google import genai

class AsyncWorkerPool:

async def execute(tasks):
    worker = AsyncWorkerPool()
    results = await worker.batch_execute(tasks)
    return [r if not isinstance(r, Exception) else None for r in results]

if __name__ == "__main__":
    import asyncio
    async def mock_task(n): return n * 2
    tasks = [mock_task(i) for i in range(5)]
    print(asyncio.run(execute(tasks)))
    def __init__(self, concurrency=3):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.queue = asyncio.Queue()

    async def run_task(self, coro):
        async with self.semaphore:
            return await coro

    async def batch_execute(self, tasks):
        return await asyncio.gather(*[self.run_task(t) for t in tasks], return_exceptions=True)