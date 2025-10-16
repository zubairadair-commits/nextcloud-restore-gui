# Automated Restore Process Flow Diagram

## Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER STARTS RESTORE                         │
│  (Selects backup, enters password & credentials)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: BACKUP EXTRACTION (5-20%)                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • If encrypted (.gpg): Decrypt with GPG                 │   │
│  │ • Extract tar.gz to temporary directory                 │   │
│  │ • Verify extraction successful                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: DATABASE CONTAINER SETUP (20-45%)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Check if database container exists                    │   │
│  │ • If not: Create PostgreSQL container                   │   │
│  │   - Name: nextcloud-db                                  │   │
│  │   - Credentials from user input                         │   │
│  │   - Port: 5432                                          │   │
│  │ • Wait 5 seconds for container to be ready              │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: NEXTCLOUD CONTAINER SETUP (30-35%)                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Check if Nextcloud container exists                   │   │
│  │ • If not: Create Nextcloud container                    │   │
│  │   - Name: nextcloud-app (or custom)                     │   │
│  │   - Linked to database: --link nextcloud-db:db         │   │
│  │   - Port: 9000 (or custom)                              │   │
│  │ • Wait 5 seconds for container to be ready              │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: FILE RESTORATION (50%)                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ For each folder (config, data, apps, custom_apps):     │   │
│  │                                                          │   │
│  │ • Remove existing folder in container:                  │   │
│  │   docker exec rm -rf /var/www/html/[folder]            │   │
│  │                                                          │   │
│  │ • Copy backup folder to container:                      │   │
│  │   docker cp backup/[folder]/. container:/var/www/html/ │   │
│  │                                                          │   │
│  │ Result: Files in correct locations                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: DATABASE IMPORT (70%)                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Check if nextcloud-db.sql exists in backup            │   │
│  │ • Import SQL file into PostgreSQL:                      │   │
│  │   docker exec -i nextcloud-db psql ... < backup.sql    │   │
│  │ • Capture stdout/stderr for error details               │   │
│  │ • Show "this may take a few minutes" message            │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: DATABASE VALIDATION (70%)                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Run: docker exec ... psql ... -c '\dt'                │   │
│  │ • Check output for "oc_" table prefix                   │   │
│  │ • If not found: Show warning                            │   │
│  │ • If found: Confirm success                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: CONFIG.PHP UPDATE (75%)                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Create PHP script in container (/tmp/update_config)   │   │
│  │ • Update config.php with:                               │   │
│  │   - dbtype = 'pgsql'                                    │   │
│  │   - dbhost = 'nextcloud-db' (container name)            │   │
│  │   - dbname = [user provided]                            │   │
│  │   - dbuser = [user provided]                            │   │
│  │   - dbpassword = [user provided]                        │   │
│  │ • Execute PHP script in container                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: FILE VALIDATION (85%)                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Validate config.php exists:                           │   │
│  │   docker exec ... test -f .../config/config.php         │   │
│  │                                                          │   │
│  │ • Validate data folder exists:                          │   │
│  │   docker exec ... test -d .../data                      │   │
│  │                                                          │   │
│  │ • If any missing: FAIL restore with error               │   │
│  │ • If all present: Continue                              │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 9: PERMISSION SETTING (90%)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Set ownership on files:                               │   │
│  │   docker exec ... chown -R www-data:www-data            │   │
│  │     /var/www/html/config                                │   │
│  │     /var/www/html/data                                  │   │
│  │                                                          │   │
│  │ • If fails: Show warning but continue                   │   │
│  │ • If succeeds: Log success                              │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 10: CONTAINER RESTART (95%)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Restart Nextcloud container:                          │   │
│  │   docker restart nextcloud-app                          │   │
│  │                                                          │   │
│  │ • Wait 3 seconds for container to start                 │   │
│  │                                                          │   │
│  │ • If fails: Show warning but continue                   │   │
│  │ • If succeeds: Log success                              │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 11: COMPLETION (100%)                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Clean up temporary extraction directory               │   │
│  │ • Show success message to user                          │   │
│  │ • Display any warnings that occurred                    │   │
│  │ • Provide access URL: http://localhost:[port]           │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              RESTORE COMPLETE - NEXTCLOUD READY!                │
│         User can access at http://localhost:9000                │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌──────────────┐
│  Any Step    │
└──────┬───────┘
       │
       │ Error Occurs?
       │
       ├─── NO ──→ Continue to next step
       │
       └─── YES ─→ ┌────────────────────────────────────┐
                   │  Is it a CRITICAL error?          │
                   └───────┬────────────────────────────┘
                           │
                           ├─── YES (Critical) ──→ ┌──────────────────────┐
                           │                        │ • Stop restore       │
                           │                        │ • Set progress to 0% │
                           │                        │ • Show red error     │
                           │                        │ • Give specific fix  │
                           │                        └──────────────────────┘
                           │
                           └─── NO (Warning) ──→ ┌──────────────────────┐
                                                 │ • Continue restore   │
                                                 │ • Show orange warning│
                                                 │ • Log issue          │
                                                 │ • Complete restore   │
                                                 └──────────────────────┘
