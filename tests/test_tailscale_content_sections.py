#!/usr/bin/env python3
"""
Test script to verify all content sections are properly created in Tailscale pages.
This ensures no content disappears and all widgets are visible.
"""

import sys
import os
import re

def test_content_sections():
    """Test that all content sections are created in Tailscale pages"""
    print("=" * 70)
    print("Remote Access Setup (Tailscale) Content Sections Verification")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find show_tailscale_wizard method
    method_pattern = r'def show_tailscale_wizard\(self\):(.*?)(?=\n    def |\Z)'
    match = re.search(method_pattern, content, re.DOTALL)
    
    if not match:
        print("✗ Could not find show_tailscale_wizard method")
        return False
    
    method_content = match.group(1)
    
    checks = []
    
    print("Checking show_tailscale_wizard content sections:")
    print("-" * 70)
    
    # Check all expected UI elements
    ui_elements = [
        ("Title label", "🌐 Remote Access Setup"),
        ("Subtitle label", "Securely access your Nextcloud"),
        ("Info box frame", "info_frame = tk.Frame"),
        ("Info box title", "ℹ️ What is Tailscale?"),
        ("Info box description", "Tailscale creates a secure"),
        ("Return to main menu button", "Return to Main Menu"),
        ("Status frame", "status_frame = tk.Frame"),
        ("Installation status label", "Tailscale Installation:"),
        ("Actions frame", "actions_frame = tk.Frame"),
        ("Install button check", "📦 Install Tailscale"),
        ("Start button check", "▶️ Start Tailscale"),
        ("Configure button check", "⚙️ Configure Remote Access"),
    ]
    
    for name, search_text in ui_elements:
        if search_text in method_content:
            print(f"✓ {name} found")
            checks.append(True)
        else:
            print(f"✗ {name} NOT found")
            checks.append(False)
    
    print()
    print("=" * 70)
    print("Checking _show_tailscale_config content sections:")
    print("-" * 70)
    
    # Find _show_tailscale_config method
    config_pattern = r'def _show_tailscale_config\(self\):(.*?)(?=\n    def |\Z)'
    config_match = re.search(config_pattern, content, re.DOTALL)
    
    if not config_match:
        print("✗ Could not find _show_tailscale_config method")
        return False
    
    config_content = config_match.group(1)
    
    # Check all expected UI elements in config page
    config_elements = [
        ("Title label", "⚙️ Configure Remote Access"),
        ("Back button", "← Back to Tailscale Setup"),
        ("Info frame", "info_frame = tk.Frame"),
        ("Network info title", "📡 Your Tailscale Network Information"),
        ("Tailscale IP label check", "Tailscale IP:"),
        ("MagicDNS label check", "MagicDNS Name:"),
        ("Custom domains section", "Custom Domains (Optional)"),
        ("Domain entry field", "custom_domain_var = tk.StringVar()"),
        ("Apply button", "✓ Apply Configuration to Nextcloud"),
        ("Info box with config items", "ℹ️ What will be configured:"),
        ("Current domains display", "_display_current_trusted_domains"),
    ]
    
    for name, search_text in config_elements:
        if search_text in config_content:
            print(f"✓ {name} found")
            checks.append(True)
        else:
            print(f"✗ {name} NOT found")
            checks.append(False)
    
    print()
    print("=" * 70)
    print("Checking pack/place calls (ensure widgets are added to layout):")
    print("-" * 70)
    
    # Count pack calls in show_tailscale_wizard
    pack_count = method_content.count('.pack(')
    print(f"✓ show_tailscale_wizard has {pack_count} .pack() calls")
    if pack_count < 10:
        print(f"  ⚠️  Warning: Only {pack_count} pack calls found, might be missing widgets")
    
    # Count pack calls in _show_tailscale_config
    config_pack_count = config_content.count('.pack(')
    print(f"✓ _show_tailscale_config has {config_pack_count} .pack() calls")
    if config_pack_count < 15:
        print(f"  ⚠️  Warning: Only {config_pack_count} pack calls found, might be missing widgets")
    
    print()
    print("=" * 70)
    print(f"Results: {sum(checks)}/{len(checks)} content checks passed")
    print("=" * 70)
    
    if all(checks):
        print("\n✅ All content sections are present and properly defined!")
        return True
    else:
        print(f"\n⚠️  Some content sections may be missing. {len(checks) - sum(checks)} issues found.")
        return False

if __name__ == "__main__":
    success = test_content_sections()
    sys.exit(0 if success else 1)
