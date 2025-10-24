# Manual Testing Guide for Remote Access Page Improvements

## Summary of Changes
This update addresses two issues in the Remote Access Setup page:
1. Improved mouse wheel scrolling for better usability
2. Suppressed flashing command prompt windows on Windows

## Testing Instructions

### 1. Test Scrollable Remote Access Page

#### Steps:
1. Launch the Nextcloud Restore & Backup application
2. Click on "🌐 Remote Access" from the main menu
3. Click "⚙️ Configure Remote Access"
4. Resize the window to various sizes (small, medium, large)
5. Test mouse wheel scrolling:
   - Place cursor over the page content
   - Scroll with mouse wheel (or trackpad)
   - Verify that:
     - All content is accessible via scrolling
     - Scrolling is smooth and responsive
     - Scrollbar appears on the right side
     - Content doesn't get cut off at any window size

#### Expected Behavior:
- ✓ Mouse wheel scrolling works immediately when hovering over the page
- ✓ All sections are accessible (Tailscale info, Custom Domains, Auto-serve settings, Current Trusted Domains)
- ✓ Scrolling works at any window size
- ✓ Scrollbar is visible when content exceeds window height
- ✓ No conflicts with scrolling on other pages (e.g., Backup History page)

#### Platform-Specific:
- **Windows**: Test with standard mouse wheel
- **macOS**: Test with trackpad two-finger scroll
- **Linux**: Test with both mouse wheel and touchpad

### 2. Test Suppressed Command Prompt Windows (Windows Only)

#### Prerequisites:
- Windows operating system
- Tailscale installed and running

#### Steps:
1. Launch the application
2. Navigate to "🌐 Remote Access" → "⚙️ Configure Remote Access"
3. Watch for any flashing command prompt windows during:
   - Page load (when Tailscale status is checked)
   - Checking scheduled task status
   - Enabling/disabling auto-start
   - Creating new scheduled tasks

#### Expected Behavior:
- ✓ No command prompt windows should flash or appear briefly
- ✓ All operations should execute silently in the background
- ✓ Application should feel more polished and less "technical"

#### Before vs After:
**Before**: Black command prompt windows would briefly flash on screen during:
- Tailscale status checks
- Creating/checking scheduled tasks
- Starting Tailscale Serve

**After**: All subprocess operations run silently with no visible windows

### 3. Regression Testing

Test that existing functionality still works:

#### Remote Access Features:
- [ ] Can view Tailscale IP and hostname
- [ ] Can add custom domains
- [ ] Can configure automatic Tailscale serve
- [ ] Can manage trusted domains (add/remove)
- [ ] Can enable/disable scheduled tasks

#### Other Pages:
- [ ] Backup History page scrolling still works
- [ ] Main landing page works normally
- [ ] Restore wizard functions properly

## Code Changes Summary

### File: `src/nextcloud_restore_and_backup-v9.py`

#### Change 1: Fixed Mouse Wheel Scrolling (Lines ~12996-13014)
```python
# Before:
def on_mouse_wheel(event):
    if event.num == 5 or event.delta < 0:
        canvas.yview_scroll(1, "units")
    if event.num == 4 or event.delta > 0:
        canvas.yview_scroll(-1, "units")

canvas.bind_all("<MouseWheel>", on_mouse_wheel)

# After:
def on_mouse_wheel(event):
    if event.delta:
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    elif event.num == 5:
        canvas.yview_scroll(1, "units")
    elif event.num == 4:
        canvas.yview_scroll(-1, "units")

canvas.bind("<MouseWheel>", on_mouse_wheel)  # Changed from bind_all to bind
content.bind("<MouseWheel>", on_mouse_wheel)  # Also bind to content
```

**Why**: 
- `event.delta/120` is the correct way to handle Windows/Mac mouse wheel
- Using `bind()` instead of `bind_all()` prevents conflicts with other scrollable pages
- Binding to both canvas and content ensures scrolling works everywhere

#### Change 2: Added Creation Flags to Tailscale Status Check (Line ~14025)
```python
# Before:
result = subprocess.run(
    [tailscale_cmd, "status", "--json"],
    capture_output=True,
    text=True,
    timeout=15
)

# After:
creation_flags = get_subprocess_creation_flags()
result = subprocess.run(
    [tailscale_cmd, "status", "--json"],
    capture_output=True,
    text=True,
    timeout=15,
    creationflags=creation_flags
)
```

**Why**: 
- `get_subprocess_creation_flags()` returns `0x08000000` (CREATE_NO_WINDOW) on Windows
- This flag tells Windows to not create a visible console window
- Returns 0 on non-Windows platforms (no effect)

## Test Results

### Automated Tests
All 8 new tests passing:
- ✓ test_get_tailscale_info_has_creationflags
- ✓ test_canvas_scrolling_uses_bind_not_bind_all
- ✓ test_mouse_wheel_handler_uses_delta_division
- ✓ test_domain_list_canvas_has_scrolling
- ✓ test_check_scheduled_task_uses_flags
- ✓ test_disable_scheduled_task_uses_flags
- ✓ test_enable_scheduled_task_uses_flags
- ✓ test_setup_windows_task_scheduler_uses_flags

### Manual Testing Checklist

#### Scrolling Test (All Platforms):
- [ ] Mouse wheel scrolls content smoothly
- [ ] All sections are reachable
- [ ] Scrollbar visible when needed
- [ ] No conflicts with other pages
- [ ] Works at different window sizes

#### Windows Subprocess Test (Windows Only):
- [ ] No flashing command prompts during page load
- [ ] No flashing command prompts during status checks
- [ ] No flashing command prompts during task management
- [ ] Application feels polished and professional

## Notes for Reviewer

1. **Minimal Changes**: Only two specific issues addressed, no additional changes
2. **Backward Compatible**: Changes don't affect existing functionality
3. **Platform-Specific**: Creation flags only affect Windows (no change on Linux/Mac)
4. **Well-Tested**: 8 automated tests validate the changes
5. **User-Facing Impact**: 
   - Better UX with smooth scrolling
   - More professional appearance (no flashing windows)
