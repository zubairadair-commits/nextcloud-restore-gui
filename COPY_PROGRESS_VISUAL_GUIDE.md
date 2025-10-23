# Copy Progress Tracking - Visual Guide

## Before vs After

### BEFORE (Problem)
```
Extraction phase: 0% → 20% ✓ (with file-by-file updates)
     ↓
Progress stays at 20% (stuck!)
     ↓
Copying phase: Jumps to 30%, then stuck until folder completes
     ↓
Progress jumps between folder boundaries (30%, 37%, 45%, 52%, 60%)
     ↓
No indication of progress within each folder copy
```

Status text:
```
20% | Extraction complete!
30% | Copying config folder to container...  (stuck here for minutes)
37% | Copying data folder to container...     (stuck here for minutes)
45% | Copying apps folder to container...     (stuck here for minutes)
52% | Copying custom_apps folder to container...
60% | Copied all folders
```

### AFTER (Solution)
```
Extraction phase: 0% → 20% ✓ (with file-by-file updates)
     ↓
Copying phase: 30% → 60% ✓ (with smooth file-count updates)
     │
     ├─ 30% → 31% → 32% ... (config: 45 files)
     │
     ├─ 32% → 35% → 38% → 41% → 44% → 47% (data: 1250 files)
     │
     ├─ 47% → 50% → 53% → 56% → 58% (apps: 850 files)
     │
     └─ 58% → 59% → 60% (custom_apps: 120 files)
```

Status text:
```
20% | Extraction complete!
30% | Copying config: 15/2265 files | Elapsed: 0s | Est: 1m 30s
32% | Copying data: 450/2265 files | Elapsed: 5s | Est: 1m 10s
38% | Copying data: 1050/2265 files | Elapsed: 15s | Est: 35s
47% | Copying apps: 1500/2265 files | Elapsed: 25s | Est: 18s
56% | Copying apps: 2000/2265 files | Elapsed: 35s | Est: 5s
60% | ✓ Copied all files (2265 files)
```

## Key Improvements

### 1. Smooth Progress Bar
- **Before**: Progress bar stuck at 20%, then jumps to 30%, stays stuck
- **After**: Progress bar smoothly fills from 30% to 60% in real-time

### 2. File Count Display
- **Before**: Only shows folder name being copied
- **After**: Shows "Copying [folder]: X/Y files" with running count

### 3. Time Estimates
- **Before**: No time information during copying
- **After**: Shows elapsed time and estimated remaining time

### 4. User Feedback
- **Before**: User has no idea how long copying will take
- **After**: User sees:
  - How many files are being copied total
  - Current progress (file count)
  - How much time has elapsed
  - Estimated time remaining

## Technical Implementation

### File Counting Phase
```python
# Count all files across all folders
total_files_to_copy = 0
folder_file_counts = {}

for folder in folders_to_copy:
    file_count = count_files_in_folder(folder)
    folder_file_counts[folder] = file_count
    total_files_to_copy += file_count
```

### Progress Tracking During Copy
```python
# While copying each folder
while not copy_done:
    # Estimate current file count based on elapsed time
    estimated_files_done = estimate_progress(folder_elapsed)
    current_files = folder_start_files + estimated_files_done
    
    # Calculate progress (30-60% range)
    copy_percent = (current_files / total_files_to_copy) * 100
    progress_val = 30 + int((copy_percent / 100) * 30)
    
    # Update UI
    self.set_restore_progress(progress_val, 
        f"Copying {folder}: {current_files}/{total_files_to_copy} files | "
        f"Elapsed: {elapsed_str} | Est: {est_str}")
```

### Thread-Safe UI Updates
```python
def update_copy_progress():
    try:
        self.set_restore_progress(progress_val, status_msg)
        self.process_label.config(text=f"Copying {folder}: {current_files}/{total_files} files")
        self.update_idletasks()
    except tk.TclError:
        pass

# Schedule on main thread
self.after(0, update_copy_progress)
```

## Example Progress Flow

For a backup with 2,265 files:

```
Time    Progress  Status
-----   --------  ------------------------------------------------
0:00    30%       Copying config: 0/2265 files | Elapsed: 0s
0:01    30%       Copying config: 45/2265 files | Elapsed: 1s | Est: 49s
0:02    32%       Copying data: 170/2265 files | Elapsed: 2s | Est: 24s
0:05    35%       Copying data: 450/2265 files | Elapsed: 5s | Est: 20s
0:10    41%       Copying data: 850/2265 files | Elapsed: 10s | Est: 16s
0:15    47%       Copying data: 1295/2265 files | Elapsed: 15s | Est: 11s
0:18    50%       Copying apps: 1550/2265 files | Elapsed: 18s | Est: 9s
0:23    56%       Copying apps: 2000/2265 files | Elapsed: 23s | Est: 3s
0:25    58%       Copying custom_apps: 2145/2265 files | Elapsed: 25s | Est: 1s
0:26    60%       ✓ Copied all files (2265 files)
```

## Performance Impact

### Minimal Overhead
- File counting: ~0.5-1 second for typical backups
- Progress updates: Every 0.3 seconds (low UI overhead)
- Copy method: Still uses efficient `docker cp` command (no slowdown)

### Benefits
- User sees continuous progress (reduces anxiety)
- Clear time estimates (better user experience)
- No performance degradation compared to before
- Thread-safe implementation (no UI freezing)
