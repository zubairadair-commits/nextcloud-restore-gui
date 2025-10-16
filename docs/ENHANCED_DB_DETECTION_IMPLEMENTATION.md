# Enhanced Database Detection Implementation

## Overview

This document describes the enhanced database detection feature that automatically identifies the database type used by Nextcloud by inspecting running Docker containers. The implementation ensures all Docker commands run silently without showing console windows to the user.

## Problem Statement

Previously, the application would:
1. Only read config.php from the Nextcloud container
2. Show console windows when running Docker commands on Windows
3. Prompt users to manually select database type when auto-detection failed

## Solution

The enhanced detection system uses multiple strategies to robustly detect the database:

### 1. Silent Docker Execution

All Docker commands now run without showing console windows:

#### `get_subprocess_creation_flags()`
- Returns `CREATE_NO_WINDOW` (0x08000000) flag on Windows
- Returns 0 on Linux/macOS (not needed)

#### `run_docker_command_silent(cmd, timeout=10)`
- Wrapper around `subprocess.run()` that applies creation flags
- Prevents console windows from appearing
- Handles timeouts and errors gracefully
- Returns `subprocess.CompletedProcess` or `None` on error

### 2. Container Discovery

#### `list_running_database_containers()`
Lists all running database containers by:
- Running `docker ps --format '{{.Names}}|{{.Image}}'`
- Parsing output to identify MySQL, MariaDB, and PostgreSQL containers
- Returns list of dicts: `[{'name': str, 'image': str, 'type': str}, ...]`

Supported database types:
- `mysql` - MySQL containers
- `mariadb` - MariaDB containers  
- `pgsql` - PostgreSQL containers

### 3. Container Inspection

#### `inspect_container_environment(container_name)`
Extracts environment variables from a container:
- Runs `docker inspect` to get container configuration
- Parses environment variables (KEY=VALUE format)
- Returns dict of environment variables
- Useful for finding database credentials and configuration

### 4. Multi-Strategy Detection

#### `detect_db_from_container_inspection(nextcloud_container, db_containers)`

Implements three detection strategies in order:

**Strategy 1: Read config.php**
- Reads config.php from Nextcloud container using existing `detect_database_type_from_container()`
- Extracts dbtype, dbname, dbuser, dbhost
- Tries to match with running database containers

**Strategy 2: Single Container Match**
- If only one database container is running, assume it's the one
- Inspects its environment for additional info
- Returns the detected type

**Strategy 3: Network Analysis**
- When multiple DB containers exist, checks network connections
- Finds which DB container shares a network with Nextcloud
- Returns the matched container's database type

Returns: `(dbtype, db_info)` where:
- `dbtype`: 'mysql', 'mariadb', 'pgsql', or None
- `db_info`: dict with container details, config, environment, networks

## Integration with Backup Flow

The enhanced detection is integrated into `start_backup()`:

```python
# 1. Scan for database containers
db_containers = list_running_database_containers()

# 2. Use comprehensive detection
dbtype, db_info = detect_db_from_container_inspection(nextcloud_container, db_containers)

# 3. Fallback to simple config.php reading
if not dbtype:
    dbtype, db_config = detect_database_type_from_container(nextcloud_container)

# 4. Only prompt user as last resort
if not dbtype:
    # Show messagebox asking user to select database type
    ...
```

## Updated Functions

All Docker subprocess calls now use `run_docker_command_silent()`:

- `is_docker_running()` - Check if Docker daemon is running
- `get_nextcloud_container_name()` - Find Nextcloud container
- `get_postgres_container_name()` - Find PostgreSQL container  
- `check_container_network()` - Check container network membership
- `attach_container_to_network()` - Connect container to network
- `detect_database_type_from_container()` - Read config.php from container

## User Experience Improvements

### Before
1. Docker commands showed console windows (flash on Windows)
2. Limited detection (only config.php reading)
3. Frequent manual database selection prompts

### After
1. All Docker commands run silently (no console windows)
2. Multi-strategy detection with higher success rate:
   - Scans all database containers
   - Checks container images
   - Analyzes network connections
   - Reads config.php
3. Manual selection only when all strategies fail
4. Informative messages about detected database

## Testing

Comprehensive test suite in `test_enhanced_db_detection.py`:

1. **Subprocess Creation Flags Test**
   - Verifies correct flags on Windows (CREATE_NO_WINDOW)
   - Verifies no flags on Linux/macOS

2. **Silent Docker Command Test**
   - Executes Docker commands
   - Verifies no console windows appear
   - Checks command output

3. **List Database Containers Test**
   - Scans for MySQL, MariaDB, PostgreSQL
   - Identifies container types from images

4. **Container Environment Inspection Test**
   - Extracts environment variables
   - Finds database configuration

5. **Comprehensive Detection Test**
   - Tests multi-strategy detection
   - Verifies correct database type identification

6. **No Console Window Test**
   - Visual verification that no windows flash
   - Platform-specific validation

## Example Detection Output

```
Scanning for database containers...
Found 2 database container(s)
✓ Found database container on shared network: nextcloud-db (pgsql)
✓ Detected database: PostgreSQL
  Database name: nextcloud
  Container: nextcloud-db
Database detected: PostgreSQL
```

## Platform Support

### Windows
- Uses CREATE_NO_WINDOW flag (0x08000000)
- Prevents console windows from appearing
- Tested with Docker Desktop

### Linux
- No special flags needed (console not shown by default)
- Works with Docker daemon
- Tested on Ubuntu/Debian

### macOS
- No special flags needed
- Works with Docker Desktop
- Should work identically to Linux

## Error Handling

All functions handle errors gracefully:
- Timeouts return None or empty results
- Missing containers don't crash the application
- Failed detection triggers user prompt as fallback
- Detailed error messages printed to console for debugging

## Performance

- Silent execution adds no overhead
- Container scanning is fast (single docker ps call)
- Detection completes in < 1 second typically
- Minimal impact on backup start time

## Security Considerations

- No credentials stored or logged
- Environment variables with "PASSWORD" are masked in debug output
- Uses existing Docker permissions (no elevation needed)
- All subprocess calls have timeouts to prevent hanging

## Future Enhancements

Potential improvements:
1. Cache detection results between operations
2. Support for remote Docker hosts
3. Detection of database version/variant
4. Database health checks before backup
5. Automatic credential extraction from environment

## Backward Compatibility

The changes are fully backward compatible:
- Existing detection methods still work
- Manual selection still available as fallback
- No changes to backup file format
- No new dependencies required
