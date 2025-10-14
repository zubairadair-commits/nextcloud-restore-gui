# Quick Fix: Scheduled Backup Errors

## Problem
Getting "RuntimeError: main thread is not in main loop" when running scheduled backups?

## Solution
✅ **FIXED** in this version!

## What Changed
- Scheduled backups no longer initialize the GUI
- No more Tkinter errors in Task Scheduler
- Console-only output in scheduled mode

## Testing Your Fix

### 1. Test Command Line
```cmd
python nextcloud_restore_and_backup-v9.py ^
  --scheduled ^
  --backup-dir "C:\Test\Backup" ^
  --no-encrypt
```

### 2. Expected Output
```
Starting scheduled backup to C:\Test\Backup
Step 1/10: Preparing backup...
Step 2/10: Checking and copying 'config'...
...
Scheduled backup completed successfully
```

### 3. What You Should NOT See
- ❌ RuntimeError: main thread is not in main loop
- ❌ _tkinter.TclError
- ❌ Any GUI windows or dialogs

## For Windows Task Scheduler

Your existing scheduled tasks will work automatically!

### If You Created Tasks Before This Fix
No action needed. The same command will now work without errors.

### If Creating New Tasks
Use the app's "Schedule Backup" button for automatic setup.

## Troubleshooting

### "ERROR: Docker is not running"
✅ This is normal - just start Docker before the scheduled time

### "ERROR: No running Nextcloud container found"
✅ This is normal - start your Nextcloud container

### Any other RuntimeError or GUI errors
❌ Please report - should not happen with this fix!

## Command-Line Arguments

```
--scheduled              Run in scheduled mode (required)
--backup-dir <path>      Where to save backups (required)
--encrypt                Enable encryption (optional)
--no-encrypt             Disable encryption (optional)
--password <pass>        Encryption password (optional)
```

## Example Commands

### Basic Backup
```cmd
python app.py --scheduled --backup-dir "C:\Backups"
```

### With Encryption
```cmd
python app.py --scheduled --backup-dir "C:\Backups" ^
  --encrypt --password "MySecretPass123"
```

### Without Encryption (Explicit)
```cmd
python app.py --scheduled --backup-dir "C:\Backups" --no-encrypt
```

## Logs

Task Scheduler logs are in:
- **Windows**: Task Scheduler → Task History
- **App logs**: `nextcloud_restore_gui.log` in app directory

## More Information

See `SCHEDULED_BACKUP_GUI_FIX.md` for technical details.

---

✅ **Status**: Fixed  
🗓️ **Date**: October 2025  
🐛 **Issue**: RuntimeError in scheduled mode  
✨ **Solution**: Conditional GUI initialization
