import httpx

async def ask_gemini_async(prompt: str):
    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.gemini.example/v1", json={"prompt": prompt})
        return response.json()