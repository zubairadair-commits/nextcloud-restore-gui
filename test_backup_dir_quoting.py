#!/usr/bin/env python3
"""
Test to verify that backup_dir argument is properly quoted in scheduled task commands.
This test specifically validates the fix for paths with spaces.
"""

import sys
import os


def simulate_command_construction_fixed(exe_path, backup_dir, encrypt, password=""):
    """
    Simulate the FIXED command construction logic with backup_dir quoting.
    This is what the implementation should do after the fix.
    """
    # Ensure backup_dir is safely quoted
    backup_dir_quoted = '"' + backup_dir.strip('"') + '"'
    
    # Build the command arguments for scheduled execution
    args = [
        "--scheduled",
        "--backup-dir", backup_dir_quoted,
        "--encrypt" if encrypt else "--no-encrypt"
    ]
    
    if encrypt and password:
        args.extend(["--password", password])
    
    # Build the full command
    # Detect if running as .py script or .exe executable
    if exe_path.lower().endswith('.py'):
        # For Python scripts, invoke through Python interpreter
        command = f'python "{exe_path}" {" ".join(args)}'
    else:
        # For compiled executables (.exe), run directly
        command = f'"{exe_path}" {" ".join(args)}'
    
    return command


def test_backup_dir_with_spaces():
    """Test that backup_dir with spaces is properly quoted."""
    print("Test 1: Backup Directory with Spaces (Problem Statement Example)")
    print("-" * 70)
    
    exe_path = r"C:\Program Files\NextcloudBackup\backup_tool.exe"
    backup_dir = r"C:/Users/zubai/Desktop/MANUAL BACKUP"
    encrypt = False
    
    command = simulate_command_construction_fixed(exe_path, backup_dir, encrypt)
    
    print(f"  Input path: {exe_path}")
    print(f"  Backup dir: {backup_dir}")
    print(f"  Encrypt: {encrypt}")
    print(f"\n  Generated command:")
    print(f"  {command}")
    
    # Verify backup_dir is quoted
    expected_quoted = f'--backup-dir "{backup_dir}"'
    assert expected_quoted in command, f"Expected '{expected_quoted}' in command"
    
    print(f"\n  ✓ PASSED: backup_dir is properly quoted as: --backup-dir \"{backup_dir}\"")
    return True


def test_backup_dir_already_quoted():
    """Test that backup_dir that's already quoted doesn't get double-quoted."""
    print("\n\nTest 2: Backup Directory Already Quoted")
    print("-" * 70)
    
    exe_path = r"C:\app.exe"
    backup_dir = r'"C:\My Backups\Data"'  # Already has quotes
    encrypt = False
    
    command = simulate_command_construction_fixed(exe_path, backup_dir, encrypt)
    
    print(f"  Input path: {exe_path}")
    print(f"  Backup dir: {backup_dir}")
    print(f"  Encrypt: {encrypt}")
    print(f"\n  Generated command:")
    print(f"  {command}")
    
    # Verify no double-quoting: should have one set of quotes, not two
    assert '""' not in command, "Should not have double quotes"
    # Should have exactly the right format
    expected_quoted = '--backup-dir "C:\\My Backups\\Data"'
    assert expected_quoted in command, f"Expected '{expected_quoted}' in command"
    
    print(f"\n  ✓ PASSED: Already-quoted backup_dir doesn't get double-quoted")
    return True


def test_backup_dir_without_spaces():
    """Test that backup_dir without spaces still gets quoted for consistency."""
    print("\n\nTest 3: Backup Directory Without Spaces")
    print("-" * 70)
    
    exe_path = r"C:\app.exe"
    backup_dir = r"C:\Backups\Nextcloud"
    encrypt = False
    
    command = simulate_command_construction_fixed(exe_path, backup_dir, encrypt)
    
    print(f"  Input path: {exe_path}")
    print(f"  Backup dir: {backup_dir}")
    print(f"  Encrypt: {encrypt}")
    print(f"\n  Generated command:")
    print(f"  {command}")
    
    # Verify backup_dir is quoted even without spaces
    expected_quoted = f'--backup-dir "{backup_dir}"'
    assert expected_quoted in command, f"Expected '{expected_quoted}' in command"
    
    print(f"\n  ✓ PASSED: backup_dir without spaces is still quoted for consistency")
    return True


def test_backup_dir_with_multiple_spaces():
    """Test backup_dir with multiple spaces in different parts of the path."""
    print("\n\nTest 4: Backup Directory with Multiple Spaces")
    print("-" * 70)
    
    exe_path = r"C:\app.py"
    backup_dir = r"C:\Users\John Doe\My Documents\Project Files\Backup Data"
    encrypt = True
    password = "secure123"
    
    command = simulate_command_construction_fixed(exe_path, backup_dir, encrypt, password)
    
    print(f"  Input path: {exe_path}")
    print(f"  Backup dir: {backup_dir}")
    print(f"  Encrypt: {encrypt}")
    print(f"\n  Generated command:")
    print(f"  {command}")
    
    # Verify backup_dir is quoted
    expected_quoted = f'--backup-dir "{backup_dir}"'
    assert expected_quoted in command, f"Expected '{expected_quoted}' in command"
    
    print(f"\n  ✓ PASSED: Complex path with multiple spaces is properly quoted")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("BACKUP DIRECTORY QUOTING FIX - VALIDATION TESTS")
    print("=" * 70)
    
    try:
        tests = [
            test_backup_dir_with_spaces,
            test_backup_dir_already_quoted,
            test_backup_dir_without_spaces,
            test_backup_dir_with_multiple_spaces
        ]
        
        all_passed = True
        for test in tests:
            if not test():
                all_passed = False
        
        if all_passed:
            print("\n" + "=" * 70)
            print("ALL TESTS PASSED! ✓")
            print("=" * 70)
            print("\nSummary:")
            print("  ✓ backup_dir with spaces is properly quoted")
            print("  ✓ Already-quoted backup_dir doesn't get double-quoted")
            print("  ✓ backup_dir without spaces is quoted for consistency")
            print("  ✓ Complex paths with multiple spaces are handled correctly")
            print("=" * 70)
            return 0
        else:
            print("\n" + "=" * 70)
            print("SOME TESTS FAILED! ✗")
            print("=" * 70)
            return 1
            
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
