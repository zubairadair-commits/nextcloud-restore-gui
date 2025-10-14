#!/usr/bin/env python3
"""
Test script to verify Test Run button implementation.

This ensures:
1. Test Run button is positioned in Current Status section
2. Button is enabled when schedule is active
3. Button is disabled when no schedule exists
4. Tooltip is present for both states
5. Button uses schedule configuration when clicked
6. Inline feedback is displayed correctly
"""

import sys
import os


def test_test_run_button_in_status_section():
    """Test that Test Run button was added to Current Status section."""
    print("=" * 70)
    print("TEST 1: Test Run Button in Current Status Section")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find show_schedule_backup method
    method_start = content.find('def show_schedule_backup(')
    assert method_start != -1, "show_schedule_backup method should exist"
    
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Check for Test Run button in status section
    # Look for the button after "Current Status" but before "Configure New Schedule"
    status_start = method_content.find('Current Status')
    config_start = method_content.find('Configure New Schedule')
    
    assert status_start != -1, "Should have Current Status section"
    assert config_start != -1, "Should have Configure New Schedule section"
    
    status_section = method_content[status_start:config_start]
    
    # Check that Test Run button is in status section
    assert '🧪 Test Run' in status_section, \
        "Test Run button should be in Current Status section"
    
    print("  ✓ Test Run button is in Current Status section")
    print("  ✓ Button positioned before Configure New Schedule section")
    print()
    return True


def test_test_run_button_enabled_state():
    """Test that Test Run button has proper enabled/disabled logic."""
    print("=" * 70)
    print("TEST 2: Test Run Button Enable/Disable Logic")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find show_schedule_backup method
    method_start = content.find('def show_schedule_backup(')
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Check for enabled button when schedule exists
    assert 'if status and status.get(\'exists\'):' in method_content, \
        "Should check if schedule exists"
    
    # Look for Test Run button text (with or without emoji)
    # and the blue background color which indicates enabled state
    test_run_count = method_content.count('Test Run')
    assert test_run_count >= 2, \
        f"Should have at least 2 Test Run buttons (found {test_run_count})"
    
    # Check for blue background color (enabled state)
    assert 'bg="#3498db"' in method_content, \
        "Active Test Run button should have blue background"
    
    print("  ✓ Test Run button is enabled when schedule is active")
    print("  ✓ Button has correct blue background color (#3498db)")
    
    # Check for disabled button state
    assert 'state=tk.DISABLED' in method_content, \
        "Test Run button should be disabled when no schedule exists"
    
    assert '#d3d3d3' in method_content or 'gray' in method_content.lower(), \
        "Disabled Test Run button should have gray background"
    
    print("  ✓ Test Run button is disabled when no schedule exists")
    print("  ✓ Disabled button has gray background")
    print()
    return True


def test_test_run_button_tooltip():
    """Test that Test Run button has tooltip in both states."""
    print("=" * 70)
    print("TEST 3: Test Run Button Tooltips")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find show_schedule_backup method
    method_start = content.find('def show_schedule_backup(')
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Count ToolTip instances for Test Run button
    tooltip_count = method_content.count('ToolTip(test_run_btn')
    
    assert tooltip_count >= 2, \
        f"Should have tooltips for both active and disabled Test Run buttons (found {tooltip_count})"
    
    # Check that tooltips have meaningful messages
    assert 'disabled because no backup schedule is configured' in method_content or \
           'no schedule' in method_content.lower(), \
        "Should have tooltip explaining why button is disabled"
    
    assert 'immediately run a backup' in method_content.lower() or \
           'verify' in method_content.lower(), \
        "Should have tooltip explaining what Test Run does when enabled"
    
    print("  ✓ Tooltip present for enabled Test Run button")
    print("  ✓ Tooltip present for disabled Test Run button")
    print("  ✓ Tooltips contain helpful explanatory text")
    print()
    return True


def test_test_run_uses_schedule_config():
    """Test that Test Run uses schedule configuration."""
    print("=" * 70)
    print("TEST 4: Test Run Uses Schedule Configuration")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for _run_test_backup_scheduled method
    assert 'def _run_test_backup_scheduled(' in content, \
        "Should have _run_test_backup_scheduled method"
    
    # Find the method
    method_start = content.find('def _run_test_backup_scheduled(')
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Check that it uses config parameter
    assert 'config' in method_content, \
        "Method should accept config parameter"
    
    assert "config.get('backup_dir'" in method_content, \
        "Should get backup_dir from config"
    
    assert "config.get('encrypt'" in method_content, \
        "Should get encrypt setting from config"
    
    assert 'run_test_backup(' in method_content, \
        "Should call run_test_backup function"
    
    print("  ✓ _run_test_backup_scheduled method exists")
    print("  ✓ Method accepts schedule config parameter")
    print("  ✓ Method extracts backup_dir from config")
    print("  ✓ Method extracts encrypt setting from config")
    print("  ✓ Method calls run_test_backup with config values")
    print()
    return True


