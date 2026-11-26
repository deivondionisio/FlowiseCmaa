@echo off
REM Atalho: roda o run.ps1 sem esbarrar na politica de scripts do Windows
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"
