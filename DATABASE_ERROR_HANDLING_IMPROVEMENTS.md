# Database Type Detection Error Handling Improvements

## Overview
This document describes the improvements made to error handling when database type detection fails during the backup process, as referenced in **Image 8** of the problem statement.

## Problem Statement
Previously, when database type detection failed, the application showed a generic unhelpful message:
> "Database utility 'unknown' is required but installation instructions are not available."

This provided no guidance to users on:
- Why detection failed
- What they could do about it
- How to check their configuration
- Where to get help

## Improvements Made

### 1. Enhanced Detection Failure Dialog
When database type cannot be automatically detected, users now see:

**❌ Could not automatically detect the database type from your Nextcloud container.**

**Possible reasons:**
- config.php file is missing or inaccessible
- Container does not have the expected file structure
- Permission issues reading the container filesystem
- Network connectivity issues

**📋 MANUAL SELECTION:**
Please select your database type:
- Yes = PostgreSQL (default)
- No = MySQL/MariaDB
- Cancel = Abort backup and check configuration

**ℹ️ Note:** SQLite databases are backed up automatically with the data folder.

**⚠️ If you're unsure**, click Cancel and check your Nextcloud config/config.php file to verify the 'dbtype' setting.

**For help:** https://docs.nextcloud.com/server/latest/admin_manual/configuration_database/

### 2. Improved Error Messages for Unknown/Unsupported Database Types
When an unknown or unsupported database type is detected, users now see:

**❌ DATABASE TYPE DETECTION FAILED**

The database type 'xxx' is not recognized or not supported.

**Possible reasons:**
- config.php file is missing or corrupted
- Database type is not supported (only MySQL/MariaDB, PostgreSQL, and SQLite are supported)
- Container is not accessible or not running

**What to do:**
1. Check your Nextcloud configuration file (config/config.php)
2. Verify the 'dbtype' field contains one of: 'mysql', 'pgsql', or 'sqlite'
3. Ensure your Nextcloud container is running: `docker ps`
4. For help, see: https://docs.nextcloud.com/server/latest/admin_manual/configuration_database/

**⚠️ Backup cannot proceed until the database type is correctly detected.**

### 3. Validation Before Proceeding
Added validation that checks if the detected database type is supported before proceeding with the backup:

```python
# Validate database type before proceeding
if dbtype and dbtype not in ['sqlite', 'sqlite3', 'pgsql', 'mysql', 'mariadb']:
    # Show error and return to landing page
    # Prevents backup from proceeding
```

### 4. Enhanced Console Logging
Improved console output for debugging with detailed information:

```
❌ Could not read config.php from container 'nextcloud-app'
   Error: cat: can't open '/var/www/html/config/config.php': No such file or directory
   Possible causes:
   • config.php file does not exist at /var/www/html/config/config.php
   • Insufficient permissions to read the file
   • Container is not running or not accessible
```

```
❌ Could not find 'dbtype' field in config.php
   The configuration file may be corrupted or incomplete.
   Please verify the config.php file in your Nextcloud installation.
```

```
⚠️ Detected unsupported database type: 'oracle'
   Supported types: sqlite, sqlite3, pgsql, mysql, mariadb
   Please check your Nextcloud configuration.
```

```
❌ Timeout reading config.php from container
   The container may be unresponsive or experiencing issues.
   Please check container status: docker ps
```

## Technical Changes

### Modified Functions

#### 1. `detect_database_type_from_container(container_name)`
- Added detailed error logging for each failure scenario
- Validates detected database type against supported types
- Returns unsupported types so they can be properly reported to user

#### 2. `prompt_install_database_utility(parent, dbtype, utility_name)`
- Replaced generic error message with comprehensive guidance
- Lists possible reasons for detection failure
- Provides step-by-step instructions for resolution
- Includes link to official Nextcloud documentation
- Shows error dialog (not retry dialog) for unknown types
- Returns `False` immediately for unsupported types (doesn't offer retry)

#### 3. `start_backup()` method in `NextcloudRestoreWizard` class
- Enhanced detection failure dialog with more context
- Added validation step before checking utilities
- Logs user's manual database type selection
- Shows clear error and prevents backup for unsupported types

## User Experience Flow

### Before (Poor Experience)
1. Detection fails
2. Generic "unknown utility" message
3. No guidance on what to do
4. User is stuck

### After (Improved Experience)
1. Detection fails
2. Clear explanation of possible reasons
3. Option to manually select database type
4. Guidance to check config.php if unsure
5. Link to documentation for help
6. If unsupported type detected, clear error prevents backup
7. User knows exactly what to do

## Testing
A comprehensive test suite (`test_database_error_handling.py`) was created to verify:
- Clear error messages are shown
- Manual selection is available
- Config.php guidance is provided
- Documentation links are included
- Validation prevents backup with unsupported types
- Comprehensive error logging for debugging

All tests pass successfully.

## References
- Problem Statement: Image 8 - "Database utility 'unknown' is required but installation instructions are not available"
- Nextcloud Documentation: https://docs.nextcloud.com/server/latest/admin_manual/configuration_database/
- Supported Database Types: MySQL/MariaDB, PostgreSQL, SQLite

## Benefits
1. **Clear Communication**: Users understand why detection failed
2. **Actionable Guidance**: Users know exactly what steps to take
3. **Self-Service**: Users can resolve issues without external help
4. **Safety**: Backup is prevented until database type is correctly identified
5. **Debugging**: Detailed logging helps troubleshoot issues
6. **Documentation**: Link to official help resources
7. **Better UX**: No more dead-end error messages