```

## Critical vs Non-Critical Errors

### Critical Errors (Stop Restore)
- ❌ Backup decryption failed
- ❌ Backup extraction failed
- ❌ Cannot start database container
- ❌ Cannot start Nextcloud container
- ❌ File copy failed
- ❌ Database import failed
- ❌ config.php not found after restore
- ❌ data folder not found after restore

### Non-Critical Errors (Show Warning, Continue)
- ⚠️ Database validation unclear
- ⚠️ Config.php update failed
- ⚠️ Permission setting failed
- ⚠️ Container restart failed
- ⚠️ No database backup file found

## Container Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Host                         │
│                                                          │
│  ┌─────────────────────┐      ┌──────────────────────┐ │
│  │  nextcloud-app      │      │   nextcloud-db       │ │
│  │  (Nextcloud)        │◄─────┤   (PostgreSQL)       │ │
│  │                     │ link │                      │ │
│  │  Port: 9000 → 80    │      │   Port: 5432         │ │
│  │                     │      │                      │ │
│  │  /var/www/html/     │      │   Database:          │ │
│  │  ├── config/        │      │   - nextcloud        │ │
│  │  │   └── config.php │      │   User: nextcloud    │ │
│  │  ├── data/          │      │   Pass: [from user]  │ │
│  │  ├── apps/          │      │                      │ │
│  │  └── custom_apps/   │      │                      │ │
│  └─────────────────────┘      └──────────────────────┘ │
│           ▲                              ▲              │
└───────────┼──────────────────────────────┼──────────────┘
            │                              │
            │                              │
         docker cp                    docker exec
         (file copy)                  (db import)
            │                              │
            │                              │
┌───────────┴──────────────────────────────┴──────────────┐
│           Backup Archive Contents                       │
│  ┌────────────────────────────────────────────────┐    │
│  │  nextcloud-backup-YYYYMMDD_HHMMSS.tar.gz.gpg  │    │
│  │  (or .tar.gz)                                  │    │
│  │                                                │    │
│  │  Contents:                                     │    │
│  │  ├── config/                                   │    │
│  │  │   └── config.php (original credentials)    │    │
│  │  ├── data/                                     │    │
│  │  │   └── [user files]                         │    │
│  │  ├── apps/                                     │    │
│  │  ├── custom_apps/                              │    │
│  │  └── nextcloud-db.sql (database dump)         │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

```
Backup File → Decrypt → Extract → Temporary Directory
                                        │
                 ┌──────────────────────┼──────────────────────┐
                 │                      │                      │
                 ▼                      ▼                      ▼
          config folder           data folder           nextcloud-db.sql
                 │                      │                      │
                 │ docker cp            │ docker cp            │ docker exec
                 ▼                      ▼                      ▼
         /var/www/html/config  /var/www/html/data      PostgreSQL Database
                 │                      │                      │
                 └──────────────────────┴──────────────────────┘
                                        │
                                        ▼
                              Nextcloud Container
                                   (Running)
```

## Progress Percentage Breakdown

| Percentage | Step                          | Description                      |
|-----------|-------------------------------|----------------------------------|
| 0%        | Start                         | User clicks "Start Restore"      |
| 5%        | Decrypting                    | If encrypted, decrypt backup     |
| 10-20%    | Extracting                    | Extract tar.gz archive           |
| 20%       | Extraction Complete           | Ready for container setup        |
| 30%       | Starting Nextcloud Container  | Create/start Nextcloud           |
| 35%       | Nextcloud Container Ready     | Container running                |
| 40%       | Starting DB Container         | Create/start PostgreSQL          |
| 45%       | DB Container Ready            | Container running                |
| 50%       | Copying Files                 | Docker cp for all folders        |
| 70%       | Restoring Database            | Import SQL file                  |
| 75%       | Updating Configuration        | Update config.php                |
| 85%       | Validating Files              | Check required files exist       |
| 90%       | Setting Permissions           | chown www-data:www-data          |
| 95%       | Restarting Container          | docker restart                   |
| 100%      | Complete                      | Success message shown            |

## Validation Points

```
┌─────────────────────────────────────────────────────────────┐
│                    Validation Checkpoints                   │
└─────────────────────────────────────────────────────────────┘

Checkpoint 1: After Extraction
  ✓ Backup extracted successfully
  ✓ Extract directory exists
  ✓ At least config or data folder present

Checkpoint 2: After Container Start
  ✓ Database container running
  ✓ Nextcloud container running
  ✓ Containers linked (if new)

Checkpoint 3: After File Copy
  ✓ config folder copied
  ✓ data folder copied
  ✓ No errors during copy

Checkpoint 4: After Database Import
  ✓ SQL file imported without errors
  ✓ Tables exist in database (oc_ prefix)
  ✓ Can query database

Checkpoint 5: After Config Update
  ✓ config.php updated (or warning shown)
  ✓ Database credentials set

Checkpoint 6: After File Validation
  ✓ config.php exists in container
  ✓ data folder exists in container
  ✓ Files readable by container

Checkpoint 7: After Permission Setting
  ✓ Permissions set (or warning shown)
  ✓ Files owned by www-data

Checkpoint 8: After Container Restart
  ✓ Container restarted (or warning shown)
  ✓ Container running
  ✓ Ready to serve requests
```

## Success Criteria

For restore to be considered successful:

1. ✅ All files copied to correct container paths
2. ✅ Database imported with all tables
3. ✅ config.php exists and is readable
4. ✅ data folder exists and is readable
5. ✅ Nextcloud container is running
6. ✅ Database container is running
7. ✅ No critical errors occurred

Warnings are acceptable if non-critical (permissions, restart).
