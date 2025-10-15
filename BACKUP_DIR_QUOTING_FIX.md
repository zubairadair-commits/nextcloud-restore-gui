# Backup Directory Quoting Fix

## Problem Statement
The backup directory argument (`--backup-dir`) for scheduled tasks was not properly quoted, causing Windows Task Scheduler to split paths with spaces into multiple arguments. This resulted in backup failures or infinite backup loops.

### Example Issue
When user sets backup directory to: `C:/Users/zubai/Desktop/MANUAL BACKUP`

**Before Fix:**
```cmd
"C:\app.exe" --scheduled --backup-dir C:/Users/zubai/Desktop/MANUAL BACKUP --no-encrypt
```
This would be interpreted as:
- `--backup-dir C:/Users/zubai/Desktop/MANUAL`
- Extra argument: `BACKUP`
- Extra argument: `--no-encrypt`

**After Fix:**
```cmd
"C:\app.exe" --scheduled --backup-dir "C:/Users/zubai/Desktop/MANUAL BACKUP" --no-encrypt
```
Now correctly interpreted as single backup directory path.

## Solution
Added proper quoting logic in two functions that construct Task Scheduler commands:

### 1. `create_scheduled_task()` (Line 2221)
```python
# Ensure backup_dir is safely quoted (prevents argument splitting with spaces)
backup_dir_quoted = f'"{backup_dir.strip("\"")}"'

# Build the command arguments for scheduled execution
args = [
    "--scheduled",
    "--backup-dir", backup_dir_quoted,  # ← Changed from backup_dir
    "--encrypt" if encrypt else "--no-encrypt"
]
```

### 2. `_run_test_backup_scheduled()` (Line 6848)
```python
# Ensure backup_dir is safely quoted (prevents argument splitting with spaces)
backup_dir_quoted = f'"{backup_dir.strip("\"")}"'

# Build the command arguments for test run
args = [
    "--test-run",
    "--backup-dir", backup_dir_quoted,  # ← Changed from backup_dir
    "--encrypt" if encrypt else "--no-encrypt"
]
```

## Key Features
- **Safe Quoting**: Uses `backup_dir.strip("\"")` to remove existing quotes first
- **No Double Quoting**: If path already has quotes, they're stripped then re-applied once
- **Consistent**: All backup directories are quoted, even those without spaces
- **Minimal Change**: Only 2 lines added per function, 2 lines modified per function

## Testing
Created comprehensive test suite in `test_backup_dir_quoting.py`:

### Test Cases
1. ✓ Backup directory with spaces (problem statement example)
2. ✓ Backup directory already quoted (no double quoting)
3. ✓ Backup directory without spaces (still quoted for consistency)
4. ✓ Complex paths with multiple spaces

### Updated Existing Tests
Enhanced `test_scheduled_task_integration.py` to verify backup_dir quoting:
- Test 4: Executable with spaces in path
- Test 5: Python script with spaces in path

## Verification

### Example 1: Path with Spaces
```python
backup_dir = 'C:/Users/zubai/Desktop/MANUAL BACKUP'
# Result: --backup-dir "C:/Users/zubai/Desktop/MANUAL BACKUP"
```

### Example 2: Already Quoted Path
```python
backup_dir = '"C:\My Backups\Data"'
# Result: --backup-dir "C:\My Backups\Data"  (not double-quoted)
```

### Example 3: Path Without Spaces
```python
backup_dir = 'C:\Backups\Nextcloud'
# Result: --backup-dir "C:\Backups\Nextcloud"  (still quoted for consistency)
```

## Impact
- **Fixes**: Scheduled backups now work with directories containing spaces
- **Prevents**: Argument splitting errors in Windows Task Scheduler
- **Prevents**: Infinite backup loops caused by incorrect path parsing
- **No Breaking Changes**: Existing backups with paths without spaces continue to work

## Files Modified
1. `nextcloud_restore_and_backup-v9.py` (2 functions, 8 lines total)
   - `create_scheduled_task()` - Lines 2220-2226
   - `_run_test_backup_scheduled()` - Lines 6847-6853

2. `test_scheduled_task_integration.py` (updated test assertions)

3. `test_backup_dir_quoting.py` (new comprehensive test file)

## Backward Compatibility
✓ Fully backward compatible with existing configurations
✓ Paths without spaces continue to work
✓ No changes to backup logic or other functionality
