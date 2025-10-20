# SQLite Restore Logic Fix - Complete Documentation

## Overview

This document describes the changes made to fix the SQLite restore logic in the Nextcloud Restore GUI application. The goal was to ensure that when a backup with SQLite is detected, the workflow does NOT attempt to access or create a database container, as SQLite databases are file-based and stored within the data folder.

## Problem Statement

Previously, the restore workflow would:
1. Always attempt to link Nextcloud containers to a database container
2. Try to create or access database containers even for SQLite backups
3. Show misleading "Docker Error" messages when database containers were missing for SQLite
4. Include database services in docker-compose.yml files for SQLite backups

This caused confusion and unnecessary errors during SQLite restores.

## Solution

### Key Changes

#### 1. Container Creation Logic (`ensure_nextcloud_container`)

**File:** `src/nextcloud_restore_and_backup-v9.py`

**Change:** Added `dbtype` parameter to control container linking behavior

```python
def ensure_nextcloud_container(self, dbtype=None):
    """
    Ensure Nextcloud container is running, using values from GUI
    
    Args:
        dbtype: Database type ('sqlite', 'mysql', 'pgsql'). 
                If 'sqlite', skip DB container linking.
    """
```

**Behavior:**
- **For SQLite:** Creates Nextcloud container WITHOUT attempting to link to database container
  ```python
  if dbtype == 'sqlite':
      result = subprocess.run(
          f'docker run -d --name {new_container_name} --network bridge -p {port}:80 {NEXTCLOUD_IMAGE}',
          shell=True, ...
      )
  ```

- **For MySQL/PostgreSQL:** Maintains existing behavior with database linking
  ```python
  else:
      result = subprocess.run(
          f'docker run -d --name {new_container_name} --network bridge --link {POSTGRES_CONTAINER_NAME}:db -p {port}:80 {NEXTCLOUD_IMAGE}',
          shell=True, ...
      )
  ```

#### 2. Database Container Creation Skip (`_restore_auto_thread`)

**Change:** Skip database container creation entirely for SQLite

```python
db_container = None
if dbtype != 'sqlite':
    # Start database container first (needed for Nextcloud container linking)
    db_container = self.ensure_db_container(dbtype=dbtype)
    if not db_container:
        logger.error("Failed to create database container!")
        self.set_restore_progress(0, "Restore failed!")
        return
else:
    logger.info("SQLite detected - no separate database container needed")
```

**Impact:** 
- SQLite restores skip all database container operations
- Only Nextcloud app container is created for SQLite
- Database .db file is copied with the data folder (existing behavior)

#### 3. Error Classification Improvement (`analyze_docker_error`)

**Change:** Added SQLite-specific error handling

```python
def analyze_docker_error(stderr_output, container_name=None, port=None, dbtype=None):
    """
    Args:
        dbtype: Database type ('sqlite', 'mysql', 'pgsql') - helps classify errors correctly
    """
    
    # Special handling for SQLite - this is expected, not an error
    if dbtype == 'sqlite':
        error_info['error_type'] = 'expected_sqlite_no_db'
        error_info['user_message'] = "SQLite configuration detected - no separate database container needed."
        error_info['suggested_action'] = (
            "This is expected behavior for SQLite backups.\n\n"
            "SQLite stores the database in a file within the data folder,\n"
            "so no separate database container is required.\n\n"
            "The restore will continue normally."
        )
```

**Impact:**
- No misleading "Docker Error" messages for SQLite
- Helpful, context-aware messages for users
- Clear explanation that missing DB containers are expected for SQLite

#### 4. Docker Compose Generation (Already Correct)

The `generate_docker_compose_yml()` function already properly handled SQLite:

```python
if dbtype == 'sqlite':
    # SQLite - no separate database service needed
    compose_content = f"""version: '3.8'

services:
  nextcloud:
    image: nextcloud
    container_name: nextcloud-app
    ports:
      - "{nextcloud_port}:80"
    volumes:
      - ./nextcloud-data:/var/www/html
    restart: unless-stopped
    environment:
      - SQLITE_DATABASE={dbname}
"""
```

