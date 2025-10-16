#!/usr/bin/env python3
"""
Test to verify that scheduled mode doesn't call Tkinter GUI methods.
This test ensures that the fix for RuntimeError: 'main thread is not in main loop' works.
"""

import sys
import os
import re

def test_scheduled_mode_implementation():
    """Verify the code changes for scheduled mode"""
    print("=" * 70)
    print("Testing Scheduled Backup Mode Fix - Code Verification")
    print("=" * 70)
    print()
    
    script_path = os.path.join(os.path.dirname(__file__), '../src/nextcloud_restore_and_backup-v9.py')
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Check if __init__ accepts scheduled_mode parameter
    tests_total += 1
    if re.search(r'def __init__\(self,\s*scheduled_mode\s*=\s*False\s*\)', content):
        print("✓ Test 1: __init__ accepts scheduled_mode parameter")
        tests_passed += 1
    else:
        print("✗ Test 1: __init__ does NOT accept scheduled_mode parameter")
    
    # Test 2: Check if scheduled_mode flag is stored
    tests_total += 1
    if 'self.scheduled_mode = scheduled_mode' in content:
        print("✓ Test 2: scheduled_mode flag is stored in self")
        tests_passed += 1
    else:
        print("✗ Test 2: scheduled_mode flag is NOT stored")
    
    # Test 3: Check if GUI initialization is skipped in scheduled mode
    tests_total += 1
    if re.search(r'if scheduled_mode:\s*return', content):
        print("✓ Test 3: GUI initialization is skipped when scheduled_mode=True")
        tests_passed += 1
    else:
        print("✗ Test 3: GUI initialization is NOT skipped")
    
    # Test 4: Check if main block passes scheduled_mode=True
    tests_total += 1
    if 'NextcloudRestoreWizard(scheduled_mode=True)' in content:
        print("✓ Test 4: Main block creates app with scheduled_mode=True")
        tests_passed += 1
    else:
        print("✗ Test 4: Main block does NOT use scheduled_mode=True")
    
    # Test 5: Check that app.withdraw() was removed (no longer needed)
    tests_total += 1
    pattern = r'if args\.scheduled:.*?app = NextcloudRestoreWizard.*?app\.withdraw\(\)'
    if not re.search(pattern, content, re.DOTALL):
        print("✓ Test 5: app.withdraw() removed (not needed with scheduled_mode)")
        tests_passed += 1
    else:
        print("✗ Test 5: app.withdraw() still present (should be removed)")
    
    # Test 6: Verify run_scheduled_backup exists
    tests_total += 1
    if 'def run_scheduled_backup(self, backup_dir, encrypt, password):' in content:
        print("✓ Test 6: run_scheduled_backup method exists")
        tests_passed += 1
    else:
        print("✗ Test 6: run_scheduled_backup method NOT found")
    
    print()
    print("=" * 70)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("✅ ALL TESTS PASSED")
        print()
        print("Summary of fix:")
        print("- Added scheduled_mode parameter to __init__")
        print("- GUI initialization skipped when scheduled_mode=True")
        print("- No more self.after() or GUI method calls in scheduled mode")
        print("- Prevents 'main thread is not in main loop' error")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("Please verify the implementation.")
        return 1

def test_code_patterns():
    """Test for problematic patterns in scheduled mode"""
    print()
    print("=" * 70)
    print("Checking for Problematic GUI Patterns")
    print("=" * 70)
    print()
    
    script_path = os.path.join(os.path.dirname(__file__), '../src/nextcloud_restore_and_backup-v9.py')
    
    with open(script_path, 'r') as f:
        lines = f.readlines()
    
    # Find the run_scheduled_backup method
    in_scheduled_backup = False
    scheduled_backup_start = 0
    scheduled_backup_end = 0
    indent_level = 0
    
    for i, line in enumerate(lines, 1):
        if 'def run_scheduled_backup(self, backup_dir, encrypt, password):' in line:
            in_scheduled_backup = True
            scheduled_backup_start = i
            # Calculate indent level
            indent_level = len(line) - len(line.lstrip())
        elif in_scheduled_backup and line.strip() and not line.strip().startswith('#'):
            # Check if we've exited the function (next function or class definition at same or lower indent)
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and (line.strip().startswith('def ') or line.strip().startswith('class ')):
                scheduled_backup_end = i - 1
                break
    
    if scheduled_backup_end == 0:
        scheduled_backup_end = len(lines)
    
    print(f"Analyzing run_scheduled_backup (lines {scheduled_backup_start}-{scheduled_backup_end})...")
    print()
    
    problematic_patterns = [
        (r'self\.after\s*\(', 'self.after( - GUI scheduling method'),
        (r'self\._display_health_status', 'self._display_health_status - GUI display method'),
        (r'self\.show_landing', 'self.show_landing - GUI method'),
        (r'messagebox\.', 'messagebox - GUI dialog'),
        (r'tk\.\w+\(', 'tk.Widget creation'),
    ]
    
    found_issues = []
    
    for i in range(scheduled_backup_start - 1, scheduled_backup_end):
        line = lines[i]
        for pattern, description in problematic_patterns:
            if re.search(pattern, line):
                found_issues.append((i + 1, description, line.strip()))
    
    if found_issues:
        print("⚠️  Found potential GUI method calls in scheduled mode:")
        for line_num, desc, line in found_issues:
            print(f"  Line {line_num}: {desc}")
            print(f"    {line}")
        print()
        print("❌ Scheduled mode may still call GUI methods")
        return 1
    else:
        print("✓ No problematic GUI patterns found in run_scheduled_backup")
        print("✅ Scheduled mode appears safe from GUI method calls")
        return 0

def main():
    """Run all tests"""
    result1 = test_scheduled_mode_implementation()
    result2 = test_code_patterns()
    
    print()
    print("=" * 70)
    if result1 == 0 and result2 == 0:
        print("✅ ALL VERIFICATIONS PASSED")
        print("The fix should prevent 'main thread is not in main loop' errors.")
    else:
        print("❌ SOME VERIFICATIONS FAILED")
    print("=" * 70)
    
    return max(result1, result2)

if __name__ == '__main__':
    sys.exit(main())
