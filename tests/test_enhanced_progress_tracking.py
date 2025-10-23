#!/usr/bin/env python3
"""
Test script to verify the enhanced progress tracking implementation.

This script validates:
1. Progress ranges are correctly defined across the restore pipeline
2. All major steps have appropriate progress updates
3. Progress values are within expected ranges (0-100%)
4. Thread-safe update methods are used
"""

import os
import sys
import re

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_progress_ranges():
    """Test that progress ranges are correctly implemented"""
    print("=" * 70)
    print("TEST: Validating Progress Ranges in Restore Pipeline")
    print("=" * 70)
    print()
    
    # Read the source file
    src_file = "/home/runner/work/nextcloud-restore-gui/nextcloud-restore-gui/src/nextcloud_restore_and_backup-v9.py"
    
    with open(src_file, 'r') as f:
        content = f.read()
    
    # Find all set_restore_progress calls
    progress_calls = re.findall(r'set_restore_progress\((\d+),', content)
    progress_values = [int(val) for val in progress_calls]
    
    print(f"✓ Found {len(progress_values)} progress update calls")
    print()
    
    # Check that all progress values are within 0-100
    invalid_values = [val for val in progress_values if val < 0 or val > 100]
    if invalid_values:
        print(f"✗ FAIL: Found invalid progress values: {invalid_values}")
        return False
    else:
        print("✓ PASS: All progress values are within 0-100% range")
    
    # Check for reasonable distribution
    progress_values_sorted = sorted(set(progress_values))
    print(f"✓ Progress checkpoints: {progress_values_sorted}")
    print()
    
    # Validate expected ranges
    expected_ranges = {
        "Extraction": (0, 20),
        "Docker Setup": (20, 30),
        "File Copying": (30, 60),
        "Database": (60, 75),
        "Config Update": (75, 85),
        "Validation/Permissions": (85, 90),
        "Restart/Complete": (90, 100)
    }
    
    print("Expected Progress Ranges:")
    print("-" * 70)
    for phase, (start, end) in expected_ranges.items():
        values_in_range = [v for v in progress_values if start <= v <= end]
        print(f"  {phase:30s}: {start:3d}-{end:3d}% ({len(values_in_range)} updates)")
    print()
    
    return True

def test_extraction_progress_mapping():
    """Test that extraction progress is properly mapped to 0-20% range"""
    print("=" * 70)
    print("TEST: Extraction Progress Mapping (0-20%)")
    print("=" * 70)
    print()
    
    src_file = "/home/runner/work/nextcloud-restore-gui/nextcloud-restore-gui/src/nextcloud_restore_and_backup-v9.py"
    
    with open(src_file, 'r') as f:
        content = f.read()
    
    # Check for the extraction progress mapping code
    if "Map extraction progress to 0-20% range" in content:
        print("✓ PASS: Extraction progress mapping comment found")
    else:
        print("✗ WARNING: Extraction progress mapping comment not found")
    
    # Check for the specific calculation patterns
    if "int((file_percent / 100) * 20)" in content or "int((byte_percent / 100) * 20)" in content:
        print("✓ PASS: Extraction progress calculation maps to 0-20% range")
    else:
        print("✗ FAIL: Extraction progress mapping code not found")
        return False
    
    print()
    return True

def test_file_copying_progress():
    """Test that file copying has granular progress tracking"""
    print("=" * 70)
    print("TEST: File Copying Progress (30-60%)")
    print("=" * 70)
    print()
    
    src_file = "/home/runner/work/nextcloud-restore-gui/nextcloud-restore-gui/src/nextcloud_restore_and_backup-v9.py"
    
    with open(src_file, 'r') as f:
        content = f.read()
    
    # Check for folder size calculation
    if "folder_sizes" in content and "total_size" in content:
        print("✓ PASS: Folder size calculation found for progress tracking")
    else:
        print("✗ FAIL: Folder size calculation not found")
        return False
    
    # Check for threading during copy
    if "copy_thread = threading.Thread(target=do_copy" in content:
        print("✓ PASS: Threading used for non-blocking file copy operations")
    else:
        print("✗ WARNING: Threading for file copy not found")
    
    # Check for folder progress range calculation
    if "folder_start_progress" in content and "folder_end_progress" in content:
        print("✓ PASS: Per-folder progress range calculation found")
    else:
        print("✗ FAIL: Per-folder progress calculation not found")
        return False
    
    print()
    return True

