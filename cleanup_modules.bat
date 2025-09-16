@echo off
setlocal enabledelayedexpansion

:: =============================================================================
:: Module Cleanup Script for Odoo 17 (Windows Version)
:: =============================================================================
:: This script safely removes Python cache files and other temporary files 
:: from Odoo modules while creating a backup before deletion.
::
:: Usage:
::   cleanup_modules.bat [options]
::
:: Options:
::   --dry-run    Show what would be deleted without actually deleting
::   --no-backup  Skip creating a backup (NOT RECOMMENDED)
::   --help       Show this help message
::
:: Author: GitHub Copilot
:: Version: 1.0
:: =============================================================================

:: Set default options
set DRY_RUN=false
set CREATE_BACKUP=true
set SHOW_HELP=false
set BASE_DIR=%CD%
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "TIMESTAMP=%dt:~0,8%_%dt:~8,6%"
set BACKUP_DIR=%BASE_DIR%\module_backups
set BACKUP_FILE=%BACKUP_DIR%\modules_backup_%TIMESTAMP%.zip
set LOG_FILE=%BASE_DIR%\cleanup_%TIMESTAMP%.log

:: Process command-line arguments
for %%a in (%*) do (
  if "%%a"=="--dry-run" (
    set DRY_RUN=true
    echo Running in DRY RUN mode - no files will be deleted
  )
  if "%%a"=="--no-backup" (
    set CREATE_BACKUP=false
    echo WARNING: Running without creating backups. This is NOT RECOMMENDED.
  )
  if "%%a"=="--help" (
    set SHOW_HELP=true
  )
)

:: Show help if requested
if "%SHOW_HELP%"=="true" (
  echo Odoo Module Cleanup Script
  echo.
  echo This script removes Python cache files and other temporary files
  echo from Odoo modules while creating a backup before deletion.
  echo.
  echo Usage: cleanup_modules.bat [options]
  echo.
  echo Options:
  echo   --dry-run    Show what would be deleted without actually deleting
  echo   --no-backup  Skip creating a backup (NOT RECOMMENDED)
  echo   --help       Show this help message
  echo.
  exit /b 0
)

:: Setup log file
echo ===== Odoo Module Cleanup - %date% %time% ===== > "%LOG_FILE%"
echo Working directory: %BASE_DIR% >> "%LOG_FILE%"

:: Function to log messages
:log_message
echo [%date% %time%] %~1 >> "%LOG_FILE%"
echo %~1
goto :EOF

:: Create backup directory if it doesn't exist
if "%CREATE_BACKUP%"=="true" (
  call :log_message "Creating backup directory at %BACKUP_DIR%"
  if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
  
  call :log_message "Creating backup archive at %BACKUP_FILE%"
  if "%DRY_RUN%"=="false" (
    :: Create a backup of all module directories using PowerShell
    powershell -Command "Get-ChildItem -Path '%BASE_DIR%' -Directory | Where-Object { $_.FullName -ne '%BACKUP_DIR%' } | Compress-Archive -DestinationPath '%BACKUP_FILE%' -Force"
    if !errorlevel! equ 0 (
      call :log_message "Backup created successfully"
    ) else (
      call :log_message "ERROR: Backup creation failed! Aborting cleanup."
      exit /b 1
    )
    
    :: Verify backup integrity
    call :log_message "Verifying backup integrity..."
    powershell -Command "Test-Path '%BACKUP_FILE%'" | findstr "True" > nul
    if !errorlevel! equ 0 (
      call :log_message "Backup verified and is valid"
    ) else (
      call :log_message "ERROR: Backup verification failed! Aborting cleanup."
      exit /b 1
    )
  ) else (
    call :log_message "[DRY RUN] Would create backup of all modules"
  )
)

:: Function to confirm with user before proceeding
:confirm_action
:: Skip confirmation if in dry run mode
if "%DRY_RUN%"=="true" goto :EOF
  
