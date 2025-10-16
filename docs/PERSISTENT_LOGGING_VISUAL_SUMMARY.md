# Persistent Logging - Visual Summary

## Feature Overview

```
┌────────────────────────────────────────────────────────────────┐
│ Nextcloud Restore & Backup Utility                    🌙  ☰   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│                  Welcome to Nextcloud Restore                  │
│                                                                │
│         User clicks menu button ☰ ──────────────────┐         │
│                                                      │         │
│                                                      ▼         │
│                                     ┌─────────────────────┐   │
│                                     │ Advanced Features   │   │
│                                     ├─────────────────────┤   │
│                                     │ 🌐 Remote Access    │   │
│                                     │ 📋 View Logs    ◄───┼─┐ │
│                                     │                     │ │ │
│                                     │      [Close]        │ │ │
│                                     └─────────────────────┘ │ │
│                                                              │ │
└──────────────────────────────────────────────────────────────┼─┘
                                                               │
                    User clicks "View Logs"                   │
                            │                                  │
                            ▼                                  │
┌───────────────────────────────────────────────────────────────┐
│ Application Logs                                              │
│ Log file: C:\Users\...\Documents\NextcloudLogs\...log       │
├───────────────────────────────────────────────────────────────┤
│ 2025-10-14 14:20:04 - INFO - Application started             │
│ 2025-10-14 14:20:05 - INFO - Loading configuration...        │
│ 2025-10-14 14:20:10 - INFO - User started backup process     │
│ 2025-10-14 14:20:15 - INFO - Encrypting backup files...      │
│ 2025-10-14 14:20:45 - INFO - Backup completed successfully   │
│ 2025-10-14 14:21:00 - WARNING - Large file detected (>1GB)   │
│ 2025-10-14 14:22:30 - ERROR - Failed to connect to database  │
│ ...                                                           │
├───────────────────────────────────────────────────────────────┤
│ [🔄 Refresh] [📁 Open Log Folder] [🗑️ Clear Logs] [Close]   │
└───────────────────────────────────────────────────────────────┘
```

## Log File Location Flow

```
Application Starts
       │
       ▼
Detect User's Documents Folder
       │
       ├─ Windows: C:\Users\<username>\Documents\
       ├─ macOS:   /Users/<username>/Documents/
       └─ Linux:   /home/<username>/Documents/
       │
       ▼
Create NextcloudLogs Subfolder (if doesn't exist)
       │
       ▼
Configure RotatingFileHandler
       │
       ├─ File: nextcloud_restore_gui.log
       ├─ Max Size: 10 MB
       ├─ Backups: 5
       └─ Encoding: UTF-8
       │
       ▼
Start Logging All Operations
```

## Log Rotation Visualization

### Before Rotation
```
Documents/NextcloudLogs/
└── nextcloud_restore_gui.log (9.8 MB)
```

### After First Rotation (when log reaches 10 MB)
```
Documents/NextcloudLogs/
├── nextcloud_restore_gui.log     (0 KB - new, empty)
└── nextcloud_restore_gui.log.1   (10 MB - old data)
```

### After Multiple Rotations
```
Documents/NextcloudLogs/
├── nextcloud_restore_gui.log     (5.2 MB - current)
├── nextcloud_restore_gui.log.1   (10 MB - newest backup)
├── nextcloud_restore_gui.log.2   (10 MB)
├── nextcloud_restore_gui.log.3   (10 MB)
├── nextcloud_restore_gui.log.4   (10 MB)
└── nextcloud_restore_gui.log.5   (10 MB - oldest backup)
```

### When Rotation Limit Reached
```
Before:                            After:
Current:  5.2 MB                   Current:  0 MB (new)
.log.1:   10 MB                    .log.1:   5.2 MB (was current)
.log.2:   10 MB                    .log.2:   10 MB (was .log.1)
.log.3:   10 MB                    .log.3:   10 MB (was .log.2)
.log.4:   10 MB                    .log.4:   10 MB (was .log.3)
.log.5:   10 MB ───► DELETED       .log.5:   10 MB (was .log.4)
```

## User Journey: Viewing Logs

