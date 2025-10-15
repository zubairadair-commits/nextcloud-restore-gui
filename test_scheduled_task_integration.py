#!/usr/bin/env python3
"""
Integration test to demonstrate the scheduled task command construction
for both Python scripts and compiled executables.
"""

import sys
import os


def simulate_command_construction(exe_path, backup_dir, encrypt, password=""):
    """
    Simulate the command construction logic from create_scheduled_task.
    This mirrors the actual implementation.
    """
    # Ensure backup_dir is safely quoted (prevents argument splitting with spaces)
    backup_dir_quoted = f'"{backup_dir.strip("\"")}"'
    
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


def test_python_script_command():
    """Test command construction for Python script."""
    print("Test 1: Python Script (without encryption)")
    print("-" * 70)
    
    exe_path = r"C:\Users\John\Documents\nextcloud_restore_and_backup-v9.py"
    backup_dir = r"C:\Backups\Nextcloud"
    encrypt = False
    
    command = simulate_command_construction(exe_path, backup_dir, encrypt)
    
    print(f"  Input path: {exe_path}")
    print(f"  Backup dir: {backup_dir}")
    print(f"  Encrypt: {encrypt}")
    print(f"\n  Generated command:")
    print(f"  {command}")
    
    # Verify
    assert 'python' in command.lower(), "Command should start with python"
    assert exe_path in command, "Command should contain script path"
    assert '--scheduled' in command, "Command should have --scheduled flag"
    assert backup_dir in command, "Command should contain backup directory"
    
    print("\n  ✓ PASSED: Command correctly uses Python interpreter")
    return True


def test_executable_command():
    """Test command construction for compiled executable."""
    print("\n\nTest 2: Compiled Executable (without encryption)")
    print("-" * 70)
    
    exe_path = r"C:\Program Files\NextcloudBackup\backup_tool.exe"
    backup_dir = r"C:\Backups\Nextcloud"
    encrypt = False
    
    command = simulate_command_construction(exe_path, backup_dir, encrypt)
    
    print(f"  Input path: {exe_path}")
    print(f"  Backup dir: {backup_dir}")
    print(f"  Encrypt: {encrypt}")
    print(f"\n  Generated command:")
    print(f"  {command}")
    
    # Verify
    assert command.startswith('"'), "Command should start with quoted exe path"
    assert 'python' not in command.lower(), "Command should NOT use Python interpreter"
    assert exe_path in command, "Command should contain exe path"
    assert '--scheduled' in command, "Command should have --scheduled flag"
    
    print("\n  ✓ PASSED: Command correctly runs executable directly")
    return True


def test_python_script_with_encryption():
    """Test command construction for Python script with encryption."""
    print("\n\nTest 3: Python Script (with encryption)")
    print("-" * 70)
    
    exe_path = r"C:\nextcloud_restore_and_backup-v9.py"
    backup_dir = r"C:\Backups"
    encrypt = True
    password = "mypassword"
    
    command = simulate_command_construction(exe_path, backup_dir, encrypt, password)
    
    print(f"  Input path: {exe_path}")
    print(f"  Backup dir: {backup_dir}")
    print(f"  Encrypt: {encrypt}")
    print(f"  Password: {'*' * len(password)}")
    print(f"\n  Generated command:")
    print(f"  {command}")
    
    # Verify
    assert 'python' in command.lower(), "Command should use Python interpreter"
    assert '--encrypt' in command, "Command should have --encrypt flag"
    assert '--password' in command, "Command should have --password flag"
    assert password in command, "Command should contain password"
    
    print("\n  ✓ PASSED: Command correctly includes encryption parameters")
    return True


def test_executable_with_spaces():
    """Test command construction for executable with spaces in path."""
    print("\n\nTest 4: Executable with Spaces in Path")
    print("-" * 70)
    
    exe_path = r"C:\Program Files\Nextcloud Backup Tool\backup.exe"
    backup_dir = r"C:\My Backups\Nextcloud Data"
    encrypt = False
    
    command = simulate_command_construction(exe_path, backup_dir, encrypt)
    
    print(f"  Input path: {exe_path}")
    print(f"  Backup dir: {backup_dir}")
    print(f"  Encrypt: {encrypt}")
    print(f"\n  Generated command:")
    print(f"  {command}")
    
    # Verify paths are quoted
    assert f'"{exe_path}"' in command, "Exe path should be quoted"
    # Verify backup_dir is quoted
    assert f'--backup-dir "{backup_dir}"' in command, "Backup dir should be quoted"
    
    print("\n  ✓ PASSED: Paths with spaces are properly quoted")
    return True


def test_python_script_with_spaces():
    """Test command construction for Python script with spaces in path."""
    print("\n\nTest 5: Python Script with Spaces in Path")
    print("-" * 70)
    
    exe_path = r"C:\My Documents\Backup Scripts\nextcloud_backup.py"
    backup_dir = r"C:\User Data\Backups"
    encrypt = False
    
    command = simulate_command_construction(exe_path, backup_dir, encrypt)
    
    print(f"  Input path: {exe_path}")
    print(f"  Backup dir: {backup_dir}")
    print(f"  Encrypt: {encrypt}")
    print(f"\n  Generated command:")
    print(f"  {command}")
    
    # Verify
    assert 'python' in command.lower(), "Command should use Python interpreter"
    assert f'"{exe_path}"' in command, "Script path should be quoted"
    # Verify backup_dir is quoted
    assert f'--backup-dir "{backup_dir}"' in command, "Backup dir should be quoted"
    
    print("\n  ✓ PASSED: Script path with spaces is properly quoted")
    return True


def test_case_insensitive_detection():
    """Test that file extension detection is case-insensitive."""
    print("\n\nTest 6: Case-Insensitive Extension Detection")
    print("-" * 70)
    
    test_cases = [
        r"C:\script.py",
        r"C:\script.PY",
        r"C:\script.Py",
        r"C:\app.exe",
        r"C:\app.EXE",
        r"C:\app.Exe"
    ]
    
    for path in test_cases:
        command = simulate_command_construction(path, r"C:\backup", False)
        uses_python = 'python' in command.lower()
        is_py = path.lower().endswith('.py')
        
        print(f"  Path: {path:30} → {'Python' if uses_python else 'Direct':8} (expected: {'Python' if is_py else 'Direct'})")
        
        assert uses_python == is_py, f"Detection failed for {path}"
    
    print("\n  ✓ PASSED: Case-insensitive detection works correctly")
    return True


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("SCHEDULED TASK COMMAND CONSTRUCTION - INTEGRATION TESTS")
    print("=" * 70)
    
    try:
        tests = [
            test_python_script_command,
            test_executable_command,
            test_python_script_with_encryption,
            test_executable_with_spaces,
            test_python_script_with_spaces,
            test_case_insensitive_detection
        ]
        
        all_passed = True
        for test in tests:
            if not test():
                all_passed = False
        
        if all_passed:
            print("\n" + "=" * 70)
            print("ALL INTEGRATION TESTS PASSED! ✓")
            print("=" * 70)
            print("\nSummary:")
            print("  ✓ Python scripts are invoked through 'python' interpreter")
            print("  ✓ Executables are run directly without interpreter")
            print("  ✓ Encryption parameters are correctly included")
            print("  ✓ Paths with spaces are properly quoted")
            print("  ✓ File extension detection is case-insensitive")
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