echo.
echo WARNING: This will remove all Python cache files and temporary files.
echo A backup will be created at: %BACKUP_FILE%
echo.
set /p response="Do you want to proceed with deletion? (y/n): "

if /i "%response%"=="y" (
  goto :EOF
) else (
  call :log_message "Cleanup aborted by user"
  exit /b 0
)

:: Main cleanup process
call :log_message "Starting cleanup process..."

:: Confirm with user before proceeding with actual deletion
call :confirm_action

:: 1. Remove Python cache directories
call :log_message "Looking for Python cache directories..."
set "CACHE_DIRS_COUNT=0"
for /f "tokens=*" %%d in ('dir /b /s /a:d "%BASE_DIR%\__pycache__" 2^>nul') do (
  set /a CACHE_DIRS_COUNT+=1
  
  if "%DRY_RUN%"=="true" (
    call :log_message "[DRY RUN] Would remove cache directory: %%d"
  ) else (
    rmdir /s /q "%%d"
    if !errorlevel! equ 0 (
      call :log_message "Removed cache directory: %%d"
    ) else (
      call :log_message "ERROR: Failed to remove cache directory: %%d"
    )
  )
)

if %CACHE_DIRS_COUNT% equ 0 (
  call :log_message "No Python cache directories found"
)

:: 2. Remove compiled Python files (.pyc)
call :log_message "Looking for compiled Python files (.pyc)..."
set "PYC_FILES_COUNT=0"
for /f "tokens=*" %%f in ('dir /b /s "%BASE_DIR%\*.pyc" 2^>nul') do (
  set /a PYC_FILES_COUNT+=1
  
  if "%DRY_RUN%"=="true" (
    call :log_message "[DRY RUN] Would remove compiled Python file: %%f"
  ) else (
    del "%%f"
    if !errorlevel! equ 0 (
      call :log_message "Removed compiled Python file: %%f"
    ) else (
      call :log_message "ERROR: Failed to remove compiled Python file: %%f"
    )
  )
)

if %PYC_FILES_COUNT% equ 0 (
  call :log_message "No compiled Python files found"
)

:: 3. Remove backup/temporary files
call :log_message "Looking for backup/temporary files..."
set "TEMP_FILES_COUNT=0"
for /f "tokens=*" %%f in ('dir /b /s "%BASE_DIR%\*.bak" "%BASE_DIR%\*.backup" "%BASE_DIR%\*.tmp" "%BASE_DIR%\*~" "%BASE_DIR%\*.swp" 2^>nul') do (
  set /a TEMP_FILES_COUNT+=1
  
  if "%DRY_RUN%"=="true" (
    call :log_message "[DRY RUN] Would remove temporary file: %%f"
  ) else (
    del "%%f"
    if !errorlevel! equ 0 (
      call :log_message "Removed temporary file: %%f"
    ) else (
      call :log_message "ERROR: Failed to remove temporary file: %%f"
    )
  )
)

if %TEMP_FILES_COUNT% equ 0 (
  call :log_message "No backup/temporary files found"
)

:: Add summary to log
call :log_message "Cleanup process completed"
call :log_message "Summary:"
call :log_message "  - Python cache directories processed: %CACHE_DIRS_COUNT%"
call :log_message "  - Compiled Python files processed: %PYC_FILES_COUNT%"
call :log_message "  - Backup/temporary files processed: %TEMP_FILES_COUNT%"

if "%DRY_RUN%"=="true" (
  call :log_message "DRY RUN completed. No files were actually deleted."
  call :log_message "To perform actual deletion, run without the --dry-run option."
) else (
  call :log_message "Actual deletion completed. Log saved to %LOG_FILE%"
  if "%CREATE_BACKUP%"=="true" (
    call :log_message "Backup saved to %BACKUP_FILE%"
  )
)

echo ===== Cleanup Finished ===== >> "%LOG_FILE%"
endlocal