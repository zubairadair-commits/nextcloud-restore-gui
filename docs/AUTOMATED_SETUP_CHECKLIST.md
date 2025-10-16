# Automated Setup Checklist for Scheduled Backups

## Overview

The Nextcloud Restore & Backup Utility now includes a comprehensive automated setup checklist that validates all aspects of scheduled backup configuration before creating a task. This feature significantly improves reliability and user experience by catching configuration issues early.

---

## Features

### 1. Pre-Creation Validation ✅

Before creating a scheduled backup task, the system automatically validates:

#### ✓ Executable Path Verification
- Checks if the backup script or EXE file exists
- Validates the path is accessible
- Error: "✗ Executable path not found: [path]"

#### ✓ Start Directory Validation
- Verifies the 'Start in' directory (parent of executable) is valid
- Ensures the directory exists and is accessible
- Error: "✗ Start directory not found: [path]"

#### ✓ Task Arguments Validation
- Confirms all required arguments are present:
  - `--scheduled` flag
  - `--backup-dir` with directory path
  - Encryption flag (`--encrypt` or `--no-encrypt`)
  - Password if encryption is enabled
- Error: "✗ Missing required arguments: [list]"

#### ✓ Backup Destination Writable Check
- Tests if backup directory exists
- Verifies write permissions by creating a test file
- Error: "✗ Backup directory is not writable: [reason]"

#### ✓ Log File Location Check
- Verifies log directory exists or can be created
- Tests log file write capability
- Error: "✗ Cannot write to log file: [reason]"

#### ✓ Task Scheduler Fields Validation
- Validates schedule type (daily/weekly/monthly)
- Checks time format (HH:MM)
- Verifies task name is not empty
- Error: "✗ Invalid time format: [time]. Must be HH:MM"

### 2. Test Run Button 🧪

**Location**: Schedule Backup Configuration screen

**Purpose**: Run an instant test backup to verify configuration

**What it does**:
- Creates a minimal test backup file
- Tests actual file creation in the specified directory
- Verifies write permissions
- Provides immediate feedback

**Output**:
```
✓ Test backup successful!

Test file created: test_backup_20241014_150530.tar.gz
Size: 234 bytes
Location: C:\Backups\Nextcloud

Your scheduled backup configuration is working correctly.
```

### 3. Last Run Status Display 📊

**Location**: Schedule Backup Configuration screen (when task exists)

**Shows**:
- Task status (Running/Ready/Disabled)
- Last run time
- Next scheduled run time
- Most recent backup file information:
  - File name
  - Creation time
  - File size
  - Age (hours since creation)
- Cloud sync status (if applicable)

**Example Display**:
```
📊 Last Run Status

Status: Ready
Last Run: 2024-10-14 02:00:15
Next Run: 2024-10-15 02:00:00

✓ Recent Backup Found:
  File: nextcloud_backup_20241014_020015.tar.gz
  Created: 2024-10-14 02:00:45
  Size: 125.67 MB
  Age: 13.1 hours ago
```

### 4. View Recent Logs 📄

**Location**: Last Run Status section

**Purpose**: Quick access to recent log entries

**Features**:
- Shows last 200 log entries
- Filters for scheduled backup-related entries
- Displays in scrollable window
- Includes validation, test runs, and scheduled executions

**Log Entry Types**:
- `VALIDATION:` - Pre-creation validation checks
- `TEST RUN:` - Test backup execution
- `SCHEDULED:` - Scheduled backup execution
- `VERIFICATION:` - Post-run verification

### 5. Verify Scheduled Backup 🔍

**Location**: Schedule Backup Configuration screen (when task exists)

**Purpose**: Confirm scheduled backup is working correctly

**Checks**:
1. **Backup File Existence**: Looks for recent backup files
2. **Log Entry Verification**: Confirms backup logged in system logs
3. **Recency Check**: Warns if last backup is > 48 hours old

**Output Examples**:

**Success**:
```
✓ Recent backup found: nextcloud_backup_20241014_020015.tar.gz
  Created: 2024-10-14 02:00:45
  Size: 125.67 MB
✓ Found 5 scheduled backup log entries

✓ Verification successful: Scheduled backup is working correctly
```

**Warning**:
```
⚠ Last backup is 75.3 hours old
✓ Found 3 scheduled backup log entries

⚠ Backup file exists but no recent log entries found
```

**Failure**:
```
✗ No backup files found in directory
⚠ No scheduled backup entries found in recent logs

✗ Verification failed: No recent backup found
```

### 6. Enhanced Error Messages

All validation errors include:
- ✗ Clear indicator of failure
- Specific problem description
- Path or value that caused the issue
- Actionable guidance

**Example Error Messages**:

```
❌ Setup Validation Failed

The following issues were found:

• Backup directory is not writable: Permission denied
• Invalid time format: 25:00. Must be HH:MM

Please fix these issues before creating the scheduled backup.

Detailed Validation Results:

✓ Executable path exists: C:\App\nextcloud_backup.exe
✓ Start directory is valid: C:\App
✗ Task arguments are correct: --scheduled --backup-dir C:\Backups
✗ Backup directory is not writable: Permission denied
✓ Log file is writable: C:\Users\...\Documents\NextcloudLogs\...
✗ Task fields are valid (name: NextcloudBackup, type: daily, time: 25:00)
```

---

## User Workflow

### Creating a Scheduled Backup

1. **Configure Settings**
   - Select backup directory
   - Choose frequency (daily/weekly/monthly)
   - Set backup time
   - Enable/disable encryption

2. **Test Configuration (Optional)**
   - Click "🧪 Test Run" button
   - Wait for test backup to complete
   - Review success/failure message

3. **Create Schedule**
   - Click "Create/Update Schedule"
   - **Automatic validation runs**
   - Review validation results
   - Confirm creation if all checks pass
   - Fix issues if validation fails

4. **Verify Setup**
   - Wait for first scheduled run (or trigger manually)
   - Click "🔍 Verify Scheduled Backup"
   - Review verification results

### Monitoring Scheduled Backups

1. **Check Status**
   - Open Schedule Backup screen
   - Review "Last Run Status" section
   - Check backup file information

2. **View Logs**
   - Click "📄 View Recent Logs"
   - Review scheduled backup entries
   - Look for errors or warnings

3. **Verify Operation**
   - Click "🔍 Verify Scheduled Backup"
   - Confirm backup files exist
   - Check log entries are present

---

## Technical Details

### Validation Function

```python
validate_scheduled_task_setup(task_name, schedule_type, schedule_time, 
                               backup_dir, encrypt, password)
```

**Returns**:
```python
{
    'exe_path_exists': (bool, message),
    'start_dir_valid': (bool, message),
    'arguments_valid': (bool, message),
    'backup_dir_writable': (bool, message),
    'log_file_writable': (bool, message),
    'task_fields_valid': (bool, message),
    'all_valid': bool,
    'errors': [list of error messages]
}
```

### Test Run Function

```python
run_test_backup(backup_dir, encrypt, password)
```

**Returns**: `(success: bool, message: str)`

### Verification Function

```python
verify_scheduled_backup_ran(backup_dir, task_name)
```

**Returns**:
```python
{
    'backup_file_exists': bool,
    'log_entry_exists': bool,
    'backup_info': dict or None,
    'recent_logs': list,
    'success': bool,
    'message': str
}
```

### Logging

All validation, test, and verification operations are logged:

```
2024-10-14 15:05:44 - INFO - VALIDATION: Executable path verified: C:\App\nextcloud.exe
2024-10-14 15:05:44 - INFO - VALIDATION: Backup directory is writable: C:\Backups
2024-10-14 15:05:44 - INFO - VALIDATION: All checks passed successfully
2024-10-14 15:06:12 - INFO - TEST RUN: Starting test backup
2024-10-14 15:06:13 - INFO - TEST RUN: Test backup created successfully
2024-10-14 15:07:30 - INFO - VERIFICATION: Scheduled backup verification completed. Success: True
```

---

## Benefits

### For Users

