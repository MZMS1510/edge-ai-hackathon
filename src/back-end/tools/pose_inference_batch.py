#!/usr/bin/env python3
"""Run batch pose classification on a CSV of flat joints and produce a JSON report.

Usage:
  python tools/pose_inference_batch.py --csv keypoints.csv --out report.json

CSV is expected to contain 'frame' and flat joint columns as produced by extract_keypoints_mediapipe.py
"""
import argparse
import csv
import json
from pose_model import predict_from_joints, load_model


def infer(csv_path: str, out_json: str, model_path: str = None):
    model = None
    if model_path:
        model = load_model(model_path)

    results = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract joints: all keys except frame and time
            joints = {k: float(v) for k, v in row.items() if k not in ('frame', 'time') and v != ''}
            res = predict_from_joints(model, joints)
            results.append({"frame": int(float(row.get('frame', 0))), "time": float(row.get('time', 0.0)), "label": res['label'], "score": float(res['score'])})

    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)
    return out_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--model', required=False)
    args = p.parse_args()
    print(infer(args.csv, args.out, args.model))


if __name__ == '__main__':
    main()
