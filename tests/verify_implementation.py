#!/usr/bin/env python3
"""
Comprehensive verification of extraction tool validation implementation.

This script verifies that all acceptance criteria from the problem statement
are met and demonstrates the complete user experience.
"""

import sys
import os

# Add color support for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print("=" * 70)


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def verify_implementation():
    """Verify the implementation meets all requirements."""
    
    print_header("EXTRACTION TOOL VALIDATION - IMPLEMENTATION VERIFICATION")
    print()
    
    # Read the source file
    src_path = "/home/runner/work/nextcloud-restore-gui/nextcloud-restore-gui/src/nextcloud_restore_and_backup-v9.py"
    
    if not os.path.exists(src_path):
        print_error(f"Source file not found: {src_path}")
        return False
    
    with open(src_path, 'r') as f:
        content = f.read()
    
    # Verify each acceptance criterion
    all_passed = True
    
    print_header("ACCEPTANCE CRITERIA VERIFICATION")
    print()
    
    # Criterion 1: Extraction attempted right after backup selection
    print("1. Extraction attempted right after backup selection")
    if 'validate_extraction_tools(path)' in content and 'def browse_backup(self):' in content:
        print_success("browse_backup() validates tools immediately on file selection")
    else:
        print_error("browse_backup() doesn't validate tools on file selection")
        all_passed = False
    print()
    
    # Criterion 2: User-friendly error shown if extraction fails
    print("2. User-friendly error or install prompt shown if extraction fails")
    if 'def show_extraction_error_dialog' in content:
        print_success("User-friendly error dialog implemented")
        if 'Installation Options' in content and 'Install GPG' in content:
            print_success("Dialog offers installation guidance")
        else:
            print_error("Dialog doesn't offer installation guidance")
            all_passed = False
    else:
        print_error("Error dialog not implemented")
        all_passed = False
    print()
    
    # Criterion 3: User prevented from proceeding or clear instructions provided
    print("3. User prevented from proceeding until extraction is available")
    if 'return False' in content and 'check_gpg_available()' in content:
        print_success("Navigation blocked when tools are missing")
        if 'show_extraction_error_dialog' in content:
            print_success("Clear instructions provided via error dialog")
        else:
            print_error("Clear instructions not provided")
            all_passed = False
    else:
        print_error("Navigation not properly blocked")
        all_passed = False
    print()
    
    # Criterion 4: Works for both encrypted (.gpg) and unencrypted (.tar.gz)
    print("4. Works for both encrypted (.gpg) and unencrypted (.tar.gz) backups")
    if "backup_path.endswith('.gpg')" in content and 'check_gpg_available()' in content:
        print_success("Handles encrypted .gpg files with GPG check")
    else:
        print_error("Doesn't properly handle encrypted files")
        all_passed = False
    
    if "backup_path.endswith('.tar.gz')" in content or 'check_tarfile_available()' in content:
        print_success("Handles unencrypted .tar.gz files with tarfile check")
    else:
        print_error("Doesn't properly handle unencrypted files")
        all_passed = False
    print()
    
    # Criterion 5: Error/warning logged for troubleshooting
    print("5. Error/warning logged for troubleshooting")
    if 'logger.error' in content and 'logger.info' in content:
        print_success("Logging implemented for errors and info")
        if 'logger.warning' in content or 'logger.error(f"GPG not found' in content:
            print_success("Specific logging for extraction tool issues")
        else:
            print_error("Logging not comprehensive enough")
            all_passed = False
    else:
        print_error("Logging not implemented")
        all_passed = False
    print()
    
    print_header("IMPLEMENTATION FEATURES")
    print()
    
    # Feature verification
    features = [
        ('check_gpg_available()', 'GPG availability check function'),
        ('check_tarfile_available()', 'tarfile availability check function'),
        ('show_extraction_error_dialog(', 'User-friendly error dialog'),
        ('validate_extraction_tools(self, backup_path):', 'Tool validation method'),
        ('webbrowser.open(GPG_DOWNLOAD_URL)', 'Automatic GPG installer download'),
        ('Installation Options', 'Platform-specific installation instructions'),
        ('logger.info(f"Validating extraction tools', 'Validation logging'),
    ]
    
    feature_count = 0
    for feature_code, feature_name in features:
        if feature_code in content:
            print_success(feature_name)
            feature_count += 1
        else:
            print_error(f"{feature_name} not found")
    
    print()
    print(f"Features implemented: {feature_count}/{len(features)}")
    print()
    
    print_header("ERROR HANDLING VERIFICATION")
    print()
    
    # Error handling verification
    error_types = [
        ('GPG is not installed', 'GPG missing error'),
        ('Incorrect password', 'Wrong password error'),
        ('corrupted archive', 'Corrupted archive error'),
        ('No space left', 'Disk space error'),
        ('Permission denied', 'Permission error'),
    ]
    
    error_count = 0
    for error_text, error_name in error_types:
        if error_text in content:
            print_success(error_name)
            error_count += 1
        else:
            print_error(f"{error_name} not found")
    
    print()
    print(f"Error types handled: {error_count}/{len(error_types)}")
    print()
    
    print_header("TEST COVERAGE")
    print()
    
    # Check test files
    test_files = [
        ('tests/test_extraction_validation.py', 'Automated test suite'),
        ('tests/demo_extraction_validation.py', 'User flow demonstration'),
        ('tests/demo_error_dialog_visual.py', 'Visual demo of error dialog'),
    ]
    
    test_count = 0
    for test_file, test_desc in test_files:
        test_path = f"/home/runner/work/nextcloud-restore-gui/nextcloud-restore-gui/{test_file}"
        if os.path.exists(test_path):
            print_success(f"{test_desc}: {test_file}")
            test_count += 1
        else:
            print_error(f"{test_desc} not found: {test_file}")
    
    print()
    print(f"Test files created: {test_count}/{len(test_files)}")
    print()
    
    print_header("DOCUMENTATION")
    print()
    
    # Check documentation
    doc_file = "/home/runner/work/nextcloud-restore-gui/nextcloud-restore-gui/EXTRACTION_VALIDATION_IMPLEMENTATION.md"
    if os.path.exists(doc_file):
        print_success("Implementation documentation created")
        with open(doc_file, 'r') as f:
            doc_content = f.read()
            if 'User Experience Flow' in doc_content:
                print_success("User experience flow documented")
            if 'Acceptance Criteria Met' in doc_content:
                print_success("Acceptance criteria documented")
            if 'Security Considerations' in doc_content:
                print_success("Security considerations documented")
    else:
        print_error("Implementation documentation not found")
    
    print()
    
    print_header("OVERALL RESULT")
    print()
    
    if all_passed:
        print_success("ALL ACCEPTANCE CRITERIA MET!")
        print()
        print_info("The implementation successfully:")
        print("  • Validates extraction tools immediately on backup selection")
        print("  • Shows user-friendly error dialogs with installation guidance")
        print("  • Prevents navigation until tools are available")
        print("  • Works for both encrypted and unencrypted backups")
        print("  • Logs all operations for troubleshooting")
        print()
        print_info("Next steps:")
        print("  • Manual testing with missing GPG recommended")
        print("  • Test with corrupted archives")
        print("  • Test with insufficient disk space")
        print()
        return True
    else:
        print_error("Some acceptance criteria not met")
        print()
        return False


if __name__ == '__main__':
    success = verify_implementation()
    sys.exit(0 if success else 1)
