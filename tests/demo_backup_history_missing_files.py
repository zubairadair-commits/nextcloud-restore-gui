#!/usr/bin/env python3
"""
Demonstration of the backup history missing files feature.
Shows how the Backup History page filters out missing backup files.
"""

import sys
import os
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime
import json

def demo_backup_history_filtering():
    """Demonstrate backup history filtering for missing files."""
    print("=" * 70)
    print("BACKUP HISTORY - MISSING FILES FILTERING DEMONSTRATION")
    print("=" * 70)
    print()
    print("This demo shows how the Backup History page handles missing files:")
    print()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 Working directory: {tmpdir}")
        print()
        
        # Create database
        db_path = Path(tmpdir) / "backup_history.db"
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
        print("✅ Created test database")
        print()
        
        # Create some backup files
        print("📦 Creating test backup files...")
        backup1 = Path(tmpdir) / "nextcloud-backup-2024-01-15.tar.gz"
        backup1.write_text("test content 1")
        print(f"  ✓ Created: {backup1.name}")
        
        backup2 = Path(tmpdir) / "nextcloud-backup-2024-01-20.tar.gz"
        backup2.write_text("test content 2")
        print(f"  ✓ Created: {backup2.name}")
        
        backup3 = Path(tmpdir) / "nextcloud-backup-2024-01-25.tar.gz"
        backup3.write_text("test content 3")
        print(f"  ✓ Created: {backup3.name}")
        print()
        
        # Add all backups to database
        print("💾 Adding backups to database...")
        test_backups = [
            (str(backup1), "Manual backup", False),
            (str(backup2), "Scheduled backup", True),
            (str(backup3), "Manual backup with encryption", True),
            (str(Path(tmpdir) / "never-existed.tar.gz"), "Old backup", False),
        ]
        
        for path, notes, encrypted in test_backups:
            timestamp = datetime.now().isoformat()
            folders = json.dumps(["config", "data", "apps"])
            
            cursor.execute('''
                INSERT INTO backups 
                (backup_path, timestamp, size_bytes, encrypted, database_type, 
                 folders_backed_up, notes, verification_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (path, timestamp, 1024*1024*150, encrypted, "pgsql", 
                  folders, notes, "success"))
            conn.commit()
            print(f"  ✓ Added: {Path(path).name}")
        
        print(f"\n✅ Total backups in database: {len(test_backups)}")
        print()
        
        # Show initial state
        print("📋 INITIAL STATE - All backups in database:")
        cursor.execute('SELECT id, backup_path, notes FROM backups ORDER BY id')
        all_backups = cursor.fetchall()
        for backup_id, backup_path, notes in all_backups:
            exists = "✅" if os.path.exists(backup_path) else "❌"
            print(f"  {exists} ID {backup_id}: {Path(backup_path).name} - {notes}")
        print()
        
        # Simulate user deleting some backup files
        print("🗑️  SIMULATING USER ACTION: Deleting backup files from disk...")
        backup2.unlink()
        print(f"  ✗ Deleted: {backup2.name}")
        backup3.unlink()
        print(f"  ✗ Deleted: {backup3.name}")
        print()
        
        # Show state after deletion
        print("📋 AFTER DELETION - Files on disk vs database:")
        cursor.execute('SELECT id, backup_path, notes FROM backups ORDER BY id')
        all_backups = cursor.fetchall()
        for backup_id, backup_path, notes in all_backups:
            exists = "✅" if os.path.exists(backup_path) else "❌"
            print(f"  {exists} ID {backup_id}: {Path(backup_path).name} - {notes}")
        print()
        
        # Simulate the filtering logic from show_backup_history
        print("🔍 APPLYING BACKUP HISTORY FILTERING...")
        print("   (This is what happens when you open the Backup History page)")
        print()
        
        cursor.execute('SELECT id, backup_path, notes FROM backups ORDER BY timestamp DESC')
        all_backups = cursor.fetchall()
        
        existing_backups = []
        removed_backups = []
        
        for backup_id, backup_path, notes in all_backups:
            if os.path.exists(backup_path):
                existing_backups.append((backup_id, backup_path, notes))
                print(f"  ✓ KEEP: {Path(backup_path).name} (file exists)")
            else:
                removed_backups.append((backup_id, backup_path, notes))
                # Delete from database
                cursor.execute('DELETE FROM backups WHERE id = ?', (backup_id,))
                conn.commit()
                print(f"  ✗ REMOVE: {Path(backup_path).name} (file missing)")
        
        print()
        print(f"✅ Filtered results: {len(existing_backups)} backups kept, {len(removed_backups)} removed")
        print()
        
        # Show final state
        print("📋 FINAL STATE - What users see in Backup History page:")
        cursor.execute('SELECT id, backup_path, notes FROM backups ORDER BY id')
        final_backups = cursor.fetchall()
        
        if final_backups:
            for backup_id, backup_path, notes in final_backups:
                print(f"  ✅ {Path(backup_path).name}")
                print(f"     Notes: {notes}")
                print(f"     Actions: [Restore] [Verify] [Export]")
                print()
        else:
            print("  (No backups found - would show 'No backup history found' message)")
            print()
        
        conn.close()
    
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print("  • The Backup History page automatically detects missing files")
    print("  • Missing backups are removed from the database")
    print("  • Only existing backups are shown to users")
    print("  • Users can safely restore/verify/export only valid backups")
    print("  • The database stays clean and accurate")
    print()

if __name__ == "__main__":
    try:
        demo_backup_history_filtering()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
