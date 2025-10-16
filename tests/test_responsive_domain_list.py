#!/usr/bin/env python3
"""
Test script for responsive domain list in Configure Remote Access page.
This validates that:
1. Domain list is always visible with scrolling
2. "No trusted domains" message displays when list is empty
3. Layout is responsive to window size
4. Canvas expands properly with content
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_responsive_domain_list():
    """Test that responsive domain list features are properly implemented"""
    print("=" * 80)
    print("Responsive Domain List Test")
    print("=" * 80)
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
    
    # Check for empty domain list handling
    print("\n" + "=" * 80)
    print("Empty Domain List Handling")
    print("=" * 80)
    print()
    
    empty_checks = [
        ("No trusted domains configured", "Empty domains message"),
        ("if not current_domains:", "Empty list condition check"),
        ("no_domains_frame", "Empty domains frame"),
    ]
    
    all_passed = True
    for check_str, description in empty_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for responsive layout in domain list
    print("\n" + "=" * 80)
    print("Responsive Domain List Layout")
    print("=" * 80)
    print()
    
    responsive_checks = [
        ('expand=True, padx=20', "Domain list container expandable"),
        ("fill=\"both\", expand=True", "Responsive fill and expand"),
        ("configure_scroll_region", "Scroll region configuration"),
        ("canvas.itemconfig(canvas_window, width=canvas_width)", "Dynamic canvas width adjustment"),
    ]
    
    for check_str, description in responsive_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check for responsive main content frame
    print("\n" + "=" * 80)
    print("Responsive Main Content Frame")
    print("=" * 80)
    print()
    
    main_frame_checks = [
        ("Create scrollable content frame for responsive layout", "Scrollable content frame comment"),
        ("canvas = tk.Canvas(self.body_frame", "Main canvas creation"),
        ("scrollbar = tk.Scrollbar(self.body_frame", "Main scrollbar creation"),
        ('canvas.pack(side="left", fill="both", expand=True)', "Main canvas responsive packing"),
        ("configure_canvas", "Canvas configuration function"),
    ]
    
    for check_str, description in main_frame_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Check that fixed width .place() is removed from _show_tailscale_config
    print("\n" + "=" * 80)
    print("Fixed Width Removal from _show_tailscale_config")
    print("=" * 80)
    print()
    
    # Check if old fixed width code still exists in _show_tailscale_config method
    start_idx = content.find('def _show_tailscale_config')
    end_idx = content.find('def _display_current_trusted_domains')
    if start_idx != -1 and end_idx != -1:
        section = content[start_idx:end_idx]
        if 'content.place(relx=0.5, anchor="n", y=10)' in section:
            print("✗ Old fixed width .place() still exists in _show_tailscale_config")
            all_passed = False
        else:
            print("✓ Old fixed width .place() removed from _show_tailscale_config")
        
        if 'def maintain_width(event=None):' in section:
            print("✗ Old maintain_width function still exists in _show_tailscale_config")
            all_passed = False
        else:
            print("✓ Old maintain_width function removed from _show_tailscale_config")
    else:
        print("✗ Could not find _show_tailscale_config method")
        all_passed = False
    
    # Check for proper canvas scrolling implementation
    print("\n" + "=" * 80)
    print("Canvas Scrolling Implementation")
    print("=" * 80)
    print()
    
    scrolling_checks = [
        ("canvas.configure(scrollregion=canvas.bbox(\"all\"))", "Scroll region update"),
        ("canvas.bind(\"<Configure>\", configure", "Canvas configure binding"),
        ("content.bind(\"<Configure>\", configure", "Content configure binding"),
    ]
    
    for check_str, description in scrolling_checks:
        if check_str in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description} - NOT FOUND")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Result")
    print("=" * 80)
    print()
    
    if all_passed:
        print("✓ All responsive domain list features are implemented!")
        return True
    else:
        print("✗ Some features are missing. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = test_responsive_domain_list()
    sys.exit(0 if success else 1)
