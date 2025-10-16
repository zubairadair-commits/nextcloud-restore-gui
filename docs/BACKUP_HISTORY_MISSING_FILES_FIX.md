# Backup History Missing Files Fix

## Overview

This document describes the enhancement made to the Backup History page to ensure it only displays backups that still exist on disk.

## Problem Statement

Previously, the Backup History page would display all backups stored in the database, even if the actual backup files had been deleted from disk. This could lead to confusion when users tried to restore, verify, or export backups that no longer existed.

## Solution

The Backup History page now automatically:
1. **Checks file existence** - Verifies each backup file exists on disk before displaying it
2. **Cleans up database** - Removes records for missing backup files from the database
3. **Logs removals** - Records when missing backups are removed for transparency

## Implementation Details

### Changes to `BackupHistoryManager` Class

Added a new method to delete backup records:

```python
def delete_backup(self, backup_id):
    """Delete a backup record from the database"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM backups WHERE id = ?', (backup_id,))
    
    conn.commit()
    conn.close()
    logger.info(f"BACKUP HISTORY: Deleted backup record with ID {backup_id}")
```

### Changes to `show_backup_history` Method

Modified the method to filter backups and clean up missing entries:

```python
# Get backup history
backups = self.backup_history.get_all_backups()

# Filter out backups whose files no longer exist and clean up database
existing_backups = []
for backup in backups:
    backup_id = backup[0]
    backup_path = backup[1]
    
    if os.path.exists(backup_path):
        existing_backups.append(backup)
    else:
        # Remove missing backup from database
        logger.info(f"BACKUP HISTORY: Removing missing backup from history: {backup_path}")
        self.backup_history.delete_backup(backup_id)

# Display only existing backups
if not existing_backups:
    # Show "no backups" message
else:
    for backup in existing_backups:
        self._create_backup_item(content_frame, backup)
```

## Benefits

1. **Accurate Display** - Users only see backups they can actually use
2. **Clean Database** - Automatically removes stale records
3. **No Errors** - Users won't encounter "file not found" errors when trying to use displayed backups
4. **Transparent** - All removals are logged for auditing
5. **No User Action Required** - Cleanup happens automatically when viewing the history

## User Experience

### Before
- Backup History showed all historical backups, even deleted ones
- Clicking Restore/Verify/Export on missing backups showed error messages
- Database accumulated stale records over time

### After
- Backup History shows only available backups
- Users can confidently use any displayed backup
- Database stays clean and accurate
- Missing backups are logged and removed automatically

## Testing

Comprehensive tests were added in `tests/test_backup_history_missing_files.py`:

- **Test 1**: Verifies `delete_backup` method exists and works
- **Test 2**: Confirms `show_backup_history` filters missing backups
- **Test 3**: Validates database cleanup logic with real scenarios
- **Test 4**: Ensures action buttons still have file existence checks

### Running Tests

```bash
cd tests
python test_backup_history_missing_files.py
```

### Demonstration

A demo script is available to see the feature in action:

```bash
cd tests
python demo_backup_history_missing_files.py
```

## Backward Compatibility

The changes are fully backward compatible:
- Existing databases work without modification
- No schema changes required
- All existing functionality preserved
- Other methods (`_restore_from_history`, `_verify_backup_from_history`, `_export_backup`) retain their file existence checks

## Logging

All removals are logged with the prefix `BACKUP HISTORY:` for easy identification:

```
BACKUP HISTORY: Removing missing backup from history: /path/to/missing/backup.tar.gz
BACKUP HISTORY: Deleted backup record with ID 42
```

Logs can be found in: `Documents/NextcloudLogs/nextcloud_restore_gui.log`

## Future Enhancements

Possible future improvements:
- Add a "Restore from external backup" option to re-import deleted backups
- Show statistics about removed backups
- Add a preference to keep deleted backup records with a "missing" flag
- Implement archive/restore for backup records instead of permanent deletion

## Related Files

- **Main Implementation**: `src/nextcloud_restore_and_backup-v9.py`
- **Test Suite**: `tests/test_backup_history_missing_files.py`
- **Demo Script**: `tests/demo_backup_history_missing_files.py`
- **Existing Tests**: 
  - `tests/test_backup_history_display.py`
  - `tests/test_backup_history_fix.py`

## Summary

This enhancement ensures the Backup History page always reflects the actual state of backup files in the file system, providing users with accurate information and preventing errors when attempting to use backups that no longer exist.
