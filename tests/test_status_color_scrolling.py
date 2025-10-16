#!/usr/bin/env python3
"""
Test script to verify:
1. Status text color changed to yellow (#FFD700)
2. Mouse wheel scrolling implemented in show_schedule_backup
"""

import re


def test_status_text_color():
    """Test that status text colors are yellow (#FFD700)."""
    
    print("=" * 70)
    print("TEST 1: Status Text Color Changes")
    print("=" * 70)
    print()
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    checks = []
    
    # Check 1: First status text - "Running test backup via Task Scheduler... Please wait..."
    pattern1 = r'text="⏳ Running test backup via Task Scheduler\.\.\. Please wait\.\.\.",\s*fg="#FFD700"'
    if re.search(pattern1, content):
        print("✓ Check 1: First status text color is yellow (#FFD700)")
        checks.append(True)
    else:
        print("✗ Check 1: First status text color is NOT yellow")
        checks.append(False)
    
    # Check 2: Second status text - "Running test backup... Please wait..."
    pattern2 = r'text="⏳ Running test backup\.\.\. Please wait\.\.\.",\s*fg="#FFD700"'
    if re.search(pattern2, content):
        print("✓ Check 2: Second status text color is yellow (#FFD700)")
        checks.append(True)
    else:
        print("✗ Check 2: Second status text color is NOT yellow")
        checks.append(False)
    
    print()
    print(f"Results: {sum(checks)}/{len(checks)} checks passed")
    print("=" * 70)
    print()
    
    return all(checks)


def test_mouse_wheel_scrolling():
    """Test that mouse wheel scrolling is implemented."""
    
    print("=" * 70)
    print("TEST 2: Mouse Wheel Scrolling Implementation")
    print("=" * 70)
    print()
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find show_schedule_backup method
    method_start = content.find('def show_schedule_backup(self):')
    if method_start == -1:
        print("✗ ERROR: show_schedule_backup method not found")
        return False
    
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    checks = []
    
    # Check 1: Canvas created
    if 'canvas = tk.Canvas(frame, bg=self.theme_colors' in method_content and 'highlightthickness=0' in method_content:
        print("✓ Check 1: Canvas created with proper styling")
        checks.append(True)
    else:
        print("✗ Check 1: Canvas not properly created")
        checks.append(False)
    
    # Check 2: Scrollbar created
    if 'scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)' in method_content:
        print("✓ Check 2: Scrollbar created with vertical orientation")
        checks.append(True)
    else:
        print("✗ Check 2: Scrollbar not properly configured")
        checks.append(False)
    
    # Check 3: Scrollable frame created
    if 'scrollable_frame = tk.Frame(canvas, bg=self.theme_colors' in method_content:
        print("✓ Check 3: Scrollable frame created")
        checks.append(True)
    else:
        print("✗ Check 3: Scrollable frame not created")
        checks.append(False)
    
    # Check 4: Canvas window created
    if 'canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")' in method_content:
        print("✓ Check 4: Canvas window created with scrollable_frame")
        checks.append(True)
    else:
        print("✗ Check 4: Canvas window not properly created")
        checks.append(False)
    
    # Check 5: configure_scroll function defined
    if 'def configure_scroll(event=None):' in method_content:
        print("✓ Check 5: configure_scroll function defined")
        checks.append(True)
    else:
        print("✗ Check 5: configure_scroll function not defined")
        checks.append(False)
    
    # Check 6: on_mouse_wheel function defined
    if 'def on_mouse_wheel(event):' in method_content:
        print("✓ Check 6: on_mouse_wheel function defined")
        checks.append(True)
    else:
        print("✗ Check 6: on_mouse_wheel function not defined")
        checks.append(False)
    
    # Check 7: Windows/Mac mouse wheel binding
    if 'canvas.bind_all("<MouseWheel>", on_mouse_wheel)' in method_content:
        print("✓ Check 7: Windows/Mac mouse wheel binding configured")
        checks.append(True)
    else:
        print("✗ Check 7: Windows/Mac mouse wheel binding not configured")
        checks.append(False)
    
    # Check 8: Linux scroll up binding
    if 'canvas.bind_all("<Button-4>", on_mouse_wheel)' in method_content:
        print("✓ Check 8: Linux scroll up binding configured")
        checks.append(True)
    else:
        print("✗ Check 8: Linux scroll up binding not configured")
        checks.append(False)
    
    # Check 9: Linux scroll down binding
    if 'canvas.bind_all("<Button-5>", on_mouse_wheel)' in method_content:
        print("✓ Check 9: Linux scroll down binding configured")
        checks.append(True)
    else:
        print("✗ Check 9: Linux scroll down binding not configured")
        checks.append(False)
    
    # Check 10: Status section uses scrollable_frame
    if 'status_frame = tk.Frame(scrollable_frame, bg=self.theme_colors' in method_content:
        print("✓ Check 10: Status section wrapped in scrollable_frame")
        checks.append(True)
    else:
        print("✗ Check 10: Status section not in scrollable_frame")
        checks.append(False)
    
    # Check 11: Config section uses scrollable_frame
    if 'config_frame = tk.Frame(scrollable_frame, bg=self.theme_colors' in method_content:
        print("✓ Check 11: Config section wrapped in scrollable_frame")
        checks.append(True)
    else:
        print("✗ Check 11: Config section not in scrollable_frame")
        checks.append(False)
    
    # Check 12: Title is outside scrollable area
    title_pos = method_content.find('text="Schedule Automatic Backups"')
    canvas_pos = method_content.find('canvas = tk.Canvas(')
    if title_pos > 0 and canvas_pos > 0 and title_pos < canvas_pos:
        print("✓ Check 12: Title positioned outside scrollable area")
        checks.append(True)
    else:
        print("✗ Check 12: Title positioning needs verification")
        checks.append(False)
    
    print()
    print(f"Results: {sum(checks)}/{len(checks)} checks passed")
    print("=" * 70)
    print()
    
    return all(checks)


if __name__ == "__main__":
    test1_pass = test_status_text_color()
    test2_pass = test_mouse_wheel_scrolling()
    
    print("=" * 70)
    print("OVERALL RESULTS")
    print("=" * 70)
    print()
    
    if test1_pass and test2_pass:
        print("✅ All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed")
        exit(1)
