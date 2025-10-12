# SQLite Backup Fix - Complete Documentation

## Problem Statement

When SQLite (or sqlite3) was detected as the database type in a Nextcloud container's config.php, users were incorrectly prompted to install database dump utilities (pg_dump/mysqldump). SQLite databases are simple files that should just be copied with the data folder, not dumped using external utilities.

## Root Cause

The `detect_database_type_from_container()` function read the dbtype value directly from config.php, which could be either 'sqlite' or 'sqlite3'. However, subsequent checks in the backup flow only compared against 'sqlite', causing 'sqlite3' to be treated as an unknown database type that required external dump utilities.

## Solution

The fix implements a two-part approach:

### 1. Normalization at Detection
- Modified `detect_database_type_from_container()` to normalize 'sqlite3' → 'sqlite'
- Modified `parse_config_php_dbtype()` to normalize 'sqlite3' → 'sqlite'
- This ensures consistent handling throughout the application

### 2. Defensive Checks
- Updated `check_database_dump_utility()` to handle both 'sqlite' and 'sqlite3'
- Updated `start_backup()` utility check to skip both 'sqlite' and 'sqlite3'
- Updated `run_backup_process()` to handle both 'sqlite' and 'sqlite3'
- Updated `run_backup_process_scheduled()` to handle both 'sqlite' and 'sqlite3'

## Changes Made

### File: `nextcloud_restore_and_backup-v9.py`

#### 1. detect_database_type_from_container() (Line ~645)
```python
# Added normalization
if dbtype == 'sqlite3':
    dbtype = 'sqlite'
```

#### 2. parse_config_php_dbtype() (Line ~697)
```python
# Added normalization
if dbtype == 'sqlite3':
    dbtype = 'sqlite'
```

#### 3. check_database_dump_utility() (Line ~228)
```python
# Changed from: elif dbtype == 'sqlite':
# To:
elif dbtype in ['sqlite', 'sqlite3']:
    return True, 'sqlite'
```

#### 4. start_backup() (Line ~1735)
```python
# Changed from: if dbtype != 'sqlite':
# To:
if dbtype not in ['sqlite', 'sqlite3']:
    utility_installed, utility_name = check_database_dump_utility(dbtype)
```

#### 5. run_backup_process() (Line ~1847)
```python
# Changed from: if dbtype == 'sqlite':
# To:
if dbtype in ['sqlite', 'sqlite3']:
    self.set_progress(6, "SQLite database backed up with data folder")
```

#### 6. run_backup_process_scheduled() (Line ~4532)
```python
# Changed from: if dbtype == 'sqlite':
# To:
if dbtype in ['sqlite', 'sqlite3']:
    print("Step 6/10: SQLite database backed up with data folder")
```

## Flow Diagram

### Before (Broken)
```
config.php: dbtype='sqlite3'
    ↓
detect_database_type_from_container() returns 'sqlite3'
    ↓
start_backup() check: if dbtype != 'sqlite' → TRUE (enters check)
    ↓
❌ Prompts user to install pg_dump or mysqldump
    ↓
run_backup_process() check: if dbtype == 'sqlite' → FALSE
    ↓
❌ Attempts to create database dump (fails)
```

### After (Fixed)
```
config.php: dbtype='sqlite3'
    ↓
detect_database_type_from_container() returns 'sqlite' (normalized)
    ↓
start_backup() check: if dbtype not in ['sqlite', 'sqlite3'] → FALSE
    ↓
✅ No utility prompts
    ↓
run_backup_process() check: if dbtype in ['sqlite', 'sqlite3'] → TRUE
    ↓
✅ SQLite backed up with data folder (no dump needed)
```

## Benefits

1. **No User Prompts**: SQLite users are no longer prompted to install unnecessary database utilities
2. **Correct Behavior**: SQLite database files are properly backed up with the data folder
3. **Consistency**: Both 'sqlite' and 'sqlite3' dbtype values are handled correctly
4. **Backwards Compatible**: Existing 'sqlite' configurations continue to work
5. **Works Everywhere**: Fix applies to both manual and scheduled backups

## Testing

Created comprehensive test suite:
- `test_sqlite_backup_fix.py` - Validates code changes
- `test_sqlite_detection_flow.py` - Tests detection flow
- `test_sqlite_backup_integration.py` - End-to-end integration test

All tests pass successfully.

## Verification

To verify the fix:
1. Create a Nextcloud container with SQLite (config.php has `'dbtype' => 'sqlite3'`)
2. Run backup (manual or scheduled)
3. Verify: No utility prompts appear
4. Verify: Backup completes successfully
5. Verify: SQLite .db file is included in backup archive

## Related Files

- Main application: `nextcloud_restore_and_backup-v9.py`
- Test files: `test_sqlite_*.py`
- Documentation: `DATABASE_AUTO_DETECTION.md`

## Impact

This fix resolves a critical usability issue where SQLite users were blocked from creating backups due to unnecessary utility requirements. The changes are minimal, focused, and maintain backward compatibility.
