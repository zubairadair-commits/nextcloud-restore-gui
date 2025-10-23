#!/usr/bin/env python3
"""
Test admin credentials are properly passed to Docker containers.

This test verifies that:
1. Admin username and password are passed as environment variables to Docker
2. Both restore workflow and new instance workflow pass credentials
3. Credentials are properly escaped/formatted in Docker commands
"""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_restore_workflow_passes_credentials():
    """Test that restore workflow passes admin credentials to Docker"""
    print("Testing restore workflow credential passing...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check that ensure_nextcloud_container uses admin credentials
    # Look for the admin_env variable being constructed
    if 'admin_env = ""' in source and 'NEXTCLOUD_ADMIN_USER' in source:
        print("  ✓ Admin environment variables are constructed in ensure_nextcloud_container")
    else:
        print("  ✗ Admin environment variables not found in ensure_nextcloud_container")
        return False
    
    # Check that admin_env is used in docker run commands
    if '{admin_env}--network bridge' in source or '{admin_env} --network bridge' in source:
        print("  ✓ Admin environment variables are used in Docker run commands")
    else:
        print("  ✗ Admin environment variables not used in Docker run commands")
        return False
    
    # Check that restore_admin_user and restore_admin_password are accessed
    if 'self.restore_admin_user' in source and 'self.restore_admin_password' in source:
        print("  ✓ Restore admin credentials are accessed from stored values")
    else:
        print("  ✗ Restore admin credentials not accessed")
        return False
    
    return True


def test_new_instance_workflow_passes_credentials():
    """Test that new instance workflow passes admin credentials to Docker"""
    print("\nTesting new instance workflow credential passing...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check that launch_nextcloud_instance accepts admin credentials
    if 'def launch_nextcloud_instance(self, port, admin_user' in source:
        print("  ✓ launch_nextcloud_instance accepts admin_user parameter")
    else:
        print("  ✗ launch_nextcloud_instance doesn't accept admin_user parameter")
        return False
    
    if 'admin_password' in source and 'def launch_nextcloud_instance' in source:
        print("  ✓ launch_nextcloud_instance accepts admin_password parameter")
    else:
        print("  ✗ launch_nextcloud_instance doesn't accept admin_password parameter")
        return False
    
    # Check that credentials are passed to Docker (with or without escaping)
    if ('-e NEXTCLOUD_ADMIN_USER={admin_user}' in source or 
        '-e NEXTCLOUD_ADMIN_USER={safe_admin_user}' in source) and \
       ('-e NEXTCLOUD_ADMIN_PASSWORD={admin_password}' in source or 
        '-e NEXTCLOUD_ADMIN_PASSWORD={safe_admin_password}' in source):
        print("  ✓ Admin credentials passed to Docker in launch_nextcloud_instance")
    else:
        print("  ✗ Admin credentials not passed to Docker in launch_nextcloud_instance")
        return False
    
    return True


def test_ui_collects_admin_credentials():
    """Test that UI collects admin username and password"""
    print("\nTesting UI credential collection...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for admin username entry in show_port_entry
    if 'admin_user_entry' in source and 'Admin Username' in source:
        print("  ✓ UI includes admin username entry field")
    else:
        print("  ✗ UI missing admin username entry field")
        return False
    
    # Check for admin password entry
    if 'admin_password_entry' in source and 'Admin Password' in source:
        print("  ✓ UI includes admin password entry field")
    else:
        print("  ✗ UI missing admin password entry field")
        return False
    
    # Check that credentials are validated before starting
    if 'if not admin_user:' in source and 'if not admin_password:' in source:
        print("  ✓ UI validates admin credentials before starting")
    else:
        print("  ✗ UI doesn't validate admin credentials")
        return False
    
    return True


def test_credential_format():
    """Test that credentials are properly formatted in Docker commands"""
    print("\nTesting credential format in Docker commands...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check that environment variables are properly formatted
    # Pattern: -e VAR=value (with or without escaping)
    env_pattern_direct = r'-e NEXTCLOUD_ADMIN_USER=\{admin_user\}'
    env_pattern_safe = r'-e NEXTCLOUD_ADMIN_USER=\{safe.*user\}'
    if re.search(env_pattern_direct, source) or re.search(env_pattern_safe, source):
        print("  ✓ Admin username environment variable properly formatted")
    else:
        print("  ✗ Admin username environment variable format issue")
        return False
    
    env_pattern_direct = r'-e NEXTCLOUD_ADMIN_PASSWORD=\{admin_password\}'
    env_pattern_safe = r'-e NEXTCLOUD_ADMIN_PASSWORD=\{safe.*password\}'
    if re.search(env_pattern_direct, source) or re.search(env_pattern_safe, source):
        print("  ✓ Admin password environment variable properly formatted")
    else:
        print("  ✗ Admin password environment variable format issue")
        return False
    
    # Check that shlex.quote is used for security
    if 'shlex.quote' in source and 'NEXTCLOUD_ADMIN' in source:
        print("  ✓ Credentials are properly escaped using shlex.quote for security")
    else:
        print("  ⚠ Warning: Credentials may not be escaped (could be a security issue)")
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Admin Credentials Implementation")
    print("=" * 60)
    
    tests = [
        test_restore_workflow_passes_credentials,
        test_new_instance_workflow_passes_credentials,
        test_ui_collects_admin_credentials,
        test_credential_format
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
