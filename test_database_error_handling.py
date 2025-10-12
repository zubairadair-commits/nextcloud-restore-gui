#!/usr/bin/env python3
"""
Test for improved database type detection error handling.
This test verifies the improvements from the problem statement:
- Clear messages when database detection fails
- Guidance for manual selection
- Instructions to check config.php
- Link to documentation
- Proper handling of unknown/unsupported database types
"""

import sys
import re

def test_unknown_database_handling():
    """Test that unknown database types show proper error messages"""
    print("\n" + "="*70)
    print("TEST 1: Unknown Database Type Handling")
    print("="*70)
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        code = f.read()
    
    checks = {
        'Detection failed message': '❌ DATABASE TYPE DETECTION FAILED' in code,
        'Possible reasons listed': 'Possible reasons:' in code,
        'Config.php guidance': "Check your Nextcloud configuration file (config/config.php)" in code,
        'Supported types listed': "only MySQL/MariaDB, PostgreSQL, and SQLite are supported" in code,
        'Documentation link': 'https://docs.nextcloud.com/server/latest/admin_manual/configuration_database/' in code,
        'Cannot proceed warning': 'Backup cannot proceed' in code or '⚠️ Backup cannot proceed' in code,
        'Error dialog for unknown': 'messagebox.showerror' in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    if all_passed:
        print("✅ TEST 1 PASSED: Unknown database type handling is improved")
    else:
        print("❌ TEST 1 FAILED: Some checks are missing")
    
    return all_passed


def test_detection_failure_dialog():
    """Test that detection failure shows detailed information"""
    print("\n" + "="*70)
    print("TEST 2: Detection Failure Dialog")
    print("="*70)
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        code = f.read()
    
    checks = {
        'Detection failed title': 'Database Type Detection Failed' in code,
        'Missing config reason': 'config.php file is missing or inaccessible' in code,
        'Permission issues': 'Permission issues' in code,
        'Network issues': 'Network connectivity issues' in code,
        'Manual selection option': '📋 MANUAL SELECTION:' in code,
        'PostgreSQL option': 'Yes = PostgreSQL' in code,
        'MySQL option': 'No = MySQL/MariaDB' in code,
        'Cancel option': 'Cancel = Abort backup' in code,
        'SQLite note': 'SQLite databases are backed up automatically' in code,
        'Check config guidance': "check your Nextcloud config/config.php file" in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    if all_passed:
        print("✅ TEST 2 PASSED: Detection failure dialog is comprehensive")
    else:
        print("❌ TEST 2 FAILED: Some information is missing")
    
    return all_passed


def test_unsupported_dbtype_validation():
    """Test that unsupported database types are caught before proceeding"""
    print("\n" + "="*70)
    print("TEST 3: Unsupported Database Type Validation")
    print("="*70)
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        code = f.read()
    
    # Check that validation happens before utility check
    validation_pattern = r"# Validate database type before proceeding.*?if dbtype and dbtype not in.*?messagebox\.showerror.*?self\.show_landing\(\)\s+return"
    validation_exists = bool(re.search(validation_pattern, code, re.DOTALL))
    
    checks = {
        'Validation before utility check': validation_exists,
        'Unsupported type title': 'Unsupported Database Type' in code,
        'Lists supported types': '• MySQL / MariaDB' in code and '• PostgreSQL' in code and '• SQLite' in code,
        'Returns to landing': 'self.show_landing()' in code,
        'Prevents backup': 'Backup cannot proceed with an unsupported database type' in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    if all_passed:
        print("✅ TEST 3 PASSED: Unsupported database types are validated")
    else:
        print("❌ TEST 3 FAILED: Validation is incomplete")
    
    return all_passed


def test_improved_error_logging():
    """Test that detection errors are logged with helpful information"""
    print("\n" + "="*70)
    print("TEST 4: Improved Error Logging")
    print("="*70)
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        code = f.read()
    
    checks = {
        'Config read error logged': '❌ Could not read config.php from container' in code,
        'Possible causes listed': 'Possible causes:' in code,
        'Missing dbtype logged': "❌ Could not find 'dbtype' field in config.php" in code,
        'Unsupported type logged': '⚠️ Detected unsupported database type:' in code,
        'Timeout error logged': '❌ Timeout reading config.php from container' in code,
        'Container check suggestion': 'docker ps' in code,
        'Verify config suggestion': 'Please verify the config.php file' in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    if all_passed:
        print("✅ TEST 4 PASSED: Error logging is comprehensive")
    else:
        print("❌ TEST 4 FAILED: Some logging is missing")
    
    return all_passed


def test_prompt_utility_unknown_handling():
    """Test that prompt_install_database_utility handles unknown types properly"""
    print("\n" + "="*70)
    print("TEST 5: Prompt Utility Unknown Type Handling")
    print("="*70)
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        code = f.read()
    
    # Find the prompt_install_database_utility function
    func_match = re.search(
        r'def prompt_install_database_utility\(.*?\):(.*?)(?=\ndef |\nclass |\Z)',
        code,
        re.DOTALL
    )
    
    if not func_match:
        print("  ✗ Could not find prompt_install_database_utility function")
        return False
    
    func_code = func_match.group(1)
    
    checks = {
        'Has else clause for unknown': 'else:' in func_code and '# Unknown or unsupported database type' in func_code,
        'Shows error dialog': 'messagebox.showerror' in func_code,
        'Returns False for unknown': 'if dbtype not in' in func_code and 'return False' in func_code,
        'Does not offer retry': "don't offer retry" in func_code or "just show error and cancel" in func_code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    if all_passed:
        print("✅ TEST 5 PASSED: Unknown type in prompt utility is handled correctly")
    else:
        print("❌ TEST 5 FAILED: Unknown type handling needs improvement")
    
    return all_passed


def main():
    print("="*70)
    print("DATABASE TYPE DETECTION ERROR HANDLING - TEST SUITE")
    print("="*70)
    print()
    print("This test verifies improvements from the problem statement:")
    print("  1. Clear messages when database type detection fails")
    print("  2. Steps to manually select database type")
    print("  3. Guidance to check/correct config.php")
    print("  4. Link to documentation/support")
    print("  5. Prevent backup from proceeding until resolved")
    print()
    
    results = []
    
    # Run all tests
    results.append(("Unknown Database Handling", test_unknown_database_handling()))
    results.append(("Detection Failure Dialog", test_detection_failure_dialog()))
    results.append(("Unsupported Type Validation", test_unsupported_dbtype_validation()))
    results.append(("Improved Error Logging", test_improved_error_logging()))
    results.append(("Prompt Utility Unknown Handling", test_prompt_utility_unknown_handling()))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED")
        print("\nThe database type detection error handling improvements are complete!")
        print("\nKey improvements:")
        print("  • Clear error messages with possible reasons")
        print("  • Manual database type selection when detection fails")
        print("  • Guidance to check config.php file")
        print("  • Links to Nextcloud documentation")
        print("  • Validation prevents backup with unsupported types")
        print("  • Comprehensive error logging for debugging")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease review the failures above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
