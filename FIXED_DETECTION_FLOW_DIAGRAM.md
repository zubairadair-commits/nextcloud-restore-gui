# Fixed Database Detection Flow Diagram

## Complete Wizard Flow with Correct Detection Timing

```
┌─────────────────────────────────────────────────────────────────┐
│                         Landing Page                            │
│                                                                 │
│              [Create New Backup] [Restore Backup]               │
│                                                                 │
│                   User clicks "Restore Backup"                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Page 1: Backup Selection                   │
│                                                                 │
│  Step 1: Select Backup Archive                                 │
│  ┌─────────────────────────────────────────────┐                │
│  │ [                                          ]│                │
│  └─────────────────────────────────────────────┘                │
│              [Browse...]  ← User clicks                         │
│                                                                 │
│  ┌─────────────────────────────────────────────┐                │
│  │ /home/user/backup.tar.gz.gpg  ← File selected               │
│  └─────────────────────────────────────────────┘                │
│                                                                 │
│  ✅ NO DATABASE DETECTION OCCURS HERE                           │
│  ✅ NO ERROR MESSAGES DISPLAYED                                 │
│                                                                 │
│  Step 2: Decryption Password                                   │
│  ┌─────────────────────────────────────────────┐                │
│  │ ••••••••  ← User enters password                             │
│  └─────────────────────────────────────────────┘                │
│                                                                 │
│  ✅ STILL NO DETECTION - WAITING FOR "NEXT"                     │
│                                                                 │
│                    [Next →]  ← User clicks                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ wizard_navigate(direction=1)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│           perform_extraction_and_detection()                    │
│                                                                 │
│  1. Validate backup file exists                                 │
│     ├─ ✅ File exists → Continue                                │
│     └─ ❌ File missing → Error, stay on Page 1                  │
│                                                                 │
│  2. Validate password for encrypted backups                     │
│     ├─ ✅ Password provided → Continue                          │
│     └─ ❌ Password missing → Error, stay on Page 1              │
│                                                                 │
│  3. Call early_detect_database_type_from_backup()               │
│     │                                                           │
│     ├─ If .tar.gz.gpg (encrypted):                             │
│     │   ├─ Decrypt to temporary file                           │
│     │   │  ├─ ✅ Success → Continue                             │
│     │   │  └─ ❌ Fail → Error, stay on Page 1                   │
│     │   └─ Extract config/config.php from decrypted file       │
│     │                                                           │
│     └─ If .tar.gz (unencrypted):                               │
│         └─ Extract config/config.php directly                  │
│                                                                 │
│  4. Parse config.php for database type                          │
│     ├─ Found 'sqlite' or 'sqlite3' → Set detected_dbtype       │
│     ├─ Found 'mysql' → Set detected_dbtype                     │
│     ├─ Found 'pgsql' → Set detected_dbtype                     │
│     └─ Not found → Warning, allow navigation                   │
│                                                                 │
│  5. Clean up temporary files                                    │
│                                                                 │
│  6. Return True to allow navigation to Page 2                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Page 2: Database Configuration                 │
│                                                                 │
│  ℹ️ Database Type Auto-Detection                                │
│  The restore process will automatically detect your database   │
│  type from config.php                                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ IF detected_dbtype == 'sqlite':                         │   │
│  │                                                         │   │
│  │   ✓ SQLite Database Detected                           │   │
│  │                                                         │   │
│  │   No database credentials are needed for SQLite.       │   │
│  │   The database is stored as a single file within       │   │
│  │   your backup.                                         │   │
│  │                                                         │   │
│  │   [Database credential fields are HIDDEN]              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ IF detected_dbtype == 'mysql' or 'pgsql':               │   │
│  │                                                         │   │
│  │   ⚠️ Enter database credentials from ORIGINAL setup     │   │
│  │                                                         │   │
│  │   Database Name:    [nextcloud           ]             │   │
│  │   Database User:    [nextcloud           ]             │   │
│  │   Database Password:[••••••••            ]             │   │
│  │                                                         │   │
│  │   [Database credential fields are SHOWN]               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Step 4: Nextcloud Admin Credentials                           │
│  Admin Username:  [admin                ]                      │
│  Admin Password:  [••••••               ]                      │
│                                                                 │
│                [← Back]  [Next →]                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                Page 3: Container Configuration                  │
│                                                                 │
│  [Container settings and restore button]                        │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow Diagrams

### Error Case 1: Missing Password

```
Page 1: User selects encrypted backup
        ↓
