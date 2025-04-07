import asyncio
import time
from fastapi import FastAPI, Request, File, UploadFile
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


def generate_token_in_gcp_env(url: str):
    """This function generates a token while inside GCP cloud run."""
    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)
    return id_token


def generate_token():
    """Generates GCP identity token for authentication. This is used for local
    testing."""
    command = ["gcloud", "auth", "print-identity-token"]
    token = subprocess.check_output(command).decode("utf-8").strip()
    print("GCP identity token generated. ✔️")
    return token


async def call_api_with_audio_file(url: str, token: str, file: UploadFile):
    temp_filepath = save_upload_file_to_temp(file)
    with open(temp_filepath, "rb") as audio_file:
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
    """API endpoint, which performs SER and STT at the same time."""
    start_time = time.time()
    ser_token = generate_token_in_gcp_env(SER_URL)
    stt_token = generate_token_in_gcp_env(STT_URL)
    ser_response, stt_response = await asyncio.gather(
        call_api_with_audio_file(SER_URL, ser_token, file),
        call_api_with_audio_file(STT_URL, stt_token, file)
    )
    end_time = time.time()
    processing_time = end_time - start_time
    return {
        "total_processing_time": processing_time,
        "ser": ser_response,
        "stt": stt_response
    }
