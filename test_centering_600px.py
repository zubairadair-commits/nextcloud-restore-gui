#!/usr/bin/env python3
"""
Test script to verify the 600px centered layout implementation.
This test validates:
1. Content frame uses place() geometry manager
2. Fixed width of 600px
3. Centered with relx=0.5, anchor="n"
4. No canvas/scrollbar complexity
5. Child widgets use fill="x" with padx=40
"""

import re
import sys

def test_place_geometry():
    """Verify content frame uses place() geometry manager"""
    print("Testing place() geometry manager...")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check for place() with relx=0.5 and anchor="n"
    if re.search(r'\.place\(relx=0\.5,\s*anchor="n"', content):
        print("✅ Content frame uses place(relx=0.5, anchor='n')")
        return True
    else:
        print("❌ Content frame does not use place() geometry with correct parameters")
        return False

def test_fixed_width_600px():
    """Verify content frame has fixed width of 600px"""
    print("\nTesting fixed width of 600px...")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check for width=600
    if re.search(r'Frame\(self\.body_frame,\s*width=600\)', content):
        print("✅ Content frame has fixed width of 600px")
        return True
    else:
        print("❌ Content frame does not have width=600")
        return False

def test_no_canvas_scrollbar():
    """Verify canvas and scrollbar have been removed"""
    print("\nTesting removal of canvas/scrollbar...")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check that canvas and scrollbar are NOT created in create_wizard
    # Look for the create_wizard method
    match = re.search(r'def create_wizard\(self\):.*?(?=\n    def |\Z)', content, re.DOTALL)
    if match:
        method_content = match.group(0)
        
        has_canvas = 'tk.Canvas' in method_content
        has_scrollbar = 'tk.Scrollbar' in method_content
        has_canvas_window = 'canvas.create_window' in method_content
        
        if not has_canvas and not has_scrollbar and not has_canvas_window:
            print("✅ Canvas and scrollbar removed from create_wizard()")
            return True
        else:
            print("❌ Canvas or scrollbar still present in create_wizard()")
            if has_canvas:
                print("   - Found tk.Canvas")
            if has_scrollbar:
                print("   - Found tk.Scrollbar")
            if has_canvas_window:
                print("   - Found canvas.create_window")
            return False
    else:
        print("⚠️  Could not find create_wizard method")
        return False

def test_child_widget_layout():
    """Verify child widgets use fill='x' with padx=40"""
    print("\nTesting child widget layout (fill='x', padx=40)...")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check for patterns of fill="x" with padx=40
    patterns_found = 0
    patterns_expected = 10  # At least 10 instances across all pages
    
    # Look for pack with fill="x" and padx=40
    matches = re.findall(r'\.pack\([^)]*fill="x"[^)]*padx=40[^)]*\)', content)
    patterns_found = len(matches)
    
    if patterns_found >= patterns_expected:
        print(f"✅ Found {patterns_found} instances of fill='x' with padx=40 (expected >= {patterns_expected})")
        return True
    else:
        print(f"❌ Found only {patterns_found} instances of fill='x' with padx=40 (expected >= {patterns_expected})")
        return False

def test_window_geometry():
    """Verify window geometry is 900x900"""
    print("\nTesting window geometry...")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check for 900x900 geometry
    if re.search(r'self\.geometry\("900x900"\)', content):
        print("✅ Window geometry set to 900x900")
        return True
    else:
        print("❌ Window geometry not set to 900x900")
        return False

def test_syntax():
    """Verify Python syntax is valid"""
    print("\nTesting Python syntax...")
    
    import py_compile
    try:
        py_compile.compile('nextcloud_restore_and_backup-v9.py', doraise=True)
        print("✅ Python syntax is valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Python syntax error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("Testing 600px Centered Layout Implementation")
    print("=" * 70)
    
    tests = [
        test_place_geometry,
        test_fixed_width_600px,
        test_no_canvas_scrollbar,
        test_child_widget_layout,
        test_window_geometry,
        test_syntax
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} passed")
    print("=" * 70)
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
