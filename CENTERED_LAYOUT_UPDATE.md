# Centered Layout Update - Restore Wizard

## Overview
All wizard elements have been updated to use a centered layout for improved visual consistency and better user experience across different screen sizes.

## Changes Made

### Global Changes
- All titles, descriptions, buttons, input fields, and navigation elements are now centered
- Form groups (database config, admin credentials, container config) are centered as complete units
- Progress indicators and error messages are centered

### Page-by-Page Changes

#### Page 1: Backup Selection and Decryption
✅ **Centered Elements:**
- "Return to Main Menu" button
- Page title "Restore Wizard: Page 1 of 3"
- "Step 1: Select Backup Archive" title
- Backup file description text
- Backup file path input field (70 char width)
- "Browse..." button
- "Step 2: Decryption Password" title
- Password description text
- Password input field (40 char width)
- "Next →" button

#### Page 2: Database and Admin Configuration
✅ **Centered Elements:**
- Page title "Restore Wizard: Page 2 of 3"
- "Step 3: Database Configuration" title
- Database configuration description text
- Database form frame (containing all DB labels and inputs as a group)
  - Database Host input
  - Database Name input
  - Database User input
  - Database Password input
- "Step 4: Nextcloud Admin Credentials" title
- Admin credentials description text
- Admin form frame (containing all admin labels and inputs as a group)
  - Admin Username input
  - Admin Password input
- Navigation buttons: "← Back" and "Next →"

#### Page 3: Container Configuration
✅ **Centered Elements:**
- Page title "Restore Wizard: Page 3 of 3"
- "Step 5: Container Configuration" title
- Container configuration description text
- Container form frame (containing all container labels and inputs as a group)
  - Container Name input
  - Container Port input
- "Use existing Nextcloud container if found" checkbox
- Navigation buttons: "← Back" and "Start Restore"

#### Progress and Error Display
✅ **Centered Elements:**
- Error label (red text, 600px wrap length)
- Progress bar (520px length)
- Progress percentage label
- Process status label (now uses center alignment for text)

## Technical Implementation

### Changes to `show_wizard_page` method:
```python
# Before: btn_back.pack(pady=8)
# After:  btn_back.pack(pady=8, anchor="center")

# Before: tk.Label(...).pack(pady=(5, 15))
# After:  tk.Label(...).pack(pady=(5, 15), anchor="center")
```

### Changes to `create_wizard_page1` method:
```python
# All pack() calls now include anchor="center"
tk.Label(parent, ...).pack(pady=(10, 5), anchor="center")
self.backup_entry.pack(pady=5, anchor="center")
tk.Button(parent, ...).pack(pady=5, anchor="center")
```

### Changes to `create_wizard_page2` and `create_wizard_page3`:
```python
# Titles and descriptions centered
tk.Label(parent, ...).pack(pady=(10, 5), anchor="center")

# Form frames centered (grid layout inside frames keeps label/input alignment)
db_frame.pack(pady=10, anchor="center")
admin_frame.pack(pady=10, anchor="center")
container_frame.pack(pady=10, anchor="center")

# Checkbox centered
tk.Checkbutton(...).pack(pady=15, anchor="center")
```

### Process Label Alignment:
```python
# Before: anchor="w", justify="left"
# After:  anchor="center", justify="center"
```

## Visual Results

All three wizard pages now display with:
- Centered titles and headings
- Centered descriptions and helper text
- Centered input fields and buttons
- Centered form groups (labels remain right-aligned, inputs left-aligned within the centered frame)
- Centered navigation buttons
- Centered error and progress indicators

## Testing
- ✅ All three wizard pages render correctly with centered layout
- ✅ Navigation between pages works correctly
- ✅ Form elements remain properly aligned within centered frames
- ✅ Input field widths maintain appropriate sizing
- ✅ Layout is responsive and works with the 700x900 window size
- ✅ All previous functionality preserved (multi-page wizard, data persistence, validation)

## Compatibility
- No breaking changes
- All navigation and usability improvements from previous PRs preserved
- Backward compatible with existing workflow
- No changes to functionality, only visual layout

## Screenshots
See the following files for visual confirmation:
- `wizard_page1_centered.png` - Page 1 with centered layout
- `wizard_page2_centered.png` - Page 2 with centered layout
- `wizard_page3_centered.png` - Page 3 with centered layout