User leaves password field empty
        ↓
User clicks "Next"
        ↓
perform_extraction_and_detection()
        ├─ Validate backup file: ✅ OK
        ├─ Validate password: ❌ FAIL (empty)
        └─ Return False
        ↓
❌ Error displayed: "Please enter decryption password for encrypted backup"
        ↓
User stays on Page 1 to enter password
```

### Error Case 2: Wrong Password

```
Page 1: User selects encrypted backup
        ↓
User enters incorrect password
        ↓
User clicks "Next"
        ↓
perform_extraction_and_detection()
        ├─ Validate backup file: ✅ OK
        ├─ Validate password: ✅ OK (present)
        ├─ Attempt decrypt: ❌ FAIL (wrong password)
        └─ Exception caught
        ↓
❌ Error displayed: "Failed to decrypt backup: gpg decryption failed"
        ↓
User stays on Page 1 to correct password
```

### Error Case 3: Invalid Backup File

```
Page 1: User selects invalid or corrupt file
        ↓
User enters password (if prompted)
        ↓
User clicks "Next"
        ↓
perform_extraction_and_detection()
        ├─ Validate backup file: ❌ FAIL (not found or invalid)
        └─ Return False
        ↓
❌ Error displayed: "Please select a valid backup archive file"
        ↓
User stays on Page 1 to select correct file
```

## Key Improvements Illustrated

### Before: Premature Detection

```
browse_backup()
    ↓
User selects file
    ↓
❌ IMMEDIATE detection attempt (NO PASSWORD YET)
    ↓
Fails for encrypted files
    ↓
Console: "skipping early detection" (confusing!)
    ↓
User enters password later
    ↓
Detection happens again during navigation
```

**Problems:**
- Confusing double detection attempt
- Error messages before password entry
- Unclear flow

### After: Correct Detection

```
browse_backup()
    ↓
User selects file
    ↓
✅ NO detection attempt
    ↓
User enters password
    ↓
User clicks "Next"
    ↓
✅ SINGLE detection attempt with password
    ↓
Success or clear error
```

**Benefits:**
- Single, clear detection point
- No premature errors
- Predictable flow

## Detection Function Call Stack

### For Encrypted Backup with SQLite:

```
1. wizard_navigate(direction=1)
   └─ 2. perform_extraction_and_detection()
      ├─ 3. Validate backup_path exists
      ├─ 4. Validate password provided
      └─ 5. early_detect_database_type_from_backup(backup_path, password)
         ├─ 6. Check if .gpg extension
         ├─ 7. decrypt_file_gpg(backup_path, temp_file, password)
         ├─ 8. Extract config/config.php from temp_file
         ├─ 9. parse_config_php_dbtype(config_path)
         │  └─ Returns: ('sqlite', {config_dict})
         ├─ 10. Normalize 'sqlite3' → 'sqlite'
         └─ 11. Return ('sqlite', {config_dict})
      └─ 12. Set self.detected_dbtype = 'sqlite'
      └─ 13. Return True
   └─ 14. show_wizard_page(2)
      └─ 15. create_wizard_page2(frame)
         └─ 16. update_database_credential_ui('sqlite')
            └─ 17. Hide credential fields, show SQLite message
```

## Timing Comparison

### BEFORE (Incorrect):

```
Time    Event                           Detection Attempt
────────────────────────────────────────────────────────────
T0      User opens wizard               -
T1      User clicks Browse              -
T2      User selects file               ❌ ATTEMPT 1 (no password)
T3      User enters password            -
T4      User clicks Next                ✅ ATTEMPT 2 (with password)
T5      Navigate to Page 2              -
```

### AFTER (Correct):

```
Time    Event                           Detection Attempt
────────────────────────────────────────────────────────────
T0      User opens wizard               -
T1      User clicks Browse              -
T2      User selects file               ✅ NO ATTEMPT (deferred)
T3      User enters password            ✅ NO ATTEMPT (still deferred)
T4      User clicks Next                ✅ SINGLE ATTEMPT (with password)
T5      Navigate to Page 2              -
```

## Summary

The fixed implementation ensures:

✅ Database detection deferred until password entry  
✅ Single detection point after validation  
✅ No premature error messages  
✅ Clear error handling for all failure cases  
✅ SQLite users never see unnecessary fields  
✅ Responsive, centered UI on all pages  

The flow is now clean, predictable, and user-friendly.
