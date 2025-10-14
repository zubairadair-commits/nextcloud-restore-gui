# Usage Example: Scheduled Backup After Fix

## Before the Fix ❌

### What Happened
```
Windows Task Scheduler runs at 2:00 AM:
  python app.py --scheduled --backup-dir "C:\Backups"
    ↓
  App creates full GUI (hidden)
    ↓
  GUI methods called: self.after(), self.show_landing()
    ↓
  RuntimeError: main thread is not in main loop
    ↓
  BACKUP FAILED ❌
```

### User Experience
- Scheduled backup appears to run
- No error dialog (running in background)
- User thinks backups are working
- **Discovers weeks later no backups were created** 💥

## After the Fix ✅

### What Happens Now
```
Windows Task Scheduler runs at 2:00 AM:
  python app.py --scheduled --backup-dir "C:\Backups"
    ↓
  App skips GUI initialization (scheduled_mode=True)
    ↓
  Runs backup with console output
    ↓
  Backup completes successfully
    ↓
  BACKUP CREATED ✅
```

### User Experience
- Scheduled backup runs silently
- Backup file created in specified directory
- Task Scheduler shows success
- **User has reliable backups** 🎉

## Real-World Command Examples

### Example 1: Daily Backup Without Encryption
```cmd
python "C:\Apps\nextcloud_restore_and_backup-v9.py" ^
  --scheduled ^
  --backup-dir "C:\Backups\Nextcloud" ^
  --no-encrypt
```

**Output** (to console/log):
```
Starting scheduled backup to C:\Backups\Nextcloud
Step 1/10: Preparing backup...
Step 2/10: Checking and copying 'config'...
  ✓ Copied 'config'
Step 3/10: Checking and copying 'data'...
  ✓ Copied 'data'
Step 4/10: Checking and copying 'apps'...
  ✓ Copied 'apps'
Step 5/10: Checking and copying 'custom_apps'...
  - Skipping 'custom_apps' (not found; not critical)
Step 6/10: Dumping PGSQL database...
Step 7/10: Creating archive...
Step 8/10: Encrypting archive...
Step 9/10: Cleaning up temp files...
Step 10/10: Backup complete!
Backup saved to: C:\Backups\Nextcloud\nextcloud-backup-20251014_020001.tar.gz
Scheduled backup completed successfully
```

**Result**: 
- File created: `nextcloud-backup-20251014_020001.tar.gz`
- Size: ~500 MB (typical)
- Exit code: 0

### Example 2: Weekly Backup With Encryption
```cmd
python "C:\Apps\nextcloud_restore_and_backup-v9.py" ^
  --scheduled ^
  --backup-dir "D:\OneDrive\Nextcloud-Backups" ^
  --encrypt ^
  --password "MySecurePassword123!"
```

**Output**:
```
Starting scheduled backup to D:\OneDrive\Nextcloud-Backups
Step 1/10: Preparing backup...
Step 2/10: Checking and copying 'config'...
  ✓ Copied 'config'
Step 3/10: Checking and copying 'data'...
  ✓ Copied 'data'
Step 4/10: Checking and copying 'apps'...
  ✓ Copied 'apps'
Step 5/10: Checking and copying 'custom_apps'...
  ✓ Copied 'custom_apps'
Step 6/10: Dumping PGSQL database...
Step 7/10: Creating archive...
Step 8/10: Encrypting archive...  ← Encryption happening!
Step 9/10: Cleaning up temp files...
Step 10/10: Backup complete!
Backup saved to: D:\OneDrive\Nextcloud-Backups\nextcloud-backup-20251014_020001.tar.gz.gpg
Scheduled backup completed successfully
```

**Result**:
- File created: `nextcloud-backup-20251014_020001.tar.gz.gpg` (encrypted!)
- Size: ~502 MB (slightly larger due to encryption overhead)
- Exit code: 0
- Automatically synced to OneDrive ☁️

