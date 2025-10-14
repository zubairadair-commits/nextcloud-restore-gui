# Fix: Scheduled Backup RuntimeError

## Problem Statement

When running scheduled backups via Windows Task Scheduler (using the `--scheduled` flag), the application would crash with:

```
RuntimeError: main thread is not in main loop
```

This error occurred because:
1. The application was creating a full Tkinter GUI instance even in scheduled mode
2. GUI methods like `self.after()` and `self._display_health_status()` were being called
3. The main Tkinter event loop was not running, causing the crash

## Root Cause Analysis

### Before the Fix

When `--scheduled` flag was used:

```python
# Main block (before fix)
if args.scheduled:
    app = NextcloudRestoreWizard()  # Creates full GUI
    app.withdraw()                   # Hide the window
    app.run_scheduled_backup(...)    # Try to run backup
```

The problem:
- `NextcloudRestoreWizard.__init__()` fully initialized the GUI:
  - Created frames, buttons, labels
  - Called `self.after(1000, self._check_scheduled_task_on_startup)` at line 2449
  - Called `self.show_landing()` which created health dashboard
  - Health dashboard called `self._refresh_health_dashboard()` which used `self.after(0, ...)`
- These GUI methods tried to interact with the Tkinter main loop
- Since `app.withdraw()` was called and the main loop wasn't started, errors occurred

### Error Stack Trace

```
Traceback:
  File "...", line 8057, in _refresh_health_dashboard
    self.after(0, lambda: self._display_health_status(container, health_status))
RuntimeError: main thread is not in main loop
```

## Solution

### Implementation

Added a `scheduled_mode` parameter to skip ALL GUI initialization:

```python
class NextcloudRestoreWizard(tk.Tk):
    def __init__(self, scheduled_mode=False):
        super().__init__()
        
        # Store scheduled mode flag
        self.scheduled_mode = scheduled_mode
        
        # If in scheduled mode, skip all GUI initialization
        if scheduled_mode:
            return
        
        # ... rest of GUI initialization only runs in normal mode ...
```

Updated the main block:

```python
# Main block (after fix)
if args.scheduled:
    # Create minimal instance with NO GUI initialization
    app = NextcloudRestoreWizard(scheduled_mode=True)
    app.run_scheduled_backup(...)  # Run backup
    sys.exit(0)
```

### Key Changes

**File**: `nextcloud_restore_and_backup-v9.py`

1. **Line 2313**: Added `scheduled_mode=False` parameter to `__init__`
2. **Lines 2315-2319**: Added early return if `scheduled_mode=True`
3. **Line 8610**: Changed to `NextcloudRestoreWizard(scheduled_mode=True)`
4. **Line 8611**: Removed `app.withdraw()` (no longer needed)

### What Gets Skipped in Scheduled Mode

When `scheduled_mode=True`, the following are NOT initialized:
- ❌ Window title, geometry, minsize
- ❌ Theme colors and configuration
- ❌ Header frame with buttons
- ❌ Status label
- ❌ Body frame
- ❌ All GUI state variables
- ❌ Window resize bindings
- ❌ `self.after()` calls
- ❌ `self.show_landing()` and health dashboard

What DOES run in scheduled mode:
- ✅ `super().__init__()` - Creates minimal Tk instance
- ✅ `self.scheduled_mode = True` - Flags scheduled mode
- ✅ `run_scheduled_backup()` - Backup logic with console output
- ✅ Database detection and backup operations
- ✅ Print statements for logging

## Benefits

### For Scheduled Backups
- ✅ No GUI initialization overhead
- ✅ No RuntimeError crashes
- ✅ Works reliably with Windows Task Scheduler
- ✅ Pure console output (no GUI dialogs)
- ✅ Faster startup time

### For Normal GUI Mode
- ✅ No changes to GUI behavior
- ✅ All features work as before
- ✅ Theme system intact
- ✅ Health dashboard functioning

## Testing

### Verification Test

Created `test_scheduled_mode_fix.py` which verifies:
- ✅ `__init__` accepts `scheduled_mode` parameter
- ✅ `scheduled_mode` flag is stored
- ✅ GUI initialization skipped when flag is True
- ✅ Main block passes `scheduled_mode=True`
- ✅ `app.withdraw()` removed (not needed)
- ✅ No GUI method calls in `run_scheduled_backup()`

