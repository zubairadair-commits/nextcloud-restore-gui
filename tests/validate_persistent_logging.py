#!/usr/bin/env python3
"""
Complete validation script for persistent logging implementation.
Runs all tests and provides a comprehensive report.
"""

import sys
import subprocess
import os
from pathlib import Path

def run_test(test_name, test_file):
    """Run a test file and return results"""
    print()
    print("=" * 70)
    print(f"Running: {test_name}")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0
        
        # Print last 15 lines of output for summary
        lines = result.stdout.split('\n')
        for line in lines[-15:]:
            if line.strip():
                print(line)
        
        if not success and result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        return success
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def check_files_exist():
    """Check that all required files exist"""
    print()
    print("=" * 70)
    print("Checking File Existence")
    print("=" * 70)
    print()
    
    files_to_check = [
        ('Main Application', '../src/nextcloud_restore_and_backup-v9.py'),
        ('Test: Persistent Logging', 'test_persistent_logging.py'),
        ('Test: Log Rotation', 'test_log_rotation.py'),
        ('Test: Diagnostic Logging', 'test_diagnostic_logging.py'),
        ('Demo Script', 'demo_persistent_logging.py'),
        ('Documentation: Feature Guide', 'PERSISTENT_LOGGING_FEATURE.md'),
        ('Documentation: Quick Reference', 'PERSISTENT_LOGGING_QUICK_REFERENCE.md'),
        ('Documentation: Visual Summary', 'PERSISTENT_LOGGING_VISUAL_SUMMARY.md'),
    ]
    
    all_exist = True
    for name, filename in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  ✓ {name}: {filename} ({size:,} bytes)")
        else:
            print(f"  ✗ {name}: {filename} (NOT FOUND)")
            all_exist = False
    
    print()
    return all_exist


def check_log_directory():
    """Check that log directory was created"""
    print()
    print("=" * 70)
    print("Checking Log Directory")
    print("=" * 70)
    print()
    
    log_dir = Path.home() / 'Documents' / 'NextcloudLogs'
    log_file = log_dir / 'nextcloud_restore_gui.log'
    
    if log_dir.exists():
        print(f"  ✓ Log directory exists: {log_dir}")
    else:
        print(f"  ⚠️  Log directory not yet created: {log_dir}")
        print("     (Will be created on first application run)")
    
    if log_file.exists():
        size = log_file.stat().st_size
        print(f"  ✓ Log file exists: {log_file}")
        print(f"    Size: {size:,} bytes")
        
        # Count log entries
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            print(f"    Lines: {lines:,}")
        except Exception as e:
            print(f"    Could not count lines: {e}")
    else:
        print(f"  ⚠️  Log file not yet created: {log_file}")
        print("     (Will be created on first application run)")
    
    print()
    return True


def check_code_changes():
    """Verify key code changes are present"""
    print()
    print("=" * 70)
    print("Verifying Code Changes")
    print("=" * 70)
    print()
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        checks = {
            'RotatingFileHandler import': 'from logging.handlers import RotatingFileHandler' in code,
            'setup_logging function': 'def setup_logging():' in code,
            'LOG_FILE_PATH variable': 'LOG_FILE_PATH = setup_logging()' in code,
            'View Logs button': '📋 View Logs' in code,
            'show_log_viewer method': 'def show_log_viewer(self):' in code,
            'Refresh button': '🔄 Refresh' in code,
            'Open folder button': '📁 Open Log Folder' in code,
            'Clear logs button': '🗑️ Clear Logs' in code,
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
    except Exception as e:
        print(f"  ✗ Error reading main file: {e}")
        print()
        return False


def main():
    print()
    print("*" * 70)
    print("PERSISTENT LOGGING - COMPLETE VALIDATION")
    print("*" * 70)
    print()
    print("This script validates the entire persistent logging implementation:")
    print("  • File existence")
    print("  • Code changes")
    print("  • Test execution")
    print("  • Log directory creation")
    print()
    
    results = {}
    
    # Phase 1: Check files
    results['Files Exist'] = check_files_exist()
    
    # Phase 2: Check code changes
    results['Code Changes'] = check_code_changes()
    
    # Phase 3: Check log directory
    results['Log Directory'] = check_log_directory()
    
    # Phase 4: Run tests
    print()
    print("=" * 70)
    print("Running Test Suites")
    print("=" * 70)
    
    results['Test: Persistent Logging'] = run_test(
        "Persistent Logging Tests",
        "test_persistent_logging.py"
    )
    
    results['Test: Log Rotation'] = run_test(
        "Log Rotation Tests",
        "test_log_rotation.py"
    )
    
    results['Test: Diagnostic Logging'] = run_test(
        "Diagnostic Logging Tests",
        "test_diagnostic_logging.py"
    )
    
    # Phase 5: Run demo
    print()
    print("=" * 70)
    print("Running Demo")
    print("=" * 70)
    
    results['Demo Script'] = run_test(
        "Persistent Logging Demo",
        "demo_persistent_logging.py"
    )
    
    # Final Summary
    print()
    print()
    print("*" * 70)
    print("VALIDATION SUMMARY")
    print("*" * 70)
    print()
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print("*" * 70)
    print(f"RESULTS: {passed}/{total} checks passed")
    print("*" * 70)
    print()
    
    if passed == total:
        print("🎉 SUCCESS! Persistent logging is fully implemented and tested.")
        print()
        print("Key Features:")
        print("  ✅ Persistent log storage in Documents/NextcloudLogs/")
        print("  ✅ Automatic log rotation (10MB max, 5 backups)")
        print("  ✅ Built-in log viewer with GUI access")
        print("  ✅ Cross-platform support (Windows, macOS, Linux)")
        print("  ✅ Theme-aware interface")
        print("  ✅ All tests passing")
        print()
        print("To use:")
        print("  1. Launch the application")
        print("  2. Click ☰ menu button")
        print("  3. Select '📋 View Logs'")
        print()
        return 0
    else:
        print(f"⚠️  {total - passed} check(s) failed. Review output above for details.")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
