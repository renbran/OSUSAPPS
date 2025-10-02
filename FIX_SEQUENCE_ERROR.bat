@echo off
REM Fix for "Invalid field 'sequence'" error in property.payment.plan model
echo ============================================================
echo FIXING: Adding missing 'sequence' field to property.payment.plan
echo Server: 139.84.163.11 (scholarixv17)
echo Database: scholarixv17
echo ============================================================
echo.
echo Changes made:
echo 1. Added 'sequence' field to PropertyPaymentPlan model
echo 2. Updated tree view to show sequence with drag-drop handle
echo 3. Updated form view to show sequence field
echo.
echo Now updating module on server...
echo.

ssh root@139.84.163.11 "cd /var/odoo/scholarixv17 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 --update=rental_management"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS! Module updated with sequence field fix.
    echo.
    echo The Payment Plans menu should now work correctly.
    echo You can drag-and-drop rows to reorder payment plans.
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo ERROR! Update failed.
    echo.
    echo Manual steps:
    echo 1. Upload files to server
    echo 2. Go to Apps menu in Odoo
    echo 3. Find rental_management and click Upgrade
    echo ============================================================
)

pause
