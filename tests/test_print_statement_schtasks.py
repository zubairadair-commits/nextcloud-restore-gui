"""
Test to verify that print statements for schtasks_cmd debugging are present.

This test checks that:
1. create_scheduled_task has a print statement before subprocess.run(schtasks_cmd, ...)
2. _run_test_backup_scheduled has a print statement before subprocess.run(schtasks_cmd, ...)
"""
import re
import sys


def test_create_scheduled_task_print_statement():
    """Test that create_scheduled_task has the print statement for schtasks_cmd."""
    
    print("=" * 70)
    print("Testing create_scheduled_task Print Statement")
    print("=" * 70)
    
    # Read the main file
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find create_scheduled_task function
    match = re.search(r'def create_scheduled_task\(.*?\n(.*?)(?=\ndef |\Z)', content, re.DOTALL)
    if not match:
        print("❌ Could not find create_scheduled_task function")
        return False
    
    func_content = match.group(1)
    
    print("\n1. Checking for print statement before subprocess.run(schtasks_cmd, ...)...")
    
    # Find the subprocess.run(schtasks_cmd section
    pattern = r'print\("Scheduled Task Command:",\s*schtasks_cmd\)\s*\n\s*result = subprocess\.run\(\s*schtasks_cmd'
    
    if re.search(pattern, func_content, re.MULTILINE):
        print("   ✓ Print statement found immediately before subprocess.run(schtasks_cmd, ...)")
        return True
    else:
        print("❌ ERROR: Print statement not found before subprocess.run(schtasks_cmd, ...)")
        return False


def test_run_test_backup_scheduled_print_statement():
    """Test that _run_test_backup_scheduled has the print statement for schtasks_cmd."""
    
    print("\n" + "=" * 70)
    print("Testing _run_test_backup_scheduled Print Statement")
    print("=" * 70)
    
    # Read the main file
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find _run_test_backup_scheduled method
    match = re.search(r'def _run_test_backup_scheduled\(.*?\n(.*?)(?=\n    def |\Z)', content, re.DOTALL)
    if not match:
        print("❌ Could not find _run_test_backup_scheduled method")
        return False
    
    func_content = match.group(1)
    
    print("\n1. Checking for print statement before subprocess.run(schtasks_cmd, ...)...")
    
    # Find the subprocess.run(schtasks_cmd section
    pattern = r'print\("Scheduled Task Command:",\s*schtasks_cmd\)\s*\n\s*result = subprocess\.run\(\s*schtasks_cmd'
    
    if re.search(pattern, func_content, re.MULTILINE):
        print("   ✓ Print statement found immediately before subprocess.run(schtasks_cmd, ...)")
        return True
    else:
        print("❌ ERROR: Print statement not found before subprocess.run(schtasks_cmd, ...)")
        return False


if __name__ == "__main__":
    print("\nTesting Print Statements for schtasks_cmd Debugging")
    print("=" * 70)
    print("Requirement: print('Scheduled Task Command:', schtasks_cmd)")
    print("             should be present immediately before subprocess.run(schtasks_cmd, ...)")
    print("=" * 70)
    
    test1 = test_create_scheduled_task_print_statement()
    test2 = test_run_test_backup_scheduled_print_statement()
    
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    print(f"create_scheduled_task: {'✓ PASS' if test1 else '❌ FAIL'}")
    print(f"_run_test_backup_scheduled: {'✓ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 All tests PASSED! Print statements are correctly placed.")
        sys.exit(0)
    else:
        print("\n❌ Some tests FAILED. Print statements need fixing.")
        sys.exit(1)
