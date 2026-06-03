

class AsyncBatchManager:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def worker(self):
        while not self.queue.empty():
            task = await self.queue.get()
            # Logic to execute task
            self.queue.task_done()