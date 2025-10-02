@echo off
REM Fix for landlord_id field reference error
REM This reinstalls the module to clean up old database definitions

echo ============================================================
echo FIXING: landlord_id field reference error
echo This will REINSTALL rental_management module
echo ============================================================
echo.
echo Error: Field landlord_id referenced in property.rental.owner_id
echo Cause: Old model definitions in database
echo.
echo Solution: Reinstall module with -i flag
echo This will:
echo  - Remove old model definitions
echo  - Recreate all models fresh
echo  - Fix the sequence field issue
echo  - Clean up database inconsistencies
echo.
pause
echo.
echo Connecting to server and reinstalling module...
echo.

ssh root@139.84.163.11 "cd /var/odoo/scholarixv17 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 -i rental_management"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS! Module reinstalled.
    echo.
    echo All old field definitions have been cleaned up.
    echo The sequence field fix has been applied.
    echo.
    echo Test the Payment Plans menu now.
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo ERROR! Reinstall failed.
    echo.
    echo Try manual database cleanup:
    echo 1. SSH to server
    echo 2. Connect to database: psql -U odoo -d scholarixv17
    echo 3. DELETE FROM ir_model_fields WHERE model='property.rental';
    echo 4. DELETE FROM ir_model WHERE model='property.rental';
    echo 5. Then update module
    echo ============================================================
)

pause
