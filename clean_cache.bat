@echo off
REM Auto Clean Cache Files - Odoo Project (Windows)
REM Run this script to automatically clean all Python cache files

echo ============================================================
echo   Cleaning Python cache files...
echo ============================================================
echo.

REM Change to project directory
cd /d "%~dp0"

echo Removing __pycache__ directories...
for /d /r %%i in (__pycache__) do @if exist "%%i" rmdir /s /q "%%i" 2>nul
echo Done!
echo.

echo Removing .pyc files...
del /s /q *.pyc 2>nul
echo Done!
echo.

echo Removing .pyo files...
del /s /q *.pyo 2>nul
echo Done!
echo.

echo Removing backup files...
del /s /q *~ 2>nul
del /s /q *.bak 2>nul
del /s /q *.backup 2>nul
echo Done!
echo.

echo ============================================================
echo   SUCCESS! All cache files removed.
echo ============================================================
echo.
echo The .gitignore file will prevent these from being tracked.
echo Run this script anytime to clean cache files.
echo.

pause
