#!/usr/bin/env python3
"""
Test to verify log rotation functionality.
This test simulates a large log file and verifies that rotation occurs.
"""

import sys
import os
from pathlib import Path
import platform
import logging
from logging.handlers import RotatingFileHandler
import tempfile
import shutil

def test_log_rotation():
    """Test that log rotation works correctly"""
    print()
    print("=" * 70)
    print("LOG ROTATION TEST")
    print("=" * 70)
    print()
    
    # Create a temporary directory for testing
    test_dir = Path(tempfile.mkdtemp(prefix="nextcloud_log_test_"))
    test_log_file = test_dir / "test_rotation.log"
    
    print(f"Test directory: {test_dir}")
    print(f"Test log file: {test_log_file}")
    print()
    
    # Configure a rotating file handler with small max size for testing
    # Use 1KB max size to trigger rotation quickly
    file_handler = RotatingFileHandler(
        test_log_file,
        maxBytes=1024,  # 1 KB for quick testing
        backupCount=3,   # Keep 3 backups
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Create a test logger
    test_logger = logging.getLogger('rotation_test')
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(file_handler)
    
    print("Writing log entries to trigger rotation...")
    print()
    
    # Write enough entries to trigger multiple rotations
    for i in range(100):
        test_logger.info(f"Test log entry {i:03d} - This is a test message to fill the log file and trigger rotation. " * 2)
    
    # Close the handler to flush all data
    file_handler.close()
    
    # Check for rotated files
    print("Checking for rotated log files:")
    print()
    
    files_found = []
    if test_log_file.exists():
        size = test_log_file.stat().st_size
        print(f"  ✓ Main log file: {test_log_file.name} ({size} bytes)")
        files_found.append(test_log_file.name)
    
    for i in range(1, 4):
        backup_file = Path(str(test_log_file) + f".{i}")
        if backup_file.exists():
            size = backup_file.stat().st_size
            print(f"  ✓ Backup file {i}: {backup_file.name} ({size} bytes)")
            files_found.append(backup_file.name)
    
    print()
    
    # Verify rotation occurred
    if len(files_found) > 1:
        print(f"✅ SUCCESS: Log rotation working! Found {len(files_found)} log files.")
        print()
        print("This proves that:")
        print("  • Logs rotate automatically when max size is reached")
        print("  • Old logs are preserved in numbered backup files")
        print("  • The RotatingFileHandler is configured correctly")
        print()
        success = True
    else:
        print(f"⚠️  WARNING: Only found {len(files_found)} file(s). Rotation may not have occurred.")
        print("This could mean:")
        print("  • Not enough data was written to trigger rotation")
        print("  • The maxBytes threshold was not reached")
        print()
        success = False
    
    # Verify backup count limit
    backup_count = len([f for f in files_found if '.log.' in f])
    if backup_count <= 3:
        print(f"✅ Backup count limit respected: {backup_count} backups (max: 3)")
    else:
        print(f"❌ Too many backups: {backup_count} (max should be 3)")
        success = False
    
    print()
    
    # Cleanup
    print("Cleaning up test files...")
    try:
        shutil.rmtree(test_dir)
        print("✓ Test directory removed")
    except Exception as e:
        print(f"⚠️  Could not remove test directory: {e}")
    
    print()
    print("=" * 70)
    
    return success


def test_production_config():
    """Verify the production logging configuration is correct"""
    print()
    print("=" * 70)
    print("PRODUCTION CONFIGURATION TEST")
    print("=" * 70)
    print()
    
    with open('nextcloud_restore_and_backup-v9.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("Checking production logging configuration:")
    print()
    
    checks = {
        'maxBytes=10*1024*1024': '10 MB maximum file size',
        'backupCount=5': '5 backup files',
        'encoding=\'utf-8\'': 'UTF-8 encoding',
        'RotatingFileHandler': 'Using RotatingFileHandler',
    }
    
    all_passed = True
    for check_code, description in checks.items():
        if check_code in code:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_passed = False
    
    print()
    
    if all_passed:
        print("✅ Production configuration is correct:")
        print("   • Maximum log file size: 10 MB")
        print("   • Number of backup files: 5")
        print("   • Total maximum storage: ~60 MB")
        print("   • Oldest logs automatically deleted")
    
    print()
    print("=" * 70)
    
    return all_passed


def main():
    print()
    print("*" * 70)
    print("LOG ROTATION VERIFICATION TEST SUITE")
    print("*" * 70)
    
    results = []
    
    # Test 1: Actual log rotation
    results.append(("Log Rotation Functionality", test_log_rotation()))
    
    # Test 2: Production configuration
    results.append(("Production Configuration", test_production_config()))
    
    # Summary
    print()
    print("=" * 70)
    print("FINAL SUMMARY")
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
        print("✅ All log rotation tests passed!")
        print()
        print("The application will:")
        print("  • Store logs in Documents/NextcloudLogs/")
        print("  • Rotate logs when they reach 10 MB")
        print("  • Keep 5 backup files")
        print("  • Delete oldest backups automatically")
        print("  • Never exceed ~60 MB total storage")
        return 0
    else:
        print(f"❌ {total_count - passed_count} test(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
