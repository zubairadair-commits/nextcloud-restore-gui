#!/usr/bin/env python3
"""
Test to verify that SCHTASKS arguments are properly formatted.
This validates that schedule arguments like '/SC DAILY' are split into separate list elements.
"""

import sys
import os
import re


def test_schedule_args_format():
    """Test that schedule arguments are formatted as separate list elements."""
    print("Testing SCHTASKS argument format...")
    
    # Read the main file
    main_file = "nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print(f"✗ {main_file} not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the create_scheduled_task function
    func_start = content.find('def create_scheduled_task(')
    if func_start == -1:
        print("✗ create_scheduled_task function not found")
        return False
    
    # Get the function content (roughly - up to the next function definition)
    func_end = content.find('\ndef ', func_start + 1)
    func_content = content[func_start:func_end]
    
    all_passed = True
    
    # Test 1: Check that schedule_args for daily is a list
    if 'schedule_args = ["/SC", "DAILY"]' in func_content:
        print("  ✓ Daily schedule arguments correctly formatted as list: ['/SC', 'DAILY']")
    elif 'schedule_args = "/SC DAILY"' in func_content:
        print("  ✗ Daily schedule arguments incorrectly formatted as string: '/SC DAILY'")
        all_passed = False
    else:
        print("  ⚠ Could not find daily schedule args pattern")
        all_passed = False
    
    # Test 2: Check that schedule_args for weekly is a list
    if 'schedule_args = ["/SC", "WEEKLY", "/D", "MON"]' in func_content:
        print("  ✓ Weekly schedule arguments correctly formatted as list: ['/SC', 'WEEKLY', '/D', 'MON']")
    elif 'schedule_args = "/SC WEEKLY /D MON"' in func_content:
        print("  ✗ Weekly schedule arguments incorrectly formatted as string: '/SC WEEKLY /D MON'")
        all_passed = False
    else:
        print("  ⚠ Could not find weekly schedule args pattern")
        all_passed = False
    
    # Test 3: Check that schedule_args for monthly is a list
    if 'schedule_args = ["/SC", "MONTHLY", "/D", "1"]' in func_content:
        print("  ✓ Monthly schedule arguments correctly formatted as list: ['/SC', 'MONTHLY', '/D', '1']")
    elif 'schedule_args = "/SC MONTHLY /D 1"' in func_content:
        print("  ✗ Monthly schedule arguments incorrectly formatted as string: '/SC MONTHLY /D 1'")
        all_passed = False
    else:
        print("  ⚠ Could not find monthly schedule args pattern")
        all_passed = False
    
    # Test 4: Check that schedule_args is extended to schtasks_cmd (not appended as single element)
    if 'schtasks_cmd.extend(schedule_args)' in func_content:
        print("  ✓ Schedule arguments correctly extended to command list with .extend()")
    elif re.search(r'schtasks_cmd\s*=\s*\[[^\]]*schedule_args[^\]]*\]', func_content):
        print("  ✗ Schedule arguments appended as single element instead of extended")
        all_passed = False
    else:
        print("  ⚠ Could not determine how schedule_args is added to command")
        all_passed = False
    
    # Test 5: Verify that /F flag is appended separately
    if 'schtasks_cmd.append("/F")' in func_content or '"/F"' in func_content:
        print("  ✓ /F flag is present in command")
    else:
        print("  ⚠ /F flag not found")
    
    return all_passed


def test_command_structure_visualization():
    """Show the expected command structure."""
    print("\nExpected SCHTASKS command structure:")
    print("=" * 70)
    
    # Daily example
    print("\nDaily schedule command should be:")
    print("  ['schtasks', '/Create', '/TN', 'TaskName', '/TR', 'command',")
    print("   '/ST', '02:00', '/SC', 'DAILY', '/F']")
    
    # Weekly example
    print("\nWeekly schedule command should be:")
    print("  ['schtasks', '/Create', '/TN', 'TaskName', '/TR', 'command',")
    print("   '/ST', '02:00', '/SC', 'WEEKLY', '/D', 'MON', '/F']")
    
    # Monthly example
    print("\nMonthly schedule command should be:")
    print("  ['schtasks', '/Create', '/TN', 'TaskName', '/TR', 'command',")
    print("   '/ST', '02:00', '/SC', 'MONTHLY', '/D', '1', '/F']")
    
    print("\nNOTE: Each '/SC', 'DAILY', '/D', etc. must be separate list elements!")
    print("=" * 70)


def main():
    """Run all tests."""
    print("=" * 70)
    print("SCHTASKS Argument Format Test")
    print("=" * 70)
    
    try:
        test_command_structure_visualization()
        print()
        
        if test_schedule_args_format():
            print("\n" + "=" * 70)
            print("All tests passed! ✓")
            print("SCHTASKS arguments are correctly formatted.")
            print("=" * 70)
            return 0
        else:
            print("\n" + "=" * 70)
            print("Some tests failed! ✗")
            print("SCHTASKS arguments may not be correctly formatted.")
            print("=" * 70)
            return 1
            
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
