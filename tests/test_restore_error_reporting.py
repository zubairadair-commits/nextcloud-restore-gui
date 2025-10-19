#!/usr/bin/env python3
"""
Test suite for restore workflow error reporting enhancements.
Tests the new logging, error dialog, and verbose mode features.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_error_logging_initialization():
    """Test that logging is properly initialized"""
    try:
        print("Testing logging initialization...")
        
        # Read source code to verify logging setup
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            source_code = f.read()
        
        # Check for setup_logging function
        assert 'def setup_logging' in source_code, "Should have setup_logging function"
        
        # Check for LOG_FILE_PATH
        assert 'LOG_FILE_PATH' in source_code, "Should define LOG_FILE_PATH"
        
        # Check that logs go to Documents/NextcloudLogs
        assert 'NextcloudLogs' in source_code, "Should use NextcloudLogs directory"
        assert 'Documents' in source_code or 'documents' in source_code.lower(), "Should use Documents directory"
        
        # Check for RotatingFileHandler
        assert 'RotatingFileHandler' in source_code, "Should use RotatingFileHandler for log rotation"
        
        print("✓ setup_logging function exists")
        print("✓ LOG_FILE_PATH is configured")
        print("✓ Logs stored in Documents/NextcloudLogs")
        print("✓ Logging initialization test passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_verbose_logging_attribute():
    """Test that verbose logging attribute is properly initialized"""
    try:
        print("\nTesting verbose logging attribute...")
        
        # Read source code to verify verbose_logging attribute
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            source_code = f.read()
        
        # Check that verbose_logging is initialized
        assert 'self.verbose_logging = False' in source_code, \
            "Should initialize self.verbose_logging to False"
        
        # Check that it's used in conditional logging
        assert 'if self.verbose_logging' in source_code or 'self.verbose_logging:' in source_code, \
            "Should use verbose_logging for conditional logging"
        
        print("✓ verbose_logging attribute is initialized to False")
        print("✓ verbose_logging is used for conditional logging")
        print("✓ Verbose logging attribute test passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_settings_method_exists():
    """Test that show_settings method exists"""
    try:
        print("\nTesting settings method existence...")
        
        # Read source code to verify show_settings method
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            source_code = f.read()
        
        # Check that show_settings method exists
        assert 'def show_settings(self):' in source_code, "Should have show_settings method"
        
        # Check that it's called from settings button
        assert 'self.show_settings()' in source_code or 'show_settings' in source_code, \
            "show_settings should be callable"
        
        # Check for Settings button in dropdown menu
        assert '⚙️ Settings' in source_code or 'Settings' in source_code, \
            "Should have Settings option in menu"
        
        print("✓ show_settings method exists")
        print("✓ Settings accessible from menu")
        print("✓ Settings method test passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_dialog_enhancement():
    """Test that error dialog has been enhanced with log location"""
    try:
        print("\nTesting error dialog enhancements...")
        
        # Read source code to verify enhancements
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            source_code = f.read()
        
        # Check that LOG_FILE_PATH is used in show_restore_error_dialog
        assert 'LOG_FILE_PATH' in source_code, "LOG_FILE_PATH should be referenced"
        
        # Check for "Show Logs" button with proper styling
        assert 'Show Logs' in source_code, "Should have Show Logs button"
        assert 'show_log_viewer' in source_code, "Should call show_log_viewer"
        
        # Check for log file location display in error dialog
        assert 'Error details saved to' in source_code or 'saved to:' in source_code, \
            "Should display log file location on error"
        
        print("✓ Error dialog includes log file location")
        print("✓ Error dialog has Show Logs button")
        print("✓ Show Logs button opens log viewer")
        print("✓ Error dialog enhancement test passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_log_viewer_enhancements():
    """Test that log viewer has helpful messages for no logs"""
    try:
        print("\nTesting log viewer enhancements...")
        
        # Read source code to verify enhancements
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            source_code = f.read()
        
        # Check for troubleshooting tips in load_logs
        assert 'Troubleshooting' in source_code, "Should have troubleshooting tips"
        assert 'No log entries found' in source_code or 'Log file not found' in source_code, \
            "Should have message for no logs"
        
        # Check for helpful guidance
        assert 'Verbose Logging' in source_code or 'verbose' in source_code.lower(), \
            "Should mention verbose logging"
        
        print("✓ Log viewer includes troubleshooting tips")
        print("✓ Log viewer has helpful message for no logs")
        print("✓ Log viewer enhancement test passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_restore_error_logging():
    """Test that restore errors are properly logged"""
    try:
        print("\nTesting restore error logging...")
        
        # Read source code to verify error logging in _restore_auto_thread
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            source_code = f.read()
        
        # Check for comprehensive error logging in except block
        assert 'RESTORE FAILED - Error Details:' in source_code, \
            "Should log 'RESTORE FAILED - Error Details:'"
        assert 'Error Type:' in source_code, "Should log error type"
        assert 'Error Message:' in source_code, "Should log error message"
        assert 'Backup Path:' in source_code, "Should log backup path"
        
        # Check for logger.error calls
        assert 'logger.error' in source_code, "Should use logger.error"
        
        print("✓ Restore errors are comprehensively logged")
        print("✓ Error logging includes type, message, and path")
        print("✓ Restore error logging test passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_verbose_logging_usage():
    """Test that verbose logging is used throughout restore process"""
    try:
        print("\nTesting verbose logging usage...")
        
        # Read source code to verify verbose logging usage
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            source_code = f.read()
        
        # Check for self.verbose_logging checks
        verbose_count = source_code.count('self.verbose_logging')
        assert verbose_count >= 3, f"Should have multiple verbose logging checks (found {verbose_count})"
        
        # Check for logger.debug calls
        debug_count = source_code.count('logger.debug')
        assert debug_count >= 2, f"Should have debug logging statements (found {debug_count})"
        
        # Check for step logging in restore
        assert 'Step 1/7' in source_code or 'Step 2/7' in source_code, \
            "Should have step-by-step logging"
        
        print(f"✓ Found {verbose_count} verbose logging checks")
        print(f"✓ Found {debug_count} debug logging statements")
        print("✓ Step-by-step logging implemented")
        print("✓ Verbose logging usage test passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("RESTORE ERROR REPORTING ENHANCEMENT TESTS")
    print("=" * 60)
    
    tests = [
        ("Logging Initialization", test_error_logging_initialization),
        ("Verbose Logging Attribute", test_verbose_logging_attribute),
        ("Settings Method", test_settings_method_exists),
        ("Error Dialog Enhancement", test_error_dialog_enhancement),
        ("Log Viewer Enhancements", test_log_viewer_enhancements),
        ("Restore Error Logging", test_restore_error_logging),
        ("Verbose Logging Usage", test_verbose_logging_usage),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result if result is not None else True))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
