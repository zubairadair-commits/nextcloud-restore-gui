# Integration Test Plan: Docker Compose Restore Workflow

## Overview

This document outlines integration test scenarios for the Docker Compose detection and generation feature in the Nextcloud restore workflow.

## Test Environment Setup

### Prerequisites
- Docker installed and running
- Python 3.x installed
- GPG installed (for encrypted backup tests)
- Test backup files with different database types

### Test Data Preparation

Create test backups for each scenario:

1. **PostgreSQL Backup**
   - Contains config/config.php with pgsql database
   - Includes SQL dump
   - Has data directory

2. **MySQL Backup**
   - Contains config/config.php with mysql database
   - Includes SQL dump
   - Has data directory

3. **SQLite Backup**
   - Contains config/config.php with sqlite database
   - Includes .db file
   - Has data directory

4. **Encrypted Backup**
   - Any of the above, but encrypted with GPG
   - Tests password handling in detection flow

## Integration Test Scenarios

### Test 1: Fresh Restore Without Existing Docker Compose

**Scenario:** First-time restore on a clean system without docker-compose.yml

**Steps:**
1. Start application
2. Select "Restore from Backup"
3. Choose PostgreSQL backup file
4. Enter password (if encrypted)
5. Click "Next" to navigate to Page 2
6. Wait for detection to complete

**Expected Results:**
- ✅ Config.php extracted successfully
- ✅ Database type detected as PostgreSQL
- ✅ Docker Compose suggestion dialog appears
- ✅ Dialog shows: "No Docker Compose usage detected"
- ✅ "Generate docker-compose.yml" button available
- ✅ Environment configuration section shows correct settings

**Verification:**
```bash
# Check console output
grep "Docker Compose usage detected" output.log
# Should show: "No Docker Compose usage detected"

# Dialog should display:
# - Database type: PGSQL
# - Database name: nextcloud
# - Database user: nextcloud
# - Data directory path
# - Trusted domains list
```

**Actions to Test:**

a. **Generate docker-compose.yml**
   - Click "Generate docker-compose.yml"
   - Save file
   - Verify file contains correct configuration
   - Check that services are properly defined

b. **Check/Create Folders**
   - Click "Check/Create Folders"
   - Verify ./nextcloud-data created
   - Verify ./db-data created (for non-SQLite)
   - Check permissions are correct

c. **Continue Without Generation**
   - Click "Continue"
   - Verify restore workflow proceeds normally
   - Complete restore successfully

### Test 2: Restore With Existing docker-compose.yml

**Scenario:** Restore when docker-compose.yml already exists

**Setup:**
```bash
# Create a test docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=olddb
  nextcloud:
    image: nextcloud
    ports:
      - "9000:80"
EOF
```

**Steps:**
1. Start application in directory with docker-compose.yml
2. Select backup with different configuration
3. Navigate to Page 2
4. Wait for detection

**Expected Results:**
- ✅ Config.php detected
- ✅ Docker Compose file detected
- ✅ Dialog shows: "Docker Compose usage detected"
- ✅ Warning about potential mismatches displayed
- ✅ Recommendations shown:
  - Review volume mappings
  - Verify database credentials match
  - Check port mappings

**Verification:**
```bash
# Check detection
grep "Found Docker Compose file" output.log
# Should show: "docker-compose.yml"

# Dialog should show:
# ⚠️ WARNING: If your existing docker-compose.yml doesn't match
# the detected config.php settings, you may experience issues.
```

### Test 3: Restore With Running Docker Compose Containers

**Scenario:** System has containers started via docker-compose

**Setup:**
```bash
# Start containers with compose
docker-compose up -d

# Verify labels
docker ps --format '{{.Labels}}' | grep com.docker.compose
```

**Steps:**
1. Start application
2. Select backup
3. Navigate through wizard

**Expected Results:**
- ✅ Detects Docker Compose labels on containers
- ✅ Shows "Docker Compose usage detected"
- ✅ Even without docker-compose.yml file in current directory

**Verification:**
```bash
# Check for label detection
grep "Detected Docker Compose labels" output.log
```

### Test 4: MySQL Database Detection and Generation

**Scenario:** Restore MySQL/MariaDB backup

**Steps:**
1. Select MySQL backup
2. Navigate to Page 2
3. Review detection dialog

