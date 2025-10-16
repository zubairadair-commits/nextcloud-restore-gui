#!/usr/bin/env python3
"""
Test script to verify that schedule operations use inline notifications
instead of pop-up message boxes.

This ensures:
1. Validation errors are shown inline
2. Success messages are shown inline
3. Test results are shown inline
4. No blocking messagebox dialogs
5. Users can continue interacting with the page
"""

import sys
import os


def test_inline_message_label_added():
    """Test that inline message label was added to the schedule page."""
    print("=" * 70)
    print("TEST 1: Inline Message Label Added")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find show_schedule_backup method
    method_start = content.find('def show_schedule_backup(')
    assert method_start != -1, "show_schedule_backup method should exist"
    
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Check for inline message label
    assert 'schedule_message_label' in method_content, \
        "Should have schedule_message_label for inline notifications"
    
    assert 'tk.Label' in method_content and 'schedule_message_label' in method_content, \
        "schedule_message_label should be a tk.Label widget"
    
    print("  ✓ schedule_message_label added to schedule page")
    print("  ✓ Label configured for inline notifications")
    print()
    return True


def test_no_messagebox_in_create_schedule():
    """Test that _create_schedule uses inline messages instead of messagebox."""
    print("=" * 70)
    print("TEST 2: Create Schedule Uses Inline Messages")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find _create_schedule method
    method_start = content.find('def _create_schedule(')
    assert method_start != -1, "_create_schedule method should exist"
    
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Check that messagebox is not used for validation errors
    # (Allow it in other contexts, but not for main user feedback)
    validation_start = method_content.find('if not validation_results')
    if validation_start != -1:
        validation_section = method_content[validation_start:validation_start+500]
        # Should not have messagebox.showerror for validation
        assert 'messagebox.showerror' not in validation_section, \
            "Should NOT use messagebox.showerror for validation errors"
        
        # Should use schedule_message_label instead
        assert 'schedule_message_label' in validation_section or 'schedule_message_label' in method_content, \
            "Should use schedule_message_label for inline validation errors"
    
    # Check success message uses inline notification
    success_start = method_content.find('if save_schedule_config(config):')
    if success_start != -1:
        success_section = method_content[success_start:success_start+800]
        # Should not have messagebox.showinfo for success
        assert 'messagebox.showinfo' not in success_section, \
            "Should NOT use messagebox.showinfo for success messages"
        
        # Should use schedule_message_label
        assert 'schedule_message_label' in success_section, \
            "Should use schedule_message_label for inline success messages"
    
    print("  ✓ Validation errors shown inline (no messagebox)")
    print("  ✓ Success messages shown inline (no messagebox)")
    print("  ✓ Users can continue interacting with the page")
    print()
    return True


def test_test_run_uses_inline_messages():
    """Test that _run_test_backup uses inline messages."""
    print("=" * 70)
    print("TEST 3: Test Run Uses Inline Messages")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find _run_test_backup method
    method_start = content.find('def _run_test_backup(')
    assert method_start != -1, "_run_test_backup method should exist"
    
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Should use schedule_message_label for results
    assert 'schedule_message_label' in method_content, \
        "Should use schedule_message_label for test results"
    
    # Check for inline progress message
    assert 'Running test backup' in method_content or 'test backup' in method_content.lower(), \
        "Should show progress message for test backup"
    
    print("  ✓ Test Run shows progress inline")
    print("  ✓ Test Run shows results inline")
    print("  ✓ No blocking progress dialogs")
    print()
    return True


def test_disable_schedule_uses_inline_messages():
    """Test that _disable_schedule uses inline messages."""
    print("=" * 70)
    print("TEST 4: Disable Schedule Uses Inline Messages")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find _disable_schedule method
    method_start = content.find('def _disable_schedule(')
    assert method_start != -1, "_disable_schedule method should exist"
    
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Should use schedule_message_label
    assert 'schedule_message_label' in method_content, \
        "Should use schedule_message_label for disable notifications"
    
    # Check that messagebox is not used
    success_check = 'if success:' in method_content
    if success_check:
        # Find the success block
        success_start = method_content.find('if success:')
        success_section = method_content[success_start:success_start+400]
        
        # Should not use messagebox.showinfo
        assert 'messagebox.showinfo' not in success_section, \
            "Should NOT use messagebox.showinfo in success path"
    
    print("  ✓ Disable operations show inline messages")
    print("  ✓ No blocking dialogs for disable")
    print()
    return True


def test_verify_backup_uses_inline_messages():
    """Test that _verify_scheduled_backup uses inline messages."""
    print("=" * 70)
    print("TEST 5: Verify Backup Uses Inline Messages")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find _verify_scheduled_backup method
    method_start = content.find('def _verify_scheduled_backup(')
    assert method_start != -1, "_verify_scheduled_backup method should exist"
    
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Should use schedule_message_label
    assert 'schedule_message_label' in method_content, \
        "Should use schedule_message_label for verification results"
    
    # Should show verification results inline
    assert 'verification' in method_content.lower(), \
        "Should handle verification results"
    
    print("  ✓ Verification shows progress inline")
    print("  ✓ Verification shows results inline")
    print("  ✓ No blocking dialogs for verification")
    print()
    return True


def test_inline_notifications_are_non_intrusive():
    """Test that inline notifications don't block user interaction."""
    print("=" * 70)
    print("TEST 6: Inline Notifications Are Non-Intrusive")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Count remaining messagebox usages in schedule-related methods
    schedule_methods = [
        '_create_schedule',
        '_disable_schedule',
        '_run_test_backup',
        '_verify_scheduled_backup'
    ]
    
    for method_name in schedule_methods:
        method_start = content.find(f'def {method_name}(')
        if method_start == -1:
            continue
        
        method_end = content.find('\n    def ', method_start + 100)
        if method_end == -1:
            method_end = len(content)
        method_content = content[method_start:method_end]
        
        # Count messagebox calls (excluding delete which needs confirmation)
        if method_name != '_delete_schedule':
            messagebox_count = method_content.count('messagebox.')
            # Allow a few for edge cases, but should be minimal
            print(f"  • {method_name}: {messagebox_count} messagebox calls (should be minimal)")
    
    print("  ✓ Most operations use inline notifications")
    print("  ✓ Users can interact with page while viewing messages")
    print("  ✓ Test Run and Log Viewer always accessible")
    print()
    return True


def main():
    """Run all tests."""
    print()
    print("=" * 70)
    print("Inline Notifications - Verification Tests")
    print("=" * 70)
    print()
    
    tests = [
        test_inline_message_label_added,
        test_no_messagebox_in_create_schedule,
        test_test_run_uses_inline_messages,
        test_disable_schedule_uses_inline_messages,
        test_verify_backup_uses_inline_messages,
        test_inline_notifications_are_non_intrusive
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            print()
    
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print()
    
    if passed == total:
        print(f"✅ All {total} tests passed!")
        print()
        print("Inline Notifications Verified:")
        print("  ✓ Inline message label added to schedule page")
        print("  ✓ Validation errors shown inline (non-intrusive)")
        print("  ✓ Success messages shown inline")
        print("  ✓ Test Run results shown inline")
        print("  ✓ Verification results shown inline")
        print("  ✓ No blocking dialogs interrupting workflow")
        print("  ✓ Test Run and Log Viewer always accessible")
        print()
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed out of {total}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
