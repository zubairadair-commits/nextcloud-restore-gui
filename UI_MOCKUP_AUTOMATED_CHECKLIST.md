# UI Mockup: Automated Setup Checklist

## Visual Overview of New UI Elements

---

## 1. Schedule Backup Configuration Screen (With Existing Schedule)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Schedule Automatic Backups                           │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                        Current Status                              │ │
│  │                                                                    │ │
│  │  ✓ Scheduled backup is active                                     │ │
│  │  Frequency: daily                                                 │ │
│  │  Time: 02:00 (UTC-5 Eastern Time)                                │ │
│  │  Backup Directory: C:\Backups\Nextcloud                          │ │
│  │  ☁️ Cloud Sync: OneDrive (automatic sync enabled)                │ │
│  │                                                                    │ │
│  │     [Disable Schedule]    [Delete Schedule]                       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│                     Configure New Schedule                                │
│                                                                           │
│  Backup Directory:  ℹ️                                                   │
│  ┌─────────────────────────────────────────────────────────┬─────────┐  │
│  │ C:\Users\John\OneDrive\Nextcloud_Backups               │ Browse  │  │
│  └─────────────────────────────────────────────────────────┴─────────┘  │
│                                                                           │
│  📁 Detected Cloud Sync Folders:                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ ☁️ OneDrive: C:\Users\John\OneDrive                             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  Frequency:                                                               │
│     ○ Daily    ● Weekly    ○ Monthly                                     │
│                                                                           │
│  Backup Time (HH:MM):  [UTC-5 Eastern Time]                             │
│  ┌──────┐                                                                │
│  │ 02:00│  (Enter time in 24-hour format)                               │
│  └──────┘                                                                │
│                                                                           │
│  ☑ Encrypt backups                                                       │
│                                                                           │
│  Encryption Password:                                                     │
│  ┌──────────────────────┐                                                │
│  │ ••••••••••••••••••   │                                                │
│  └──────────────────────┘                                                │
│                                                                           │
│        ┌────────────┐  ┌───────────────────────────┐                    │
│        │ 🧪 Test Run│  │ Create/Update Schedule    │                    │
│        └────────────┘  └───────────────────────────┘                    │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    📊 Last Run Status                              │ │
│  │                                                                    │ │
│  │  Status: Ready                                                    │ │
│  │  Last Run: 2024-10-14 02:00:15                                   │ │
│  │  Next Run: 2024-10-15 02:00:00                                   │ │
│  │                                                                    │ │
│  │  ✓ Recent Backup Found:                                          │ │
│  │    File: nextcloud_backup_20241014_020015.tar.gz                │ │
│  │    Created: 2024-10-14 02:00:45                                  │ │
│  │    Size: 125.67 MB                                               │ │
│  │    Age: 13.1 hours ago                                           │ │
│  │                                                                    │ │
│  │                    [📄 View Recent Logs]                          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│                   [🔍 Verify Scheduled Backup]                           │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Validation Success Dialog

```
┌──────────────────────────────────────────────────────────────┐
│  Validation Successful                                  [X]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ All Validation Checks Passed                            │
│                                                              │
│  ✓ Executable path exists:                                  │
│    C:\App\nextcloud_restore_and_backup.exe                  │
│                                                              │
│  ✓ Start directory is valid:                                │
│    C:\App                                                    │
│                                                              │
│  ✓ Task arguments are correct:                              │
│    --scheduled --backup-dir C:\Backups                      │
│                                                              │
│  ✓ Backup directory is writable:                            │
│    C:\Backups\Nextcloud                                     │
│                                                              │
│  ✓ Log file is writable:                                    │
│    C:\Users\John\Documents\NextcloudLogs\...log            │
│                                                              │
│  ✓ Task fields are valid:                                   │
│    name: NextcloudBackup, type: daily, time: 02:00         │
│                                                              │
│                                                              │
│  Proceed with creating the scheduled task?                  │
│                                                              │
│           [ Yes ]              [ No ]                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Validation Failure Dialog

```
┌──────────────────────────────────────────────────────────────┐
│  Validation Failed                                      [X]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ❌ Setup Validation Failed                                 │
│                                                              │
│  The following issues were found:                           │
│                                                              │
│  • Backup directory is not writable: Permission denied      │
│  • Invalid time format: 25:00. Must be HH:MM               │
│                                                              │
│  Please fix these issues before creating the scheduled      │
│  backup.                                                     │
│                                                              │
│                                                              │
│  Detailed Validation Results:                               │
│                                                              │
│  ✓ Executable path exists:                                  │
│    C:\App\nextcloud_restore_and_backup.exe                  │
│                                                              │
│  ✓ Start directory is valid:                                │
│    C:\App                                                    │
│                                                              │
│  ✓ Task arguments are correct:                              │
│    --scheduled --backup-dir C:\Backups                      │
│                                                              │
│  ✗ Backup directory is not writable:                        │
│    Permission denied                                         │
│                                                              │
│  ✓ Log file is writable:                                    │
│    C:\Users\John\Documents\NextcloudLogs\...log            │
│                                                              │
│  ✗ Task fields are valid:                                   │
│    Invalid time format: 25:00. Must be HH:MM               │
│                                                              │
│                                                              │
│                       [ OK ]                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Test Run Progress Dialog

