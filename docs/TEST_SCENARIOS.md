# Test Scenarios for Database Detection and UI

## Overview
This document outlines test scenarios to verify the wizard correctly handles database detection and conditionally shows/hides UI elements.

## Scenario 1: Unencrypted SQLite Backup

**Setup:**
- Backup file: `nextcloud-backup.tar.gz` (unencrypted)
- config.php contains: `'dbtype' => 'sqlite3'`

**Expected Behavior:**

### Page 1
- User selects backup file
- Early detection runs immediately (no password needed)
- Console: "Early detection successful: sqlite"

### Page 2
- ✅ Title: "Step 3: Database Configuration" - centered
- ✅ Info frame about auto-detection - visible, centered
- ✅ SQLite message: "✓ SQLite Database Detected" - visible, centered, green background
- ❌ Warning label - HIDDEN
- ❌ Instruction labels - HIDDEN
- ❌ Database credential fields (name, user, password) - HIDDEN
- ✅ Admin credentials section - visible, centered

**Console Output:**
```
Early detection successful: sqlite
UI updated for database type: sqlite (is_sqlite=True)
```

---

## Scenario 2: Encrypted SQLite Backup

**Setup:**
- Backup file: `nextcloud-backup.tar.gz.gpg` (encrypted)
- Decryption password: `mypassword123`
- config.php contains: `'dbtype' => 'sqlite'`

**Expected Behavior:**

### Page 1
- User selects backup file
- User enters password
- User clicks "Next"
- `perform_extraction_and_detection()` runs
- Decrypts backup to temp file
- Extracts config.php
- Detects SQLite
- Cleans up temp files
- Console: "Decrypting backup for early detection..."
- Console: "Early detection successful: sqlite"

### Page 2
- ✅ Same as Scenario 1 - credentials HIDDEN
- ✅ SQLite message visible

**Console Output:**
```
Decrypting backup for early detection...
Backup decrypted successfully for early detection
Early detection successful: sqlite
Cleaned up temporary decrypted file
Database type detected before Page 2: sqlite
UI updated for database type: sqlite (is_sqlite=True)
```

---

## Scenario 3: Unencrypted PostgreSQL Backup

**Setup:**
- Backup file: `nextcloud-backup.tar.gz` (unencrypted)
- config.php contains: `'dbtype' => 'pgsql'`

**Expected Behavior:**

### Page 1
- User selects backup file
- Early detection runs immediately
- Console: "Early detection successful: pgsql"

### Page 2
- ✅ Title: "Step 3: Database Configuration" - centered
- ✅ Info frame about auto-detection - visible, centered
- ❌ SQLite message - HIDDEN
- ✅ Warning label - visible, centered, red text
- ✅ Instruction labels - visible, centered
- ✅ Database credential frame - visible, centered
  - ✅ Database Name field
  - ✅ Database User field
  - ✅ Database Password field
- ✅ Admin credentials section - visible, centered

**Console Output:**
```
Early detection successful: pgsql
Database config: {'dbtype': 'pgsql', 'dbname': 'nextcloud', 'dbuser': 'nextcloud', 'dbhost': 'postgres'}
UI updated for database type: pgsql (is_sqlite=False)
```

---

## Scenario 4: Encrypted MySQL Backup

**Setup:**
- Backup file: `nextcloud-backup.tar.gz.gpg` (encrypted)
- Decryption password: `secret123`
- config.php contains: `'dbtype' => 'mysql'`

**Expected Behavior:**

### Page 1
- User selects backup file
- User enters password
- User clicks "Next"
- Decryption and detection happen

### Page 2
- ✅ Same as Scenario 3 - credentials VISIBLE
- ❌ SQLite message HIDDEN

**Console Output:**
```
Decrypting backup for early detection...
Early detection successful: mysql
UI updated for database type: mysql (is_sqlite=False)
```

---

## Scenario 5: Back Navigation (SQLite → Page 1 → Page 2)

**Setup:**
- User has already been to Page 2 with SQLite detected
- User clicks "← Back" to Page 1

**Expected Behavior:**

### Going Back
- Detection state reset for encrypted backups
- Console: "Resetting detection - user navigating back to Page 1"

### Going Forward Again
- Detection runs again
- UI updated again
- SQLite message shown again

---

## Scenario 6: Back Navigation (PostgreSQL → Page 1 → Page 2)

**Setup:**
- User has already been to Page 2 with PostgreSQL detected
- User clicks "← Back" to Page 1

**Expected Behavior:**

### Going Back
- Detection state preserved (or reset for encrypted)

### Going Forward Again
- Detection runs again
- UI updated again
- Credential fields shown again

---

## Scenario 7: Invalid/Missing config.php

**Setup:**
- Backup file missing config.php

**Expected Behavior:**

### Page 1
- User selects backup file
- Detection fails
- Console: "Early detection: config.php not found in backup"

### Navigation to Page 2
- Warning shown: "Warning: Could not detect database type. Please verify credentials."
- ALL credential fields shown (default to PostgreSQL mode)

---

## Visual Verification Checklist

For each scenario, verify:

- [ ] All titles and headings are horizontally centered
- [ ] All descriptions and helper text are centered
- [ ] All form frames are centered with proper padding
- [ ] Input fields maintain proper width and alignment
- [ ] SQLite message is properly styled (green background, centered)
- [ ] Info frame is properly styled (blue background, centered)
- [ ] Navigation buttons are centered
- [ ] No widgets overlap or appear in wrong positions
- [ ] Window resizing maintains centering
- [ ] Scrolling works properly when content exceeds window height

---

## Automated Test Commands

```bash
# Syntax check
python3 -m py_compile nextcloud_restore_and_backup-v9.py

# Create test config files
echo "<?php \$CONFIG = array('dbtype' => 'sqlite3');" > /tmp/test_sqlite.php
echo "<?php \$CONFIG = array('dbtype' => 'pgsql', 'dbname' => 'test');" > /tmp/test_pgsql.php

# Test parsing (manual verification)
python3 -c "
import sys
sys.path.insert(0, '.')
# Would test here but requires tkinter
"
```

---

## Manual Test Procedure

1. **Setup**: Create test backup files with different database types
2. **Launch**: Run `python3 nextcloud_restore_and_backup-v9.py`
3. **Test Each Scenario**: Follow the expected behavior above
4. **Verify Centering**: Resize window, check all pages
5. **Check Console**: Verify console output matches expectations
6. **Screenshot**: Take screenshots of each page for documentation

---

## Expected Screenshots

### SQLite Detection (Page 2)
- Green box: "✓ SQLite Database Detected"
- No database credential fields visible
- Only admin credentials section shown

### PostgreSQL/MySQL Detection (Page 2)
- Red warning: "⚠️ Enter the database credentials..."
- Gray instructions visible
- All database credential fields visible
- Admin credentials section shown

### Centering Verification
- All elements aligned to center of window
- Proper spacing and padding maintained
- Responsive to window resize
