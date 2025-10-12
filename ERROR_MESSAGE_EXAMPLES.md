# Error Message Examples - Database Type Detection

This document shows the exact error messages users will see after the improvements.

---

## Example 1: Detection Fails (config.php Missing)

### Console Output:
```
Detecting database type...
❌ Could not read config.php from container 'nextcloud-app'
   Error: cat: can't open '/var/www/html/config/config.php': No such file or directory
   Possible causes:
   • config.php file does not exist at /var/www/html/config/config.php
   • Insufficient permissions to read the file
   • Container is not running or not accessible
```

### Dialog Box:
```
╔════════════════════════════════════════════════════════════╗
║            Database Type Detection Failed                  ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  ❌ Could not automatically detect the database type      ║
║     from your Nextcloud container.                        ║
║                                                            ║
║  Possible reasons:                                         ║
║  • config.php file is missing or inaccessible             ║
║  • Container does not have the expected file structure    ║
║  • Permission issues reading the container filesystem     ║
║  • Network connectivity issues                            ║
║                                                            ║
║  📋 MANUAL SELECTION:                                      ║
║  Please select your database type:                        ║
║  • Yes = PostgreSQL (default)                             ║
║  • No = MySQL/MariaDB                                     ║
║  • Cancel = Abort backup and check configuration          ║
║                                                            ║
║  ℹ️ Note: SQLite databases are backed up automatically    ║
║     with the data folder.                                 ║
║                                                            ║
║  ⚠️ If you're unsure, click Cancel and check your         ║
║     Nextcloud config/config.php file to verify the        ║
║     'dbtype' setting.                                     ║
║                                                            ║
║  For help:                                                 ║
║  https://docs.nextcloud.com/server/latest/                ║
║  admin_manual/configuration_database/                      ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║              [  Yes  ]  [  No  ]  [ Cancel ]              ║
╚════════════════════════════════════════════════════════════╝
```

---

## Example 2: Unsupported Database Type Detected (e.g., Oracle)

### Console Output:
```
Detecting database type...
✓ Read config.php from container successfully
⚠️ Detected unsupported database type: 'oracle'
   Supported types: sqlite, sqlite3, pgsql, mysql, mariadb
   Please check your Nextcloud configuration.
```

### Dialog Box:
```
╔════════════════════════════════════════════════════════════╗
║               Unsupported Database Type                    ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  ❌ Database type 'oracle' is not supported.              ║
║                                                            ║
║  Supported database types:                                 ║
║  • MySQL / MariaDB                                         ║
║  • PostgreSQL                                              ║
║  • SQLite                                                  ║
║                                                            ║
║  Please check your Nextcloud configuration file            ║
║  (config/config.php) and verify the 'dbtype' setting.     ║
║                                                            ║
║  For help:                                                 ║
║  https://docs.nextcloud.com/server/latest/                ║
║  admin_manual/configuration_database/                      ║
║                                                            ║
║  ⚠️ Backup cannot proceed with an unsupported             ║
║     database type.                                        ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║                        [  OK  ]                           ║
╚════════════════════════════════════════════════════════════╝
```

**Result:** Returns to main menu, backup does not proceed.

---

## Example 3: Database Type 'unknown' from utility check

### Console Output:
```
Detecting database type...
User manually selected database type: MySQL/MariaDB
Checking for database dump utility...
```

### If utility returns 'unknown' (should not happen with validation, but handled):

### Dialog Box:
```
╔════════════════════════════════════════════════════════════╗
║          Database Type Detection Failed                    ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  ❌ DATABASE TYPE DETECTION FAILED                        ║
║                                                            ║
║  The database type 'unknown' is not recognized or not     ║
║  supported.                                                ║
║                                                            ║
║  Possible reasons:                                         ║
║  • config.php file is missing or corrupted                ║
║  • Database type is not supported (only MySQL/MariaDB,    ║
║    PostgreSQL, and SQLite are supported)                  ║
║  • Container is not accessible or not running             ║
║                                                            ║
║  What to do:                                               ║
║  1. Check your Nextcloud configuration file               ║
║     (config/config.php)                                   ║
║  2. Verify the 'dbtype' field contains one of:            ║
║     'mysql', 'pgsql', or 'sqlite'                         ║
║  3. Ensure your Nextcloud container is running:           ║
║     docker ps                                              ║
║  4. For help, see:                                         ║
║     https://docs.nextcloud.com/server/latest/             ║
║     admin_manual/configuration_database/                   ║
║                                                            ║
║  ⚠️ Backup cannot proceed until the database type is      ║
║     correctly detected.                                   ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║                        [  OK  ]                           ║
╚════════════════════════════════════════════════════════════╝
```

