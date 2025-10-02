@echo off
REM Direct Fix for External ID Issue - rental_management module
REM For scholarixv17 server environment

echo ============================================================
echo DIRECT FIX: Updating rental_management module
echo Server: 139.84.163.11 (scholarixv17)
echo Database: scholarixv17
echo ============================================================
echo.
echo This will SSH to your server and run the update command.
echo Make sure you have SSH access configured.
echo.
pause

REM SSH to server and run update
ssh root@139.84.163.11 "cd /var/odoo/scholarixv17 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 --update=rental_management"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS! Module updated successfully.
    echo The external ID has been recreated.
    echo.
    echo Next steps:
    echo 1. Restart Odoo service on server
    echo 2. Test the Payment Plans menu
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo ERROR! Update failed or SSH not configured.
    echo.
    echo MANUAL STEPS - Run on your server:
    echo 1. SSH to server: ssh scholarixv17
    echo 2. Run: cd /var/odoo/scholarixv17
    echo 3. Run: sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 --update=rental_management
    echo.
    echo OR use Odoo UI:
    echo 1. Go to Apps menu
    echo 2. Remove 'Apps' filter
    echo 3. Find rental_management
    echo 4. Click Upgrade button
    echo ============================================================
)

pause