```
┌──────────────────────────────────────────────┐
│  Test Backup                            [X]  │
├──────────────────────────────────────────────┤
│                                              │
│                                              │
│        Running test backup...                │
│                                              │
│                                              │
│          Please wait...                      │
│                                              │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 5. Test Run Success Dialog

```
┌──────────────────────────────────────────────────────────────┐
│  Test Backup Successful                                 [X]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ✓ Test backup successful!                                  │
│                                                              │
│  Test file created:                                         │
│    test_backup_20241014_150530.tar.gz                      │
│                                                              │
│  Size: 234 bytes                                            │
│                                                              │
│  Location: C:\Backups\Nextcloud                             │
│                                                              │
│                                                              │
│  Your scheduled backup configuration is working             │
│  correctly.                                                  │
│                                                              │
│                                                              │
│                       [ OK ]                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. Recent Logs Window

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Recent Backup Logs                                                  [X]  │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│              📄 Recent Scheduled Backup Logs                              │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ Found 15 relevant log entries:                                     │ │
│  │                                                                     │ │
│  │ ========================================================            │ │
│  │                                                                     │ │
│  │ 2024-10-14 02:00:10 - INFO - SCHEDULED: Starting scheduled        │ │
│  │   backup                                                           │ │
│  │ 2024-10-14 02:00:15 - INFO - SCHEDULED: Backup directory:         │ │
│  │   C:\Backups\Nextcloud                                            │ │
│  │ 2024-10-14 02:00:45 - INFO - SCHEDULED: Backup completed          │ │
│  │   successfully                                                     │ │
│  │ 2024-10-14 02:00:45 - INFO - SCHEDULED: Backup file:              │ │
│  │   nextcloud_backup_20241014_020015.tar.gz                         │ │
│  │ 2024-10-14 15:05:44 - INFO - VALIDATION: Executable path          │ │
│  │   verified                                                         │ │
│  │ 2024-10-14 15:05:44 - INFO - VALIDATION: Backup directory is      │ │
│  │   writable                                                         │ │
│  │ 2024-10-14 15:05:44 - INFO - VALIDATION: All checks passed        │ │
│  │   successfully                                                     │ │
│  │ 2024-10-14 15:06:12 - INFO - TEST RUN: Starting test backup      │ │
│  │ 2024-10-14 15:06:13 - INFO - TEST RUN: Test backup created       │ │
│  │   successfully                                                     │ │
│  │                                                                     ▲│ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│                              [Close]                                      │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Verification Progress Dialog

```
┌──────────────────────────────────────────────┐
│  Verifying Scheduled Backup             [X]  │
├──────────────────────────────────────────────┤
│                                              │
│                                              │
│    Verifying scheduled backup...             │
│                                              │
│                                              │
│  Checking backup files and logs...           │
│                                              │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 8. Verification Success Dialog

```
┌──────────────────────────────────────────────────────────────┐
│  Verification Results                                   [X]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ✓ Recent backup found:                                     │
│    nextcloud_backup_20241014_020015.tar.gz                 │
│                                                              │
│    Created: 2024-10-14 02:00:45                             │
│    Size: 125.67 MB                                          │
│                                                              │
│  ✓ Found 5 scheduled backup log entries                     │
│                                                              │
│                                                              │
│  ✓ Verification successful: Scheduled backup is working     │
│    correctly                                                 │
│                                                              │
│                                                              │
│                       [ OK ]                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Verification Warning Dialog