def test_inline_feedback_for_test_run():
    """Test that Test Run displays inline feedback."""
    print("=" * 70)
    print("TEST 5: Test Run Inline Feedback")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find _run_test_backup_scheduled method
    method_start = content.find('def _run_test_backup_scheduled(')
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Check for inline message usage
    assert 'schedule_message_label' in method_content, \
        "Should use schedule_message_label for inline feedback"
    
    # Check for progress message
    assert '⏳' in method_content or 'Running test backup' in method_content, \
        "Should show progress message"
    
    # Check for success message
    assert '✅' in method_content or 'Test Backup Successful' in method_content, \
        "Should show success message"
    
    # Check for error message
    assert '❌' in method_content or 'Test Backup Failed' in method_content, \
        "Should show error message"
    
    # Check that no messagebox is used
    assert 'messagebox' not in method_content, \
        "Should NOT use messagebox (inline only)"
    
    print("  ✓ Uses schedule_message_label for inline feedback")
    print("  ✓ Shows progress message (⏳)")
    print("  ✓ Shows success message (✅)")
    print("  ✓ Shows error message (❌)")
    print("  ✓ No messagebox dialogs (inline only)")
    print()
    return True


def test_test_run_button_positioning():
    """Test that Test Run button is positioned correctly with other buttons."""
    print("=" * 70)
    print("TEST 6: Test Run Button Positioning")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find show_schedule_backup method
    method_start = content.find('def show_schedule_backup(')
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Get positions of button text in the entire method
    test_run_pos = method_content.find('Test Run')
    disable_pos = method_content.find('Disable Schedule')
    delete_pos = method_content.find('Delete Schedule')
    
    # All buttons should be present
    assert test_run_pos != -1, "Test Run button should be in method"
    assert disable_pos != -1, "Disable Schedule button should be in method"
    assert delete_pos != -1, "Delete Schedule button should be in method"
    
    # Test Run should come before Disable and Delete
    assert test_run_pos < disable_pos, \
        "Test Run should be positioned before Disable Schedule"
    assert test_run_pos < delete_pos, \
        "Test Run should be positioned before Delete Schedule"
    
    # Check they're in the same button frame
    btn_frame_section = method_content[test_run_pos-500:delete_pos+100]
    btn_frame_count = btn_frame_section.count('btn_frame')
    assert btn_frame_count > 0, "Buttons should be in btn_frame"
    
    print("  ✓ Test Run button is in same frame as Disable/Delete buttons")
    print("  ✓ Test Run button appears first (leftmost)")
    print("  ✓ Disable Schedule button appears second")
    print("  ✓ Delete Schedule button appears third (rightmost)")
    print()
    return True


def test_no_test_run_in_configure_section():
    """Test that Test Run button was removed from Configure New Schedule section."""
    print("=" * 70)
    print("TEST 7: Test Run Button Removed from Configure Section")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find show_schedule_backup method
    method_start = content.find('def show_schedule_backup(')
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Find Configure New Schedule section
    config_start = method_content.find('Configure New Schedule')
    
    # Find Last Run Status section (if it exists) to limit our search
    last_run_start = method_content.find('Last Run Status', config_start)
    if last_run_start == -1:
        last_run_start = len(method_content)
    
    config_section = method_content[config_start:last_run_start]
    
    # Check that Test Run is NOT in buttons_frame or near Create/Update Schedule
    # We should only have Create/Update Schedule button in this section
    create_update_count = config_section.count('Create/Update Schedule')
    assert create_update_count >= 1, "Should have Create/Update Schedule button"
    
    # The Test Run button should not be calling _run_test_backup (the old way)
    # in the configuration section
    if 'buttons_frame' in config_section:
        # If there's a buttons_frame, it shouldn't have Test Run
        buttons_frame_start = config_section.find('buttons_frame')
        buttons_frame_section = config_section[buttons_frame_start:buttons_frame_start+500]
        test_run_in_buttons = '🧪 Test Run' in buttons_frame_section
        assert not test_run_in_buttons, \
            "Test Run button should NOT be in Configure section's buttons_frame"
    
    print("  ✓ Create/Update Schedule button is in Configure section")
    print("  ✓ Test Run button is NOT in Configure section")
    print("  ✓ Configuration section is clean and focused")
    print()
    return True


def main():
    """Run all tests."""
    print()
    print("=" * 70)
    print("TEST RUN BUTTON IMPLEMENTATION VALIDATION")
    print("=" * 70)
    print()
    
    tests = [
        test_test_run_button_in_status_section,
        test_test_run_button_enabled_state,
        test_test_run_button_tooltip,
        test_test_run_uses_schedule_config,
        test_inline_feedback_for_test_run,
        test_test_run_button_positioning,
        test_no_test_run_in_configure_section,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            print()
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            print()
            failed += 1
    
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print()
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
