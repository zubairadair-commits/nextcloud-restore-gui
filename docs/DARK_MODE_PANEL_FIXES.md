# Dark Mode Panel Fixes - Complete Implementation

## Overview

This document describes the dark mode fixes applied to all major wizard/panel boxes in the Nextcloud Restore & Backup Utility to ensure proper theme support across the entire application.

## Problem Statement

Three major panels were not properly respecting dark mode theme colors:

1. **Start New Nextcloud Instance Panel** (image12)
   - Main panel frame had no background color
   - Labels used hardcoded colors (no `fg` parameter)
   - Entry fields used default colors
   - Hint text used hardcoded `gray` color

2. **Launch Nextcloud Instance Progress UI**
   - Progress frame had no background color
   - Status labels used hardcoded colors (`blue`, `gray`, `green`, `orange`)
   - Result frame had no background color
   - Container info labels used hardcoded colors

3. **Schedule Automatic Backups Panel** (image13)
   - Main panel frame had no background color
   - Status frame used hardcoded light blue (`#e8f4f8`)
   - Status text used hardcoded colors (`#27ae60`, `#e74c3c`)
   - Configuration labels had no theme colors
   - Entry fields used default colors
   - Radio buttons and checkboxes had no theme support
   - Warning label used hardcoded color (`#e67e22`)

## Solution

### 1. Start New Nextcloud Instance Panel

#### Updated `show_port_entry` Method

**Main Frame:**
```python
entry_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
```

**Back Button:**
```python
btn_back = tk.Button(entry_frame, text="Return to Main Menu", font=("Arial", 12), 
                    bg=self.theme_colors['button_bg'], fg=self.theme_colors['button_fg'],
                    command=self.show_landing)
```

**Title Label:**
```python
tk.Label(entry_frame, text="Select a port to access Nextcloud in your browser.", 
        font=("Arial", 14),
        bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=8)
```

**Hint Text:**
```python
tk.Label(entry_frame, 
        text="The port determines the address you use to reach Nextcloud.\nFor example, if you choose port 8080, you'll go to http://localhost:8080", 
        font=("Arial", 11), 
        bg=self.theme_colors['bg'], 
        fg=self.theme_colors['hint_fg']).pack(pady=(0,10))
```

**Custom Port Entry:**
```python
custom_port_entry = tk.Entry(entry_frame, font=("Arial", 13), width=10,
                            bg=self.theme_colors['entry_bg'], 
                            fg=self.theme_colors['entry_fg'],
                            insertbackground=self.theme_colors['entry_fg'])
```

**Theme Recursive Application:**
```python
# Apply theme recursively to all widgets in the panel
self.apply_theme_recursive(entry_frame)
```

**Note:** The "Start Nextcloud Instance" button intentionally keeps its branding color (`#f7b32b` with white text) as it's a primary action button.

---

### 2. Launch Nextcloud Instance Progress UI

#### Updated `launch_nextcloud_instance` Method

**Progress Frame:**
```python
progress_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
```

**Status Labels:**
```python
# Status label with spinner
status_label = tk.Label(progress_frame, text="", font=("Arial", 13), 
                       bg=self.theme_colors['bg'], fg=self.theme_colors['fg'])

# Detailed message label
detail_label = tk.Label(progress_frame, text="", font=("Arial", 11), 
                       bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg'])
```

**Success State (Ready):**
```python
info_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])

tk.Label(info_frame, text="✓ Nextcloud is ready!", font=("Arial", 16, "bold"), 
        bg=self.theme_colors['bg'], fg=self.theme_colors['warning_fg']).pack(pady=8)

tk.Label(info_frame, text="Access it at:", font=("Arial", 14),
        bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=(10, 5))

# URL link (intentionally blue for clickable appearance)
link_label = tk.Label(
    info_frame,
    text=url,
    font=("Arial", 16, "bold"),
    bg=self.theme_colors['bg'],
    fg="#3daee9",  # Consistent link color across themes
    cursor="hand2"
)

tk.Label(info_frame, text=f"Container ID: {container_id}", font=("Arial", 11), 
        bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg']).pack(pady=5)
```

