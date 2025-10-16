#!/usr/bin/env python3
"""
Test script for Remote Access UI/UX enhancements.
This script validates the new centering, domain display, and startup automation features.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhancements():
    """Test that enhancements are properly implemented"""
    print("=" * 80)
    print("Remote Access UI/UX Enhancements Test")
    print("=" * 80)
    print()
    
    # Check if main file exists
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    print(f"✓ Main file found: {main_file}")
    
    # Read and check for key implementations
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for centering improvements
    print("\n" + "=" * 80)
    print("Centering Improvements")
    print("=" * 80)
    print()
    
    centering_checks = [
        ("update_canvas_window", "Canvas window update callback for centering"),
        ("canvas.coords(canvas_window", "Dynamic canvas window positioning"),
        ("canvas.bind('<Configure>'", "Canvas configure event binding"),
        ("anchor=\"center\"", "Center anchor for content frame"),
        ("pack_propagate(False)", "Fixed width maintenance"),
    ]
    
    all_passed = True
    for check_str, description in centering_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for trusted domains management
    print("\n" + "=" * 80)
    print("Trusted Domains Management")
    print("=" * 80)
    print()
    
    domains_checks = [
        ("_get_trusted_domains", "Method to get trusted domains"),
        ("_remove_trusted_domain", "Method to remove trusted domain"),
        ("_display_current_trusted_domains", "Method to display domains"),
        ("_on_remove_domain", "Domain removal handler"),
        ("Current Trusted Domains", "Trusted domains section title"),
        ("✕", "Remove button symbol"),
    ]
    
    for check_str, description in domains_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for startup automation
    print("\n" + "=" * 80)
    print("Startup Automation")
    print("=" * 80)
    print()
    
    automation_checks = [
        ("_show_startup_automation_guide", "Startup automation guide method"),
        ("Setup Startup Automation", "Startup automation button text"),
        ("REMOTE_ACCESS_STARTUP_GUIDE.md", "Reference to startup guide"),
    ]
    
    for check_str, description in automation_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for startup automation files
    print("\n" + "=" * 80)
    print("Startup Automation Files")
    print("=" * 80)
    print()
    
    files_to_check = [
        ("nextcloud-remote-access.service", "Systemd service file"),
        ("nextcloud-remote-access-startup.sh", "Startup script"),
        ("REMOTE_ACCESS_STARTUP_GUIDE.md", "Installation guide"),
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"✓ {description}: {filename}")
        else:
            print(f"✗ {description}: {filename} - NOT FOUND")
            all_passed = False
    
    # Check startup script content
    if os.path.exists("nextcloud-remote-access-startup.sh"):
        with open("nextcloud-remote-access-startup.sh", 'r') as f:
            script_content = f.read()
        
        print("\n" + "=" * 80)
        print("Startup Script Content Verification")
        print("=" * 80)
        print()
        
        script_checks = [
            ("#!/bin/bash", "Bash shebang"),
            ("get_nextcloud_container", "Container detection function"),
            ("add_trusted_domain", "Domain addition function"),
            ("TAILSCALE_IP=", "Tailscale IP retrieval"),
            ("TAILSCALE_HOSTNAME=", "Tailscale hostname retrieval"),
            ("occ config:system:set", "Nextcloud occ command usage"),
            ("/var/log/nextcloud-remote-access.log", "Logging functionality"),
        ]
        
        for check_str, description in script_checks:
            if check_str in script_content:
                print(f"✓ {description}")
            else:
                print(f"✗ {description} - NOT FOUND")
                all_passed = False
    
    # Check systemd service content
    if os.path.exists("nextcloud-remote-access.service"):
        with open("nextcloud-remote-access.service", 'r') as f:
            service_content = f.read()
        
        print("\n" + "=" * 80)
        print("Systemd Service Content Verification")
        print("=" * 80)
        print()
        
        service_checks = [
            ("[Unit]", "Unit section"),
            ("[Service]", "Service section"),
            ("[Install]", "Install section"),
            ("After=docker.service", "Docker service dependency"),
            ("After=docker.service tailscaled.service", "Tailscale service dependency"),
            ("Type=oneshot", "Oneshot service type"),
            ("WantedBy=multi-user.target", "Multi-user target"),
        ]
        
        for check_str, description in service_checks:
            if check_str in service_content:
                print(f"✓ {description}")
            else:
                print(f"✗ {description} - NOT FOUND")
                all_passed = False
    
    # Final result
    print("\n" + "=" * 80)
    print("Test Result")
    print("=" * 80)
    print()
    
    if all_passed:
        print("✓ All tests passed!")
        print()
        print("Manual Testing Instructions:")
        print("-" * 80)
        print("1. Run the application: python3 nextcloud_restore_and_backup-v9.py")
        print("2. Navigate to Remote Access Setup (via dropdown menu)")
        print("3. Verify centering:")
        print("   • Content should be horizontally centered in the window")
        print("   • Content width should be fixed at 600px")
        print("   • Centering should remain stable when resizing window")
        print()
        print("4. Click 'Configure Remote Access' button")
        print("5. Verify trusted domains display:")
        print("   • Section titled 'Current Trusted Domains' should appear")
        print("   • All domains should be listed with ✕ buttons")
        print("   • Each domain should be in a bordered frame")
        print()
        print("6. Test domain removal:")
        print("   • Click ✕ button next to a domain")
        print("   • Confirm the removal dialog")
        print("   • Verify domain is removed and page refreshes")
        print()
        print("7. Test startup automation (Linux only):")
        print("   • Click 'Setup Startup Automation' button")
        print("   • Verify guide dialog appears")
        print("   • Follow guide to install service")
        print("   • Reboot and verify domains are auto-applied")
        print()
        print("8. Check accessibility:")
        print("   • All text should be readable")
        print("   • Buttons should be clearly labeled")
        print("   • Colors should have good contrast")
        print()
    else:
        print("✗ Some tests failed. Please review the implementation.")
        print()
    
    return all_passed

if __name__ == '__main__':
    success = test_enhancements()
    sys.exit(0 if success else 1)