```
┌──────────────────────────────────────────────────────────────┐
│  Verification Results                                   [X]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ⚠ Last backup is 75.3 hours old                            │
│                                                              │
│  ✓ Found 3 scheduled backup log entries                     │
│                                                              │
│                                                              │
│  ⚠ Backup file exists but no recent log entries found      │
│                                                              │
│                                                              │
│  Recommendation: Check Task Scheduler to ensure the         │
│  scheduled task is running correctly.                       │
│                                                              │
│                                                              │
│                       [ OK ]                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 10. Verification Failure Dialog

```
┌──────────────────────────────────────────────────────────────┐
│  Verification Results                                   [X]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ✗ No backup files found in directory                       │
│                                                              │
│  ⚠ No scheduled backup entries found in recent logs        │
│                                                              │
│                                                              │
│  ✗ Verification failed: No recent backup found              │
│                                                              │
│                                                              │
│  Possible causes:                                           │
│  • Scheduled task is not running                            │
│  • Task is disabled in Task Scheduler                       │
│  • Backup directory was changed                             │
│  • Previous backups were manually deleted                   │
│                                                              │
│  Next steps:                                                │
│  1. Click "Test Run" to verify configuration                │
│  2. Check Windows Task Scheduler for errors                 │
│  3. Review logs for error messages                          │
│                                                              │
│                       [ OK ]                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## UI Elements Summary

### New Buttons

1. **🧪 Test Run** (Blue button)
   - Location: Below configuration fields
   - Action: Runs instant test backup
   - Background: #3498db (blue)

2. **📄 View Recent Logs** (Standard button)
   - Location: In Last Run Status section
   - Action: Opens log viewer window
   - Shows filtered log entries

3. **🔍 Verify Scheduled Backup** (Purple button)
   - Location: Below Last Run Status
   - Action: Runs verification check
   - Background: #9b59b6 (purple)

### New Sections

1. **Last Run Status** (Info panel)
   - Border: Ridge, 2px
   - Background: Info background color
   - Shows task status and last backup info

2. **Validation Results** (Dialog content)
   - Shows ✓ for passed checks
   - Shows ✗ for failed checks
   - Lists detailed error messages

### Color Indicators

- ✅ Green checkmark: Success
- ❌ Red X: Failure
- ⚠ Yellow warning: Warning/caution
- ✓ Check: Individual check passed
- ✗ Cross: Individual check failed
- 📊 Chart: Status information
- 📄 Document: Logs
- 🧪 Test tube: Testing
- 🔍 Magnifying glass: Verification
- ☁️ Cloud: Cloud sync status

---

## User Interaction Flow

```
1. User opens Schedule Backup
   ↓
2. User configures settings
   ↓
3. [Optional] User clicks "Test Run"
   ↓
4. System validates and shows results
   ↓
5. User clicks "Create/Update Schedule"
   ↓
6. System runs validation automatically
   ↓
7. System shows validation results dialog
   ↓
8. If all valid: User confirms creation
   ↓
9. If invalid: User fixes issues and tries again
   ↓
10. After first scheduled run
   ↓
11. User can view "Last Run Status"
   ↓
12. User can click "View Recent Logs"
   ↓
13. User can click "Verify Scheduled Backup"
```

---

## Accessibility Features

- All buttons have descriptive text
- Icons supplement text (not replace)
- Color-blind safe indicators (✓/✗ symbols)
- Clear error messages with actionable steps
- Scrollable log viewer for readability
- Modal dialogs center on screen
- Progress indicators for long operations

---

## Responsive Design

- Dialogs center on screen
- Text wraps appropriately
- Scrollbars appear when content exceeds space
- Fixed dialog sizes for consistency
- Buttons grouped logically
- Clear visual hierarchy

---

## Theme Support

All new UI elements support both light and dark themes:

**Light Theme**:
- Background: Light colors
- Text: Dark colors
- Buttons: Colored backgrounds with white text

**Dark Theme**:
- Background: Dark colors
- Text: Light colors
- Buttons: Same colored backgrounds with white text
- Info panels: Darker backgrounds with light text
