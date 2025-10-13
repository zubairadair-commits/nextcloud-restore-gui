#!/usr/bin/env python3
"""
Verification script to confirm debug labels have been removed from Tailscale setup screens.
"""

import sys
import os

def verify_debug_label_removal():
    """Verify that debug labels are removed from both Tailscale functions"""
    print("=" * 70)
    print("Debug Label Removal Verification")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for debug label text
    debug_label_found = '🔍 DEBUG: Content Frame Rendered' in content
    
    # Check for debug label styling
    debug_styling_found = 'bg="#FFD700"' in content and 'DEBUG: Content Frame Rendered' in content
    
    # Check that functions still exist
    wizard_exists = 'def show_tailscale_wizard(self):' in content
    config_exists = 'def _show_tailscale_config(self):' in content
    
    print("Verification Results:")
    print("-" * 70)
    
    if not debug_label_found:
        print("✓ Debug label text NOT found in code (correctly removed)")
    else:
        print("✗ Debug label text still present in code")
    
    if not debug_styling_found:
        print("✓ Debug label styling NOT found in code (correctly removed)")
    else:
        print("✗ Debug label styling still present in code")
    
    if wizard_exists:
        print("✓ show_tailscale_wizard() function exists")
    else:
        print("✗ show_tailscale_wizard() function not found")
    
    if config_exists:
        print("✓ _show_tailscale_config() function exists")
    else:
        print("✗ _show_tailscale_config() function not found")
    
    print()
    print("=" * 70)
    
    if not debug_label_found and not debug_styling_found and wizard_exists and config_exists:
        print("✅ SUCCESS: Debug labels have been successfully removed!")
        print()
        print("Summary:")
        print("  • Debug label text removed from both functions")
        print("  • Debug label styling removed from both functions")
        print("  • Tailscale wizard functions remain intact")
        print("  • No yellow debug banner will be shown to users")
        return True
    else:
        print("❌ FAILED: Some issues detected")
        return False

if __name__ == "__main__":
    success = verify_debug_label_removal()
    sys.exit(0 if success else 1)
