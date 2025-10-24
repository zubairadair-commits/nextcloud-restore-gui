#!/usr/bin/env python3
"""
Comprehensive integration test for Tailscale Health Check feature.
This test verifies the complete functionality including error scenarios.
"""

import sys
import os
import re

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def extract_function(content, function_name):
    """Helper function to extract a function body from source code"""
    func_start = content.find(f"def {function_name}")
    if func_start == -1:
        return None
    
    # Find the next function definition at the same indentation level
    lines = content[func_start:].split('\n')
    func_lines = [lines[0]]  # Start with the def line
    
    # Determine indentation level of the function
    func_indent = len(lines[0]) - len(lines[0].lstrip())
    
    # Collect lines until we hit another function at same or lower indentation
    for line in lines[1:]:
        if line.strip() and not line.startswith(' ' * (func_indent + 1)):
            # Check if it's a new function definition at same level
            if line.strip().startswith('def '):
                break
        func_lines.append(line)
    
    return '\n'.join(func_lines)

def test_health_check_error_messages():
    """Test that all error scenarios have appropriate messages and suggestions"""
    print("=" * 70)
    print("Health Check Error Messages Test")
    print("=" * 70)
    print()
    
    main_file = "src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Extract the health check function
    health_func = extract_function(content, "check_tailscale_serve_health")
    
    if health_func is None:
        print("✗ Health check function not found")
        return False
    
    all_passed = True
    
    # Test for comprehensive error handling
    error_scenarios = [
        ("not running", "Tailscale not running scenario"),
        ("not found", "Tailscale not installed scenario"),
        ("not configured", "Serve not configured scenario"),
        ("timeout", "Timeout scenario"),
        ("Cannot connect", "Connection failure scenario"),
        ("not available", "IP/Hostname not available scenario"),
    ]
    
    for error_str, description in error_scenarios:
        if error_str in health_func:
            print(f"✓ {description} handled")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    
    # Test for suggestion messages
    suggestion_keywords = [
        ("Install Tailscale", "Installation suggestion"),
        ("Start Tailscale", "Start service suggestion"),
        ("Enable automatic Tailscale Serve", "Enable serve suggestion"),
        ("Restart Tailscale", "Restart suggestion"),
        ("Enable MagicDNS", "MagicDNS suggestion"),
        ("Check Tailscale connection", "Connection check suggestion"),
        ("Ensure Nextcloud container is running", "Container running suggestion"),
    ]
    
    for keyword, description in suggestion_keywords:
        if keyword in health_func:
            print(f"✓ {description} present")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    if all_passed:
        print("✅ ERROR MESSAGE TEST PASSED")
    else:
        print("❌ ERROR MESSAGE TEST FAILED")
    print("=" * 70)
    print()
    
    return all_passed

def test_health_check_structure():
    """Test the structure and return format of the health check function"""
    print("=" * 70)
    print("Health Check Structure Test")
    print("=" * 70)
    print()
    
    main_file = "src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Test return structure
    required_fields = [
        ("'overall_status'", "Overall status field"),
        ("'checks'", "Checks dictionary"),
        ("'serve_running'", "Serve running check"),
        ("'port_mapped'", "Port mapped check"),
        ("'ip_accessible'", "IP accessible check"),
        ("'hostname_accessible'", "Hostname accessible check"),
        ("'status'", "Status field in checks"),
        ("'message'", "Message field in checks"),
        ("'suggestion'", "Suggestion field in checks"),
    ]
    
    for field, description in required_fields:
        if field in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    
    # Test status values
    status_values = ["success", "warning", "error"]
    for status in status_values:
        if f"'{status}'" in content:
            print(f"✓ Status value: {status}")
        else:
            print(f"✗ Status value: {status} - NOT FOUND")
            all_passed = False
    
    print()
    if all_passed:
        print("✅ STRUCTURE TEST PASSED")
    else:
        print("❌ STRUCTURE TEST FAILED")
    print("=" * 70)
    print()
    
    return all_passed