**Initializing State:**
```python
tk.Label(info_frame, text="⚠ Nextcloud container is starting", font=("Arial", 16, "bold"), 
        bg=self.theme_colors['bg'], fg=self.theme_colors['warning_fg']).pack(pady=8)

tk.Label(info_frame, text="The service is still initializing.\nThe link will become available when ready.", 
        font=("Arial", 12), bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg']).pack(pady=10)

# Disabled link (uses hint color)
link_label = tk.Label(
    info_frame,
    text=url,
    font=("Arial", 16, "bold"),
    bg=self.theme_colors['bg'],
    fg=self.theme_colors['hint_fg']  # Use hint color for disabled state
)
```

**Return Button:**
```python
tk.Button(info_frame, text="Return to Main Menu", font=("Arial", 13), 
         bg=self.theme_colors['button_bg'], fg=self.theme_colors['button_fg'],
         command=self.show_landing).pack(pady=18)

# Apply theme recursively to all widgets in the panel
self.apply_theme_recursive(info_frame)
```

---

### 3. Schedule Automatic Backups Panel

#### Updated `show_schedule_backup` Method

**Main Frame:**
```python
frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
```

**Back Button:**
```python
tk.Button(
    frame, 
    text="Return to Main Menu", 
    font=("Arial", 12),
    bg=self.theme_colors['button_bg'],
    fg=self.theme_colors['button_fg'],
    command=self.show_landing
).pack(pady=8)
```

**Title:**
```python
tk.Label(
    frame, 
    text="Schedule Automatic Backups", 
    font=("Arial", 18, "bold"),
    bg=self.theme_colors['bg'],
    fg=self.theme_colors['fg']
).pack(pady=15)
```

**Status Frame (uses info theme colors):**
```python
status_frame = tk.Frame(frame, bg=self.theme_colors['info_bg'], relief="ridge", borderwidth=2)

tk.Label(
    status_frame, 
    text="Current Status", 
    font=("Arial", 14, "bold"), 
    bg=self.theme_colors['info_bg'],
    fg=self.theme_colors['info_fg']
).pack(pady=5)
```

**Active Status (success state):**
```python
tk.Label(
    status_frame, 
    text=status_text, 
    font=("Arial", 11), 
    bg=self.theme_colors['info_bg'], 
    fg=self.theme_colors['warning_fg']  # Green in both themes
).pack(pady=5)

# Buttons within status frame
btn_frame = tk.Frame(status_frame, bg=self.theme_colors['info_bg'])

tk.Button(
    btn_frame, 
    text="Disable Schedule", 
    font=("Arial", 11),
    bg=self.theme_colors['button_bg'],
    fg=self.theme_colors['button_fg'],
    command=lambda: self._disable_schedule(task_name)
).pack(side="left", padx=5)
```

**Inactive Status (error state):**
```python
tk.Label(
    status_frame, 
    text="✗ No scheduled backup configured", 
    font=("Arial", 11), 
    bg=self.theme_colors['info_bg'], 
    fg=self.theme_colors['error_fg']  # Red in both themes
).pack(pady=5)
```

**Configuration Section:**
```python
config_frame = tk.Frame(frame, bg=self.theme_colors['bg'])

# Section title
tk.Label(
    config_frame, 
    text="Configure New Schedule", 
    font=("Arial", 14, "bold"),
    bg=self.theme_colors['bg'],
    fg=self.theme_colors['fg']
).pack(pady=10)

# Field labels
tk.Label(config_frame, text="Backup Directory:", font=("Arial", 11),
        bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=5)

# Entry fields
dir_entry = tk.Entry(dir_frame, textvariable=backup_dir_var, font=("Arial", 11),
                    bg=self.theme_colors['entry_bg'], 
                    fg=self.theme_colors['entry_fg'],
                    insertbackground=self.theme_colors['entry_fg'])

# Radio buttons
tk.Radiobutton(
    freq_frame, 
    text=freq.capitalize(), 
    variable=frequency_var, 
    value=freq,
    font=("Arial", 11),
    bg=self.theme_colors['bg'],
    fg=self.theme_colors['fg'],
    selectcolor=self.theme_colors['entry_bg']  # Selection indicator
).pack(side="left", padx=10)

# Checkboxes
tk.Checkbutton(
    config_frame, 
    text="Encrypt backups", 
    variable=encrypt_var,
    font=("Arial", 11),
    bg=self.theme_colors['bg'],
    fg=self.theme_colors['fg'],
    selectcolor=self.theme_colors['entry_bg']  # Selection indicator
).pack(pady=10)
```

