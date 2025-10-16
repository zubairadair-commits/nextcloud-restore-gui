#!/usr/bin/env python3
"""
Test script to verify the Remote Access Setup (Tailscale) centering fix.
Validates that the container frame approach is properly implemented.
"""

import sys
import os
import re

def test_tailscale_centering():
    """Test that Tailscale pages use container frame for proper centering"""
    print("=" * 70)
    print("Remote Access Setup (Tailscale) Centering Fix Verification")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
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
    
    # Check 1: Container frame is created
    if 'container = tk.Frame(self.body_frame' in method_content:
        print("✓ Check 1: Container frame created")
        checks.append(True)
    else:
        print("✗ Check 1: Container frame NOT found")
        checks.append(False)
    
    # Check 2: Container frame is packed
    if 'container.pack(fill="both", expand=True)' in method_content:
        print("✓ Check 2: Container frame packed correctly")
        checks.append(True)
    else:
        print("✗ Check 2: Container frame NOT packed correctly")
        checks.append(False)
    
    # Check 3: Canvas is child of container
    if 'canvas = tk.Canvas(container' in method_content:
        print("✓ Check 3: Canvas created in container (not body_frame)")
        checks.append(True)
    else:
        print("✗ Check 3: Canvas NOT created in container")
        checks.append(False)
    
    # Check 4: Scrollbar is child of container
    if 'scrollbar = ttk.Scrollbar(container' in method_content:
        print("✓ Check 4: Scrollbar created in container (not body_frame)")
        checks.append(True)
    else:
        print("✗ Check 4: Scrollbar NOT created in container")
        checks.append(False)
    
    # Check 5: Scrollable frame has fixed width
    if 'scrollable_frame = tk.Frame(canvas, bg=self.theme_colors[\'bg\'], width=700)' in method_content:
        print("✓ Check 5: Scrollable frame has fixed width (700px)")
        checks.append(True)
    else:
        print("✗ Check 5: Scrollable frame does NOT have fixed width")
        checks.append(False)
    
    # Check 6: Content frame still has 600px width
    if 'content = tk.Frame(scrollable_frame, bg=self.theme_colors[\'bg\'], width=600)' in method_content:
        print("✓ Check 6: Content frame maintains 600px width")
        checks.append(True)
    else:
        print("✗ Check 6: Content frame width changed or missing")
        checks.append(False)
    
    # Check 7: Comments explain the container frame purpose
    if 'container frame' in method_content.lower() and 'centering context' in method_content.lower():
        print("✓ Check 7: Explanatory comments present")
        checks.append(True)
    else:
        print("✗ Check 7: Missing explanatory comments")
        checks.append(False)
    
    print()
    print("=" * 70)
    
    # Now check _show_tailscale_config method
    config_pattern = r'def _show_tailscale_config\(self\):(.*?)(?=\n    def |\Z)'
    config_match = re.search(config_pattern, content, re.DOTALL)
    
    if not config_match:
        print("✗ Could not find _show_tailscale_config method")
        return False
    
    config_content = config_match.group(1)
    
    print("Checking _show_tailscale_config method...")
    print()
    
    # Same checks for config method
    if 'container = tk.Frame(self.body_frame' in config_content:
        print("✓ Check 8: Container frame created in config method")
        checks.append(True)
    else:
        print("✗ Check 8: Container frame NOT found in config method")
        checks.append(False)
    
    if 'canvas = tk.Canvas(container' in config_content:
        print("✓ Check 9: Canvas created in container in config method")
        checks.append(True)
    else:
        print("✗ Check 9: Canvas NOT created in container in config method")
        checks.append(False)
    
    if 'scrollable_frame = tk.Frame(canvas, bg=self.theme_colors[\'bg\'], width=700)' in config_content:
        print("✓ Check 10: Scrollable frame has fixed width in config method")
        checks.append(True)
    else:
        print("✗ Check 10: Scrollable frame does NOT have fixed width in config method")
        checks.append(False)
    
    print()
    print("=" * 70)
    print(f"Results: {sum(checks)}/{len(checks)} checks passed")
    print("=" * 70)
    
    if all(checks):
        print("\n✅ All checks passed! The centering fix is properly implemented.")
        return True
    else:
        print(f"\n⚠️  Some checks failed. {len(checks) - sum(checks)} issues found.")
        return False

if __name__ == "__main__":
    success = test_tailscale_centering()
    sys.exit(0 if success else 1)
