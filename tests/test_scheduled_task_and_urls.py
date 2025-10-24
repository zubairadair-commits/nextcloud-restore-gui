#!/usr/bin/env python3
"""
Test script for Scheduled Task Management and Clickable URL features.
This script validates the implementation of:
1. Windows Scheduled Task management (check, enable, disable, remove)
2. Clickable Nextcloud URLs in Tailscale wizard
"""

import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def test_scheduled_task_features():
    """Test that scheduled task management features are properly implemented"""
    print("=" * 80)
    print("Scheduled Task Management Features Test")
    print("=" * 80)
    print()
    
    # Check if main file exists
    main_file = os.path.join(os.path.dirname(__file__), "../src/nextcloud_restore_and_backup-v9.py")
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    print(f"✓ Main file found: {main_file}")
    
    # Read and check for key implementations
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for scheduled task status function
    print("\n" + "=" * 80)
    print("Scheduled Task Status Functions")
    print("=" * 80)
    print()
    
    all_passed = True
    status_checks = [
        ("def check_scheduled_task_status():", "Scheduled task status check function"),
        ("'exists': False,", "Task exists flag in status dict"),
        ("'enabled': False,", "Task enabled flag in status dict"),
        ("'status': 'Not configured',", "Default status string"),
        ("'next_run': 'N/A',", "Next run time field"),
        ("'last_run': 'N/A',", "Last run time field"),
        ("'port': None", "Port field in status dict"),
        ("/Query", "Windows schtasks query command"),
        ("'is-enabled'", "Linux service check"),
    ]
    
    for check_str, description in status_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for enable/disable functions
    print("\n" + "=" * 80)
    print("Enable/Disable Task Functions")
    print("=" * 80)
    print()
    
    enable_disable_checks = [
        ("def disable_scheduled_task():", "Disable scheduled task function"),
        ("def enable_scheduled_task():", "Enable scheduled task function"),
        ("/Change", "Windows schtasks change command"),
        ("/DISABLE", "Windows task disable flag"),
        ("/ENABLE", "Windows task enable flag"),
    ]
    
    for check_str, description in enable_disable_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for UI handler methods
    print("\n" + "=" * 80)
    print("UI Handler Methods")
    print("=" * 80)
    print()
    
    ui_handler_checks = [
        ("def _disable_scheduled_task(self, content_frame, canvas):", "Disable task UI handler"),
        ("def _enable_scheduled_task(self, content_frame, canvas):", "Enable task UI handler"),
        ("def _remove_scheduled_task(self, content_frame, canvas):", "Remove task UI handler"),
        ("messagebox.askyesno", "Confirmation dialog for task removal"),
        ("self._show_tailscale_config()", "Page refresh after task management"),
    ]
    
    for check_str, description in ui_handler_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for scheduled task status display in UI
    print("\n" + "=" * 80)
    print("Scheduled Task Status UI Display")
    print("=" * 80)
    print()
    
    status_ui_checks = [
        ("task_status = check_scheduled_task_status()", "Task status check in UI"),
        ("📅 Scheduled Task Status", "Status section title"),
        ("✓ Enabled", "Enabled status indicator"),
        ("✗ Disabled", "Disabled status indicator"),
        ("Configured Port:", "Port display in status"),
        ("Next Run:", "Next run time display"),
        ("⏸ Disable Auto-Start", "Disable button text"),
        ("▶️ Enable Auto-Start", "Enable button text"),
        ("🗑️ Remove Task", "Remove button text"),
        ("command=lambda: self._disable_scheduled_task", "Disable button command"),
        ("command=lambda: self._enable_scheduled_task", "Enable button command"),
        ("command=lambda: self._remove_scheduled_task", "Remove button command"),
    ]
    
    for check_str, description in status_ui_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    return all_passed


def test_clickable_url_features():
    """Test that clickable URL features are properly implemented"""
    print("\n" + "=" * 80)
    print("Clickable URL Features Test")
    print("=" * 80)
    print()
    
    # Check if main file exists
    main_file = os.path.join(os.path.dirname(__file__), "../src/nextcloud_restore_and_backup-v9.py")
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    # Read and check for key implementations
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Check for clickable URL helper methods
    print("Clickable URL Helper Methods")
    print("-" * 80)
    print()
    
    url_helper_checks = [
        ("def _create_clickable_url(self, parent, display_text, url):", "Clickable URL helper method"),
        ("def _create_clickable_url_config(self, parent, display_text, url):", "Config page URL helper"),
        ("webbrowser.open(url)", "Browser open call"),
        ('cursor="hand2"', "Hand cursor for clickable links"),
        ('font=("Arial", 9, "underline")', "Underlined link text"),
        ("fg=\"#3daee9\"", "Blue link color"),
        ("url_label.bind(\"<Button-1>\", open_url)", "Click event binding"),
        ("url_label.bind(\"<Enter>\", on_enter)", "Hover enter event"),
        ("url_label.bind(\"<Leave>\", on_leave)", "Hover leave event"),
    ]
    
    for check_str, description in url_helper_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for URL display in Tailscale info
    print("\n" + "=" * 80)
    print("URL Display in Tailscale Info")
    print("=" * 80)
    print()
    
    url_display_checks = [
        ("detected_port = get_nextcloud_port()", "Port detection in info display"),
        ("🌐 Access Nextcloud via:", "URL section title"),
        ("Local:", "Local URL label"),
        ("Tailscale IP:", "Tailscale IP URL label"),
        ("Tailscale Hostname:", "Tailscale hostname URL label"),
        ("http://localhost:", "Local URL format"),
        ("https://", "HTTPS protocol for Tailscale URLs"),
        ("self._create_clickable_url(info_frame,", "Clickable URL creation call"),
        ("self._create_clickable_url_config(info_frame,", "Config page URL creation call"),
    ]
    
    for check_str, description in url_display_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for conditional URL display based on task status
    print("\n" + "=" * 80)
    print("Conditional URL Display")
    print("=" * 80)
    print()
    
    conditional_checks = [
        ("if task_status['exists']:", "Check task status for URL display"),
        ("(enable auto-serve below to use)", "Message when auto-serve not configured"),
        ("(configure auto-serve below)", "Alternative message variant"),
    ]
    
    for check_str, description in conditional_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests"""
    print("Testing Scheduled Task Management and Clickable URLs Implementation\n")
    
    task_passed = test_scheduled_task_features()
    url_passed = test_clickable_url_features()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if task_passed and url_passed:
        print("✓ All tests passed!")
        return 0
    else:
        if not task_passed:
            print("✗ Scheduled task management tests failed")
        if not url_passed:
            print("✗ Clickable URL tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
