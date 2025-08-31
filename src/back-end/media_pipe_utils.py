"""Utilities to convert MediaPipe pose landmarks into the flat joints dict expected by pose_model.

The converter accepts a list (or iterable) of landmarks where each landmark is a dict-like with
keys 'x','y','z' and optionally 'visibility'. The order must follow MediaPipe Pose landmark indices.
"""
from typing import List, Dict, Any

# Ordered MediaPipe Pose landmarks names (33 landmarks)
LANDMARK_NAMES = [
    "nose",
    "left_eye_inner",
    "left_eye",
    "left_eye_outer",
    "right_eye_inner",
    "right_eye",
    "right_eye_outer",
    "left_ear",
    "right_ear",
    "mouth_left",
    "mouth_right",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_pinky",
    "right_pinky",
    "left_index",
    "right_index",
    "left_thumb",
    "right_thumb",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index",
]


def convert_landmarks_to_flat(landmarks: List[Any]) -> Dict[str, float]:
    """Convert a sequence of MediaPipe landmarks into a flat dict of joint_{x,y,z}.

    landmarks: list of dict-like or objects with attributes x,y,z,visibility. The order must match LANDMARK_NAMES.
    Returns: dict like {'nose_x':0.5, 'nose_y':0.4, 'nose_z':0.0, ...}
    """
    out = {}
    if landmarks is None:
        return out

    for idx, name in enumerate(LANDMARK_NAMES):
        if idx >= len(landmarks):
            # missing landmarks -> fill with 0.0
            out[f"{name}_x"] = 0.0
            out[f"{name}_y"] = 0.0
            out[f"{name}_z"] = 0.0
            continue

        lm = landmarks[idx]
        # support dict-like or object attributes
        try:
            x = float(lm["x"]) if isinstance(lm, dict) else float(getattr(lm, "x"))
            y = float(lm["y"]) if isinstance(lm, dict) else float(getattr(lm, "y"))
            z = float(lm.get("z", 0.0) if isinstance(lm, dict) else getattr(lm, "z", 0.0))
        except Exception:
            # fallback to zeros
            x, y, z = 0.0, 0.0, 0.0

        out[f"{name}_x"] = x
        out[f"{name}_y"] = y
        out[f"{name}_z"] = z

    return out
