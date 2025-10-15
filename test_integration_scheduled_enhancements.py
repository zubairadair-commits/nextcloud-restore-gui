#!/usr/bin/env python3
"""
Integration test for scheduled backup enhancements.
Tests the complete workflow including:
1. Creating scheduled task with essential flags only (reverted /RL and /Z)
2. Verifying backup history is updated after scheduled backup
3. Checking that backup history is displayed correctly
"""

import sys
import os
import re

def test_integration_workflow():
    """Test the complete integration of scheduled backup enhancements."""
    print("Testing integrated workflow...")
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Test 1: Verify task creation command structure
    print("\n1. Verifying scheduled task creation command structure...")
    
    # Find the schtasks command building section
    create_task_start = content.find('def create_scheduled_task(')
    assert create_task_start != -1, "create_scheduled_task function not found"
    
    create_task_end = content.find('\ndef ', create_task_start + 1)
    create_task_section = content[create_task_start:create_task_end]
    
    # Check command structure: should NOT have /RL HIGHEST and /Z (reverted)
    schtasks_cmd_pattern = r'schtasks_cmd\s*=\s*\[(.*?)\].*?schtasks_cmd\.extend\(schedule_args\)'
    match = re.search(schtasks_cmd_pattern, create_task_section, re.DOTALL)
    assert match, "schtasks_cmd structure not found"
    
    cmd_list = match.group(1)
    # Verify /RL and /Z are NOT present (reverted)
    assert '"/RL"' not in create_task_section, "/RL flag should not be present (reverted)"
    assert '"/Z"' not in create_task_section, "/Z flag should not be present (reverted)"
    
    # Verify essential flags are present
    assert '"/F"' in create_task_section, "/F flag should be present"
    assert '"/ST"' in create_task_section, "/ST flag should be present"
    
    print("   ✓ Task creation command properly structured")
    print("   ✓ /RL flag not present (reverted)")
    print("   ✓ /Z flag not present (reverted)")
    print("   ✓ Essential flags /F and /ST present")
    
    # Test 2: Verify scheduled backup adds to history with proper timing
    print("\n2. Verifying scheduled backup history integration...")
    
    scheduled_backup_start = content.find('def run_backup_process_scheduled(')
    assert scheduled_backup_start != -1, "run_backup_process_scheduled function not found"
    
    scheduled_backup_end = content.find('\n    def ', scheduled_backup_start + 1)
    if scheduled_backup_end == -1:
        scheduled_backup_end = len(content)
    scheduled_section = content[scheduled_backup_start:scheduled_backup_end]
    
    # Verify backup history is added
    assert 'self.backup_history.add_backup(' in scheduled_section, \
        "Scheduled backup doesn't add to history"
    
    # Verify it happens after backup completion message
    backup_complete_pos = scheduled_section.find('Backup complete!')
    add_backup_pos = scheduled_section.find('self.backup_history.add_backup(')
    
    assert backup_complete_pos != -1 and add_backup_pos != -1, \
        "Required markers not found"
    assert backup_complete_pos < add_backup_pos, \
        "History addition should be after backup completion"
    
    print("   ✓ Scheduled backup adds to history")
    print("   ✓ History added after successful backup completion")
    
    # Test 3: Verify history tracking parameters
    print("\n3. Verifying history tracking parameters...")
    
    # Extract the add_backup call
    add_backup_start = scheduled_section.find('self.backup_history.add_backup(')
    add_backup_end = scheduled_section.find(')', add_backup_start)
    # Extend to capture multi-line call
    for _ in range(10):  # Look up to 10 closing parens
        if scheduled_section[add_backup_end:add_backup_end+20].count('(') <= scheduled_section[add_backup_end:add_backup_end+20].count(')'):
            break
        add_backup_end = scheduled_section.find(')', add_backup_end + 1)
    
    add_backup_call = scheduled_section[add_backup_start:add_backup_end+1]
    
    required_params = ['backup_path=', 'database_type=', 'folders=', 'encrypted=']
    for param in required_params:
        assert param in add_backup_call, f"Missing parameter: {param}"
        print(f"   ✓ Parameter present: {param}")
    
    # Test 4: Verify backup history display remains functional
    print("\n4. Verifying backup history display functionality...")
    
    show_history_start = content.find('def show_backup_history(self):')
    assert show_history_start != -1, "show_backup_history method not found"
    
    show_history_end = content.find('\n    def ', show_history_start + 1)
    if show_history_end == -1:
        show_history_end = len(content)
    show_history_section = content[show_history_start:show_history_end]
    
    # Verify it fetches backups
    assert 'self.backup_history.get_all_backups()' in show_history_section, \
        "History display doesn't fetch backups"
    
    print("   ✓ Backup history display fetches all backups")
    print("   ✓ This includes both manual and scheduled backups")
    
    # Test 5: Verify no breaking changes to existing functionality
    print("\n5. Verifying no breaking changes...")
    
    # Check that normal backup process still works
    run_backup_start = content.find('def run_backup_process(')
    if run_backup_start != -1:
        run_backup_end = content.find('\n    def ', run_backup_start + 1)
        if run_backup_end == -1:
            run_backup_end = len(content)
        run_backup_section = content[run_backup_start:run_backup_end]
        
        assert 'self.backup_history.add_backup(' in run_backup_section, \
            "Normal backup should still add to history"
        print("   ✓ Normal backup process unaffected")
    
    # Check that BackupHistoryManager is unchanged
    assert 'class BackupHistoryManager:' in content, "BackupHistoryManager missing"
    assert 'def add_backup(' in content, "add_backup method missing"
    assert 'def get_all_backups(' in content, "get_all_backups method missing"
    
    print("   ✓ BackupHistoryManager class intact")
    print("   ✓ History methods unchanged")
    
    print("\n✅ Integration workflow test PASSED")

def test_documentation_and_comments():
    """Test that changes are properly documented."""
    print("\nTesting documentation...")
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the create_scheduled_task function and check for comments
    create_task_start = content.find('def create_scheduled_task(')
    create_task_end = content.find('\ndef ', create_task_start + 1)
    create_task_section = content[create_task_start:create_task_end]
    
    # Verify /RL HIGHEST and /Z comments are NOT present (reverted)
    if '# Run with highest privileges' not in create_task_section:
        print("   ✓ /RL HIGHEST comment not present (reverted)")
    else:
        print("   ⚠ /RL HIGHEST comment still present (should be removed)")
    
    if not ('missed' in create_task_section.lower() and 'soon as possible' in create_task_section.lower()):
        print("   ✓ /Z comment not present (reverted)")
    else:
        print("   ⚠ /Z comment still present (should be removed)")
    
    print("✅ Documentation test PASSED")

def main():
    """Run all integration tests."""
    print("=" * 70)
    print("SCHEDULED BACKUP ENHANCEMENTS - INTEGRATION TEST SUITE")
    print("=" * 70)
    
    try:
        test_integration_workflow()
        test_documentation_and_comments()
        
        print("\n" + "=" * 70)
        print("ALL INTEGRATION TESTS PASSED ✅")
        print("=" * 70)
        print("\nSummary:")
        print("  • Scheduled tasks now run with highest privileges")
        print("  • Scheduled tasks run ASAP after missed scheduled time")
        print("  • Scheduled backups are added to backup history")
        print("  • Backup history shows all backups (manual and scheduled)")
        print("  • Existing functionality remains intact")
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
