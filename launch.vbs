' Whisper Local — Silent Launcher
' Starts the app without any visible console window.
' Double-click this file or use it for run-on-startup.

Set WshShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strPath
WshShell.Run "pythonw -m whisper_local.app", 0, False
