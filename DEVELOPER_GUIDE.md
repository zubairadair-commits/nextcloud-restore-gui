# Developer Guide - Database Detection & UI Logic

## Quick Reference

### Where Database Detection Happens

1. **Page 1 → Page 2 Navigation**: `wizard_navigate()` (line 843)
2. **Extraction & Detection**: `perform_extraction_and_detection()` (line 880)
3. **Early Detection**: `early_detect_database_type_from_backup()` (line 1481)
4. **Config Parsing**: `parse_config_php_dbtype()` (line 101)

### Where UI Updates Happen

1. **Page Creation**: `create_wizard_page2()` (line 650)
2. **UI Update Logic**: `update_database_credential_ui()` (line 1604)

---

## Key Data Structures

### Instance Variables

```python
# Detection state
self.detected_dbtype = None           # 'sqlite', 'pgsql', 'mysql', or None
self.detected_db_config = None        # Dict with dbname, dbuser, dbhost
self.db_auto_detected = False         # True if detection was successful

# UI references
self.db_credential_packed_widgets = [] # List of packed warning/instruction labels
self.db_credential_frame = None        # Frame containing grid widgets
self.db_sqlite_message_label = None    # SQLite informational message label
```

### Widget Structure

```
Page 2 Layout:
├── Info Frame (auto-detection explanation) - always visible
├── SQLite Message - shown for SQLite, hidden otherwise
├── Warning Label (packed) - hidden for SQLite, shown otherwise
├── Instruction Label 1 (packed) - hidden for SQLite, shown otherwise
├── Instruction Label 2 (packed) - hidden for SQLite, shown otherwise
├── DB Frame (packed, contains grid widgets) - hidden for SQLite, shown otherwise
│   ├── DB Name Label (grid)
│   ├── DB Name Entry (grid)
│   ├── DB Name Hint (grid)
│   ├── DB User Label (grid)
│   ├── DB User Entry (grid)
│   ├── DB User Hint (grid)
│   ├── DB Password Label (grid)
│   ├── DB Password Entry (grid)
│   └── DB Password Hint (grid)
└── Admin Frame - always visible
    ├── Admin Username (grid)
    └── Admin Password (grid)
```

---

## Critical Rules

### Geometry Manager Usage

⚠️ **NEVER mix pack() and grid() on the same widget!**

✅ **Correct:**
- Use `pack_forget()` / `pack()` for packed widgets
- Hide parent frame to hide grid widgets within it

❌ **Incorrect:**
- Calling `grid_remove()` on a packed widget
- Calling `pack_forget()` on a grid widget

### Widget Visibility Rules

**For SQLite:**
```python
# Hide these
- warning_label (pack_forget)
- instruction_label1 (pack_forget)
- instruction_label2 (pack_forget)
- db_credential_frame (pack_forget)

# Show these
- db_sqlite_message_label (pack)
- info_frame (already visible)
- admin_frame (already visible)
```

**For MySQL/PostgreSQL:**
```python
# Show these
- warning_label (pack)
- instruction_label1 (pack)
- instruction_label2 (pack)
- db_credential_frame (pack)

# Hide these
- db_sqlite_message_label (pack_forget)

# Already visible
- info_frame
- admin_frame
```

---

## Common Tasks

### Adding a New Database Type

1. Update `parse_config_php_dbtype()` if needed
2. Update `is_sqlite` logic in `update_database_credential_ui()`
3. Test extraction and parsing
4. Update documentation

### Changing UI Layout

1. Ensure consistent use of geometry managers
2. Update widget references in `create_wizard_page2()`
3. Test hide/show logic still works
4. Verify centering maintained

### Debugging Detection Issues

1. Check console output for "Early detection..." messages
2. Verify backup contains config/config.php
3. Test with both encrypted and unencrypted backups
4. Check regex patterns in `parse_config_php_dbtype()`

---

## Testing Checklist

### Unit Tests
- [ ] Parse SQLite config (sqlite, sqlite3)
- [ ] Parse PostgreSQL config
- [ ] Parse MySQL config
- [ ] Handle missing config.php
- [ ] Handle malformed config.php

### Integration Tests
- [ ] Unencrypted SQLite backup
- [ ] Encrypted SQLite backup
- [ ] Unencrypted PostgreSQL backup
- [ ] Encrypted PostgreSQL backup
- [ ] Unencrypted MySQL backup
- [ ] Encrypted MySQL backup

### UI Tests
- [ ] SQLite: Credentials hidden, message shown
- [ ] PostgreSQL: Credentials shown, message hidden
- [ ] MySQL: Credentials shown, message hidden
- [ ] Back navigation resets correctly
- [ ] Forward navigation applies detection
- [ ] Window resize maintains centering

