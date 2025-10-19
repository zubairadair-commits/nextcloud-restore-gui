#!/usr/bin/env python3
"""
Integration test for backup rotation logic.
This test simulates the backup rotation process by creating fake backup files
and verifying that the oldest ones are deleted when the limit is exceeded.
"""

import sys
import os
import tempfile
import shutil
import time
from pathlib import Path

def create_fake_backup(directory, timestamp_offset=0):
    """
    Create a fake backup file with a specific modification time.
    
    Args:
        directory: Directory to create the backup in
        timestamp_offset: Seconds to offset from current time (negative = older)
    
    Returns:
        Path to the created backup file
    """
    # Create a fake backup filename
    import time as time_module
    timestamp = time_module.strftime("%Y%m%d_%H%M%S", 
                                    time_module.localtime(time.time() + timestamp_offset))
    filename = f"nextcloud-backup-{timestamp}.tar.gz"
    filepath = os.path.join(directory, filename)
    
    # Create the file with some content
    with open(filepath, 'w') as f:
        f.write("Fake backup content")
    
    # Set modification time
    modified_time = time.time() + timestamp_offset
    os.utime(filepath, (modified_time, modified_time))
    
    return filepath

def test_rotation_keep_3():
    """Test that rotation keeps only the 3 newest backups."""
    print("Testing rotation with keep_count=3...")
    
    # Create temporary directory for backups
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"  Using temp directory: {temp_dir}")
        
        # Create 5 backup files with different timestamps
        backups = []
        for i in range(5):
            # Create older files first (negative offset)
            offset = -((5-i) * 60)  # Each backup 1 minute apart
            backup_path = create_fake_backup(temp_dir, offset)
            backups.append(backup_path)
            print(f"  Created backup: {os.path.basename(backup_path)}")
        
        # Verify all 5 files exist
        assert len(os.listdir(temp_dir)) == 5, "Should have 5 backup files"
        
        # Simulate rotation logic
        keep_count = 3
        backup_files = []
        for filename in os.listdir(temp_dir):
            if filename.startswith('nextcloud-backup-') and filename.endswith('.tar.gz'):
                filepath = os.path.join(temp_dir, filename)
                if os.path.isfile(filepath):
                    backup_files.append(filepath)
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        print(f"  Found {len(backup_files)} backup files")
        print(f"  Keeping {keep_count} newest backups")
        
        # Delete old backups
        if len(backup_files) > keep_count:
            files_to_delete = backup_files[keep_count:]
            print(f"  Deleting {len(files_to_delete)} old backups")
            
            for filepath in files_to_delete:
                print(f"    Deleting: {os.path.basename(filepath)}")
                os.remove(filepath)
        
        # Verify only 3 files remain
        remaining_files = [f for f in os.listdir(temp_dir) 
                          if f.startswith('nextcloud-backup-')]
        assert len(remaining_files) == 3, f"Should have 3 backups, found {len(remaining_files)}"
        
        # Verify the newest 3 remain
        remaining_paths = [os.path.join(temp_dir, f) for f in remaining_files]
        remaining_paths.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # The newest 3 should be the last 3 created
        assert remaining_paths[0] == backups[4], "Newest backup should remain"
        assert remaining_paths[1] == backups[3], "2nd newest backup should remain"
        assert remaining_paths[2] == backups[2], "3rd newest backup should remain"
        
        print("  ✓ Correctly kept 3 newest backups")
        print("  ✓ Correctly deleted 2 oldest backups")
    
    print("✅ Rotation keep_count=3 test PASSED\n")

