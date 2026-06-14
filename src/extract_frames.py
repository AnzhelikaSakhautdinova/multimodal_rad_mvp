import cv2
import os
from pathlib import Path

import pandas as pd
from tqdm import tqdm


VIDEO_PATH = "data/videos/video1.mp4"
OUTPUT_DIR = "data/frames"
OUTPUT_CSV = "data/captions.csv"

FRAME_EVERY_SECONDS = 2

os.makedirs(OUTPUT_DIR, exist_ok=True)

old_df = None
if Path(OUTPUT_CSV).exists():
    old_df = pd.read_csv(OUTPUT_CSV)
    print("Existing captions.csv found. Descriptions will be preserved.")

cap = cv2.VideoCapture(VIDEO_PATH)

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps

print(f"FPS: {fps}")
print(f"Total frames: {total_frames}")
print(f"Duration: {duration:.2f} seconds")

frame_interval = int(fps * FRAME_EVERY_SECONDS)

rows = []
saved_id = 0

for frame_id in tqdm(range(total_frames)):
    ret, frame = cap.read()
    if not ret:
        break

    if frame_id % frame_interval == 0:
        timestamp_sec = round(frame_id / fps, 2)

        minutes = int(timestamp_sec // 60)
        seconds = int(timestamp_sec % 60)
        timestamp = f"{minutes:02d}:{seconds:02d}"

        frame_name = f"video1_frame_{saved_id:04d}.jpg"
        frame_path = os.path.join(OUTPUT_DIR, frame_name)

        cv2.imwrite(frame_path, frame)

        rows.append(
            {
                "frame_path": frame_path,
                "timestamp_sec": timestamp_sec,
                "timestamp": timestamp,
                "description": "",
            }
        )

        saved_id += 1

cap.release()

new_df = pd.DataFrame(rows)

if old_df is not None and "description" in old_df.columns:
    n = min(len(new_df), len(old_df))
    new_df.loc[: n - 1, "description"] = old_df.loc[: n - 1, "description"].values

new_df.to_csv(OUTPUT_CSV, index=False)

print(f"Saved {saved_id} frames")
print(f"CSV saved to {OUTPUT_CSV}")
print(new_df.head())