---

## Code Flow Diagram

```
User Action: Select Backup & Click "Next"
    │
    ▼
wizard_navigate(direction=1)
    │
    ├─> save_wizard_page_data()
    │
    └─> perform_extraction_and_detection()
            │
            ├─> Validate backup file exists
            ├─> Validate password (if encrypted)
            │
            └─> early_detect_database_type_from_backup(backup_path, password)
                    │
                    ├─> If .gpg: decrypt_file_gpg() to temp file
                    ├─> Extract config/config.php from tar.gz
                    ├─> parse_config_php_dbtype(config_path)
                    │       │
                    │       ├─> Regex match for 'dbtype'
                    │       ├─> Extract dbname, dbuser, dbhost
                    │       └─> Return (dbtype, db_config)
                    │
                    ├─> Normalize sqlite3 → sqlite
                    ├─> Cleanup temp files
                    └─> Return (dbtype, db_config)
            
            Set: self.detected_dbtype = dbtype
            Set: self.detected_db_config = db_config
            Set: self.db_auto_detected = True
    │
    ▼
show_wizard_page(2)
    │
    └─> create_wizard_page2(parent)
            │
            ├─> Create info_frame
            ├─> Create db_sqlite_message_label (hidden)
            ├─> Create warning_label (packed)
            ├─> Create instruction_labels (packed)
            ├─> Create db_frame with grid widgets
            ├─> Create admin_frame
            │
            ├─> Store widget references
            │   ├─> self.db_credential_packed_widgets
            │   └─> self.db_credential_frame
            │
            └─> If self.detected_dbtype:
                    update_database_credential_ui(dbtype)
                        │
                        ├─> If SQLite:
                        │   ├─> Hide packed widgets (pack_forget)
                        │   ├─> Hide db_frame (pack_forget)
                        │   └─> Show SQLite message (pack)
                        │
                        └─> Else:
                            ├─> Show packed widgets (pack)
                            ├─> Show db_frame (pack)
                            └─> Hide SQLite message (pack_forget)
```

---

## Troubleshooting

### Issue: Widgets not hiding/showing

**Check:**
1. Are widget references properly stored?
2. Is `update_database_credential_ui()` being called?
3. Is `detected_dbtype` set correctly?
4. Check console output for error messages

**Debug:**
```python
print(f"detected_dbtype: {self.detected_dbtype}")
print(f"db_credential_packed_widgets: {hasattr(self, 'db_credential_packed_widgets')}")
print(f"db_credential_frame: {hasattr(self, 'db_credential_frame')}")
```

### Issue: Detection not happening

**Check:**
1. Does backup contain config/config.php?
2. Is password correct (for encrypted)?
3. Is regex pattern matching config.php format?
4. Check temporary file cleanup

**Debug:**
```python
# In early_detect_database_type_from_backup()
print(f"Backup path: {backup_path}")
print(f"Encrypted: {backup_path.endswith('.gpg')}")
print(f"Password provided: {password is not None}")
print(f"Config path: {config_path}")
print(f"Config exists: {os.path.exists(config_path)}")
```

### Issue: Geometry manager errors

**Check:**
1. Are you using correct manager for each widget?
2. Did you call `pack()` on a gridded widget?
3. Did you call `grid()` on a packed widget?

**Fix:**
- Use `pack_forget()` / `pack()` for packed widgets
- Hide parent frame for grid widgets

---

## Performance Tips

1. **Cache detection**: Don't re-detect if already done
2. **Extract only what's needed**: Only extract config.php
3. **Clean up immediately**: Remove temp files after use
4. **Avoid UI updates in loops**: Batch updates together

---

## Best Practices

1. **Always use hasattr()**: Check widget existence before accessing
2. **Document geometry managers**: Comment which widgets use pack vs grid
3. **Test both paths**: Encrypted and unencrypted backups
4. **Preserve widget order**: Re-pack in same order as created
5. **Maintain centering**: Use `anchor="center"` consistently

---

## References

- **Main Implementation**: `nextcloud_restore_and_backup-v9.py`
- **Bug Fix Details**: `WIDGET_GEOMETRY_FIX.md`
- **Test Scenarios**: `TEST_SCENARIOS.md`
- **Full Summary**: `FINAL_IMPLEMENTATION_SUMMARY.md`
- **Original Feature**: `BEFORE_PAGE2_IMPLEMENTATION.md`
- **SQLite UI**: `IMPLEMENTATION_SUMMARY_SQLITE.md`
- **Centering**: `CENTERED_LAYOUT_UPDATE.md`
