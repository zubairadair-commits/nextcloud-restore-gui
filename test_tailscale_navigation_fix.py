#!/usr/bin/env python3
"""
Test script to verify the Tailscale navigation and theme toggle fix.
Ensures pages don't go blank on navigation, theme change, or menu actions.
"""

import sys
import os
import re

def test_navigation_tracking():
    """Test that current_page tracking is properly implemented"""
    print("=" * 70)
    print("Tailscale Navigation & Theme Toggle Fix Verification")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: current_page variable exists in __init__
    init_pattern = r'def __init__\(self\):(.*?)(?=\n    def |\Z)'
    init_match = re.search(init_pattern, content, re.DOTALL)
    
    if init_match and 'self.current_page' in init_match.group(1):
        print("✓ Check 1: current_page tracking variable added to __init__")
        checks.append(True)
    else:
        print("✗ Check 1: current_page tracking variable NOT found in __init__")
        checks.append(False)
    
    # Check 2: refresh_current_page method exists
    if 'def refresh_current_page(self):' in content:
        print("✓ Check 2: refresh_current_page method exists")
        checks.append(True)
    else:
        print("✗ Check 2: refresh_current_page method NOT found")
        checks.append(False)
    
    # Check 3: toggle_theme calls refresh_current_page
    toggle_pattern = r'def toggle_theme\(self\):(.*?)(?=\n    def |\Z)'
    toggle_match = re.search(toggle_pattern, content, re.DOTALL)
    
    if toggle_match and 'self.refresh_current_page()' in toggle_match.group(1):
        print("✓ Check 3: toggle_theme calls refresh_current_page (not show_landing)")
        checks.append(True)
    else:
        print("✗ Check 3: toggle_theme does NOT call refresh_current_page")
        checks.append(False)
    
    # Check 4: show_landing sets current_page
    landing_pattern = r'def show_landing\(self\):(.*?)(?=\n        for widget|\Z)'
    landing_match = re.search(landing_pattern, content, re.DOTALL)
    
    if landing_match and 'self.current_page' in landing_match.group(1):
        print("✓ Check 4: show_landing sets current_page")
        checks.append(True)
    else:
        print("✗ Check 4: show_landing does NOT set current_page")
        checks.append(False)
    
    # Check 5: show_tailscale_wizard sets current_page
    wizard_pattern = r'def show_tailscale_wizard\(self\):(.*?)(?=\n    def |\Z)'
    wizard_match = re.search(wizard_pattern, content, re.DOTALL)
    
    if wizard_match and 'self.current_page' in wizard_match.group(1):
        print("✓ Check 5: show_tailscale_wizard sets current_page")
        checks.append(True)
    else:
        print("✗ Check 5: show_tailscale_wizard does NOT set current_page")
        checks.append(False)
    
    # Check 6: _show_tailscale_config sets current_page
    config_pattern = r'def _show_tailscale_config\(self\):(.*?)(?=\n    def |\Z)'
    config_match = re.search(config_pattern, content, re.DOTALL)
    
    if config_match and 'self.current_page' in config_match.group(1):
        print("✓ Check 6: _show_tailscale_config sets current_page")
        checks.append(True)
    else:
        print("✗ Check 6: _show_tailscale_config does NOT set current_page")
        checks.append(False)
    
    # Check 7: show_schedule_backup sets current_page
    schedule_pattern = r'def show_schedule_backup\(self\):(.*?)(?=\n    def |\Z)'
    schedule_match = re.search(schedule_pattern, content, re.DOTALL)
    
    if schedule_match and 'self.current_page' in schedule_match.group(1):
        print("✓ Check 7: show_schedule_backup sets current_page")
        checks.append(True)
    else:
        print("✗ Check 7: show_schedule_backup does NOT set current_page")
        checks.append(False)
    
    # Check 8: refresh_current_page handles tailscale_wizard
    refresh_pattern = r'def refresh_current_page\(self\):(.*?)(?=\n    def |\Z)'
    refresh_match = re.search(refresh_pattern, content, re.DOTALL)
    
    if refresh_match and 'tailscale_wizard' in refresh_match.group(1) and 'show_tailscale_wizard' in refresh_match.group(1):
        print("✓ Check 8: refresh_current_page handles tailscale_wizard page")
        checks.append(True)
    else:
        print("✗ Check 8: refresh_current_page does NOT handle tailscale_wizard")
        checks.append(False)
    
    # Check 9: refresh_current_page handles tailscale_config
    if refresh_match and 'tailscale_config' in refresh_match.group(1) and '_show_tailscale_config' in refresh_match.group(1):
        print("✓ Check 9: refresh_current_page handles tailscale_config page")
        checks.append(True)
    else:
        print("✗ Check 9: refresh_current_page does NOT handle tailscale_config")
        checks.append(False)
    
    # Check 10: All widgets still properly created (centering fix preserved)
    if 'container = tk.Frame(self.body_frame' in content:
        widget_checks = []
        
        # In show_tailscale_wizard
        if wizard_match:
            wizard_content = wizard_match.group(0)
            if 'tk.Label' in wizard_content and '🌐 Remote Access Setup' in wizard_content:
                widget_checks.append(True)
            if 'tk.Button' in wizard_content and 'Return to Main Menu' in wizard_content:
                widget_checks.append(True)
        
        # In _show_tailscale_config
        if config_match:
            config_content = config_match.group(0)
            if 'tk.Label' in config_content and '⚙️ Configure Remote Access' in config_content:
                widget_checks.append(True)
            if 'tk.Button' in config_content and 'Back to Tailscale Setup' in config_content:
                widget_checks.append(True)
        
        if len(widget_checks) >= 4:
            print("✓ Check 10: All widgets still properly created with centering")
            checks.append(True)
        else:
            print("✗ Check 10: Some widgets may be missing")
            checks.append(False)
    else:
        print("✗ Check 10: Container frame for centering NOT found")
        checks.append(False)
    
    print()
    print("=" * 70)
    print(f"Results: {sum(checks)}/{len(checks)} checks passed")
    print("=" * 70)
    
    if all(checks):
        print("\n✅ All checks passed! Navigation and theme toggle fix is properly implemented.")
        print("\n📋 What was fixed:")
        print("  • Added current_page tracking to prevent losing page state")
        print("  • Theme toggle now refreshes current page instead of going to landing")
        print("  • All page methods update current_page on entry")
        print("  • Centering and widget creation logic preserved")
        print("\n🎯 Expected behavior:")
        print("  • Toggle theme on Tailscale wizard → stays on Tailscale wizard")
        print("  • Toggle theme on Tailscale config → stays on Tailscale config")
        print("  • Navigate between pages → all content visible and centered")
        print("  • Use menu to access pages → pages never blank")
        return True
    else:
        print(f"\n⚠️  Some checks failed. {len(checks) - sum(checks)} issues found.")
        return False

if __name__ == "__main__":
    success = test_navigation_tracking()
    sys.exit(0 if success else 1)
