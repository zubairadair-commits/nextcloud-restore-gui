# Extraction Tool Validation and Error Handling Implementation

## Summary
Enhanced the restore wizard to validate extraction tools (GPG, tarfile) immediately when a backup file is selected, providing clear error messages and installation guidance when tools are missing.

## Problem Addressed
When users selected a backup archive in the restore wizard, if the application couldn't extract the archive (due to missing GPG or other tools), the wizard would fall back to showing all credential fields without clear guidance. This caused confusion, especially for SQLite backups.

## Solution Implemented

### 1. Tool Availability Checks
Added utility functions to check if required tools are available:
- `check_gpg_available()`: Verifies GPG is installed and functional
- `check_tarfile_available()`: Verifies Python's tarfile module works

These functions return both availability status and descriptive error messages.

### 2. User-Friendly Error Dialog
Created `show_extraction_error_dialog()` that displays:
- Clear error title and warning icon
- Explanation of the missing tool and why it's needed
- The backup filename that couldn't be processed
- Platform-specific installation instructions
- "Install GPG" button for Windows users (opens browser to download)
- "Cancel" button to go back

### 3. Early Validation in browse_backup()
When a user selects a backup file:
- Immediately validates required tools
- Shows error dialog if tools are missing
- Provides immediate feedback without waiting for "Next" button

### 4. Enhanced perform_extraction_and_detection()
Before attempting to extract and detect database type:
- Validates GPG availability for encrypted (.gpg) files
- Validates tarfile availability for .tar.gz files
- Blocks navigation to Page 2 if tools are missing
- Shows specific error messages based on error type:
  - "GPG is not installed" → Offers to download GPG
  - "Incorrect password" → Asks user to retry
  - "Invalid or corrupted archive" → Suggests verifying backup
  - "No space left on device" → Suggests freeing disk space

### 5. Improved Error Handling in early_detect_database_type_from_backup()
Enhanced exception handling to:
- Distinguish between different error types (GPG missing vs wrong password vs corrupted archive)
- Raise specific exceptions with clear messages
- Log all errors for troubleshooting

### 6. Comprehensive Logging
Added logging throughout the validation process:
- Tool availability checks
- Validation start/end
- Error conditions
- User actions (install vs cancel)

## Files Modified

### src/nextcloud_restore_and_backup-v9.py
- Added `check_gpg_available()` (lines ~1233-1255)
- Added `check_tarfile_available()` (lines ~1257-1277)
- Added `show_extraction_error_dialog()` (lines ~1287-1450)
- Enhanced `browse_backup()` to call validation (line ~4905)
- Added `validate_extraction_tools()` method (lines ~4697-4768)
- Enhanced `perform_extraction_and_detection()` with early validation (lines ~4798-4848)
- Improved error handling in extraction result processing (lines ~4897-4946)
- Enhanced exception handling in `early_detect_database_type_from_backup()` (lines ~5699-5723)

## Tests Created

### tests/test_extraction_validation.py
Comprehensive test with 20 validation checks covering:
- Tool availability check functions
- Error dialog implementation
- Early validation in browse_backup
- Tool validation in perform_extraction_and_detection
- Specific error messages for different failure types
- Logging implementation

All 20 checks pass successfully.

### tests/demo_extraction_validation.py
Demonstrates the user experience flow:
- Tool availability checking
- Error recovery process
- Key benefits of the implementation

### tests/demo_error_dialog_visual.py
Shows what the error dialog looks like (with text fallback for headless environments)

## User Experience Flow

1. **User selects backup file**
   - `browse_backup()` is called
   - `validate_extraction_tools()` runs immediately
   - Shows error dialog if tools are missing

2. **User clicks 'Next' to go to Page 2**
   - `wizard_navigate()` calls `perform_extraction_and_detection()`
   - Validates tools again before attempting extraction
   - Blocks navigation if tools are missing
   - Shows specific error messages based on failure type

3. **Error recovery**
   - User installs missing tool (GPG, etc.)
   - User clicks 'Next' again
   - System re-validates tools
   - Proceeds if tools are now available

## Acceptance Criteria Met

✅ Extraction is attempted right after backup selection, before rendering credential fields
✅ If extraction fails, a user-friendly error or install prompt is shown
✅ The user is prevented from proceeding until extraction is available, or clear instructions are provided
✅ Works for both encrypted (.gpg) and unencrypted (.tar.gz) backups
✅ Error/warning is logged for troubleshooting

## Benefits

1. **Immediate Feedback**: Users know right away if they're missing required tools
2. **Clear Guidance**: Error messages explain what's missing and how to fix it
3. **Automatic Installation**: Windows users can click a button to download GPG
4. **No Confusion**: Users don't see empty credential fields due to extraction failures
5. **Better Troubleshooting**: Comprehensive logging helps diagnose issues
6. **Graceful Degradation**: System handles missing tools without crashing

## Testing

All changes have been tested with:
- Automated test suite (20 checks, 100% passing)
- Demo scripts showing user flow
- Visual representation of error dialog

Manual testing recommended:
- Test with GPG not installed (encrypted backup)
- Test with corrupted archive
- Test with incorrect password
- Test with insufficient disk space

## Security Considerations

No security vulnerabilities introduced. The changes:
- Don't expose sensitive information in error messages
- Don't bypass security checks
- Use secure subprocess calls
- Log appropriately without exposing credentials
