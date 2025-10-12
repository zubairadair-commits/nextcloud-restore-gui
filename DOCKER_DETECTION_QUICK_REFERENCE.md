# Docker Detection - Quick Reference

## What Changed?

The Nextcloud Restore & Backup Utility now checks if Docker is running **before** attempting any operations.

## For Users

### New Behavior
- ✅ **Backup/Restore/New Instance**: All check Docker first
- ✅ **Clear Dialog**: Shows "Docker Not Running" with helpful actions
- ✅ **Auto-Start** (Windows/Mac): Can launch Docker Desktop automatically
- ✅ **Retry Option**: Easy to retry after starting Docker
- ✅ **No Confusion**: No more cryptic container errors

### What You'll See

**When Docker is Running:**
- Normal operation, no changes to workflow

**When Docker is NOT Running:**
- Dialog appears: "⚠ Docker Not Running"
- Options provided:
  - **Start Docker Desktop** (Windows/Mac) - Launches Docker for you
  - **Retry** - Check again after starting Docker
  - **Cancel** - Return to main menu

### How to Use

1. **Click any operation** (Backup, Restore, or New Instance)
2. **If Docker not running**:
   - Windows/Mac: Click "Start Docker Desktop"
   - Linux: Run `sudo systemctl start docker` in terminal
   - Wait 10-20 seconds for Docker to start
   - Click "Retry"
3. **Operation proceeds** normally

## For Developers

### Key Functions Added

```python
# Check if Docker is running
is_docker_running() -> bool

# Get Docker Desktop path
get_docker_desktop_path() -> str | None

# Launch Docker Desktop
start_docker_desktop() -> bool

# Show Docker prompt dialog
prompt_start_docker(parent) -> bool

# Class method: check with retry logic
check_docker_running(self) -> bool
```

### Integration Points

**Before each operation:**
```python
def start_backup(self):
    if not self.check_docker_running():
        self.show_landing()
        return
    # ... proceed with backup

def start_restore(self):
    if not self.check_docker_running():
        self.show_landing()
        return
    # ... proceed with restore

def start_new_instance_workflow(self):
    if not self.check_docker_running():
        self.show_landing()
        return
    # ... proceed with new instance
```

### Code Location

- **Main file**: `nextcloud_restore_and_backup-v9.py`
- **New imports**: Lines 13-14 (`platform`, `sys`)
- **Docker functions**: Lines 35-244
- **Class method**: Lines 980-1011
- **Integration**: Lines 1040, 1221, 3068

## Platform Support

| Platform | Detection | Auto-Start | Manual Command |
|----------|-----------|------------|----------------|
| Windows  | ✅        | ✅         | Start Docker Desktop from Start Menu |
| macOS    | ✅        | ✅         | Open Docker from Applications |
| Linux    | ✅        | ❌         | `sudo systemctl start docker` |

## Testing

**Run the test:**
```bash
python3 test_docker_detection.py
```

**Expected output:**
```
✓ Platform: Linux
✓ Docker installed: Docker version 28.0.4
✓ Docker daemon is running
✓ Docker API accessible
✓ All checks passed - Docker is ready
```

## Common Scenarios

### 1. Docker Running
```
User Action: Click "Backup Now"
Result: Backup proceeds immediately (no dialogs)
```

### 2. Docker Not Running - Windows/Mac
```
User Action: Click "Restore from Backup"
Result: "Docker Not Running" dialog appears
User Action: Click "Start Docker Desktop"
Result: Docker launches, wait 10-20 seconds
User Action: Click "Retry"
Result: Restore wizard opens
```

### 3. Docker Not Running - Linux
```
User Action: Click "Start New Instance"
Result: "Docker Not Running" dialog with instructions
User Action: In terminal: sudo systemctl start docker
User Action: Click "Retry"
Result: Port selection screen appears
```

### 4. User Cancels
```
User Action: Click any operation
Result: "Docker Not Running" dialog appears
User Action: Click "Cancel"
Result: Returns to main menu (no errors)
```

## Troubleshooting

### Issue: "Could not start Docker Desktop automatically"
**Fix**: Start Docker Desktop manually, then click "Retry"

### Issue: Docker check times out
**Fix**: Restart Docker daemon/Desktop

### Issue: Permission denied (Linux)
**Fix**: `sudo usermod -aG docker $USER` (then log out/in)

## Files Modified

- ✅ `nextcloud_restore_and_backup-v9.py` - Added Docker detection
- ✅ `test_docker_detection.py` - New test file
- ✅ `DOCKER_DETECTION_FEATURE.md` - Full documentation
- ✅ `DOCKER_DETECTION_QUICK_REFERENCE.md` - This file

## Summary

**Before**: Operations failed with confusing errors when Docker not running

**After**: Clear prompt with helpful actions to start Docker

**Impact**: Better user experience, fewer support issues, professional behavior
