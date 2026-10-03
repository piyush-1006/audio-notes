import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import httpx

# Load variables from backend/.env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GNANI_API_KEY = os.getenv("GNANI_API_KEY")

if not GNANI_API_KEY or GNANI_API_KEY == "your_gnani_api_key":
    print("[-] Error: GNANI_API_KEY is not configured in backend/.env")
    sys.exit(1)

# Endpoint: Gnani REST ASR API (Vachana Platform)
GNANI_URL = "https://api.vachana.ai/stt/v3"

def test_gnani_transcription(audio_file_path: str):
    if not os.path.exists(audio_file_path):
        print(f"[-] File not found: {audio_file_path}")
        return

    print(f"[+] Testing Gnani ASR with file: {audio_file_path}")
    headers = {
        "X-API-Key-ID": GNANI_API_KEY,
    }

    start_time = time.time()
    try:
        with open(audio_file_path, "rb") as f:
            # Note the key must be 'audio_file'
            files = {"audio_file": (os.path.basename(audio_file_path), f, "audio/wav")}
            data = {"language_code": "en-IN"}

            response = httpx.post(
                GNANI_URL,
                headers=headers,
                data=data,
                files=files,
                timeout=60.0
            )

        elapsed = time.time() - start_time
        print(f"[+] HTTP Status: {response.status_code}")
        print(f"[+] Elapsed Time: {elapsed:.2f} seconds")
        print(f"[+] Response Body:\n{response.text}\n")

    except httpx.RequestError as exc:
        print(f"[-] Network/Request error: {exc}")
    except Exception as e:
        print(f"[-] Unexpected error: {e}")

if __name__ == "__main__":
    # CHANGE THIS LINE to use your new speech file
    test_file = Path(__file__).resolve().parent / "test_speech.wav"
    test_gnani_transcription(str(test_file))