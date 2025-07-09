import os
import torch
import subprocess
from diffusers.utils import export_to_video
import logging


def get_model():
    from diffusers import MochiPipeline
    logging.warning(f"[DEBUG] CUDA Available: {torch.cuda.is_available()}")
    logging.warning(f"[DEBUG] Current Device: {torch.cuda.current_device() if torch.cuda.is_available() else 'None'}")
    logging.warning(f"[DEBUG] GPU Name: {torch.cuda.get_device_name(torch.cuda.current_device()) if torch.cuda.is_available() else 'N/A'}")
    try:
        print("[INFO] Loading MochiPipeline model...")
        pipe = MochiPipeline.from_pretrained("genmo/mochi-1-preview", cache_dir="/mnt/mochi-models", torch_dtype=torch.bfloat16)
        pipe.enable_model_cpu_offload()
        pipe.enable_vae_tiling()
        print("[INFO] Model loaded")
        return pipe
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        raise

def generate_video(prompt: str, job_id: str, pipe) -> str:
    video_path = f"/mnt/data/output/{job_id}.mp4"
    fixed_video_path = f"/mnt/data/output/{job_id}-fixed.mp4"

    print(f"[INFO] Generating video for job_id={job_id}, prompt='{prompt}'")

    try:
        os.makedirs(os.path.dirname(video_path), exist_ok=True)

        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            result = pipe(prompt, num_frames=300)
            frames = result.frames[0]

        export_to_video(frames, video_path, fps=30)
        print(f"[INFO] Video generated at: {video_path}")

        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            raise RuntimeError(f"Video file not found or empty at {video_path}")

        print(f"[INFO] Re-encoding video for browser compatibility...")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-movflags", "+faststart",
            fixed_video_path
        ], check=True)

        if not os.path.exists(fixed_video_path) or os.path.getsize(fixed_video_path) == 0:
            raise RuntimeError(f"Re-encoded video file not found or empty at {fixed_video_path}")

        print(f"[INFO] Re-encoded video saved at: {fixed_video_path}")
        return fixed_video_path

    except Exception as e:
        print(f"[ERROR] Video generation failed: {e}")
        raise


# def generate_video(prompt: str, job_id: str) -> str:
#     video_path = f"/mnt/data/output/{job_id}.mp4"

#     print(f"[INFO] Generating video for job_id={job_id}, prompt='{prompt}'")

#     try:
#         os.makedirs(os.path.dirname(video_path), exist_ok=True)
#         model = get_model()

#         with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
#             result = model(prompt, num_frames=84)
#             frames = result.frames[0]

#         export_to_video(frames, video_path, fps=30)
#         print(f"[INFO] Video generated at: {video_path}")

#     except Exception as e:
#         print(f"[ERROR] Video generation failed: {e}")
#         raise

#     return video_path

# import os
# import torch
# from diffusers import MochiPipeline
# from diffusers.utils import export_to_video




# print("[INFO] Loading MochiPipeline model...")
# pipe = MochiPipeline.from_pretrained("genmo/mochi-1-preview", torch_dtype=torch.bfloat16)
# # pipe.enable_model_cpu_offload()
# pipe.enable_vae_tiling()
# print("[INFO] Model loaded")

# def generate_video(prompt: str, job_id: str) -> str:
#     video_path = f"/mnt/data/output/{job_id}.mp4"
#     print(f"[INFO] Generating video for job_id={job_id}, prompt='{prompt}'")

#     try:
#         os.makedirs(os.path.dirname(video_path), exist_ok=True)

#         with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
#             result = pipe(prompt, num_frames=84)
#             frames = result.frames[0]

#         export_to_video(frames, video_path, fps=30)
#         print(f"[INFO] Video generated at: {video_path}")
#         return video_path

#     except Exception as e:
#         print(f"[ERROR] Video generation failed: {e}")
#         raise


# import torch
# import accelerate
# from diffusers import MochiPipeline
# from diffusers.utils import export_to_video
# import os

# pipe = MochiPipeline.from_pretrained("genmo/mochi-1-preview", torch_dtype=torch.bfloat16)

# # Enable memory savings
# # pipe.enable_model_cpu_offload()
# pipe.enable_vae_tiling()
# pipe.to("cuda")

# def generate_video(prompt: str, job_id: str) -> str:
#     video_path = f"/mnt/data/output/{job_id}.mp4"

#     print(f"[INFO] Generating video for job_id={job_id}, prompt='{prompt}'")

#     os.makedirs(os.path.dirname(video_path), exist_ok=True)

#     frames = pipe(prompt, num_frames=84).frames[0]

#     export_to_video(frames, video_path, fps=30)
#     print(f"[INFO] Video generated at: {video_path}")

#     return video_path

# def generate_video():
#     prompt = "Close-up of a chameleon's eye, with its scaly skin changing color. Ultra high resolution 4k."
#     frames = pipe(prompt, num_frames=84).frames[0]

#     export_to_video(frames, "mochi.mp4", fps=30)

# if __name__ == "__main__":
#     generate_video()

# ECU downgrading POC (brakes as well as E67)
# TCU downgrading
# Factory Driverless Pipeline
# Reliability improvements such as ssh, run-overlay, recover dead car, etc. 
# Always available for any escalations in any of the chats