```
Step 1: Open Application
┌─────────────────────────────┐
│ Nextcloud Restore & Backup  │
│                             │
│     [Start Restore]         │
│     [Create Backup]         │
└─────────────────────────────┘
              │
              │ Click ☰ menu button
              ▼
Step 2: Open Menu
┌─────────────────────────────┐
│ Advanced Features           │
│ ─────────────────────────── │
│ 🌐 Remote Access (Tailscale)│
│ 📋 View Logs            ◄───┼─── Click here
│                             │
│      [Close]                │
└─────────────────────────────┘
              │
              │ Logs window opens
              ▼
Step 3: View Logs
┌─────────────────────────────┐
│ Application Logs            │
│ ─────────────────────────── │
│ [Scrollable log display]    │
│                             │
│ • See all operations        │
│ • Track errors              │
│ • Review history            │
│                             │
│ [🔄] [📁] [🗑️] [Close]     │
└─────────────────────────────┘
```

## Log Entry Anatomy

```
┌──────────────┬───────────┬────────────────────────────────────┐
│  Timestamp   │   Level   │            Message                 │
├──────────────┼───────────┼────────────────────────────────────┤
│ 2025-10-14   │   INFO    │ Application started                │
│ 14:20:04,878 │           │                                    │
└──────────────┴───────────┴────────────────────────────────────┘
      │              │                     │
      │              │                     └─ What happened
      │              └─ Severity level
      └─ When it happened
```

## Log Levels Explained

```
INFO Level (Most Common)
├─ ✓ Normal operations
├─ ✓ Successful actions
├─ ✓ Progress updates
└─ Example: "Backup created successfully"

WARNING Level (Attention Needed)
├─ ⚠️  Potential issues
├─ ⚠️  Non-critical problems
├─ ⚠️  Performance concerns
└─ Example: "Large file detected (>1GB)"

ERROR Level (Action Required)
├─ ✗ Failed operations
├─ ✗ Exceptions
├─ ✗ Stack traces
└─ Example: "Failed to connect to database"
```

## Feature Comparison

### Before (Old Logging)
```
❌ Log file in application directory
❌ No rotation (grows indefinitely)
❌ No GUI viewer
❌ Manual file access required
❌ May fill disk space
❌ Lost on uninstall
```

### After (New Logging)
```
✅ Log file in user's Documents folder
✅ Automatic rotation (10MB max)
✅ Built-in GUI viewer
✅ Easy 3-click access
✅ Controlled disk usage (~60MB max)
✅ Persists through updates
```

## Log Viewer Button Actions

```
┌───────────────────────────────────────────────────────────┐
│ [🔄 Refresh]                                              │
│  ├─ Reloads log file from disk                           │
│  ├─ Shows latest entries                                 │
│  └─ Use when monitoring active operations                │
├───────────────────────────────────────────────────────────┤
│ [📁 Open Log Folder]                                      │
│  ├─ Opens file explorer                                  │
│  ├─ Shows all log files (including backups)              │
│  └─ Allows copying files for sharing                     │
├───────────────────────────────────────────────────────────┤
│ [🗑️ Clear Logs]                                          │
│  ├─ Deletes all log entries                              │
│  ├─ Requires confirmation                                │
│  └─ Cannot be undone                                     │
├───────────────────────────────────────────────────────────┤
│ [Close]                                                   │
│  └─ Closes log viewer window                             │
└───────────────────────────────────────────────────────────┘
```

## Cross-Platform Support

```
Windows
├─ Log Location: C:\Users\<username>\Documents\NextcloudLogs\
├─ Open Folder: os.startfile()
└─ Status: ✅ Fully Supported

macOS
├─ Log Location: /Users/<username>/Documents/NextcloudLogs/
├─ Open Folder: subprocess.Popen(['open', ...])
└─ Status: ✅ Fully Supported

Linux
├─ Log Location: /home/<username>/Documents/NextcloudLogs/
├─ Open Folder: subprocess.Popen(['xdg-open', ...])
└─ Status: ✅ Fully Supported
```

## Implementation Architecture

```
nextcloud_restore_and_backup-v9.py
│
├─ setup_logging() [Lines 25-68]
│  ├─ Detects OS and Documents folder
│  ├─ Creates NextcloudLogs directory
│  ├─ Configures RotatingFileHandler
│  └─ Returns log file path
│
├─ LOG_FILE_PATH [Line 71]
│  └─ Global variable with log file location
│
├─ show_dropdown_menu() [Lines 2573-2713]
│  ├─ Creates dropdown menu
│  ├─ Adds "View Logs" button
│  └─ Calls show_log_viewer() on click
│
└─ show_log_viewer() [Lines 2715-2871]
   ├─ Creates log viewer window
   ├─ Displays log contents in Text widget
   ├─ Implements Refresh button
   ├─ Implements Open Folder button
   ├─ Implements Clear Logs button
   └─ Applies theme (light/dark)
```

