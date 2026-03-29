@echo off
REM Whisper Local — Silent Launcher
REM This launches the app without any visible console window.
REM Works from double-click, CMD, or PowerShell.

cd /d "%~dp0"
start "" wscript "%~dp0launch.vbs"
exit
