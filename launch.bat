@echo off
REM Whisper Local — Launch Script
REM Starts the app without a visible console window.
REM For a fully silent launch (no CMD flash), use launch.vbs instead.

cd /d "%~dp0"
start "" /B pythonw -m whisper_local.app
