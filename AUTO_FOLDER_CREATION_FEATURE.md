# Automatic Host Folder Creation Feature

## Overview

The Nextcloud Restore GUI now automatically detects and creates required host folders during the restore process. This eliminates manual setup steps and prevents restore failures due to missing directories.

## What's New?

### 🚀 Automatic Folder Creation

During the restore workflow, the system now:

1. **Detects required folders** from:
   - `config.php` (database type, data directory)
   - `docker-compose.yml` (custom volume mappings, if present)
   - Extracted backup contents (config, data, apps, custom_apps)

2. **Creates folders automatically** before starting containers:
   - `./nextcloud-data` - Main Nextcloud volume mount
   - `./db-data` - Database data directory (for MySQL/PostgreSQL only)
   - Proper permissions set (755)

3. **Provides clear feedback**:
   - Shows which folders were created
   - Lists folders that already existed
   - Displays warnings if creation fails (but continues with restore)

### 🎯 Benefits

✅ **No Manual Setup Required**
- Folders are created automatically during restore
- No need to manually create directories beforehand
- Reduces user errors and confusion

✅ **Prevents Restore Failures**
- Missing folders no longer cause restore to fail
- Docker volume mounts work correctly
- Files are copied to the right locations

✅ **Smart Detection**
- Detects database type (SQLite doesn't need `db-data` folder)
- Respects custom folder names from docker-compose.yml
- Only creates folders that are actually needed

✅ **Robust Error Handling**
- Clear error messages if folder creation fails
- Permission issues are reported with guidance
- Restore continues even if some folders can't be created

## How It Works

### Workflow Integration

The automatic folder creation happens at this point in the restore workflow:

```
1. User selects backup file
2. Backup is extracted
3. Database type is detected from config.php
   ⬇️
4. 🆕 REQUIRED FOLDERS ARE AUTO-DETECTED
5. 🆕 HOST FOLDERS ARE AUTO-CREATED
   ⬇️
6. Docker containers are started
7. Files are copied into containers
8. Database is restored
9. Configuration is updated
10. Restore completes
```

### Detection Logic

**Step 1: Detect Database Type**
- Reads `config.php` to determine if database is SQLite, MySQL, or PostgreSQL
- SQLite: Only `./nextcloud-data` needed
- MySQL/PostgreSQL: Both `./nextcloud-data` and `./db-data` needed

**Step 2: Check for Custom Folder Names**
- If `docker-compose.yml` exists, parse it for volume mappings
- Example: `./my-nextcloud-data:/var/www/html` → uses `./my-nextcloud-data`
- Falls back to default names if no custom mappings found

**Step 3: Verify Backup Contents**
- Checks which folders exist in the extracted backup
- Standard folders: config, data, apps, custom_apps
- Only creates host folders if corresponding backup folders exist

### Folder Creation

**Permissions**
- All folders created with mode `0o755` (rwxr-xr-x)
- Owner: Current user running the restore
- Group: Current user's primary group

**Error Handling**
```python
try:
    os.makedirs(folder, mode=0o755, exist_ok=True)
    print(f"✓ Created folder: {folder}")
except Exception as e:
    print(f"✗ Failed to create {folder}: {e}")
    # Continue with restore, show warning
```

**Idempotent Operation**
- If folder already exists: Marked as "existing", no error
- If folder created successfully: Marked as "created"
- If creation fails: Error logged, but restore continues

## Examples

### Example 1: PostgreSQL Restore

**Scenario:** Restoring a Nextcloud backup with PostgreSQL database

**Detection:**
```
✓ Detected database type: pgsql
✓ Required folders:
  - ./nextcloud-data (for Nextcloud files)
  - ./db-data (for PostgreSQL data)
```

**Folder Creation:**
```
✓ Created folder: ./nextcloud-data
✓ Created folder: ./db-data
Host folders prepared: Created: ./nextcloud-data, ./db-data
```

**Result:**
- Both folders created automatically
- Restore proceeds without manual intervention
- Docker containers mount volumes correctly

### Example 2: SQLite Restore

**Scenario:** Restoring a Nextcloud backup with SQLite database

**Detection:**
```
✓ Detected database type: sqlite3
✓ Required folders:
  - ./nextcloud-data (for Nextcloud files)
  - ./db-data: None (SQLite doesn't need separate folder)
```

**Folder Creation:**
```
✓ Created folder: ./nextcloud-data
Host folders prepared: Created: ./nextcloud-data
```

**Result:**
- Only `./nextcloud-data` created
- No `./db-data` folder (not needed for SQLite)
- SQLite database file restored within data folder

### Example 3: Custom Docker Compose Folder Names

**Scenario:** Existing docker-compose.yml with custom volume names

**docker-compose.yml:**
```yaml
services:
  nextcloud:
    volumes:
      - ./my-nc-data:/var/www/html
  db:
    volumes:
      - ./my-db-storage:/var/lib/postgresql/data
```

**Detection:**
```
✓ Detected custom folder names from docker-compose.yml
✓ Required folders:
  - ./my-nc-data (custom Nextcloud data folder)
  - ./my-db-storage (custom database folder)
```

**Folder Creation:**
```
✓ Created folder: ./my-nc-data
✓ Created folder: ./my-db-storage
Host folders prepared: Created: ./my-nc-data, ./my-db-storage
```

**Result:**
- Custom folder names respected
- Matches existing docker-compose.yml configuration
- No conflicts with existing setup

### Example 4: Folders Already Exist

**Scenario:** User previously ran restore or manually created folders

**Detection:**
```
✓ Required folders:
  - ./nextcloud-data
  - ./db-data
```

**Folder Creation:**
```
Host folders prepared: Already exist: ./nextcloud-data, ./db-data
```

**Result:**
- No errors about existing folders
- Existing folders are reused
- Restore proceeds normally

### Example 5: Permission Error

**Scenario:** User doesn't have write permission in current directory

**Detection:**
```
✓ Required folders:
  - ./nextcloud-data
  - ./db-data
```

**Folder Creation:**
```
⚠️ Warning: Some folders could not be created:
Failed to create ./nextcloud-data: [Errno 13] Permission denied: './nextcloud-data'
Failed to create ./db-data: [Errno 13] Permission denied: './db-data'

Continuing with restore...
```

**Result:**
- Warning displayed to user
- Error details logged
- Restore continues (may fail later when Docker tries to mount)
- User can manually create folders and retry

## User Interface

### Progress Messages

During restore, you'll see these messages:

```
Checking and creating required host folders...
  ↓
✓ Created folder: ./nextcloud-data
✓ Created folder: ./db-data
  ↓
Host folders prepared: Created: ./nextcloud-data, ./db-data
```

### Warning Messages

If folder creation fails:

```
⚠️ Warning: Could not auto-create folders: [Error details]

Continuing with restore...
```

### Success Confirmation

After successful folder creation:

```
Host folders prepared: Created: ./nextcloud-data, ./db-data | Already exist: (none)
```

## Technical Details

### Functions Added

**`detect_required_host_folders(config_php_path, compose_file_path, extract_dir)`**
- Detects which folders are needed based on configuration
- Returns dict with folder paths and extracted backup folders
- Handles SQLite vs MySQL/PostgreSQL differences
- Parses docker-compose.yml for custom folder names

**`create_required_host_folders(folders_dict)`**
- Creates folders with proper permissions (755)
- Returns success status, created list, existing list, errors list
- Idempotent operation (safe to run multiple times)
- Robust error handling

### Integration Point

Added in `_restore_auto_thread()` method:

```python
# After database detection (line ~2632)
self.set_restore_progress(20, self.restore_steps[1])

# 🆕 Auto-create required host folders
folders_dict = detect_required_host_folders(...)
success, created, existing, errors = create_required_host_folders(folders_dict)

# Before starting containers (line ~2636)
if dbtype != 'sqlite':
    db_container = self.ensure_db_container()
```

### Configuration Parsing

**From config.php:**
```php
$CONFIG = array (
  'dbtype' => 'pgsql',  // Determines if db-data needed
  'datadirectory' => '/var/www/html/data',
  // ... other settings
);
```

**From docker-compose.yml:**
```yaml
services:
  nextcloud:
    volumes:
      - ./nextcloud-data:/var/www/html  # Host folder detected here
  db:
    volumes:
      - ./db-data:/var/lib/postgresql/data  # DB folder detected here
```

## Testing

### Unit Tests

Run: `python3 test_auto_folder_creation.py`

Tests cover:
- ✅ Folder detection from config.php (PostgreSQL)
- ✅ Folder detection from config.php (SQLite)
- ✅ Folder detection from docker-compose.yml
- ✅ Successful folder creation
- ✅ Handling of existing folders
- ✅ SQLite-specific behavior (no db-data)

### Integration Tests

Run: `python3 test_integration_auto_folder_creation.py`

Tests cover:
- ✅ Complete restore workflow with auto-folder creation
- ✅ SQLite restore workflow (no db-data folder)
- ✅ Folder permissions verification
- ✅ Error handling

### All Tests Pass ✅

```
============================================================
Results: 6/6 unit tests passed
Results: 2/2 integration tests passed
============================================================
✅ ALL TESTS PASSED
```

## Migration Guide

### For Existing Users

**No Action Required!**

If you've been using the restore wizard:
- The new feature is completely automatic
- Your existing workflows continue to work
- Folders are created automatically during restore
- No breaking changes

### For New Users

**Even Easier Now!**

When running your first restore:
1. Select your backup file
2. Enter decryption password (if encrypted)
3. Let the wizard detect your configuration
4. **Folders are created automatically** ← 🆕 No manual steps!
5. Containers are started with correct volume mounts
6. Restore completes successfully

### Manual Folder Creation No Longer Needed

**Before (Old Workflow):**
```bash
# User had to manually create folders
mkdir -p ./nextcloud-data
mkdir -p ./db-data
chmod 755 ./nextcloud-data ./db-data

# Then run restore
python3 nextcloud_restore_and_backup-v9.py
```

**Now (Automatic):**
```bash
# Just run restore - folders created automatically!
python3 nextcloud_restore_and_backup-v9.py
```

### Docker Compose Dialog

The "Check/Create Folders" button still exists in the Docker Compose suggestion dialog for manual verification, but it's now optional since folders are created automatically during restore.

## Troubleshooting

### Issue: "Permission denied" when creating folders

**Cause:** User doesn't have write permission in current directory

**Solution:**
```bash
# Run restore from a directory where you have write permission
cd ~/nextcloud-restore
python3 /path/to/nextcloud_restore_and_backup-v9.py

# Or fix permissions
sudo chown -R $USER:$USER /target/directory
```

### Issue: "Folder already exists" warning

**This is not an error!** The system detected existing folders and will reuse them. This is the expected behavior.

### Issue: Docker mount fails even though folders were created

**Possible causes:**
1. SELinux blocking access (on RHEL/CentOS)
   ```bash
   sudo setenforce 0  # Temporary fix
   ```

2. Folder ownership issue
   ```bash
   sudo chown -R 33:33 ./nextcloud-data  # www-data user
   ```

3. Wrong working directory
   - Ensure you're in the directory where folders were created
   - Docker Compose must be run from the same directory

## Future Enhancements

Potential improvements for future versions:

1. **Volume mount validation** - Verify Docker can actually mount the created folders
2. **Smart permission detection** - Set folder ownership to match container user (www-data)
3. **Backup folder structure** - Copy original permissions from backup
4. **Custom folder locations** - Allow user to specify custom folder paths
5. **Cleanup on failure** - Option to remove created folders if restore fails

## Related Documentation

- [Docker Compose Feature Guide](DOCKER_COMPOSE_FEATURE_GUIDE.md) - Docker Compose generation and detection
- [Automated Restore Guide](AUTOMATED_RESTORE_GUIDE.md) - Complete restore workflow
- [Developer Guide](DEVELOPER_GUIDE.md) - Technical implementation details

## Summary

The automatic host folder creation feature makes Nextcloud restores more reliable and user-friendly by:

✅ **Detecting** required folders from configuration  
✅ **Creating** folders automatically before container start  
✅ **Handling** SQLite vs MySQL/PostgreSQL differences  
✅ **Respecting** custom folder names from docker-compose.yml  
✅ **Providing** clear feedback and error handling  
✅ **Preventing** restore failures due to missing directories  

**Result:** Restores "just work" without manual folder setup!
