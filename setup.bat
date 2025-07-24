@echo off
setlocal

echo Odoo 17 Local Testing Environment

IF "%1" == "" (
    goto :usage
) ELSE (
    goto :%1
)

:usage
echo.
echo Usage:
echo   setup.bat start     - Start containers
echo   setup.bat stop      - Stop containers
echo   setup.bat restart   - Restart containers
echo   setup.bat logs      - View logs
echo   setup.bat build     - Rebuild containers
echo   setup.bat shell     - Access Odoo shell
echo   setup.bat update    - Update all modules
echo   setup.bat update_mod MODULE - Update specific module
echo   setup.bat status    - Check status
goto :eof

:start
echo Starting Odoo containers...
docker-compose up -d
goto :eof

:stop
echo Stopping Odoo containers...
docker-compose down
goto :eof

:restart
echo Restarting Odoo containers...
docker-compose restart
goto :eof

:logs
echo Showing Odoo logs...
docker-compose logs -f odoo
goto :eof

:build
echo Rebuilding Odoo containers...
docker-compose build --no-cache
docker-compose up -d
goto :eof

:shell
echo Opening Odoo shell...
docker-compose exec odoo bash
goto :eof

:update
echo Updating all modules...
docker-compose exec odoo odoo --stop-after-init --update=all
goto :eof

:update_mod
IF "%2" == "" (
    echo Please specify module name
    goto :usage
) ELSE (
    echo Updating module %2...
    docker-compose exec odoo odoo --stop-after-init --update=%2
)
goto :eof

:status
echo Checking container status...
docker-compose ps
goto :eof

endlocal
