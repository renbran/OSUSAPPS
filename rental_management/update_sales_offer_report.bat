@echo off
REM Update rental_management module after Sales Offer Report enhancement
REM Run this script to apply the changes to Odoo

echo =======================================================================
echo   Rental Management - Sales Offer Report Update
echo =======================================================================
echo.
echo This script will update the rental_management module with the new
echo Sales Offer Report enhancements.
echo.
echo Changes include:
echo   * Biltmore Sufouh color scheme (Bronze/Gold)
echo   * Three-column layout on Page 1
echo   * Comprehensive payment plan breakdown
echo   * Registration fees section
echo   * Booking amount section
echo   * 'Developer' label (changed from 'Landlord')
echo   * Bank details section
echo   * Enhanced visual design
echo.
echo =======================================================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Update the module
echo Updating rental_management module...
echo.

docker-compose exec -T odoo odoo --update=rental_management --stop-after-init --log-level=info

if errorlevel 1 (
    echo.
    echo [ERROR] Module update failed
    echo Check the logs above for errors
    pause
    exit /b 1
)

echo.
echo [OK] Module updated successfully
echo.

REM Restart Odoo
echo Restarting Odoo to apply changes...
docker-compose restart odoo

if errorlevel 1 (
    echo.
    echo [ERROR] Odoo restart failed
    pause
    exit /b 1
)

echo.
echo [OK] Odoo restarted successfully
echo.

echo =======================================================================
echo   Update Complete!
echo =======================================================================
echo.
echo Next steps:
echo   1. Open Odoo in your browser: http://localhost:8069
echo   2. Clear your browser cache (Ctrl+Shift+R)
echo   3. Navigate to a property record
echo   4. Click 'Print' - 'Sales Offer' to view the new report
echo.
echo For detailed changes, see:
echo   rental_management\SALES_OFFER_ENHANCEMENT_SUMMARY.md
echo.
echo Backup file created:
echo   rental_management\report\property_brochure_enhanced_report.xml.backup
echo.
echo =======================================================================
pause
