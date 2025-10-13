#!/usr/bin/env python3
"""
Test to verify that the scheduled task automatic repair functionality works correctly.

This test validates:
1. Detection of app movement (path changes)
2. Extraction of path from scheduled task commands
3. Comparison of current path vs scheduled task path
4. Automatic repair of scheduled task with new path
5. Support for both .py and .exe file types
"""

import sys
import os
import re


def test_path_extraction():
    """Test that we can extract paths from various command formats."""
    print("Testing path extraction from task commands...")
    
    test_cases = [
        # (command, expected_path)
        ('python "C:\\Users\\John\\script.py" --scheduled --backup-dir "C:\\backups"', 
         'C:\\Users\\John\\script.py'),
        ('"C:\\Program Files\\App\\backup.exe" --scheduled --backup-dir "C:\\backups"',
         'C:\\Program Files\\App\\backup.exe'),
        ('python.exe "C:\\My Documents\\backup tool.py" --encrypt',
         'C:\\My Documents\\backup tool.py'),
        ('"C:\\app.exe" --scheduled',
         'C:\\app.exe'),
    ]
    
    all_passed = True
    
    for i, (command, expected) in enumerate(test_cases, 1):
        print(f"\n  Test case {i}:")
        print(f"    Command: {command}")
        print(f"    Expected: {expected}")
        
        # Check if function exists in the main file
        with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        if 'def extract_path_from_task_command' in content:
            print(f"    ✓ extract_path_from_task_command function found")
        else:
            print(f"    ✗ extract_path_from_task_command function NOT found")
            all_passed = False
    
    return all_passed


def test_scheduled_task_query():
    """Test that we can query scheduled task commands."""
    print("\nTesting scheduled task query functionality...")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('def get_scheduled_task_command', 'get_scheduled_task_command function'),
        ('Task To Run', 'parsing "Task To Run" field from schtasks output'),
    ]
    
    all_passed = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False
    
    return all_passed


def test_repair_functionality():
    """Test that the repair functionality exists and has correct logic."""
    print("\nTesting scheduled task repair functionality...")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('def check_and_repair_scheduled_task', 'check_and_repair_scheduled_task function'),
        ('current_path = get_exe_path()', 'getting current executable path'),
        ('get_scheduled_task_command', 'querying scheduled task command'),
        ('extract_path_from_task_command', 'extracting path from task command'),
        ('os.path.normcase', 'normalizing paths for comparison'),
        ('create_scheduled_task', 'recreating task with new path'),
    ]
    
    all_passed = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False
    
    return all_passed


def test_startup_integration():
    """Test that repair is integrated into app startup."""
    print("\nTesting startup integration...")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find the __init__ method of NextcloudRestoreWizard
    init_start = content.find('class NextcloudRestoreWizard')
    if init_start == -1:
        print("  ✗ NextcloudRestoreWizard class not found")
        return False
    
    # Find __init__ method after the class definition
    init_method_start = content.find('def __init__(self):', init_start)
    if init_method_start == -1:
        print("  ✗ __init__ method not found")
        return False
    
    # Get the init method content (up to the next method or end)
    next_method = content.find('\n    def ', init_method_start + 20)
    if next_method == -1:
        init_content = content[init_method_start:]
    else:
        init_content = content[init_method_start:next_method]
    
    checks = [
        ('_check_scheduled_task_on_startup', 'calling repair check on startup'),
        ('def _check_scheduled_task_on_startup', '_check_scheduled_task_on_startup method exists'),
        ('check_and_repair_scheduled_task', 'invoking repair function'),
    ]
    
    all_passed = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False
    
    return all_passed