**Warning Label:**
```python
warning_label = tk.Label(
    config_frame,
    text="⚠️ Note: Scheduled backups are currently only supported on Windows",
    font=("Arial", 10),
    bg=self.theme_colors['bg'],
    fg=self.theme_colors['warning_fg']
)
```

**Create/Update Button:**
```python
tk.Button(
    config_frame,
    text="Create/Update Schedule",
    font=("Arial", 13, "bold"),
    bg="#27ae60",  # Intentional green branding color
    fg="white",
    command=lambda: self._create_schedule(...)
).pack(pady=20)

# Apply theme recursively to all widgets in the panel
self.apply_theme_recursive(frame)
```

**Note:** The "Create/Update Schedule" button intentionally keeps its green branding color (`#27ae60` with white text) as it's a primary action button.

---

## Theme Colors Used

### Light Theme (`THEMES['light']`)
- `bg`: `#f0f0f0` - Light gray background
- `fg`: `#000000` - Black text
- `button_bg`: `#e0e0e0` - Light button background
- `button_fg`: `#000000` - Black button text
- `entry_bg`: `#ffffff` - White entry fields
- `entry_fg`: `#000000` - Black entry text
- `info_bg`: `#e3f2fd` - Light blue info panels
- `info_fg`: `#000000` - Black info text
- `warning_fg`: `#2e7d32` - Green for success/active states
- `error_fg`: `#d32f2f` - Red for error states
- `hint_fg`: `#666666` - Gray for hint text

### Dark Theme (`THEMES['dark']`)
- `bg`: `#1e1e1e` - Dark gray background
- `fg`: `#e0e0e0` - Light gray text
- `button_bg`: `#2d2d2d` - Dark button background
- `button_fg`: `#e0e0e0` - Light button text
- `entry_bg`: `#2d2d2d` - Dark entry fields
- `entry_fg`: `#e0e0e0` - Light entry text
- `info_bg`: `#1a3a4a` - Dark blue info panels
- `info_fg`: `#e0e0e0` - Light info text
- `warning_fg`: `#7cb342` - Light green for success/active states
- `error_fg`: `#ef5350` - Light red for error states
- `hint_fg`: `#999999` - Light gray for hint text

---

## Intentional Hardcoded Colors

Some colors are intentionally kept as hardcoded values to maintain visual consistency and branding:

### Primary Action Buttons
1. **Start Nextcloud Instance Button**: `bg="#f7b32b"` (yellow/orange) with `fg="white"`
   - This is the main action button with distinctive branding color
   
2. **Create/Update Schedule Button**: `bg="#27ae60"` (green) with `fg="white"`
   - This is the main action button with distinctive branding color

### Clickable Links
3. **URL Links**: `fg="#3daee9"` (blue)
   - Standard blue color for clickable URLs, consistent across both themes
   - Makes URLs instantly recognizable as clickable elements

These colors are excluded from theme color validation as they serve specific branding and UX purposes.

---

## Automatic Theme Updates

All three panels now call `self.apply_theme_recursive(frame)` at the end of their setup, ensuring:

1. **Dynamic Theme Switching**: When users toggle between light and dark themes, all widgets automatically update
2. **Child Widget Support**: Nested frames and their children are properly themed
3. **Consistent Experience**: All UI elements maintain visual consistency
4. **Future-Proof**: New widgets added to these panels will automatically pick up theme colors

---

## Testing

### Automated Tests

A comprehensive test suite (`test_panel_dark_mode.py`) validates:

1. ✅ Start New Instance panel uses theme colors for:
   - Frames (background)
   - Labels (background and foreground)
   - Entry fields (background, foreground, cursor)
   - Hint text (appropriate contrast)

2. ✅ Launch Instance Progress uses theme colors for:
   - Progress frame (background)
   - Status labels (background and foreground)
   - Detail labels (hint color for reduced emphasis)
   - Result frame (background)
   - Container info labels (hint color)

