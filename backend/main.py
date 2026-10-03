import os
import uuid
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client, Client
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import AudioJob, JobStatus
from services import process_audio_job

load_dotenv()

app = FastAPI(title="Audio Notes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "audio-uploads")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
async def health_check():
    return {"status": "success", "message": "Audio Notes Backend is running"}

@app.post("/api/upload")
async def upload_audio(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    job_id = str(uuid.uuid4())
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "wav"
    storage_filename = f"{job_id}.{file_ext}"
    file_bytes = await file.read()

    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=storage_filename,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {str(e)}")

    new_job = AudioJob(
        id=job_id,
        filename=storage_filename,
        status=JobStatus.PENDING
    )
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # Trigger background processing
    background_tasks.add_task(process_audio_job, job_id, storage_filename)

    return {
        "job_id": new_job.id,
        "status": new_job.status,
        "message": "Audio uploaded and processing started"
    }


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(AudioJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "filename": job.filename,
        "status": job.status,
        "transcript": job.transcript,
        "summary": job.summary,
        "error_message": job.error_message
    }