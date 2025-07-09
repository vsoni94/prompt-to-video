import multiprocessing

# Set multiprocessing start method to 'spawn' to avoid CUDA errors
# when using CUDA in forked subprocesses (common issue with PyTorch + Celery).
try:
    multiprocessing.set_start_method('spawn', force=True)
except RuntimeError:
    pass  # start method already set, no action needed

from celery import Celery
from celery.signals import worker_process_init
from app.video_generator import generate_video, get_model
from app import jobs

# Initialize Celery app with Redis as broker and backend
celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

pipe = None  # Global variable to hold the model instance per worker subprocess

# Signal handler called when a Celery worker subprocess starts
# Load the ML model once per subprocess here to avoid repeated loads and CUDA init errors
@worker_process_init.connect
def init_worker(**kwargs):
    global pipe
    print("[INFO] Worker subprocess initializing model...")
    pipe = get_model()  # Load and cache model for this worker process
    print("[INFO] Model initialized in worker subprocess.")

# Celery task to generate video asynchronously
@celery_app.task
def generate_video_task(job_id, prompt):
    jobs.update_status(job_id, "PROCESSING")  # Update job status in Redis

    global pipe
    if pipe is None:
        # Fallback in case init_worker signal did not run or model was not loaded
        pipe = get_model()

    try:
        # Run video generation passing the cached model instance
        video_path = generate_video(prompt, job_id, pipe)
        # On success, update job status and store resulting video path
        jobs.update_status(job_id, "COMPLETED", result=video_path)
    except Exception as e:
        # On failure, update job status with error message
        error_msg = f"FAILED: {str(e)}"
        jobs.update_status(job_id, "FAILED", result=error_msg)