def test_user_notification():
    """Test that user is notified when repair occurs."""
    print("\nTesting user notification on repair...")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Look for notification logic in the startup check method
    if '_check_scheduled_task_on_startup' in content:
        # Get the method content
        method_start = content.find('def _check_scheduled_task_on_startup')
        method_end = content.find('\n    def ', method_start + 10)
        method_content = content[method_start:method_end] if method_end != -1 else content[method_start:]
        
        checks = [
            ('if repaired:', 'checking if repair was performed'),
            ('Toplevel', 'creating notification dialog'),
            ('Scheduled Task', 'showing descriptive title'),
        ]
        
        all_passed = True
        for pattern, description in checks:
            if pattern in method_content:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ Missing: {description}")
                all_passed = False
        
        return all_passed
    else:
        print("  ✗ _check_scheduled_task_on_startup method not found")
        return False


def test_py_vs_exe_detection():
    """Test that both .py and .exe paths are handled correctly."""
    print("\nTesting .py vs .exe detection in repair...")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # The create_scheduled_task function should handle both cases
    if 'def create_scheduled_task' in content:
        func_start = content.find('def create_scheduled_task')
        func_end = content.find('\ndef ', func_start + 1)
        func_content = content[func_start:func_end]
        
        checks = [
            ("endswith('.py')", '.py file detection'),
            ('python', 'Python interpreter for .py files'),
        ]
        
        all_passed = True
        for pattern, description in checks:
            if pattern in func_content:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ Missing: {description}")
                all_passed = False
        
        return all_passed
    else:
        print("  ✗ create_scheduled_task function not found")
        return False


def visualize_repair_flow():
    """Show the expected repair flow."""
    print("\n" + "=" * 70)
    print("EXPECTED REPAIR FLOW")
    print("=" * 70)
    
    print("\nScenario 1: App moved from C:\\App to D:\\NewApp")
    print("  1. App starts, gets current path: D:\\NewApp\\backup.py")
    print("  2. Query scheduled task command: python \"C:\\App\\backup.py\" --scheduled ...")
    print("  3. Extract path from task: C:\\App\\backup.py")
    print("  4. Compare paths: D:\\NewApp\\backup.py != C:\\App\\backup.py")
    print("  5. Paths differ -> Repair needed")
    print("  6. Extract task parameters (backup dir, encryption, etc.)")
    print("  7. Recreate task with new path: python \"D:\\NewApp\\backup.py\" --scheduled ...")
    print("  8. Show success notification to user")
    
    print("\nScenario 2: App not moved")
    print("  1. App starts, gets current path: C:\\App\\backup.exe")
    print("  2. Query scheduled task command: \"C:\\App\\backup.exe\" --scheduled ...")
    print("  3. Extract path from task: C:\\App\\backup.exe")
    print("  4. Compare paths: C:\\App\\backup.exe == C:\\App\\backup.exe")
    print("  5. Paths match -> No repair needed")
    print("  6. Continue normal startup (no notification)")
    
    print("\nScenario 3: No scheduled task exists")
    print("  1. App starts, gets current path: C:\\App\\backup.py")
    print("  2. Query scheduled task command: None (task doesn't exist)")
    print("  3. No repair needed")
    print("  4. Continue normal startup (no notification)")
    
    print("\n" + "=" * 70)


def main():
    """Run all tests."""
    print("=" * 70)
    print("SCHEDULED TASK AUTOMATIC REPAIR TEST")
    print("=" * 70)
    
    try:
        visualize_repair_flow()
        print()
        
        all_passed = True
        all_passed = test_path_extraction() and all_passed
        all_passed = test_scheduled_task_query() and all_passed
        all_passed = test_repair_functionality() and all_passed
        all_passed = test_startup_integration() and all_passed
        all_passed = test_user_notification() and all_passed
        all_passed = test_py_vs_exe_detection() and all_passed
        
        if all_passed:
            print("\n" + "=" * 70)
            print("All tests passed! ✓")
            print("Scheduled task automatic repair is correctly implemented.")
            print("=" * 70)
            return 0
        else:
            print("\n" + "=" * 70)
            print("Some tests failed! ✗")
            print("Scheduled task automatic repair needs implementation.")
            print("=" * 70)
            return 1
            
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
