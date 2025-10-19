# Scheduled Backup Enhancements

## Overview

This document describes the new features added to the scheduled backup functionality in the Nextcloud Restore & Backup Utility.

## Features

### 1. Component Selection for Scheduled Backups

Users can now choose which components to include in their scheduled backups, mirroring the functionality available in manual backups.

#### UI Components

**Location**: Schedule Backup Configuration page (`show_schedule_backup()`)

**Section Header**: 📁 Components to Backup

**Description**: "Select which folders to include in scheduled backups"

**Checkboxes**:
- ✅ **config** - Configuration files (Required) - *Always checked, disabled*
- ✅ **data** - User data and files (Required) - *Always checked, disabled*
- ☐ **apps** - Standard Nextcloud apps - *Optional, user can toggle*
- ☐ **custom_apps** - Custom/third-party apps - *Optional, user can toggle*

**Default Behavior**: All components are selected by default. The required components (config and data) cannot be deselected.

#### Configuration Storage

Component selections are stored in the schedule configuration file (`~/.nextcloud_backup/schedule_config.json`):

```json
{
  "task_name": "NextcloudBackup",
  "backup_dir": "/path/to/backups",
  "frequency": "daily",
  "time": "02:00",
  "encrypt": false,
  "password": "",
  "components": {
    "config": true,
    "data": true,
    "apps": true,
    "custom_apps": false
  },
  "rotation_keep": 3,
  "enabled": true,
  "created_at": "2025-10-19T12:00:00"
}
```

#### Command-Line Integration

When the scheduled task runs, component selections are passed via the `--components` argument:

```bash
python nextcloud_restore_and_backup-v9.py --scheduled --backup-dir "/path/to/backups" --components "config,data,apps"
```

### 2. Automatic Backup Rotation

Users can now configure automatic backup rotation to manage disk space by keeping only a specified number of recent backups.

#### UI Components

**Location**: Schedule Backup Configuration page (`show_schedule_backup()`)

**Section Header**: ♻️ Backup Rotation

**Description**: "Automatically delete old backups when limit is reached"

**Radio Buttons** (labeled "Keep last:"):
- ⚪ **Unlimited (no deletion)** - All backups are preserved (default)
- ⚪ **1 backup (always replace)** - Each new backup deletes the previous one
- ⚪ **3 backups** - Keep the 3 most recent backups
- ⚪ **5 backups** - Keep the 5 most recent backups
- ⚪ **10 backups** - Keep the 10 most recent backups

**Tooltips**:
- "Unlimited": "All backups are kept (manual cleanup required)"
- "1 backup": "Each new backup will delete the previous one, saving disk space"
- "3/5/10 backups": "Keep the N most recent backups, delete older ones automatically"

#### Configuration Storage

The rotation setting is stored as `rotation_keep` in the schedule configuration:

```json
{
  "rotation_keep": 3  // 0 = unlimited, 1-10 = keep N backups
}
```

#### Command-Line Integration

The rotation setting is passed via the `--rotation-keep` argument:

```bash
python nextcloud_restore_and_backup-v9.py --scheduled --backup-dir "/path/to/backups" --rotation-keep 3
```

#### Rotation Logic

When a scheduled backup completes successfully and rotation is enabled (`rotation_keep > 0`):

1. **Scan Backup Directory**: List all files matching the pattern `nextcloud-backup-*.tar.gz` or `nextcloud-backup-*.tar.gz.gpg`
2. **Sort by Time**: Sort files by modification time (newest first)
3. **Identify Old Backups**: Files beyond the `rotation_keep` limit are marked for deletion
4. **Delete Files**: Remove old backup files from disk
5. **Update History**: Remove deleted backups from the backup history database
6. **Logging**: All rotation operations are logged for troubleshooting

**Example**: With `rotation_keep: 3`:
- Before: 5 backups (oldest to newest: B1, B2, B3, B4, B5)
- After new backup (B6): 4 backups kept (B4, B5, B6), 3 deleted (B1, B2, B3)
- After next backup (B7): Still 3 backups (B5, B6, B7), B4 deleted

## Implementation Details

### Modified Functions

1. **`show_schedule_backup()`**
   - Added component selection checkboxes
   - Added backup rotation radio buttons
   - Updated `_create_schedule()` call to pass new parameters

2. **`_create_schedule()`**
   - Updated signature to accept `component_vars` and `rotation_keep`
   - Extract component selections from checkboxes
   - Save components and rotation settings to configuration
   - Pass parameters to `create_scheduled_task()`

3. **`create_scheduled_task()`**
   - Updated signature to accept `components` and `rotation_keep`
   - Build command-line arguments with `--components` and `--rotation-keep`
   - Create Windows scheduled task with enhanced command

4. **`run_scheduled_backup()`**
   - Updated signature to accept `components` and `rotation_keep`
   - Parse component list from command-line argument
   - Pass components to backup process
   - Call `_perform_backup_rotation()` after successful backup

5. **`run_backup_process_scheduled()`**
   - Updated signature to accept `components` parameter
   - Filter `folders_to_copy` based on component selection
   - Maintain backward compatibility (None = backup all components)

6. **`_perform_backup_rotation()` (NEW)**
   - Scan backup directory for backup files
   - Sort by modification time
   - Delete old files exceeding the limit
   - Update backup history database
   - Comprehensive logging

