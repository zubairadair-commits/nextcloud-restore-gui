# Database Auto-Detection Flow Diagram

## Visual Flow Chart

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESTORE WORKFLOW START                       │
│                   User clicks "Start Restore"                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: BACKUP EXTRACTION (5-20%)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Decrypt if .gpg encrypted (5-10%)                      │  │
│  │ • Extract tar.gz archive (10-20%)                        │  │
│  │ • Creates temporary directory with backup contents       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  🆕 STEP 2: DATABASE TYPE DETECTION (18%)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Locate config/config.php in extracted backup           │  │
│  │ • Parse config.php using regex                           │  │
│  │ • Extract 'dbtype' field                                 │  │
│  │ • Extract database configuration (name, user, host)      │  │
│  │                                                           │  │
│  │ Result: dbtype = 'sqlite' | 'pgsql' | 'mysql' | None    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                   ┌─────────┴─────────┐
                   │   Detection OK?   │
                   └─────────┬─────────┘
                             │
                  ┌──────────┼──────────┐
                  │          │          │
                YES         NO       MISSING
                  │          │          │
                  ▼          ▼          ▼
         ┌────────────┐ ┌─────────┐ ┌──────────────┐
         │ Show Type  │ │ Warning │ │ Warning &    │
         │ to User    │ │ Message │ │ Use Default  │
         │            │ │         │ │ (PostgreSQL) │
         └─────┬──────┘ └────┬────┘ └──────┬───────┘
               │             │              │
               └─────────────┼──────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: CONTAINER SETUP (20-50%)                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │  IF dbtype == 'sqlite':                                  │  │
│  │    ✗ Skip database container (not needed)                │  │
│  │    ✓ Start Nextcloud container only                      │  │
│  │                                                           │  │
│  │  ELSE (pgsql or mysql):                                  │  │
│  │    ✓ Start database container (PostgreSQL/MySQL)         │  │
│  │    ✓ Start Nextcloud container (linked to DB)           │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: FILE COPY (50-70%)                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Copy config folder                                      │  │
│  │ • Copy data folder (includes .db for SQLite)             │  │
│  │ • Copy apps folder                                        │  │
│  │ • Copy custom_apps folder                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  🆕 STEP 5: DATABASE RESTORE - BRANCHING LOGIC (70%)           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  BRANCH: dbtype == 'sqlite'                              │  │
│  │  ────────────────────────────                            │  │
│  │  Method: restore_sqlite_database()                       │  │
│  │  • Verify .db file exists in data folder                 │  │
│  │  • No import needed (already copied with data)           │  │
│  │  • Validate file exists in container                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  BRANCH: dbtype == 'pgsql'                               │  │
│  │  ────────────────────────────                            │  │
│  │  Method: restore_postgresql_database()                   │  │
│  │  • Find nextcloud-db.sql in backup                       │  │
│  │  • Import using: psql -U user -d dbname                  │  │
│  │  • Set PGPASSWORD environment variable                   │  │
│  │  • Pipe SQL file to psql stdin                           │  │
│  │  • Validate tables exist (check for 'oc_' prefix)        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  BRANCH: dbtype == 'mysql'                               │  │
│  │  ────────────────────────────                            │  │
│  │  Method: restore_mysql_database()                        │  │
│  │  • Find nextcloud-db.sql in backup                       │  │
│  │  • Import using: mysql -u user -p[password] dbname       │  │
│  │  • Pipe SQL file to mysql stdin                          │  │
│  │  • Validate tables exist (check for 'oc_' prefix)        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  🆕 STEP 6: UPDATE CONFIG.PHP (75%)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Update database type with detected value               │  │
│  │   (Previously hardcoded to 'pgsql')                      │  │
│  │ • Update database host                                   │  │
│  │ • Update database credentials                            │  │
│  │ • Uses detected dbtype parameter                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: VALIDATION & PERMISSIONS (85-95%)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Validate config.php exists                             │  │
│  │ • Validate data folder exists                            │  │
│  │ • Set file ownership (chown www-data)                    │  │
│  │ • Restart Nextcloud container                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  RESTORE COMPLETE (100%)                        │
│               User can access Nextcloud instance                │
└─────────────────────────────────────────────────────────────────┘
```

## Decision Tree for Database Detection

```
                    Start Detection
                          │
                          ▼
              ┌───────────────────────┐
              │ config.php exists?    │
              └───────────┬───────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
             YES                     NO
              │                       │
              ▼                       ▼
    ┌─────────────────┐    ┌────────────────────┐
    │ Parse dbtype    │    │ Show Warning:      │
    │ from config.php │    │ "Cannot detect DB" │
    └────────┬────────┘    │ Fallback: pgsql    │
             │             └────────────────────┘
             ▼
    ┌─────────────────┐
    │ dbtype found?   │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
   YES               NO
    │                 │
    ▼                 ▼
