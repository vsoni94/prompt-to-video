from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from app import jobs  # import Redis-backed jobs module
from app.worker import generate_video_task

app = FastAPI()

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
    return jobs.get_job(job_id)

@app.get("/jobs")
def list_jobs():
    return jobs.list_jobs()

@app.get("/jobs/{job_id}/result")
def get_result(job_id: str):
    job = jobs.get_job(job_id)
    if job.get("status") == "COMPLETED":
        return {"url": f"/static/{job_id}.mp4"}
    return {"status": job.get("status")}