**Verified:** No `db:` service in SQLite docker-compose.yml files

## Database Type Flow

### SQLite Restore Flow

```
1. Extract backup
2. Detect database type → "sqlite"
3. Generate docker-compose.yml (NO db service)
4. Create host folders (only nextcloud-data)
5. Start Nextcloud container (NO database linking)
6. Copy config, data, apps folders
7. Restore SQLite database (file copy - handled by data folder)
8. Update config.php
9. Complete ✓
```

### MySQL/PostgreSQL Restore Flow

```
1. Extract backup
2. Detect database type → "mysql" or "pgsql"
3. Generate docker-compose.yml (WITH db service)
4. Create host folders (nextcloud-data AND db-data)
5. Start database container
6. Start Nextcloud container (WITH database linking)
7. Copy config, data, apps folders
8. Restore database from SQL dump
9. Update config.php
10. Complete ✓
```

## Test Coverage

### New Tests

1. **`tests/test_sqlite_restore_logic.py`** (8 tests)
   - ✅ ensure_nextcloud_container accepts dbtype
   - ✅ SQLite skips database linking
   - ✅ Database container not created for SQLite
   - ✅ docker-compose.yml has no db service for SQLite
   - ✅ analyze_docker_error handles SQLite
   - ✅ ensure_db_container accepts dbtype
   - ✅ Restore thread passes dbtype
   - ✅ SQLite restore method exists

2. **`tests/test_restore_flow_branching.py`** (6 integration tests)
   - ✅ SQLite restore flow
   - ✅ MySQL restore flow
   - ✅ PostgreSQL restore flow
   - ✅ Container creation branching
   - ✅ Error handling branching
   - ✅ Docker-compose generation branching

### Existing Tests (Still Passing)

- ✅ `test_sqlite_detection_flow.py` (5 tests)
- ✅ `test_restore_error_reporting.py` (7 tests)

**Total Test Coverage:** 26 tests, all passing

## Security

**CodeQL Analysis:** ✅ Passed (0 alerts)

See `SECURITY_SUMMARY_SQLITE_RESTORE.md` for detailed security analysis.

## Backward Compatibility

✅ All changes are backward compatible:
- New parameters are optional with safe defaults
- Existing code paths continue to work
- No breaking changes to public APIs
- Error handling is enhanced, not replaced

## Benefits

1. **For SQLite Users:**
   - ✅ No misleading database container errors
   - ✅ Faster restore (no unnecessary container creation)
   - ✅ Cleaner, simpler docker-compose.yml files
   - ✅ Clear, helpful error messages

2. **For MySQL/PostgreSQL Users:**
   - ✅ No changes to existing behavior
   - ✅ Maintains database container linking
   - ✅ Same restore flow as before

3. **For Developers:**
   - ✅ Cleaner code with proper branching
   - ✅ Better error classification
   - ✅ Comprehensive test coverage
   - ✅ No security vulnerabilities

## Usage

No user action required. The changes are automatic:

1. User selects a backup to restore
2. System detects database type from config.php
3. Restore flow automatically branches based on database type
4. SQLite: Simple, container-only restore
5. MySQL/PostgreSQL: Full restore with database containers

## Future Enhancements

Potential improvements for future PRs:
- [ ] Add database type indicator in UI
- [ ] Show different progress steps for SQLite vs SQL databases
- [ ] Add tooltip explaining why SQLite is different
- [ ] Consider adding SQLite validation checks

## Conclusion

The SQLite restore logic is now robust, silent (no misleading errors), and correctly branches based on database type. All tests pass, no security issues detected, and the user experience is significantly improved for SQLite backups.

---

**Author:** GitHub Copilot Coding Agent  
**Date:** 2025-10-20  
**PR:** Fix SQLite restore logic to skip DB container operations
