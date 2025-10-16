#!/usr/bin/env python3
"""
Test that backup history only displays backups that exist on disk.
Verifies that missing backups are removed from the database and not shown in the UI.
"""

import sys
import os
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime
import json

def test_delete_backup_method():
    """Test that delete_backup method exists and works correctly."""
    print("Testing delete_backup method...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Verify delete_backup method exists in BackupHistoryManager
    assert 'def delete_backup(self, backup_id):' in content, \
        "delete_backup method should exist in BackupHistoryManager"
    print("  ✓ delete_backup method exists")
    
    # Find the delete_backup method
    delete_start = content.find('def delete_backup(self, backup_id):')
    delete_end = content.find('\n    def ', delete_start + 1)
    if delete_end == -1:
        delete_end = content.find('\n\n# ---', delete_start + 1)
    delete_section = content[delete_start:delete_end]
    
    # Verify it has SQL DELETE statement
    assert 'DELETE FROM backups WHERE id = ?' in delete_section, \
        "delete_backup should execute DELETE SQL statement"
    print("  ✓ delete_backup executes DELETE SQL statement")
    
    # Verify it has logging
    assert 'logger.info' in delete_section, "delete_backup should log the deletion"
    print("  ✓ delete_backup logs the deletion")
    
    return True

def test_show_backup_history_filters_missing():
    """Test that show_backup_history filters out missing backups."""
    print("\nTesting show_backup_history filters missing backups...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find show_backup_history method
    show_history_start = content.find('def show_backup_history(self):')
    assert show_history_start != -1, "show_backup_history method should exist"
    
    show_history_end = content.find('\n    def ', show_history_start + 1)
    if show_history_end == -1:
        show_history_end = len(content)
    show_history_section = content[show_history_start:show_history_end]
    
    # Verify it checks if backup files exist
    assert 'os.path.exists(backup_path)' in show_history_section, \
        "show_backup_history should check if backup files exist"
    print("  ✓ show_backup_history checks if backup files exist")
    
    # Verify it filters backups
    assert 'existing_backups' in show_history_section or 'if os.path.exists' in show_history_section, \
        "show_backup_history should filter existing backups"
    print("  ✓ show_backup_history filters backups based on file existence")
    
    # Verify it calls delete_backup for missing files
    assert 'self.backup_history.delete_backup(' in show_history_section, \
        "show_backup_history should call delete_backup for missing files"
    print("  ✓ show_backup_history removes missing backups from database")
    
    # Verify it logs removal
    assert 'logger.info' in show_history_section and 'missing' in show_history_section.lower(), \
        "show_backup_history should log when removing missing backups"
    print("  ✓ show_backup_history logs missing backup removal")
    
    return True

def test_database_cleanup_logic():
    """Test the database cleanup logic with a temporary database."""
    print("\nTesting database cleanup logic...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_backup_history.db"
        
        # Create database with same schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_path TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                size_bytes INTEGER,
                encrypted BOOLEAN,
                database_type TEXT,
                folders_backed_up TEXT,
                verification_status TEXT,
                verification_details TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("  ✓ Test database created")
        
        # Create a temporary backup file that exists
        existing_backup = Path(tmpdir) / "existing-backup.tar.gz"
        existing_backup.write_text("test backup content")
        
        # Add backups - one exists, one doesn't
        test_backups = [
            (str(existing_backup), "Existing backup", False),
            ("/nonexistent/path/missing-backup.tar.gz", "Missing backup", False),
            (str(Path(tmpdir) / "also-missing.tar.gz"), "Another missing", True),
        ]
        
        for path, notes, encrypted in test_backups:
            timestamp = datetime.now().isoformat()
            folders = json.dumps(["config", "data"])
            
            cursor.execute('''
                INSERT INTO backups 
                (backup_path, timestamp, size_bytes, encrypted, database_type, 
                 folders_backed_up, notes, verification_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (path, timestamp, 1024*1024*100, encrypted, "pgsql", 
                  folders, notes, "success"))
            conn.commit()
        
        print(f"  ✓ Added {len(test_backups)} test backups (1 existing, 2 missing)")
        
        # Get all backups
        cursor.execute('SELECT id, backup_path FROM backups ORDER BY id')
        all_backups = cursor.fetchall()
        assert len(all_backups) == 3, "Should have 3 backups initially"
        print(f"  ✓ Verified {len(all_backups)} backups in database")
        
        # Simulate filtering logic - remove backups that don't exist
        backups_to_delete = []
        for backup_id, backup_path in all_backups:
            if not os.path.exists(backup_path):
                backups_to_delete.append(backup_id)
        
        assert len(backups_to_delete) == 2, "Should identify 2 missing backups"
        print(f"  ✓ Identified {len(backups_to_delete)} missing backups")
        
        # Delete missing backups
        for backup_id in backups_to_delete:
            cursor.execute('DELETE FROM backups WHERE id = ?', (backup_id,))
            conn.commit()
        
        # Verify only existing backup remains
        cursor.execute('SELECT id, backup_path FROM backups')
        remaining_backups = cursor.fetchall()
        assert len(remaining_backups) == 1, "Should have only 1 backup remaining"
        assert os.path.exists(remaining_backups[0][1]), "Remaining backup should exist"
        print(f"  ✓ Successfully cleaned up database, {len(remaining_backups)} backup(s) remain")
        
        conn.close()
    
    print("✅ Database cleanup logic test PASSED")
    return True

def test_action_buttons_not_affected():
    """Test that action buttons (_restore_from_history, _verify_backup_from_history, _export_backup)
    still have their file existence checks."""
    print("\nTesting action button methods still have file existence checks...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    methods_to_check = [
        '_restore_from_history',
        '_verify_backup_from_history',
        '_export_backup'
    ]
    
    for method_name in methods_to_check:
        method_start = content.find(f'def {method_name}(self,')
        assert method_start != -1, f"{method_name} method should exist"
        
        method_end = content.find('\n    def ', method_start + 1)
        if method_end == -1:
            method_end = len(content)
        method_section = content[method_start:method_end]
        
        assert 'os.path.exists(backup_path)' in method_section, \
            f"{method_name} should still check if backup file exists"
        print(f"  ✓ {method_name} still has file existence check")
    
    return True

def main():
    """Run all tests."""
    print("=" * 70)
    print("BACKUP HISTORY MISSING FILES TEST")
    print("=" * 70)
    print()
    
    try:
        test_delete_backup_method()
        test_show_backup_history_filters_missing()
        test_database_cleanup_logic()
        test_action_buttons_not_affected()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✅")
        print("=" * 70)
        print("\nSummary:")
        print("  • Backup History page only shows backups that exist on disk")
        print("  • Missing backups are automatically removed from database")
        print("  • Database cleanup happens when viewing history")
        print("  • Action buttons retain their file existence checks")
        print("  • Changes are logged for transparency")
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
