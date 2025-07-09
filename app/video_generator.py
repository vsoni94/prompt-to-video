import os
import torch
from diffusers import MochiPipeline
from diffusers.utils import export_to_video

pipe = None

def get_model():
    global pipe
    if pipe is None:
        try:
            print("[INFO] Loading MochiPipeline model...")
            pipe = MochiPipeline.from_pretrained("genmo/mochi-1-preview", torch_dtype=torch.bfloat16)
            pipe.enable_model_cpu_offload()
            pipe.enable_vae_tiling()
            print("[INFO] Model loaded")
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            raise
    return pipe

def generate_video(prompt: str, job_id: str) -> str:
    video_path = f"/mnt/data/output/{job_id}.mp4"

    print(f"[INFO] Generating video for job_id={job_id}, prompt='{prompt}'")

    try:
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        model = get_model()

        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            result = model(prompt, num_frames=84)
            frames = result.frames[0]

        export_to_video(frames, video_path, fps=30)
        print(f"[INFO] Video generated at: {video_path}")

    except Exception as e:
        print(f"[ERROR] Video generation failed: {e}")
        raise

    return video_path

# import os
# import torch
# from diffusers import MochiPipeline
# from diffusers.utils import export_to_video

# import logging
# logging.warning(f"[DEBUG] CUDA Available: {torch.cuda.is_available()}")
# logging.warning(f"[DEBUG] Current Device: {torch.cuda.current_device() if torch.cuda.is_available() else 'None'}")
# logging.warning(f"[DEBUG] GPU Name: {torch.cuda.get_device_name(torch.cuda.current_device()) if torch.cuda.is_available() else 'N/A'}")


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
