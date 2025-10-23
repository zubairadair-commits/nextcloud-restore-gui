# Live File-by-File Copying Progress Implementation

## Overview

This document describes the implementation of live progress updates during the file copying phase of the Nextcloud restore process. The enhancement provides real-time feedback showing the number of files copied, current file being copied, and accurate time estimates.

## Problem Statement

Previously, the copying phase (30-60% of the restore process) showed progress updates based on elapsed time estimates. Users had no visibility into which files were being copied, and the progress bar could appear "stuck" at a single value for extended periods.

## Solution

Implemented file-by-file copying with live progress updates that:
- Shows exact file count (e.g., "Copying data: 45/120 files")
- Displays current file being copied
- Provides accurate elapsed and estimated time
- Updates progress bar smoothly and continuously
- Uses thread-safe UI updates to keep the application responsive

## Technical Implementation

### 1. New Function: `copy_folder_to_container_with_progress`

**Location**: `src/nextcloud_restore_and_backup-v9.py` (lines 6864-6958)

**Purpose**: Copy a folder to a Docker container with live file-by-file progress updates.

**Key Features**:
- Recursively walks through folder structure
- Copies files individually using `docker cp`
- Creates directory structure as needed in the container
- Calls progress callback every 5 files (configurable)
- Tracks: total files, files copied, current file, elapsed time

**Signature**:
```python
def copy_folder_to_container_with_progress(
    self, 
    local_path,           # Local folder path to copy from
    container_name,       # Docker container name
    container_path,       # Destination path in container
    folder_name,          # Name of folder (for display)
    progress_start,       # Starting progress % (e.g., 30)
    progress_end,         # Ending progress % (e.g., 37)
    progress_callback=None # Optional callback function
)
```

**Progress Callback Parameters**:
```python
progress_callback(
    files_copied,    # Number of files copied so far
    total_files,     # Total files to copy
    current_file,    # Relative path of current file
    percent,         # Current progress percentage
    elapsed          # Elapsed time in seconds
)
```

### 2. Updated Copying Phase

**Location**: `src/nextcloud_restore_and_backup-v9.py` (lines 8721-8873)

**Changes**:
1. **Pre-count files**: Count all files before copying to show accurate totals
2. **Progress callback**: Define callback function for thread-safe UI updates
3. **Integration**: Use new function for each folder (config, data, apps, custom_apps)
4. **UI updates**: Update progress bar, status message, and current file label

**Progress Callback Implementation**:
```python
def copy_progress_callback(files_copied, total_files, current_file, percent, elapsed):
    # Calculate overall progress
    overall_files_copied = files_copied_so_far + files_copied
    
    # Format current file for display (truncate if needed)
    file_display = current_file
    if len(file_display) > 60:
        file_display = "..." + file_display[-57:]
    
    # Calculate time estimates
    elapsed_str = self._format_time(elapsed)
    rate = files_copied / elapsed if elapsed > 0 else 0
    remaining_files = total_files - files_copied
    est_remaining = remaining_files / rate if rate > 0 else 0
    est_str = self._format_time(est_remaining)
    
    # Build status message
    status_msg = f"Copying {folder}: {files_copied}/{total_files} files | Elapsed: {elapsed_str} | Est: {est_str}"
    
    # Thread-safe UI update
    def update_ui():
        self.set_restore_progress(percent, status_msg)
        self.process_label.config(text=f"Copying: {file_display}")
        if self.winfo_exists():
            self.update_idletasks()
    
    self.after(0, update_ui)  # Schedule on main thread
```

### 3. Thread Safety

All UI updates from the worker thread are scheduled on the main thread using `self.after(0, update_ui)`. This follows the same proven pattern used in the extraction progress implementation.

**Safety Measures**:
- All widget updates wrapped in try/except blocks
- Catches `tk.TclError` if window is closed
- Uses `self.winfo_exists()` before calling `update_idletasks()`
- No direct widget manipulation from worker thread

## Progress Ranges

The restore process uses the following progress ranges:

