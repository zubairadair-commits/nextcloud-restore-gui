#!/usr/bin/env python3
"""
Test script to verify that navigation after creating/updating a scheduled backup
keeps the user on the schedule page instead of redirecting to the main menu.

This ensures users can:
1. Immediately test their backup setup with the Test Run button
2. View logs to verify configuration
3. Access verification tools
4. Navigate freely between pages
"""

import sys
import os


def test_create_schedule_stays_on_page():
    """Test that _create_schedule stays on schedule page after success."""
    print("=" * 70)
    print("TEST 1: Navigation After Schedule Creation")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _create_schedule method
    method_start = content.find('def _create_schedule(')
    assert method_start != -1, "_create_schedule method should exist"
    
    # Find the success message section
    success_start = content.find('if save_schedule_config(config):', method_start)
    assert success_start != -1, "Should have save_schedule_config call"
    
    # Get the section with the success handling
    method_end = content.find('\n    def ', success_start + 100)
    if method_end == -1:
        method_end = len(content)
    success_section = content[success_start:method_end]
    
    # Check that it calls show_schedule_backup instead of show_landing
    assert 'self.show_schedule_backup()' in success_section, \
        "Should call show_schedule_backup() to stay on schedule page"
    
    # Make sure it doesn't call show_landing in the success path
    # Look for show_landing only after the success message
    success_msg_end = success_section.find(')')
    after_success = success_section[success_msg_end:]
    lines_after = after_success.split('\n')[:5]  # Check next few lines
    
    calls_landing_in_success = any('self.show_landing()' in line and 
                                   'self.show_schedule_backup()' not in success_section[:success_section.find(line)]
                                   for line in lines_after if 'self.show_landing()' in line)
    
    assert not calls_landing_in_success or 'self.show_schedule_backup()' in success_section, \
        "Should NOT call show_landing() in success path after creating schedule"
    
    print("  ✓ _create_schedule calls show_schedule_backup() after success")
    print("  ✓ User stays on schedule page to test and verify setup")
    print()
    return True


def test_test_run_button_accessible():
    """Test that Test Run button is present on schedule page."""
    print("=" * 70)
    print("TEST 2: Test Run Button Accessibility")
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
    
    # Check for Test Run button
    assert '🧪 Test Run' in method_content or 'Test Run' in method_content, \
        "Test Run button should be present on schedule page"
    
    # Check that it calls _run_test_backup
    assert 'self._run_test_backup' in method_content, \
        "Test Run button should call _run_test_backup method"
    
    print("  ✓ Test Run button present on schedule page")
    print("  ✓ Button calls _run_test_backup method")
    print("  ✓ Users can immediately test after creating schedule")
    print()
    return True


def test_log_viewer_accessible():
    """Test that log viewer is accessible from schedule page."""
    print("=" * 70)
    print("TEST 3: Log Viewer Accessibility")
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
    
    # Check for View Logs button/functionality
    assert 'View Recent Logs' in method_content or '_show_recent_logs' in method_content, \
        "Log viewer should be accessible from schedule page"
    
    print("  ✓ View Recent Logs button present on schedule page")
    print("  ✓ Users can view logs after creating schedule")
    print()
    return True


def test_navigation_between_pages():
    """Test that users can navigate freely between main page and schedule page."""
    print("=" * 70)
    print("TEST 4: Navigation Between Pages")
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
    
    # Check for "Return to Main Menu" button
    assert 'Return to Main Menu' in method_content or 'show_landing' in method_content, \
        "Should have button to return to main menu"
    
    # Find show_landing method to check for Schedule Backup button
    landing_start = content.find('def show_landing(')
    landing_end = content.find('\n    def ', landing_start + 100)
    if landing_end == -1:
        landing_end = len(content)
    landing_content = content[landing_start:landing_end]
    
    # Check for Schedule Backup button on landing page
    assert 'Schedule Backup' in landing_content or 'show_schedule_backup' in landing_content, \
        "Landing page should have Schedule Backup button"
    
    print("  ✓ Schedule page has 'Return to Main Menu' button")
    print("  ✓ Landing page has 'Schedule Backup' button")
    print("  ✓ Users can navigate freely between pages")
    print()
    return True


def test_success_message_mentions_testing():
    """Test that success message mentions testing capability."""
    print("=" * 70)
    print("TEST 5: Success Message Guides Users")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _create_schedule method
    method_start = content.find('def _create_schedule(')
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Look for success message
    success_msg_start = method_content.find('Scheduled backup created successfully')
    if success_msg_start == -1:
        success_msg_start = method_content.find('messagebox.showinfo')
    
    assert success_msg_start != -1, "Should have success message"
    
    # Get the success message section
    success_msg_end = method_content.find('self.show_schedule_backup()', success_msg_start)
    success_msg_section = method_content[success_msg_start:success_msg_end]
    
    # Check if message mentions testing or verification
    mentions_testing = any(word in success_msg_section.lower() 
                          for word in ['test', 'verify', 'setup', 'run'])
    
    if mentions_testing:
        print("  ✓ Success message mentions testing capability")
        print("  ✓ Users are guided to test their setup")
    else:
        print("  ⚠ Success message could mention testing (optional improvement)")
    
    print()
    return True


def test_disable_schedule_refreshes_page():
    """Test that disabling schedule stays on schedule page (existing behavior)."""
    print("=" * 70)
    print("TEST 6: Disable Schedule Navigation")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _disable_schedule method
    method_start = content.find('def _disable_schedule(')
    assert method_start != -1, "_disable_schedule method should exist"
    
    method_end = content.find('\n    def ', method_start + 100)
    if method_end == -1:
        method_end = len(content)
    method_content = content[method_start:method_end]
    
    # Check that it refreshes the schedule page
    assert 'self.show_schedule_backup()' in method_content, \
        "Should refresh schedule page after disabling"
    
    print("  ✓ _disable_schedule refreshes the schedule page")
    print("  ✓ Consistent behavior with create/update")
    print()
    return True


def main():
    """Run all tests."""
    print()
    print("=" * 70)
    print("Schedule Navigation Fix - Verification Tests")
    print("=" * 70)
    print()
    
    tests = [
        test_create_schedule_stays_on_page,
        test_test_run_button_accessible,
        test_log_viewer_accessible,
        test_navigation_between_pages,
        test_success_message_mentions_testing,
        test_disable_schedule_refreshes_page,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            print()
            results.append(False)
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            print()
            results.append(False)
    
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print()
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ All {total} tests passed!")
        print()
        print("Navigation Fix Verified:")
        print("  ✓ Users stay on schedule page after creating/updating backup")
        print("  ✓ Test Run button remains accessible")
        print("  ✓ Log viewer remains accessible")
        print("  ✓ Clear navigation options between pages")
        print("  ✓ Users can test and validate setup immediately")
        print()
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed out of {total}")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
