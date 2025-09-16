#!/bin/bash

# =============================================================================
# Module Cleanup Script for Odoo 17
# =============================================================================
# This script safely removes Python cache files and other temporary files 
# from Odoo modules while creating a backup before deletion.
#
# Usage:
#   ./cleanup_modules.sh [options]
#
# Options:
#   --dry-run    Show what would be deleted without actually deleting
#   --no-backup  Skip creating a backup (NOT RECOMMENDED)
#   --help       Show this help message
#
# Author: GitHub Copilot
# Version: 1.0
# =============================================================================

# Set default options
DRY_RUN=false
CREATE_BACKUP=true
SHOW_HELP=false
BASE_DIR=$(pwd)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BASE_DIR}/module_backups"
BACKUP_FILE="${BACKUP_DIR}/modules_backup_${TIMESTAMP}.tar.gz"
LOG_FILE="${BASE_DIR}/cleanup_${TIMESTAMP}.log"

# Process command-line arguments
for arg in "$@"; do
  case $arg in
    --dry-run)
      DRY_RUN=true
      echo "Running in DRY RUN mode - no files will be deleted"
      ;;
    --no-backup)
      CREATE_BACKUP=false
      echo "WARNING: Running without creating backups. This is NOT RECOMMENDED."
      ;;
    --help)
      SHOW_HELP=true
      ;;
  esac
done

# Show help if requested
if [ "$SHOW_HELP" = true ]; then
  echo "Odoo Module Cleanup Script"
  echo ""
  echo "This script removes Python cache files and other temporary files"
  echo "from Odoo modules while creating a backup before deletion."
  echo ""
  echo "Usage: ./cleanup_modules.sh [options]"
  echo ""
  echo "Options:"
  echo "  --dry-run    Show what would be deleted without actually deleting"
  echo "  --no-backup  Skip creating a backup (NOT RECOMMENDED)"
  echo "  --help       Show this help message"
  echo ""
  exit 0
fi

# Setup log file
echo "===== Odoo Module Cleanup - $(date) =====" > "$LOG_FILE"
echo "Working directory: $BASE_DIR" >> "$LOG_FILE"

# Function to log messages
log_message() {
  local message="$1"
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $message" >> "$LOG_FILE"
  echo "$message"
}

# Create backup directory if it doesn't exist
if [ "$CREATE_BACKUP" = true ]; then
  log_message "Creating backup directory at $BACKUP_DIR"
  mkdir -p "$BACKUP_DIR"
  
  log_message "Creating backup archive at $BACKUP_FILE"
  if [ "$DRY_RUN" = false ]; then
    # Create a backup of all module directories
    log_message "Identifying modules to back up..."
    MODULES=$(find "$BASE_DIR" -maxdepth 1 -type d -not -path "$BASE_DIR" -not -path "$BACKUP_DIR")
    MODULE_COUNT=$(echo "$MODULES" | wc -l)
    log_message "Found $MODULE_COUNT modules/directories to back up"
    
    # Check if modules were found
    if [ -z "$MODULES" ]; then
      log_message "WARNING: No modules found to back up!"
    else
      # Create backup archive
      tar -czf "$BACKUP_FILE" $(echo "$MODULES" | tr '\n' ' ') 2>/dev/null
      if [ $? -eq 0 ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        log_message "Backup created successfully (Size: $BACKUP_SIZE)"
        
        # Verify backup integrity
        log_message "Verifying backup integrity..."
        tar -tzf "$BACKUP_FILE" >/dev/null 2>&1
        if [ $? -eq 0 ]; then
          log_message "Backup verified and is valid"
        else
          log_message "ERROR: Backup verification failed! Aborting cleanup."
          exit 1
        fi
      else
        log_message "ERROR: Backup creation failed! Aborting cleanup."
        exit 1
      fi
    fi
  else
    log_message "[DRY RUN] Would create backup of all modules"
  fi
fi

# Function to check if a path is safe to remove
is_safe_to_remove() {
  local target="$1"
  local type="$2"
  
  # Safety check 1: Don't delete outside working directory
  if [[ ! "$target" == "$BASE_DIR"* ]]; then
    log_message "SAFETY ERROR: Attempted to remove $type outside working directory: $target"
    return 1
  fi
  
  # Safety check 2: Don't delete important module files
  if [[ "$target" == *"__init__.py" ]] || [[ "$target" == *"__manifest__.py" ]]; then
    log_message "SAFETY ERROR: Attempted to remove critical module file: $target"
    return 1
  fi
  
  # Safety check 3: Ensure we're only removing cache or temp files
  if [[ "$type" == "cache directory" && "$target" != *"__pycache__"* ]]; then
    log_message "SAFETY ERROR: Attempted to remove non-cache directory: $target"
    return 1
  elif [[ "$type" == "compiled Python file" && "$target" != *".pyc" ]]; then
    log_message "SAFETY ERROR: Attempted to remove non-compiled Python file: $target"
    return 1
  elif [[ "$type" == "temporary file" && ! ( "$target" == *".bak" || "$target" == *".backup" || \
         "$target" == *".tmp" || "$target" == *"~" || "$target" == *".swp" ) ]]; then
    log_message "SAFETY ERROR: Attempted to remove non-temporary file: $target"
    return 1
  fi
  
  return 0
}

# Function to safely remove files/directories
safe_remove() {
  local target="$1"
  local type="$2"
  
  if [ -e "$target" ]; then
    # Check if it's safe to remove
    if is_safe_to_remove "$target" "$type"; then
      if [ "$DRY_RUN" = true ]; then
        log_message "[DRY RUN] Would remove $type: $target"
      else
        rm -rf "$target"
        if [ $? -eq 0 ]; then
          log_message "Removed $type: $target"
        else
          log_message "ERROR: Failed to remove $type: $target"
        fi
      fi
    else
      log_message "SKIPPED: $target (safety check failed)"
    fi
  fi
}

# Function to confirm with user before proceeding
confirm_action() {
  # Skip confirmation if in dry run mode
  if [ "$DRY_RUN" = true ]; then
    return 0
  fi
  
  echo ""
  echo "WARNING: This will remove all Python cache files and temporary files."
  echo "A backup will be created at: $BACKUP_FILE"
  echo ""
  read -p "Do you want to proceed with deletion? (y/n): " response
  
  case "$response" in
    [yY][eE][sS]|[yY]) 
      return 0
      ;;
    *)
      log_message "Cleanup aborted by user"
      exit 0
      ;;
  esac
}

