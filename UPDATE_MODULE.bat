@echo off
REM One-line fix for rental_management external ID issue
echo Connecting to server 139.84.163.11 and updating module...
ssh root@139.84.163.11 "cd /var/odoo/scholarixv17 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv17 --update=rental_management"
echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! Module updated. Test the Payment Plans menu.
) else (
    echo FAILED! Use Odoo UI: Apps ^> rental_management ^> Upgrade
)
pause
