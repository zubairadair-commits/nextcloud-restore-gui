# Wizard Flow Diagram - Before and After

## BEFORE: Original Flow (Problem)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Page 1: Backup Selection & Password                                │
│                                                                     │
│ 1. User selects backup file                                        │
│    ├─ If UNENCRYPTED: Early detection runs → dbtype detected ✓     │
│    └─ If ENCRYPTED: Early detection SKIPPED → dbtype unknown ✗     │
│                                                                     │
│ 2. User enters password (if encrypted)                             │
│                                                                     │
│ 3. User clicks "Next" → Navigate to Page 2                         │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Page 2: Database Configuration                                     │
│                                                                     │
│ ❌ PROBLEM: For encrypted backups, dbtype is still unknown!        │
│                                                                     │
│ • SQLite users see unnecessary database credential fields          │
│ • Database Name, User, Password fields shown for ALL backups       │
│ • User must fill in fields even though they won't be used          │
│                                                                     │
│ User enters database credentials and admin credentials             │
│                                                                     │
│ User clicks "Next" → Navigate to Page 3                            │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Page 3: Container Configuration                                    │
│                                                                     │
│ User configures container settings                                 │
│                                                                     │
│ User clicks "Start Restore"                                        │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Restore Process                                                     │
│                                                                     │
│ 1. Extract backup                                                  │
│ 2. ✓ NOW detect database type from config.php (TOO LATE!)          │
│ 3. Create containers                                               │
│ 4. Copy files                                                      │
│ 5. Restore database                                                │
└─────────────────────────────────────────────────────────────────────┘
```

## AFTER: New Flow (Solution)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Page 1: Backup Selection & Password                                │
│                                                                     │
│ 1. User selects backup file                                        │
│    ├─ If UNENCRYPTED: Early detection runs → dbtype detected ✓     │
│    └─ If ENCRYPTED: Early detection skipped (password not ready)   │
│                                                                     │
│ 2. User enters password (if encrypted)                             │
│                                                                     │
│ 3. User clicks "Next"                                               │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 🎯 NEW: Extraction and Detection BEFORE Page 2                     │
│                                                                     │
│ ✓ Validate backup file exists                                      │
│ ✓ Validate password (if encrypted)                                 │
│ ✓ Show progress: "Extracting and detecting database type..."       │
│                                                                     │
│ For ENCRYPTED backups:                                             │
│   1. Decrypt backup to temporary file                              │
│   2. Extract config/config.php                                     │
│   3. Parse dbtype from config.php                                  │
│   4. Clean up temporary files                                      │
│                                                                     │
│ For UNENCRYPTED backups:                                           │
│   1. Extract config/config.php (if not already done)               │
│   2. Parse dbtype from config.php                                  │
│                                                                     │
│ ✓ Set detected_dbtype before rendering Page 2                      │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Page 2: Database Configuration                                     │
│                                                                     │
│ ✅ SOLUTION: Database type is NOW KNOWN!                           │
│                                                                     │
│ IF dbtype = 'sqlite' or 'sqlite3':                                 │
│   • Hide all database credential fields                            │
│   • Show message: "✓ SQLite Database Detected"                     │
│   • Show message: "No database credentials are needed"             │
│   • Only show Admin Credentials section                            │
│                                                                     │
│ IF dbtype = 'mysql' or 'pgsql':                                    │
│   • Show database credential fields (Name, User, Password)         │
│   • Show warning about matching original credentials               │
│   • Show Admin Credentials section                                 │
│                                                                     │
│ User enters required credentials                                   │
│                                                                     │
│ User clicks "Next" → Navigate to Page 3                            │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Page 3: Container Configuration                                    │
│                                                                     │
│ User configures container settings                                 │
│                                                                     │
│ User clicks "Start Restore"                                        │
└─────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Restore Process                                                     │
│                                                                     │
│ 1. Extract backup (if not already extracted)                       │
│ 2. Skip detection (already done!)                                  │
│ 3. Create containers (skip DB container for SQLite)                │
│ 4. Copy files                                                      │
│ 5. Restore database (appropriate method based on detected type)    │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Encrypted SQLite backups** | User sees database credential fields | User sees "No credentials needed" message |
| **Detection timing** | During restore (too late) | Before Page 2 (just in time) |
| **User experience** | Confusing - fill fields that won't be used | Clear - only see what's needed |
| **Validation** | Required fields even for SQLite | Skip database fields for SQLite |
| **Performance** | Extract backup twice (once for detection, once for restore) | Extract config.php once for detection |

## Edge Cases Handled

### Case 1: User goes back from Page 2 to Page 1
```
Page 2 → Back button → Page 1
  ↓
Reset detection for encrypted backups
(Allows user to correct password or change backup file)
  ↓
User clicks "Next" again → Re-detect with new password
```

### Case 2: User changes backup file on Page 1
```
Page 1: Select backup A (SQLite)
  ↓
browse_backup() → Detect SQLite → Set detected_dbtype
  ↓
User selects backup B (PostgreSQL)
  ↓
browse_backup() → Detect PostgreSQL → Update detected_dbtype
  ↓
User clicks "Next" → Use PostgreSQL detection
```

### Case 3: Detection fails
```
Page 1 → User clicks "Next"
  ↓
perform_extraction_and_detection()
  ↓
Detection fails (invalid backup, wrong password, etc.)
  ↓
Show warning: "Could not detect database type. Please verify credentials."
  ↓
Allow navigation to Page 2 (show all fields as fallback)
```

## Code Flow

### 1. wizard_navigate(direction)
```python
if wizard_page == 2 and direction == -1:
    # Going back to Page 1 - reset detection for encrypted backups
    if detected_dbtype and backup_path.endswith('.gpg'):
        reset_detection()

if wizard_page == 1 and direction == 1:
    # Going forward to Page 2 - perform detection
    if not perform_extraction_and_detection():
        return  # Don't navigate if validation fails
```

### 2. perform_extraction_and_detection()
```python
# Validate backup file and password
# Show progress message
# Call early_detect_database_type_from_backup(backup_path, password)
# Set detected_dbtype and db_auto_detected
# Clear progress message
# Return True/False
```

### 3. early_detect_database_type_from_backup(backup_path, password=None)
```python
if backup_path.endswith('.gpg'):
    if not password:
        return None, None
    
    # Decrypt to temporary file
    decrypt_file_gpg(backup_path, temp_file, password)
    backup_to_extract = temp_file
else:
    backup_to_extract = backup_path

# Extract config/config.php
# Parse dbtype
# Clean up temporary files
# Return (dbtype, db_config)
```

### 4. create_wizard_page2(parent)
```python
# Create all UI widgets
# Store credential widgets in self.db_credential_widgets
# Create SQLite message (hidden by default)

if self.detected_dbtype:
    self.update_database_credential_ui(self.detected_dbtype)
```

### 5. update_database_credential_ui(dbtype)
```python
is_sqlite = dbtype.lower() in ['sqlite', 'sqlite3']

if is_sqlite:
    # Hide credential widgets
    # Show SQLite message
else:
    # Show credential widgets
    # Hide SQLite message
```
