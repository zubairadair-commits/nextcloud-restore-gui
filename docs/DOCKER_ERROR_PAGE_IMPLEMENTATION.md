# Docker Error Page Implementation

## Overview

This document describes the implementation of the Docker error page feature, which replaces popup error dialogs with a dedicated error page within the main GUI.

## Problem Statement

Previously, when Docker errors occurred during the restore wizard (such as "Docker Not Running" or container creation failures), the errors were shown in separate popup windows. This approach interrupted the user flow and required closing dialogs to return to the main interface.

The new implementation displays these errors as a dedicated page within the GUI itself, maintaining the same visual style and information while providing a more integrated user experience.

## Implementation Details

### New Method: `show_docker_error_page()`

**Location:** `src/nextcloud_restore_and_backup-v9.py` (line ~8380)

**Signature:**
```python
def show_docker_error_page(self, error_info, stderr_output, container_name, port):
    """
    Show Docker error as a dedicated page within the main GUI (not a popup dialog).
    
    Args:
        error_info: Dictionary with error analysis from analyze_docker_error()
        stderr_output: Raw stderr output from Docker command
        container_name: Name of the container that failed
        port: Port that was being used (or None)
    """
```

**Key Features:**
1. **Error Information Display**
   - Error type (port conflict, container name conflict, etc.)
   - Container name and port information
   - User-friendly error message
   - Detailed suggested actions
   - Alternative port suggestions (when applicable)

2. **Inline Docker Error Logs**
   - Raw Docker error output displayed in a scrollable text widget
   - No need to open separate dialogs to view error details

3. **Navigation**
   - "Return to Main Menu" button for easy navigation
   - "Open Error Log Folder" button to access log files
   - Integrated into the main page navigation system

4. **Visual Design**
   - Maintains the same visual style as the original error dialogs
   - Uses color-coded sections for different information types:
     - Red header for error indication
     - Light red background for error description
     - Green background for suggested actions
     - Yellow background for alternative port suggestions
   - Scrollable content to accommodate long error messages

### Changes to Error Handling Flow

**Previous Flow:**
```
Docker Error → show_docker_container_error_dialog() → Popup Window → User closes → Back to wizard
```

**New Flow:**
```
Docker Error → show_docker_error_page() → Error Page (in main GUI) → Return to Main Menu → Landing page
```

### Code Changes

1. **Method Calls Replaced (4 locations):**
   - Line ~6491: Nextcloud image pull error
   - Line ~6558: Nextcloud container creation error
   - Line ~6645: Database image pull error
   - Line ~6699: Database container creation error

2. **Page Navigation Updates:**
   - Added `self.current_page = 'docker_error'` tracking
   - Updated `refresh_current_page()` method to handle docker_error page refresh

3. **Error Data Storage:**
   - Added `self.current_docker_error` dictionary to store error information
   - Allows page refresh and theme changes to preserve error state

### UI Components

The error page includes the following sections:

1. **Header Section**
   - Large red banner with "❌ Docker Container Failed" text
   - Immediately visible to indicate error state

2. **Error Type Section**
   - Displays the error type in a readable format
   - Example: "Port Conflict" instead of "port_conflict"

3. **Container Information Panel**
   - Shows container name and port
   - Bordered info box for easy identification

4. **Error Description Panel**
   - Light red background
   - Clear error message explaining what went wrong

5. **Suggested Action Panel**
   - Green background to indicate actionable items
   - Step-by-step instructions for resolution
   - Command examples where applicable

6. **Alternative Port Suggestion Panel** (conditional)
   - Yellow background
   - Only shown for port conflict errors
   - Suggests specific alternative ports

7. **Docker Error Output Section**
   - Scrollable text widget
   - Shows raw stderr output from Docker
   - Courier font for monospaced display

8. **Log File Location**
   - Shows path to Docker error log file
   - Helps users find logs for troubleshooting

9. **Action Buttons**
   - "Open Error Log Folder" - Opens file explorer to log directory
   - "Return to Main Menu" - Navigates back to landing page

## Error Types Handled

The error page handles all Docker error types detected by `analyze_docker_error()`:

1. **Port Conflict** - Port already in use
2. **Container Name Conflict** - Container name already exists
3. **Image Not Found** - Docker image not available
4. **Network Error** - Docker network issues
5. **Volume Error** - Mount/volume problems
6. **Docker Not Running** - Docker daemon not accessible
7. **Permission Error** - Insufficient privileges
8. **Disk Space Error** - Out of disk space
9. **Unknown Error** - Catch-all for unrecognized errors

Each error type has specific suggested actions tailored to the error.

## Testing

### Verification Test

**File:** `tests/verify_docker_error_page.py`

This automated test verifies:
- New method exists with correct signature
- Old dialog calls have been replaced
- Page navigation is properly configured
- Error data storage is implemented
- All UI elements are present

**Run with:**
```bash
python3 tests/verify_docker_error_page.py
```

### Visual Demo

**File:** `tests/demo_docker_error_page.py`

Interactive demo that shows the error page for different scenarios:
- Port Conflict Error
- Container Name Conflict
- Docker Not Running
- Image Not Found

**Run with:**
```bash
python3 tests/demo_docker_error_page.py
```

### Existing Tests

All existing Docker error analysis tests continue to pass:
```bash
python3 tests/test_docker_error_analysis.py
```

## Benefits

1. **Integrated User Experience**
   - No popup windows interrupting the flow
   - Consistent navigation pattern throughout the app

2. **Better Error Visibility**
   - Error details always visible on the page
   - No need to remember information from closed dialogs

3. **Easier Navigation**
   - Single "Return to Main Menu" button
   - No multiple dialog closes required

4. **Theme Consistency**
   - Error page respects dark/light theme settings
   - Matches overall application design

5. **Inline Error Logs**
   - Docker error output visible immediately
   - No need to click "Show Details" button

## Backwards Compatibility

The old dialog methods (`show_docker_container_error_dialog` and `show_docker_error_details`) remain in the codebase but are no longer called. This ensures:
- No breaking changes for any external code
- Easy rollback if needed
- Minimal code changes (additions only, no deletions)

## Future Enhancements

Potential future improvements:
1. Add "Try Again" button to retry the operation
2. Add "Change Port" button to modify port directly from error page
3. Add Docker status indicator showing if Docker is running
4. Add quick action buttons for common fixes (e.g., "Stop Conflicting Container")

## Conclusion

This implementation successfully replaces popup error dialogs with an integrated error page, improving the user experience while maintaining all functionality and visual design of the original error displays.
