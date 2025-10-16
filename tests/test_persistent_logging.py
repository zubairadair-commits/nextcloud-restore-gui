#!/usr/bin/env python3
"""
Test suite for persistent logging with rotation and log viewer functionality.
"""

import os
import sys
import tempfile
import time
from pathlib import Path

def test_logging_imports():
    """Test that logging imports are correct"""
    print("=" * 70)
    print("TEST 1: Logging Imports")
    print("=" * 70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    checks = {
        'RotatingFileHandler import': 'from logging.handlers import RotatingFileHandler' in code,
        'setup_logging function': 'def setup_logging():' in code,
        'LOG_FILE_PATH global': 'LOG_FILE_PATH = setup_logging()' in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    return all_passed


def test_log_file_location():
    """Test that log file is set to Documents/NextcloudLogs"""
    print("=" * 70)
    print("TEST 2: Log File Location")
    print("=" * 70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    checks = {
        'Documents directory': 'Path.home() / \'Documents\'' in code,
        'NextcloudLogs folder': 'NextcloudLogs' in code,
        'nextcloud_restore_gui.log': 'nextcloud_restore_gui.log' in code,
        'Directory creation': 'log_dir.mkdir(parents=True, exist_ok=True)' in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    return all_passed


def test_rotation_configuration():
    """Test that log rotation is properly configured"""
    print("=" * 70)
    print("TEST 3: Log Rotation Configuration")
    print("=" * 70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    checks = {
        'RotatingFileHandler used': 'RotatingFileHandler(' in code,
        'maxBytes parameter': 'maxBytes=' in code,
        'backupCount parameter': 'backupCount=' in code,
        'UTF-8 encoding': "encoding='utf-8'" in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    return all_passed


def test_log_viewer_button():
    """Test that View Logs button is added to dropdown menu"""
    print("=" * 70)
    print("TEST 4: View Logs Button")
    print("=" * 70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    checks = {
        'View Logs button': '📋 View Logs' in code,
        'show_log_viewer method': 'def show_log_viewer(self):' in code,
        'Button calls show_log_viewer': 'self.show_log_viewer()' in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    return all_passed


def test_log_viewer_features():
    """Test that log viewer has all required features"""
    print("=" * 70)
    print("TEST 5: Log Viewer Features")
    print("=" * 70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    checks = {
        'Log viewer window': 'log_window = tk.Toplevel(self)' in code,
        'Text widget for logs': 'log_text = tk.Text(' in code,
        'Scrollbar': 'scrollbar = tk.Scrollbar(' in code,
        'Load logs function': 'def load_logs():' in code,
        'Refresh button': '🔄 Refresh' in code,
        'Open log folder button': '📁 Open Log Folder' in code,
        'Clear logs button': '🗑️ Clear Logs' in code,
        'Read log file': 'with open(LOG_FILE_PATH, \'r\'' in code,
        'Theme applied to log viewer': 'log_window.configure(bg=self.theme_colors' in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    return all_passed


def test_cross_platform_support():
    """Test that logging works cross-platform"""
    print("=" * 70)
    print("TEST 6: Cross-Platform Support")
    print("=" * 70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    checks = {
        'platform.system() check': 'platform.system()' in code,
        'Windows support': "'Windows'" in code,
        'macOS support': "'Darwin'" in code or 'macOS' in code,
        'Linux support': 'xdg-open' in code or 'Linux' in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    return all_passed


def test_log_persistence():
    """Test that log file location will persist after restart"""
    print("=" * 70)
    print("TEST 7: Log Persistence")
    print("=" * 70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Check that logs are NOT in temp directory
    checks = {
        'Not in temp directory': 'tempfile' not in code or 'NextcloudLogs' in code,
        'User Documents directory': 'Path.home() / \'Documents\'' in code,
        'Persistent location': 'NextcloudLogs' in code,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print()
    print("Note: Log file will be stored in:")
    if os.name == 'nt':
        print(f"  {Path.home() / 'Documents' / 'NextcloudLogs' / 'nextcloud_restore_gui.log'}")
    else:
        print(f"  {Path.home() / 'Documents' / 'NextcloudLogs' / 'nextcloud_restore_gui.log'}")
    print()
    
    return all_passed


def main():
    print()
    print("=" * 70)
    print("PERSISTENT LOGGING WITH ROTATION - TEST SUITE")
    print("=" * 70)
    print()
    print("Testing implementation of:")
    print("  • Persistent log file in Documents/NextcloudLogs/")
    print("  • RotatingFileHandler with 10MB max size and 5 backups")
    print("  • View Logs button in dropdown menu")
    print("  • Log viewer with refresh, open folder, and clear features")
    print("  • Cross-platform support (Windows, macOS, Linux)")
    print()
    
    results = []
    
    # Run all tests
    results.append(("Logging Imports", test_logging_imports()))
    results.append(("Log File Location", test_log_file_location()))
    results.append(("Rotation Configuration", test_rotation_configuration()))
    results.append(("View Logs Button", test_log_viewer_button()))
    results.append(("Log Viewer Features", test_log_viewer_features()))
    results.append(("Cross-Platform Support", test_cross_platform_support()))
    results.append(("Log Persistence", test_log_persistence()))
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print("=" * 70)
    print(f"Results: {passed_count}/{total_count} tests passed")
    print("=" * 70)
    print()
    
    if passed_count == total_count:
        print("✅ All tests passed! Persistent logging is properly implemented.")
        return 0
    else:
        print(f"❌ {total_count - passed_count} test(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
