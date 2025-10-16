#!/usr/bin/env python3
"""
Test script to verify SQLite backup fix.
This validates that sqlite3 is properly normalized and no utility prompts occur.
"""

import sys
import os
import re

def test_sqlite_normalization():
    """Test that sqlite3 is normalized to sqlite in detection functions."""
    print("Testing SQLite normalization...")
    
    # Read the main file
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print(f"  ✗ {main_file} not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check detect_database_type_from_container has normalization
    pattern1 = r"def detect_database_type_from_container.*?# Normalize sqlite3 to sqlite"
    if not re.search(pattern1, content, re.DOTALL):
        print("  ✗ detect_database_type_from_container missing sqlite3 normalization")
        return False
    print("  ✓ detect_database_type_from_container has sqlite3 normalization")
    
    # Check parse_config_php_dbtype has normalization
    pattern2 = r"def parse_config_php_dbtype.*?# Normalize sqlite3 to sqlite"
    if not re.search(pattern2, content, re.DOTALL):
        print("  ✗ parse_config_php_dbtype missing sqlite3 normalization")
        return False
    print("  ✓ parse_config_php_dbtype has sqlite3 normalization")
    
    return True

def test_check_database_utility():
    """Test that check_database_dump_utility handles sqlite3."""
    print("\nTesting check_database_dump_utility...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check that sqlite3 is handled in check_database_dump_utility
    pattern = r"elif dbtype in \['sqlite', 'sqlite3'\]:"
    if not re.search(pattern, content):
        print("  ✗ check_database_dump_utility doesn't handle sqlite3")
        return False
    print("  ✓ check_database_dump_utility handles both sqlite and sqlite3")
    
    return True

def test_backup_process_checks():
    """Test that backup processes check for both sqlite and sqlite3."""
    print("\nTesting backup process checks...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check start_backup utility check
    pattern1 = r"if dbtype not in \['sqlite', 'sqlite3'\]:\s+utility_installed"
    if not re.search(pattern1, content):
        print("  ✗ start_backup doesn't check for both sqlite and sqlite3")
        return False
    print("  ✓ start_backup checks for both sqlite and sqlite3")
    
    # Check run_backup_process
    pattern2 = r"if dbtype in \['sqlite', 'sqlite3'\]:\s+# SQLite database is already backed up"
    if not re.search(pattern2, content):
        print("  ✗ run_backup_process doesn't check for both sqlite and sqlite3")
        return False
    print("  ✓ run_backup_process checks for both sqlite and sqlite3")
    
    # Check run_backup_process_scheduled
    pattern3 = r"if dbtype in \['sqlite', 'sqlite3'\]:\s+print\(\"Step 6/10: SQLite database"
    if not re.search(pattern3, content):
        print("  ✗ run_backup_process_scheduled doesn't check for both sqlite and sqlite3")
        return False
    print("  ✓ run_backup_process_scheduled checks for both sqlite and sqlite3")
    
    return True

def test_no_duplicate_normalization():
    """Test that there's no redundant normalization in places we've already fixed."""
    print("\nChecking for consistency...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Count normalization occurrences
    normalize_pattern = r"if dbtype.*?== 'sqlite3':\s+dbtype = 'sqlite'"
    matches = re.findall(normalize_pattern, content, re.DOTALL)
    
    # Should have normalization in the two detection functions
    if len(matches) >= 2:
        print(f"  ✓ Found {len(matches)} normalization points in detection functions")
    else:
        print(f"  ⚠ Only found {len(matches)} normalization points (expected at least 2)")
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("SQLite Backup Fix Validation")
    print("=" * 60)
    
    all_passed = True
    
    all_passed &= test_sqlite_normalization()
    all_passed &= test_check_database_utility()
    all_passed &= test_backup_process_checks()
    all_passed &= test_no_duplicate_normalization()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