### Command-Line Arguments

Added two new arguments to the argument parser:

```python
parser.add_argument('--components', type=str, default='', 
                    help='Comma-separated list of components to backup')
parser.add_argument('--rotation-keep', type=int, default=0, 
                    help='Number of backups to keep (0 = unlimited)')
```

### Backward Compatibility

- Existing scheduled backups without component/rotation settings will continue to work
- Default behavior: backup all components, no rotation (unlimited backups)
- Configuration files are backward compatible

## Usage Examples

### Scheduling a Backup with Component Selection

1. Navigate to "Schedule Backup Configuration"
2. Configure backup directory, frequency, and time
3. In "Components to Backup" section:
   - Config and Data are always selected (required)
   - Check "apps" if you want to include standard Nextcloud apps
   - Check "custom_apps" if you want to include custom/third-party apps
4. Click "Create/Update Schedule"

### Configuring Backup Rotation

1. In the "Backup Rotation" section, select:
   - "Unlimited" to keep all backups (no automatic deletion)
   - "1 backup" to always replace the previous backup (saves space)
   - "3/5/10 backups" to keep that many recent backups
2. The rotation will apply automatically after each scheduled backup

### Manual Testing

To test the scheduled backup manually:

```bash
# With component selection and rotation
python nextcloud_restore_and_backup-v9.py --scheduled \
  --backup-dir "/path/to/backups" \
  --components "config,data,apps" \
  --rotation-keep 3 \
  --encrypt --password "mypassword"

# Minimal (backup all, no rotation)
python nextcloud_restore_and_backup-v9.py --scheduled \
  --backup-dir "/path/to/backups"
```

## Testing

### Automated Tests

Three comprehensive test suites have been created:

1. **`test_scheduled_backup_enhancements.py`** (existing)
   - Validates scheduled task creation
   - Validates backup history tracking

2. **`test_scheduled_backup_component_rotation.py`** (new)
   - Tests component selection UI presence
   - Tests rotation UI presence
   - Tests parameter passing through the call chain
   - Tests configuration storage
   - 8 test cases, all passing

3. **`test_backup_rotation_logic.py`** (new)
   - Tests rotation with keep_count=3
   - Tests rotation with keep_count=1 (always replace)
   - Tests rotation with unlimited (no deletion)
   - Tests rotation with mixed encrypted/unencrypted files
   - 4 test scenarios, all passing

### Manual Testing Checklist

- [ ] Open Schedule Backup Configuration page
- [ ] Verify component selection checkboxes are present and correctly labeled
- [ ] Verify config and data checkboxes are checked and disabled
- [ ] Verify apps and custom_apps checkboxes are toggleable
- [ ] Verify backup rotation section is present with all options
- [ ] Create a schedule with custom component selection
- [ ] Verify configuration is saved correctly
- [ ] Run a test backup with component selection
- [ ] Verify only selected components are backed up
- [ ] Configure rotation (e.g., keep 3 backups)
- [ ] Create multiple backups to exceed the limit
- [ ] Verify old backups are automatically deleted
- [ ] Verify backup history database is updated correctly

## Benefits

### Component Selection
- **Flexibility**: Users can choose what to backup based on their needs
- **Space Savings**: Excluding large optional components saves disk space
- **Speed**: Smaller backups complete faster
- **Consistency**: Mirrors manual backup selection experience

### Backup Rotation
- **Automatic Management**: No manual cleanup required
- **Disk Space Control**: Prevents unlimited backup accumulation
- **Configurable**: Multiple options to suit different needs
- **Safe**: Always keeps the newest backups, deletes oldest first

## Future Enhancements

Potential improvements for future versions:

1. **Custom Rotation Counts**: Allow users to specify any number of backups to keep
2. **Time-Based Rotation**: Delete backups older than X days/weeks/months
3. **Size-Based Rotation**: Delete old backups when total size exceeds a threshold
4. **Notification**: Alert users when rotation deletes backups
5. **Rotation History**: Track what was deleted and when
6. **Component Presets**: Save and load component selection presets
7. **Smart Rotation**: Keep daily backups for a week, weekly for a month, monthly for a year

## Troubleshooting

### Component Selection Not Working

1. Check the schedule configuration file: `~/.nextcloud_backup/schedule_config.json`
2. Verify the `components` field contains the expected selections
3. Check the Windows Task Scheduler for the actual command being run
4. Review the backup logs in `Documents/NextcloudLogs/nextcloud_restore_gui.log`

### Rotation Not Deleting Old Backups

1. Verify `rotation_keep` is greater than 0 in the configuration
2. Check if there are enough backups to exceed the limit
3. Review rotation logs in `Documents/NextcloudLogs/nextcloud_restore_gui.log`
4. Ensure backup files match the expected naming pattern
5. Check file permissions in the backup directory

### Logs Location

All operations are logged to: `Documents/NextcloudLogs/nextcloud_restore_gui.log`

Search for:
- `SCHEDULED BACKUP:` - Scheduled backup events
- `BACKUP ROTATION:` - Rotation operations
- Component selections are logged during backup

## Conclusion

These enhancements significantly improve the scheduled backup feature by giving users more control over what gets backed up and how backup storage is managed. The implementation is thoroughly tested, backward compatible, and follows the existing code patterns in the application.
