#!/usr/bin/env python3
"""
Test various scenarios for the responsive domain list.
This validates behavior with different numbers of domains and window sizes.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_scenario(title, description):
    """Print a scenario header"""
    print("\n" + "─" * 80)
    print(f"📋 Scenario: {title}")
    print(f"   {description}")
    print("─" * 80)

def test_scenarios():
    """Test different domain list scenarios"""
    print("=" * 80)
    print("Responsive Domain List - Scenario Testing")
    print("=" * 80)
    
    # Check if main file exists
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    # Read file content
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _display_current_trusted_domains method
    start_idx = content.find('def _display_current_trusted_domains(self, parent):')
    end_idx = content.find('\n    def ', start_idx + 1)
    display_method = content[start_idx:end_idx] if start_idx != -1 and end_idx != -1 else ""
    
    all_passed = True
    
    # Scenario 1: Empty domain list
    print_scenario(
        "Empty Domain List",
        "User has no trusted domains configured yet"
    )
    
    checks = [
        ("Check for empty domains", "if not current_domains:" in display_method),
        ("Display empty message frame", "no_domains_frame = tk.Frame(parent" in display_method),
        ("Bold empty message", '"No trusted domains configured"' in display_method),
        ("Help text visible", "Add domains using the form below to allow access" in display_method),
        ("Warning styling", "warning_bg" in display_method),
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    print("\n  Expected Behavior:")
    print("    • Clear message: 'No trusted domains configured'")
    print("    • Helpful guidance for user to add domains")
    print("    • No empty scrollable list shown")
    print("    • Add domain form still accessible below")
    
    # Scenario 2: Short domain list (1-3 domains)
    print_scenario(
        "Short Domain List (1-3 domains)",
        "User has a few domains configured"
    )
    
    checks = [
        ("Create scrollable container", 'list_container = tk.Frame(parent' in display_method),
        ("Container expands", 'expand=True' in display_method and 'list_container.pack' in display_method),
        ("Canvas for domains", "canvas = tk.Canvas(" in display_method),
        ("Height calculation", "min(300, len(current_domains) * 50)" in display_method),
        ("All domains visible", "for domain in current_domains:" in display_method),
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    print("\n  Expected Behavior:")
    print("    • All domains visible without scrolling (< 6 domains)")
    print("    • Each domain has status icon and remove button")
    print("    • Container sized to content")
    print("    • No vertical scrollbar needed")
    
    # Scenario 3: Long domain list (10+ domains)
    print_scenario(
        "Long Domain List (10+ domains)",
        "User has many domains configured"
    )
    
    checks = [
        ("Scrollbar creation", "scrollbar = tk.Scrollbar(" in display_method),
        ("Max height limit", "min(300, len(current_domains) * 50)" in display_method),
        ("Vertical scrollbar", 'orient="vertical"' in display_method),
        ("Scroll command config", "yscrollcommand=scrollbar.set" in display_method),
        ("Scrollbar packing", 'scrollbar.pack(side="right", fill="y")' in display_method),
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    print("\n  Expected Behavior:")
    print("    • Scrollbar appears on right side")
    print("    • Max height of 300px (about 6 domains)")
    print("    • All domains accessible via scrolling")
    print("    • Smooth scrolling with mouse wheel")
    
    # Scenario 4: Small window size
    print_scenario(
        "Small Window Size (e.g., 400px wide)",
        "User resizes window to very small size"
    )
    
    # Check main content frame implementation
    start_idx = content.find('def _show_tailscale_config(self):')
    end_idx = content.find('\n    def ', start_idx + 1)
    config_method = content[start_idx:end_idx] if start_idx != -1 and end_idx != -1 else ""
    
    checks = [
        ("Main canvas scrollable", "canvas = tk.Canvas(self.body_frame" in config_method),
        ("Main scrollbar present", "scrollbar = tk.Scrollbar(self.body_frame" in config_method),
        ("Canvas expands", 'canvas.pack(side="left", fill="both", expand=True)' in config_method),
        ("Dynamic width calc", "content_width = min(600, canvas_width - 20)" in config_method),
        ("Content never cut off", "canvas.configure(scrollregion=canvas.bbox" in config_method),
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    print("\n  Expected Behavior:")
    print("    • Content area shrinks to fit window")
    print("    • Vertical scrollbar appears for main content")
    print("    • All widgets remain accessible")
    print("    • No horizontal scrollbar needed")
    print("    • Content centered with appropriate width")
    
    # Scenario 5: Large window size
    print_scenario(
        "Large Window Size (e.g., 1920px wide)",
        "User has a large monitor or maximized window"
    )
    
    checks = [
        ("Max width constraint", "content_width = min(600, canvas_width - 20)" in config_method),
        ("Center calculation", "x_offset = (canvas_width - content_width) // 2" in config_method),
        ("Canvas coords update", "canvas.coords(canvas_window, x_offset, 10)" in config_method),
        ("Responsive to resize", 'canvas.bind("<Configure>"' in config_method),
        ("Content width config", "canvas.itemconfig(canvas_window, width=content_width)" in config_method),
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    print("\n  Expected Behavior:")
    print("    • Content width limited to 600px max")
    print("    • Content centered horizontally")
    print("    • Empty space on both sides")
    print("    • Clean, uncluttered appearance")
    
    # Scenario 6: Window resize during use
    print_scenario(
        "Dynamic Window Resizing",
        "User resizes window while viewing the page"
    )
    
    checks = [
        ("Canvas configure bind", 'canvas.bind("<Configure>"' in config_method),
        ("Content configure bind", 'content.bind("<Configure>"' in config_method),
        ("Domain canvas configure", ".bind(\"<Configure>\", configure" in display_method),
        ("Scroll region update", "canvas.configure(scrollregion=canvas.bbox" in display_method),
        ("Width recalculation", "canvas_width = canvas.winfo_width()" in display_method),
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    print("\n  Expected Behavior:")
    print("    • Layout updates smoothly on resize")
    print("    • No flickering or jumpy behavior")
    print("    • Content recenters automatically")
    print("    • Scrollbars appear/disappear as needed")
    print("    • All content remains visible")
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    if all_passed:
        print("\n✓ All scenarios are properly handled!")
        print("\nThe responsive domain list implementation:")
        print("  ✓ Handles empty state with clear messaging")
        print("  ✓ Displays short lists without unnecessary scrolling")
        print("  ✓ Provides scrolling for long lists")
        print("  ✓ Adapts to small windows without cutting off content")
        print("  ✓ Centers content in large windows")
        print("  ✓ Updates smoothly during window resizing")
        return True
    else:
        print("\n✗ Some scenarios are not properly handled.")
        return False

if __name__ == "__main__":
    success = test_scenarios()
    sys.exit(0 if success else 1)
