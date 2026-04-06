@echo off
REM  %~dp0 expands to atual (d)rive + (p)ath of this (0) .bat file
cd /d "%~dp0"
"%~dp0.venv\Scripts\python.exe" -m src.bridge