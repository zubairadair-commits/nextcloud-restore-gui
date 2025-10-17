#!/usr/bin/env python3
"""
Test script for Remote Access refactoring and improvements.
This script validates:
1. UI references changed from 'Tailscale' to 'Remote Access'
2. Improved responsiveness with wraplength
3. Enhanced cross-platform Tailscale detection
4. Automatic tailscale serve functionality
"""

import sys
import os
import re

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ui_refactoring():
    """Test that UI has been refactored to use 'Remote Access' instead of just 'Tailscale'"""
    print("=" * 70)
    print("Remote Access UI Refactoring Test")
    print("=" * 70)
    print()
    
    # Check if main file exists
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    print(f"✓ Main file found: {main_file}")
    
    # Read and check for key UI changes
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Check for updated menu text
    checks = [
        ("🌐 Remote Access\"", "Menu button updated to 'Remote Access'"),
        ("Remote Access Setup\"", "Page title updated to 'Remote Access Setup'"),
        ("← Back to Remote Access Setup", "Back button updated"),
        ("wraplength=520", "Text wrapping implemented for responsiveness"),
    ]
    
    for check_str, description in checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    return all_passed

def test_detection_improvements():
    """Test that enhanced cross-platform detection is implemented"""
    print("=" * 70)
    print("Tailscale Detection Improvements Test")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Check for enhanced detection methods
    checks = [
        ("def _check_tailscale_running", "Enhanced running check method exists"),
        ("sc', 'query', 'Tailscale'", "Windows service check implemented"),
        ("tasklist.*tailscaled.exe", "Windows process check implemented"),
        ("systemctl.*is-active.*tailscaled", "Linux systemd check implemented"),
        ("pgrep.*tailscaled", "Unix process check implemented"),
        ("Method 1:", "Multi-method detection approach"),
        ("Method 2:", "Fallback detection methods"),
    ]
    
    for check_str, description in checks:
        if re.search(check_str, content):
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    return all_passed

def test_auto_serve_functionality():
    """Test that automatic tailscale serve functionality is implemented"""
    print("=" * 70)
    print("Automatic Tailscale Serve Test")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Check for auto-serve implementation
    checks = [
        ("def get_nextcloud_port", "Port detection function exists"),
        ("def setup_tailscale_serve_startup", "Auto-serve setup function exists"),
        ("def _setup_windows_task_scheduler", "Windows Task Scheduler integration"),
        ("def _setup_linux_systemd_service", "Linux systemd service integration"),
        ("def _setup_macos_launchagent", "macOS LaunchAgent integration"),
        ("auto_serve_var", "Auto-serve checkbox variable"),
        ("port_override_var", "Port override entry variable"),
        ("enable_auto_serve", "Auto-serve parameter in apply config"),
        ("setup_tailscale_serve_startup", "Auto-serve setup called in config"),
    ]
    
    for check_str, description in checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for platform-specific implementations
    print()
    print("Platform-specific implementations:")
    
    platform_checks = [
        ("Register-ScheduledTask", "Windows scheduled task creation"),
        ("/etc/systemd/system/", "Linux systemd service path"),
        ("Library/LaunchAgents/", "macOS LaunchAgent path"),
        ("tailscale serve --bg --https=443", "Tailscale serve command format"),
    ]
    
    for check_str, description in platform_checks:
        if check_str in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    return all_passed

def test_ui_responsiveness():
    """Test that UI elements have proper wrapping and spacing"""
    print("=" * 70)
    print("UI Responsiveness Test")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Count wraplength usages (should be more than before)
    wraplength_count = content.count("wraplength=")
    if wraplength_count >= 5:
        print(f"✓ Text wrapping implemented ({wraplength_count} instances found)")
    else:
        print(f"✗ Insufficient text wrapping ({wraplength_count} instances)")
        all_passed = False
    
    # Check for proper padding
    padding_patterns = [
        "pady=",
        "padx=",
    ]
    
    for pattern in padding_patterns:
        count = content.count(pattern)
        if count > 0:
            print(f"✓ Padding implemented: {pattern} ({count} instances)")
        else:
            print(f"✗ Padding missing: {pattern}")
            all_passed = False
    
    print()
    return all_passed

def test_integration():
    """Test that all components are properly integrated"""
    print("=" * 70)
    print("Integration Test")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    # Try to import/compile the module
    try:
        import py_compile
        py_compile.compile(main_file, doraise=True)
        print("✓ Python syntax is valid (compiles successfully)")
    except Exception as e:
        print(f"✗ Python syntax error: {e}")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Check that all new functions are called
    integration_checks = [
        ("get_nextcloud_port()", "Port detection is called"),
        ("setup_tailscale_serve_startup", "Auto-serve setup is called"),
        ("_check_tailscale_running()", "Enhanced detection is used"),
    ]
    
    for check_str, description in integration_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    return all_passed

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Remote Access Refactoring - Comprehensive Test Suite".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    tests = [
        ("UI Refactoring", test_ui_refactoring),
        ("Detection Improvements", test_detection_improvements),
        ("Auto-Serve Functionality", test_auto_serve_functionality),
        ("UI Responsiveness", test_ui_responsiveness),
        ("Integration", test_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 All tests passed! Remote Access refactoring is complete.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
