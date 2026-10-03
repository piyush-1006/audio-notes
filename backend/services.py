import asyncio
import os

import google.generativeai as genai
import httpx
from supabase import create_client

from database import AsyncSessionLocal
from models import AudioJob, JobStatus

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


async def process_audio_job(job_id: str, filename: str) -> None:
    """Run long-running audio work outside the request's database session."""
    async with AsyncSessionLocal() as db:
        job = await db.get(AudioJob, job_id)
        if not job:
            return

        try:
            job.status = JobStatus.PROCESSING
            await db.commit()

            # This SDK is synchronous. Move it to a worker thread so it cannot
            # block FastAPI's event loop while it downloads the recording.
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
            bucket = os.getenv("SUPABASE_BUCKET", "audio-uploads")
            audio_bytes = await asyncio.to_thread(supabase.storage.from_(bucket).download, filename)

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://api.vachana.ai/stt/v3",
                    headers={"X-API-Key-ID": os.getenv("GNANI_API_KEY")},
                    data={"language_code": "en-IN"},
                    files={"audio_file": (filename, audio_bytes, "audio/wav")},
                )
            response.raise_for_status()
            transcript = response.json().get("transcript", "")

            summary = "No speech detected."
            if transcript.strip():
                model = genai.GenerativeModel("gemini-3.8-flash")
                prompt = f"Please provide a concise summary of the following audio transcript:\n\n{transcript}"
                result = await model.generate_content_async(prompt)
                summary = result.text

            job.transcript = transcript
            job.summary = summary
            job.status = JobStatus.COMPLETED
            await db.commit()
        except Exception as exc:
            # A failed DB operation invalidates the current transaction. Roll it
            # back before querying/updating again to avoid async session errors.
            await db.rollback()
            job = await db.get(AudioJob, job_id)
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(exc)
                await db.commit()