### Simulation Test

Created `test_scheduled_backup_simulation.py` which:
- Simulates Windows Task Scheduler execution
- Verifies no GUI errors occur
- Checks for "main thread is not in main loop" error
- Tests with actual command-line arguments

## Usage

### Windows Task Scheduler Command

```cmd
python "C:\path\to\nextcloud_restore_and_backup-v9.py" ^
  --scheduled ^
  --backup-dir "C:\Backups\Nextcloud" ^
  --encrypt ^
  --password "mypassword"
```

### Expected Output (Console)

```
Starting scheduled backup to C:\Backups\Nextcloud
Step 1/10: Preparing backup...
Step 2/10: Checking and copying 'config'...
  ✓ Copied 'config'
Step 3/10: Checking and copying 'data'...
  ✓ Copied 'data'
...
Step 10/10: Backup complete!
Backup saved to: C:\Backups\Nextcloud\nextcloud-backup-20251014_080230.tar.gz
Scheduled backup completed successfully
```

### Error Handling

If Docker is not running:
```
ERROR: Docker is not running. Cannot perform backup.
```

If no Nextcloud container:
```
ERROR: No running Nextcloud container found.
```

All errors are printed to console (can be captured by Task Scheduler logs).

## Code Comparison

### Before (❌ Broken)

```python
class NextcloudRestoreWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nextcloud Restore & Backup Utility")
        self.geometry("900x900")
        # ... 100+ lines of GUI initialization ...
        self.after(1000, self._check_scheduled_task_on_startup)
        self.show_landing()  # Creates health dashboard with self.after()

# Main block
if args.scheduled:
    app = NextcloudRestoreWizard()  # Full GUI created!
    app.withdraw()                   # Try to hide it
    app.run_scheduled_backup(...)    # CRASH: main thread not in loop
```

### After (✅ Fixed)

```python
class NextcloudRestoreWizard(tk.Tk):
    def __init__(self, scheduled_mode=False):
        super().__init__()
        self.scheduled_mode = scheduled_mode
        
        # Early exit for scheduled mode
        if scheduled_mode:
            return
        
        # GUI initialization only in normal mode
        self.title("Nextcloud Restore & Backup Utility")
        self.geometry("900x900")
        # ... 100+ lines of GUI initialization ...
        self.after(1000, self._check_scheduled_task_on_startup)
        self.show_landing()

# Main block
if args.scheduled:
    app = NextcloudRestoreWizard(scheduled_mode=True)  # No GUI!
    app.run_scheduled_backup(...)                      # Works!
    sys.exit(0)
```

## Migration Notes

### For Existing Scheduled Tasks

No changes needed! Existing Windows scheduled tasks will work automatically because:
1. They already use `--scheduled` flag
2. The fix is backward compatible
3. Same command-line arguments

### For New Scheduled Tasks

Use the GUI's "Schedule Backup" feature, which:
- Creates the task with correct arguments
- Automatically uses `--scheduled` flag
- Handles paths with spaces correctly

## Technical Details

### Minimal Tk Instance

Even with `scheduled_mode=True`, we still call `super().__init__()` to create a minimal Tk instance. This is necessary because:
1. `run_scheduled_backup()` is a method of the class
2. Some internal state may be accessed
3. The instance provides a namespace for attributes

However, no GUI widgets are created, so no event loop is required.

### Thread Safety

In scheduled mode:
- No threads are created for GUI updates
- No `self.after()` scheduling
- No widget manipulation
- Pure sequential execution

## Related Files

- **Main fix**: `nextcloud_restore_and_backup-v9.py` (lines 2313-2319, 8610)
- **Verification**: `test_scheduled_mode_fix.py`
- **Simulation**: `test_scheduled_backup_simulation.py`
- **Documentation**: This file (`SCHEDULED_BACKUP_GUI_FIX.md`)

## Status

✅ **Fixed** - Scheduled backups now run without GUI errors

---

*Fix implemented: October 2025*  
*Issue: RuntimeError: 'main thread is not in main loop'*  
*Solution: Conditional GUI initialization based on scheduled_mode flag*
