@echo off
REM Whisper Local — Launch Script
REM Starts the Whisper Local system tray application

cd /d "%~dp0"
python -m whisper_local.app