# Main cleanup process
log_message "Starting cleanup process..."

# Confirm with user before proceeding with actual deletion
confirm_action

# 1. Remove Python cache directories
log_message "Looking for Python cache directories..."
CACHE_DIRS=$(find "$BASE_DIR" -type d -name "__pycache__")

if [ -n "$CACHE_DIRS" ]; then
  log_message "Found $(echo "$CACHE_DIRS" | wc -l) Python cache directories"
  
  echo "$CACHE_DIRS" | while read -r dir; do
    safe_remove "$dir" "cache directory"
  done
else
  log_message "No Python cache directories found"
fi

# 2. Remove compiled Python files (.pyc)
log_message "Looking for compiled Python files (.pyc)..."
PYC_FILES=$(find "$BASE_DIR" -type f -name "*.pyc")

if [ -n "$PYC_FILES" ]; then
  log_message "Found $(echo "$PYC_FILES" | wc -l) compiled Python files"
  
  echo "$PYC_FILES" | while read -r file; do
    safe_remove "$file" "compiled Python file"
  done
else
  log_message "No compiled Python files found"
fi

# 3. Remove backup/temporary files
log_message "Looking for backup/temporary files..."
TEMP_FILES=$(find "$BASE_DIR" -type f \( -name "*.bak" -o -name "*.backup" -o -name "*.tmp" -o -name "*~" -o -name "*.swp" \))

if [ -n "$TEMP_FILES" ]; then
  log_message "Found $(echo "$TEMP_FILES" | wc -l) backup/temporary files"
  
  echo "$TEMP_FILES" | while read -r file; do
    safe_remove "$file" "temporary file"
  done
else
  log_message "No backup/temporary files found"
fi

# Add summary to log
log_message "Cleanup process completed"
log_message "Summary:"
log_message "  - Python cache directories processed: $(echo "$CACHE_DIRS" | wc -l)"
log_message "  - Compiled Python files processed: $(echo "$PYC_FILES" | wc -l)" 
log_message "  - Backup/temporary files processed: $(echo "$TEMP_FILES" | wc -l)"

if [ "$DRY_RUN" = true ]; then
  log_message "DRY RUN completed. No files were actually deleted."
  log_message "To perform actual deletion, run without the --dry-run option."
else
  log_message "Actual deletion completed. Log saved to $LOG_FILE"
  if [ "$CREATE_BACKUP" = true ]; then
    log_message "Backup saved to $BACKUP_FILE"
  fi
fi

echo "===== Cleanup Finished =====" >> "$LOG_FILE"