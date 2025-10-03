@echo off
REM Fix Missing Product Record - Windows Batch Script
REM ================================================

echo ================================================================
echo    Missing Product Record Fix Tool
echo ================================================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running or not installed
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo Choose an option:
echo.
echo 1. Generate Report Only (Safe - Read Only)
echo 2. Access Database Shell for Manual Fix
echo 3. Run Python Fix Script
echo 4. Use Odoo Database Cleanup Module
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto report
if "%choice%"=="2" goto shell
if "%choice%"=="3" goto python
if "%choice%"=="4" goto odoo_cleanup
if "%choice%"=="5" goto end

echo Invalid choice!
pause
exit /b 1

:report
echo.
echo ================================================================
echo Generating Report...
echo ================================================================
echo.
python fix_missing_product_record.py --fix-mode report
pause
goto end

:shell
echo.
echo ================================================================
echo Opening Database Shell
echo ================================================================
echo.
echo You can run SQL queries to inspect and fix the issue.
echo Example queries:
echo.
echo   -- Check if product exists
echo   SELECT * FROM product_product WHERE id = 11;
echo.
echo   -- Find references in sale order lines
echo   SELECT * FROM sale_order_line WHERE product_id = 11;
echo.
echo Type 'exit' to close the shell
echo.
docker-compose exec db psql -U odoo -d odoo
pause
goto end

:python
echo.
echo ================================================================
echo Python Fix Script Options
echo ================================================================
echo.
echo WARNING: This will modify your database!
echo.
echo 1. Replace with another product (enter product ID)
echo 2. Remove orphaned references
echo 3. Cancel
echo.
set /p fix_choice="Enter your choice (1-3): "

if "%fix_choice%"=="1" goto replace
if "%fix_choice%"=="2" goto remove
if "%fix_choice%"=="3" goto end

echo Invalid choice!
pause
goto end

:replace
set /p replacement_id="Enter replacement product ID: "
echo.
echo Running replacement fix with product ID %replacement_id%...
python fix_missing_product_record.py --fix-mode replace --replacement-id %replacement_id%
pause
goto end

:remove
echo.
echo WARNING: This will DELETE records!
echo.
set /p confirm="Are you sure? Type 'YES' to confirm: "
if not "%confirm%"=="YES" (
    echo Cancelled.
    pause
    goto end
)
python fix_missing_product_record.py --fix-mode remove
pause
goto end

:odoo_cleanup
echo.
echo ================================================================
echo Odoo Database Cleanup Module
echo ================================================================
echo.
echo To use the Database Cleanup module:
echo.
echo 1. Open Odoo in your browser: http://localhost:8069
echo 2. Enable Developer Mode:
echo    - Click your profile icon (top right)
echo    - Click "Developer Mode" at the bottom
echo 3. Go to: Settings ^> Technical ^> Database Structure ^> Database Cleanup
echo 4. Choose the cleanup option:
echo    - "Purge Data" to remove orphaned data references
echo    - "Purge Models" to clean up missing models
echo 5. Click "Purge All" or select specific items
echo.
echo Press any key to open Odoo in your browser...
pause
start http://localhost:8069
goto end

:end
echo.
echo ================================================================
echo Done!
echo ================================================================
