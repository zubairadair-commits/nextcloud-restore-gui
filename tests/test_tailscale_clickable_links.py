#!/usr/bin/env python3
"""
Test script to validate that Tailscale IP and MagicDNS Hostname URLs
are always displayed as clickable HTTPS links after configuration.
"""

import sys
import os
import re

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_tailscale_clickable_links():
    """Test that Tailscale links are always clickable regardless of auto-serve status"""
    print("=" * 80)
    print("Tailscale Clickable Links Test")
    print("=" * 80)
    print()
    
    # Check if main file exists
    main_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "src", "nextcloud_restore_and_backup-v9.py")
    if not os.path.exists(main_file):
        print(f"✗ Main file not found at: {main_file}")
        return False
    
    print(f"✓ Main file found: {main_file}")
    
    # Read the file content
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Test 1: Check that _show_tailscale_config always shows clickable links
    print("\n" + "=" * 80)
    print("Test 1: Configuration Page (_show_tailscale_config)")
    print("=" * 80)
    print()
    
    # Find the _show_tailscale_config method
    config_method_match = re.search(
        r'def _show_tailscale_config\(self\):.*?(?=\n    def |\nclass |\Z)',
        content,
        re.DOTALL
    )
    
    if not config_method_match:
        print("✗ Could not find _show_tailscale_config method")
        all_passed = False
    else:
        config_method = config_method_match.group(0)
        print("✓ Found _show_tailscale_config method")
        
        # Check that Tailscale IP URL is always created as clickable
        if 'ts_ip_url = f"https://{ts_ip}"' in config_method:
            print("✓ Tailscale IP URL uses HTTPS")
        else:
            print("✗ Tailscale IP URL does not use HTTPS")
            all_passed = False
        
        if '_create_clickable_url_config(info_frame, f"Tailscale IP: {ts_ip_url}", ts_ip_url)' in config_method:
            print("✓ Tailscale IP URL is created as clickable link")
        else:
            print("✗ Tailscale IP URL is not created as clickable link")
            all_passed = False
        
        # Check that Tailscale Hostname URL is always created as clickable
        if 'ts_hostname_url = f"https://{ts_hostname}"' in config_method:
            print("✓ Tailscale Hostname URL uses HTTPS")
        else:
            print("✗ Tailscale Hostname URL does not use HTTPS")
            all_passed = False
        
        if '_create_clickable_url_config(info_frame, f"Tailscale Hostname: {ts_hostname_url}", ts_hostname_url)' in config_method:
            print("✓ Tailscale Hostname URL is created as clickable link")
        else:
            print("✗ Tailscale Hostname URL is not created as clickable link")
            all_passed = False
        
        # Check that there's no conditional check for auto-serve status
        # Look for patterns that check task_status before creating links
        if 'task_status = check_scheduled_task_status()' in config_method:
            # Find all occurrences and check if they're before link creation
            task_status_pattern = r'if ts_ip:.*?task_status = check_scheduled_task_status\(\).*?if task_status\[.*?_create_clickable_url'
            if re.search(task_status_pattern, config_method, re.DOTALL):
                print("✗ Still checking task_status before creating clickable links")
                all_passed = False
            else:
                print("✓ No conditional task_status check before creating links")
        else:
            print("✓ No task_status check in IP/Hostname URL section")
    
    # Test 2: Check that _display_tailscale_info always shows clickable links
    print("\n" + "=" * 80)
    print("Test 2: Info Display Page (_display_tailscale_info)")
    print("=" * 80)
    print()
    
    # Find the _display_tailscale_info method
    display_method_match = re.search(
        r'def _display_tailscale_info\(self, parent\):.*?(?=\n    def |\nclass |\Z)',
        content,
        re.DOTALL
    )
    
    if not display_method_match:
        print("✗ Could not find _display_tailscale_info method")
        all_passed = False
    else:
        display_method = display_method_match.group(0)
        print("✓ Found _display_tailscale_info method")
        
        # Check that Tailscale IP URL is always created as clickable
        if 'ts_ip_url = f"https://{ts_ip}"' in display_method:
            print("✓ Tailscale IP URL uses HTTPS")
        else:
            print("✗ Tailscale IP URL does not use HTTPS")
            all_passed = False
        
        if '_create_clickable_url(info_frame, f"Tailscale IP: {ts_ip_url}", ts_ip_url)' in display_method:
            print("✓ Tailscale IP URL is created as clickable link")
        else:
            print("✗ Tailscale IP URL is not created as clickable link")
            all_passed = False
        
        # Check that Tailscale Hostname URL is always created as clickable
        if 'ts_hostname_url = f"https://{ts_hostname}"' in display_method:
            print("✓ Tailscale Hostname URL uses HTTPS")
        else:
            print("✗ Tailscale Hostname URL does not use HTTPS")
            all_passed = False
        
        if '_create_clickable_url(info_frame, f"Tailscale Hostname: {ts_hostname_url}", ts_hostname_url)' in display_method:
            print("✓ Tailscale Hostname URL is created as clickable link")
        else:
            print("✗ Tailscale Hostname URL is not created as clickable link")
            all_passed = False
        
        # Check that there's no conditional check for auto-serve status before creating links
        task_status_pattern = r'if ts_ip:.*?task_status = check_scheduled_task_status\(\).*?if task_status\[.*?_create_clickable_url'
        if re.search(task_status_pattern, display_method, re.DOTALL):
            print("✗ Still checking task_status before creating clickable links")
            all_passed = False
        else:
            print("✓ No conditional task_status check before creating links")
    
    # Test 3: Verify helper methods exist
    print("\n" + "=" * 80)
    print("Test 3: Helper Methods")
    print("=" * 80)
    print()
    
    if '_create_clickable_url(self, parent, display_text, url)' in content:
        print("✓ _create_clickable_url method exists")
    else:
        print("✗ _create_clickable_url method not found")
        all_passed = False
    
    if '_create_clickable_url_config(self, parent, display_text, url)' in content:
        print("✓ _create_clickable_url_config method exists")
    else:
        print("✗ _create_clickable_url_config method not found")
        all_passed = False
    
    # Check that clickable URL methods use webbrowser.open
    if 'webbrowser.open(url)' in content:
        print("✓ URLs are opened using webbrowser.open")
    else:
        print("✗ webbrowser.open not found")
        all_passed = False
    
    # Final result
    print("\n" + "=" * 80)
    print("Test Result")
    print("=" * 80)
    print()
    
    if all_passed:
        print("✓ All tests passed!")
        print()
        print("Summary:")
        print("-" * 80)
        print("• Tailscale IP and MagicDNS Hostname URLs are now always displayed")
        print("  as clickable HTTPS hyperlinks after configuration")
        print("• Links are independent of auto-serve configuration status")
        print("• URLs open in the user's default web browser when clicked")
        print("• Both configuration page and info display page are updated")
        print()
        print("Manual Testing Instructions:")
        print("-" * 80)
        print("1. Run the application: python3 src/nextcloud_restore_and_backup-v9.py")
        print("2. Navigate to Remote Access Setup")
        print("3. If Tailscale is running, verify that:")
        print("   • Tailscale IP URL is displayed as a blue, underlined link")
        print("   • MagicDNS Hostname URL is displayed as a blue, underlined link")
        print("   • Both links use HTTPS protocol")
        print("   • Clicking links opens browser to the correct URL")
        print("4. Test both in the wizard page and configuration page")
        print()
    else:
        print("✗ Some tests failed. Please review the implementation.")
        print()
    
    return all_passed

if __name__ == '__main__':
    success = test_tailscale_clickable_links()
    sys.exit(0 if success else 1)
