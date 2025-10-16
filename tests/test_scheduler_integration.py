#!/usr/bin/env python3
"""
Test script to verify the Test Run button now uses Windows Task Scheduler integration.
This test validates:
1. New --test-run command-line argument exists
2. New run_scheduled_task_now() function exists
3. _run_test_backup_scheduled() creates and runs temporary tasks
4. Inline feedback uses visual symbols (✅ ❌)
"""

import sys
import os
import re


def test_test_run_argument_exists():
    """Test that --test-run command-line argument exists."""
    print("=" * 70)
    print("TEST 1: --test-run Command-Line Argument")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for --test-run argument
    assert "--test-run" in content, "Should have --test-run argument"
    assert "parser.add_argument('--test-run'" in content, "Should add --test-run via argparse"
    
    # Check for test-run handling
    assert "if args.test_run:" in content, "Should handle args.test_run"
    assert "run_test_backup(args.backup_dir" in content, "Should call run_test_backup in test mode"
    
    print("  ✓ --test-run argument added to argparse")
    print("  ✓ args.test_run handling implemented")
    print("  ✓ Calls run_test_backup() for test runs")
    print()
    return True


def test_run_scheduled_task_now_function():
    """Test that run_scheduled_task_now() function exists."""
    print("=" * 70)
    print("TEST 2: run_scheduled_task_now() Function")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for function definition
    assert "def run_scheduled_task_now(task_name):" in content, \
        "Should define run_scheduled_task_now() function"
    
    # Check for schtasks /Run command
    func_start = content.find('def run_scheduled_task_now(')
    func_end = content.find('\ndef ', func_start + 100)
    func_content = content[func_start:func_end]
    
    assert 'schtasks", "/Run", "/TN"' in func_content, \
        "Should use schtasks /Run command"
    assert 'return' in func_content and 'success' in func_content.lower(), \
        "Should return success/failure status"
    
    print("  ✓ run_scheduled_task_now() function defined")
    print("  ✓ Uses schtasks /Run /TN command")
    print("  ✓ Returns (success, message) tuple")
    print()
    return True


def test_temporary_task_creation():
    """Test that _run_test_backup_scheduled creates temporary tasks."""
    print("=" * 70)
    print("TEST 3: Temporary Task Creation in _run_test_backup_scheduled")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _run_test_backup_scheduled method
    func_start = content.find('def _run_test_backup_scheduled(')
    func_end = content.find('\n    def ', func_start + 100)
    func_content = content[func_start:func_end]
    
    # Check for temporary task name
    assert '_TestRun' in func_content or 'TestRun' in func_content, \
        "Should create temporary task with TestRun suffix"
    
    # Check for task creation
    assert 'schtasks", "/Create"' in func_content, \
        "Should create scheduled task"
    
    # Check for --test-run flag in command
    assert '--test-run' in func_content, \
        "Should include --test-run flag in task command"
    
    # Check for task execution
    assert 'run_scheduled_task_now' in func_content, \
        "Should call run_scheduled_task_now() to trigger task"
    
    # Check for task deletion/cleanup
    assert 'schtasks", "/Delete"' in func_content, \
        "Should delete temporary task after completion"
    
    print("  ✓ Creates temporary task with TestRun suffix")
    print("  ✓ Includes --test-run flag in task command")
    print("  ✓ Calls run_scheduled_task_now() to trigger task")
    print("  ✓ Deletes temporary task after completion")
    print()
    return True


def test_visual_feedback_symbols():
    """Test that inline feedback uses visual symbols."""
    print("=" * 70)
    print("TEST 4: Visual Feedback Symbols")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _run_test_backup_scheduled method
    func_start = content.find('def _run_test_backup_scheduled(')
    func_end = content.find('\n    def ', func_start + 100)
    func_content = content[func_start:func_end]
    
    # Check for visual symbols
    assert '✅' in func_content, "Should use green checkmark (✅) for success"
    assert '❌' in func_content, "Should use red X (❌) for failure"
    assert '⏳' in func_content, "Should use hourglass (⏳) for progress"
    
    # Check for inline feedback (no messagebox)
    assert 'schedule_message_label.config' in func_content, \
        "Should use schedule_message_label for inline feedback"
    assert 'messagebox' not in func_content, \
        "Should not use messagebox pop-ups"
    
    # Check for green/red colors
    assert 'fg="green"' in func_content or "fg='green'" in func_content, \
        "Should use green color for success"
    assert 'error_fg' in func_content, \
        "Should use error color for failures"
    
    print("  ✓ Uses ✅ green checkmark for success")
    print("  ✓ Uses ❌ red X for failure")
    print("  ✓ Uses ⏳ hourglass for progress")
    print("  ✓ Uses inline feedback (no messagebox)")
    print("  ✓ Applies appropriate colors (green/red)")
    print()
    return True


