#!/usr/bin/env python3
"""
Comprehensive test suite for GUI fixes.
Tests all three issues to ensure they are properly fixed.
"""

import sys
import os
import re

def test_console_handler_fix():
    """Test that console handler is conditionally added"""
    print("=" * 80)
    print("TEST 1: Console Handler Fix")
    print("=" * 80)
    
    src_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'src',
        'nextcloud_restore_and_backup-v9.py'
    )
    
    with open(src_file, 'r') as f:
        content = f.read()
    
    # Test patterns
    tests = {
        'Checks for --scheduled flag': r"'--scheduled'\s+in\s+sys\.argv",
        'Checks for --test-run flag': r"'--test-run'\s+in\s+sys\.argv",
        'Conditional console handler': r"if\s+is_non_gui_mode:",
        'Console handler creation': r"console_handler\s*=\s*logging\.StreamHandler\(\)",
    }
    
    results = {}
    for test_name, pattern in tests.items():
        results[test_name] = bool(re.search(pattern, content))
    
    # Display results
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ Issue 1 FIXED: Console handler is conditionally added")
    else:
        print("❌ Issue 1 FAILED: Some checks did not pass")
    
    return all_passed

def test_canvas_configuration_fix():
    """Test that canvas width configuration is correct"""
    print("\n" + "=" * 80)
    print("TEST 2: Canvas Configuration Fix")
    print("=" * 80)
    
    src_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'src',
        'nextcloud_restore_and_backup-v9.py'
    )
    
    with open(src_file, 'r') as f:
        lines = f.readlines()
    
    # Find show_backup_history function
    in_function = False
    function_start = -1
    function_lines = []
    
    for i, line in enumerate(lines):
        if 'def show_backup_history(self):' in line:
            in_function = True
            function_start = i
        elif in_function:
            if line.strip().startswith('def ') and 'show_backup_history' not in line:
                break
            function_lines.append(line)
    
    function_content = ''.join(function_lines)
    
    # Test patterns
    tests = {
        'Unbinds MouseWheel events': r'self\.unbind_all\("<MouseWheel>"\)',
        'Unbinds Button-4 events': r'self\.unbind_all\("<Button-4>"\)',
        'Unbinds Button-5 events': r'self\.unbind_all\("<Button-5>"\)',
        'configure_scroll function': r'def configure_scroll\(event=None\):',
        'Canvas width validation': r'canvas_width\s*>\s*1',
        'Binds content_frame': r'content_frame\.bind\("<Configure>",\s*configure_scroll\)',
        'Binds canvas': r'canvas\.bind\("<Configure>",\s*configure_scroll\)',
    }
    
    results = {}
    for test_name, pattern in tests.items():
        results[test_name] = bool(re.search(pattern, function_content))
    
    # Display results
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ Issue 2 FIXED: Canvas configuration is correct")
    else:
        print("❌ Issue 2 FAILED: Some checks did not pass")
    
    return all_passed

def test_backup_cleanup_implementation():
    """Test that backup cleanup is implemented"""
    print("\n" + "=" * 80)
    print("TEST 3: Backup History Cleanup")
    print("=" * 80)
    
    src_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'src',
        'nextcloud_restore_and_backup-v9.py'
    )
    
    with open(src_file, 'r') as f:
        lines = f.readlines()
    
    # Find show_backup_history function
    in_function = False
    function_lines = []
    
    for i, line in enumerate(lines):
        if 'def show_backup_history(self):' in line:
            in_function = True
        elif in_function:
            if line.strip().startswith('def ') and 'show_backup_history' not in line:
                break
            function_lines.append(line)
    
    function_content = ''.join(function_lines)
    
    # Test patterns
    tests = {
        'Gets all backups': r'get_all_backups\(\)',
        'Initializes existing_backups': r'existing_backups\s*=\s*\[\]',
        'Checks file existence': r'if\s+os\.path\.exists\(backup_path\):',
        'Appends existing backups': r'existing_backups\.append\(backup\)',
        'Deletes missing backups': r'self\.backup_history\.delete_backup\(backup_id\)',
        'Logs removal': r'Removing missing backup',
        'Displays existing backups': r'for backup in existing_backups:',
    }
    
    results = {}
    for test_name, pattern in tests.items():
        results[test_name] = bool(re.search(pattern, function_content))
    
    # Display results
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ Issue 3 VERIFIED: Backup cleanup is implemented")
    else:
        print("❌ Issue 3 FAILED: Some checks did not pass")
    
    return all_passed

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "GUI FIXES - COMPREHENSIVE TEST SUITE" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    results = []
    
    # Run all tests
    results.append(("Console Handler Fix", test_console_handler_fix()))
    results.append(("Canvas Configuration Fix", test_canvas_configuration_fix()))
    results.append(("Backup Cleanup Implementation", test_backup_cleanup_implementation()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 27 + "🎉 ALL TESTS PASSED! 🎉" + " " * 28 + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        return 0
    else:
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 30 + "⚠️  TESTS FAILED ⚠️" + " " * 30 + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