**Expected Results:**
- ✅ Database type detected as MySQL
- ✅ Generated docker-compose.yml uses mariadb image
- ✅ MySQL environment variables present
- ✅ Port 3306 mapped correctly
- ✅ Transaction isolation command included

**Verification:**
```bash
# Check generated file
grep "mariadb" docker-compose.yml
grep "MYSQL_DATABASE" docker-compose.yml
grep "MYSQL_USER" docker-compose.yml
grep "3306:3306" docker-compose.yml
grep "transaction-isolation" docker-compose.yml
```

### Test 5: SQLite Database Detection and Generation

**Scenario:** Restore SQLite backup

**Steps:**
1. Select SQLite backup
2. Navigate to Page 2
3. Review detection and generation

**Expected Results:**
- ✅ Database type detected as SQLite
- ✅ No separate db service in compose file
- ✅ Only nextcloud service present
- ✅ SQLITE_DATABASE environment variable set
- ✅ No db-data folder required
- ✅ Database credential fields hidden on Page 2

**Verification:**
```bash
# Check generated file
grep "services:" docker-compose.yml | wc -l
# Should be 1 (only nextcloud)

grep "SQLITE_DATABASE" docker-compose.yml
# Should be present

grep "db:" docker-compose.yml
# Should not exist (no separate db service)
```

### Test 6: Encrypted Backup Handling

**Scenario:** Restore encrypted backup with Docker Compose detection

**Steps:**
1. Select .tar.gz.gpg backup
2. Enter decryption password
3. Navigate to Page 2
4. Wait for detection

**Expected Results:**
- ✅ Backup decrypted successfully
- ✅ Config.php extracted from decrypted archive
- ✅ Detection works same as unencrypted
- ✅ Temporary decrypted file cleaned up
- ✅ Dialog appears with correct configuration

**Verification:**
```bash
# Check cleanup
ls /tmp/nextcloud_decrypt_* 2>/dev/null
# Should be empty (temp files cleaned)

# Check detection log
grep "Backup decrypted successfully" output.log
grep "Config.php extracted" output.log
```

### Test 7: Config.php Parsing Edge Cases

**Scenario:** Test various config.php formats

**Test Cases:**

a. **Single quotes in config.php**
```php
$CONFIG = array (
  'dbtype' => 'pgsql',
  'dbname' => 'nextcloud',
);
```

b. **Double quotes in config.php**
```php
$CONFIG = array (
  "dbtype" => "mysql",
  "dbname" => "nextcloud",
);
```

c. **Mixed quotes**
```php
$CONFIG = array (
  'dbtype' => "sqlite",
  "dbname" => 'nextcloud',
);
```

d. **Multiple trusted domains**
```php
$CONFIG = array (
  'trusted_domains' => array (
    0 => 'localhost',
    1 => 'nextcloud.local',
    2 => '192.168.1.100',
  ),
);
```

**Expected Results:**
- ✅ All formats parsed correctly
- ✅ Database type detected in each case
- ✅ Trusted domains array parsed properly
- ✅ Mixed quotes handled correctly

### Test 8: Folder Creation and Validation

**Scenario:** Test folder management functionality

**Steps:**
1. Delete any existing folders
2. Run restore wizard
3. Click "Check/Create Folders"

**Expected Results:**
- ✅ ./nextcloud-data created if missing
- ✅ ./db-data created if missing (non-SQLite)
- ✅ Success message shows created folders
- ✅ Second click shows folders already exist
- ✅ Proper permissions set (755)

**Verification:**
```bash
# Check folder creation
ls -la | grep nextcloud-data
ls -la | grep db-data

# Check permissions
stat -c "%a %n" nextcloud-data db-data
# Should show: 755
```

### Test 9: Complete Restore Workflow Integration

**Scenario:** Full end-to-end restore with Docker Compose

**Steps:**
1. Select backup file
2. Navigate to Page 2, wait for detection
3. Generate docker-compose.yml
4. Create required folders
5. Click "Continue"
6. Fill in remaining configuration
7. Start restore

**Expected Results:**
- ✅ Detection completes successfully
- ✅ docker-compose.yml generated
- ✅ Folders created
- ✅ Can proceed with restore
- ✅ Restore uses detected configuration
- ✅ Final Nextcloud instance matches backup

**Verification:**
```bash
# After restore completes
docker-compose ps
# Should show running containers

docker exec nextcloud-app cat /var/www/html/config/config.php
# Should match backup configuration

# Test Nextcloud access
curl -I http://localhost:8080
# Should return 200 OK
```

