from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uuid import uuid4
from app import jobs
from app.worker import generate_video_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="/mnt/data/output"), name="static")

class JobRequest(BaseModel):
    prompt: str

@app.post("/jobs")
def submit_job(request: JobRequest):
    job_id = str(uuid4())
    jobs.add_job(job_id, request.prompt)
    generate_video_task.delay(job_id, request.prompt)
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = jobs.get_job(job_id)
    if job["status"] == "NOT_FOUND":
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    return job

@app.get("/jobs")
def list_jobs():
    return jobs.list_jobs()

@app.get("/jobs/{job_id}/result")
def get_result(job_id: str, request: Request):
    job = jobs.get_job(job_id)
    if job.get("status") == "COMPLETED":
        url = request.url_for("static", path=f"{job_id}.mp4")
        return {"url": url}
    return {"status": job.get("status")}
