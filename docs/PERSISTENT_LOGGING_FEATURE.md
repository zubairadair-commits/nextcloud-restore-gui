# Persistent Logging with Log Rotation Feature

## Overview

The Nextcloud Restore & Backup Utility now includes persistent logging with automatic log rotation and a built-in log viewer. This feature helps users troubleshoot issues, track backup history, and monitor application activity.

## Key Features

✅ **Persistent Log Storage**
- Logs stored in `Documents/NextcloudLogs/nextcloud_restore_gui.log`
- Survives PC restarts and application updates
- User-writable location (no admin/system permissions required)

✅ **Automatic Log Rotation**
- Maximum log file size: 10 MB
- Keeps 5 backup files (`.log.1`, `.log.2`, etc.)
- Prevents unlimited disk space usage
- Uses Python's `RotatingFileHandler`

✅ **Built-in Log Viewer**
- Access via dropdown menu: Click ☰ → "📋 View Logs"
- Features:
  - View all log entries in scrollable window
  - Refresh logs in real-time
  - Open log folder in file explorer
  - Clear logs (with confirmation)
  - Theme-aware (supports light/dark modes)

✅ **Cross-Platform Support**
- Windows: `C:\Users\<username>\Documents\NextcloudLogs\`
- macOS: `/Users/<username>/Documents/NextcloudLogs/`
- Linux: `/home/<username>/Documents/NextcloudLogs/`

✅ **Works for All Execution Methods**
- Running as `.py` script
- Running as `.exe` (compiled executable)
- Scheduled backup mode

## Log File Location

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

## What Gets Logged

The application logs comprehensive information about:

### Application Events
- Application startup and shutdown
- Page navigation and UI rendering
- Theme changes
- Button clicks and user interactions

### Backup Operations
- Backup creation start/completion
- Backup file paths and sizes
- Encryption/decryption operations
- Backup verification results

### Restore Operations
- Restore process initiation
- Database restoration steps
- File copying operations
- Docker container interactions
- Permission settings

### Scheduled Backups
- Scheduled task creation
- Automated backup execution
- Cloud synchronization (if configured)

### Errors and Warnings
- Error messages with stack traces
- Warning conditions
- Failed operations with context
- Recovery attempts

### Configuration Changes
- Database configuration updates
- Docker Compose detection
- Domain management changes
- Tailscale setup steps

## Using the Log Viewer

### Opening the Log Viewer

1. Launch the Nextcloud Restore & Backup Utility
2. Click the menu button (☰) in the top-right corner
3. Select "📋 View Logs"

### Log Viewer Interface

```
┌─────────────────────────────────────────────────────────────┐
│ Application Logs                                            │
│ Log file: C:\Users\...\Documents\NextcloudLogs\...log     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  2025-10-14 14:20:04 - INFO - Application started         │
│  2025-10-14 14:20:05 - INFO - Loading backup history...   │
│  2025-10-14 14:20:10 - INFO - User clicked Restore        │
│  2025-10-14 14:20:15 - INFO - Decrypting backup...        │
│  ...                                                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [🔄 Refresh] [📁 Open Log Folder] [🗑️ Clear Logs] [Close]│
└─────────────────────────────────────────────────────────────┘
```

### Button Functions

- **🔄 Refresh**: Reload log contents to see latest entries
- **📁 Open Log Folder**: Open the `NextcloudLogs` folder in your file explorer
- **🗑️ Clear Logs**: Delete all log entries (requires confirmation)
- **Close**: Close the log viewer window

## Log Rotation Behavior

### How It Works

1. Application writes logs to `nextcloud_restore_gui.log`
2. When log file reaches 10 MB, it's automatically renamed to `nextcloud_restore_gui.log.1`
3. A new empty `nextcloud_restore_gui.log` is created
4. This process continues, creating `.log.2`, `.log.3`, `.log.4`, `.log.5`
5. When `.log.5` exists and a new rotation occurs, the oldest backup (`.log.5`) is deleted

### Example

```
nextcloud_restore_gui.log      ← Current log file
nextcloud_restore_gui.log.1    ← Previous log (oldest entries)
nextcloud_restore_gui.log.2    ← 2nd oldest
nextcloud_restore_gui.log.3    ← 3rd oldest
nextcloud_restore_gui.log.4    ← 4th oldest
nextcloud_restore_gui.log.5    ← 5th oldest (deleted on next rotation)
```

### Total Storage

- Maximum total log storage: ~60 MB (10 MB × 6 files)
- Automatic cleanup prevents unlimited growth
- Old logs never lost until rotation limit reached

## Log Format

Each log entry includes:

```
YYYY-MM-DD HH:MM:SS,mmm - LEVEL - Message
```

Example:
```
2025-10-14 14:20:04,878 - INFO - Application started
2025-10-14 14:20:05,123 - WARNING - Backup file size exceeds 1 GB
2025-10-14 14:20:10,456 - ERROR - Failed to connect to database: Connection timeout
```

### Log Levels

- **INFO**: Normal operations, successful actions
- **WARNING**: Potential issues that don't prevent operation
- **ERROR**: Failed operations, exceptions with stack traces

## Privacy and Security

✅ **Safe to Share**
- No passwords or sensitive credentials logged
- No personal data or file contents logged
- No network credentials or API keys logged

✅ **Local Storage Only**
- Logs never sent to external servers
- Stored locally on your machine
- You have full control over log files

⚠️ **What is Logged**
- File paths (may reveal username and directory structure)
- Application events and operations
- Error messages and stack traces
- Configuration settings (non-sensitive only)

## Troubleshooting

### Log File Not Found

If logs don't appear:

1. Check that the `Documents` folder exists
2. Verify you have write permissions to `Documents/NextcloudLogs/`
3. Run the application as your regular user (not as admin/root)
4. Check console output for "Logging initialized" message

### Cannot Open Log Folder

If "Open Log Folder" doesn't work:

- **Windows**: Manually navigate to `%USERPROFILE%\Documents\NextcloudLogs\`
- **macOS**: Use Finder → Go → Home → Documents → NextcloudLogs
- **Linux**: Use file manager to navigate to `~/Documents/NextcloudLogs/`

### Logs Growing Too Large

If you need more or less storage:

- Default: 10 MB per file, 5 backups (60 MB total)
- To adjust: Modify `maxBytes` and `backupCount` in `setup_logging()` function
- Clear old logs: Use "🗑️ Clear Logs" button in log viewer

## Implementation Details

### Code Location

The logging setup is in `nextcloud_restore_and_backup-v9.py`:

```python
# Lines 17-68: Logging configuration
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Setup logging with rotation to a user-writable location."""
    # Determine user's Documents directory
    documents_dir = Path.home() / 'Documents'
    
    # Create log directory
    log_dir = documents_dir / 'NextcloudLogs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure rotating file handler
    file_handler = RotatingFileHandler(
        log_dir / 'nextcloud_restore_gui.log',
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    # ... (rest of setup)

LOG_FILE_PATH = setup_logging()
logger = logging.getLogger(__name__)
```

### Log Viewer Location

The log viewer is accessible from the dropdown menu:

```python
# Lines 2635-2662: "View Logs" button in dropdown menu
logs_btn = tk.Button(
    menu_frame,
    text="📋 View Logs",
    command=lambda: [menu_window.destroy(), self.show_log_viewer()],
    # ...
)

# Lines 2680-2836: Log viewer implementation
def show_log_viewer(self):
    """Show log viewer window with current log contents"""
    # Creates window with:
    # - Scrollable text display
    # - Refresh button
    # - Open folder button
    # - Clear logs button
    # - Theme support
```

## Testing

### Automated Tests

Run the test suite to verify logging implementation:

```bash
python3 test_persistent_logging.py
```

Expected output:
```
======================================================================
Results: 7/7 tests passed
======================================================================
✅ All tests passed! Persistent logging is properly implemented.
```

### Manual Testing

1. **Test Log Creation**:
   ```bash
   python3 demo_persistent_logging.py
   ```
   Verifies log file is created and contains test entries.

2. **Test Log Viewer**:
   - Launch application
   - Click ☰ → "📋 View Logs"
   - Verify logs are displayed
   - Click "🔄 Refresh" to update
   - Click "📁 Open Log Folder" to view location

3. **Test Log Rotation**:
   - Create a large log file (>10 MB)
   - Verify `.log.1` backup is created
   - Verify oldest backups are deleted after 5 rotations

## Benefits

### For Users
- ✅ Easy troubleshooting with visible error history
- ✅ Track backup and restore operations
- ✅ No need to run commands or search for log files
- ✅ Logs persist after PC restart
- ✅ Automatic cleanup prevents disk space issues

### For Developers
- ✅ Comprehensive debugging information
- ✅ User can share logs for support
- ✅ Stack traces included for errors
- ✅ All operations logged with timestamps
- ✅ Easy to add new logging statements

### For Support
- ✅ Users can easily export logs
- ✅ Clear timestamps for issue correlation
- ✅ Complete operation history
- ✅ Error context with stack traces
- ✅ Cross-platform consistency

## Future Enhancements

Possible improvements for future versions:

1. **Export Logs**: Add button to export logs to a ZIP file
2. **Filter Logs**: Add dropdown to filter by log level (INFO/WARNING/ERROR)
3. **Search**: Add search box to find specific log entries
4. **Date Range**: Add date picker to view logs from specific time periods
5. **Auto-Refresh**: Option to auto-refresh logs every N seconds
6. **Remote Logging**: Optional cloud logging for remote diagnostics (opt-in)
7. **Log Viewer Themes**: Additional color schemes for log display
8. **Performance Metrics**: Log and display operation timing statistics

## Compatibility

- ✅ **Backward Compatible**: No breaking changes to existing functionality
- ✅ **Python Version**: Requires Python 3.6+ (same as before)
- ✅ **Dependencies**: Only uses standard library (logging.handlers)
- ✅ **Existing Logs**: Old logs in application directory still accessible
- ✅ **All Platforms**: Tested on Windows, macOS, and Linux

## Migration from Old Logging

### Old Behavior
- Log file: `nextcloud_restore_gui.log` (in application directory)
- No rotation (file grows indefinitely)
- No built-in viewer

### New Behavior
- Log file: `Documents/NextcloudLogs/nextcloud_restore_gui.log`
- Automatic rotation (10 MB max, 5 backups)
- Built-in log viewer with GUI

### Migration Steps

Old logs are not automatically migrated. To preserve old logs:

1. Locate old log file: `nextcloud_restore_gui.log` (in app directory)
2. Copy to new location: `Documents/NextcloudLogs/`
3. Old logs will appear in log viewer
4. Delete old log file from app directory (optional)

## Summary

The persistent logging feature provides:

- 📋 **Comprehensive Logging**: All operations logged with timestamps
- 🔄 **Automatic Rotation**: Prevents unlimited log growth
- 🖥️ **Built-in Viewer**: Easy access to logs from GUI
- 💾 **Persistent Storage**: Logs survive restarts and updates
- 🌍 **Cross-Platform**: Works on Windows, macOS, and Linux
- 🎨 **Theme Support**: Matches application theme (light/dark)
- 🔒 **Privacy-Safe**: No sensitive data logged

Users can now easily troubleshoot issues, track backup history, and monitor application activity without any command-line knowledge.

---

**Implementation Date**: October 14, 2025  
**Status**: ✅ Complete  
**Tests**: 7/7 passing  
**Documentation**: Complete
