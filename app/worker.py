import multiprocessing

try:
    multiprocessing.set_start_method('spawn', force=True)
except RuntimeError:
    pass  # start method already set

from celery import Celery
from celery.signals import worker_process_init
from app.video_generator import generate_video, get_model
from app import jobs

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

pipe = None  # global model instance per worker subprocess

@worker_process_init.connect
def init_worker(**kwargs):
    global pipe
    print("[INFO] Worker subprocess initializing model...")
    pipe = get_model()
    print("[INFO] Model initialized in worker subprocess.")

@celery_app.task
def generate_video_task(job_id, prompt):
    jobs.update_status(job_id, "PROCESSING")
    global pipe
    if pipe is None:
        # Safety fallback, but ideally pipe is ready by worker_process_init
        pipe = get_model()
    try:
        video_path = generate_video(prompt, job_id, pipe)
        jobs.update_status(job_id, "COMPLETED", result=video_path)
    except Exception as e:
        error_msg = f"FAILED: {str(e)}"
        jobs.update_status(job_id, "FAILED", result=error_msg)
