import asyncio
import time
from fastapi import FastAPI, Request, HTTPException, File, UploadFile
import httpx
from configs import SER_URL, STT_URL
import subprocess
import tempfile
import shutil
import google.auth.transport.requests
import google.oauth2.id_token
import requests

app = FastAPI()


def save_upload_file_to_temp(upload_file: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        upload_file.file.seek(0)
        shutil.copyfileobj(upload_file.file, temp_file)
        temp_file_path = temp_file.name
    return temp_file_path


def generate_token(url: str):
    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)
    return id_token


# def generate_token():
#     """Generates GCP identity token for authentication."""
#     command = ["gcloud", "auth", "print-identity-token"]
#     token = subprocess.check_output(command).decode("utf-8").strip()
#     print("GCP identity token generated. ✔️")
#     return token


async def call_api_with_file(url: str, token: str, file: UploadFile):
    temp_filepath = save_upload_file_to_temp(file)

    with open(temp_filepath, "rb") as audio_file:
        # Create a dictionary of files to be uploaded
        files = {
            "file": (temp_filepath.split("/")[-1], audio_file, "audio/mpeg")
        }
        headers = {
            "Authorization": f"Bearer {token}"
        }
        print(type(audio_file))

        # files = {'file': open(temp_filepath, 'rb')}

        response = requests.post(url, headers=headers, files=files)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print("made the request")
        return response.json()
    return {}


@app.post("/translate/")
async def translate(request: Request, file: UploadFile = File(...)):
    # auth_header = request.headers.get("Authorization")

    # token = auth_header[len("Bearer "):]
    # print(token)
    start_time = time.time()
    ser_response, stt_response = await asyncio.gather(
        call_api_with_file(SER_URL, generate_token(SER_URL), file),
        call_api_with_file(STT_URL, generate_token(STT_URL), file)
    )
    end_time = time.time()
    processing_time = end_time - start_time
    return {
        "processing_time_seconds": processing_time,
        "ser": ser_response,
        "stt": stt_response
    }


@app.post("/simple_translate/")
async def simple_translate(request: Request, file: UploadFile = File(...)):
    temp_filepath = save_upload_file_to_temp(file)

    with open(temp_filepath, "rb") as audio_file:
        # Create a dictionary of files to be uploaded
        files = {
            "file": (temp_filepath.split("/")[-1], audio_file, "audio/mpeg")
        }
        headers = {
            "Authorization": f"Bearer {generate_token()}"
        }
        print(type(audio_file))

        # files = {'file': open(temp_filepath, 'rb')}
    
        response = requests.post(STT_URL, headers=headers, files=files)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print("made the request")
        return response.json()
    return {}

