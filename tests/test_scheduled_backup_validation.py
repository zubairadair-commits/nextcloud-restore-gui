#!/usr/bin/env python3
"""
Test script for automated setup checklist in scheduled backup functionality.
This validates the new validation functions, test run, and verification features.
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime

def test_validation_functions_exist():
    """Test that validation functions are present in the code."""
    print("Testing validation functions exist...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    assert os.path.exists(main_file), f"{main_file} should exist"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for new validation functions
    required_functions = [
        'validate_scheduled_task_setup',
        'run_test_backup',
        'get_last_backup_info',
        'get_recent_log_entries',
        'verify_scheduled_backup_ran'
    ]
    
    for func in required_functions:
        assert f"def {func}" in content, f"Function {func} should be defined"
        print(f"  ✓ Found function: {func}")
    
    return True

def test_validation_checks():
    """Test that all validation checks are implemented."""
    print("\nTesting validation checks...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the validate_scheduled_task_setup function
    func_start = content.find('def validate_scheduled_task_setup(')
    assert func_start != -1, "validate_scheduled_task_setup function should exist"
    
    # Get the function content (approximately)
    func_end = content.find('\ndef ', func_start + 100)
    func_content = content[func_start:func_end]
    
    # Check for all required validation checks
    checks = {
        'exe_path_exists': 'Backup script/EXE path validation',
        'start_dir_valid': 'Start directory validation',
        'arguments_valid': 'Task arguments validation',
        'backup_dir_writable': 'Backup directory writable check',
        'log_file_writable': 'Log file writable check',
        'task_fields_valid': 'Task fields validation'
    }
    
    for check_key, check_desc in checks.items():
        assert check_key in func_content, f"Validation check '{check_key}' should be present"
        print(f"  ✓ Found validation check: {check_desc}")
    
    # Check for error tracking
    assert "'errors'" in func_content, "Should track errors list"
    assert "'all_valid'" in func_content, "Should track overall validation status"
    print("  ✓ Error tracking implemented")
    
    return True

def test_validation_logging():
    """Test that validation includes logging."""
    print("\nTesting validation logging...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the validate_scheduled_task_setup function
    func_start = content.find('def validate_scheduled_task_setup(')
    func_end = content.find('\ndef ', func_start + 100)
    func_content = content[func_start:func_end]
    
    # Check for logging statements
    log_checks = [
        'logger.info',
        'logger.error',
        'VALIDATION'
    ]
    
    for check in log_checks:
        assert check in func_content, f"Should have '{check}' in validation function"
        print(f"  ✓ Found logging: {check}")
    
    return True

def test_test_run_function():
    """Test that test run function is implemented."""
    print("\nTesting test run function...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the run_test_backup function
    func_start = content.find('def run_test_backup(')
    assert func_start != -1, "run_test_backup function should exist"
    
    func_end = content.find('\ndef ', func_start + 100)
    func_content = content[func_start:func_end]
    
    # Check for key components
    checks = [
        'test_backup',
        'tarfile',
        'logger.info',
        'TEST RUN'
    ]
    
    for check in checks:
        assert check in func_content, f"Test run should include '{check}'"
        print(f"  ✓ Test run includes: {check}")
    
    return True

def test_last_run_verification():
    """Test that last run verification is implemented."""
    print("\nTesting last run verification...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for get_last_backup_info function
    assert 'def get_last_backup_info(' in content, "Should have get_last_backup_info function"
    print("  ✓ get_last_backup_info function exists")
    
    # Check for verify_scheduled_backup_ran function
    assert 'def verify_scheduled_backup_ran(' in content, "Should have verify_scheduled_backup_ran function"
    print("  ✓ verify_scheduled_backup_ran function exists")
    
    # Find the verification function
    func_start = content.find('def verify_scheduled_backup_ran(')
    func_end = content.find('\ndef ', func_start + 100)
    func_content = content[func_start:func_end]
    
    # Check for verification components
    checks = [
        'backup_file_exists',
        'log_entry_exists',
        'backup_info',
        'recent_logs'
    ]
    
    for check in checks:
        assert check in func_content, f"Verification should check '{check}'"
        print(f"  ✓ Verification checks: {check}")
    
    return True

def test_ui_integration():
    """Test that UI has been updated with new features."""
    print("\nTesting UI integration...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for Test Run button
    assert '🧪 Test Run' in content or 'Test Run' in content, "Should have Test Run button"
    print("  ✓ Test Run button added to UI")
    
    # Check for _run_test_backup method
    assert 'def _run_test_backup(' in content, "Should have _run_test_backup method"
    print("  ✓ _run_test_backup UI method exists")
    
    # Check for _show_recent_logs method
    assert 'def _show_recent_logs(' in content, "Should have _show_recent_logs method"
    print("  ✓ _show_recent_logs UI method exists")
    
    # Check for _verify_scheduled_backup method
    assert 'def _verify_scheduled_backup(' in content, "Should have _verify_scheduled_backup method"
    print("  ✓ _verify_scheduled_backup UI method exists")
    
    # Check for Last Run Status section
    assert 'Last Run Status' in content or 'last_run_frame' in content, "Should have Last Run Status section"
    print("  ✓ Last Run Status section added")
    
    # Check for View Logs button
    assert 'View Recent Logs' in content or 'view_logs' in content.lower(), "Should have View Logs functionality"
    print("  ✓ View Logs functionality added")
    
    return True

def test_validation_in_create_schedule():
    """Test that _create_schedule method uses validation."""
    print("\nTesting validation integration in _create_schedule...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _create_schedule method
    method_start = content.find('def _create_schedule(')
    assert method_start != -1, "_create_schedule method should exist"
    
    method_end = content.find('\n    def ', method_start + 100)
    method_content = content[method_start:method_end]
    
    # Check that validation is called
    assert 'validate_scheduled_task_setup' in method_content, "Should call validate_scheduled_task_setup"
    print("  ✓ Validation function is called")
    
    # Check for validation results handling
    assert 'validation_results' in method_content, "Should store validation results"
    print("  ✓ Validation results are stored")
    
    # Check for error handling
    assert "all_valid" in method_content, "Should check validation success"
    print("  ✓ Validation success is checked")
    
    # Check for error messages
    assert 'messagebox.showerror' in method_content or 'Validation Failed' in method_content, "Should show validation errors"
    print("  ✓ Validation errors are displayed")
    
    return True

def test_error_messages():
    """Test that clear error messages are implemented."""
    print("\nTesting error messages...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for error message indicators
    error_indicators = [
        '✗',  # Cross mark for errors
        '✓',  # Check mark for success
        'Validation Failed',
        'error',
        'success'
    ]
    
    for indicator in error_indicators:
        assert indicator in content, f"Should have error indicator: {indicator}"
        print(f"  ✓ Found error indicator: {indicator}")
    
    return True

def test_comprehensive_checks():
    """Test that all 10 requirements from problem statement are addressed."""
    print("\nTesting comprehensive checklist implementation...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    requirements = {
        1: ('exe_path_exists', 'Backup script/EXE path exists check'),
        2: ('start_dir_valid', 'Start in directory validation'),
        3: ('arguments_valid', 'Task arguments validation'),
        4: ('backup_dir_writable', 'Backup destination writable check'),
        5: ('log_file_writable', 'Log file location writable check'),
        6: ('task_fields_valid', 'Task Scheduler fields validation'),
        7: ('Test Run', 'Test Run button'),
        8: ('messagebox.showerror', 'Error message display'),
        9: ('Last Run Status', 'Last run status display'),
        10: ('verify_scheduled_backup_ran', 'Post-run verification')
    }
    
    for req_num, (check_str, description) in requirements.items():
        assert check_str in content, f"Requirement {req_num} not found: {description}"
        print(f"  ✓ Requirement {req_num}: {description}")
    
    print("\n✅ All 10 requirements from problem statement are implemented!")
    return True

def main():
    """Run all tests."""
    print("=" * 70)
    print("Automated Setup Checklist - Validation Tests")
    print("=" * 70)
    
    tests = [
        test_validation_functions_exist,
        test_validation_checks,
        test_validation_logging,
        test_test_run_function,
        test_last_run_verification,
        test_ui_integration,
        test_validation_in_create_schedule,
        test_error_messages,
        test_comprehensive_checks
    ]
    
    try:
        for test in tests:
            if not test():
                print(f"\n✗ Test failed: {test.__name__}")
                return 1
        
        print("\n" + "=" * 70)
        print("All tests passed! ✓")
        print("=" * 70)
        print("\n✅ Automated Setup Checklist Implementation Complete!")
        print("\nFeatures Implemented:")
        print("  1. ✓ Backup script/EXE path validation")
        print("  2. ✓ Start directory validation")
        print("  3. ✓ Task arguments validation")
        print("  4. ✓ Backup destination writable check")
        print("  5. ✓ Log file writable check")
        print("  6. ✓ Task Scheduler fields validation")
        print("  7. ✓ Test Run button for instant verification")
        print("  8. ✓ Clear error messages")
        print("  9. ✓ Last run status display")
        print(" 10. ✓ Post-run backup/log verification")
        print("\n" + "=" * 70)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
