import redis

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

def add_job(job_id, prompt):
    r.hset(f"job:{job_id}", mapping={"prompt": prompt, "status": "PENDING"})

def update_status(job_id, status):
    r.hset(f"job:{job_id}", "status", status)

def get_job(job_id):
    job = r.hgetall(f"job:{job_id}")
    if job:
        return job
    else:
        return {"status": "NOT_FOUND"}

def list_jobs():
    keys = r.keys("job:*")
    return [
        {"job_id": key.split(":")[1], **r.hgetall(key)}
        for key in keys
    ]

def get_output_path(job_id):
    return f"/mnt/data/output/{job_id}.mp4"
