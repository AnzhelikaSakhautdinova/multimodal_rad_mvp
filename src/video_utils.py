import subprocess
from pathlib import Path


def create_clip(video_path, center_sec, output_path, clip_duration=6):
    start_sec = max(0, center_sec - clip_duration / 2)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_sec),
            "-i",
            video_path,
            "-t",
            str(clip_duration),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            output_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def concat_clips(clip_paths, output_path):
    list_path = Path(output_path).with_suffix(".txt")

    with open(list_path, "w") as f:
        for clip_path in clip_paths:
            abs_path = Path(clip_path).resolve()
            f.write(f"file '{abs_path}'\n")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c",
            "copy",
            output_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )