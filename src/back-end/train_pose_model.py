"""Training helper for pose classification.

Usage:
  python train_pose_model.py --csv data.csv --out model.joblib

CSV must contain flat joint columns matching media_pipe_utils output and a 'label' column (0/1).
"""
import argparse
from pose_model import train_from_csv


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="CSV with joint columns and 'label' column")
    p.add_argument("--out", required=True, help="Output joblib path")
    args = p.parse_args()
    train_from_csv(args.csv, args.out)


if __name__ == "__main__":
    main()
