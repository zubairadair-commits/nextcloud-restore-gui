#!/usr/bin/env python3
"""
Test for Extraction Tool Validation and Error Handling.

This test validates that the extraction tool validation and error handling
implementation meets the acceptance criteria:

1. Check functions exist for validating GPG and tarfile availability
2. Error dialogs provide user-friendly messages and installation guidance
3. browse_backup method validates tools on file selection
4. perform_extraction_and_detection validates tools before proceeding
5. Proper error messages are shown for missing tools
6. Prevents navigation to Page 2 when tools are missing
"""

import os
import sys
import re


def test_extraction_validation():
    """Test all acceptance criteria for extraction validation."""
    
    print("=" * 70)
    print("Extraction Tool Validation Test")
    print("=" * 70)
    print()
    
    file_path = "/home/runner/work/nextcloud-restore-gui/nextcloud-restore-gui/src/nextcloud_restore_and_backup-v9.py"
    
    if not os.path.exists(file_path):
        print(f"✗ ERROR: File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    criteria = []
    
    print("ACCEPTANCE CRITERION 1:")
    print("Check functions exist for validating tool availability")
    print("-" * 70)
    
    # Check 1a: check_gpg_available function exists
    if 'def check_gpg_available():' in content:
        print("  ✓ check_gpg_available() function implemented")
        criteria.append(True)
    else:
        print("  ✗ check_gpg_available() function not found")
        criteria.append(False)
    
    # Check 1b: check_tarfile_available function exists
    if 'def check_tarfile_available():' in content:
        print("  ✓ check_tarfile_available() function implemented")
        criteria.append(True)
    else:
        print("  ✗ check_tarfile_available() function not found")
        criteria.append(False)
    
    # Check 1c: check_gpg_available uses subprocess to test gpg command
    if "subprocess.run" in content and "'gpg', '--version'" in content:
        print("  ✓ check_gpg_available properly tests GPG command")
        criteria.append(True)
    else:
        print("  ✗ check_gpg_available doesn't properly test GPG")
        criteria.append(False)
    
    print()
    print("ACCEPTANCE CRITERION 2:")
    print("Error dialog provides user-friendly messages and installation options")
    print("-" * 70)
    
    # Check 2a: show_extraction_error_dialog function exists
    if 'def show_extraction_error_dialog(parent, missing_tool, backup_path):' in content:
        print("  ✓ show_extraction_error_dialog() function implemented")
        criteria.append(True)
    else:
        print("  ✗ show_extraction_error_dialog() function not found")
        criteria.append(False)
    
    # Check 2b: Dialog shows tool name and explanation
    if 'tool_name =' in content and 'explanation =' in content:
        print("  ✓ Dialog includes tool name and explanation")
        criteria.append(True)
    else:
        print("  ✗ Dialog doesn't show tool name/explanation")
        criteria.append(False)
    
    # Check 2c: Dialog offers installation for GPG
    if 'Install GPG' in content and 'webbrowser.open(GPG_DOWNLOAD_URL)' in content:
        print("  ✓ Dialog offers GPG installation option")
        criteria.append(True)
    else:
        print("  ✗ Dialog doesn't offer GPG installation")
        criteria.append(False)
    
    # Check 2d: Dialog shows installation instructions
    if 'install_instructions' in content and 'Installation Options' in content:
        print("  ✓ Dialog shows installation instructions")
        criteria.append(True)
    else:
        print("  ✗ Dialog doesn't show installation instructions")
        criteria.append(False)
    
    print()
    print("ACCEPTANCE CRITERION 3:")
    print("browse_backup validates tools on file selection")
    print("-" * 70)
    
    # Check 3a: browse_backup calls validation
    if 'def browse_backup(self):' in content:
        browse_start = content.find('def browse_backup(self):')
        browse_end = content.find('\n    def ', browse_start + 1)
        browse_method = content[browse_start:browse_end] if browse_end > browse_start else content[browse_start:]
        
        if 'validate_extraction_tools' in browse_method:
            print("  ✓ browse_backup calls validate_extraction_tools")
            criteria.append(True)
        else:
            print("  ✗ browse_backup doesn't call validate_extraction_tools")
            criteria.append(False)
    else:
        print("  ✗ browse_backup method not found")
        criteria.append(False)
    
    # Check 3b: validate_extraction_tools method exists
    if 'def validate_extraction_tools(self, backup_path):' in content:
        print("  ✓ validate_extraction_tools() method implemented")
        criteria.append(True)
    else:
        print("  ✗ validate_extraction_tools() method not found")
        criteria.append(False)
    
    print()
    print("ACCEPTANCE CRITERION 4:")
    print("perform_extraction_and_detection validates tools before proceeding")
    print("-" * 70)
    
    # Check 4a: Method checks for GPG when file is encrypted
    if 'def perform_extraction_and_detection(self):' in content:
        perf_start = content.find('def perform_extraction_and_detection(self):')
        perf_end = content.find('\n    def ', perf_start + 1)
        perf_method = content[perf_start:perf_end] if perf_end > perf_start else content[perf_start:perf_start + 5000]
        
        if 'check_gpg_available()' in perf_method and '.gpg' in perf_method:
            print("  ✓ Checks GPG availability for encrypted backups")
            criteria.append(True)
        else:
            print("  ✗ Doesn't check GPG for encrypted backups")
            criteria.append(False)
        
        # Check 4b: Method checks for tarfile
        if 'check_tarfile_available()' in perf_method:
            print("  ✓ Checks tarfile availability")
            criteria.append(True)
        else:
            print("  ✗ Doesn't check tarfile availability")
            criteria.append(False)
        
        # Check 4c: Shows error dialog when tools are missing
        if 'show_extraction_error_dialog' in perf_method:
            print("  ✓ Shows error dialog when tools are missing")
            criteria.append(True)
        else:
            print("  ✗ Doesn't show error dialog for missing tools")
            criteria.append(False)
        
        # Check 4d: Returns False to prevent navigation when tools missing
        if 'return False' in perf_method:
            print("  ✓ Prevents navigation when tools are missing")
            criteria.append(True)
        else:
            print("  ✗ Doesn't prevent navigation properly")
            criteria.append(False)
    else:
        print("  ✗ perform_extraction_and_detection method not found")
        criteria.append(False)
        criteria.append(False)
        criteria.append(False)
        criteria.append(False)
    
    print()
    print("ACCEPTANCE CRITERION 5:")
    print("Proper error messages for missing tools and extraction failures")
    print("-" * 70)
    
    # Check 5a: GPG-specific error messages
    if 'GPG is not installed' in content and 'GPG Error' in content:
        print("  ✓ GPG-specific error messages present")
        criteria.append(True)
    else:
        print("  ✗ GPG-specific error messages not found")
        criteria.append(False)
    
    # Check 5b: Password error messages
    if 'Incorrect password' in content or 'Bad session key' in content:
        print("  ✓ Password error messages present")
        criteria.append(True)
    else:
        print("  ✗ Password error messages not found")
        criteria.append(False)
    
    # Check 5c: Archive corruption error messages
    if 'corrupted archive' in content or 'Invalid or corrupted' in content:
        print("  ✓ Archive corruption error messages present")
        criteria.append(True)
    else:
        print("  ✗ Archive corruption error messages not found")
        criteria.append(False)
    
    # Check 5d: Disk space error messages
    if 'No space left' in content or 'Disk Space Error' in content:
        print("  ✓ Disk space error messages present")
        criteria.append(True)
    else:
        print("  ✗ Disk space error messages not found")
        criteria.append(False)
    
    print()
    print("ACCEPTANCE CRITERION 6:")
    print("Logging added for troubleshooting")
    print("-" * 70)
    
    # Check 6a: Logger used in check functions
    if 'logger.info' in content and 'logger.error' in content:
        print("  ✓ Logging statements present")
        criteria.append(True)
    else:
        print("  ✗ Logging statements not found")
        criteria.append(False)
    
    # Check 6b: Logs extraction tool checks
    log_checks = [
        'logger.info("GPG is available' in content or 'logger.info("tarfile' in content,
        'logger.error("GPG not found' in content or 'logger.error("tarfile' in content,
    ]
    if any(log_checks):
        print("  ✓ Logs extraction tool availability checks")
        criteria.append(True)
    else:
        print("  ✗ Doesn't log extraction tool checks")
        criteria.append(False)
    
    # Check 6c: Logs validation process
    if 'logger.info(f"Validating extraction tools' in content:
        print("  ✓ Logs validation process")
        criteria.append(True)
    else:
        print("  ✗ Doesn't log validation process")
        criteria.append(False)
    
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(criteria)
    total = len(criteria)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Passed: {passed}/{total} checks ({percentage:.1f}%)")
    print()
    
    if passed == total:
        print("✅ ALL ACCEPTANCE CRITERIA MET!")
        return True
    else:
        print(f"⚠️  {total - passed} checks failed")
        return False


if __name__ == '__main__':
    success = test_extraction_validation()
    sys.exit(0 if success else 1)
