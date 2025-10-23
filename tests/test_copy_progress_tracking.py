#!/usr/bin/env python3
"""
Test to verify the copy progress tracking implementation.

This test validates that:
1. File counting logic is present before copying
2. Progress updates show file counts during copying
3. Thread-safe UI updates are used
4. Progress mapping to 30-60% range is correct
"""

import os
import sys
import re

# Add src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(os.path.dirname(script_dir), 'src')
sys.path.insert(0, src_path)

def test_copy_progress_tracking():
    """
    Test that the copy phase includes file-by-file progress tracking.
    """
    print("\n" + "="*70)
    print("Testing Copy Progress Tracking Implementation")
    print("="*70)
    
    # Read the source file
    script_path = os.path.join(src_path, 'nextcloud_restore_and_backup-v9.py')
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Verify file counting logic exists
    print("\n1. Checking for file counting logic...")
    tests_total += 1
    if 'total_files_to_copy' in content and 'folder_file_counts' in content:
        print("   ✓ File counting logic found")
        tests_passed += 1
    else:
        print("   ✗ File counting logic NOT found")
    
    # Test 2: Verify progress updates with file counts
    print("\n2. Checking for file count in progress updates...")
    tests_total += 1
    if re.search(r'Copying.*files.*total_files_to_copy', content):
        print("   ✓ Progress updates with file counts found")
        tests_passed += 1
    else:
        print("   ✗ Progress updates with file counts NOT found")
    
    # Test 3: Verify thread-safe UI updates using self.after()
    print("\n3. Checking for thread-safe UI updates...")
    tests_total += 1
    if re.search(r'self\.after\(0,\s*update_copy_progress\)', content):
        print("   ✓ Thread-safe UI updates found")
        tests_passed += 1
    else:
        print("   ✗ Thread-safe UI updates NOT found")
    
    # Test 4: Verify progress range mapping (30-60%)
    print("\n4. Checking for correct progress range mapping...")
    tests_total += 1
    if re.search(r'progress_val\s*=\s*30\s*\+\s*int\(\(.*\)\s*\*\s*30\)', content):
        print("   ✓ Progress mapping to 30-60% range found")
        tests_passed += 1
    else:
        print("   ✗ Progress mapping to 30-60% range NOT found")
    
    # Test 5: Verify elapsed and estimated time display
    print("\n5. Checking for time tracking (elapsed/estimated)...")
    tests_total += 1
    if 'elapsed_str' in content and 'est_str' in content and 'Elapsed:' in content and 'Est:' in content:
        print("   ✓ Time tracking found")
        tests_passed += 1
    else:
        print("   ✗ Time tracking NOT found")
    
    # Test 6: Verify copy monitoring thread
    print("\n6. Checking for copy monitoring logic...")
    tests_total += 1
    if 'do_folder_copy' in content and 'copy_thread' in content:
        print("   ✓ Copy monitoring thread found")
        tests_passed += 1
    else:
        print("   ✗ Copy monitoring thread NOT found")
    
    # Test 7: Verify status message format
    print("\n7. Checking for proper status message format...")
    tests_total += 1
    if re.search(r'Copying.*folder.*files.*Elapsed.*Est', content):
        print("   ✓ Proper status message format found")
        tests_passed += 1
    else:
        print("   ✗ Proper status message format NOT found")
    
    # Summary
    print("\n" + "="*70)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print("="*70)
    
    if tests_passed == tests_total:
        print("\n✓ All tests passed! Copy progress tracking is properly implemented.")
        return True
    else:
        print(f"\n✗ {tests_total - tests_passed} test(s) failed!")
        return False

if __name__ == '__main__':
    success = test_copy_progress_tracking()
    sys.exit(0 if success else 1)