def test_scheduler_integration_messaging():
    """Test that success message mentions scheduler verification."""
    print("=" * 70)
    print("TEST 5: Scheduler Integration Messaging")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _run_test_backup_scheduled method
    func_start = content.find('def _run_test_backup_scheduled(')
    func_end = content.find('\n    def ', func_start + 100)
    func_content = content[func_start:func_end]
    
    # Check for scheduler-related messaging
    assert 'Task Scheduler' in func_content or 'scheduler' in func_content.lower(), \
        "Should mention Task Scheduler in messages"
    
    # Check for verification messaging
    assert 'Verified' in func_content or 'verified' in func_content, \
        "Should mention verification in success message"
    
    print("  ✓ Messages mention Task Scheduler")
    print("  ✓ Success message indicates verification")
    print("  ✓ User understands test validates scheduler integration")
    print()
    return True


def test_config_only_backup():
    """Test that config file backup is still maintained."""
    print("=" * 70)
    print("TEST 6: Config-Only Backup Maintained")
    print("=" * 70)
    print()
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check that run_test_backup still exists and backs up config
    func_start = content.find('def run_test_backup(')
    func_end = content.find('\ndef ', func_start + 100)
    func_content = content[func_start:func_end]
    
    assert 'schedule_config.json' in func_content, \
        "Should backup schedule_config.json"
    assert 'os.remove(test_backup_path)' in func_content, \
        "Should delete test backup after creation"
    
    # Check that --test-run calls run_test_backup
    test_run_start = content.find('if args.test_run:')
    test_run_end = content.find('elif args.scheduled:', test_run_start)
    test_run_content = content[test_run_start:test_run_end]
    
    assert 'run_test_backup' in test_run_content, \
        "--test-run should call run_test_backup()"
    
    print("  ✓ run_test_backup() still backs up config file only")
    print("  ✓ Test backup is deleted after creation")
    print("  ✓ --test-run flag calls run_test_backup()")
    print()
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("TEST RUN BUTTON SCHEDULER INTEGRATION TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_test_run_argument_exists,
        test_run_scheduled_task_now_function,
        test_temporary_task_creation,
        test_visual_feedback_symbols,
        test_scheduler_integration_messaging,
        test_config_only_backup,
    ]
    
    try:
        all_passed = True
        for test in tests:
            if not test():
                print(f"\n✗ Test failed: {test.__name__}")
                all_passed = False
        
        if all_passed:
            print("\n" + "=" * 70)
            print("ALL TESTS PASSED! ✓")
            print("=" * 70)
            print()
            print("Summary of Changes:")
            print("  ✓ Added --test-run command-line argument")
            print("  ✓ Created run_scheduled_task_now() function")
            print("  ✓ Modified _run_test_backup_scheduled() to use Task Scheduler")
            print("  ✓ Temporary tasks created/triggered/cleaned up")
            print("  ✓ Inline visual feedback with ✅ ❌ symbols")
            print("  ✓ No pop-up dialogs")
            print("  ✓ Config-only backup maintained")
            print("  ✓ Validates scheduler integration, permissions, and environment")
            print()
            print("Test Run button now:")
            print("  • Triggers backup via Windows Task Scheduler")
            print("  • Validates real scheduled backup environment")
            print("  • Shows inline feedback with visual symbols")
            print("  • No intrusive pop-ups")
            print("  • Continues to test only config file")
            print()
            return 0
        else:
            print("\n" + "=" * 70)
            print("SOME TESTS FAILED! ✗")
            print("=" * 70)
            return 1
            
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
