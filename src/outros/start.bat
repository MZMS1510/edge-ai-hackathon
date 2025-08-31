@echo off
cd /d "%~dp0"
echo 🎯 Iniciando Edge Video Converter...
if exist "edge-video-env\Scripts\activate.bat" (
    call edge-video-env\Scripts\activate.bat
) else (
    conda activate mediapipe-env 2>nul
)
python web_video_converter.py
pause