**Result:** Returns to main menu, backup does not proceed.

---

## Example 4: Successful Detection (for comparison)

### Console Output:
```
Detecting database type...
✓ Detected database type from container: pgsql
  Database configuration: {'dbtype': 'pgsql', 'dbname': 'nextcloud', 
                          'dbuser': 'nextcloud', 'dbhost': 'db'}
Checking for database dump utility...
✓ pg_dump utility found
Proceeding with backup...
```

**No error dialogs shown** - backup proceeds normally.

---

## Example 5: Container Timeout

### Console Output:
```
Detecting database type...
❌ Timeout reading config.php from container
   The container may be unresponsive or experiencing issues.
   Please check container status: docker ps
```

### Dialog Box:
(Same as Example 1 - Detection Fails)

The user is prompted to manually select database type or cancel to check configuration.

---

## Example 6: dbtype field missing from config.php

### Console Output:
```
Detecting database type...
✓ Read config.php from container successfully
❌ Could not find 'dbtype' field in config.php
   The configuration file may be corrupted or incomplete.
   Please verify the config.php file in your Nextcloud installation.
```

### Dialog Box:
(Same as Example 1 - Detection Fails)

The user is prompted to manually select database type or cancel to check configuration.

---

## Key Features of New Error Messages

### ✅ Clear Icons
- ❌ = Error/Failure
- ⚠️ = Warning
- ✓ = Success
- ℹ️ = Information
- 📋 = Action Required

### ✅ Structured Information
1. **What happened** - Clear statement of the problem
2. **Why it happened** - Possible reasons listed
3. **What to do** - Step-by-step resolution guide
4. **Where to get help** - Link to documentation

### ✅ User-Friendly Language
- No technical jargon without explanation
- Clear, conversational tone
- Actionable instructions
- Supportive, not accusatory

### ✅ Prevents Dead Ends
- Always provides next steps
- Never leaves user stuck
- Options to cancel and investigate
- Links to documentation

### ✅ Safety First
- Backup does not proceed with invalid configuration
- Returns safely to main menu on error
- No risk of partial/corrupted backups
- User must resolve issue before continuing

---

## Comparison: Old vs New

### OLD (Image 8 Reference):
```
╔══════════════════════════════════════════╗
║      Database Utility Required           ║
╠══════════════════════════════════════════╣
║                                          ║
║  Database utility 'unknown' is required  ║
║  but installation instructions are not   ║
║  available.                              ║
║                                          ║
║  Click OK after installing to retry,     ║
║  or Cancel to abort.                     ║
║                                          ║
╠══════════════════════════════════════════╣
║         [  OK  ]      [ Cancel ]         ║
╚══════════════════════════════════════════╝
```

**Problems:**
- ❌ What is "unknown"?
- ❌ Why is it unknown?
- ❌ What should I install?
- ❌ How do I install it?
- ❌ Where can I get help?
- ❌ No guidance at all

### NEW:
See Examples 1-3 above.

**Improvements:**
- ✅ Explains what went wrong
- ✅ Lists possible reasons
- ✅ Provides resolution steps
- ✅ Links to documentation
- ✅ Prevents backup until resolved
- ✅ Professional, helpful tone

---

## Impact on User Experience

### Before:
😞 Frustrated → Confused → Stuck → Abandon/Contact Support

### After:
😊 Informed → Guided → Resolved → Success or Know Where to Get Help

---

This completes the error message improvements for database type detection failures.
