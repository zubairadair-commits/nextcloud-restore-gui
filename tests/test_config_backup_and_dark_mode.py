#!/usr/bin/env python3
"""
Test script to verify:
1. Test Run button backs up only the config file (not a full backup)
2. Config backup is immediately deleted after test
3. App starts in dark mode by default
"""

import sys
import os


def test_run_test_backup_uses_config_file():
    """Test that run_test_backup function backs up only the config file."""
    print("=" * 70)
    print("TEST 1: Test Run Backs Up Only Config File")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the run_test_backup function
    func_start = content.find('def run_test_backup(')
    assert func_start != -1, "run_test_backup function should exist"
    
    func_end = content.find('\ndef ', func_start + 100)
    func_content = content[func_start:func_end]
    
    # Check that it backs up the config file
    assert 'get_schedule_config_path()' in func_content, \
        "Should call get_schedule_config_path() to get config file"
    
    assert 'schedule_config.json' in func_content, \
        "Should reference schedule_config.json"
    
    # Check it's not creating a test.txt file anymore
    assert 'test.txt' not in func_content or 'arcname=\'schedule_config.json\'' in func_content, \
        "Should backup config file, not test.txt"
    
    # Check it adds the config file to tar
    assert 'tar.add(config_path' in func_content, \
        "Should add config_path to tar archive"
    
    print("  ✓ run_test_backup uses get_schedule_config_path()")
    print("  ✓ Backs up schedule_config.json")
    print("  ✓ Archives the actual config file")
    print()
    return True


def test_backup_immediately_deleted():
    """Test that the config backup is immediately deleted after test."""
    print("=" * 70)
    print("TEST 2: Config Backup Immediately Deleted")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the run_test_backup function
    func_start = content.find('def run_test_backup(')
    func_end = content.find('\ndef ', func_start + 100)
    func_content = content[func_start:func_end]
    
    # Check for cleanup code
    assert 'os.remove(test_backup_path)' in func_content, \
        "Should delete test backup using os.remove()"
    
    # Check the order: backup is created, then deleted
    backup_creation = func_content.find('tarfile.open(test_backup_path')
    backup_deletion = func_content.find('os.remove(test_backup_path)')
    
    assert backup_creation < backup_deletion, \
        "Backup deletion should come after backup creation"
    
    # Check for logging about deletion
    assert 'deleted' in func_content.lower() or 'cleanup' in func_content.lower(), \
        "Should log about deletion/cleanup"
    
    print("  ✓ Backup file is deleted with os.remove()")
    print("  ✓ Deletion happens after backup creation")
    print("  ✓ Deletion is logged")
    print()
    return True


def test_dark_mode_default():
    """Test that the app starts in dark mode by default."""
    print("=" * 70)
    print("TEST 3: App Starts in Dark Mode by Default")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find where current_theme is initialized
    # Look for the __init__ method of the main app class
    init_start = content.find('def __init__(self, master):')
    if init_start == -1:
        # Try alternative patterns
        init_start = content.find('self.current_theme = ')
    
    assert init_start != -1, "Should initialize current_theme"
    
    # Get a section around the initialization
    init_section = content[init_start:init_start + 2000]
    
    # Check for dark mode default
    assert "self.current_theme = 'dark'" in init_section, \
        "Should initialize current_theme to 'dark'"
    
    # Make sure it's not set to 'light'
    # (unless there's a conditional or it's changed to dark)
    light_init = init_section.find("self.current_theme = 'light'")
    dark_init = init_section.find("self.current_theme = 'dark'")
    
    if light_init != -1 and dark_init != -1:
        # Both exist, dark should come after light (overriding it)
        assert dark_init > light_init, \
            "If both exist, 'dark' should come after 'light' to override"
    elif light_init == -1:
        # Only dark exists, which is correct
        assert dark_init != -1, "Should have dark theme initialization"
    
    print("  ✓ current_theme is set to 'dark'")
    print("  ✓ App starts in dark mode by default")
    print("  ✓ Users can still toggle to light mode")
    print()
    return True


def test_theme_toggle_still_works():
    """Test that theme toggle functionality is preserved."""
    print("=" * 70)
    print("TEST 4: Theme Toggle Still Works")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for toggle_theme method
    assert 'def toggle_theme(self):' in content, \
        "Should have toggle_theme method"
    
    # Find toggle_theme method
    toggle_start = content.find('def toggle_theme(self):')
    toggle_end = content.find('\n    def ', toggle_start + 100)
    toggle_content = content[toggle_start:toggle_end]
    
    # Check it toggles between light and dark
    assert "'dark'" in toggle_content and "'light'" in toggle_content, \
        "Should toggle between 'dark' and 'light'"
    
    # Check for theme button in UI
    assert '🌙' in content or '☀️' in content, \
        "Should have theme toggle button with sun/moon emoji"
    
    print("  ✓ toggle_theme method exists")
    print("  ✓ Toggles between dark and light themes")
    print("  ✓ Theme toggle button present in UI")
    print()
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("CONFIG BACKUP AND DARK MODE TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_run_test_backup_uses_config_file,
        test_backup_immediately_deleted,
        test_dark_mode_default,
        test_theme_toggle_still_works,
    ]
    
    try:
        for test in tests:
            if not test():
                print(f"\n✗ Test failed: {test.__name__}")
                return 1
        
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Tests passed: {len(tests)}/{len(tests)}")
        print(f"Tests failed: 0/{len(tests)}")
        print()
        print("✅ All tests passed!")
        print()
        print("Changes Verified:")
        print("  1. ✓ Test Run backs up only the config file")
        print("  2. ✓ Config backup is immediately deleted")
        print("  3. ✓ App starts in dark mode by default")
        print("  4. ✓ Users can still toggle to light mode")
        print()
        return 0
    
    except AssertionError as e:
        print(f"\n✗ Assertion failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
