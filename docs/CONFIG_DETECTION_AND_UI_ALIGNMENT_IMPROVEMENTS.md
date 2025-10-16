# Config.php Detection and UI Alignment Improvements

## Overview
This document summarizes the improvements made to implement robust config.php detection and fix wizard page alignment issues.

## Changes Implemented

### 1. Robust config.php Detection Using Python's tarfile Module

#### New Function: `find_config_php_recursive(directory)`
- **Purpose**: Recursively search for config.php in any subdirectory
- **Logic**: 
  - Uses `os.walk()` to traverse all directories recursively
  - Checks each file named 'config.php'
  - Validates that it's a Nextcloud config by checking for `$CONFIG` or `dbtype` in the first 100 characters
  - Returns the full path to config.php if found, None otherwise
- **Location**: Lines 101-125

#### Updated: `detect_database_type(extract_dir)`
- **Enhancement**: Now uses recursive search as fallback
- **Flow**:
  1. First tries standard location: `extract_dir/config/config.php`
  2. If not found, performs recursive search using `find_config_php_recursive()`
  3. Shows clear warning if config.php not found after recursive search
  4. Returns (dbtype, db_config) or (None, None)
- **Location**: Lines 1465-1491

#### Updated: `early_detect_database_type_from_backup(backup_path, password)`
- **Major Change**: Now uses Python's `tarfile` module instead of subprocess
- **Benefits**:
  - More robust and platform-independent
  - Better error handling
  - Extracts all files (not just config/config.php)
  - Enables recursive search for config.php
- **Flow**:
  1. Decrypt backup if encrypted (.gpg)
  2. Extract all files using `tarfile.open()` and `tar.extractall()`
  3. Try standard location first
  4. Fall back to recursive search if needed
  5. Parse config.php and normalize database type
  6. Clean up temporary files
- **Location**: Lines 1493-1592

#### Updated: `fast_extract_tar_gz(archive_path, extract_to)`
- **Change**: Replaced subprocess tar extraction with Python's tarfile module
- **Benefits**:
  - More robust and portable
  - Better error handling
  - Platform-independent (no dependency on system tar command)
- **Location**: Lines 268-278

### 2. Improved Warning Messages

#### Enhanced Warnings When config.php Not Found
- **In `perform_extraction_and_detection()`**: Shows multi-line warning but allows navigation
  ```
  "⚠️ Warning: config.php not found or could not be read.
   Database type detection failed. You can still continue,
   but please ensure your database credentials are correct."
  ```
- **In `_restore_auto_thread()`**: Shows detailed warning during restore
  ```
  "⚠️ WARNING: config.php not found in backup!
   
   Database type could not be automatically detected.
   Using PostgreSQL as default. The restore will continue,
   but please verify your database configuration matches your backup."
  ```
- **Workflow**: Never breaks the restore workflow - always allows user to continue

### 3. Fixed Wizard Page Alignment

#### Page 1 Improvements
- Added `anchor="center"` to entry container frames
- Added `justify="center"` to Entry widgets
- Added consistent padding (`pady=(0, 5)`) to description labels
- Ensured Browse button is centered

#### Page 2 Improvements
- Enhanced info frame centering with `anchor="center"` for all labels
- Added `justify="center"` to multi-line labels in info frame
- Ensured warning labels, instruction labels, and database frame are all centered
- Admin credentials frame properly centered

#### Page 3 Improvements
- Enhanced info frame centering
- Changed bullet list items from `anchor="w"` to `anchor="center"` with `justify="center"`
- Added consistent padding to description labels
- Ensured all container configuration elements are centered

#### General Improvements
- All section headings use `anchor="center"`
- All description labels use `anchor="center"` with consistent `pady=(0, 5)` padding
- All frames use `anchor="center"` for horizontal centering
- Info boxes and warning boxes properly centered

### 4. Detection Logic Flow

#### Before Navigation to Page 2:
```
User on Page 1 → Clicks "Next"
  ↓
wizard_navigate(direction=1)
  ↓
perform_extraction_and_detection()
  ↓
early_detect_database_type_from_backup(backup_path, password)
  ↓
- Decrypt if .gpg (requires password)
- Extract ALL files using tarfile
- Search for config.php (standard location first, then recursive)
- Parse dbtype from config.php
- Set detected_dbtype
  ↓
Navigate to Page 2
```

#### During Actual Restore:
```
Start Restore → _restore_auto_thread()
  ↓
auto_extract_backup() - Extract full backup
  ↓
detect_database_type(extract_dir)
  ↓
- Try standard location: extract_dir/config/config.php
- Fall back to recursive search
- Parse dbtype
  ↓
Continue with restore using detected dbtype
```

## Testing

All changes have been validated with unit tests covering:
1. ✓ Finding config.php at standard location (config/config.php)
2. ✓ Finding config.php in nested subdirectories (backup/data/config/config.php)
3. ✓ Handling missing config.php gracefully
4. ✓ Extracting tar.gz archives and finding config.php

## Benefits

1. **Robustness**: Recursive search ensures config.php is found even in non-standard locations
2. **Platform Independence**: Using Python's tarfile module eliminates dependency on system tar
3. **Better UX**: Clear warnings when config.php not found, but workflow never breaks
4. **Consistent UI**: All wizard elements properly centered for better visual consistency
5. **Extraction After Decryption**: Detection only happens after successful decryption and extraction

## Backward Compatibility

- All existing functionality preserved
- Fallback to PostgreSQL maintained when detection fails
- No breaking changes to the restore workflow
- Enhanced detection is transparent to users

## Files Modified

- `nextcloud_restore_and_backup-v9.py` - Main application file
  - New function: `find_config_php_recursive()`
  - Updated: `detect_database_type()`
  - Updated: `early_detect_database_type_from_backup()`
  - Updated: `fast_extract_tar_gz()`
  - Updated: `perform_extraction_and_detection()`
  - Updated: `_restore_auto_thread()`
  - Updated: `create_wizard_page1()`
  - Updated: `create_wizard_page2()`
  - Updated: `create_wizard_page3()`

## Visual Status Indicators

Enhanced console output with visual indicators:
- ✓ Success indicators (green checkmarks in text)
- ⚠️ Warning indicators (warning symbols)
- ✗ Error indicators (red X symbols)
- Clear, descriptive messages for each operation

## Next Steps

The implementation is complete and ready for use. All requirements from the problem statement have been addressed:

1. ✅ Robust config.php detection using tarfile and recursive search
2. ✅ Fixed wizard page alignment with proper centering
3. ✅ Detection only runs after successful extraction
4. ✅ Clear warnings when config.php not found
5. ✅ Workflow never breaks, always allows continuation
