# def generate_video(prompt: str, job_id: str):
#     # Placeholder for actual Mochi model logic
#     video_path = f"/mnt/data/output/{job_id}.mp4"
#     with open(video_path, "wb") as f:
#         f.write(b"FAKE_VIDEO")
#     return video_path

import os

def generate_video(prompt: str, job_id: str):
    video_path = f"/mnt/data/output/{job_id}.mp4"

    print("[INFO] Pretending to generate video...")
    print(f"[DEBUG] Prompt received: {prompt}")
    print(f"[DEBUG] Job ID: {job_id}")
    print(f"[INFO] Simulating output video at: {video_path}")

    # Simulate file creation
    os.makedirs(os.path.dirname(video_path), exist_ok=True)
    with open(video_path, "wb") as f:
        f.write(b"SIMULATED_VIDEO_CONTENT")

    print("[INFO] Mock video generation complete")
    return video_path