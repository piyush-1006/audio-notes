import os
import httpx
import google.generativeai as genai
from supabase import create_client
from database import AsyncSessionLocal
from models import AudioJob, JobStatus

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def process_audio_job(job_id: str, filename: str):
    async with AsyncSessionLocal() as db:
        try:
            job = await db.get(AudioJob, job_id)
            if not job:
                return
            job.status = JobStatus.PROCESSING
            await db.commit()

            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
            bucket = os.getenv("SUPABASE_BUCKET", "audio-uploads")
            audio_bytes = supabase.storage.from_(bucket).download(filename)

            gnani_url = "https://api.vachana.ai/stt/v3"
            headers = {"X-API-Key-ID": os.getenv("GNANI_API_KEY")}
            files = {"audio_file": (filename, audio_bytes, "audio/wav")}
            
            async with httpx.AsyncClient() as client:
                gnani_res = await client.post(
                    gnani_url,
                    headers=headers,
                    data={"language_code": "en-IN"},
                    files=files,
                    timeout=120.0
                )
            gnani_res.raise_for_status()
            transcript = gnani_res.json().get("transcript", "")

            summary = "No speech detected."
            if transcript.strip():
                model = genai.GenerativeModel("gemini-3.8-flash")
                prompt = f"Please provide a concise summary of the following audio transcript:\n\n{transcript}"
                gemini_res = await model.generate_content_async(prompt)
                summary = gemini_res.text

            job.transcript = transcript
            job.summary = summary
            job.status = JobStatus.COMPLETED
            await db.commit()

        except Exception as e:
            job = await db.get(AudioJob, job_id)
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            await db.commit()