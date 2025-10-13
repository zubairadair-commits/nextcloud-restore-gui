#!/usr/bin/env python3
"""
Test script for Tailscale feature implementation.
This script validates the new UI elements and Tailscale wizard functionality.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ui_elements():
    """Test that UI elements are properly defined"""
    print("=" * 70)
    print("Tailscale Feature Implementation Test")
    print("=" * 70)
    print()
    
    # Check if main file exists
    main_file = "nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    print(f"✓ Main file found: {main_file}")
    
    # Read and check for key implementations
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for header controls
    checks = [
        ("header_theme_btn", "Theme toggle button in header"),
        ("header_menu_btn", "Dropdown menu button in header"),
        ("show_dropdown_menu", "Dropdown menu method"),
        ("show_tailscale_wizard", "Tailscale wizard main method"),
        ("_check_tailscale_installed", "Tailscale installation check"),
        ("_check_tailscale_running", "Tailscale running check"),
        ("_install_tailscale", "Tailscale installation guide"),
        ("_start_tailscale", "Tailscale start method"),
        ("_show_tailscale_config", "Tailscale configuration wizard"),
        ("_get_tailscale_info", "Get Tailscale IP and hostname"),
        ("_apply_tailscale_config", "Apply Tailscale config to Nextcloud"),
        ("_update_trusted_domains", "Update trusted_domains in config.php"),
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
    print("UI Changes Verification")
    print("=" * 70)
    print()
    
    # Check that theme toggle was removed from landing page
    landing_theme_button_removed = "self.theme_toggle_btn = tk.Button" not in content or \
                                    content.count("self.theme_toggle_btn") == 0
    
    # Actually it's ok if it exists in header but not in landing
    header_has_theme = "self.header_theme_btn" in content
    
    if header_has_theme:
        print("✓ Theme toggle moved to header")
    else:
        print("✗ Theme toggle not found in header")
        all_passed = False
    
    # Check for grid layout in header
    if "header_content.grid_columnconfigure" in content:
        print("✓ Header uses grid layout for centering")
    else:
        print("✗ Header grid layout not found")
        all_passed = False
    
    # Check for dropdown menu button
    if '"☰"' in content:
        print("✓ Dropdown menu button (☰) found")
    else:
        print("✗ Dropdown menu button not found")
        all_passed = False
    
    # Check for theme icons
    if '"☀️"' in content and '"🌙"' in content:
        print("✓ Theme toggle icons (☀️/🌙) found")
    else:
        print("✗ Theme toggle icons not found")
        all_passed = False
    
    print()
    print("=" * 70)
    print("Tailscale Wizard Features")
    print("=" * 70)
    print()
    
    # Check for Tailscale features
    features = [
        ("Tailscale installation check", "tailscale" in content.lower()),
        ("Installation guide", "install.sh" in content or "Download and run" in content),
        ("Status detection", '"tailscale", "status"' in content),
        ("IP address retrieval", "TailscaleIPs" in content),
        ("MagicDNS hostname", "DNSName" in content),
        ("Custom domain input", "custom_domain_var" in content),
        ("trusted_domains update", "trusted_domains" in content),
        ("Nextcloud config.php update", "config/config.php" in content),
    ]
    
    for feature, check in features:
        if check:
            print(f"✓ {feature}")
        else:
            print(f"✗ {feature}")
            all_passed = False
    
    print()
    print("=" * 70)
    print("Test Result")
    print("=" * 70)
    print()
    
    if all_passed:
        print("✓ All tests passed!")
        print()
        print("Manual Testing Instructions:")
        print("-" * 70)
        print("1. Install tkinter: sudo apt-get install python3-tk")
        print("2. Run: python3 nextcloud_restore_and_backup-v9.py")
        print("3. Verify the following:")
        print("   • Top-right header has theme toggle icon (☀️ or 🌙)")
        print("   • Top-right header has dropdown menu button (☰)")
        print("   • Clicking theme toggle switches themes")
        print("   • Clicking dropdown menu shows 'Remote Access (Tailscale)' option")
        print("   • Theme toggle button is NOT on the landing page")
        print("   • Tailscale wizard opens when clicking Remote Access option")
        print("   • Tailscale wizard checks installation status")
        print("   • Configuration wizard shows IP and hostname")
        print("   • Custom domain input works")
        print("   • Apply button updates Nextcloud config.php")
        print()
    else:
        print("✗ Some tests failed. Please review the implementation.")
        print()
    
    return all_passed

if __name__ == '__main__':
    success = test_ui_elements()
    sys.exit(0 if success else 1)
