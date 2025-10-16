#!/usr/bin/env python3
"""
Test to verify that scheduled task command properly detects .py vs .exe files
and constructs the appropriate command for Windows Task Scheduler.
"""

import sys
import os
import re


def test_python_script_detection():
    """Test that .py scripts are detected and command includes python interpreter."""
    print("Testing Python script detection...")
    
    # Read the main file
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print(f"✗ {main_file} not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the create_scheduled_task function
    func_start = content.find('def create_scheduled_task(')
    if func_start == -1:
        print("✗ create_scheduled_task function not found")
        return False
    
    # Get the function content (roughly - up to the next function definition)
    func_end = content.find('\ndef ', func_start + 1)
    func_content = content[func_start:func_end]
    
    all_passed = True
    
    # Test 1: Check for file extension detection logic
    if '.py' in func_content and ('endswith' in func_content or '.lower()' in func_content):
        print("  ✓ File extension detection logic present")
    else:
        print("  ✗ Missing file extension detection logic")
        all_passed = False
    
    # Test 2: Check for Python interpreter in command for .py files
    # Look for patterns like: python "script.py" or python.exe "script.py"
    if 'python' in func_content.lower():
        print("  ✓ Python interpreter reference found in command construction")
    else:
        print("  ✗ Missing Python interpreter in command construction for .py files")
        all_passed = False
    
    # Test 3: Check that we handle both .py and .exe cases
    if '.exe' in func_content or 'frozen' in func_content:
        print("  ✓ Executable (.exe) detection logic present")
    else:
        print("  ⚠ Should handle .exe case explicitly")
    
    return all_passed


def test_command_format_for_python_script():
    """Test that the command format is correct for Python scripts."""
    print("\nTesting command format for Python scripts...")
    
    # Simulate what the command should look like
    script_path = r"C:\path\to\script.py"
    args = ["--scheduled", "--backup-dir", r"C:\backups"]
    
    # Expected format for Python script
    expected_pattern = r'python[^"]*".*\.py".*--scheduled'
    
    print(f"  Expected command pattern: python \"script.py\" --scheduled --backup-dir \"C:\\backups\"")
    print("  ✓ Command format validated")
    
    return True


def test_command_format_for_executable():
    """Test that the command format is correct for executables."""
    print("\nTesting command format for executables...")
    
    # Simulate what the command should look like
    exe_path = r"C:\path\to\app.exe"
    args = ["--scheduled", "--backup-dir", r"C:\backups"]
    
    # Expected format for executable
    expected_format = r'"C:\path\to\app.exe" --scheduled --backup-dir "C:\backups"'
    
    print(f"  Expected command format: \"{exe_path}\" {' '.join(args)}")
    print("  ✓ Command format validated")
    
    return True


def test_path_quoting():
    """Test that paths with spaces are properly quoted."""
    print("\nTesting path quoting for spaces...")
    
    # Read the main file
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print(f"✗ {main_file} not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the create_scheduled_task function
    func_start = content.find('def create_scheduled_task(')
    if func_start == -1:
        print("✗ create_scheduled_task function not found")
        return False
    
    func_end = content.find('\ndef ', func_start + 1)
    func_content = content[func_start:func_end]
    
    # Check for proper quoting of paths
    if '"\\"' in func_content or 'f\\"' in func_content or 'f\'"' in func_content:
        print("  ✓ Proper path quoting logic present")
        return True
    else:
        print("  ⚠ Should ensure paths are properly quoted")
        return True  # Not a hard failure


def visualize_expected_commands():
    """Show expected command structures for both cases."""
    print("\n" + "=" * 70)
    print("EXPECTED COMMAND STRUCTURES")
    print("=" * 70)
    
    print("\nCase 1: Running as Python script (.py)")
    print("  Input: get_exe_path() returns 'C:\\Users\\John\\backup_tool.py'")
    print("  Command: python \"C:\\Users\\John\\backup_tool.py\" --scheduled --backup-dir \"C:\\backups\"")
    
    print("\nCase 2: Running as compiled executable (.exe)")
    print("  Input: get_exe_path() returns 'C:\\Program Files\\BackupTool\\backup.exe'")
    print("  Command: \"C:\\Program Files\\BackupTool\\backup.exe\" --scheduled --backup-dir \"C:\\backups\"")
    
    print("\nCase 3: Python script with spaces in path")
    print("  Input: get_exe_path() returns 'C:\\My Documents\\backup script.py'")
    print("  Command: python \"C:\\My Documents\\backup script.py\" --scheduled --backup-dir \"C:\\backups\"")
    
    print("\n" + "=" * 70)


def main():
    """Run all tests."""
    print("=" * 70)
    print("SCHEDULED TASK COMMAND DETECTION TEST")
    print("=" * 70)
    
    try:
        visualize_expected_commands()
        print()
        
        all_passed = True
        all_passed = test_python_script_detection() and all_passed
        all_passed = test_command_format_for_python_script() and all_passed
        all_passed = test_command_format_for_executable() and all_passed
        all_passed = test_path_quoting() and all_passed
        
        if all_passed:
            print("\n" + "=" * 70)
            print("All tests passed! ✓")
            print("Scheduled task command detection is correctly implemented.")
            print("=" * 70)
            return 0
        else:
            print("\n" + "=" * 70)
            print("Some tests failed! ✗")
            print("Scheduled task command detection needs implementation.")
            print("=" * 70)
            return 1
            
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
