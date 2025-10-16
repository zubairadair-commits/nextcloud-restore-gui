#!/usr/bin/env python3
"""
Test script to verify that Tailscale page navigation and theme changes work correctly.
Validates that:
1. Pages are properly tracked in current_page
2. refresh_current_page() calls the correct page methods
3. toggle_theme() refreshes the current page
4. Menu actions properly navigate to pages
"""

import sys
import os
import re

def test_navigation_and_theme():
    """Test that navigation and theme changes properly render Tailscale pages"""
    print("=" * 70)
    print("Tailscale Navigation and Theme Change Verification")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: show_tailscale_wizard sets current_page
    print("Testing Page Tracking:")
    print("-" * 70)
    if "self.current_page = 'tailscale_wizard'" in content:
        print("✓ Check 1: show_tailscale_wizard sets current_page")
        checks.append(True)
    else:
        print("✗ Check 1: show_tailscale_wizard does NOT set current_page")
        checks.append(False)
    
    # Check 2: _show_tailscale_config sets current_page
    if "self.current_page = 'tailscale_config'" in content:
        print("✓ Check 2: _show_tailscale_config sets current_page")
        checks.append(True)
    else:
        print("✗ Check 2: _show_tailscale_config does NOT set current_page")
        checks.append(False)
    
    # Check 3: refresh_current_page exists
    print("\nTesting Page Refresh:")
    print("-" * 70)
    if "def refresh_current_page(self):" in content:
        print("✓ Check 3: refresh_current_page method exists")
        checks.append(True)
    else:
        print("✗ Check 3: refresh_current_page method NOT found")
        checks.append(False)
    
    # Check 4: refresh_current_page handles tailscale_wizard
    if "if self.current_page == 'tailscale_wizard':" in content and \
       "self.show_tailscale_wizard()" in content:
        print("✓ Check 4: refresh_current_page handles tailscale_wizard")
        checks.append(True)
    else:
        print("✗ Check 4: refresh_current_page does NOT handle tailscale_wizard")
        checks.append(False)
    
    # Check 5: refresh_current_page handles tailscale_config
    if "elif self.current_page == 'tailscale_config':" in content and \
       "self._show_tailscale_config()" in content:
        print("✓ Check 5: refresh_current_page handles tailscale_config")
        checks.append(True)
    else:
        print("✗ Check 5: refresh_current_page does NOT handle tailscale_config")
        checks.append(False)
    
    # Check 6: toggle_theme exists
    print("\nTesting Theme Toggle:")
    print("-" * 70)
    if "def toggle_theme(self):" in content:
        print("✓ Check 6: toggle_theme method exists")
        checks.append(True)
    else:
        print("✗ Check 6: toggle_theme method NOT found")
        checks.append(False)
    
    # Check 7: toggle_theme calls refresh_current_page
    toggle_pattern = r'def toggle_theme\(self\):(.*?)(?=\n    def |\Z)'
    match = re.search(toggle_pattern, content, re.DOTALL)
    if match and "self.refresh_current_page()" in match.group(1):
        print("✓ Check 7: toggle_theme calls refresh_current_page")
        checks.append(True)
    else:
        print("✗ Check 7: toggle_theme does NOT call refresh_current_page")
        checks.append(False)
    
    # Check 8: Menu action calls show_tailscale_wizard
    print("\nTesting Menu Navigation:")
    print("-" * 70)
    menu_pattern = r'Remote Access.*?command=.*?show_tailscale_wizard'
    if re.search(menu_pattern, content, re.DOTALL | re.IGNORECASE):
        print("✓ Check 8: Menu action calls show_tailscale_wizard")
        checks.append(True)
    else:
        print("✗ Check 8: Menu action does NOT call show_tailscale_wizard")
        checks.append(False)
    
    # Check 9: Back button in config calls show_tailscale_wizard
    if "← Back to Tailscale Setup" in content and \
       "command=self.show_tailscale_wizard" in content:
        print("✓ Check 9: Back button in config navigates to wizard")
        checks.append(True)
    else:
        print("✗ Check 9: Back button navigation NOT found")
        checks.append(False)
    
    # Check 10: Configure button in wizard calls _show_tailscale_config
    if "⚙️ Configure Remote Access" in content and \
       "command=self._show_tailscale_config" in content:
        print("✓ Check 10: Configure button navigates to config")
        checks.append(True)
    else:
        print("✗ Check 10: Configure button navigation NOT found")
        checks.append(False)
    
    # Check 11: @log_page_render decorator is present
    print("\nTesting Error Handling:")
    print("-" * 70)
    if "@log_page_render(\"TAILSCALE WIZARD\")" in content:
        print("✓ Check 11: show_tailscale_wizard has error handling decorator")
        checks.append(True)
    else:
        print("✗ Check 11: show_tailscale_wizard missing error handling")
        checks.append(False)
    
    # Check 12: @log_page_render decorator is present for config
    if "@log_page_render(\"TAILSCALE CONFIG\")" in content:
        print("✓ Check 12: _show_tailscale_config has error handling decorator")
        checks.append(True)
    else:
        print("✗ Check 12: _show_tailscale_config missing error handling")
        checks.append(False)
    
    # Overall result
    print("\n" + "=" * 70)
    if all(checks):
        print("✅ OVERALL: All navigation and theme tests passed!")
        print("\nSummary:")
        print("  • Page tracking implemented (current_page)")
        print("  • refresh_current_page() handles both Tailscale pages")
        print("  • toggle_theme() refreshes current page")
        print("  • Menu actions properly navigate to pages")
        print("  • Navigation buttons work correctly")
        print("  • Error handling decorators in place")
        return True
    else:
        print("❌ OVERALL: Some navigation/theme tests failed")
        failed_count = len([c for c in checks if not c])
        print(f"   {failed_count} out of {len(checks)} checks failed")
        return False

if __name__ == "__main__":
    success = test_navigation_and_theme()
    sys.exit(0 if success else 1)
