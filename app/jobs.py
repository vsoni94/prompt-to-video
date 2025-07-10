import redis

# Create a Redis connection instance.
# 'host' is the name of the Redis service (used in Docker/K8s), port 6379 is default.
# decode_responses=True makes sure we get strings instead of byte objects.
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

# Add a new job entry to Redis with its prompt, frames, and initial status.
def add_job(job_id, prompt, frames=30):
    r.hset(f"job:{job_id}", mapping={
        "prompt": prompt,
        "frames": str(frames),     # Store frames as string (Redis stores strings)
        "status": "PENDING",       # Initial state
        "result": ""               # Will hold video path or error later
    })

# Update a job's status. If there's a result (e.g., video path or error), update that too.
def update_status(job_id, status, result=None):
    if result is not None:
        r.hset(f"job:{job_id}", mapping={"status": status, "result": result})
    else:
        r.hset(f"job:{job_id}", "status", status)

# Retrieve a job's full info from Redis. If the job ID doesn't exist, return NOT_FOUND.
def get_job(job_id):
    job = r.hgetall(f"job:{job_id}")
    if job:
        return job
    else:
        return {"status": "NOT_FOUND"}

# Return a list of all jobs in Redis.
# Useful for debugging or showing a history of requests.
def list_jobs():
    keys = r.keys("job:*")  # Grab all keys that match our job pattern
    return [
        {
            "job_id": key.split(":")[1],  # Extract job ID from the Redis key
            **r.hgetall(key)              # Merge the hash fields (prompt, status, result, frames)
        }
        for key in keys
    ]
