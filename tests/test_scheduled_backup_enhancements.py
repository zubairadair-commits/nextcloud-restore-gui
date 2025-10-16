#!/usr/bin/env python3
"""
Test script for scheduled backup enhancements.
Validates:
1. Task creation does NOT include /RL HIGHEST flag (reverted)
2. Task creation does NOT include /Z flag (reverted)
3. Scheduled backup adds to backup history
"""

import sys
import os
import re

def test_scheduled_task_flags():
    """Test that scheduled task creation does NOT include /RL and /Z flags (reverted)."""
    print("Testing scheduled task creation flags (reverted)...")
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    assert os.path.exists(main_file), f"{main_file} should exist"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the create_scheduled_task function
    function_start = content.find('def create_scheduled_task(')
    assert function_start != -1, "create_scheduled_task function should exist"
    
    # Extract the function content (next 300 lines should be enough)
    function_content = content[function_start:function_start+10000]
    
    # Check that /RL HIGHEST flag is NOT present (reverted)
    assert '"/RL"' not in function_content, \
        "Task creation should NOT include /RL flag (reverted)"
    print("  ✓ /RL flag not present (reverted)")
    
    # Check that /Z flag is NOT present (reverted)
    assert '"/Z"' not in function_content, \
        "Task creation should NOT include /Z flag (reverted)"
    print("  ✓ /Z flag not present (reverted)")
    
    # Verify essential flags are present
    assert '"/F"' in function_content, \
        "Task creation should include /F flag"
    print("  ✓ /F flag found (force creation)")
    
    assert '"/ST"' in function_content, \
        "Task creation should include /ST flag"
    print("  ✓ /ST flag found (start time)")
    
    print("✅ Scheduled task flags test PASSED (reverted)\n")

def test_scheduled_backup_history():
    """Test that scheduled backup adds to backup history."""
    print("Testing scheduled backup history tracking...")
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the run_backup_process_scheduled function
    function_start = content.find('def run_backup_process_scheduled(')
    assert function_start != -1, "run_backup_process_scheduled function should exist"
    
    # Extract the function content
    function_end = content.find('\n    def ', function_start + 1)
    if function_end == -1:
        function_end = len(content)
    function_content = content[function_start:function_end]
    
    # Check that backup_history.add_backup is called
    assert 'backup_history.add_backup' in function_content, \
        "Scheduled backup should add to backup history"
    print("  ✓ backup_history.add_backup() call found")
    
    # Check that the call happens after "Backup complete"
    backup_complete_pos = function_content.find('Backup complete!')
    add_backup_pos = function_content.find('backup_history.add_backup')
    assert backup_complete_pos != -1 and add_backup_pos != -1, \
        "Both markers should be present"
    assert backup_complete_pos < add_backup_pos, \
        "Backup should be added to history after successful completion"
    print("  ✓ History tracking occurs after successful backup")
    
    # Check that required parameters are passed
    assert 'backup_path=' in function_content, \
        "backup_path parameter should be passed"
    assert 'database_type=' in function_content, \
        "database_type parameter should be passed"
    assert 'folders=' in function_content, \
        "folders parameter should be passed"
    assert 'encrypted=' in function_content, \
        "encrypted parameter should be passed"
    print("  ✓ All required parameters are passed to add_backup()")
    
    print("✅ Scheduled backup history test PASSED\n")

def test_code_integrity():
    """Test that the modified code doesn't break existing functionality."""
    print("Testing code integrity...")
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check that BackupHistoryManager class still exists
    assert 'class BackupHistoryManager:' in content, \
        "BackupHistoryManager class should exist"
    print("  ✓ BackupHistoryManager class exists")
    
    # Check that show_backup_history method exists
    assert 'def show_backup_history(self):' in content, \
        "show_backup_history method should exist"
    print("  ✓ show_backup_history method exists")
    
    # Check that the normal backup process also adds to history
    run_backup_process_pos = content.find('def run_backup_process(')
    if run_backup_process_pos != -1:
        # Find the end of this function
        next_def = content.find('\n    def ', run_backup_process_pos + 1)
        if next_def == -1:
            next_def = len(content)
        run_backup_content = content[run_backup_process_pos:next_def]
        
        assert 'backup_history.add_backup' in run_backup_content, \
            "Normal backup process should also add to history"
        print("  ✓ Normal backup process also adds to history")
    
    print("✅ Code integrity test PASSED\n")

def main():
    """Run all tests."""
    print("=" * 60)
    print("SCHEDULED BACKUP ENHANCEMENTS TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_scheduled_task_flags()
        test_scheduled_backup_history()
        test_code_integrity()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
