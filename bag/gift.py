# async_batcher.py — WIP, abandoned mid-cycle
# Trying to batch multiple Gemini calls concurrently instead of sequentially
# Something is wrong with the gather logic — results come back scrambled

import asyncio
import google.generativeai as genai

async def call_gemini_async(model, prompt: str) -> str:
    # TODO: this blocks — needs to be truly async
    response = model.generate_content(prompt)
    return response.text.strip()

async def batch_prompts(model, prompts: list[str]) -> list[str]:
    tasks = [call_gemini_async(model, p) for p in prompts]
    # BUG: results seem out of order sometimes?
    results = await asyncio.gather(*tasks)
    return results

# Never got around to wiring this into sam.py
