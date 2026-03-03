@echo off
:: Starts the PowerShell script in the same directory
powershell -ExecutionPolicy Bypass -File "%~dp0auto_correct_ffb_settings.ps1"
pause