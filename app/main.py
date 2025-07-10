from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from uuid import uuid4
from app import jobs
from app.worker import generate_video_task
import os

# Initialize the FastAPI app instance
app = FastAPI()

# Add CORS middleware to allow requests from any frontend (localhost, web clients, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],   # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],   # Allow all headers
)

# Serve video output files from a static directory
app.mount("/static", StaticFiles(directory="/mnt/data/output"), name="static")

# Define the expected request payload structure
class JobRequest(BaseModel):
    prompt: str  # The text prompt used to generate the video

# Endpoint to submit a new video generation job
@app.post("/jobs")
def submit_job(request: JobRequest):
    job_id = str(uuid4())  # Generate a unique job ID
    jobs.add_job(job_id, request.prompt)  # Store job in Redis
    generate_video_task.delay(job_id, request.prompt)  # Run the job asynchronously via Celery
    return {"job_id": job_id}  # Return the job ID to the client

# Endpoint to check the status of a specific job
@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = jobs.get_job(job_id)
    if job["status"] == "NOT_FOUND":
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    return job  # Returns job dict: prompt, status, result

# Endpoint to list all jobs (mainly for debugging or admin UI)
@app.get("/jobs")
def list_jobs():
    return jobs.list_jobs()

# Endpoint to retrieve the result (video URL or error) for a completed job
@app.get("/jobs/{job_id}/result")
def get_result(job_id: str, request: Request):
    job = jobs.get_job(job_id)

    if job.get("status") == "COMPLETED":
        # The result contains the full path — extract just the filename to generate the URL
        video_filename = os.path.basename(job["result"])
        # url = str(request.base_url) + f"static/{video_filename}"  # Build full video URL
        url = f"/static/{video_filename}"
        return {"url": url}

    elif job.get("status") == "FAILED":
        # Return the error message from the job result
        return {"status": "FAILED", "error": job.get("result")}

    else:
        # Job is still pending or processing
        return {"status": job.get("status")}
