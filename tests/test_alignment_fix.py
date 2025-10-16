#!/usr/bin/env python3
"""
Test script to verify the alignment fix code changes.
This test validates that the frame packing parameters are correct.
"""

import re
import sys

def test_alignment_fix():
    """
    Verify that all wizard frame pack() calls no longer use fill="x"
    """
    print("Testing page alignment fix...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find all pack() calls in wizard page methods
    issues = []
    
    # Test 1: Check for fill="x" in wizard form frames
    # These should NOT have fill="x" anymore
    problematic_patterns = [
        (r'entry_container\.pack\(.*fill="x"', 'entry_container should not use fill="x"'),
        (r'password_container\.pack\(.*fill="x"', 'password_container should not use fill="x"'),
        (r'db_frame\.pack\(.*fill="x"', 'db_frame should not use fill="x"'),
        (r'admin_frame\.pack\(.*fill="x"', 'admin_frame should not use fill="x"'),
        (r'container_frame\.pack\(.*fill="x"', 'container_frame should not use fill="x"'),
    ]
    
    for pattern, message in problematic_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"❌ {message}")
            for match in matches:
                issues.append(f"   Found: {match}")
    
    # Test 2: Verify Entry widgets have width parameters
    entry_checks = [
        (r'self\.backup_entry\s*=\s*tk\.Entry\(.*?width\s*=\s*\d+', 'backup_entry should have width parameter'),
        (r'self\.password_entry\s*=\s*tk\.Entry\(.*?width\s*=\s*\d+', 'password_entry should have width parameter'),
    ]
    
    for pattern, message in entry_checks:
        if not re.search(pattern, content):
            issues.append(f"❌ {message}")
        else:
            print(f'✅ {message.replace("should have", "has")}')
    
    # Test 3: Verify frames use anchor="center" without fill="x"
    good_patterns = [
        (r'entry_container\.pack\(.*anchor="center".*\)', 'entry_container uses anchor="center"'),
        (r'password_container\.pack\(.*anchor="center".*\)', 'password_container uses anchor="center"'),
        (r'db_frame\.pack\(.*anchor="center".*\)', 'db_frame uses anchor="center"'),
        (r'admin_frame\.pack\(.*anchor="center".*\)', 'admin_frame uses anchor="center"'),
        (r'container_frame\.pack\(.*anchor="center".*\)', 'container_frame uses anchor="center"'),
    ]
    
    for pattern, message in good_patterns:
        if not re.search(pattern, content):
            issues.append(f"⚠️  Warning: {message} - could not verify")
    
    # Test 4: Check update_database_credential_ui method
    ui_update_pattern = r'def update_database_credential_ui.*?(?=\n    def |\Z)'
    ui_update_match = re.search(ui_update_pattern, content, re.DOTALL)
    
    if ui_update_match:
        ui_update_code = ui_update_match.group(0)
        if 'db_credential_frame.pack' in ui_update_code:
            if 'fill="x"' in ui_update_code:
                issues.append('❌ update_database_credential_ui still uses fill="x"')
            elif 'anchor="center"' in ui_update_code:
                print('✅ update_database_credential_ui correctly uses anchor="center"')
    
    # Report results
    print("\n" + "="*60)
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(issue)
        print("\nPlease review the alignment fix implementation.")
        return False
    else:
        print("✅ ALL TESTS PASSED!")
        print("\nVerified:")
        print("  • All wizard form frames removed fill=\"x\" parameter")
        print("  • Entry widgets have appropriate width parameters")
        print("  • All frames use anchor=\"center\" for proper centering")
        print("  • Dynamic UI update method also fixed")
        print("\nThe alignment fix appears to be correctly implemented.")
        return True

def test_syntax():
    """
    Verify Python syntax is valid
    """
    print("\nChecking Python syntax...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            compile(f.read(), '../src/nextcloud_restore_and_backup-v9.py', 'exec')
        print("✅ Python syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

def test_no_hardcoded_padx():
    """
    Verify that padx values were removed from wizard frames
    """
    print("\nChecking for removed padx parameters...")
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check wizard page methods specifically
    wizard_methods = [
        'def create_wizard_page1',
        'def create_wizard_page2',
        'def create_wizard_page3',
    ]
    
    issues = []
    for method in wizard_methods:
        method_pattern = f'{method}.*?(?=\\n    def |\\Z)'
        method_match = re.search(method_pattern, content, re.DOTALL)
        
        if method_match:
            method_code = method_match.group(0)
            # Look for form frames with padx in their pack() calls
            form_frames = ['entry_container', 'password_container', 'db_frame', 
                          'admin_frame', 'container_frame', 'info_frame']
            
            for frame in form_frames:
                pattern = f'{frame}\\.pack\\([^)]*padx'
                if re.search(pattern, method_code):
                    # Allow padx for info_frame as it might be intentional
                    if frame != 'info_frame':
                        issues.append(f"❌ {frame} in {method} still has padx parameter")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    else:
        print("✅ Hardcoded padx values removed from wizard form frames")
        return True

def main():
    print("="*60)
    print("Page Alignment Fix - Validation Tests")
    print("="*60)
    
    all_passed = True
    
    # Run all tests
    all_passed = test_syntax() and all_passed
    all_passed = test_alignment_fix() and all_passed
    all_passed = test_no_hardcoded_padx() and all_passed
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL VALIDATION TESTS PASSED")
        print("\nThe alignment fix is correctly implemented.")
        print("Manual testing with GUI is recommended to verify visual results.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
