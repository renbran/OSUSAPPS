# Module Cleanup Documentation

## Overview

This documentation explains the process of cleaning up cache files and other temporary files from Odoo modules in the OSUSAPPS project. The cleanup is essential for ensuring optimal performance and preventing issues that can arise from stale cache files.

## Why Cleanup Is Necessary

Python generates cache files (`.pyc` files and `__pycache__` directories) during execution to improve performance. However, these files can sometimes cause issues:

1. **Stale Cache**: Old bytecode files can persist even after source code changes, leading to unexpected behavior
2. **Module Upgrades**: When upgrading Odoo modules, cached files from previous versions may interfere
3. **Disk Space**: Cache files consume additional disk space unnecessarily
4. **Version Control**: These files should not be in version control systems but sometimes get committed accidentally
5. **Clean Deployments**: Having a clean module structure improves deployment consistency

## The Cleanup Script: `cleanup_modules.sh`

A dedicated script has been created to safely handle the cleanup process. This script removes Python cache files and directories while creating a backup first to ensure no data is lost.

### What the Script Removes

1. **Python Cache Directories**: All `__pycache__` directories
2. **Python Compiled Files**: All `.pyc` files
3. **Temporary/Backup Files**: Files with extensions like `.bak`, `.backup`, `.tmp`, `.swp`, and files ending with `~`

### Safety Features

The script includes several safety measures to prevent accidental data loss:

1. **Backup Creation**: Creates a full backup of all modules before deletion
2. **Dry Run Mode**: Allows previewing what would be deleted without actually removing files
3. **Safety Checks**: Prevents deletion of critical files or directories
4. **Confirmation Prompt**: Requires user confirmation before proceeding with deletion
5. **Detailed Logging**: Logs all actions to a timestamped log file

## Usage Instructions

### Basic Usage

```bash
cd /path/to/OSUSAPPS
./cleanup_modules.sh
```

This will:

1. Create a backup of all modules
2. Prompt for confirmation
3. Remove all cache files
4. Generate a log file

### Command-Line Options

- **Dry Run Mode**: `./cleanup_modules.sh --dry-run`  
  Shows what would be deleted without actually removing any files

- **Skip Backup** (not recommended): `./cleanup_modules.sh --no-backup`  
  Skips the backup creation step (use with caution)

- **Help**: `./cleanup_modules.sh --help`  
  Shows usage instructions and available options

### Example Workflow

1. **First Run in Dry-Run Mode**:

   ```bash
   ./cleanup_modules.sh --dry-run
   ```

   Review the output to ensure the correct files will be removed

2. **Perform Actual Cleanup**:

   ```bash
   ./cleanup_modules.sh
   ```

   This will create a backup and perform the actual deletion

3. **Verify Results**:
   - Check the log file created in the root directory
   - Ensure Odoo modules still function correctly

## Best Practices

1. **Run Before Module Updates**: Clean cache files before updating modules
2. **Regular Maintenance**: Schedule regular cleanups, especially in development environments
3. **Backup Retention**: Keep backups for a reasonable period before deleting them
4. **Test After Cleanup**: Verify module functionality after cache cleanup
5. **Include in CI/CD**: Consider incorporating cleanup in your CI/CD pipeline

## Troubleshooting

If you encounter any issues after running the cleanup script:

1. **Restore from Backup**:

   ```bash
   tar -xzf /path/to/backup/modules_backup_TIMESTAMP.tar.gz -C /path/to/restore/
   ```

2. **Regenerate Cache Files**:
   Cache files will be automatically regenerated when the Odoo server is restarted

3. **Check Permissions**:
   Ensure the script has proper permissions to access all directories

## Additional Notes

- The script identifies cache files based on naming patterns, so custom cache files with non-standard names won't be removed
- IDE-specific files in the `.vscode` directory are not removed by this script
- The script is designed to be run from the root of the OSUSAPPS directory
