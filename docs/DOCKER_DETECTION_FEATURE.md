# Docker Detection Feature

## Overview

The Nextcloud Restore & Backup Utility now includes automatic Docker detection to ensure Docker is running before attempting any container operations. This prevents confusing error messages and provides clear guidance to users when Docker is not available.

## Features

### 1. Cross-Platform Docker Detection

The utility automatically detects whether Docker is running on:
- **Windows**: Checks for Docker Desktop
- **macOS**: Checks for Docker Desktop
- **Linux**: Checks for Docker daemon

### 2. Automatic Detection on Startup

Before any operation (Backup, Restore, or New Instance), the utility checks:
1. If Docker is installed
2. If Docker daemon/Desktop is running
3. If Docker API is accessible

### 3. User-Friendly Prompts

When Docker is not running, users see a clear dialog with:
- **Explanation**: Why Docker is needed
- **Action buttons**: 
  - "Start Docker Desktop" (Windows/Mac only) - Attempts to launch Docker automatically
  - "Retry" - Checks Docker status again
  - "Cancel" - Returns to main menu

### 4. Automatic Docker Desktop Launch (Windows/Mac)

On Windows and macOS, the utility can automatically start Docker Desktop:
- Detects Docker Desktop installation path
- Launches Docker Desktop with user confirmation
- Provides visual feedback while Docker starts
- Waits for user to retry after Docker has started

### 5. Helpful Error Messages

When Docker cannot be started automatically, users receive:
- Clear error messages
- Platform-specific instructions
- Commands to manually start Docker

## Technical Implementation

### Core Functions

#### `is_docker_running()`
```python
def is_docker_running():
    """
    Check if Docker daemon is running by attempting a simple Docker command.
    Returns: True if Docker is running, False otherwise
    """
```
- Executes `docker ps` command
- Returns True if command succeeds
- Returns False if Docker is not accessible
- Includes 5-second timeout to prevent hanging

#### `get_docker_desktop_path()`
```python
def get_docker_desktop_path():
    """
    Get the path to Docker Desktop executable based on the platform.
    Returns: Path to Docker Desktop or None if not found
    """
```
- **Windows**: Checks common installation paths
  - `C:\Program Files\Docker\Docker\Docker Desktop.exe`
  - Uses environment variables for flexibility
- **macOS**: Checks `/Applications/Docker.app`
- **Linux**: Returns None (uses daemon instead)

#### `start_docker_desktop()`
```python
def start_docker_desktop():
    """
    Attempt to start Docker Desktop based on the platform.
    Returns: True if launch was attempted, False otherwise
    """
```
- Launches Docker Desktop executable
- **Windows**: Direct executable launch
- **macOS**: Uses `open -a Docker` command
- Returns success/failure status

#### `prompt_start_docker(parent)`
```python
def prompt_start_docker(parent):
    """
    Show a dialog prompting the user to start Docker.
    On Windows/Mac, offer to start Docker Desktop automatically.
    Returns: True if user wants to retry, False to cancel
    """
```
- Creates modal dialog window
- Shows platform-specific messages
- Provides appropriate action buttons
- Handles user interaction
- Returns retry decision

### Class Method Integration

#### `check_docker_running()`
```python
def check_docker_running(self):
    """
    Check if Docker is running and prompt user if not.
    Returns: True if Docker is running, False if user cancels
    """
```
- Called before all major operations
- Implements retry logic (up to 3 attempts)
- Shows user prompts when needed
- Returns True if Docker is available
- Returns False if user cancels

### Integration Points

The Docker check is now integrated into:

1. **`start_backup()`**
   - Checks Docker before selecting backup folder
   - Prevents backup attempts when Docker is not running

2. **`start_restore()`**
   - Checks Docker before starting restore wizard
   - Ensures containers can be managed during restore

3. **`start_new_instance_workflow()`**
   - Checks Docker installation first
   - Then checks if Docker is running
   - Prevents new instance creation when Docker unavailable

## User Experience

### Scenario 1: Docker Running (Happy Path)
```
1. User clicks "Start New Nextcloud Instance"
2. Docker check passes silently
3. User proceeds to port selection
4. Nextcloud container starts successfully
```

### Scenario 2: Docker Not Running (Windows/Mac)
```
1. User clicks "Backup Now"
2. Dialog appears: "Docker Not Running"
3. User clicks "Start Docker Desktop"
4. Docker Desktop launches
5. Message shows: "Docker Desktop is starting..."
6. User waits 10-20 seconds
7. User clicks "Retry"
8. Docker check passes
9. Backup proceeds normally
```

### Scenario 3: Docker Not Running (Linux)
```
1. User clicks "Restore from Backup"
2. Dialog appears: "Docker Not Running"
3. Instructions show: "sudo systemctl start docker"
4. User starts Docker in terminal
5. User clicks "Retry"
6. Docker check passes
7. Restore wizard opens
```

