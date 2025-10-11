# Widget Geometry Manager Fix - SQLite Database Detection UI

## Problem Statement

The Nextcloud Restore & Backup Utility wizard needed to:
1. Extract and detect database type immediately after backup selection and decryption (Page 1)
2. Conditionally show/hide database credential fields based on detected type
3. For SQLite databases: Hide credential fields and show informative message
4. For MySQL/PostgreSQL: Show credential fields as normal
5. Ensure all UI elements are properly centered on all pages

## Bug Discovered

While reviewing the implementation, a critical bug was found in the `update_database_credential_ui()` method:

### The Issue

The method attempted to use `grid_remove()` and `grid()` on ALL database credential widgets, but these widgets used different geometry managers:

- **Packed widgets**: `warning_label`, `instruction_label1`, `instruction_label2` (used `pack()`)
- **Grid widgets**: All database field labels, entries, and hints (used `grid()` within `db_frame`)

**Tkinter Rule**: You cannot mix geometry managers on the same widget. Calling `grid_remove()` on a packed widget causes errors or unpredictable behavior.

### Code Before Fix

```python
# In create_wizard_page2()
self.db_credential_widgets = [
    warning_label,           # PACKED
    instruction_label1,      # PACKED
    instruction_label2,      # PACKED
    db_name_label,          # GRID
    self.db_name_entry,     # GRID
    # ... more grid widgets
]

# In update_database_credential_ui()
for widget in self.db_credential_widgets:
    widget.grid_remove()  # ❌ WRONG for packed widgets!
```

## Solution Implemented

### 1. Separated Widget References

Split the widget references based on their geometry manager:

```python
# Packed widgets (warning/instruction labels)
self.db_credential_packed_widgets = [
    warning_label,
    instruction_label1,
    instruction_label2
]

# Frame containing all grid widgets
self.db_credential_frame = db_frame
```

### 2. Updated Hide/Show Logic

Fixed `update_database_credential_ui()` to use the correct geometry manager methods:

```python
def update_database_credential_ui(self, dbtype):
    is_sqlite = dbtype and dbtype.lower() in ['sqlite', 'sqlite3']
    
    if is_sqlite:
        # Hide packed widgets with pack_forget()
        for widget in self.db_credential_packed_widgets:
            widget.pack_forget()
        
        # Hide the entire db_frame (which is also packed)
        self.db_credential_frame.pack_forget()
        
        # Show SQLite message
        self.db_sqlite_message_label.pack(pady=(10, 10), anchor="center")
    else:
        # Re-pack widgets in correct order
        self.db_credential_packed_widgets[0].pack(anchor="center", pady=(5, 0))
        self.db_credential_packed_widgets[1].pack(anchor="center")
        self.db_credential_packed_widgets[2].pack(anchor="center", pady=(0, 10))
        
        # Show db_frame
        self.db_credential_frame.pack(pady=10, anchor="center", fill="x", padx=50)
        
        # Hide SQLite message
        self.db_sqlite_message_label.pack_forget()
```

### 3. Enhanced Centering

Added `anchor="center"` to the info_frame for consistent layout:

```python
info_frame.pack(pady=(5, 10), padx=50, fill="x", anchor="center")
```

## Benefits

✅ **Correct geometry manager usage** - No more mixing pack() and grid() operations
✅ **Cleaner code** - Separated concerns between packed and grid widgets
✅ **Better organization** - Frame-level hiding for grid widgets
✅ **Robustness** - Added hasattr() checks for safety
✅ **Proper re-packing** - Widgets restored with original settings and order
✅ **Improved centering** - All elements properly aligned

## Testing

### Unit Tests
- ✅ Config.php parsing verified for SQLite, PostgreSQL, MySQL
- ✅ SQLite detection logic validated (sqlite, sqlite3)
- ✅ Python syntax validated

### Integration Tests Required
- [ ] Visual verification with GUI
- [ ] Test with encrypted SQLite backup
- [ ] Test with unencrypted SQLite backup
- [ ] Test with encrypted PostgreSQL backup
- [ ] Test with unencrypted MySQL backup
- [ ] Verify navigation back/forth between pages
- [ ] Verify window resizing maintains centering

## Files Modified

- `nextcloud_restore_and_backup-v9.py`
  - Lines 287-289: Updated initialization
  - Line 658: Added anchor="center" to info_frame
  - Lines 735-743: Split widget references
  - Lines 950: Updated check for widget existence
  - Lines 1608-1639: Fixed hide/show logic

## Related Documentation

- `BEFORE_PAGE2_IMPLEMENTATION.md` - Implementation of extraction before Page 2
- `IMPLEMENTATION_SUMMARY_SQLITE.md` - Original SQLite UI improvements
- `CENTERED_LAYOUT_UPDATE.md` - Centering implementation
- `CENTERING_FIX_SUMMARY.md` - Canvas centering fix

## Impact

This fix ensures that:
1. SQLite users NEVER see unnecessary database credential fields
2. The UI correctly hides/shows widgets based on detection
3. All elements remain properly centered
4. The application doesn't crash or behave unpredictably due to geometry manager conflicts