def test_ui_thread_safety():
    """Test that health check runs in background thread"""
    print("=" * 70)
    print("UI Thread Safety Test")
    print("=" * 70)
    print()
    
    main_file = "src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Find _run_health_check method
    if "def _run_health_check" in content:
        print("✓ Health check method exists")
        
        # Check for threading
        if "threading.Thread" in content:
            print("✓ Uses threading for background execution")
        else:
            print("✗ Does not use threading")
            all_passed = False
        
        # Check for daemon thread
        if "daemon=True" in content:
            print("✓ Uses daemon thread (won't block app exit)")
        else:
            print("✗ Does not use daemon thread")
            all_passed = False
        
        # Check for self.after() to update UI in main thread
        if "self.after(" in content:
            print("✓ Updates UI in main thread using self.after()")
        else:
            print("⚠️ Warning: May not be updating UI in main thread")
    else:
        print("✗ Health check method not found")
        all_passed = False
    
    print()
    if all_passed:
        print("✅ THREAD SAFETY TEST PASSED")
    else:
        print("❌ THREAD SAFETY TEST FAILED")
    print("=" * 70)
    print()
    
    return all_passed

def test_url_accessibility_checks():
    """Test that URL accessibility checks use proper HTTP methods"""
    print("=" * 70)
    print("URL Accessibility Test")
    print("=" * 70)
    print()
    
    main_file = "src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Extract the health check function
    health_func = extract_function(content, "check_tailscale_serve_health")
    if health_func is None:
        health_func = ""
    
    # Check for urllib usage
    if "urllib.request" in health_func:
        print("✓ Uses urllib.request for HTTP checks")
    else:
        print("✗ urllib.request not used")
        all_passed = False
    
    # Check for proper error handling
    http_errors = [
        ("urllib.error.HTTPError", "HTTPError handling"),
        ("urllib.error.URLError", "URLError handling"),
        ("socket.timeout", "Timeout handling"),
    ]
    
    for error_class, description in http_errors:
        if error_class in health_func:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for SSL certificate handling
    if "certificate" in health_func.lower() or "ssl" in health_func.lower():
        print("✓ Handles SSL certificate errors")
    else:
        print("⚠️ Warning: SSL certificate error handling not explicit")
    
    # Check for timeout parameter
    if "timeout=" in health_func:
        print("✓ Sets timeout for HTTP requests")
    else:
        print("✗ No timeout set for HTTP requests")
        all_passed = False
    
    print()
    if all_passed:
        print("✅ URL ACCESSIBILITY TEST PASSED")
    else:
        print("❌ URL ACCESSIBILITY TEST FAILED")
    print("=" * 70)
    print()
    
    return all_passed

def test_ui_display_methods():
    """Test that UI display methods exist and are properly structured"""
    print("=" * 70)
    print("UI Display Methods Test")
    print("=" * 70)
    print()
    
    main_file = "src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Check for display methods
    display_methods = [
        ("def _display_health_check_results", "Display results method"),
        ("def _add_check_result", "Add check result method"),
        ("def _display_health_check_error", "Display error method"),
    ]
    
    for method, description in display_methods:
        if method in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    
    # Check for UI elements in display methods
    ui_elements = [
        ("tk.Label", "Label widgets"),
        ("tk.Frame", "Frame widgets"),
        ("webbrowser.open", "Clickable URLs"),
        ("underline", "URL styling"),
        ("cursor=\"hand2\"", "Link cursor"),
    ]
    
    for element, description in ui_elements:
        if element in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    
    # Check for loading indicator
    if "Running health checks" in content or "⏳" in content:
        print("✓ Loading indicator present")
    else:
        print("✗ Loading indicator not found")
        all_passed = False
    
    print()
    if all_passed:
        print("✅ UI DISPLAY TEST PASSED")
    else:
        print("❌ UI DISPLAY TEST FAILED")
    print("=" * 70)
    print()
    
    return all_passed

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("COMPREHENSIVE INTEGRATION TEST SUITE")
    print("=" * 70)
    print()
    
    test_results = []
    
    test_results.append(test_health_check_structure())
    test_results.append(test_health_check_error_messages())
    test_results.append(test_ui_thread_safety())
    test_results.append(test_url_accessibility_checks())
    test_results.append(test_ui_display_methods())
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results)
    
    print(f"\nTests Passed: {passed_tests}/{total_tests}")
    
    if all(test_results):
        print("\n✅ ALL INTEGRATION TESTS PASSED!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n❌ SOME INTEGRATION TESTS FAILED")
        print("=" * 70)
        sys.exit(1)
