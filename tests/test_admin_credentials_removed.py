#!/usr/bin/env python3
"""
Test to verify that admin credentials have been removed from the restore workflow.
This ensures the changes are correctly implemented.
"""

import sys
import os

# Add the script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_file = os.path.join(os.path.dirname(script_dir), 'src', 'nextcloud_restore_and_backup-v9.py')

def test_syntax():
    """Test Python syntax is valid"""
    print("Testing Python syntax...")
    import py_compile
    try:
        py_compile.compile(src_file, doraise=True)
        print("  ✓ Syntax check passed")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ✗ Syntax error: {e}")
        return False

def test_admin_fields_not_in_restore_wizard():
    """Test that admin credential fields are not in create_wizard_page2"""
    print("\nTesting admin fields removed from restore wizard...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Find the create_wizard_page2 method
        start_marker = "def create_wizard_page2(self, parent):"
        start_idx = content.find(start_marker)
        if start_idx == -1:
            print("  ✗ Could not find create_wizard_page2 method")
            return False
        
        # Find the end of the method (next def at same indentation level)
        end_marker = "\n    def "
        end_idx = content.find(end_marker, start_idx + len(start_marker))
        if end_idx == -1:
            end_idx = len(content)
        
        method_content = content[start_idx:end_idx]
        
        # Check that admin fields are NOT present
        admin_field_indicators = [
            "Step 4: Nextcloud Admin Credentials",
            "Admin Username:",
            "Admin Password:",
            "admin_user_entry",
            "admin_password_entry"
        ]
        
        found_indicators = []
        for indicator in admin_field_indicators:
            if indicator in method_content:
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"  ✗ Found admin field indicators in create_wizard_page2: {found_indicators}")
            return False
        else:
            print("  ✓ No admin credential fields found in restore wizard")
            return True
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_admin_data_not_saved():
    """Test that admin credentials are not saved in save_wizard_page_data"""
    print("\nTesting admin data not saved...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Find the save_wizard_page_data method
        start_marker = "def save_wizard_page_data(self):"
        start_idx = content.find(start_marker)
        if start_idx == -1:
            print("  ✗ Could not find save_wizard_page_data method")
            return False
        
        # Find the end of the method
        end_marker = "\n    def "
        end_idx = content.find(end_marker, start_idx + len(start_marker))
        if end_idx == -1:
            end_idx = len(content)
        
        method_content = content[start_idx:end_idx]
        
        # Check that we're NOT saving admin credentials in page 2
        # Look for the page 2 section
        page2_section_start = method_content.find("elif self.wizard_page == 2:")
        if page2_section_start == -1:
            print("  ✗ Could not find page 2 section in save_wizard_page_data")
            return False
        
        # Get content from page 2 section to page 3 section
        page3_section_start = method_content.find("elif self.wizard_page == 3:", page2_section_start)
        if page3_section_start == -1:
            page2_content = method_content[page2_section_start:]
        else:
            page2_content = method_content[page2_section_start:page3_section_start]
        
        # Check that admin data is NOT being saved
        if "admin_user_entry" in page2_content or "admin_password_entry" in page2_content:
            print("  ✗ Admin credential data is still being saved in page 2")
            return False
        else:
            print("  ✓ Admin credential data is not saved in wizard page 2")
            return True
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_admin_validation_removed():
    """Test that admin credential validation is removed from validate_and_start_restore"""
    print("\nTesting admin validation removed...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Find the validate_and_start_restore method
        start_marker = "def validate_and_start_restore(self):"
        start_idx = content.find(start_marker)
        if start_idx == -1:
            print("  ✗ Could not find validate_and_start_restore method")
            return False
        
        # Find the end of the method
        end_marker = "\n    def "
        end_idx = content.find(end_marker, start_idx + len(start_marker))
        if end_idx == -1:
            end_idx = len(content)
        
        method_content = content[start_idx:end_idx]
        
        # Check that we're NOT validating admin credentials
        validation_checks = [
            'if not admin_user:',
            'if not admin_password:',
            'Error: Admin username is required',
            'Error: Admin password is required'
        ]
        
        found_checks = []
        for check in validation_checks:
            if check in method_content:
                found_checks.append(check)
        
        if found_checks:
            print(f"  ✗ Found admin validation in validate_and_start_restore: {found_checks}")
            return False
        else:
            print("  ✓ No admin credential validation found")
            return True
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_admin_env_not_set():
    """Test that admin environment variables are not set during container creation"""
    print("\nTesting admin environment variables not set...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Find the section where container is created (around line 7540-7580)
        # Look for the comment about not setting admin credentials
        expected_comment = "# Note: During restore, we do NOT set admin credentials via environment variables"
        
        if expected_comment not in content:
            print("  ✗ Expected comment about not setting admin credentials not found")
            return False
        
        print("  ✓ Found comment explaining admin credentials are not set during restore")
        
        # Find the start_restore_thread method (where container creation happens)
        start_marker = "def start_restore_thread(self):"
        start_idx = content.find(start_marker)
        if start_idx == -1:
            print("  ✗ Could not find start_restore_thread method")
            return False
        
        # Find the end of the method
        end_marker = "\n    def "
        end_idx = content.find(end_marker, start_idx + len(start_marker))
        if end_idx == -1:
            end_idx = len(content)
        
        method_content = content[start_idx:end_idx]
        
        # Check that we're NOT setting admin env vars
        if "NEXTCLOUD_ADMIN_USER" in method_content or "NEXTCLOUD_ADMIN_PASSWORD" in method_content:
            print("  ✗ Found NEXTCLOUD_ADMIN_USER or NEXTCLOUD_ADMIN_PASSWORD in start_restore_thread")
            return False
        else:
            print("  ✓ Admin environment variables are not set during container creation")
            return True
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_completion_message_always_shown():
    """Test that completion message about previous credentials is always shown"""
    print("\nTesting completion message always shown...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Find the show_restore_completion_dialog method
        start_marker = "def show_restore_completion_dialog(self, container_name, port, admin_username=None):"
        start_idx = content.find(start_marker)
        if start_idx == -1:
            print("  ✗ Could not find show_restore_completion_dialog method")
            return False
        
        # Find the end of the method
        end_marker = "\n    def "
        end_idx = content.find(end_marker, start_idx + len(start_marker))
        if end_idx == -1:
            end_idx = len(content)
        
        method_content = content[start_idx:end_idx]
        
        # Check that message is always shown
        expected_patterns = [
            "Log in with your previous admin credentials",
            "admin_info_text =",
            "admin_info = tk.Label"
        ]
        
        all_found = True
        for pattern in expected_patterns:
            if pattern not in method_content:
                print(f"  ✗ Pattern not found: {pattern}")
                all_found = False
        
        if all_found:
            print("  ✓ Completion message about previous credentials is always shown")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_new_instance_workflow_unchanged():
    """Test that the new instance workflow still has admin credential fields"""
    print("\nTesting new instance workflow unchanged...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Find the show_port_entry method (part of new instance workflow)
        start_marker = "def show_port_entry(self):"
        start_idx = content.find(start_marker)
        if start_idx == -1:
            print("  ✗ Could not find show_port_entry method")
            return False
        
        # Find the end of the method
        end_marker = "\n    def "
        end_idx = content.find(end_marker, start_idx + len(start_marker))
        if end_idx == -1:
            end_idx = len(content)
        
        method_content = content[start_idx:end_idx]
        
        # Check that admin fields ARE present in new instance workflow
        required_elements = [
            "Admin Credentials",
            "Admin Username:",
            "Admin Password:",
            "admin_user_entry",
            "admin_password_entry"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in method_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"  ✗ Missing elements in new instance workflow: {missing_elements}")
            return False
        else:
            print("  ✓ New instance workflow still has admin credential fields (correct)")
            return True
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Admin Credentials Removal from Restore Workflow")
    print("=" * 60)
    
    tests = [
        test_syntax,
        test_admin_fields_not_in_restore_wizard,
        test_admin_data_not_saved,
        test_admin_validation_removed,
        test_admin_env_not_set,
        test_completion_message_always_shown,
        test_new_instance_workflow_unchanged
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} passed")
    print("=" * 60)
    
    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
