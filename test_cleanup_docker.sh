#!/bin/bash

# =============================================================================
# Odoo Module Cleanup Docker Test Script
# =============================================================================
# This script copies the cleanup_modules.sh to the Odoo container and
# executes it there to test the functionality in the Docker environment.
#
# Author: GitHub Copilot
# Version: 1.0
# =============================================================================

# Set default options
DRY_RUN=true
COPY_ONLY=false
SHOW_HELP=false
CONTAINER_NAME="odoo"
MODULES_PATH="/mnt/extra-addons"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="docker_cleanup_test_${TIMESTAMP}.log"

# Process command-line arguments
for arg in "$@"; do
  case $arg in
    --no-dry-run)
      DRY_RUN=false
      ;;
    --copy-only)
      COPY_ONLY=true
      ;;
    --help)
      SHOW_HELP=true
      ;;
    --container=*)
      CONTAINER_NAME="${arg#*=}"
      ;;
    --modules-path=*)
      MODULES_PATH="${arg#*=}"
      ;;
  esac
done

# Show help if requested
if [ "$SHOW_HELP" = true ]; then
  echo "Odoo Module Cleanup Docker Test Script"
  echo ""
  echo "This script copies the cleanup_modules.sh to the Odoo container"
  echo "and executes it there to test the functionality."
  echo ""
  echo "Usage: ./test_cleanup_docker.sh [options]"
  echo ""
  echo "Options:"
  echo "  --no-dry-run       Run the actual cleanup (default is dry-run)"
  echo "  --copy-only        Only copy the script to container without executing"
  echo "  --container=NAME   Set the container name (default: odoo)"
  echo "  --modules-path=PATH   Set the modules path in container (default: /mnt/extra-addons)"
  echo "  --help             Show this help message"
  echo ""
  exit 0
fi

# Setup log file
echo "===== Odoo Module Cleanup Docker Test - $(date) =====" > "$LOG_FILE"

# Function to log messages
log_message() {
  local message="$1"
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $message" | tee -a "$LOG_FILE"
}

# Check if Docker is running
log_message "Checking if Docker is running..."
if ! docker info >/dev/null 2>&1; then
  log_message "ERROR: Docker is not running or not accessible. Please start Docker and try again."
  exit 1
fi

# Check if the container exists and is running
log_message "Checking if container '${CONTAINER_NAME}' is running..."
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  log_message "ERROR: Container '${CONTAINER_NAME}' is not running. Please start it and try again."
  exit 1
fi

# Copy the cleanup script to the container
log_message "Copying cleanup_modules.sh to the container..."
if ! docker cp cleanup_modules.sh "${CONTAINER_NAME}:${MODULES_PATH}/"; then
  log_message "ERROR: Failed to copy cleanup_modules.sh to the container."
  exit 1
fi

# Make the script executable in the container
log_message "Making the script executable in the container..."
docker exec "${CONTAINER_NAME}" chmod +x "${MODULES_PATH}/cleanup_modules.sh"
if [ $? -ne 0 ]; then
  log_message "ERROR: Failed to make the script executable."
  exit 1
fi

# Exit if only copying was requested
if [ "$COPY_ONLY" = true ]; then
  log_message "Script copied to container. Exiting as requested with --copy-only option."
  exit 0
fi

# Run the script in the container
log_message "Running the cleanup script in the container..."
if [ "$DRY_RUN" = true ]; then
  log_message "Running in DRY RUN mode..."
  docker exec "${CONTAINER_NAME}" bash -c "cd ${MODULES_PATH} && ./cleanup_modules.sh --dry-run" | tee -a "$LOG_FILE"
else
  log_message "WARNING: Running actual cleanup (not dry run)..."
  docker exec "${CONTAINER_NAME}" bash -c "cd ${MODULES_PATH} && ./cleanup_modules.sh" | tee -a "$LOG_FILE"
fi

# Check the result
if [ $? -eq 0 ]; then
  log_message "Cleanup script executed successfully."
else
  log_message "ERROR: Cleanup script failed."
  exit 1
fi

# Summary
log_message "Test completed. Log saved to ${LOG_FILE}"
if [ "$DRY_RUN" = true ]; then
  log_message "This was a DRY RUN. No files were actually deleted."
  log_message "To perform actual cleanup, run with --no-dry-run option."
else
  log_message "Actual cleanup was performed."
fi

echo "===== Test Finished =====" >> "$LOG_FILE"