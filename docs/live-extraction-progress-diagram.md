# Live Extraction Progress - Technical Diagram

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Main UI Thread                           │
│  (Tkinter Event Loop - Always Responsive)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ User clicks "Start Restore"
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Restore Thread (Daemon)                       │
│  _restore_auto_thread(backup_path, password)                    │
│                                                                  │
│  Steps:                                                          │
│  1. Extract backup       ← WE ENHANCED THIS                     │
│  2. Detect database type                                         │
│  3. Generate docker-compose                                      │
│  4. Start containers                                             │
│  5. Copy files                                                   │
│  6. Import database                                              │
│  7. Complete restore                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Calls auto_extract_backup()
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               Extraction Thread (Daemon)                         │
│  do_extraction() inside auto_extract_backup()                   │
│                                                                  │
│  Calls: fast_extract_tar_gz(archive, dir, callback)            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Extracts files one-by-one
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              fast_extract_tar_gz()                               │
│                                                                  │
│  for each file in archive:                                      │
│    1. Extract file                                              │
│    2. Increment counter                                         │
│    3. If batch complete or last file:                           │
│       ├─→ Call progress_callback()                             │
│       └─→ Report: files_extracted, total, current_file         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Callback after each batch
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│        extraction_progress_callback()                            │
│                                                                  │
│  1. Calculate progress percentage                               │
│  2. Calculate elapsed time                                      │
│  3. Estimate remaining time                                     │
│  4. Update progress bar (10-18% range)                          │
│  5. Update status message                                       │
│  6. Update current file label                                   │
│  7. Force UI refresh (update_idletasks)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ safe_widget_update()
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UI Widgets Updated                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Progress Bar:    [████████████░░░░░░░░░░░░]  65%       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Status: Extracting files: 650/1000 |                   │  │
│  │          Elapsed: 1m 23s | Est: 48s                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Current: Extracting: user_documents/photo_123.jpg      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Progress Update Flow

### Old Approach (Before)
```
Start Extraction
      ↓
Progress: 10% ──[long wait]──→ 12% ──[long wait]──→ 14% ──[long wait]──→ 16% ──[long wait]──→ 18%
      ↓                                                                                         ↓
Extract ALL files                                                                      Complete
  (blocking)                                                                           
```

**Issues:**
- No visibility during extraction
- Fixed progress steps unrelated to actual work
- Long periods with no updates
- Users think app is frozen

### New Approach (After)
```
Start Extraction
      ↓
Progress: 10.0% → 10.8% → 11.6% → 12.4% → 13.2% → ... → 17.2% → 18.0%
      ↓           ↓       ↓       ↓       ↓           ↓       ↓
Extract batch   batch   batch   batch   batch       batch   Complete
  file 1-50    51-100  101-150 151-200 201-250    951-1000
      ↓           ↓       ↓       ↓       ↓           ↓
Callback      Callback Callback Callback Callback  Callback
  (show         (show    (show    (show    (show     (show
  progress)     progress) progress) progress) progress) progress)
```

**Benefits:**
- Continuous visibility
- Progress tied to actual work
- Frequent updates
- Users see activity

## Batch Processing Strategy

```
Archive Contents: 1,000 files

┌──────────────────────────────────────────────────────────────────┐
│  Batch 1: Files 1-50                                             │
│  ├─ Extract file 1                                               │
│  ├─ Extract file 2                                               │
│  ├─ ...                                                           │
│  ├─ Extract file 50                                              │
│  └─ Callback: progress_callback(50, 1000, "file_50.txt")        │
│     └─→ Update UI: "50/1000 files | Elapsed: 2s | Est: 38s"     │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│  Batch 2: Files 51-100                                           │
│  ├─ Extract file 51                                              │
│  ├─ Extract file 52                                              │
│  ├─ ...                                                           │
│  ├─ Extract file 100                                             │
│  └─ Callback: progress_callback(100, 1000, "file_100.txt")      │
│     └─→ Update UI: "100/1000 files | Elapsed: 4s | Est: 36s"    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
                            [...]
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│  Batch 20: Files 951-1000                                        │
│  ├─ Extract file 951                                             │
│  ├─ Extract file 952                                             │
│  ├─ ...                                                           │
│  ├─ Extract file 1000                                            │
│  └─ Callback: progress_callback(1000, 1000, "file_1000.txt")    │
│     └─→ Update UI: "1000/1000 files | Elapsed: 40s | Complete!" │
└──────────────────────────────────────────────────────────────────┘
```

