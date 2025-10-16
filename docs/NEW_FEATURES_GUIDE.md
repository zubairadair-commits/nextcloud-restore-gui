# New Features Guide - Nextcloud Restore & Backup Utility

## Overview

This guide documents the major features added to the Nextcloud Restore & Backup Utility to make it more beginner-friendly, robust, and feature-rich.

---

## 1. 🏥 Service Health Dashboard

### Description
Real-time monitoring of critical services with visual status indicators.

### Features
- **Live Status Checks**: Monitors Docker, Nextcloud, Tailscale, and network connectivity
- **Color-Coded Indicators**:
  - ✅ Green: Service is healthy
  - ⚠️ Yellow: Warning or degraded state
  - ❌ Red: Service error or not available
  - ❓ Gray: Status unknown
- **Refresh Button**: Manual refresh of all health checks
- **Last Checked Time**: Shows when health was last verified

### Location
Visible on the main landing page at the bottom of the screen.

### How to Use
1. Launch the application
2. View the "🏥 System Health" section on the landing page
3. Click the 🔄 button to manually refresh health status
4. Hover over any item for more details

### Technical Details
- Non-blocking: Health checks run in background threads
- Cached: Results are cached to avoid excessive checking
- Services checked:
  - **Docker**: Verifies Docker daemon is running
  - **Nextcloud**: Checks if Nextcloud container is running
  - **Tailscale**: Verifies Tailscale VPN status (Linux only)
  - **Network**: Tests internet connectivity

---

## 2. ✓ Backup Verification System

### Description
Automatic integrity checking of backups to ensure they're valid and complete.

### Features
- **Automatic Verification**: Runs after each backup completes
- **Manual Verification**: Verify any backup from history
- **Comprehensive Checks**:
  - File existence and size
  - Archive integrity (tar.gz)
  - Encryption validation
  - Required folders (config, data)
- **Status Tracking**: Results stored in backup history

### Verification Statuses
- **Success** (✅): Backup is valid and complete
- **Warning** (⚠️): Backup exists but may be incomplete
- **Error** (❌): Backup is corrupted or invalid
- **Pending** (⏳): Verification not yet performed

### How to Use

#### Automatic Verification
1. Create a backup normally
2. After backup completes, verification runs automatically
3. Results shown in completion dialog
4. Status saved to backup history

#### Manual Verification
1. Go to "📜 Backup History"
2. Find the backup to verify
3. Click "✓ Verify" button
4. Enter encryption password if required
5. View verification results

