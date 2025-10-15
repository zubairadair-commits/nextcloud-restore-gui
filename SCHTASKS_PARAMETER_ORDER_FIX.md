# Fix: Windows Task Scheduler Parameter Order

## Problem Statement

The `create_scheduled_task` function was building the schtasks command with incorrect parameter order. According to Windows Task Scheduler (`schtasks.exe`) requirements, the `/SC` (schedule type) parameter must come **BEFORE** the `/ST` (start time) parameter.

## Issue

### Before Fix ❌

```python
schtasks_cmd = [
    "schtasks", "/Create",
    "/TN", task_name,
    "/TR", command,
    "/ST", schedule_time,      # ❌ /ST came first
    "/RL", "HIGHEST",
    "/Z"
]
schtasks_cmd.extend(schedule_args)  # ❌ /SC added after /ST
schtasks_cmd.append("/F")
```

**Resulting command (Daily schedule):**
```
schtasks /Create /TN TaskName /TR "command" /ST 02:00 /RL HIGHEST /Z /SC DAILY /F
                                             ^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^
                                             /ST comes before /SC - WRONG ORDER!
```

### Why This Was Wrong

Windows Task Scheduler (`schtasks.exe`) requires parameters in a specific order:
1. `/TN` (Task Name)
2. `/TR` (Task Run command)
3. **`/SC` (Schedule type) - MUST COME FIRST**
4. `/D` (Day - if applicable)
5. **`/ST` (Start time) - MUST COME AFTER /SC**
6. `/RL` (Run Level)
7. `/Z` (Run after missed)
8. `/F` (Force)

When `/ST` comes before `/SC`, Windows Task Scheduler may:
- Reject the command with an error
- Create the task but fail to execute it properly
- Ignore the schedule parameters

## Solution

### After Fix ✅

```python
# Note: /SC (schedule type) must come BEFORE /ST (start time) per schtasks requirements
schtasks_cmd = [
    "schtasks", "/Create",
    "/TN", task_name,
    "/TR", command
]
schtasks_cmd.extend(schedule_args)  # ✅ Add /SC and /D first
schtasks_cmd.extend([
    "/ST", schedule_time,      # ✅ /ST now comes after /SC
    "/RL", "HIGHEST",
    "/Z",
    "/F"
])
```

**Resulting command (Daily schedule):**
```
schtasks /Create /TN TaskName /TR "command" /SC DAILY /ST 02:00 /RL HIGHEST /Z /F
                                             ^^^^^^^^^ ^^^^^^^^
                                             /SC comes before /ST - CORRECT ORDER!
```

## Code Changes

### File: `nextcloud_restore_and_backup-v9.py`

**Function:** `create_scheduled_task()` (lines 2263-2276)

**Changes:**
1. Split the `schtasks_cmd` list construction into multiple parts
2. Add `schedule_args` (containing `/SC` and optional `/D`) after `/TR`
3. Add `/ST` and remaining parameters after `schedule_args`
4. Added clarifying comment about parameter order requirement

## Testing

### New Test: `test_schtasks_parameter_order.py`

Created comprehensive test that verifies:

1. **Parameter order in `create_scheduled_task`:**
   - ✅ `/ST` is not in the base command (before schedule_args)
   - ✅ `schedule_args` is extended to the command
   - ✅ `/ST` is added after `schedule_args`
   - ✅ All three schedule types (DAILY, WEEKLY, MONTHLY) are defined

2. **Parameter order in `_run_test_backup_scheduled`:**
   - ✅ `/SC` comes before `/ST` in the test task creation
   - ✅ (This function already had correct order, no fix needed)

### Test Results

```bash
$ python test_schtasks_parameter_order.py

Testing Windows Task Scheduler Parameter Order
======================================================================
Requirement: /SC (schedule type) must come BEFORE /ST (start time)
======================================================================

Testing schtasks Parameter Order in create_scheduled_task
   ✓ /ST is not in base command (good)
   ✓ schedule_args is extended to command
   ✓ /ST is added after schedule_args
   ✓ Found schedule types: DAILY, WEEKLY, MONTHLY
   ✓ Parameter order is CORRECT

Testing schtasks Parameter Order in _run_test_backup_scheduled
   ✓ /SC comes before /ST
   ✓ Parameter order is CORRECT

🎉 All tests PASSED! Parameter order is correct.
```