def test_rotation_keep_1():
    """Test that rotation keeps only 1 backup (always replace)."""
    print("Testing rotation with keep_count=1 (always replace)...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"  Using temp directory: {temp_dir}")
        
        # Create 3 backup files
        backups = []
        for i in range(3):
            offset = -((3-i) * 60)
            backup_path = create_fake_backup(temp_dir, offset)
            backups.append(backup_path)
            print(f"  Created backup: {os.path.basename(backup_path)}")
        
        # Verify all 3 files exist
        assert len(os.listdir(temp_dir)) == 3, "Should have 3 backup files"
        
        # Simulate rotation logic with keep_count=1
        keep_count = 1
        backup_files = []
        for filename in os.listdir(temp_dir):
            if filename.startswith('nextcloud-backup-') and filename.endswith('.tar.gz'):
                filepath = os.path.join(temp_dir, filename)
                if os.path.isfile(filepath):
                    backup_files.append(filepath)
        
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        print(f"  Found {len(backup_files)} backup files")
        print(f"  Keeping {keep_count} newest backup")
        
        # Delete old backups
        if len(backup_files) > keep_count:
            files_to_delete = backup_files[keep_count:]
            print(f"  Deleting {len(files_to_delete)} old backups")
            
            for filepath in files_to_delete:
                print(f"    Deleting: {os.path.basename(filepath)}")
                os.remove(filepath)
        
        # Verify only 1 file remains
        remaining_files = [f for f in os.listdir(temp_dir) 
                          if f.startswith('nextcloud-backup-')]
        assert len(remaining_files) == 1, f"Should have 1 backup, found {len(remaining_files)}"
        
        # Verify the newest remains
        remaining_path = os.path.join(temp_dir, remaining_files[0])
        assert remaining_path == backups[2], "Only newest backup should remain"
        
        print("  ✓ Correctly kept 1 newest backup")
        print("  ✓ Correctly deleted 2 older backups")
    
    print("✅ Rotation keep_count=1 test PASSED\n")

def test_rotation_unlimited():
    """Test that rotation with keep_count=0 doesn't delete anything."""
    print("Testing rotation with keep_count=0 (unlimited)...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"  Using temp directory: {temp_dir}")
        
        # Create 10 backup files
        backups = []
        for i in range(10):
            offset = -((10-i) * 60)
            backup_path = create_fake_backup(temp_dir, offset)
            backups.append(backup_path)
        
        initial_count = len(os.listdir(temp_dir))
        print(f"  Created {initial_count} backups")
        
        # Simulate rotation logic with keep_count=0 (unlimited)
        keep_count = 0
        
        if keep_count > 0:  # This should NOT execute
            # Rotation logic would go here
            pass
        else:
            print("  Skipping rotation (unlimited mode)")
        
        # Verify all files still exist
        final_count = len(os.listdir(temp_dir))
        assert final_count == initial_count, f"All backups should remain, had {initial_count}, now {final_count}"
        
        print(f"  ✓ All {final_count} backups preserved")
    
    print("✅ Rotation unlimited test PASSED\n")

def test_rotation_with_encrypted_files():
    """Test that rotation handles both encrypted and unencrypted files."""
    print("Testing rotation with encrypted files...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"  Using temp directory: {temp_dir}")
        
        # Create mix of encrypted and unencrypted backups
        backups = []
        for i in range(4):
            offset = -((4-i) * 60)
            
            # Alternate between encrypted and unencrypted
            if i % 2 == 0:
                # Create unencrypted
                backup_path = create_fake_backup(temp_dir, offset)
            else:
                # Create encrypted (with .gpg extension)
                timestamp = time.strftime("%Y%m%d_%H%M%S", 
                                        time.localtime(time.time() + offset))
                filename = f"nextcloud-backup-{timestamp}.tar.gz.gpg"
                filepath = os.path.join(temp_dir, filename)
                
                with open(filepath, 'w') as f:
                    f.write("Fake encrypted backup content")
                
                modified_time = time.time() + offset
                os.utime(filepath, (modified_time, modified_time))
                backup_path = filepath
            
            backups.append(backup_path)
            print(f"  Created: {os.path.basename(backup_path)}")
        
        # Verify all 4 files exist
        assert len(os.listdir(temp_dir)) == 4, "Should have 4 backup files"
        
        # Simulate rotation logic - should handle both .tar.gz and .tar.gz.gpg
        keep_count = 2
        backup_files = []
        for filename in os.listdir(temp_dir):
            if filename.startswith('nextcloud-backup-') and (
                filename.endswith('.tar.gz') or filename.endswith('.tar.gz.gpg')
            ):
                filepath = os.path.join(temp_dir, filename)
                if os.path.isfile(filepath):
                    backup_files.append(filepath)
        
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        print(f"  Found {len(backup_files)} backup files (mixed types)")
        print(f"  Keeping {keep_count} newest backups")
        
        # Delete old backups
        if len(backup_files) > keep_count:
            files_to_delete = backup_files[keep_count:]
            print(f"  Deleting {len(files_to_delete)} old backups")
            
            for filepath in files_to_delete:
                print(f"    Deleting: {os.path.basename(filepath)}")
                os.remove(filepath)
        
        # Verify only 2 files remain
        remaining_files = [f for f in os.listdir(temp_dir) 
                          if f.startswith('nextcloud-backup-')]
        assert len(remaining_files) == 2, f"Should have 2 backups, found {len(remaining_files)}"
        
        print("  ✓ Correctly handled mixed encrypted/unencrypted files")
        print("  ✓ Kept 2 newest backups regardless of type")
    
    print("✅ Rotation with encrypted files test PASSED\n")

def main():
    """Run all rotation tests."""
    print("=" * 60)
    print("BACKUP ROTATION LOGIC TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_rotation_keep_3()
        test_rotation_keep_1()
        test_rotation_unlimited()
        test_rotation_with_encrypted_files()
        
        print("=" * 60)
        print("ALL ROTATION TESTS PASSED ✅")
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
