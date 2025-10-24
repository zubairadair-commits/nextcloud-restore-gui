#!/usr/bin/env python3
"""
Test admin username extraction from restored database.

This test verifies that:
1. extract_admin_username method exists and handles different database types
2. The method properly queries SQLite, MySQL, and PostgreSQL databases
3. The completion dialog accepts and displays the admin username
4. Error handling is in place for failed extractions
"""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_extract_admin_username_exists():
    """Test that extract_admin_username method exists"""
    print("Testing extract_admin_username method existence...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check that the method exists
    if 'def extract_admin_username(self, container_name, dbtype):' in source:
        print("  ✓ extract_admin_username method exists")
    else:
        print("  ✗ extract_admin_username method not found")
        return False
    
    return True


def test_extract_admin_username_handles_sqlite():
    """Test that extract_admin_username handles SQLite databases"""
    print("\nTesting SQLite support in extract_admin_username...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for SQLite-specific query
    if "dbtype == 'sqlite'" in source and 'sqlite3' in source:
        print("  ✓ SQLite database extraction is implemented")
    else:
        print("  ✗ SQLite database extraction not found")
        return False
    
    # Check for proper SQL query
    if 'oc_users' in source and 'oc_group_user' in source and "gid = 'admin'" in source:
        print("  ✓ Proper SQL query for admin users is present")
    else:
        print("  ✗ SQL query for admin users not found")
        return False
    
    return True


def test_extract_admin_username_handles_mysql():
    """Test that extract_admin_username handles MySQL/MariaDB databases"""
    print("\nTesting MySQL support in extract_admin_username...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for MySQL-specific handling
    if "dbtype in ['mysql', 'mariadb']" in source or "elif dbtype == 'mysql'" in source or "elif dbtype in ['mysql'" in source:
        print("  ✓ MySQL database extraction is implemented")
    else:
        print("  ✗ MySQL database extraction not found")
        return False
    
    # Check for MySQL command
    if 'mysql -u' in source or 'mysql' in source:
        print("  ✓ MySQL command is present")
    else:
        print("  ✗ MySQL command not found")
        return False
    
    return True


def test_extract_admin_username_handles_postgresql():
    """Test that extract_admin_username handles PostgreSQL databases"""
    print("\nTesting PostgreSQL support in extract_admin_username...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for PostgreSQL-specific handling
    if "dbtype == 'pgsql'" in source:
        print("  ✓ PostgreSQL database extraction is implemented")
    else:
        print("  ✗ PostgreSQL database extraction not found")
        return False
    
    # Check for psql command
    if 'psql -U' in source or 'psql' in source:
        print("  ✓ PostgreSQL command is present")
    else:
        print("  ✗ PostgreSQL command not found")
        return False
    
    return True


def test_completion_dialog_displays_admin_username():
    """Test that completion dialog displays admin username"""
    print("\nTesting completion dialog admin username display...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check that show_restore_completion_dialog accepts admin_username parameter
    if 'def show_restore_completion_dialog(self, container_name, port, admin_username=' in source:
        print("  ✓ show_restore_completion_dialog accepts admin_username parameter")
    else:
        print("  ✗ show_restore_completion_dialog doesn't accept admin_username parameter")
        return False
    
    # Check that admin username is displayed in the UI
    if 'Log in with your previous admin credentials' in source or 'admin username is:' in source:
        print("  ✓ Admin username message is displayed in UI")
    else:
        print("  ✗ Admin username message not found in UI")
        return False
    
    # Check for conditional display (only when admin_username is available)
    if 'if admin_username:' in source:
        print("  ✓ Admin username is conditionally displayed")
    else:
        print("  ✗ Admin username display not conditional")
        return False
    
    return True


def test_admin_username_extracted_before_completion():
    """Test that admin username is extracted before showing completion dialog"""
    print("\nTesting admin username extraction timing...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check that extract_admin_username is called
    if 'self.extract_admin_username' in source:
        print("  ✓ extract_admin_username is called")
    else:
        print("  ✗ extract_admin_username is not called")
        return False
    
    # Check that it's called before show_restore_completion_dialog
    # Find the positions in the code
    extract_pos = source.find('self.extract_admin_username')
    completion_pos = source.find('self.show_restore_completion_dialog')
    
    if extract_pos > 0 and completion_pos > 0 and extract_pos < completion_pos:
        print("  ✓ Admin username is extracted before showing completion dialog")
    else:
        print("  ✗ Admin username extraction timing issue")
        return False
    
    return True


def test_error_handling():
    """Test that error handling is in place"""
    print("\nTesting error handling in admin username extraction...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for try-except blocks
    if 'try:' in source and 'except' in source:
        print("  ✓ Error handling (try-except) is present")
    else:
        print("  ✗ Error handling not found")
        return False
    
    # Check for timeout handling
    if 'TimeoutExpired' in source or 'timeout=' in source:
        print("  ✓ Timeout handling is present")
    else:
        print("  ⚠ Warning: Timeout handling may not be present")
    
    # Check for logger warnings on failure
    if 'logger.warning' in source:
        print("  ✓ Logger warnings are present for error cases")
    else:
        print("  ✗ Logger warnings not found")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Admin Username Extraction Implementation")
    print("=" * 60)
    
    tests = [
        test_extract_admin_username_exists,
        test_extract_admin_username_handles_sqlite,
        test_extract_admin_username_handles_mysql,
        test_extract_admin_username_handles_postgresql,
        test_completion_dialog_displays_admin_username,
        test_admin_username_extracted_before_completion,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