## Storage Management

```
Total Storage Used:
┌─────────────────────────────────────────┐
│ Current Log:        10 MB (max)         │
│ Backup 1 (.log.1):  10 MB               │
│ Backup 2 (.log.2):  10 MB               │
│ Backup 3 (.log.3):  10 MB               │
│ Backup 4 (.log.4):  10 MB               │
│ Backup 5 (.log.5):  10 MB               │
├─────────────────────────────────────────┤
│ TOTAL:             ~60 MB (maximum)     │
└─────────────────────────────────────────┘

Automatic Cleanup:
• Oldest backup deleted when limit reached
• No manual intervention required
• Disk space never exceeded
```

## Testing Coverage

```
Test Suite 1: Persistent Logging
├─ Test 1: Logging imports ✅
├─ Test 2: Log file location ✅
├─ Test 3: Rotation configuration ✅
├─ Test 4: View Logs button ✅
├─ Test 5: Log viewer features ✅
├─ Test 6: Cross-platform support ✅
└─ Test 7: Log persistence ✅

Test Suite 2: Log Rotation
├─ Test 1: Rotation functionality ✅
└─ Test 2: Production config ✅

Test Suite 3: Diagnostic Logging
└─ All 12 checks passing ✅

Total: 21/21 tests passed ✅
```

## Use Cases

```
Use Case 1: Troubleshooting Errors
User Action:     Operation fails
Application:     Logs error with stack trace
User:            Opens log viewer
Result:          Sees exact error and can report it

Use Case 2: Tracking Backup History
User Action:     Creates multiple backups over time
Application:     Logs each backup with timestamp
User:            Opens log viewer
Result:          Reviews complete backup history

Use Case 3: Monitoring Active Operations
User Action:     Starts long-running restore
Application:     Logs each step in real-time
User:            Opens log viewer, clicks refresh
Result:          Sees live progress updates

Use Case 4: Sharing Logs for Support
User Action:     Encounters issue
Application:     All details logged
User:            Clicks "Open Log Folder", copies file
Result:          Can share log with support team

Use Case 5: Disk Space Management
User Action:     None (automatic)
Application:     Rotates logs when 10MB reached
Result:          Disk space controlled, old logs preserved
```

## Privacy & Security Model

```
✅ SAFE (Never Logged)
├─ Passwords
├─ API keys
├─ Credentials
├─ Personal data
├─ File contents
└─ Network secrets

⚠️  LOGGED (May contain)
├─ File paths (with username)
├─ Timestamps
├─ Configuration settings
├─ Error messages
└─ Stack traces

🔒 SECURITY
├─ Local storage only
├─ No external transmission
├─ User-controlled location
└─ Standard file permissions
```

## Benefits Summary

```
For End Users:
├─ ✓ Easy troubleshooting (GUI access)
├─ ✓ Complete operation history
├─ ✓ No command-line required
├─ ✓ Persistent across restarts
└─ ✓ Automatic cleanup

For Developers:
├─ ✓ Comprehensive debugging info
├─ ✓ Stack traces included
├─ ✓ Easy to add logging
├─ ✓ Timestamps for correlation
└─ ✓ Cross-platform consistency

For Support:
├─ ✓ Users can share logs easily
├─ ✓ Complete context available
├─ ✓ Error details with traces
├─ ✓ Operation timeline
└─ ✓ No special tools needed
```

## Future Enhancement Ideas

```
Possible Additions:
├─ 🔍 Search functionality in log viewer
├─ 📊 Filter by log level (INFO/WARNING/ERROR)
├─ 📅 Date range selection
├─ 📦 Export logs to ZIP
├─ 🔄 Auto-refresh option
├─ 🎨 Syntax highlighting
├─ 📈 Performance metrics
└─ ☁️  Optional remote logging
```

---

**Summary**: Persistent logging provides a complete, user-friendly solution for tracking application activity, troubleshooting errors, and maintaining operational history—all accessible with just 3 clicks from the main interface.

**Access**: Menu (☰) → View Logs (📋) → Done!
