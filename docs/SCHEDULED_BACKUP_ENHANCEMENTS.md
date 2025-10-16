# Scheduled Backup Enhancements

## Overview
This document describes the enhancements made to the scheduled backup functionality in the Nextcloud Restore & Backup Utility.

## Changes Implemented

### 1. Run with Highest Privileges
**Change:** Added `/RL HIGHEST` flag to Windows Task Scheduler task creation.

**Location:** `create_scheduled_task()` function in `nextcloud_restore_and_backup-v9.py`

**Impact:** 
- Scheduled backup tasks now run with the highest available privileges
- Ensures backup can access all necessary files and Docker containers
- Prevents permission-related backup failures

**Technical Details:**
```python
schtasks_cmd = [
    "schtasks", "/Create",
    "/TN", task_name,
    "/TR", command,
    "/ST", schedule_time,
    "/RL", "HIGHEST",  # Run with highest privileges
    "/Z"  # Run task as soon as possible after scheduled start is missed
]
```

### 2. Run Missed Tasks ASAP
**Change:** Added `/Z` flag to Windows Task Scheduler task creation.

**Location:** `create_scheduled_task()` function in `nextcloud_restore_and_backup-v9.py`

**Impact:**
- If the computer is off or asleep at the scheduled backup time, the task will run as soon as possible after the system is available
- Ensures backups are not skipped due to system downtime
- Provides better backup coverage and reliability

**Behavior:**
- If scheduled time is 2:00 AM and computer is off, task runs when computer turns on
- Task runs immediately upon system availability, not waiting for next scheduled time
- Logged in Task Scheduler history

### 3. Backup History Tracking for Scheduled Backups
**Change:** Added backup history database tracking to scheduled backup execution.

**Location:** `run_backup_process_scheduled()` function in `nextcloud_restore_and_backup-v9.py`

**Impact:**
- Scheduled backups are now recorded in the backup history database
- "Backup History" button on main page shows recent scheduled backups immediately
- Backups include metadata: timestamp, size, database type, folders, encryption status
- Marked with "Scheduled backup" note to distinguish from manual backups

**Technical Details:**
```python
# Add backup to history
folders_list = ['config', 'data'] + [f for f in copied_folders if f not in ['config', 'data']]
backup_id = self.backup_history.add_backup(
    backup_path=final_file,
    database_type=dbtype,
    folders=folders_list,
    encrypted=bool(encrypt and encryption_password),
    notes="Scheduled backup"
)
```

## Verification

### How to Verify Changes

#### 1. Verify Task Scheduler Settings (Windows Only)
After creating a scheduled backup:
1. Open Windows Task Scheduler
2. Navigate to Task Scheduler Library
3. Find your scheduled task (e.g., "NextcloudBackup")
4. Right-click → Properties
5. Go to "General" tab
6. Verify "Run with highest privileges" is checked
7. Go to "Settings" tab
8. Verify "Run task as soon as possible after a scheduled start is missed" is checked

#### 2. Verify Backup History Tracking
After a scheduled backup runs:
1. Open the Nextcloud Restore & Backup Utility
2. Click "📜 Backup History" button on main page
3. Verify the most recent backup appears in the list
4. Check that it shows:
   - Correct timestamp
   - File size
   - Database type
   - Encryption status (if applicable)
   - Note: "Scheduled backup"

#### 3. Run Automated Tests
```bash
# Test scheduled task flags
python3 test_scheduled_backup_enhancements.py

# Test integration
python3 test_integration_scheduled_enhancements.py

# Test existing functionality
python3 test_scheduled_backup.py
```

## Compatibility

- **Windows:** Full support for all features
- **Linux/Mac:** Task scheduling features not available (as before)
- **Docker:** No changes to Docker integration

## Testing

### Test Files
1. `test_scheduled_backup_enhancements.py` - Unit tests for new features
2. `test_integration_scheduled_enhancements.py` - Integration tests
3. `test_scheduled_backup.py` - Existing tests (still passing)

### Test Coverage
- ✅ Task creation includes `/RL HIGHEST` flag
- ✅ Task creation includes `/Z` flag
- ✅ Flags are properly positioned in command
- ✅ Scheduled backup adds to backup history
- ✅ History tracking occurs after successful backup
- ✅ All required parameters passed to history database
- ✅ Backup history display shows all backups
- ✅ Existing functionality unaffected
- ✅ No breaking changes introduced

## Benefits

1. **Better Reliability:** Tasks run with appropriate permissions and won't be skipped
2. **Better Visibility:** All backups (manual and scheduled) appear in backup history
3. **Better Tracking:** Can verify scheduled backups are running as expected
4. **Better Recovery:** Can see all available backup points in one place
5. **Better User Experience:** No need to check file system to verify scheduled backups ran

## Technical Notes

### Windows Task Scheduler Flags Used

| Flag | Purpose | Effect |
|------|---------|--------|
| `/RL HIGHEST` | Run level | Task runs with highest available privileges |
| `/Z` | Run after missed | Task runs ASAP if scheduled time was missed |
| `/F` | Force | Overwrites existing task with same name |

### Database Schema
No changes to database schema were required. The existing `BackupHistoryManager` class supports all necessary fields:
- `backup_path` - Full path to backup file
- `timestamp` - When backup was created
- `size_bytes` - Size of backup file
- `encrypted` - Whether backup is encrypted
- `database_type` - Type of database (pgsql, mysql, sqlite)
- `folders_backed_up` - List of folders included
- `notes` - Custom notes (used to mark scheduled backups)

## Future Enhancements

Possible future improvements:
- Email notifications when scheduled backups complete
- Configurable retention policy for scheduled backups
- Scheduled backup statistics and reporting
- Cloud backup integration for scheduled backups

## Troubleshooting

### Backup History Not Showing Scheduled Backups
1. Verify the scheduled task actually ran (check Task Scheduler history)
2. Check the log file at `Documents/NextcloudLogs/nextcloud_restore_gui.log`
3. Run a test backup using the app's "Test Backup" feature
4. Verify Docker is running when scheduled task executes

### Task Not Running with Highest Privileges
1. User account must have administrator rights
2. UAC may prompt for permission on first run
3. Verify in Task Scheduler Properties → General tab

### Task Not Running After Missed Schedule
1. Verify `/Z` flag in task properties
2. Check Task Scheduler history for missed task entries
3. Ensure system allows scheduled tasks to wake computer (if needed)

## References

- Windows Task Scheduler documentation: https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page
- Schtasks command reference: https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks
