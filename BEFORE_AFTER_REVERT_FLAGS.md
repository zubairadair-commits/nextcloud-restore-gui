# Before/After: Revert Scheduled Task Flags

## Visual Comparison

### Before (with /RL and /Z flags)
```python
# Create new task
schtasks_cmd = [
    "schtasks", "/Create",
    "/TN", task_name,
    "/TR", command
]
schtasks_cmd.extend(schedule_args)  # Add /SC and /D parameters
schtasks_cmd.extend([
    "/ST", schedule_time,
    "/RL", "HIGHEST",  # Run with highest privileges
    "/Z",  # Run task as soon as possible after scheduled start is missed
    "/F"  # Force creation, overwrite if exists
])
```

**Generated Command Example (Daily):**
```
schtasks /Create /TN "NextcloudBackup" /TR "C:\app.exe --scheduled --backup-dir \"C:\Backups\" --no-encrypt" /SC DAILY /ST 02:00 /RL HIGHEST /Z /F
```

### After (reverted - essential flags only)
```python
# Create new task
schtasks_cmd = [
    "schtasks", "/Create",
    "/TN", task_name,
    "/TR", command
]
schtasks_cmd.extend(schedule_args)  # Add /SC and /D parameters
schtasks_cmd.extend([
    "/ST", schedule_time,
    "/F"  # Force creation, overwrite if exists
])
```

**Generated Command Example (Daily):**
```
schtasks /Create /TN "NextcloudBackup" /TR "C:\app.exe --scheduled --backup-dir \"C:\Backups\" --no-encrypt" /SC DAILY /ST 02:00 /F
```

## Detailed Comparison

### Removed Flags

| Flag | Purpose | Reason for Removal |
|------|---------|-------------------|
| `/RL HIGHEST` | Run with highest privileges | Reverted to restore previous working behavior |
| `/Z` | Run missed tasks ASAP | Reverted to restore previous working behavior |

### Retained Flags

| Flag | Value | Purpose | Required |
|------|-------|---------|----------|
| `/Create` | - | Create a new scheduled task | ✓ Yes |
| `/TN` | Task name | Specify the name of the task | ✓ Yes |
| `/TR` | Command | Specify the command to run | ✓ Yes |
| `/SC` | DAILY/WEEKLY/MONTHLY | Schedule type | ✓ Yes |
| `/D` | Day value | Day of week/month (conditional) | Conditional |
| `/ST` | HH:MM | Start time | ✓ Yes |
| `/F` | - | Force creation (overwrite) | ✓ Yes |

## Command Examples

### Daily Backup

**Before:**
```
schtasks /Create /TN "NextcloudBackup" /TR "C:\backup.exe --scheduled --backup-dir \"C:\Backups\" --no-encrypt" /SC DAILY /ST 02:00 /RL HIGHEST /Z /F
```

**After:**
```
schtasks /Create /TN "NextcloudBackup" /TR "C:\backup.exe --scheduled --backup-dir \"C:\Backups\" --no-encrypt" /SC DAILY /ST 02:00 /F
```

### Weekly Backup (Monday at 3:00 AM)

**Before:**
```
schtasks /Create /TN "NextcloudBackup" /TR "C:\backup.exe --scheduled --backup-dir \"C:\Backups\" --no-encrypt" /SC WEEKLY /D MON /ST 03:00 /RL HIGHEST /Z /F
```

**After:**
```
schtasks /Create /TN "NextcloudBackup" /TR "C:\backup.exe --scheduled --backup-dir \"C:\Backups\" --no-encrypt" /SC WEEKLY /D MON /ST 03:00 /F
```

### Monthly Backup (1st day at 4:00 AM)

**Before:**
```
schtasks /Create /TN "NextcloudBackup" /TR "C:\backup.exe --scheduled --backup-dir \"C:\Backups\" --no-encrypt" /SC MONTHLY /D 1 /ST 04:00 /RL HIGHEST /Z /F
```

**After:**
```
schtasks /Create /TN "NextcloudBackup" /TR "C:\backup.exe --scheduled --backup-dir \"C:\Backups\" --no-encrypt" /SC MONTHLY /D 1 /ST 04:00 /F
```

## Behavior Changes

### Before (with /RL and /Z)

1. **Task Privileges**: Tasks run with highest available privileges
2. **Missed Tasks**: If computer is off during scheduled time, task runs ASAP when computer turns on
3. **UAC Prompts**: May prompt for elevation when task runs

### After (reverted)

1. **Task Privileges**: Tasks run with standard user privileges (or as configured in Task Scheduler)
2. **Missed Tasks**: If computer is off during scheduled time, task waits for next scheduled time
3. **UAC Prompts**: No elevation prompts (runs with user's normal privileges)

## Path Quoting (Unchanged)

Both before and after, paths with spaces are correctly quoted:

### EXE Path Quoting
```python
if exe_path.lower().endswith('.py'):
    command = f'python "{exe_path}" {" ".join(args)}'
else:
    command = f'"{exe_path}" {" ".join(args)}'
```

**Examples:**
- `"C:\Program Files\Nextcloud\backup.exe"` ✓
- `python "C:\My Documents\script.py"` ✓

### Backup Directory Quoting
```python
backup_dir_quoted = '"' + backup_dir.strip('"') + '"'
```

**Examples:**
- `--backup-dir "C:\My Backups\Nextcloud"` ✓
- `--backup-dir "C:\Users\John\Documents\Backups"` ✓

## Test Updates

### Tests Updated to Verify Reverted Behavior

1. **test_complete_workflow.py**
   - Now checks that `/RL` is NOT present
   - Now checks that `/Z` is NOT present
   - Verifies `/F` flag is present

2. **test_integration_scheduled_enhancements.py**
   - Validates absence of `/RL` and `/Z`
   - Confirms essential flags are present

3. **test_scheduled_backup_enhancements.py**
   - Checks `/RL` is not in function
   - Checks `/Z` is not in function
   - Validates `/F` and `/ST` are present

### All Tests Pass ✓

```
✓ test_schtasks_fix.py
✓ test_scheduled_backup.py
✓ test_scheduled_backup_enhancements.py
✓ test_integration_scheduled_enhancements.py
✓ test_complete_workflow.py
✓ test_scheduled_task_integration.py
```

## Summary

✅ **Completed:**
- Removed `/RL HIGHEST` flag
- Removed `/Z` flag
- Retained all essential flags
- Path quoting works correctly
- All tests updated and passing

✅ **Impact:**
- Scheduled tasks created with essential flags only
- Previous working behavior restored
- No breaking changes to existing functionality
- All scheduled backup features continue to work

✅ **Backward Compatible:**
- Existing scheduled tasks continue to work
- No changes to user interface
- No changes to backup process
