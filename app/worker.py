import multiprocessing
multiprocessing.set_start_method('spawn', force=True) #  To address Cannot re-initialize CUDA in forked subprocess. To use CUDA with multiprocessing, you must use the 'spawn' start method

from celery import Celery
from app.video_generator import generate_video
from app import jobs

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task
def generate_video_task(job_id, prompt):
    jobs.update_status(job_id, "PROCESSING")
    try:
        generate_video(prompt, job_id)
        jobs.update_status(job_id, "COMPLETED")
    except Exception as e:
        jobs.update_status(job_id, f"FAILED: {str(e)}")
