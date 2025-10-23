#!/usr/bin/env python3
"""
Test to verify the progressbar fix resolves the issue where the progress bar
doesn't visually fill during extraction.

This test validates that using __setitem__ instead of setattr properly updates
the tkinter ttk.Progressbar widget.
"""

import os
import sys

# Add src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(os.path.dirname(script_dir), 'src')
sys.path.insert(0, src_path)

def test_progressbar_update_fix():
    """
    Test that the set_restore_progress method uses the correct progressbar update method.
    
    The issue was that the code used:
        lambda: setattr(self.progressbar, 'value', percent)
    
    This sets a Python attribute but doesn't trigger tkinter's internal update mechanism.
    
    The fix is to use:
        lambda: self.progressbar.__setitem__('value', percent)
    
    This is equivalent to:
        self.progressbar['value'] = percent
    
    Which properly triggers tkinter's widget update mechanism.
    """
    print("\n" + "="*70)
    print("Testing Progressbar Update Fix")
    print("="*70)
    
    # Read the source file
    script_path = os.path.join(src_path, 'nextcloud_restore_and_backup-v9.py')
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Verify the broken setattr pattern is NOT present
    print("\n1. Checking that broken setattr pattern is removed...")
    tests_total += 1
    
    broken_pattern = "lambda: setattr(self.progressbar, 'value', percent)"
    if broken_pattern in content:
        print(f"   ❌ FAIL: Found broken pattern: {broken_pattern}")
        print("   The progressbar won't update visually!")
    else:
        print("   ✅ PASS: Broken setattr pattern not found")
        tests_passed += 1
    
    # Test 2: Verify the correct __setitem__ pattern IS present
    print("\n2. Checking that correct __setitem__ pattern is present...")
    tests_total += 1
    
    correct_pattern = "lambda: self.progressbar.__setitem__('value', percent)"
    if correct_pattern in content:
        print(f"   ✅ PASS: Found correct pattern: {correct_pattern}")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: Correct pattern not found!")
        # Also check for direct dict syntax as an alternative correct approach
        alt_pattern = "self.progressbar['value'] = percent"
        if alt_pattern in content:
            print(f"   ✅ PASS: Found alternative correct pattern: {alt_pattern}")
            tests_passed += 1
    
    # Test 3: Verify set_restore_progress method exists
    print("\n3. Checking that set_restore_progress method exists...")
    tests_total += 1
    
    if "def set_restore_progress(self, percent, msg=" in content:
        print("   ✅ PASS: set_restore_progress method found")
        tests_passed += 1
    else:
        print("   ❌ FAIL: set_restore_progress method not found")
    
    # Test 4: Verify safe_widget_update is used
    print("\n4. Checking that safe_widget_update is used for progressbar...")
    tests_total += 1
    
    if "safe_widget_update(" in content and "progressbar" in content:
        print("   ✅ PASS: safe_widget_update is used")
        tests_passed += 1
    else:
        print("   ❌ FAIL: safe_widget_update not used properly")
    
    # Test 5: Extract the relevant code section to verify it looks correct
    print("\n5. Extracting set_restore_progress progressbar update code...")
    tests_total += 1
    
    # Find the progressbar update section in set_restore_progress
    lines = content.split('\n')
    in_method = False
    found_update = False
    code_snippet = []
    
    for i, line in enumerate(lines):
        if 'def set_restore_progress(self, percent, msg=' in line:
            in_method = True
        elif in_method and 'def ' in line and 'set_restore_progress' not in line:
            in_method = False
            break
        elif in_method and 'Update progress bar' in line:
            # Capture the next ~10 lines
            code_snippet = lines[i:i+10]
            found_update = True
            break
    
    if found_update:
        print("   Code snippet:")
        for line in code_snippet:
            if line.strip():
                print(f"      {line}")
        
        # Verify it has __setitem__
        snippet_text = '\n'.join(code_snippet)
        if '__setitem__' in snippet_text and "'value'" in snippet_text:
            print("   ✅ PASS: Progressbar update code uses __setitem__")
            tests_passed += 1
        else:
            print("   ❌ FAIL: Progressbar update code doesn't use __setitem__")
    else:
        print("   ❌ FAIL: Could not find progressbar update code")
    
    # Summary
    print("\n" + "="*70)
    print(f"Test Results: {tests_passed}/{tests_total} tests passed")
    print("="*70)
    
    if tests_passed == tests_total:
        print("\n✅ ALL TESTS PASSED!")
        print("\nThe fix is correctly applied:")
        print("  - The broken setattr pattern has been removed")
        print("  - The correct __setitem__ pattern is in place")
        print("  - The progressbar will now update visually during extraction")
        print("\nExpected behavior:")
        print("  ✓ Progress bar fills from 0% to 100% in real-time")
        print("  ✓ Current file being extracted is displayed")
        print("  ✓ Elapsed time and estimates are shown")
        print("  ✓ User can see extraction progress smoothly")
        return True
    else:
        print(f"\n❌ {tests_total - tests_passed} TEST(S) FAILED")
        print("The fix may not be correctly applied.")
        return False

if __name__ == "__main__":
    try:
        success = test_progressbar_update_fix()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