### Scenario 4: User Cancels
```
1. User clicks any operation
2. Docker not running dialog appears
3. User clicks "Cancel"
4. Returns to main menu
5. No error messages or confusion
```

## Benefits

### For End Users
- **Clear Communication**: No confusing "container not found" errors
- **Guided Actions**: Clear steps to resolve Docker issues
- **Automatic Help**: One-click Docker Desktop launch on Windows/Mac
- **Less Frustration**: Prevents wasted time on operations that will fail

### For System Administrators
- **Predictable Behavior**: Consistent Docker checks across all operations
- **Better Logging**: Clear messages about Docker availability
- **Easy Troubleshooting**: Users can self-diagnose Docker issues

### For Developers
- **Reusable Functions**: Docker detection functions work independently
- **Cross-Platform**: Single codebase works on Windows, Mac, and Linux
- **Extensible**: Easy to add more Docker checks or features
- **Tested**: Comprehensive test coverage

## Configuration

No configuration required! The feature works out-of-the-box with:
- Standard Docker Desktop installations
- Standard Docker daemon setups
- Default installation paths

## Error Handling

The implementation includes robust error handling:

1. **Timeout Protection**: 5-second timeout on Docker commands
2. **Exception Handling**: Graceful handling of all subprocess errors
3. **Retry Logic**: Up to 3 retry attempts with delays
4. **User Control**: User can always cancel and return to main menu
5. **Informative Messages**: Clear error messages with recovery steps

## Platform-Specific Notes

### Windows
- Detects Docker Desktop at standard installation paths
- Can launch Docker Desktop automatically
- Supports both Program Files locations
- Uses environment variable expansion for flexibility

### macOS
- Detects Docker.app in Applications folder
- Uses `open -a Docker` to launch
- Standard macOS application launching

### Linux
- Focuses on Docker daemon status
- Provides systemctl commands for users
- Does not attempt automatic Docker Desktop launch
- Recommends manual daemon start

## Testing

### Unit Tests
The `test_docker_detection.py` script verifies:
- Platform detection
- Docker installation check
- Docker daemon running check
- Docker Desktop path detection
- Docker API accessibility
- Container listing

### Manual Testing Checklist
- [ ] Test with Docker running
- [ ] Test with Docker not running
- [ ] Test "Start Docker Desktop" button (Windows/Mac)
- [ ] Test "Retry" button after starting Docker
- [ ] Test "Cancel" button returns to main menu
- [ ] Test all three operations (Backup, Restore, New Instance)
- [ ] Test on Windows
- [ ] Test on macOS
- [ ] Test on Linux

## Future Enhancements

Potential improvements for future versions:

1. **Docker Compose Detection**: Check for docker-compose availability
2. **Resource Checks**: Verify Docker has enough memory/disk space
3. **Version Compatibility**: Check Docker version meets minimum requirements
4. **Background Monitoring**: Monitor Docker status during long operations
5. **Smart Retry**: Automatically retry when Docker becomes available
6. **Status Indicator**: Show Docker status in UI (green/red indicator)

## Troubleshooting

### Docker Desktop Not Found (Windows/Mac)
**Problem**: "Could not start Docker Desktop automatically"

**Solution**: 
1. Verify Docker Desktop is installed
2. Check installation path matches expected location
3. Manually start Docker Desktop from Start menu/Applications
4. Click "Retry" in the dialog

### Docker Command Times Out
**Problem**: Docker check hangs or times out

**Solution**:
1. Check Docker daemon is responsive: `docker ps`
2. Restart Docker service/daemon
3. Check Docker logs for errors
4. Ensure Docker socket is accessible

### Permission Denied (Linux)
**Problem**: Docker commands fail with permission errors

**Solution**:
1. Add user to docker group: `sudo usermod -aG docker $USER`
2. Log out and back in
3. Or use: `sudo systemctl start docker`
4. Verify: `docker ps`

## Related Files

- `nextcloud_restore_and_backup-v9.py` - Main application with Docker detection
- `test_docker_detection.py` - Test script for Docker detection
- `DOCKER_DETECTION_FEATURE.md` - This documentation file

## Support

If you encounter issues with Docker detection:

1. Run the test script: `python3 test_docker_detection.py`
2. Check Docker is installed: `docker --version`
3. Check Docker is running: `docker ps`
4. Check Docker logs for errors
5. Consult platform-specific Docker documentation

## Summary

The Docker detection feature ensures users have a smooth experience by:
- ✅ Detecting Docker availability before operations
- ✅ Providing clear, actionable error messages
- ✅ Offering automatic Docker Desktop launch
- ✅ Supporting Windows, macOS, and Linux
- ✅ Preventing confusing error messages
- ✅ Guiding users to resolve Docker issues

This enhancement makes the Nextcloud Restore & Backup Utility more robust, user-friendly, and professional.
