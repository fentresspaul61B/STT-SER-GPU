import asyncio
import time
from fastapi import FastAPI, Request, HTTPException, File, UploadFile
import httpx
from configs import SER_URL, STT_URL

app = FastAPI()


async def call_api_with_file(url: str, token: str, file: UploadFile):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    # Important: reset file pointer to beginning for each API call (?)
    await file.seek(0)
    files = {
        "file": (file.filename, await file.read(), file.content_type)
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, files=files)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error calling {url}: {response.text}"
        )
    return response.json()


@app.post("/translate/")
async def translate(request: Request, file: UploadFile = File(...)):
    token = request.headers.get("Authorization")

    print("My token")

    print(token)

    print(token)
    start_time = time.time()
    ser_response, stt_response = await asyncio.gather(
        call_api_with_file(SER_URL, token, file),
        call_api_with_file(STT_URL, token, file)
    )
    end_time = time.time()
    processing_time = end_time - start_time
    return {
        "processing_time_seconds": processing_time,
        "ser": ser_response,
        "stt": stt_response
    }
