# Progress Bar Indeterminate Mode Fix

## Problem Statement

During the restore workflow, when the bulk Docker copy operation (`docker cp`) executes to transfer files from the staging area to the Docker container, the progress bar would freeze and become unresponsive. This occurred because the `subprocess.run()` call was blocking the restore thread, preventing any UI updates during the potentially long-running transfer operation.

### Symptoms
- Progress bar stuck at approximately 70% during "Transferring to Docker container..." step
- UI appears frozen/unresponsive during large file transfers
- No visual indication that work is being performed
- User cannot tell if the application is working or has crashed

## Solution

The fix implements an indeterminate progress bar mode with background threading:

### Key Changes

1. **Indeterminate Progress Mode**: The progress bar switches to "indeterminate" (animated/marquee) mode during the bulk transfer, providing visual feedback that work is in progress.

2. **Background Threading**: The `docker cp` subprocess is executed in a separate background thread, allowing the main UI thread to remain responsive.

3. **Periodic UI Updates**: The main thread checks for completion every 100ms and calls `update_idletasks()` to keep the UI responsive and animated.

4. **Automatic Mode Switching**: Progress bar automatically switches:
   - FROM: Determinate mode (shows percentage)
   - TO: Indeterminate mode (animated marquee) during bulk copy
   - BACK TO: Determinate mode after completion

### Technical Implementation

#### Code Flow

```
1. Robocopy completes (70% progress)
2. Switch progress bar to indeterminate mode
3. Start animation (marquee effect)
4. Launch docker cp in background thread
5. Main thread monitors completion (100ms intervals)
6. Keep UI responsive with update_idletasks()
7. Docker cp completes
8. Stop animation
9. Switch back to determinate mode
10. Continue with normal progress (100%)
```

#### Key Functions

**`switch_to_indeterminate()`**
- Changes progress bar mode to 'indeterminate'
- Starts the animation with 10ms interval
- Uses `safe_widget_update()` for thread-safe UI updates

**`switch_to_determinate()`**
- Stops the animation
- Changes progress bar mode back to 'determinate'
- Restores normal progress percentage display

**`run_docker_cp()`**
- Executes docker cp in background thread
- Stores result in thread-safe dictionary
- Signals completion via threading.Event

### Modified Methods

- **`_copy_folder_with_robocopy()`** (Primary fix)
  - Lines 6982-7087 in `nextcloud_restore_and_backup-v9.py`
  - Implements indeterminate mode during bulk docker cp transfer
  - Runs docker cp in background thread
  - Maintains UI responsiveness

## Benefits

### User Experience
- ✅ **Visual Feedback**: Animated progress bar shows work is in progress
- ✅ **Responsive UI**: Interface remains interactive during long transfers
- ✅ **Clear Status**: User knows the application is working, not frozen
- ✅ **Reduced Anxiety**: No more wondering if the app has crashed

### Technical Benefits
- ✅ **Non-blocking**: Docker cp runs in background without blocking UI
- ✅ **Thread-safe**: Proper synchronization using threading.Event
- ✅ **Error Handling**: Captures and reports docker cp errors
- ✅ **Maintainable**: Clean separation of concerns

## Testing

Comprehensive unit tests were added in `tests/test_progress_indeterminate_fix.py`:

1. **Mode Switching Test**: Verifies progress bar switches between determinate and indeterminate modes
2. **Background Thread Test**: Ensures docker cp runs in background without blocking
3. **UI Responsiveness Test**: Validates main thread remains responsive with periodic updates

All tests pass successfully:
```
✅ Progress bar switches to indeterminate mode
✅ Background thread executes docker cp without blocking
✅ UI remains responsive during bulk copy operations
✅ Progress bar switches back to determinate mode
```

## Visual Comparison

### Before (Frozen UI)
```
Progress: 70% [████████████████████          ]
Status: "Transferring to Docker container..."
UI: FROZEN - no updates, appears hung
```

### After (Responsive UI)
```
Progress: [████████████████████████████] (animated)
Status: "Transferring to Docker container..."
UI: RESPONSIVE - continuous animation, can interact
```

## Platform Compatibility

- **Windows**: Uses robocopy method - benefits from this fix
- **Linux/Mac**: Uses file-by-file method - already has granular progress
- **All Platforms**: UI responsiveness improved during any blocking operations

## Performance Impact

- **Minimal overhead**: Background thread adds negligible CPU usage
- **100ms polling**: Balances responsiveness vs. resource usage
- **Memory efficient**: No significant memory overhead
- **Same transfer speed**: Docker cp performance unchanged

## Future Enhancements

Potential improvements for future versions:

1. **Progress estimation**: Show estimated bytes remaining during bulk transfer
2. **Transfer rate**: Display MB/s during docker cp operation
3. **Cancellation**: Allow user to cancel long-running transfers
4. **Fine-grained progress**: Monitor docker cp output for real-time progress

## Related Files

- **Source**: `src/nextcloud_restore_and_backup-v9.py`
- **Tests**: `tests/test_progress_indeterminate_fix.py`
- **Documentation**: This file

## References

- Issue: Progress bar freezes during "Transferring to Docker container..." step
- Framework: Tkinter (Python standard library)
- Progress Bar Widget: `ttk.Progressbar`
- Threading: Python `threading` module