### Technical Details
- Tests archive extraction without full restore
- Checks for critical folders (config, data)
- Handles both encrypted and unencrypted backups
- Non-destructive (doesn't modify backup files)

---

## 3. 💡 In-App Help & Tooltips

### Description
Context-sensitive help system with hover tooltips for all UI elements.

### Features
- **Hover Tooltips**: Appear when mouse hovers over buttons/fields
- **Professional Appearance**: Yellow background, black text
- **Smart Positioning**: Automatically positioned near the element
- **Delay**: 500ms delay prevents accidental triggers
- **Cross-Platform**: Works on Windows, Linux, and macOS

### Tooltips Added To
- Main action buttons (Backup, Restore, New Instance, Schedule)
- Backup History button
- Health dashboard refresh button
- Folder selection checkboxes
- All buttons in backup history view
- Password entry fields
- Navigation buttons

### How to Use
Simply hover your mouse over any button, field, or control for about half a second to see contextual help.

### Example Tooltips
- **Backup Now**: "Create a backup of your Nextcloud data, config, and database"
- **Restore from Backup**: "Restore your Nextcloud from a previous backup file"
- **Encryption Password**: "Use a strong password to protect sensitive data. Leave empty to skip encryption."
- **Folder Checkboxes**: "This folder is required for a complete backup"

---

## 4. 📜 Backup History & Restore Points

### Description
Visual database of all backups with metadata, allowing easy restore and management.

### Features
- **Persistent Storage**: SQLite database stores all backup metadata
- **Rich Information Display**:
  - Timestamp (date and time)
  - File size (MB)
  - Encryption status (🔒 indicator)
  - Database type (PostgreSQL, MySQL, SQLite)
  - Verification status with icons
  - User notes
- **Quick Actions**:
  - 🛠 Restore: One-click restore from backup
  - ✓ Verify: Check backup integrity
  - 📤 Export: Copy backup to another location
  - 📍 Show Path: Display full file path
- **Scrollable List**: Handles hundreds of backups efficiently
- **Mouse Wheel Support**: Smooth scrolling with mouse wheel

### How to Use

#### View Backup History
1. Click "📜 Backup History" on the landing page
2. Browse the list of previous backups
3. Each item shows full details

#### Restore from History
1. Find the desired backup in the list
2. Click "🛠 Restore" button
3. Confirm the restoration
4. Follow the restore wizard

#### Verify a Backup
1. Find the backup in the list
2. Click "✓ Verify" button
3. Enter password if encrypted
4. Wait for verification to complete
5. View results

#### Export a Backup
1. Find the backup in the list
2. Click "📤 Export" button
3. Select destination folder
4. Wait for copy to complete

### Database Location
- Windows: `%USERPROFILE%\.nextcloud_backup_utility\backup_history.db`
- Linux/Mac: `~/.nextcloud_backup_utility/backup_history.db`

### Technical Details
- SQLite database for cross-platform compatibility
- Automatically created on first use
- Stores up to unlimited backups
- Default display: 50 most recent backups
- Thread-safe operations

---

## 5. 📁 Selective Backup

### Description
Choose which folders to include in backups, allowing for smaller, faster backups.

### Features
- **Visual Selection**: Checkboxes for each folder
- **Critical Folders**: Config and data are always included (locked)
- **Optional Folders**: Apps and custom_apps can be excluded
- **Clear Descriptions**: Each folder shows what it contains
- **Tooltips**: Hover for more information
- **Persistent Selection**: Choices saved for the backup session

### Available Folders
1. **config** (Required)
   - Configuration files
   - Essential for Nextcloud operation
   - Cannot be deselected

2. **data** (Required)
   - User files and data
   - Essential for Nextcloud operation
   - Cannot be deselected

3. **apps** (Optional)
   - Standard Nextcloud apps
   - Can be re-downloaded
   - Safe to exclude for smaller backups

4. **custom_apps** (Optional)
   - Third-party/custom apps
   - May need manual reinstallation
   - Include if you have custom apps

### How to Use
1. Start a backup normally
2. On the folder selection screen:
   - Review the folder list
   - Check/uncheck optional folders
   - Critical folders are pre-selected and locked
3. Click "Continue →"
4. Proceed with encryption and backup

### Use Cases

#### Full Backup (Default)
Select all folders for complete backup including all apps.

#### Quick Backup
- Select only config and data
- Skip apps for faster backup
- Good for frequent backups

#### Data-Only Backup
- Select only critical folders
- Smallest backup size
- Restore requires app reinstallation

### Technical Details
- Folder selection UI created dynamically
- Choices stored in `self.selected_backup_folders`
- Backwards compatible (defaults to all folders if not used)
- Works with both GUI and scheduled backups

---

## 6. 📤 Download/Export Backups

### Description
Copy backups to external locations for off-site storage or sharing.

### Features
- **One-Click Export**: Copy backup files easily
- **Any Destination**: Export to local drives, network shares, USB drives
- **Progress Indication**: Shows progress during copy
- **Metadata Preservation**: Maintains file timestamps and permissions
- **Works with All Backups**: Both encrypted and unencrypted

### How to Use

#### From Backup History
1. Go to "📜 Backup History"
2. Find the backup to export
3. Click "📤 Export" button
4. Choose destination folder
5. Wait for copy to complete
6. Confirmation shown when done

#### Manual Copy
Alternatively, you can manually copy backup files from their original location. Use the 📍 button to show the full path.

### Destination Options
- **External Drive**: USB drive, external HDD
- **Network Share**: NAS, file server
- **Cloud Sync Folder**: Dropbox, Google Drive, OneDrive sync folder
- **Different Local Drive**: Another partition or drive

### Best Practices
1. **Regular Off-Site Backups**: Export critical backups to external storage
2. **Test Restores**: Verify exported backups can be restored
3. **Multiple Locations**: Keep backups in multiple places
4. **Encrypted Backups**: Export encrypted backups for security
5. **Document Passwords**: Store encryption passwords securely

### Cloud Service Integration
While direct cloud upload isn't implemented, you can:
1. Export backup to cloud sync folder (e.g., `~/Dropbox/Backups/`)
2. Let cloud service handle the upload automatically
3. Supported services:
   - Dropbox
   - Google Drive
   - OneDrive
   - iCloud Drive
   - Any sync service

---

## 7. 📱 Responsive Layout Improvements

### Description
Enhanced window resizing and layout management for various screen sizes.

### Features
- **Dynamic Font Sizing**: Adjusts for smaller windows
- **Minimum Window Size**: 700x700 prevents excessive shrinking
- **Smart Layout**: Elements adapt to available space
- **Mouse Wheel Scrolling**: Scroll lists with mouse wheel
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Touch-Friendly**: Larger buttons and spacing
- **Window Resize Handler**: Smooth adaptation to size changes

### Responsive Behaviors

#### Window Width < 750px
- Header font reduces to 18pt (from 22pt)
- Maintains readability on narrow screens

#### Window Width >= 750px
- Normal font sizes (22pt header)
- Full feature display

#### Scrollable Areas
- Backup history list: Full mouse wheel support
- Domain management: Scroll with mouse wheel
- All scroll areas: Linux (Button-4/5) and Windows support

### Keyboard Navigation
- Tab key: Move between fields
- Enter key: Activate focused button
- Escape key: Close dialogs (where applicable)

### Accessibility Features
- High contrast colors
- Clear visual hierarchy
- Tooltips for context
- Descriptive labels
- Keyboard shortcuts

### Testing on Different Screens

#### Desktop (1920x1080 or higher)
- All features visible
- No scrolling needed for main content
- Comfortable spacing

#### Laptop (1366x768)
- Slight scrolling may be needed
- All features accessible
- Responsive font sizing

#### Small Windows (700x700 minimum)
- Reduced font sizes
- Scrollable areas
- All features remain functional

---

## Usage Examples

### Example 1: Full Backup with Verification
```
1. Click "🔄 Backup Now"
2. Select backup destination
3. Keep all folders selected
4. Enter encryption password
5. Click "Start Backup"
6. Wait for backup to complete
7. Automatic verification runs
8. View results in completion dialog
9. Check "📜 Backup History" to see entry
```

### Example 2: Quick Data-Only Backup
```
1. Click "🔄 Backup Now"
2. Select backup destination
3. Uncheck "apps" and "custom_apps"
4. Skip encryption (leave password blank)
5. Click "Start Backup"
6. Faster backup completes
7. Smaller backup file created
```

### Example 3: Restore from History
```
1. Click "📜 Backup History"
2. Browse previous backups
3. Find desired restore point
4. Click "🛠 Restore" button
5. Confirm restoration
6. Enter password if encrypted
7. Follow restore wizard
8. System restored to that point
```

### Example 4: Verify and Export Old Backup
```
1. Click "📜 Backup History"
2. Find old backup to verify
3. Click "✓ Verify" button
4. View verification status
5. If valid, click "📤 Export"
6. Select USB drive or cloud folder
7. Wait for copy to complete
8. Safely store off-site
```

---

## Troubleshooting

### Health Dashboard Shows Errors
**Problem**: All services show error status
**Solution**:
1. Click refresh button 🔄
2. Check Docker is running: `docker ps`
3. Verify network connectivity
4. Restart application

### Backup Verification Fails
**Problem**: Backup shows ❌ error status
**Solution**:
1. Check file exists and isn't corrupted
2. Verify disk space isn't full
3. Try extracting manually with tar
4. Create new backup if needed

### Backup History Not Showing
**Problem**: No backups appear in history
**Solution**:
1. Check database file exists: `~/.nextcloud_backup_utility/backup_history.db`
2. Only shows backups created with this version
3. Old backups won't appear (create new ones)
4. Check file permissions on database

### Export Fails
**Problem**: Cannot export backup to destination
**Solution**:
1. Check destination has enough space
2. Verify write permissions
3. Try different destination
4. Check backup file isn't locked

### Tooltips Don't Appear
**Problem**: No tooltips when hovering
**Solution**:
1. Wait full 500ms (half second)
2. Ensure mouse is over the element
3. Check application has focus
4. Restart application if needed

---

## Technical Architecture

### Component Overview
```
┌─────────────────────────────────────────────┐
│           User Interface Layer              │
│  - Landing Page with Health Dashboard       │
│  - Backup History View                      │
│  - Folder Selection Dialog                  │
│  - Tooltip System                           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Business Logic Layer                │
│  - BackupHistoryManager                     │
│  - Health Check Functions                   │
│  - Verification Functions                   │
│  - Export/Copy Operations                   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Data Storage Layer                 │
│  - SQLite Database (backup_history.db)      │
│  - Configuration Files                      │
│  - Backup Files (.tar.gz / .tar.gz.gpg)     │
└─────────────────────────────────────────────┘
```

### Class Diagram
```
┌──────────────────────────┐
│     ToolTip              │
│  - widget                │
│  - text                  │
│  - delay                 │
│  + on_enter()            │
│  + on_leave()            │
│  + show_tooltip()        │
│  + hide_tooltip()        │
└──────────────────────────┘

┌──────────────────────────┐
│ BackupHistoryManager     │
│  - db_path               │
│  + add_backup()          │
│  + update_verification() │
│  + get_all_backups()     │
│  + get_backup_by_id()    │
└──────────────────────────┘

┌──────────────────────────┐
│ NextcloudRestoreWizard   │
│  - backup_history        │
│  - health_check_cache    │
│  - selected_folders      │
│  + show_backup_history() │
│  + _add_health_dashboard()│
│  + _verify_backup()      │
│  + _export_backup()      │
└──────────────────────────┘
```

### Database Schema
```sql
CREATE TABLE backups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_path TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    size_bytes INTEGER,
    encrypted BOOLEAN,
    database_type TEXT,
    folders_backed_up TEXT,
    verification_status TEXT,
    verification_details TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Reference

### BackupHistoryManager Class

#### `__init__(db_path=None)`
Initialize backup history manager.
- **Parameters**: `db_path` (str, optional) - Path to SQLite database
- **Returns**: BackupHistoryManager instance

#### `add_backup(backup_path, database_type=None, folders=None, encrypted=False, notes="")`
Add a new backup record.
- **Returns**: Backup ID (int)

#### `update_verification(backup_id, status, details="")`
Update verification status of a backup.
- **Parameters**:
  - `backup_id` (int) - ID of backup to update
  - `status` (str) - One of: 'success', 'warning', 'error', 'pending'
  - `details` (str) - Description of verification result

#### `get_all_backups(limit=50)`
Retrieve all backups, most recent first.
- **Returns**: List of tuples with backup data

#### `get_backup_by_id(backup_id)`
Get a specific backup record.
- **Returns**: Tuple with backup data or None

### Health Check Functions

#### `check_service_health()`
Check health of all services.
- **Returns**: Dict with service status information

#### `verify_backup_integrity(backup_path, password=None)`
Verify backup file integrity.
- **Returns**: Tuple of (status, details)
  - status: 'success', 'warning', or 'error'
  - details: Description string

---

## Migration Guide

### From Previous Versions

#### Database
No database migration needed. The backup history database is created automatically on first use. Previous backups won't appear in history until you create a new backup.

#### Configuration
All existing configuration files and settings are preserved.

#### Backups
All existing backup files remain compatible. You can:
1. Add them to history by doing a manual verification
2. Continue using them with the restore wizard
3. Export them to other locations

### Upgrading
1. Replace the old `nextcloud_restore_and_backup-v9.py` file
2. Launch the application
3. New features are immediately available
4. Create a test backup to populate history
5. Verify health dashboard shows correct status

---

## FAQ

### Q: Will old backups appear in the history?
**A**: No, only backups created with the new version are tracked. Existing backups can still be restored using the normal restore wizard.

### Q: Where is the backup history database stored?
**A**: `~/.nextcloud_backup_utility/backup_history.db` (cross-platform)

### Q: Can I delete entries from backup history?
**A**: Not yet implemented in the UI. You can manually delete records from the SQLite database if needed.

### Q: Does verification modify the backup file?
**A**: No, verification is read-only and never modifies backup files.

### Q: Can I export to cloud storage?
**A**: Export to your cloud sync folder (Dropbox, Google Drive, etc.) and let the sync service upload automatically.

### Q: What happens if I deselect critical folders?
**A**: Critical folders (config, data) cannot be deselected. They're required for a functional backup.

### Q: Do tooltips work on touchscreens?
**A**: Tooltips are primarily for mouse users. Touch users should rely on clear button labels and help dialogs.

### Q: Is the health check real-time?
**A**: It checks on landing page load and when you click refresh. It doesn't continuously monitor.

---

## Contributing

To add new features or improve existing ones:

1. Follow the existing code style
2. Add appropriate tooltips for new UI elements
3. Update backup history for new backup types
4. Add tests to `test_new_features.py`
5. Update this documentation

---

## Credits

Developed as part of the Nextcloud Restore & Backup Utility enhancement project.

**Version**: 9.1 (with major features)
**Last Updated**: 2025-10-13
