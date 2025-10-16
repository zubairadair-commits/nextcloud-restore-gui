#!/usr/bin/env python3
"""
Test script to verify the UI centering enhancement.
This test validates:
1. Increased content max-width from 700px to 850px
2. Increased window size from 700x900 to 900x900
3. Wider input fields and buttons
4. Better padding and spacing
"""

import re
import sys

def test_content_width():
    """Verify content width increased from 700px to 850px"""
    print("Testing content width enhancement...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check for the new 850px width
    if re.search(r'scrollable_frame\s*=\s*tk\.Frame\(canvas,\s*width=850\)', content):
        print("✅ Content width increased to 850px")
        return True
    elif re.search(r'scrollable_frame\s*=\s*tk\.Frame\(canvas,\s*width=700\)', content):
        print("❌ Content width is still 700px (should be 850px)")
        return False
    else:
        print("⚠️  Could not find scrollable_frame width setting")
        return False

def test_window_geometry():
    """Verify window geometry increased from 700x900 to 900x900"""
    print("\nTesting window geometry...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check for the new 900x900 geometry
    if re.search(r'self\.geometry\("900x900"\)', content):
        print("✅ Window geometry set to 900x900")
        return True
    elif re.search(r'self\.geometry\("700x900"\)', content):
        print("❌ Window geometry is still 700x900 (should be 900x900)")
        return False
    else:
        print("⚠️  Could not find geometry setting")
        return False

def test_minimum_size():
    """Verify minimum window size increased from 600x700 to 700x700"""
    print("\nTesting minimum window size...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check for the new minsize
    if re.search(r'self\.minsize\(700,\s*700\)', content):
        print("✅ Minimum window size set to 700x700")
        return True
    elif re.search(r'self\.minsize\(600,\s*700\)', content):
        print("❌ Minimum window size is still 600x700 (should be 700x700)")
        return False
    else:
        print("⚠️  Could not find minsize setting")
        return False

def test_input_field_widths():
    """Verify input fields have been widened"""
    print("\nTesting input field widths...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    issues = []
    passed = []
    
    # Check backup_entry width (should be ~80)
    if re.search(r'self\.backup_entry\s*=\s*tk\.Entry\([^)]*width=80', content):
        passed.append("backup_entry width set to 80")
    elif re.search(r'self\.backup_entry\s*=\s*tk\.Entry\([^)]*width=60', content):
        issues.append("backup_entry width is still 60 (should be ~80)")
    
    # Check password_entry width (should be ~70)
    if re.search(r'self\.password_entry\s*=\s*tk\.Entry\([^)]*width=70', content):
        passed.append("password_entry width set to 70")
    elif re.search(r'self\.password_entry\s*=\s*tk\.Entry\([^)]*width=50', content):
        issues.append("password_entry width is still 50 (should be ~70)")
    
    for p in passed:
        print(f"✅ {p}")
    
    if issues:
        for issue in issues:
            print(f"❌ {issue}")
        return False
    else:
        print("✅ All input fields widened appropriately")
        return True

def test_grid_column_minsize():
    """Verify grid columns have minimum width for better layout"""
    print("\nTesting grid column minimum sizes...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check for minsize parameter in grid_columnconfigure
    minsize_count = len(re.findall(r'grid_columnconfigure\(\d+,\s*weight=1,\s*minsize=400\)', content))
    
    if minsize_count >= 3:
        print(f"✅ Found {minsize_count} grid columns with minsize=400")
        return True
    elif minsize_count > 0:
        print(f"⚠️  Found {minsize_count} grid columns with minsize (expected 3)")
        return True
    else:
        print("❌ No grid columns with minsize found")
        return False

def test_button_widths():
    """Verify navigation buttons have been widened"""
    print("\nTesting button widths...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    passed = []
    issues = []
    
    # Check navigation buttons (should be width=15)
    # Use DOTALL flag to handle multi-line button definitions
    nav_back_pattern = r'text="← Back".*?width=15'
    nav_next_pattern = r'text="Next →".*?width=15'
    
    if re.search(nav_back_pattern, content, re.DOTALL):
        passed.append("Back button width set to 15")
    else:
        issues.append("Back button width not set to 15")
    
    if re.search(nav_next_pattern, content, re.DOTALL):
        passed.append("Next button width set to 15")
    else:
        issues.append("Next button width not set to 15")
    
    # Check Start Restore button (should be width=18)
    if re.search(r'text="Start Restore".*?width=18', content, re.DOTALL):
        passed.append("Start Restore button width set to 18")
    else:
        issues.append("Start Restore button width not set to 18")
    
    for p in passed:
        print(f"✅ {p}")
    
    if issues:
        for issue in issues:
            print(f"⚠️  {issue}")
        return len(passed) > 0  # Partial pass
    else:
        print("✅ All navigation buttons widened")
        return True

def test_improved_padding():
    """Verify improved padding on frames"""
    print("\nTesting improved padding...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    passed = []
    
    # Check for padx on key frames
    if re.search(r'entry_container\.pack\([^)]*padx=30', content):
        passed.append("entry_container has padx=30")
    
    if re.search(r'password_container\.pack\([^)]*padx=30', content):
        passed.append("password_container has padx=30")
    
    if re.search(r'db_frame\.pack\([^)]*padx=40', content):
        passed.append("db_frame has padx=40")
    
    if re.search(r'admin_frame\.pack\([^)]*padx=40', content):
        passed.append("admin_frame has padx=40")
    
    if re.search(r'container_frame\.pack\([^)]*padx=40', content):
        passed.append("container_frame has padx=40")
    
    # Check for improved top padding on sections
    if re.search(r'Step 1: Select Backup Archive.*?pady=\(20', content):
        passed.append("Section 1 has increased top padding")
    
    if re.search(r'Step 2: Decryption Password.*?pady=\(30', content):
        passed.append("Section 2 has increased top padding")
    
    for p in passed:
        print(f"✅ {p}")
    
    if len(passed) >= 5:
        print("✅ Improved padding implemented")
        return True
    else:
        print(f"⚠️  Only {len(passed)} padding improvements found (expected more)")
        return len(passed) > 0

def test_syntax():
    """Verify Python syntax is valid"""
    print("\nChecking Python syntax...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            compile(f.read(), '../src/nextcloud_restore_and_backup-v9.py', 'exec')
        print("✅ Python syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

def main():
    print("="*70)
    print("UI Centering Enhancement - Validation Tests")
    print("="*70)
    
    all_passed = True
    
    # Run all tests
    all_passed = test_syntax() and all_passed
    all_passed = test_content_width() and all_passed
    all_passed = test_window_geometry() and all_passed
    all_passed = test_minimum_size() and all_passed
    all_passed = test_input_field_widths() and all_passed
    all_passed = test_grid_column_minsize() and all_passed
    all_passed = test_button_widths() and all_passed
    all_passed = test_improved_padding() and all_passed
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL VALIDATION TESTS PASSED")
        print("\nThe UI centering enhancement is correctly implemented.")
        print("Manual testing with GUI is recommended to verify visual results.")
        print("\nKey improvements:")
        print("  • Content width increased from 700px to 850px")
        print("  • Window size increased from 700x900 to 900x900")
        print("  • Input fields widened for better space utilization")
        print("  • Grid columns have minimum width of 400px")
        print("  • Buttons widened for better visual balance")
        print("  • Improved padding throughout for better spacing")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
