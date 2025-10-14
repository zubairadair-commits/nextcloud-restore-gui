# Test Run Button - Scheduler Integration Quick Reference

## 🚀 What Changed?

The Test Run button now **triggers backups via Windows Task Scheduler** instead of calling the backup function directly. This validates the actual scheduled backup environment.

## 🎯 Key Features

### Before
- ❌ Direct function call (bypassed scheduler)
- ❌ Ran in GUI process
- ❌ Didn't test scheduler integration

### After
- ✅ Creates temporary scheduled task
- ✅ Triggers via `schtasks /Run`
- ✅ Validates scheduler, permissions, and environment
- ✅ Inline visual feedback (✅ ❌ ⏳)
- ✅ No pop-up dialogs

## 📝 User Experience

### Click Test Run Button

**Progress (Blue):**
```
⏳ Running test backup via Task Scheduler... Please wait...
```

**Success (Green):**
```
✅ Test Backup Successful!

Config file backed up: schedule_config.json
Task Scheduler: Verified ✓
Permissions: Verified ✓
Environment: Verified ✓
Test backup deleted (as expected)

Your scheduled backup is configured correctly.
```

**Failure (Red):**
```
❌ Test backup failed: [error details]
```

**Timeout (Orange):**
```
⚠️ Test backup timed out. Task may still be running in background.
```

## 🔧 Technical Details

### New Command-Line Argument
```bash
--test-run    Run a test backup (config file only, deleted after)
```

### New Function
```python
run_scheduled_task_now(task_name)
# Triggers scheduled task via: schtasks /Run /TN <task_name>
```

### How It Works
```
1. Create temporary task: NextcloudBackup_TestRun
2. Task command: python script.py --test-run --backup-dir "..." 
3. Trigger via scheduler: schtasks /Run /TN NextcloudBackup_TestRun
4. Wait for completion (max 60 seconds)
5. Verify test backup deleted
6. Delete temporary task
7. Show inline result
```

## ✅ What Gets Validated

- **Task Scheduler Integration**: Can create and run scheduled tasks
- **Permissions**: Can read config, write backups, delete files
- **Environment**: Python/exe works, paths correct, dependencies available
- **Configuration**: Backup dir valid, encryption works, passwords correct

## 🧪 Testing

### Run Tests
```bash
# New integration test
python test_scheduler_integration.py

# Updated button test
python test_test_run_button.py

# Config backup test
python test_config_backup_and_dark_mode.py
```

### Manual Test (Windows)
```bash
# Via command line
python nextcloud_restore_and_backup-v9.py --test-run --backup-dir "C:\backups" --encrypt --password "test"

# Via GUI
1. Configure a backup schedule
2. Click "Test Run" button
3. Watch inline feedback
```

## 📂 Files Changed

1. `nextcloud_restore_and_backup-v9.py`
   - Added `--test-run` argument
   - Added `run_scheduled_task_now()` function
   - Rewrote `_run_test_backup_scheduled()` method

2. `test_test_run_button.py`
   - Updated to validate scheduler integration

3. `test_scheduler_integration.py` (NEW)
   - Comprehensive integration tests

## 🐛 Troubleshooting

### "Failed to create test task: Access denied"
**Solution:** Run as administrator or check Task Scheduler permissions

### "Test backup timed out"
**Solution:** Check Task Scheduler history, verify backup directory is accessible

### "Test backup ran but cleanup failed"
**Solution:** Manually delete `test_config_backup_*.tar.gz` files from backup directory

## 📊 Logs

All operations logged to: `Documents/NextcloudLogs/nextcloud_restore_gui.log`

Look for:
```
INFO: Triggering scheduled task 'NextcloudBackup_TestRun'...
INFO: TEST RUN: Starting test backup of config file
INFO: TEST RUN: Config backup created successfully
INFO: TEST RUN: Config backup deleted after successful test
INFO: Test task completed
```

## 🎯 Success Indicators

When test succeeds, you'll see:
- ✅ Green checkmark
- "Task Scheduler: Verified ✓"
- "Permissions: Verified ✓"
- "Environment: Verified ✓"
- "Test backup deleted (as expected)"

This means your **scheduled backups will work correctly**!

## 🔗 Related Docs

- `IMPLEMENTATION_SUMMARY_SCHEDULER_INTEGRATION.md` - Full technical details
- `TEST_RUN_BUTTON_IMPLEMENTATION_CHECKLIST.md` - Original implementation
- `INLINE_NOTIFICATIONS_IMPLEMENTATION.md` - Inline feedback system

---

**Implementation Date:** October 14, 2024  
**Status:** ✅ Complete and Tested
