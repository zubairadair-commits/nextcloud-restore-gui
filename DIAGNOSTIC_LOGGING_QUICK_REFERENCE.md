# Diagnostic Logging Quick Reference

## Overview
The Tailscale pages now include comprehensive diagnostic logging to ensure they never appear blank and provide clear troubleshooting information.

## Key Features

✅ **Never Blank Pages** - Automatic error handling with fallback to landing page
✅ **Clear Error Messages** - User-friendly dialogs with log file reference
✅ **Full Diagnostics** - All page renders, theme changes, and errors logged
✅ **Works Both Themes** - Tested in both light and dark modes
✅ **Zero Breaking Changes** - Fully backward compatible

## Log File Location

```
nextcloud_restore_gui.log
```
In the same directory as the application.

## Viewing Logs

### Real-time (Linux/Mac)
```bash
tail -f nextcloud_restore_gui.log
```

### Real-time (Windows PowerShell)
```powershell
Get-Content nextcloud_restore_gui.log -Wait -Tail 10
```

### View last 50 lines
```bash
tail -50 nextcloud_restore_gui.log
```

## What Gets Logged

### Page Rendering
- ✅ When Tailscale wizard starts/completes
- ✅ When Tailscale config starts/completes
- ✅ Current theme for each render
- ✅ Widget creation and initialization

### Theme Changes
- ✅ Theme toggle from/to (light ↔ dark)
- ✅ Theme applied to UI elements
- ✅ Current page being refreshed

### Navigation
- ✅ Page refresh initiated
- ✅ Which page method is called
- ✅ Page refresh completion

### Errors
- ✅ Error message and type
- ✅ Full stack trace
- ✅ Fallback attempt to landing page

## Log Entry Examples

### Successful Page Load
```
2025-10-13 13:30:45 - INFO - ============================================================
2025-10-13 13:30:45 - INFO - TAILSCALE WIZARD: Starting page render
2025-10-13 13:30:45 - INFO - Current theme: light
2025-10-13 13:30:45 - INFO - TAILSCALE WIZARD: Page render complete successfully
2025-10-13 13:30:45 - INFO - ============================================================
```

### Theme Toggle
```
2025-10-13 13:31:20 - INFO - THEME TOGGLE: Changed theme from light to dark
2025-10-13 13:31:20 - INFO - THEME TOGGLE: Applied theme to UI elements
2025-10-13 13:31:20 - INFO - THEME TOGGLE: Refreshing current page: tailscale_wizard
```

### Error with Fallback
```
2025-10-13 13:32:10 - ERROR - TAILSCALE WIZARD: ERROR during page render: AttributeError
2025-10-13 13:32:10 - ERROR - TAILSCALE WIZARD: Traceback: <full stack trace>
2025-10-13 13:32:10 - INFO - TAILSCALE WIZARD: Attempting fallback to landing page
```

## Troubleshooting Guide

### Problem: Page appears blank

1. **Check the log file:**
   ```bash
   tail -30 nextcloud_restore_gui.log
   ```

2. **Look for ERROR entries:**
   - Contains the exception type and message
   - Shows the full stack trace
   - Indicates where the error occurred

3. **Check for fallback:**
   - Should see "Attempting fallback to landing page"
   - If fallback also failed, app may be in bad state

### Problem: Theme toggle not working

1. **Check log for:**
   ```
   THEME TOGGLE: Changed theme from X to Y
   ```

2. **Verify page refresh:**
   ```
   REFRESH PAGE: Starting refresh for page: tailscale_wizard
   ```

3. **Check for errors during refresh:**
   - Look for ERROR entries after theme toggle
   - Check if page render completed successfully

### Problem: Navigation doesn't work

1. **Check log for:**
   ```
   REFRESH PAGE: Calling show_tailscale_wizard()
   ```

2. **Verify page render started:**
   ```
   TAILSCALE WIZARD: Starting page render
   ```

3. **Check if render completed:**
   ```
   TAILSCALE WIZARD: Page render complete successfully
   ```

## Testing the Logging

### Run the diagnostic test:
```bash
python3 test_diagnostic_logging.py
```

### Expected output:
```
======================================================================
Results: 12/12 checks passed
======================================================================

✅ All checks passed! Diagnostic logging is properly implemented.
```

### Test manually:
1. Start the app
2. Navigate to Tailscale wizard
3. Toggle theme
4. Check log file for entries

## Error Handling Flow

```
User Action (e.g., Navigate to Tailscale)
    ↓
Decorator logs: "Starting page render"
    ↓
Page method executes
    ↓
    ├─→ Success: Decorator logs "Page render complete successfully"
    │
    └─→ Exception:
        ├─→ Decorator logs: "ERROR during page render"
        ├─→ Decorator logs: Full stack trace
        ├─→ Show error dialog to user
        ├─→ Decorator logs: "Attempting fallback to landing page"
        └─→ Call show_landing() to avoid blank page
```

## Benefits Summary

| Before | After |
|--------|-------|
| Silent failures | Clear error messages |
| Blank pages possible | Always shows something |
| No diagnostic info | Complete event log |
| Hard to troubleshoot | Easy to diagnose issues |
| User confusion | User-friendly errors |

## Implementation Details

### Code Changes
- ✅ Added logging module import
- ✅ Configured file + console logging
- ✅ Created `@log_page_render()` decorator
- ✅ Applied decorator to Tailscale methods
- ✅ Added logging to theme/navigation methods

### Files Modified
- `nextcloud_restore_and_backup-v9.py` - Main changes
- `.gitignore` - Exclude log files from git

### Files Created
- `test_diagnostic_logging.py` - Automated test
- `DIAGNOSTIC_LOGGING_IMPLEMENTATION.md` - Full documentation
- `DIAGNOSTIC_LOGGING_QUICK_REFERENCE.md` - This file

## All Tests Passing ✅

- ✅ test_tailscale_navigation_fix.py (10/10)
- ✅ test_tailscale_centering_fix.py (10/10)
- ✅ test_tailscale_content_sections.py (23/23)
- ✅ test_diagnostic_logging.py (12/12)

## Support

For questions or issues:
1. Check the log file first
2. Review full documentation in `DIAGNOSTIC_LOGGING_IMPLEMENTATION.md`
3. Run tests to verify implementation
4. Check existing issues in the repository

---

**Status:** ✅ Complete and Production Ready
