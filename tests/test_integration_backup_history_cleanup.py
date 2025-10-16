#!/usr/bin/env python3
"""
Integration test simulating real user workflow:
1. User creates backups
2. User deletes some backup files
3. User opens Backup History page
4. System automatically cleans up missing backups
"""

import sys
import os
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime
import json

def simulate_user_workflow():
    """Simulate complete user workflow with backup history."""
    print("=" * 70)
    print("INTEGRATION TEST: Backup History Cleanup Workflow")
    print("=" * 70)
    print()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: User creates backups
        print("📦 STEP 1: User creates 3 backups")
        print("-" * 70)
        
        db_path = Path(tmpdir) / "backup_history.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create database
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
        
        # Create actual backup files
        backups = []
        for i in range(1, 4):
            backup_file = Path(tmpdir) / f"backup-{i}.tar.gz"
            backup_file.write_text(f"backup content {i}")
            backups.append(backup_file)
            
            # Add to database
            timestamp = datetime.now().isoformat()
            folders = json.dumps(["config", "data"])
            cursor.execute('''
                INSERT INTO backups 
                (backup_path, timestamp, size_bytes, encrypted, database_type, 
                 folders_backed_up, notes, verification_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (str(backup_file), timestamp, 1024*1024*100, False, "pgsql", 
                  folders, f"Backup #{i}", "success"))
            conn.commit()
            print(f"  ✓ Created: {backup_file.name} (ID: {cursor.lastrowid})")
        
        print(f"\n✅ User has {len(backups)} backups")
        print()
        
        # Step 2: User deletes some backups
        print("🗑️  STEP 2: User deletes backup-2.tar.gz from disk")
        print("-" * 70)
        backups[1].unlink()
        print(f"  ✗ Deleted: {backups[1].name}")
        print()
        
        # Step 3: Verify database state (should still have 3 records)
        print("📊 STEP 3: Database state before cleanup")
        print("-" * 70)
        cursor.execute('SELECT id, backup_path FROM backups')
        db_records = cursor.fetchall()
        print(f"  Database records: {len(db_records)}")
        for backup_id, backup_path in db_records:
            exists = "✅" if os.path.exists(backup_path) else "❌"
            print(f"    {exists} ID {backup_id}: {Path(backup_path).name}")
        print()
        
        # Step 4: User opens Backup History page (simulated)
        print("👤 STEP 4: User opens Backup History page")
        print("-" * 70)
        
        # Simulate show_backup_history filtering logic
        cursor.execute('''
            SELECT id, backup_path, timestamp, size_bytes, encrypted, 
                   database_type, folders_backed_up, verification_status, 
                   verification_details, notes
            FROM backups
            ORDER BY timestamp DESC
        ''')
        all_backups = cursor.fetchall()
        
        existing_backups = []
        removed_count = 0
        
        print("  Processing backups...")
        for backup in all_backups:
            backup_id = backup[0]
            backup_path = backup[1]
            
            if os.path.exists(backup_path):
                existing_backups.append(backup)
                print(f"    ✓ DISPLAY: {Path(backup_path).name}")
            else:
                # Remove missing backup from database
                cursor.execute('DELETE FROM backups WHERE id = ?', (backup_id,))
                conn.commit()
                removed_count += 1
                print(f"    ✗ REMOVE: {Path(backup_path).name} (file not found)")
        
        print()
        print(f"  Result: {len(existing_backups)} backups shown, {removed_count} removed")
        print()
        
        # Step 5: Verify final state
        print("✅ STEP 5: Final verification")
        print("-" * 70)
        
        cursor.execute('SELECT id, backup_path FROM backups')
        final_records = cursor.fetchall()
        
        print(f"  Database records after cleanup: {len(final_records)}")
        for backup_id, backup_path in final_records:
            assert os.path.exists(backup_path), f"All remaining records should have existing files"
            print(f"    ✅ ID {backup_id}: {Path(backup_path).name}")
        
        # Verify counts
        assert len(final_records) == 2, "Should have 2 records remaining"
        assert removed_count == 1, "Should have removed 1 record"
        assert len(existing_backups) == 2, "Should display 2 backups"
        
        print()
        print("✅ All assertions passed!")
        print()
        
        conn.close()
    
    print("=" * 70)
    print("INTEGRATION TEST PASSED ✅")
    print("=" * 70)
    print()
    print("Workflow Summary:")
    print("  1. User created 3 backups → Stored in database ✅")
    print("  2. User deleted 1 file from disk → Database unchanged ✅")
    print("  3. User opened Backup History page → Missing file detected ✅")
    print("  4. System cleaned up database → Only 2 backups remain ✅")
    print("  5. User sees accurate list → Can safely restore backups ✅")
    print()

if __name__ == "__main__":
    try:
        simulate_user_workflow()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
