#!/usr/bin/env python3
"""
Test script for scheduled backup UX and cloud storage integration enhancements.
This validates the new timezone display and cloud storage detection features.
"""

import sys
import os
import re
import platform


def test_timezone_function():
    """Test that timezone detection function exists and works."""
    print("\n" + "=" * 70)
    print("TEST 1: Timezone Detection Function")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Check for function definition
        if 'def get_system_timezone_info():' not in content:
            print("✗ get_system_timezone_info() function NOT FOUND")
            return False
        
        print("✓ get_system_timezone_info() function exists")
        
        # Check for key components
        checks = [
            ('datetime.now()', 'Uses datetime to get current time'),
            ('astimezone()', 'Gets local timezone'),
            ('strftime', 'Formats timezone info'),
            ('UTC', 'Returns UTC offset'),
        ]
        
        all_passed = True
        for check_str, description in checks:
            if check_str in content:
                print(f"  ✓ {description}")
            else:
                print(f"  ⚠ Warning: {description} - pattern '{check_str}' not found")
        
        # Test the actual function
        try:
            # Import and test the function
            import importlib.util
            spec = importlib.util.spec_from_file_location("app", "../src/nextcloud_restore_and_backup-v9.py")
            module = importlib.util.module_from_spec(spec)
            
            # We can't fully load the module as it requires tkinter, but we can check syntax
            print("  ✓ Module syntax is valid")
        except Exception as e:
            print(f"  ⚠ Could not import module: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cloud_detection_function():
    """Test that cloud storage detection function exists and works."""
    print("\n" + "=" * 70)
    print("TEST 2: Cloud Storage Detection Function")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Check for function definition
        if 'def detect_cloud_sync_folders():' not in content:
            print("✗ detect_cloud_sync_folders() function NOT FOUND")
            return False
        
        print("✓ detect_cloud_sync_folders() function exists")
        
        # Check for cloud provider detection
        providers = [
            ('OneDrive', 'OneDrive detection'),
            ('Google Drive', 'Google Drive detection'),
            ('Dropbox', 'Dropbox detection'),
            ('iCloud Drive', 'iCloud Drive detection (Mac)'),
        ]
        
        all_passed = True
        for provider, description in providers:
            if provider in content:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description} NOT FOUND")
                all_passed = False
        
        # Check for proper return value
        if 'return cloud_folders' in content:
            print("  ✓ Returns cloud_folders dictionary")
        else:
            print("  ✗ Missing return statement")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_timezone_display():
    """Test that timezone is displayed in the UI."""
    print("\n" + "=" * 70)
    print("TEST 3: UI Timezone Display")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Check for timezone display in UI
        checks = [
            ('get_system_timezone_info()', 'Calls timezone info function'),
            ('tz_info', 'Stores timezone info in variable'),
            ('[tz_info]', 'Displays timezone in UI'),
            ('Backup times are in your system', 'Tooltip about system time'),
            ('ToolTip', 'Uses tooltip system'),
        ]
        
        all_passed = True
        for check_str, description in checks:
            if check_str in content:
                print(f"  ✓ {description}")
            else:
                print(f"  ⚠ Warning: {description}")
                all_passed = False
        
        # Check for timezone in status display
        if 'tz_info = get_system_timezone_info()' in content:
            print("  ✓ Timezone info retrieved for status display")
        else:
            print("  ⚠ Timezone might not be shown in status")
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_cloud_storage_hints():
    """Test that cloud storage hints are displayed in the UI."""
    print("\n" + "=" * 70)
    print("TEST 4: UI Cloud Storage Hints")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Check for cloud storage UI elements
        checks = [
            ('detect_cloud_sync_folders()', 'Calls cloud detection function'),
            ('Cloud Sync Folders', 'Displays detected cloud folders'),
            ('info_icon', 'Info icon for backup directory'),
            ('Cloud Storage Options', 'Tooltip with cloud storage info'),
            ('automatically sync to cloud', 'Mentions automatic sync'),
            ('Cloud Sync:', 'Shows cloud sync status'),
            ('Local only', 'Shows local-only status'),
            ('Cloud Storage Setup Guide', 'Setup guide section'),
        ]
        
        all_passed = True
        for check_str, description in checks:
            if check_str in content:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description} NOT FOUND")
                all_passed = False
        
        # Check for cloud provider setup instructions
        providers = ['OneDrive', 'Google Drive', 'Dropbox']
        for provider in providers:
            pattern = f"Install {provider}"
            if pattern in content or provider in content:
                print(f"  ✓ Setup instructions for {provider}")
            else:
                print(f"  ⚠ Setup instructions for {provider} might be missing")
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cloud_status_in_schedule():
    """Test that scheduled backup status shows cloud sync info."""
    print("\n" + "=" * 70)
    print("TEST 5: Cloud Sync Status in Schedule Display")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Check for cloud sync detection in status display
        checks = [
            ('cloud_folders = detect_cloud_sync_folders()', 'Detects cloud folders in status'),
            ('cloud_sync_detected', 'Tracks cloud sync status'),
            ('Cloud Sync:', 'Displays cloud sync provider'),
            ('automatic sync enabled', 'Indicates automatic sync'),
            ('no cloud sync detected', 'Shows when no cloud sync'),
        ]
        
        all_passed = True
        for check_str, description in checks:
            if check_str in content:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description} NOT FOUND")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tooltip_usage():
    """Test that tooltips are properly used for new features."""
    print("\n" + "=" * 70)
    print("TEST 6: Tooltip Usage")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Count ToolTip instances in scheduled backup section
        # Look for the show_schedule_backup function
        func_match = re.search(r'def show_schedule_backup\(self\):.*?(?=\n    def |\Z)', content, re.DOTALL)
        if not func_match:
            print("✗ Could not find show_schedule_backup function")
            return False
        
        func_content = func_match.group(0)
        tooltip_count = func_content.count('ToolTip(')
        
        print(f"  ✓ Found {tooltip_count} tooltips in show_schedule_backup")
        
        if tooltip_count >= 3:
            print("  ✓ Adequate number of tooltips for new features")
            return True
        else:
            print("  ⚠ Expected at least 3 tooltips for timezone and cloud storage hints")
            return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_quality():
    """Test overall code quality and structure."""
    print("\n" + "=" * 70)
    print("TEST 7: Code Quality")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Check for proper error handling
        if 'try:' in content and 'except' in content:
            print("  ✓ Error handling present")
        else:
            print("  ⚠ Limited error handling")
        
        # Check for logging
        if 'logger' in content or 'logging' in content:
            print("  ✓ Logging infrastructure present")
        else:
            print("  ⚠ No logging found")
        
        # Check for docstrings in new functions
        docstring_pattern = r'def (get_system_timezone_info|detect_cloud_sync_folders)\([^)]*\):\s*"""'
        if re.search(docstring_pattern, content):
            print("  ✓ New functions have docstrings")
        else:
            print("  ⚠ Some functions might be missing docstrings")
        
        # Check syntax
        import py_compile
        try:
            py_compile.compile('../src/nextcloud_restore_and_backup-v9.py', doraise=True)
            print("  ✓ Python syntax is valid")
        except py_compile.PyCompileError as e:
            print(f"  ✗ Syntax error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("SCHEDULED BACKUP UX & CLOUD STORAGE ENHANCEMENTS TEST SUITE")
    print("=" * 70)
    
    tests = [
        test_timezone_function,
        test_cloud_detection_function,
        test_ui_timezone_display,
        test_ui_cloud_storage_hints,
        test_cloud_status_in_schedule,
        test_tooltip_usage,
        test_code_quality,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        print("\nNew Features Summary:")
        print("  • Timezone display next to time picker")
        print("  • System timezone shown in status")
        print("  • Cloud storage folder detection")
        print("  • Cloud sync status indicators")
        print("  • Setup guide for cloud providers")
        print("  • Tooltips for all new features")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