### Existing Tests Still Pass

All existing scheduled backup tests continue to pass:
- ✅ `test_scheduled_backup.py`
- ✅ `test_schtasks_fix.py`
- ✅ `test_scheduled_task_integration.py`

## Examples

### Daily Backup

**Command generated (After Fix):**
```bash
schtasks /Create /TN "NextcloudBackup" /TR "python \"C:\app.py\" --scheduled --backup-dir \"C:\Backups\" --no-encrypt" /SC DAILY /ST 02:00 /RL HIGHEST /Z /F
```

**Parameter order:**
1. `/TN` "NextcloudBackup"
2. `/TR` "python \"C:\app.py\" ..."
3. `/SC` DAILY ✅
4. `/ST` 02:00 ✅ (after /SC)
5. `/RL` HIGHEST
6. `/Z`
7. `/F`

### Weekly Backup

**Command generated (After Fix):**
```bash
schtasks /Create /TN "NextcloudBackup" /TR "C:\app.exe --scheduled --backup-dir \"C:\Backups\" --encrypt" /SC WEEKLY /D MON /ST 03:00 /RL HIGHEST /Z /F
```

**Parameter order:**
1. `/TN` "NextcloudBackup"
2. `/TR` "C:\app.exe ..."
3. `/SC` WEEKLY ✅
4. `/D` MON ✅
5. `/ST` 03:00 ✅ (after /SC and /D)
6. `/RL` HIGHEST
7. `/Z`
8. `/F`

### Monthly Backup

**Command generated (After Fix):**
```bash
schtasks /Create /TN "NextcloudBackup" /TR "\"C:\app.exe\" --scheduled --backup-dir \"C:\Backups\" --no-encrypt" /SC MONTHLY /D 1 /ST 04:00 /RL HIGHEST /Z /F
```

**Parameter order:**
1. `/TN` "NextcloudBackup"
2. `/TR` "\"C:\app.exe\" ..."
3. `/SC` MONTHLY ✅
4. `/D` 1 ✅
5. `/ST` 04:00 ✅ (after /SC and /D)
6. `/RL` HIGHEST
7. `/Z`
8. `/F`

## Impact

### Benefits
- ✅ Scheduled tasks will be created correctly in Windows Task Scheduler
- ✅ Tasks will execute on the specified schedule
- ✅ No more parameter order errors
- ✅ Complies with schtasks.exe requirements

### Backward Compatibility
- ✅ Existing scheduled tasks continue to work
- ✅ No breaking changes to the API
- ✅ All existing tests pass
- ✅ No changes to user interface

### What Was NOT Changed
- `_run_test_backup_scheduled()` - Already had correct order
- Schedule configuration format
- Task execution logic
- User interface elements
- Command-line arguments

## Related Documentation

- **Microsoft schtasks documentation:** [https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create)
- **Scheduled Backup Guide:** `SCHEDULED_BACKUP_FEATURE.md`
- **Backup Directory Quoting Fix:** `BEFORE_AFTER_BACKUP_DIR_QUOTING.md`

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Parameter order | ❌ Incorrect (/ST before /SC) | ✅ Correct (/SC before /ST) |
| Task creation | ⚠️ May fail or malfunction | ✅ Works reliably |
| Compliance | ❌ Violates schtasks requirements | ✅ Follows schtasks specification |
| Test coverage | ⚠️ No specific test | ✅ Dedicated test added |

**Lines changed:** 13 lines in `create_scheduled_task()` function  
**Tests added:** 1 new test file (`test_schtasks_parameter_order.py`)  
**Breaking changes:** None  
**Status:** ✅ **Fixed and Verified**

---

*Fix implemented: October 2025*  
*Issue: Incorrect schtasks parameter order*  
*Solution: Reorder command construction to place /SC before /ST*