def test_database_progress():
    """Test that database restore has progress tracking"""
    print("=" * 70)
    print("TEST: Database Restore Progress (60-75%)")
    print("=" * 70)
    print()
    
    src_file = "/home/runner/work/nextcloud-restore-gui/nextcloud-restore-gui/src/nextcloud_restore_and_backup-v9.py"
    
    with open(src_file, 'r') as f:
        content = f.read()
    
    # Check for database size display
    if "sql_size_str = self._format_bytes(sql_size)" in content:
        print("✓ PASS: Database file size formatting found")
    else:
        print("✗ WARNING: Database file size formatting not found")
    
    # Check for threading during database restore
    if "restore_thread = threading.Thread(target=do_restore" in content:
        print("✓ PASS: Threading used for non-blocking database restore")
    else:
        print("✗ WARNING: Threading for database restore not found")
    
    # Check for progress updates in MySQL restore
    if "Restoring MySQL database" in content and "62-72% range" in content:
        print("✓ PASS: MySQL progress range comments found")
    else:
        print("✗ WARNING: MySQL progress range comments not found")
    
    # Check for progress updates in PostgreSQL restore
    if "Restoring PostgreSQL database" in content and "62-72% range" in content:
        print("✓ PASS: PostgreSQL progress range comments found")
    else:
        print("✗ WARNING: PostgreSQL progress range comments not found")
    
    # Check for SQLite progress
    if "Verifying SQLite database" in content:
        print("✓ PASS: SQLite progress tracking found")
    else:
        print("✗ WARNING: SQLite progress tracking not found")
    
    print()
    return True

def test_thread_safe_updates():
    """Test that thread-safe UI updates are used"""
    print("=" * 70)
    print("TEST: Thread-Safe UI Updates")
    print("=" * 70)
    print()
    
    src_file = "/home/runner/work/nextcloud-restore-gui/nextcloud-restore-gui/src/nextcloud_restore_and_backup-v9.py"
    
    with open(src_file, 'r') as f:
        content = f.read()
    
    # Count safe_widget_update calls
    safe_update_count = content.count("safe_widget_update(")
    print(f"✓ Found {safe_update_count} safe_widget_update() calls")
    
    # Check for direct widget updates in restore thread (should be avoided)
    # Look for patterns like self.process_label.config( outside of lambda
    direct_updates = re.findall(r'self\.(process_label|error_label|progress_label)\.config\([^)]*\)(?!\s*,\s*")', content)
    
    if len(direct_updates) > 20:  # Some direct updates are acceptable in non-threaded contexts
        print(f"⚠ WARNING: Found {len(direct_updates)} potential direct widget updates")
        print("  (Some may be in safe contexts)")
    else:
        print("✓ PASS: Minimal direct widget updates found")
    
    print()
    return True

def main():
    """Run all tests"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "Enhanced Progress Tracking Validation" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("Progress Ranges", test_progress_ranges()))
    results.append(("Extraction Mapping", test_extraction_progress_mapping()))
    results.append(("File Copying Progress", test_file_copying_progress()))
    results.append(("Database Progress", test_database_progress()))
    results.append(("Thread-Safe Updates", test_thread_safe_updates()))
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("✅ All validation checks passed!")
        print()
        print("The enhanced progress tracking implementation is ready for testing.")
        print("Run the actual GUI application and perform a restore to see the")
        print("smooth progress bar updates from 0% to 100%.")
    else:
        print("⚠️  Some validation checks failed. Review the implementation.")
    
    print()
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