**Batch Size Configuration:**
- Small archives (<1,000 files): batch_size = 10 (more frequent updates)
- Medium archives (1,000-10,000 files): batch_size = 50 (default)
- Large archives (>10,000 files): batch_size = 100 (less UI overhead)

## Time Estimation Algorithm

```python
def calculate_time_estimate(files_extracted, total_files, elapsed_time):
    """
    Estimate remaining time based on extraction rate
    """
    if files_extracted == 0 or elapsed_time == 0:
        return "Calculating..."
    
    # Calculate extraction rate (files per second)
    rate = files_extracted / elapsed_time
    
    # Calculate remaining files
    remaining_files = total_files - files_extracted
    
    # Estimate remaining time
    est_remaining = remaining_files / rate
    
    # Format nicely
    return format_time(est_remaining)
```

**Example:**
- 400 files extracted in 20 seconds
- Rate: 400 / 20 = 20 files/second
- Remaining: 1000 - 400 = 600 files
- Estimate: 600 / 20 = 30 seconds

## Thread Safety

All UI updates go through `safe_widget_update()`:

```python
def safe_widget_update(widget, update_func, error_context):
    """
    Safely update a widget from a background thread.
    Catches TclError if widget has been destroyed.
    """
    try:
        update_func()
    except tk.TclError as e:
        logger.debug(f"TclError during {error_context}: {e}")
        # Widget destroyed, ignore
```

This prevents crashes if:
- User closes window during extraction
- Widget is destroyed mid-update
- Thread outlives the UI

## Progress Percentage Mapping

The extraction phase uses 10-18% of the total restore progress:

```
Total Restore Progress: 0% ──────────────────────────────────────→ 100%

Extraction Phase (8% range):
  0-10%:   Decryption (if needed)
  10-18%:  File extraction ← ENHANCED
  18-20%:  Database detection
  20-40%:  Docker setup
  40-60%:  File copying
  60-80%:  Database import
  80-100%: Finalization

File Extraction Detail (10-18% range):
  file_percent = (files_extracted / total_files) * 100
  progress_val = 10 + int((file_percent / 100) * 8)
  
  Examples:
    0/1000 files (0%)    → 10.0% total progress
    250/1000 files (25%) → 12.0% total progress
    500/1000 files (50%) → 14.0% total progress
    750/1000 files (75%) → 16.0% total progress
    1000/1000 files (100%) → 18.0% total progress
```

## Performance Considerations

### File Extraction Speed
- **Small files** (<1KB): ~10,000 files/second
- **Medium files** (1KB-1MB): ~1,000 files/second
- **Large files** (>1MB): ~100 files/second

### UI Update Frequency
- **Batch size 10**: Update every ~0.1-1 second (small archives)
- **Batch size 50**: Update every ~0.5-5 seconds (medium archives)
- **Batch size 100**: Update every ~1-10 seconds (large archives)

### Memory Usage
- Extract one file at a time (low memory footprint)
- No need to load entire archive into memory
- Callback is lightweight (just counters)

## Error Handling

```
┌─────────────────────────────────────────────┐
│  Start Extraction                           │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  Try: Extract file                          │
└─────────────────────────────────────────────┘
              │
              ├──────────────────────────────┐
              │                              │
              ▼                              ▼
    ┌─────────────────┐        ┌──────────────────────────┐
    │  Success        │        │  Exception               │
    │  - Continue     │        │  - Catch in do_extraction│
    │  - Update count │        │  - Set error flag        │
    │  - Callback     │        │  - Return to caller      │
    └─────────────────┘        └──────────────────────────┘
              │                              │
              ▼                              ▼
    ┌─────────────────┐        ┌──────────────────────────┐
    │  Next file      │        │  Show error dialog       │
    └─────────────────┘        │  Clean up temp files     │
                               │  Return None             │
                               └──────────────────────────┘
```

**Error Types Handled:**
- `tarfile.ReadError`: Corrupted archive
- `OSError` (errno 28): No space left on device
- `OSError` (errno 13): Permission denied
- `Exception`: General extraction failure

All errors are caught, logged, and displayed to user with helpful messages.
