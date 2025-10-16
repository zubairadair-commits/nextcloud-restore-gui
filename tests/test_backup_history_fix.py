#!/usr/bin/env python3
"""
Test that backup history is properly initialized in both GUI and scheduled modes.
Verifies the fix for the bug where BackupHistoryManager was not initialized in scheduled mode.
"""

import sys
import os
import tempfile
from pathlib import Path

def test_backup_history_manager_basic():
    """Test BackupHistoryManager functionality."""
    print("Testing BackupHistoryManager basic functionality...")
    
    # Read the main file to verify BackupHistoryManager class exists
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    assert 'class BackupHistoryManager:' in content, "BackupHistoryManager class should exist"
    print("  ✓ BackupHistoryManager class exists")
    
    # Verify add_backup method has diagnostic logging
    add_backup_start = content.find('def add_backup(self,')
    assert add_backup_start != -1, "add_backup method should exist"
    
    add_backup_end = content.find('\n    def ', add_backup_start + 1)
    if add_backup_end == -1:
        add_backup_end = len(content)
    add_backup_section = content[add_backup_start:add_backup_end]
    
    assert 'logger.info' in add_backup_section, "add_backup should have logger.info calls"
    assert 'BACKUP HISTORY:' in add_backup_section, "add_backup should log with BACKUP HISTORY prefix"
    assert 'Database location:' in add_backup_section, "add_backup should log database location"
    print("  ✓ add_backup method has diagnostic logging")
    
    return True

def test_scheduled_mode_initialization():
    """Test that BackupHistoryManager is initialized in scheduled mode."""
    print("\nTesting scheduled mode initialization...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find the __init__ method
    init_start = content.find('def __init__(self, scheduled_mode=False):')
    assert init_start != -1, "__init__ method should exist"
    
    # Find the early return for scheduled mode
    early_return = content.find('if scheduled_mode:\n            return', init_start)
    assert early_return != -1, "Early return for scheduled_mode should exist"
    
    # Find where backup_history is initialized
    backup_history_init = content.find('self.backup_history = BackupHistoryManager()', init_start)
    assert backup_history_init != -1, "backup_history should be initialized"
    
    # Verify backup_history is initialized BEFORE the early return
    assert backup_history_init < early_return, \
        "backup_history must be initialized BEFORE the early return in scheduled mode"
    print("  ✓ backup_history is initialized before early return in scheduled mode")
    
    # Check that the initialization includes logging
    init_section = content[init_start:early_return + 100]
    assert 'logger.info' in init_section, "Initialization should include logging"
    assert 'Backup history manager initialized' in init_section, "Should log initialization message"
    print("  ✓ Initialization includes diagnostic logging")
    
    return True

def test_scheduled_backup_adds_to_history():
    """Test that scheduled backup process adds to history."""
    print("\nTesting scheduled backup adds to history...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find run_backup_process_scheduled method
    scheduled_backup_start = content.find('def run_backup_process_scheduled(self,')
    assert scheduled_backup_start != -1, "run_backup_process_scheduled method should exist"
    
    scheduled_backup_end = content.find('\n    def ', scheduled_backup_start + 1)
    if scheduled_backup_end == -1:
        scheduled_backup_end = content.find('\n    # -----', scheduled_backup_start + 1)
    scheduled_backup_section = content[scheduled_backup_start:scheduled_backup_end]
    
    # Verify it calls add_backup
    assert 'self.backup_history.add_backup(' in scheduled_backup_section, \
        "Scheduled backup should call add_backup"
    print("  ✓ Scheduled backup calls add_backup")
    
    # Verify it has diagnostic logging
    assert 'logger.info' in scheduled_backup_section, "Should have logger.info calls"
    assert 'SCHEDULED BACKUP:' in scheduled_backup_section, "Should log with SCHEDULED BACKUP prefix"
    assert 'Adding to history' in scheduled_backup_section, "Should log when adding to history"
    print("  ✓ Scheduled backup has diagnostic logging")
    
    # Verify it prints the database location
    assert 'Database location:' in scheduled_backup_section or 'db_path' in scheduled_backup_section, \
        "Should show database location to user"
    print("  ✓ Scheduled backup shows database location")
    
    return True

def test_gui_backup_adds_to_history():
    """Test that GUI backup process adds to history."""
    print("\nTesting GUI backup adds to history...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find run_backup_process method (not the scheduled version)
    gui_backup_start = content.find('def run_backup_process(self, backup_dir, encrypt, encryption_password, container_name):')
    assert gui_backup_start != -1, "run_backup_process method should exist"
    
    gui_backup_end = content.find('\n    # --- Restore logic', gui_backup_start + 1)
    if gui_backup_end == -1:
        gui_backup_end = content.find('\n    def ', gui_backup_start + 1)
    gui_backup_section = content[gui_backup_start:gui_backup_end]
    
    # Verify it calls add_backup
    assert 'self.backup_history.add_backup(' in gui_backup_section, \
        "GUI backup should call add_backup"
    print("  ✓ GUI backup calls add_backup")
    
    # Verify it has diagnostic logging
    assert 'logger.info' in gui_backup_section, "Should have logger.info calls"
    assert 'GUI BACKUP:' in gui_backup_section, "Should log with GUI BACKUP prefix"
    assert 'Adding to history' in gui_backup_section, "Should log when adding to history"
    print("  ✓ GUI backup has diagnostic logging")
    
    return True

def test_no_duplicate_initialization():
    """Test that backup_history is only initialized once."""
    print("\nTesting no duplicate initialization...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find all occurrences of backup_history initialization in __init__
    init_start = content.find('def __init__(self, scheduled_mode=False):')
    init_end = content.find('\n    def ', init_start + 1)
    if init_end == -1:
        init_end = content.find('\n\n    def ', init_start + 1)
    init_section = content[init_start:init_end]
    
    # Count initializations
    init_count = init_section.count('self.backup_history = BackupHistoryManager()')
    
    assert init_count == 1, f"backup_history should be initialized exactly once, found {init_count} times"
    print(f"  ✓ backup_history is initialized exactly once in __init__")
    
    return True

def main():
    """Run all tests."""
    print("=" * 70)
    print("BACKUP HISTORY FIX VERIFICATION TEST")
    print("=" * 70)
    print()
    
    try:
        test_backup_history_manager_basic()
        test_scheduled_mode_initialization()
        test_scheduled_backup_adds_to_history()
        test_gui_backup_adds_to_history()
        test_no_duplicate_initialization()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✅")
        print("=" * 70)
        print("\nVerification Summary:")
        print("  ✓ BackupHistoryManager is properly initialized in both modes")
        print("  ✓ Scheduled backups can now add to history database")
        print("  ✓ GUI backups continue to add to history database")
        print("  ✓ Diagnostic logging added to track when backups are added")
        print("  ✓ Database location is logged for transparency")
        print("\nThe fix ensures that:")
        print("  • ALL backups (GUI + scheduled) are added to the same database")
        print("  • Users can verify backup additions via log files")
        print("  • Database file location is clearly shown in logs")
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
