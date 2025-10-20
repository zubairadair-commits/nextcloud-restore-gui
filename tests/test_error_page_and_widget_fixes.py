#!/usr/bin/env python3
"""
Test for error page centering and safe widget update fixes.

This test validates that:
1. Error page centering is properly implemented with canvas window positioning
2. Safe widget update helper function exists and handles TclErrors
3. Widget updates in background threads use safe updates
4. Docker detection doesn't have hardcoded paths/usernames
5. TclError is caught separately from other exceptions in restore thread
"""

import os
import re
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_error_page_centering():
    """Test that error page has proper centering implementation."""
    
    print("=" * 70)
    print("TEST 1: Error Page Centering")
    print("=" * 70)
    print()
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    
    if not os.path.exists(file_path):
        print(f"✗ ERROR: File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    criteria = []
    
    # Check 1: Canvas window created with anchor="n" (north/top-center) instead of "nw" (northwest)
    if 'canvas_window = canvas.create_window((0, 0), window=error_frame, anchor="n")' in content:
        print("  ✓ Canvas window uses anchor='n' for centering (top-center)")
        criteria.append(True)
    else:
        print("  ✗ Canvas window does not use anchor='n'")
        criteria.append(False)
    
    # Check 2: Update function that centers content horizontally
    if 'def update_scroll_region' in content and 'x_position = max(0, (canvas_width - frame_width) // 2)' in content:
        print("  ✓ Update function calculates x_position for horizontal centering")
        criteria.append(True)
    else:
        print("  ✗ Horizontal centering logic not found")
        criteria.append(False)
    
    # Check 3: Canvas bind for recalculating position on resize
    if 'canvas.bind("<Configure>", update_scroll_region)' in content:
        print("  ✓ Canvas bound to update on resize for responsive centering")
        criteria.append(True)
    else:
        print("  ✗ Canvas resize binding not found")
        criteria.append(False)
    
    success = all(criteria)
    print()
    print(f"Error Page Centering: {'PASS ✓' if success else 'FAIL ✗'}")
    print()
    return success


def test_safe_widget_update_function():
    """Test that safe_widget_update helper function exists and is properly implemented."""
    
    print("=" * 70)
    print("TEST 2: Safe Widget Update Helper Function")
    print("=" * 70)
    print()
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    criteria = []
    
    # Check 1: Function exists
    if 'def safe_widget_update(widget, update_func, error_context=' in content:
        print("  ✓ safe_widget_update function exists")
        criteria.append(True)
    else:
        print("  ✗ safe_widget_update function not found")
        criteria.append(False)
    
    # Check 2: Checks widget existence
    if 'if not widget.winfo_exists():' in content:
        print("  ✓ Function checks widget existence with winfo_exists()")
        criteria.append(True)
    else:
        print("  ✗ Widget existence check not found")
        criteria.append(False)
    
    # Check 3: Catches TclError
    if 'except tk.TclError as e:' in content:
        print("  ✓ Function catches TclError specifically")
        criteria.append(True)
    else:
        print("  ✗ TclError exception handling not found")
        criteria.append(False)
    
    # Check 4: Logs debug messages for TclError
    if 'logger.debug(f"TclError during {error_context}:' in content:
        print("  ✓ TclError logged as debug (not error)")
        criteria.append(True)
    else:
        print("  ✗ TclError debug logging not found")
        criteria.append(False)
    
    success = all(criteria)
    print()
    print(f"Safe Widget Update Function: {'PASS ✓' if success else 'FAIL ✗'}")
    print()
    return success


def test_safe_widget_usage():
    """Test that widget updates use safe_widget_update in critical areas."""
    
    print("=" * 70)
    print("TEST 3: Safe Widget Update Usage")
    print("=" * 70)
    print()
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    criteria = []
    
    # Check 1: set_restore_progress uses safe_widget_update
    set_restore_progress_pattern = r'def set_restore_progress\(self.*?\n(.*?)\n    def '
    match = re.search(set_restore_progress_pattern, content, re.DOTALL)
    if match and 'safe_widget_update' in match.group(1):
        print("  ✓ set_restore_progress uses safe_widget_update")
        criteria.append(True)
    else:
        print("  ✗ set_restore_progress does not use safe_widget_update")
        criteria.append(False)
    
    # Check 2: auto_extract_backup uses safe_widget_update
    if content.count('safe_widget_update') >= 5:
        print(f"  ✓ safe_widget_update used {content.count('safe_widget_update')} times throughout the code")
        criteria.append(True)
    else:
        print(f"  ✗ safe_widget_update used only {content.count('safe_widget_update')} times (expected >= 5)")
        criteria.append(False)
    
    # Check 3: update_idletasks is wrapped in try-except
    if 'try:\n                if self.winfo_exists():\n                    self.update_idletasks()\n            except tk.TclError:' in content:
        print("  ✓ update_idletasks wrapped in try-except with winfo_exists check")
        criteria.append(True)
    else:
        print("  ✗ update_idletasks not properly protected")
        criteria.append(False)
    
    success = all(criteria)
    print()
    print(f"Safe Widget Usage: {'PASS ✓' if success else 'FAIL ✗'}")
    print()
    return success


def test_docker_detection_no_hardcoded_paths():
    """Test that Docker detection doesn't have hardcoded usernames or paths."""
    
    print("=" * 70)
    print("TEST 4: Docker Detection - No Hardcoded Paths")
    print("=" * 70)
    print()
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    criteria = []
    
    # Check 1: No $USER in Docker detection
    if '$USER' not in content:
        print("  ✓ No hardcoded $USER environment variable")
        criteria.append(True)
    else:
        print("  ✗ Hardcoded $USER found")
        criteria.append(False)
    
    # Check 2: Uses $(whoami) instead
    if '$(whoami)' in content:
        print("  ✓ Uses $(whoami) for dynamic username")
        criteria.append(True)
    else:
        print("  ✗ $(whoami) not found")
        criteria.append(False)
    
    # Check 3: Platform-specific messages exist
    if "platform.system() == 'Windows'" in content and "platform.system() == 'Linux'" in content:
        print("  ✓ Platform-specific error messages implemented")
        criteria.append(True)
    elif "platform.system() ==" in content and content.count("platform.system()") >= 3:
        print("  ✓ Platform-specific error messages implemented")
        criteria.append(True)
    else:
        print("  ✗ Platform-specific messages not found")
        criteria.append(False)
    
    success = all(criteria)
    print()
    print(f"Docker Detection (No Hardcoded Paths): {'PASS ✓' if success else 'FAIL ✗'}")
    print()
    return success


def test_tclerror_separate_handling():
    """Test that TclError is caught separately from other exceptions in restore thread."""
    
    print("=" * 70)
    print("TEST 5: TclError Separate Exception Handling")
    print("=" * 70)
    print()
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    criteria = []
    
    # Check 1: TclError caught before general Exception in restore thread
    pattern = r'except tk\.TclError as e:.*?except Exception as e:'
    if re.search(pattern, content, re.DOTALL):
        print("  ✓ TclError caught before general Exception (correct order)")
        criteria.append(True)
    else:
        print("  ✗ TclError not caught before general Exception")
        criteria.append(False)
    
    # Check 2: TclError handler logs info/debug, not error
    tclerror_pattern = r'except tk\.TclError.*?logger\.(info|debug)'
    if re.search(tclerror_pattern, content, re.DOTALL):
        print("  ✓ TclError logged as info/debug (not error)")
        criteria.append(True)
    else:
        print("  ✗ TclError not logged as info/debug")
        criteria.append(False)
    
    # Check 3: Comment explains TclError is expected behavior
    if 'Widget was destroyed - likely user closed window or navigated away' in content:
        print("  ✓ Comment explains TclError is expected behavior")
        criteria.append(True)
    else:
        print("  ✗ Explanatory comment not found")
        criteria.append(False)
    
    success = all(criteria)
    print()
    print(f"TclError Separate Handling: {'PASS ✓' if success else 'FAIL ✗'}")
    print()
    return success


def test_docker_detection_all_workflows():
    """Test that all workflows (backup/restore/new instance) check Docker."""
    
    print("=" * 70)
    print("TEST 6: Docker Detection in All Workflows")
    print("=" * 70)
    print()
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    criteria = []
    
    # Check 1: Backup workflow checks Docker
    backup_pattern = r'def start_backup\(self\):.*?if not self\.check_docker_running\(\):'
    if re.search(backup_pattern, content, re.DOTALL):
        print("  ✓ Backup workflow checks if Docker is running")
        criteria.append(True)
    else:
        print("  ✗ Backup workflow missing Docker check")
        criteria.append(False)
    
    # Check 2: Restore workflow checks Docker
    restore_pattern = r'def start_restore\(self\):.*?if not self\.check_docker_running\(\):'
    if re.search(restore_pattern, content, re.DOTALL):
        print("  ✓ Restore workflow checks if Docker is running")
        criteria.append(True)
    else:
        print("  ✗ Restore workflow missing Docker check")
        criteria.append(False)
    
    # Check 3: New instance workflow checks Docker
    new_instance_pattern = r'def start_new_instance_workflow\(self\):.*?if not self\.check_docker_running\(\):'
    if re.search(new_instance_pattern, content, re.DOTALL):
        print("  ✓ New instance workflow checks if Docker is running")
        criteria.append(True)
    else:
        print("  ✗ New instance workflow missing Docker check")
        criteria.append(False)
    
    success = all(criteria)
    print()
    print(f"Docker Detection in All Workflows: {'PASS ✓' if success else 'FAIL ✗'}")
    print()
    return success


def run_all_tests():
    """Run all tests and report overall result."""
    print("\n")
    print("*" * 70)
    print("ERROR PAGE AND WIDGET FIXES - COMPREHENSIVE TEST SUITE")
    print("*" * 70)
    print("\n")
    
    results = []
    
    results.append(test_error_page_centering())
    results.append(test_safe_widget_update_function())
    results.append(test_safe_widget_usage())
    results.append(test_docker_detection_no_hardcoded_paths())
    results.append(test_tclerror_separate_handling())
    results.append(test_docker_detection_all_workflows())
    
    print("=" * 70)
    print("OVERALL TEST RESULTS")
    print("=" * 70)
    print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ ALL TESTS PASSED")
        return True
    else:
        print("\n✗ SOME TESTS FAILED")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
