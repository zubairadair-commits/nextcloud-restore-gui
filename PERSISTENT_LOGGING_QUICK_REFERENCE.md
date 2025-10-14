# Persistent Logging - Quick Reference Guide

## 🚀 Quick Start

### How to View Logs

1. Launch Nextcloud Restore & Backup Utility
2. Click the **☰** menu button (top-right corner)
3. Select **📋 View Logs**

That's it! The log viewer will open showing all application activity.

## 📍 Log File Location

### Windows
```
C:\Users\<YourUsername>\Documents\NextcloudLogs\nextcloud_restore_gui.log
```

### macOS
```
/Users/<YourUsername>/Documents/NextcloudLogs/nextcloud_restore_gui.log
```

### Linux
```
/home/<YourUsername>/Documents/NextcloudLogs/nextcloud_restore_gui.log
```

## 🔄 Log Rotation

- **Maximum file size**: 10 MB
- **Backup files kept**: 5
- **Total storage**: ~60 MB maximum
- **Automatic cleanup**: Yes

### Rotation Example
```
nextcloud_restore_gui.log      ← Current log (active)
nextcloud_restore_gui.log.1    ← 1st backup
nextcloud_restore_gui.log.2    ← 2nd backup
nextcloud_restore_gui.log.3    ← 3rd backup
nextcloud_restore_gui.log.4    ← 4th backup
nextcloud_restore_gui.log.5    ← 5th backup (oldest)
```

When the current log reaches 10 MB:
1. `.log.5` is deleted
2. `.log.4` → `.log.5`
3. `.log.3` → `.log.4`
4. `.log.2` → `.log.3`
5. `.log.1` → `.log.2`
6. Current → `.log.1`
7. New empty log file created

## 🎛️ Log Viewer Controls

### 🔄 Refresh
- Reloads log file to show latest entries
- Use when monitoring active operations

### 📁 Open Log Folder
- Opens `NextcloudLogs` folder in file explorer
- Access backup logs or copy files

### 🗑️ Clear Logs
- Deletes all log entries (requires confirmation)
- **Cannot be undone** - use with caution

### Close
- Closes the log viewer window

## 📋 What Gets Logged

### ✅ Always Logged
- Application startup/shutdown
- Backup creation and completion
- Restore operations and results
- Configuration changes
- Docker container interactions
- Database operations
- File operations
- Errors with stack traces

### ❌ Never Logged
- Passwords or credentials
- Personal data or file contents
- Network credentials or API keys
- Sensitive configuration values

## 🔍 Reading Log Entries

### Log Format
```
YYYY-MM-DD HH:MM:SS,mmm - LEVEL - Message
```

### Example Entry
```
2025-10-14 14:20:04,878 - INFO - Backup created successfully
```

### Log Levels
- **INFO**: Normal operations (green ✓)
- **WARNING**: Potential issues (yellow ⚠️)
- **ERROR**: Failed operations (red ✗)

## 🛠️ Troubleshooting

### Problem: Can't find log file

**Solution**:
1. Check your Documents folder exists
2. Run the application once to create logs
3. Look for `NextcloudLogs` subfolder in Documents
4. Check console output for "Logging initialized" message

### Problem: Log viewer is empty

**Solution**:
1. Click "🔄 Refresh" button
2. Check log file exists at location shown
3. Run application to generate some log entries
4. Verify file permissions (should be user-readable)

### Problem: Logs growing too large

**Solution**:
- Rotation is automatic - no action needed
- Maximum storage is ~60 MB
- Clear old logs: Use "🗑️ Clear Logs" button
- Backup logs saved as `.log.1`, `.log.2`, etc.

### Problem: Can't open log folder

**Solution**:
- **Windows**: Navigate to `%USERPROFILE%\Documents\NextcloudLogs\`
- **macOS**: Finder → Go → Home → Documents → NextcloudLogs
- **Linux**: File manager → Home → Documents → NextcloudLogs

## 📊 Common Log Patterns

### Successful Backup
```
INFO - Starting backup creation
INFO - Encrypting backup files
INFO - Backup saved: /path/to/backup.tar.gpg
INFO - Backup completed successfully
```

### Failed Restore
```
INFO - Starting restore process
ERROR - Failed to decrypt backup: Invalid password
ERROR - Restore operation failed
```

### Database Detection
```
INFO - Detecting database configuration
INFO - Found database type: postgresql
INFO - Database auto-detection successful
```

### Theme Change
```
INFO - Theme changed from light to dark
INFO - Applying theme to UI elements
INFO - Theme applied successfully
```

## 🧪 Testing

### Run Tests
```bash
# Test persistent logging implementation
python3 test_persistent_logging.py

# Test log rotation functionality
python3 test_log_rotation.py

# Demo logging in action
python3 demo_persistent_logging.py
```

### Expected Results
- All tests should pass
- Log file created in Documents/NextcloudLogs/
- Rotation verified with multiple backup files

## 🔐 Privacy & Security

### Safe to Share
✅ Log files contain no passwords  
✅ No personal data or file contents  
✅ No network credentials  
✅ Error messages only (not sensitive data)

### What's Included
⚠️ File paths (may show username)  
⚠️ Configuration settings (non-sensitive)  
⚠️ Error messages and stack traces  
⚠️ Timestamps of operations

### Best Practices
- Review logs before sharing publicly
- Redact file paths if needed
- Remove identifying information if necessary
- Keep logs secure on your machine

## 💡 Tips & Tricks

### Monitor Live Activity
1. Open log viewer
2. Perform an action (backup, restore, etc.)
3. Click "🔄 Refresh" to see new entries

### Find Specific Entries
1. Open log viewer
2. Use Ctrl+F (Cmd+F on macOS) to search
3. Enter search term (e.g., "ERROR", "backup", date)

### Export Logs for Support
1. Click "📁 Open Log Folder"
2. Copy `nextcloud_restore_gui.log`
3. Share via email or support ticket

### Clean Up Old Logs
1. Open log viewer
2. Review contents
3. Click "🗑️ Clear Logs"
4. Confirm deletion

### Check Disk Space
- Log folder: ~60 MB maximum
- Individual log: 10 MB maximum
- Auto cleanup: Every rotation

## 📚 Additional Resources

### Documentation
- **Full Guide**: See `PERSISTENT_LOGGING_FEATURE.md`
- **Tests**: See `test_persistent_logging.py`
- **Demo**: Run `demo_persistent_logging.py`

### Key Files
- Main app: `nextcloud_restore_and_backup-v9.py`
- Log setup: Lines 17-68 (setup_logging function)
- Log viewer: Lines 2680-2836 (show_log_viewer method)

## ✅ Feature Checklist

- [x] Persistent log storage
- [x] Automatic log rotation
- [x] Built-in log viewer
- [x] Cross-platform support
- [x] Theme integration
- [x] Refresh functionality
- [x] Open folder functionality
- [x] Clear logs functionality
- [x] UTF-8 encoding support
- [x] Privacy-safe logging

## 🎯 Summary

**Persistent logging provides:**
- 📋 Complete operation history
- 🔄 Automatic size management
- 🖥️ Easy GUI access
- 💾 Survives PC restarts
- 🌍 Works everywhere
- 🎨 Theme-aware interface
- 🔒 Privacy-safe

**Access logs in 3 clicks:**
1. Click ☰
2. Click 📋 View Logs
3. See everything

---

**Questions?** Check `PERSISTENT_LOGGING_FEATURE.md` for detailed documentation.