1. **Confidence**: Know setup is correct before first scheduled run
2. **Early Detection**: Catch configuration issues immediately
3. **Self-Service**: Test and verify without technical knowledge
4. **Visibility**: See when backups ran and if they succeeded
5. **Troubleshooting**: Quick access to logs for debugging

### For System Reliability

1. **Reduced Failures**: Pre-validation prevents common mistakes
2. **Better Logging**: Comprehensive logs for troubleshooting
3. **Automated Testing**: Built-in test capability
4. **Post-Verification**: Confirm scheduled tasks are working
5. **Early Warning**: Detect issues before data loss

---

## Troubleshooting

### Validation Fails: Backup Directory Not Writable

**Cause**: Insufficient permissions or directory doesn't exist

**Solution**:
1. Verify directory exists
2. Check folder permissions (right-click → Properties → Security)
3. Try selecting a different directory
4. Create directory manually with write permissions

### Test Run Fails

**Cause**: Configuration issue or permission problem

**Solution**:
1. Review error message carefully
2. Verify backup directory is correct
3. Check available disk space
4. Test with encryption disabled
5. Review logs for detailed error

### No Recent Backup Found

**Cause**: Scheduled task not running or failing

**Solution**:
1. Open Task Scheduler (Windows)
2. Find "NextcloudBackup" task
3. Check task history for errors
4. Verify task is enabled
5. Run task manually to test
6. Review logs for errors

### Log File Not Writable

**Cause**: Permissions issue in Documents folder

**Solution**:
1. Check Documents folder exists
2. Verify permissions on Documents folder
3. Manually create NextcloudLogs subfolder
4. Run application as administrator (if needed)

---

## Testing

### Test Suite: `test_scheduled_backup_validation.py`

**Coverage**:
- ✓ Validation functions exist
- ✓ All validation checks present
- ✓ Validation logging implemented
- ✓ Test run function works
- ✓ Last run verification works
- ✓ UI integration complete
- ✓ Error messages clear
- ✓ All 10 requirements met

**Run Tests**:
```bash
python3 test_scheduled_backup_validation.py
```

**Expected Output**:
```
======================================================================
Automated Setup Checklist - Validation Tests
======================================================================
...
All tests passed! ✓
======================================================================

✅ Automated Setup Checklist Implementation Complete!

Features Implemented:
  1. ✓ Backup script/EXE path validation
  2. ✓ Start directory validation
  3. ✓ Task arguments validation
  4. ✓ Backup destination writable check
  5. ✓ Log file writable check
  6. ✓ Task Scheduler fields validation
  7. ✓ Test Run button for instant verification
  8. ✓ Clear error messages
  9. ✓ Last run status display
 10. ✓ Post-run backup/log verification
```

---

## Future Enhancements

Potential improvements for future versions:

1. **Email Notifications**: Alert on validation or backup failures
2. **Scheduled Test Runs**: Periodic automatic tests
3. **Health Dashboard**: Visual status indicators
4. **Backup Size Trending**: Track backup size over time
5. **Retention Policy Validation**: Check for sufficient space
6. **Remote Backup Verification**: Verify cloud uploads completed
7. **Recovery Testing**: Automated restore tests
8. **Performance Metrics**: Track backup duration trends

---

## Related Documentation

- [SCHEDULED_BACKUP_FEATURE.md](SCHEDULED_BACKUP_FEATURE.md) - Original scheduled backup feature
- [QUICK_START_SCHEDULED_BACKUP.md](QUICK_START_SCHEDULED_BACKUP.md) - User quick start guide
- [IMPLEMENTATION_COMPLETE_SCHEDULED_BACKUP.md](IMPLEMENTATION_COMPLETE_SCHEDULED_BACKUP.md) - Implementation details

---

## Version History

- **v1.0** (2024-10-14): Initial implementation
  - Pre-creation validation
  - Test run functionality
  - Last run status display
  - Log viewer
  - Post-run verification
  - Enhanced error messages

---

## Support

For issues or questions:
1. Check validation error messages
2. Review logs via "View Recent Logs"
3. Run "Test Run" to diagnose issues
4. Use "Verify Scheduled Backup" for confirmation
5. Check Windows Task Scheduler for task status
6. Review application logs in Documents/NextcloudLogs/
