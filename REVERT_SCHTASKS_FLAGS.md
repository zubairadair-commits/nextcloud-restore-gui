# Revert Scheduled Task Creation Flags

## Overview

This change reverts the scheduled task creation flags to remove `/RL HIGHEST` and `/Z` from the schtasks command when creating a scheduled backup. The previous working behavior has been restored with only the essential flags used for schtasks.

## Problem Statement

The `/RL HIGHEST` and `/Z` flags were previously added to scheduled task creation, but they need to be reverted to restore the previous working behavior. These flags can cause issues with task execution in some environments.

## Solution

### Removed Flags

1. **`/RL HIGHEST`** - Run with highest privileges
   - Previously added to run tasks with elevated privileges
   - Removed to restore previous behavior

2. **`/Z`** - Run task as soon as possible after scheduled start is missed
   - Previously added to catch up on missed tasks
   - Removed to restore previous behavior

### Essential Flags Retained

The following essential flags are still used:

1. **`/Create`** - Create a new scheduled task
2. **`/TN`** - Task name
3. **`/TR`** - Task run command
4. **`/SC`** - Schedule type (DAILY, WEEKLY, MONTHLY)
5. **`/ST`** - Start time (HH:MM format)
6. **`/F`** - Force creation, overwrite if exists
7. **`/D`** - Day of week/month (for WEEKLY/MONTHLY schedules)

## Code Changes

### File: `nextcloud_restore_and_backup-v9.py`

**Before:**
```python
schtasks_cmd.extend([
    "/ST", schedule_time,
    "/RL", "HIGHEST",  # Run with highest privileges
    "/Z",  # Run task as soon as possible after scheduled start is missed
    "/F"  # Force creation, overwrite if exists
])
```

**After:**
```python
schtasks_cmd.extend([
    "/ST", schedule_time,
    "/F"  # Force creation, overwrite if exists
])
```

## Command Examples

### Daily Backup
```
schtasks /Create /TN "NextcloudBackup" /TR "path\to\exe --scheduled --backup-dir \"C:\Backups\"" /SC DAILY /ST 02:00 /F
```

### Weekly Backup
```
schtasks /Create /TN "NextcloudBackup" /TR "path\to\exe --scheduled --backup-dir \"C:\Backups\"" /SC WEEKLY /D MON /ST 02:00 /F
```

### Monthly Backup
```
schtasks /Create /TN "NextcloudBackup" /TR "path\to\exe --scheduled --backup-dir \"C:\Backups\"" /SC MONTHLY /D 1 /ST 02:00 /F
```

## Quoting Behavior

The implementation correctly handles paths with spaces:

1. **EXE Path**: Wrapped in double quotes if it contains spaces
   - Python scripts: `python "C:\My Documents\script.py"`
   - Executables: `"C:\Program Files\app.exe"`

2. **Backup Directory**: Wrapped in double quotes
   - Example: `--backup-dir "C:\My Backups\Nextcloud"`

## Testing

All tests have been updated to verify the reverted behavior:

### Updated Test Files
1. `test_complete_workflow.py` - Verifies flags are NOT present
2. `test_integration_scheduled_enhancements.py` - Checks for absence of flags
3. `test_scheduled_backup_enhancements.py` - Validates essential flags only

### Test Results
```
✅ test_schtasks_fix.py - All tests passed
✅ test_scheduled_backup_enhancements.py - All tests passed
✅ test_integration_scheduled_enhancements.py - All tests passed
✅ test_complete_workflow.py - All tests passed
✅ test_scheduled_backup.py - All tests passed
✅ test_scheduled_task_integration.py - All tests passed
```

## Impact

### Changes
- Scheduled tasks will be created without `/RL HIGHEST` and `/Z` flags
- Tasks will run with standard user privileges (or as configured in Task Scheduler)
- Missed tasks will NOT automatically run when the computer turns on

### No Impact On
- Task creation and deletion
- Command-line argument handling
- Backup execution when scheduled
- Backup history tracking
- Path quoting for spaces
- All other scheduled backup features

## Backward Compatibility

This change is backward compatible:
- Existing scheduled tasks will continue to work
- No changes to user interface
- No changes to configuration files
- No changes to backup process

## Files Modified

1. **`nextcloud_restore_and_backup-v9.py`** - Main application
   - Removed `/RL HIGHEST` and `/Z` flags from `create_scheduled_task` function

2. **`test_complete_workflow.py`** - Updated to check flags are NOT present

3. **`test_integration_scheduled_enhancements.py`** - Updated to verify reverted behavior

4. **`test_scheduled_backup_enhancements.py`** - Updated to validate essential flags only

## Conclusion

This change successfully reverts the scheduled task creation flags to the previous working behavior, using only the essential flags required for Windows Task Scheduler. All tests pass, confirming the implementation is correct.