3. ✅ Schedule Backup panel uses theme colors for:
   - Main frame (background)
   - Labels (background and foreground)
   - Entry fields (background, foreground, cursor)
   - Status frame (info background for visual distinction)
   - Radio buttons and checkboxes (selection indicators)
   - Warning labels (warning color)

4. ✅ All panels call `apply_theme_recursive` for automatic theme updates

**Test Results:**
```
======================================================================
TOTAL: 4/4 tests passed
======================================================================

🎉 ALL TESTS PASSED! 🎉
```

### Manual Testing Checklist

#### Light Theme Testing
- [x] Navigate to "Start New Nextcloud Instance"
- [x] Verify all text is readable (black on light gray)
- [x] Check entry field has white background
- [x] Verify hint text has appropriate gray color
- [x] Check button colors and text contrast

#### Dark Theme Testing
- [x] Toggle to dark mode
- [x] Navigate to "Start New Nextcloud Instance"
- [x] Verify all text is readable (light gray on dark gray)
- [x] Check entry field has dark background
- [x] Verify hint text has appropriate light gray color
- [x] Check button colors and text contrast
- [x] Verify URL link is blue and visible

#### Schedule Backup Testing (Light)
- [x] Navigate to "Schedule Automatic Backups"
- [x] Verify status frame has light blue background
- [x] Check all labels are readable
- [x] Verify entry fields have white backgrounds
- [x] Check radio buttons and checkboxes are visible

#### Schedule Backup Testing (Dark)
- [x] Toggle to dark mode
- [x] Navigate to "Schedule Automatic Backups"
- [x] Verify status frame has dark blue background
- [x] Check all labels are readable (light on dark)
- [x] Verify entry fields have dark backgrounds
- [x] Check radio buttons and checkboxes are visible
- [x] Verify selection indicators work

---

## Benefits

### User Experience
- **Consistent Visual Theme**: All panels now respect the user's theme choice
- **Reduced Eye Strain**: Dark mode is properly supported throughout the app
- **Professional Appearance**: Uniform styling across all dialogs and wizards
- **Clear Visual Hierarchy**: Info panels, status indicators, and content are clearly distinguished

### Technical Benefits
- **Maintainable Code**: All theme colors reference `self.theme_colors` dictionary
- **Theme Switching**: Automatic updates when toggling between themes
- **Extensible**: Easy to add new widgets with proper theme support
- **Tested**: Comprehensive test coverage ensures theme support is maintained

### Accessibility
- **Color Contrast**: Theme colors provide appropriate contrast ratios
- **Readability**: Text is clearly readable in both light and dark themes
- **Visual Indicators**: Status colors (green for success, red for errors) work in both themes
- **Hint Text**: Reduced emphasis for secondary information

---

## Files Changed

1. **`nextcloud_restore_and_backup-v9.py`**
   - `show_port_entry()`: Lines ~5002-5043
   - `launch_nextcloud_instance()`: Lines ~5043-5256
   - `show_schedule_backup()`: Lines ~5260-5445

2. **`test_panel_dark_mode.py`** (NEW)
   - Comprehensive test suite for panel dark mode support
   - 4 test cases covering all three panels
   - Validates proper theme color usage and recursive application

---

## Visual Comparison

### Before (Dark Mode)
**Issues:**
- White/light backgrounds on panels
- Black text on light backgrounds (jarring contrast)
- Entry fields with white backgrounds
- Hardcoded colors that don't adapt to theme

### After (Dark Mode)
**Improvements:**
- Dark backgrounds (`#1e1e1e`) on all panels
- Light text (`#e0e0e0`) on dark backgrounds
- Entry fields with dark backgrounds (`#2d2d2d`)
- Info frames with dark blue backgrounds (`#1a3a4a`)
- All colors from `self.theme_colors` dictionary
- Automatic theme updates when toggling

---

## Summary

All three major panels now fully support both light and dark themes:

1. ✅ **Restore Wizard** (already fixed - image10)
2. ✅ **Start New Nextcloud Instance** (image12) - FIXED
3. ✅ **Schedule Automatic Backups** (image13) - FIXED

The application now provides a consistent, professional dark mode experience across all major UI components, with proper contrast, readability, and visual hierarchy maintained in both themes.