┌─────────┐  ┌────────────────────┐
│ dbtype  │  │ Show Warning:      │
│ value?  │  │ "Cannot parse DB"  │
└────┬────┘  │ Fallback: pgsql    │
     │       └────────────────────┘
     │
┌────┴─────────┬──────────┐
│              │          │
▼              ▼          ▼
sqlite       pgsql      mysql
│              │          │
▼              ▼          ▼
Use .db      Use SQL    Use SQL
file         dump +     dump +
             psql       mysql
```

## Code Flow with New Functions

```
_restore_auto_thread()
  │
  ├─→ auto_extract_backup()         # Existing function
  │     └─→ Returns: extract_dir
  │
  ├─→ 🆕 detect_database_type()     # NEW function
  │     ├─→ parse_config_php_dbtype()  # NEW standalone function
  │     └─→ Returns: (dbtype, db_config)
  │
  ├─→ 🆕 show_db_detection_message() # NEW function
  │     └─→ Displays detection info to user
  │
  ├─→ ensure_db_container()          # Existing - modified logic
  │     └─→ Skipped if dbtype == 'sqlite'
  │
  ├─→ ensure_nextcloud_container()   # Existing function
  │
  ├─→ Copy files (loop)              # Existing function
  │
  ├─→ 🆕 Database restore branching  # NEW logic
  │     │
  │     ├─→ 🆕 restore_sqlite_database()     # NEW function
  │     │     └─→ Verify .db file
  │     │
  │     ├─→ 🆕 restore_postgresql_database() # NEW function
  │     │     └─→ Import with psql
  │     │
  │     └─→ 🆕 restore_mysql_database()      # NEW function
  │           └─→ Import with mysql
  │
  ├─→ 🆕 update_config_php()         # Modified - now accepts dbtype param
  │     └─→ Uses detected dbtype instead of hardcoded 'pgsql'
  │
  ├─→ Validation                     # Existing function
  │
  └─→ Complete                       # Existing function
```

## Key Improvements

### 1. Automatic Detection
- **Before**: Assumed PostgreSQL for all restores
- **After**: Detects actual database type from backup

### 2. Multi-Database Support
- **Before**: Only PostgreSQL supported
- **After**: SQLite, PostgreSQL, MySQL/MariaDB all supported

### 3. Smart Container Management
- **Before**: Always created PostgreSQL container
- **After**: Skips database container for SQLite (not needed)

### 4. Correct Restore Method
- **Before**: Always used psql command
- **After**: Uses appropriate tool (none for SQLite, psql for PostgreSQL, mysql for MySQL)

### 5. User Communication
- **Before**: No visibility into database type
- **After**: Shows detected type and configuration to user

### 6. Error Handling
- **Before**: Would fail on non-PostgreSQL backups
- **After**: Falls back gracefully, warns user if detection fails

## Testing Scenarios Covered

✅ PostgreSQL backup with config.php
✅ MySQL backup with config.php
✅ SQLite backup with config.php
✅ Backup missing config.php (fallback)
✅ config.php without dbtype (fallback)
✅ Single and double quote handling
✅ Various database credential formats