### Example 3: Error Handling (Docker Not Running)
```cmd
python app.py --scheduled --backup-dir "C:\Backups"
```

**Output**:
```
ERROR: Docker is not running. Cannot perform backup.
```

**Result**:
- No backup file created
- Exit code: Non-zero
- Task Scheduler logs the error
- User can check Task Scheduler history

### Example 4: Error Handling (No Container)
```cmd
python app.py --scheduled --backup-dir "C:\Backups"
```

**Output** (if Docker running but no Nextcloud container):
```
ERROR: No running Nextcloud container found.
```

**Result**:
- No backup file created
- Exit code: Non-zero
- User reminded to start Nextcloud first

## Windows Task Scheduler Setup

### Using the GUI (Recommended)

1. Open the application normally
2. Click "📅 Schedule Backup"
3. Configure:
   - Backup Directory: `C:\Backups\Nextcloud`
   - Frequency: Daily
   - Time: 02:00
   - Encryption: Enabled
   - Password: (your password)
4. Click "Create Schedule"
5. Done! ✅

The app automatically creates the task with correct arguments.

### Manual Task Scheduler Setup (Advanced)

If you prefer to create the task manually:

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Nextcloud Backup"
4. Trigger: Daily at 2:00 AM
5. Action: Start a program
6. Program: `python` (or full path to python.exe)
7. Arguments:
   ```
   "C:\path\to\nextcloud_restore_and_backup-v9.py" --scheduled --backup-dir "C:\Backups" --encrypt --password "yourpass"
   ```
8. Finish

**Note**: The GUI method is easier and less error-prone!

## Verifying It Works

### Method 1: Check Task History
1. Open Task Scheduler
2. Find "NextcloudBackup" task
3. Click "History" tab
4. Look for recent runs with "Task completed" status

### Method 2: Check Backup Files
1. Navigate to your backup directory
2. Look for files like: `nextcloud-backup-YYYYMMDD_HHMMSS.tar.gz`
3. Check file timestamps match scheduled times
4. Verify file sizes are reasonable (not 0 bytes)

### Method 3: Manual Test Run
```cmd
# Run the exact command used by Task Scheduler
python "C:\Apps\nextcloud_restore_and_backup-v9.py" ^
  --scheduled ^
  --backup-dir "C:\Test\Backup" ^
  --no-encrypt

# Expected: Console output showing backup progress
# Expected: Backup file created in C:\Test\Backup
# Expected: Exit code 0
```

## Troubleshooting

### "ERROR: --backup-dir is required"
**Solution**: Add `--backup-dir "C:\path"` to command

### "ERROR: Docker is not running"
**Solution**: Start Docker Desktop before scheduled time

### "ERROR: No running Nextcloud container found"
**Solution**: Ensure Nextcloud container is running

### No output / Silent failure
**Old behavior (before fix)**: Would crash with RuntimeError  
**New behavior (after fix)**: Should show error message in Task Scheduler logs

### Task shows "Running" but never completes
**Solution**: This should NOT happen after the fix. If it does:
1. Check if Docker is hanging
2. Check available disk space
3. Review Task Scheduler logs

## What Changed in This Fix

### For End Users
- ✅ Scheduled backups actually work now
- ✅ No more silent failures
- ✅ Existing tasks work without modification

### For System Administrators
- ✅ Reliable automated backups
- ✅ Task Scheduler logs show actual status
- ✅ Can monitor backup success/failure

### For Developers
- ✅ Clean separation of GUI and CLI modes
- ✅ No GUI initialization in scheduled mode
- ✅ Easier to maintain and test

## Conclusion

The fix ensures that scheduled backups work reliably by preventing GUI initialization when running in scheduled/CLI mode. Users can now trust that their automated backups are actually running, protecting their Nextcloud data.

---

**Fixed**: October 2025  
**Issue**: RuntimeError in scheduled mode  
**Result**: Reliable scheduled backups ✅
