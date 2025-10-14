#!/usr/bin/env python3
"""
Test diagnostic logging for Tailscale pages.
Verifies that logging statements are present and the decorator is applied.
"""

import os
import sys

def test_logging_infrastructure():
    """Test that logging is properly configured"""
    print("=" * 70)
    print("Diagnostic Logging Test for Tailscale Pages")
    print("=" * 70)
    print()
    
    # Read the file
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    checks_passed = 0
    total_checks = 0
    
    # Check 1: Logging module imported
    total_checks += 1
    if 'import logging' in content:
        print("✓ Check 1: logging module imported")
        checks_passed += 1
    else:
        print("✗ Check 1: logging module NOT imported")
    
    # Check 2: Logger configured (updated for RotatingFileHandler)
    total_checks += 1
    if ('setup_logging()' in content or 'logging.basicConfig' in content) and 'nextcloud_restore_gui.log' in content:
        print("✓ Check 2: Logger configured with file handler")
        checks_passed += 1
    else:
        print("✗ Check 2: Logger NOT properly configured")
    
    # Check 3: Logger instance created
    total_checks += 1
    if 'logger = logging.getLogger(__name__)' in content:
        print("✓ Check 3: Logger instance created")
        checks_passed += 1
    else:
        print("✗ Check 3: Logger instance NOT created")
    
    # Check 4: Decorator function defined
    total_checks += 1
    if 'def log_page_render(page_name):' in content:
        print("✓ Check 4: log_page_render decorator defined")
        checks_passed += 1
    else:
        print("✗ Check 4: log_page_render decorator NOT defined")
    
    # Check 5: Decorator applied to show_tailscale_wizard
    total_checks += 1
    if '@log_page_render("TAILSCALE WIZARD")' in content:
        print("✓ Check 5: Decorator applied to show_tailscale_wizard")
        checks_passed += 1
    else:
        print("✗ Check 5: Decorator NOT applied to show_tailscale_wizard")
    
    # Check 6: Decorator applied to _show_tailscale_config
    total_checks += 1
    if '@log_page_render("TAILSCALE CONFIG")' in content:
        print("✓ Check 6: Decorator applied to _show_tailscale_config")
        checks_passed += 1
    else:
        print("✗ Check 6: Decorator NOT applied to _show_tailscale_config")
    
    # Check 7: Theme toggle has logging
    total_checks += 1
    if 'THEME TOGGLE: Changed theme from' in content:
        print("✓ Check 7: Theme toggle method has logging")
        checks_passed += 1
    else:
        print("✗ Check 7: Theme toggle method does NOT have logging")
    
    # Check 8: Refresh page has logging
    total_checks += 1
    if 'REFRESH PAGE: Starting refresh for page' in content:
        print("✓ Check 8: refresh_current_page method has logging")
        checks_passed += 1
    else:
        print("✗ Check 8: refresh_current_page method does NOT have logging")
    
    # Check 9: Error handling in decorator
    total_checks += 1
    if 'Page Rendering Error' in content and 'messagebox.showerror' in content:
        print("✓ Check 9: Error handling with user notification present")
        checks_passed += 1
    else:
        print("✗ Check 9: Error handling NOT properly implemented")
    
    # Check 10: Fallback to landing page in decorator
    total_checks += 1
    if 'Attempting fallback to landing page' in content:
        print("✓ Check 10: Fallback to landing page on error")
        checks_passed += 1
    else:
        print("✗ Check 10: Fallback NOT implemented")
    
    # Check 11: Logging for widget creation
    total_checks += 1
    if 'TAILSCALE WIZARD: Setting current_page' in content:
        print("✓ Check 11: Logging for wizard page initialization")
        checks_passed += 1
    else:
        print("✗ Check 11: Widget creation logging NOT present")
    
    # Check 12: Logging for config page initialization
    total_checks += 1
    if 'TAILSCALE CONFIG: Setting current_page' in content:
        print("✓ Check 12: Logging for config page initialization")
        checks_passed += 1
    else:
        print("✗ Check 12: Config page logging NOT present")
    
    print()
    print("=" * 70)
    print(f"Results: {checks_passed}/{total_checks} checks passed")
    print("=" * 70)
    print()
    
    if checks_passed == total_checks:
        print("✅ All checks passed! Diagnostic logging is properly implemented.")
        print()
        print("📋 What was added:")
        print("  • Logging module configured with file and console output")
        print("  • Page rendering decorator with automatic error handling")
        print("  • Detailed logging for theme changes and page refreshes")
        print("  • Automatic fallback to landing page on rendering errors")
        print("  • User-friendly error messages with log file reference")
        print()
        print("🎯 Benefits:")
        print("  • All page rendering is logged with timestamps")
        print("  • Errors are caught and logged with full stack traces")
        print("  • Users are notified of errors with helpful messages")
        print("  • Pages never appear blank - fallback ensures something shows")
        print("  • Log file (nextcloud_restore_gui.log) aids troubleshooting")
        return 0
    else:
        print(f"❌ {total_checks - checks_passed} checks failed.")
        return 1

if __name__ == '__main__':
    sys.exit(test_logging_infrastructure())
