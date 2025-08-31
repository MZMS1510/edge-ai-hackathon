"""Example runner: extract keypoints from a video and run pose inference batch.

This is a convenience script; it requires OpenCV and MediaPipe to be installed.
"""
import argparse
from pathlib import Path
import subprocess


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--video', required=True)
    p.add_argument('--outdir', required=True)
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / 'keypoints.csv'
    report_path = outdir / 'report.json'

    # Note: calls the scripts in this tools folder
    subprocess.check_call(['python', 'src/back-end/tools/extract_keypoints_mediapipe.py', '--video', args.video, '--out', str(csv_path)])
    subprocess.check_call(['python', 'src/back-end/tools/pose_inference_batch.py', '--csv', str(csv_path), '--out', str(report_path)])
    print('Pipeline finished. Report at', report_path)


if __name__ == '__main__':
    main()
