# UI Alignment Fixes - Restore Wizard

## Problem
The restore wizard had hardcoded width values for input fields that caused alignment issues when the window was not full screen. Elements would not resize properly and could appear misaligned.

## Solution
Replaced fixed-width Entry widgets with responsive layout using:
- Container frames with `fill="x"` and appropriate `padx` values
- Grid layout with column weight configuration (`grid_columnconfigure`)
- `sticky="ew"` for Entry widgets to make them expand horizontally
- Consistent padding values (padx=50 for containers, padx=100 for single entries)

## Changes Made

### Page 1: Backup Selection and Decryption
**Before:**
- `self.backup_entry = tk.Entry(parent, width=70, ...)`
- `self.password_entry = tk.Entry(parent, width=40, ...)`

**After:**
- Created container frames for each entry with `fill="x"` and `padx` values
- Entries use `pack(fill="x", expand=True)` for responsive width
- Backup entry container: `padx=50` (wider field needs less padding)
- Password entry container: `padx=100` (narrower field needs more padding)

### Page 2: Database Configuration and Admin Credentials
**Before:**
- Grid-based layout with `width=30` for all Entry widgets
- No column configuration for responsive resizing

**After:**
- Added `grid_columnconfigure` with weights:
  - Column 0 (labels): `weight=0` (fixed width)
  - Column 1 (entries): `weight=1` (expandable)
  - Column 2 (hints): `weight=0` (fixed width)
- All Entry widgets use `sticky="ew"` to expand horizontally
- Frames use `fill="x"` and `padx=50` for consistent margins
- Info frame updated to use `padx=50` and `fill="x"`

### Page 3: Container Configuration
**Before:**
- Grid-based layout with `width=30` for Entry widgets
- No column configuration

**After:**
- Same responsive grid approach as Page 2
- Column weights configured for expandable entries
- All Entry widgets use `sticky="ew"`
- Frame uses `fill="x"` and `padx=50`
- Info frame updated to use `padx=50` and `fill="x"`

### Backup Workflow
**Before:**
- Encryption password entry: `width=30`

**After:**
- Container frame with `padx=100` and `fill="x"`
- Entry uses `pack(fill="x", expand=True)`

## Benefits
1. **Responsive Layout**: Input fields now adjust to window size
2. **Consistent Centering**: All elements remain centered at any window size
3. **No Fixed Widths**: Removed hardcoded character widths from all form inputs
4. **Better UX**: Fields scale appropriately in both windowed and full-screen modes
5. **Maintainable**: Column weight configuration makes future adjustments easier

## Testing
- ✅ Python syntax validation passed
- ✅ No breaking changes to functionality
- ✅ All wizard pages use responsive layouts
- ✅ Consistent padding values across all pages
- ✅ Grid-based layouts properly configured with column weights