### Test 10: Error Handling and Recovery

**Scenario:** Test error conditions

**Test Cases:**

a. **Missing config.php in backup**
   - Expected: Warning shown, workflow continues
   - Detection returns None, no dialog shown

b. **Corrupted config.php**
   - Expected: Parsing fails gracefully
   - User can still proceed with defaults

c. **Permission denied creating folders**
   - Expected: Clear error message
   - Instructions for manual creation

d. **Invalid backup format**
   - Expected: Extraction fails with clear message
   - User guided back to file selection

e. **Disk space issues**
   - Expected: Proper error handling
   - Cleanup of partial files

## Automated Test Script

### Basic Integration Test Runner

```bash
#!/bin/bash
# integration_test.sh

set -e

echo "=== Docker Compose Integration Tests ==="

# Test 1: Detection without compose file
echo "Test 1: No existing docker-compose.yml"
rm -f docker-compose.yml
# Run application and verify detection
# (Manual verification needed for GUI)

# Test 2: Detection with compose file
echo "Test 2: With existing docker-compose.yml"
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  test:
    image: nginx
EOF
# Verify file is detected

# Test 3: Folder creation
echo "Test 3: Folder creation"
rm -rf nextcloud-data db-data
mkdir -p test-dir
cd test-dir
# Run folder creation
# Verify folders exist

# Cleanup
cd ..
rm -rf test-dir docker-compose.yml

echo "✅ All tests completed"
```

## Performance Benchmarks

Expected performance metrics:

- **Config.php extraction**: < 1 second
- **Full config parsing**: < 0.1 seconds
- **Docker Compose detection**: < 0.5 seconds
- **Dialog display**: < 0.2 seconds
- **docker-compose.yml generation**: < 0.1 seconds
- **Folder creation**: < 0.5 seconds

## Test Results Template

```
Test Run: [Date]
Environment: [OS, Docker version, Python version]

| Test | Status | Notes |
|------|--------|-------|
| Test 1: Fresh Restore | ✅ PASS | |
| Test 2: With Existing Compose | ✅ PASS | |
| Test 3: Running Containers | ✅ PASS | |
| Test 4: MySQL Detection | ✅ PASS | |
| Test 5: SQLite Detection | ✅ PASS | |
| Test 6: Encrypted Backup | ✅ PASS | |
| Test 7: Config Parsing | ✅ PASS | |
| Test 8: Folder Creation | ✅ PASS | |
| Test 9: Full Workflow | ✅ PASS | |
| Test 10: Error Handling | ✅ PASS | |

Overall Result: [PASS/FAIL]
Issues Found: [None/List]
```

## Manual Testing Checklist

- [ ] UI appears correctly on different screen sizes
- [ ] Dialog is properly centered
- [ ] Text is readable and well-formatted
- [ ] Buttons respond to clicks
- [ ] File save dialog works correctly
- [ ] Error messages are clear and helpful
- [ ] Console output is informative
- [ ] Detection runs in background thread (UI doesn't freeze)
- [ ] Progress indicator shows during detection
- [ ] Can navigate back and forth between pages
- [ ] Detection state persists correctly
- [ ] Cleanup happens on error conditions

## Success Criteria

For the integration tests to pass:

1. ✅ All 10 test scenarios complete successfully
2. ✅ No crashes or unhandled exceptions
3. ✅ Dialog appears consistently after detection
4. ✅ Generated docker-compose.yml files are valid YAML
5. ✅ Folder creation works on different filesystems
6. ✅ Error handling is graceful and informative
7. ✅ Performance meets benchmarks
8. ✅ Works with all database types (SQLite, MySQL, PostgreSQL)
9. ✅ Handles both encrypted and unencrypted backups
10. ✅ Integration with existing restore workflow is seamless

## Known Limitations

- GUI testing requires manual interaction (no automated UI tests)
- Docker must be available for container detection
- Tkinter must be installed for dialog display
- Some tests require specific backup files to exist

## Future Test Improvements

- [ ] Automated GUI testing with pytest-qt or similar
- [ ] Mock Docker commands for testing without Docker
- [ ] Automated backup file generation for tests
- [ ] Performance profiling and optimization
- [ ] Cross-platform testing (Windows, macOS, Linux)
- [ ] Stress testing with large backups
- [ ] Concurrency testing with multiple restores
