#!/usr/bin/env python3
"""
Test script for Tailscale Health Check feature.
This script validates the health check functionality and UI elements.
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_health_check_function():
    """Test that the health check function exists and has correct structure"""
    print("=" * 70)
    print("Tailscale Health Check Feature Test")
    print("=" * 70)
    print()
    
    # Check if main file exists
    main_file = "src/nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    print(f"✓ Main file found: {main_file}")
    
    # Read and check for key implementations
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for health check function and UI elements
    checks = [
        ("check_tailscale_serve_health", "Health check function"),
        ("_run_health_check", "Run health check method"),
        ("_display_health_check_results", "Display health check results method"),
        ("_add_check_result", "Add individual check result method"),
        ("_display_health_check_error", "Display error method"),
        ("Connection Health Check", "Health check section title"),
        ("Run Health Check", "Health check button text"),
        ("serve_running", "Serve running check"),
        ("port_mapped", "Port mapping check"),
        ("ip_accessible", "IP accessibility check"),
        ("hostname_accessible", "Hostname accessibility check"),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    print("=" * 70)
    print("Health Check Function Structure")
    print("=" * 70)
    print()
    
    # Check for proper return structure
    if "'overall_status'" in content:
        print("✓ Health check returns overall_status")
    else:
        print("✗ overall_status not found in return structure")
        all_passed = False
    
    if "'checks'" in content:
        print("✓ Health check returns individual checks")
    else:
        print("✗ checks dict not found in return structure")
        all_passed = False
    
    # Check for status values
    status_checks = [
        ("'success'", "Success status"),
        ("'warning'", "Warning status"),
        ("'error'", "Error status"),
    ]
    
    for status_str, description in status_checks:
        if status_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    print("=" * 70)
    print("Health Check UI Elements")
    print("=" * 70)
    print()
    
    # Check for UI elements
    ui_checks = [
        ("🔍 Run Health Check", "Health check button with icon"),
        ("⏳ Running health checks", "Loading indicator"),
        ("All checks passed", "Success message"),
        ("Some checks failed", "Warning message"),
        ("Multiple checks failed", "Error message"),
        ("Tailscale Serve Status", "Serve status check label"),
        ("Nextcloud Port Detection", "Port detection check label"),
        ("Tailscale IP Accessibility", "IP accessibility check label"),
        ("MagicDNS Hostname Accessibility", "Hostname accessibility check label"),
    ]
    
    for ui_str, description in ui_checks:
        if ui_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    print("=" * 70)
    print("Health Check Error Handling")
    print("=" * 70)
    print()
    
    # Check for error handling and suggestions
    error_checks = [
        ("suggestion", "Suggestion field in check results"),
        ("Ensure Tailscale Serve is running", "Serve suggestion message"),
        ("Check Tailscale connection", "Connection suggestion"),
        ("Enable MagicDNS", "MagicDNS suggestion"),
        ("urllib.request", "HTTP request capability"),
        ("threading.Thread", "Async health check execution"),
    ]
    
    for error_str, description in error_checks:
        if error_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    print()
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
    print()
    
    return all_passed

def test_health_check_integration():
    """Test that health check is properly integrated into config wizard"""
    print("=" * 70)
    print("Health Check Integration Test")
    print("=" * 70)
    print()
    
    main_file = "src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check that health check section appears in the right place
    # It should be after the Tailscale info section and before Custom domains
    
    # Find indices
    info_section_idx = content.find("Use these addresses to access Nextcloud")
    health_section_idx = content.find("Connection Health Check")
    custom_domain_idx = content.find("Custom Domains (Optional)")
    
    all_passed = True
    
    if info_section_idx != -1:
        print("✓ Tailscale info section found")
    else:
        print("✗ Tailscale info section not found")
        all_passed = False
    
    if health_section_idx != -1:
        print("✓ Health check section found")
    else:
        print("✗ Health check section not found")
        all_passed = False
    
    if custom_domain_idx != -1:
        print("✓ Custom domains section found")
    else:
        print("✗ Custom domains section not found")
        all_passed = False
    
    # Check ordering
    if info_section_idx != -1 and health_section_idx != -1 and custom_domain_idx != -1:
        if info_section_idx < health_section_idx < custom_domain_idx:
            print("✓ Health check section is properly positioned")
        else:
            print("✗ Health check section is not in the correct position")
            all_passed = False
    
    print()
    if all_passed:
        print("✅ INTEGRATION TEST PASSED")
    else:
        print("❌ INTEGRATION TEST FAILED")
    print("=" * 70)
    print()
    
    return all_passed

if __name__ == "__main__":
    test1_passed = test_health_check_function()
    test2_passed = test_health_check_integration()
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
