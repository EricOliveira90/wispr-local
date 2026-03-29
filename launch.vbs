' Whisper Local — Silent Launcher
' Starts the app without any visible console window.
'
' How to use:
'   - Double-click this file in File Explorer
'   - Or from CMD:    wscript launch.vbs
'   - Or from PowerShell:  wscript .\launch.vbs
'   - Or from anywhere:    wscript "C:\full\path\to\launch.vbs"

Set objFSO = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")

' Change to the directory where this script lives
strPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strPath

' Find pythonw.exe (windowless Python) and launch the app
WshShell.Run "pythonw -m whisper_local.app", 0, False
