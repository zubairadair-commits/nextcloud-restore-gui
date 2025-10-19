#!/usr/bin/env python3
"""
Test script for backup rotation dropdown UI changes.

Tests:
1. Verify '2 backups' option is present in rotation options
2. Verify rotation options use dropdown (Combobox) instead of radio buttons
3. Verify all expected rotation values are present
"""

import sys
import os

def test_two_backups_option():
    """Test that '2 backups' option is present."""
    print("Testing '2 backups' option...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    assert os.path.exists(main_file), f"{main_file} should exist"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the show_schedule_backup function
    function_start = content.find('def show_schedule_backup(self):')
    assert function_start != -1, "show_schedule_backup function should exist"
    
    schedule_section_end = content.find('\n    def ', function_start + 1)
    schedule_section = content[function_start:schedule_section_end]
    
    # Check for '2 backups' option
    assert '(2, "2 backups")' in schedule_section, \
        "'2 backups' option should be present in rotation options"
    print("  ✓ '2 backups' option found")
    
    print("✅ '2 backups' option test PASSED\n")

def test_dropdown_instead_of_radio():
    """Test that dropdown (Combobox) is used instead of radio buttons."""
    print("Testing dropdown implementation...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the show_schedule_backup function
    function_start = content.find('def show_schedule_backup(self):')
    schedule_section_end = content.find('\n    def ', function_start + 1)
    schedule_section = content[function_start:schedule_section_end]
    
    # Check for Combobox (dropdown)
    assert 'ttk.Combobox' in schedule_section, \
        "Combobox should be used for rotation selection"
    print("  ✓ Combobox (dropdown) implementation found")
    
    # Check that RadioButton is NOT used for rotation
    # Look for rotation_combobox specifically
    assert 'rotation_combobox' in schedule_section, \
        "rotation_combobox variable should exist"
    print("  ✓ rotation_combobox variable found")
    
    # Check for readonly state
    assert "state='readonly'" in schedule_section or 'state="readonly"' in schedule_section, \
        "Combobox should be readonly"
    print("  ✓ Combobox is readonly")
    
    # Check for ComboboxSelected event binding
    assert '<<ComboboxSelected>>' in schedule_section, \
        "Should bind to ComboboxSelected event"
    print("  ✓ ComboboxSelected event binding found")
    
    print("✅ Dropdown implementation test PASSED\n")

def test_all_rotation_values():
    """Test that all expected rotation values are present."""
    print("Testing all rotation values...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the show_schedule_backup function
    function_start = content.find('def show_schedule_backup(self):')
    schedule_section_end = content.find('\n    def ', function_start + 1)
    schedule_section = content[function_start:schedule_section_end]
    
    # Expected rotation options
    expected_options = [
        '(0, "Unlimited (no deletion)")',
        '(1, "1 backup (always replace)")',
        '(2, "2 backups")',
        '(3, "3 backups")',
        '(5, "5 backups")',
        '(10, "10 backups")'
    ]
    
    for option in expected_options:
        assert option in schedule_section, \
            f"Expected rotation option not found: {option}"
        print(f"  ✓ Found: {option}")
    
    print("✅ All rotation values test PASSED\n")

def test_tooltip_on_dropdown():
    """Test that tooltip is added to the dropdown."""
    print("Testing tooltip on dropdown...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the show_schedule_backup function
    function_start = content.find('def show_schedule_backup(self):')
    schedule_section_end = content.find('\n    def ', function_start + 1)
    schedule_section = content[function_start:schedule_section_end]
    
    # Check for tooltip on combobox
    # Look for ToolTip(rotation_combobox, ...)
    assert 'ToolTip(rotation_combobox,' in schedule_section, \
        "Tooltip should be added to rotation_combobox"
    print("  ✓ Tooltip found on rotation_combobox")
    
    print("✅ Tooltip test PASSED\n")

def main():
    """Run all tests."""
    print("=" * 60)
    print("BACKUP ROTATION DROPDOWN UI TESTS")
    print("Testing dropdown implementation and '2 backups' option")
    print("=" * 60)
    print()
    
    try:
        test_two_backups_option()
        test_dropdown_instead_of_radio()
        test_all_rotation_values()
        test_tooltip_on_dropdown()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
