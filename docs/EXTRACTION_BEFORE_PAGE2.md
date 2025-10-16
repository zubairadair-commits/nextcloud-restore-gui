# Extraction and Detection Before Page 2 - Implementation

## Overview

This update refactors the wizard flow to perform backup archive extraction and database type detection **before** rendering Page 2 (Database Configuration), as requested in the problem statement.

## Problem Statement

Previously, the wizard had the following limitations:

1. **Encrypted backups (.gpg)**: Database type detection was skipped on Page 1 because the password was needed but the user hadn't navigated to the next page yet
2. **Delayed detection**: For encrypted backups, detection only happened during the restore process (after Page 3), meaning SQLite users still saw unnecessary database credential fields
3. **Poor UX**: Users with SQLite databases had to see and potentially fill in database credential fields that weren't needed

## Solution Implemented

### 1. Intercept Navigation from Page 1 to Page 2

Modified `wizard_navigate()` to intercept navigation when moving from Page 1 to Page 2:

```python
def wizard_navigate(self, direction):
    """Navigate between wizard pages, saving current page data"""
    # Save current page data
    self.save_wizard_page_data()
    
    # If navigating from Page 1 to Page 2, perform extraction and detection
    if self.wizard_page == 1 and direction == 1:
        if not self.perform_extraction_and_detection():
            # Detection failed or was cancelled - don't navigate
            return
    
    # Navigate to new page
    new_page = self.wizard_page + direction
    if 1 <= new_page <= 3:
        self.show_wizard_page(new_page)
```

### 2. New Method: `perform_extraction_and_detection()`

This method is called before showing Page 2:

```python
def perform_extraction_and_detection(self):
    """
    Perform backup extraction and database type detection before showing Page 2.
    Returns True if successful (or already detected), False if validation fails.
    """
```

**Key features:**
- Validates backup file and password before attempting detection
- Shows progress message during detection: "Extracting and detecting database type..."
- Handles detection failures gracefully (allows navigation but shows warning)
- Skips re-detection if already detected (user going back and forth)
- Sets `self.detected_dbtype` and `self.db_auto_detected` flags

### 3. Enhanced `early_detect_database_type_from_backup()` Method

Updated to support encrypted backups with password parameter:

```python
def early_detect_database_type_from_backup(self, backup_path, password=None):
```

**Changes:**
- Added optional `password` parameter
- Decrypts backup to temporary file if encrypted and password is provided
- Extracts config.php from decrypted backup
- Cleans up temporary decrypted file after extraction
- Returns `(dbtype, db_config)` tuple

**Flow for encrypted backups:**
1. Check if password is provided
2. Decrypt backup to temporary file using `decrypt_file_gpg()`
3. Extract config/config.php from decrypted file
4. Parse config.php to detect database type
5. Clean up temporary files

### 4. Existing UI Update Logic (Unchanged)

The existing `update_database_credential_ui()` method is called when Page 2 is created:

```python
# In create_wizard_page2()
if self.detected_dbtype:
    self.update_database_credential_ui(self.detected_dbtype)
```

This method:
- Hides database credential fields for SQLite
- Shows green informational message for SQLite
- Shows credential fields for MySQL/PostgreSQL

## User Experience Flow

### Before (Encrypted Backups)
1. Page 1: Select backup and enter password
2. Page 2: See all database credential fields (even for SQLite)
3. Page 3: Container configuration
4. Start Restore: Detection happens during restore process

### After (All Backups)
1. Page 1: Select backup and enter password
2. **Click "Next"**: Extraction and detection happens (with progress message)
3. Page 2: 
   - **SQLite**: Only see admin credential fields, database fields hidden
   - **MySQL/PostgreSQL**: See all database credential fields
4. Page 3: Container configuration
5. Start Restore: Skip detection (already done)

## Benefits

✅ **SQLite users never see unnecessary database credential fields**
✅ **Detection happens before Page 2 for all backup types (encrypted and unencrypted)**
✅ **Better UX with progress feedback during extraction**
✅ **Validation of backup file and password before navigation**
✅ **Graceful handling of detection failures**
✅ **No duplicate detection during restore process**

## Testing

Verified the following scenarios:

1. **SQLite detection from unencrypted backup**: ✓
2. **SQLite detection from encrypted backup**: ✓ (with password)
3. **PostgreSQL detection**: ✓
4. **MySQL detection**: ✓
5. **Config.php parsing**: ✓
6. **Tar.gz extraction**: ✓
7. **Navigation back and forth**: ✓ (skips re-detection)
8. **Invalid backup file**: ✓ (shows error, prevents navigation)
9. **Missing password**: ✓ (shows error, prevents navigation)

## Files Modified

- `nextcloud_restore_and_backup-v9.py`:
  - Modified `wizard_navigate()` - Added interception logic
  - Added `perform_extraction_and_detection()` - New method (54 lines)
  - Modified `early_detect_database_type_from_backup()` - Added password parameter and decryption logic
  - No changes to `update_database_credential_ui()` - Already implemented
  - No changes to `create_wizard_page2()` - Already calls update method
  - No changes to `validate_and_start_restore()` - Already skips SQLite validation

## Backward Compatibility

✅ **Fully backward compatible:**
- Unencrypted backups: Work as before (detection on file selection)
- Encrypted backups: Now detect before Page 2 (previously detected during restore)
- Non-SQLite databases: See same fields as before
- Validation logic: Unchanged
- Restore process: Unchanged

## Code Quality

- Clear error messages and progress feedback
- Proper cleanup of temporary files
- Graceful error handling
- Detailed logging for debugging
- Comprehensive comments
