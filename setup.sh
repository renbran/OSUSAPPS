#!/bin/bash

function show_usage {
    echo "Odoo 17 Local Testing Environment"
    echo
    echo "Usage:"
    echo "  ./setup.sh start     - Start containers"
    echo "  ./setup.sh stop      - Stop containers"
    echo "  ./setup.sh restart   - Restart containers"
    echo "  ./setup.sh logs      - View logs"
    echo "  ./setup.sh build     - Rebuild containers"
    echo "  ./setup.sh shell     - Access Odoo shell"
    echo "  ./setup.sh update    - Update all modules"
    echo "  ./setup.sh update_mod MODULE - Update specific module"
    echo "  ./setup.sh status    - Check status"
}

case "$1" in
    start)
        echo "Starting Odoo containers..."
        docker-compose up -d
        ;;
    stop)
        echo "Stopping Odoo containers..."
        docker-compose down
        ;;
    restart)
        echo "Restarting Odoo containers..."
        docker-compose restart
        ;;
    logs)
        echo "Showing Odoo logs..."
        docker-compose logs -f odoo
        ;;
    build)
        echo "Rebuilding Odoo containers..."
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    shell)
        echo "Opening Odoo shell..."
        docker-compose exec odoo bash
        ;;
    update)
        echo "Updating all modules..."
        docker-compose exec odoo odoo --stop-after-init --update=all
        ;;
    update_mod)
        if [ -z "$2" ]; then
            echo "Please specify module name"
            show_usage
        else
            echo "Updating module $2..."
            docker-compose exec odoo odoo --stop-after-init --update=$2
        fi
        ;;
    status)
        echo "Checking container status..."
        docker-compose ps
        ;;
    *)
        show_usage
        ;;
esac
