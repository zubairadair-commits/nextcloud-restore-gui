#!/usr/bin/env python3
"""
Test script to validate the scrollable Schedule Backup Configuration page implementation.
This test verifies that:
1. Canvas and Scrollbar are properly created
2. Mouse wheel scrolling is configured for Windows/Mac/Linux
3. All content sections are wrapped in scrollable_frame
4. The configure_scroll function properly updates the scroll region
"""

import re
import os


def test_scheduled_backup_scrolling():
    """Test that the scheduled backup UI has proper scrolling implementation."""
    
    print("=" * 70)
    print("Testing Schedule Backup Configuration Scrolling Implementation")
    print("=" * 70)
    print()
    
    file_path = "/home/runner/work/nextcloud-restore-gui/nextcloud-restore-gui/demo_scheduled_backup_ui.py"
    
    if not os.path.exists(file_path):
        print(f"✗ ERROR: File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: Canvas and Scrollbar created
    if 'canvas = tk.Canvas(' in content and 'bg="#f0f0f0"' in content and 'highlightthickness=0' in content:
        print("✓ Check 1: Canvas created with proper styling")
        checks.append(True)
    else:
        print("✗ Check 1: Canvas not properly created")
        checks.append(False)
    
    # Check 2: Scrollbar created with proper orientation
    if 'scrollbar = tk.Scrollbar(' in content and 'orient="vertical"' in content and 'command=canvas.yview' in content:
        print("✓ Check 2: Scrollbar created with vertical orientation")
        checks.append(True)
    else:
        print("✗ Check 2: Scrollbar not properly configured")
        checks.append(False)
    
    # Check 3: Scrollable frame created
    if 'scrollable_frame = tk.Frame(canvas' in content and 'bg="#f0f0f0"' in content:
        print("✓ Check 3: Scrollable frame created")
        checks.append(True)
    else:
        print("✗ Check 3: Scrollable frame not created")
        checks.append(False)
    
    # Check 4: Canvas yview configured
    if 'canvas.configure(yscrollcommand=scrollbar.set)' in content:
        print("✓ Check 4: Canvas yscrollcommand configured")
        checks.append(True)
    else:
        print("✗ Check 4: Canvas yscrollcommand not configured")
        checks.append(False)
    
    # Check 5: Canvas window created
    if 'canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")' in content:
        print("✓ Check 5: Canvas window created with scrollable_frame")
        checks.append(True)
    else:
        print("✗ Check 5: Canvas window not properly created")
        checks.append(False)
    
    # Check 6: Configure scroll function exists
    if 'def configure_scroll(event=None):' in content:
        print("✓ Check 6: configure_scroll function defined")
        checks.append(True)
    else:
        print("✗ Check 6: configure_scroll function not found")
        checks.append(False)
    
    # Check 7: Scroll region configuration
    if 'canvas.configure(scrollregion=canvas.bbox("all"))' in content:
        print("✓ Check 7: Scroll region properly configured")
        checks.append(True)
    else:
        print("✗ Check 7: Scroll region not configured")
        checks.append(False)
    
    # Check 8: Width adjustment for scrollable_frame
    if 'canvas.itemconfig(canvas_window, width=canvas_width)' in content:
        print("✓ Check 8: Scrollable frame width dynamically adjusted")
        checks.append(True)
    else:
        print("✗ Check 8: Width adjustment not implemented")
        checks.append(False)
    
    # Check 9: Mouse wheel scrolling function
    if 'def on_mouse_wheel(event):' in content:
        print("✓ Check 9: Mouse wheel scrolling function defined")
        checks.append(True)
    else:
        print("✗ Check 9: Mouse wheel scrolling function not found")
        checks.append(False)
    
    # Check 10: Windows/Mac mouse wheel binding
    if 'canvas.bind_all("<MouseWheel>", on_mouse_wheel)' in content:
        print("✓ Check 10: Windows/Mac mouse wheel binding configured")
        checks.append(True)
    else:
        print("✗ Check 10: Windows/Mac mouse wheel binding missing")
        checks.append(False)
    
    # Check 11: Linux scroll up binding
    if 'canvas.bind_all("<Button-4>", on_mouse_wheel)' in content:
        print("✓ Check 11: Linux scroll up binding configured")
        checks.append(True)
    else:
        print("✗ Check 11: Linux scroll up binding missing")
        checks.append(False)
    
    # Check 12: Linux scroll down binding
    if 'canvas.bind_all("<Button-5>", on_mouse_wheel)' in content:
        print("✓ Check 12: Linux scroll down binding configured")
        checks.append(True)
    else:
        print("✗ Check 12: Linux scroll down binding missing")
        checks.append(False)
    
    # Check 13: Proper delta handling for Windows/Mac
    if 'event.delta' in content and 'canvas.yview_scroll' in content:
        print("✓ Check 13: Windows/Mac delta handling implemented")
        checks.append(True)
    else:
        print("✗ Check 13: Windows/Mac delta handling missing")
        checks.append(False)
    
    # Check 14: Linux event.num handling
    if 'event.num == 5' in content and 'event.num == 4' in content:
        print("✓ Check 14: Linux event.num handling implemented")
        checks.append(True)
    else:
        print("✗ Check 14: Linux event.num handling missing")
        checks.append(False)
    
    # Check 15: Content sections use scrollable_frame
    if 'self.create_status_section(scrollable_frame)' in content:
        print("✓ Check 15: Status section wrapped in scrollable_frame")
        checks.append(True)
    else:
        print("✗ Check 15: Status section not in scrollable_frame")
        checks.append(False)
    
    # Check 16: Config section uses scrollable_frame
    if 'self.create_config_section(scrollable_frame)' in content:
        print("✓ Check 16: Config section wrapped in scrollable_frame")
        checks.append(True)
    else:
        print("✗ Check 16: Config section not in scrollable_frame")
        checks.append(False)
    
    # Check 17: Setup guide uses scrollable_frame
    if 'self.create_setup_guide(scrollable_frame)' in content:
        print("✓ Check 17: Setup guide wrapped in scrollable_frame")
        checks.append(True)
    else:
        print("✗ Check 17: Setup guide not in scrollable_frame")
        checks.append(False)
    
    # Check 18: Title remains outside scrollable area (better UX)
    init_pattern = r'def __init__\(self\):(.*?)def create_status_section'
    init_match = re.search(init_pattern, content, re.DOTALL)
    if init_match:
        init_content = init_match.group(1)
        # Title should be created before scrollable_frame
        title_pos = init_content.find('text="Schedule Backup Configuration"')
        scrollable_pos = init_content.find('scrollable_frame = tk.Frame(canvas')
        if title_pos > 0 and scrollable_pos > 0 and title_pos < scrollable_pos:
            print("✓ Check 18: Title positioned outside scrollable area")
            checks.append(True)
        else:
            print("✗ Check 18: Title positioning needs verification")
            checks.append(False)
    else:
        print("✗ Check 18: Could not verify title positioning")
        checks.append(False)
    
    # Check 19: Scrollbar packed before canvas
    if 'scrollbar.pack(side="right", fill="y")' in content and 'canvas.pack(side="left", fill="both", expand=True)' in content:
        print("✓ Check 19: Scrollbar and canvas properly packed")
        checks.append(True)
    else:
        print("✗ Check 19: Scrollbar/canvas packing incorrect")
        checks.append(False)
    
    # Check 20: Event bindings configured
    if 'scrollable_frame.bind("<Configure>", configure_scroll)' in content and 'canvas.bind("<Configure>", configure_scroll)' in content:
        print("✓ Check 20: Configure event bindings set up")
        checks.append(True)
    else:
        print("✗ Check 20: Configure event bindings missing")
        checks.append(False)
    
    print()
    print("=" * 70)
    print(f"Results: {sum(checks)}/{len(checks)} checks passed")
    print("=" * 70)
    
    if all(checks):
        print()
        print("✅ All checks passed! The scrollable implementation is correct.")
        print()
        print("Features implemented:")
        print("  • Canvas + Scrollbar wrapper for config section")
        print("  • Mouse wheel scrolling for Windows (event.delta)")
        print("  • Mouse wheel scrolling for Linux (Button-4, Button-5)")
        print("  • Dynamic width adjustment")
        print("  • All content sections wrapped in scrollable area")
        print("  • Title kept outside scroll for better UX")
        return True
    else:
        print()
        print(f"⚠️  Some checks failed. {len(checks) - sum(checks)} issues found.")
        return False


if __name__ == "__main__":
    success = test_scheduled_backup_scrolling()
    exit(0 if success else 1)