| Range   | Phase                  | Status                                    |
|---------|------------------------|-------------------------------------------|
| 0-20%   | Extraction             | ✓ Already enhanced with live updates      |
| 20-30%  | Transition             | Container setup                           |
| 30-60%  | **Copying files**      | ✨ **NEW: Live file-by-file updates**     |
| 60-75%  | Database restore       | Existing implementation                   |
| 75-100% | Config & finalization  | Existing implementation                   |

## User Experience Improvements

### Before
```
[37%] Copying data (128.5MB)...
[37%] Copying data (128.5MB)...  [stuck, no visible progress]
[37%] Copying data (128.5MB)...
[45%] ✓ Copied data folder
```

### After
```
[37%] Copying data: 5/120 files | Elapsed: 2s | Est: 45s
      Copying: data/admin/files/document_0.txt
[38%] Copying data: 15/120 files | Elapsed: 6s | Est: 42s
      Copying: data/admin/files/photo_5.jpg
[39%] Copying data: 25/120 files | Elapsed: 10s | Est: 38s
      Copying: data/user1/files/spreadsheet.xlsx
[41%] Copying data: 45/120 files | Elapsed: 18s | Est: 30s
      Copying: data/user1/cache/thumbnail_123.png
[45%] ✓ Copied data folder (120 files)
```

## Testing

### Automated Tests

Created `tests/test_copying_progress.py` with 9 test cases:

1. ✓ Syntax validation
2. ✓ Function existence check
3. ✓ Progress callback parameter
4. ✓ File-by-file copying implementation
5. ✓ Progress callback invocation
6. ✓ Thread-safe UI updates
7. ✓ Integration with restore process
8. ✓ Progress range configuration
9. ✓ Current file display in UI

**Result**: All tests pass

### Visual Demo

Created `tests/demo_copying_progress.py` that simulates the copying phase:
- Creates realistic test folder structure (237 files across 4 folders)
- Simulates copying with progress updates
- Shows before/after comparison
- Demonstrates all features

**Run demo**: `python3 tests/demo_copying_progress.py`

### Security Analysis

Ran CodeQL security analysis on all changes:
- **Result**: 0 alerts
- No security vulnerabilities introduced

## Performance Considerations

### Update Frequency

Progress callback is invoked every 5 files to balance between:
- **Responsiveness**: Frequent enough for smooth progress bar updates
- **Performance**: Not too frequent to avoid overwhelming the UI

Adjustable via the condition in `copy_folder_to_container_with_progress`:
```python
if progress_callback and (files_copied % 5 == 0 or files_copied == total_files):
    progress_callback(...)
```

### Docker CP Performance

Files are copied one by one using `docker cp`. This approach:
- **Pros**: Accurate progress tracking, better visibility
- **Cons**: Slightly slower than bulk copy for many small files
- **Mitigation**: Directory structure is created once, then files are copied

For most use cases (hundreds to thousands of files), the visibility benefit outweighs the small performance overhead.

## Code Locations

| Component | File | Lines |
|-----------|------|-------|
| Copy function | `src/nextcloud_restore_and_backup-v9.py` | 6864-6958 |
| Restore integration | `src/nextcloud_restore_and_backup-v9.py` | 8721-8873 |
| Automated tests | `tests/test_copying_progress.py` | Complete file |
| Demo script | `tests/demo_copying_progress.py` | Complete file |

## Future Enhancements

Possible improvements for future versions:

1. **Batch copying**: Copy multiple small files at once for better performance
2. **Size-based progress**: Show bytes copied in addition to file count
3. **Parallel copying**: Use multiple threads for faster copying (requires careful coordination)
4. **Resume capability**: Support resuming interrupted copies
5. **Compression**: Compress before copying for faster transfer

## Related Documentation

- `LIVE_EXTRACTION_PROGRESS_SUMMARY.md` - Similar enhancement for extraction phase
- `ENHANCED_PROGRESS_PIPELINE.md` - Overall progress tracking architecture
- `GUI_ENHANCEMENTS_SUMMARY.md` - General UI improvements

## Conclusion

This enhancement significantly improves the user experience during the restore process by providing real-time visibility into file copying operations. The implementation follows established patterns from the extraction progress enhancement, ensuring consistency and reliability.

Users can now see exactly which files are being copied, how many remain, and accurate time estimates - eliminating the frustration of an apparently "stuck" progress bar.
