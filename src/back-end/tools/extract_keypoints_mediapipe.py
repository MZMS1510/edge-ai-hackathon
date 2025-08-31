#!/usr/bin/env python3
"""Extract MediaPipe pose keypoints from a video and save a per-frame CSV.

Usage:
  python tools/extract_keypoints_mediapipe.py --video input.mp4 --out keypoints.csv

Dependencies: opencv-python, mediapipe
"""
import argparse
import csv
import sys
import time
from pathlib import Path

try:
    import cv2
    import mediapipe as mp
except Exception as e:
    cv2 = None
    mp = None

from media_pipe_utils import convert_landmarks_to_flat


def process(video_path: str, out_csv: str, frame_step: int = 1, max_frames: int = None):
    if cv2 is None or mp is None:
        raise RuntimeError("OpenCV and MediaPipe are required to run extraction. Install opencv-python and mediapipe.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

    out_fields = None
    written = 0
    frame_i = 0
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_i % frame_step != 0:
                frame_i += 1
                continue

            # Convert BGR to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            landmarks = None
            if results.pose_landmarks is not None:
                # extract as list of dicts
                landmarks = []
                for lm in results.pose_landmarks.landmark:
                    landmarks.append({"x": lm.x, "y": lm.y, "z": lm.z, "visibility": getattr(lm, "visibility", 0.0)})

            flat = convert_landmarks_to_flat(landmarks)
            timestamp = frame_i / fps
            row = {"frame": frame_i, "time": timestamp}
            row.update(flat)

            if writer is None:
                out_fields = list(row.keys())
                writer = csv.DictWriter(f, fieldnames=out_fields)
                writer.writeheader()

            writer.writerow(row)
            written += 1
            frame_i += 1
            if max_frames and written >= max_frames:
                break

    cap.release()
    pose.close()
    return out_csv


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--frame-step", type=int, default=1)
    p.add_argument("--max-frames", type=int, default=None)
    args = p.parse_args()
    start = time.time()
    out = process(args.video, args.out, frame_step=args.frame_step, max_frames=args.max_frames)
    print(f"Wrote {out}")
    print(f"Elapsed: {time.time()-start:.2f}s")


if __name__ == "__main__":
    main()
