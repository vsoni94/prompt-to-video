import os
import torch
import subprocess
from diffusers.utils import export_to_video
import logging

def get_model():
    from diffusers import MochiPipeline

    # Log CUDA status and GPU info for debugging
    logging.warning(f"[DEBUG] CUDA Available: {torch.cuda.is_available()}")
    logging.warning(f"[DEBUG] Current Device: {torch.cuda.current_device() if torch.cuda.is_available() else 'None'}")
    logging.warning(f"[DEBUG] GPU Name: {torch.cuda.get_device_name(torch.cuda.current_device()) if torch.cuda.is_available() else 'N/A'}")

    try:
        print("[INFO] Loading MochiPipeline model...")
        # Load the Mochi model from pretrained weights and cache locally
        pipe = MochiPipeline.from_pretrained(
            "genmo/mochi-1-preview",
            cache_dir="/mnt/mochi-models",
            torch_dtype=torch.bfloat16
        )
        # Enable CPU offload to reduce GPU memory pressure
        pipe.enable_model_cpu_offload()
        # Enable VAE tiling to optimize memory usage during generation
        pipe.enable_vae_tiling()
        print("[INFO] Model loaded")
        return pipe

    except Exception as e:
        # Log and re-raise any loading errors for troubleshooting
        print(f"[ERROR] Failed to load model: {e}")
        raise

def generate_video(prompt: str, job_id: str, pipe, frames:int=30) -> str:
    # Define output paths for generated video and its re-encoded version
    video_path = f"/mnt/data/output/{job_id}.mp4"
    fixed_video_path = f"/mnt/data/output/{job_id}-fixed.mp4"

    print(f"[INFO] Generating video for job_id={job_id}, prompt='{prompt}'")

    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(video_path), exist_ok=True)

        # Use mixed precision autocasting for faster GPU inference
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            # Run the model to generate video frames
            result = pipe(prompt, num_frames=frames)
            frames = result.frames[0]

        # Export the generated frames as a video file (MP4)
        export_to_video(frames, video_path, fps=30)
        print(f"[INFO] Video generated at: {video_path}")

        # Verify that the video file exists and is non-empty
        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            raise RuntimeError(f"Video file not found or empty at {video_path}")

        print(f"[INFO] Re-encoding video for browser compatibility...")
        # Re-encode the video using ffmpeg with H264 codec for wide browser support
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-movflags", "+faststart",
            fixed_video_path
        ], check=True)

        # Confirm the re-encoded file exists and is non-empty
        if not os.path.exists(fixed_video_path) or os.path.getsize(fixed_video_path) == 0:
            raise RuntimeError(f"Re-encoded video file not found or empty at {fixed_video_path}")

        print(f"[INFO] Re-encoded video saved at: {fixed_video_path}")
        return fixed_video_path

    except Exception as e:
        # Log and propagate any errors during generation or encoding
        print(f"[ERROR] Video generation failed: {e}")
        raise
