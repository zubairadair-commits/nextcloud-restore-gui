#!/usr/bin/env python3
"""
Test script to validate the main application file has:
1. Status text color changed to yellow (#FFD700)
2. Mouse wheel scrolling in show_schedule_backup method
"""

import re
import os


def test_main_app_scrolling():
    """Test that the main application has proper scrolling implementation."""
    
    print("=" * 70)
    print("Testing Main Application - Scrolling & Status Color")
    print("=" * 70)
    print()
    
    file_path = "../src/nextcloud_restore_and_backup-v9.py"
    
    if not os.path.exists(file_path):
        print(f"✗ ERROR: File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
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
    
    print("STATUS TEXT COLOR CHECKS:")
    print("-" * 70)
    
    # Check 1: First status text color
    if 'text="⏳ Running test backup via Task Scheduler... Please wait..."' in content and 'fg="#FFD700"' in content:
        # Verify they're close together (within 100 chars)
        idx = content.find('text="⏳ Running test backup via Task Scheduler... Please wait..."')
        if idx > 0:
            snippet = content[idx:idx+200]
            if 'fg="#FFD700"' in snippet:
                print("✓ Check 1: First status text uses yellow (#FFD700)")
                checks.append(True)
            else:
                print("✗ Check 1: First status text color not yellow")
                checks.append(False)
        else:
            print("✗ Check 1: First status text not found")
            checks.append(False)
    else:
        print("✗ Check 1: First status text or yellow color not found")
        checks.append(False)
    
    # Check 2: Second status text color
    pattern = r'text="⏳ Running test backup\.\.\. Please wait\.\.\.",\s*fg="#FFD700"'
    if re.search(pattern, content):
        print("✓ Check 2: Second status text uses yellow (#FFD700)")
        checks.append(True)
    else:
        print("✗ Check 2: Second status text color not yellow")
        checks.append(False)
    
    print()
    print("SCROLLING IMPLEMENTATION CHECKS:")
    print("-" * 70)
    
    # Check 3: Canvas created
    if 'canvas = tk.Canvas(frame, bg=self.theme_colors' in method_content and 'highlightthickness=0' in method_content:
        print("✓ Check 3: Canvas created with proper styling")
        checks.append(True)
    else:
        print("✗ Check 3: Canvas not properly created")
        checks.append(False)
    
    # Check 4: Scrollbar created
    if 'scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)' in method_content:
        print("✓ Check 4: Scrollbar created")
        checks.append(True)
    else:
        print("✗ Check 4: Scrollbar not created")
        checks.append(False)
    
    # Check 5: Scrollable frame created
    if 'scrollable_frame = tk.Frame(canvas, bg=self.theme_colors' in method_content:
        print("✓ Check 5: Scrollable frame created")
        checks.append(True)
    else:
        print("✗ Check 5: Scrollable frame not created")
        checks.append(False)
    
    # Check 6: Canvas window created
    if 'canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")' in method_content:
        print("✓ Check 6: Canvas window created")
        checks.append(True)
    else:
        print("✗ Check 6: Canvas window not created")
        checks.append(False)
    
    # Check 7: configure_scroll function
    if 'def configure_scroll(event=None):' in method_content:
        print("✓ Check 7: configure_scroll function defined")
        checks.append(True)
    else:
        print("✗ Check 7: configure_scroll not defined")
        checks.append(False)
    
    # Check 8: on_mouse_wheel function
    if 'def on_mouse_wheel(event):' in method_content:
        print("✓ Check 8: on_mouse_wheel function defined")
        checks.append(True)
    else:
        print("✗ Check 8: on_mouse_wheel not defined")
        checks.append(False)
    
    # Check 9: Mouse wheel bindings
    if 'canvas.bind_all("<MouseWheel>", on_mouse_wheel)' in method_content:
        print("✓ Check 9: Windows/Mac mouse wheel binding")
        checks.append(True)
    else:
        print("✗ Check 9: Windows/Mac binding missing")
        checks.append(False)
    
    # Check 10: Linux bindings
    if 'canvas.bind_all("<Button-4>", on_mouse_wheel)' in method_content and 'canvas.bind_all("<Button-5>", on_mouse_wheel)' in method_content:
        print("✓ Check 10: Linux scroll bindings")
        checks.append(True)
    else:
        print("✗ Check 10: Linux bindings missing")
        checks.append(False)
    
    # Check 11: Status frame uses scrollable_frame
    if 'status_frame = tk.Frame(scrollable_frame' in method_content:
        print("✓ Check 11: Status section in scrollable_frame")
        checks.append(True)
    else:
        print("✗ Check 11: Status section not scrollable")
        checks.append(False)
    
    # Check 12: Config frame uses scrollable_frame
    if 'config_frame = tk.Frame(scrollable_frame' in method_content:
        print("✓ Check 12: Config section in scrollable_frame")
        checks.append(True)
    else:
        print("✗ Check 12: Config section not scrollable")
        checks.append(False)
    
    # Check 13: Title outside scrollable area
    title_pos = method_content.find('text="Schedule Automatic Backups"')
    canvas_pos = method_content.find('canvas = tk.Canvas(')
    if title_pos > 0 and canvas_pos > 0 and title_pos < canvas_pos:
        print("✓ Check 13: Title outside scrollable area")
        checks.append(True)
    else:
        print("✗ Check 13: Title positioning incorrect")
        checks.append(False)
    
    print()
    print("=" * 70)
    print(f"Results: {sum(checks)}/{len(checks)} checks passed")
    print("=" * 70)
    print()
    
    if all(checks):
        print("✅ All checks passed!")
        return True
    else:
        print("❌ Some checks failed")
        return False


if __name__ == "__main__":
    success = test_main_app_scrolling()
    exit(0 if success else 1)
