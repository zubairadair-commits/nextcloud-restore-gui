#!/usr/bin/env python3
"""
Test robocopy implementation to ensure:
1. Robocopy is used on Windows platforms
2. Recommended robocopy options are present (/E, /NFL, /NDL, /MT:8, /R:2, /W:2)
3. Fallback to file-by-file method exists for non-Windows platforms
4. Status messages indicate when robocopy is being used
5. Error handling and fallback for robocopy failures
"""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_robocopy_method_exists():
    """Test that _copy_folder_with_robocopy method exists"""
    print("Testing robocopy method existence...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for robocopy method
    if 'def _copy_folder_with_robocopy(' in source:
        print("  ✓ _copy_folder_with_robocopy method exists")
    else:
        print("  ✗ _copy_folder_with_robocopy method not found")
        return False
    
    return True


def test_robocopy_options():
    """Test that robocopy is called with recommended options"""
    print("\nTesting robocopy options...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for all required robocopy options
    required_options = ['/E', '/NFL', '/NDL', '/MT:8', '/R:2', '/W:2']
    missing_options = []
    
    for option in required_options:
        # Look for the option in the robocopy command
        if f"'{option}'" in source or f'"{option}"' in source:
            print(f"  ✓ Option {option} found")
        else:
            print(f"  ✗ Option {option} not found")
            missing_options.append(option)
    
    if missing_options:
        print(f"  ✗ Missing options: {', '.join(missing_options)}")
        return False
    
    return True


def test_platform_detection():
    """Test that platform detection is used to choose copy method"""
    print("\nTesting platform detection...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for platform detection in copy_folder_to_container_with_progress
    if "platform.system() == 'Windows'" in source:
        print("  ✓ Platform detection found")
    else:
        print("  ✗ Platform detection not found")
        return False
    
    # Check that robocopy method is called on Windows
    pattern = r"if is_windows:.*?_copy_folder_with_robocopy"
    if re.search(pattern, source, re.DOTALL):
        print("  ✓ Robocopy method called on Windows")
    else:
        print("  ✗ Robocopy method not properly dispatched")
        return False
    
    return True


def test_fallback_method_exists():
    """Test that file-by-file fallback method exists"""
    print("\nTesting fallback method...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for file-by-file method
    if 'def _copy_folder_file_by_file(' in source:
        print("  ✓ _copy_folder_file_by_file fallback method exists")
    else:
        print("  ✗ Fallback method not found")
        return False
    
    # Check that fallback is called on non-Windows
    pattern = r"else:.*?_copy_folder_file_by_file"
    if re.search(pattern, source, re.DOTALL):
        print("  ✓ Fallback method called on non-Windows platforms")
    else:
        print("  ✗ Fallback not properly configured")
        return False
    
    return True


def test_robocopy_error_handling():
    """Test that robocopy errors trigger fallback"""
    print("\nTesting robocopy error handling...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for robocopy exit code handling
    if 'result.returncode > 3' in source:
        print("  ✓ Robocopy exit code checking found")
    else:
        print("  ✗ Robocopy exit code checking not found")
        return False
    
    # Check that fallback is triggered on error
    pattern = r"if result\.returncode > 3:.*?_copy_folder_file_by_file"
    if re.search(pattern, source, re.DOTALL):
        print("  ✓ Fallback triggered on robocopy errors")
    else:
        print("  ✗ Fallback on error not found")
        return False
    
    return True


def test_status_messages():
    """Test that status messages indicate robocopy usage"""
    print("\nTesting status messages...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for robocopy-specific status messages
    robocopy_patterns = [
        'robocopy',
        'Using robocopy',
        'using robocopy'
    ]
    
    found_message = False
    for pattern in robocopy_patterns:
        if pattern.lower() in source.lower():
            print(f"  ✓ Status message mentioning robocopy found: '{pattern}'")
            found_message = True
            break
    
    if not found_message:
        print("  ✗ No status messages mentioning robocopy found")
        return False
    
    return True


def test_staging_directory_cleanup():
    """Test that staging directory is cleaned up"""
    print("\nTesting staging directory cleanup...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for staging directory creation
    if 'staging_dir' in source and 'nextcloud_copy_staging' in source:
        print("  ✓ Staging directory creation found")
    else:
        print("  ✗ Staging directory not found")
        return False
    
    # Check for cleanup
    if 'shutil.rmtree(staging_dir' in source:
        print("  ✓ Staging directory cleanup found")
    else:
        print("  ✗ Staging directory cleanup not found")
        return False
    
    return True


def test_docker_cp_single_folder():
    """Test that docker cp is used for entire folder transfer"""
    print("\nTesting docker cp strategy...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check that docker cp is used after robocopy in the robocopy method
    pattern = r"def _copy_folder_with_robocopy.*?docker cp.*?staging_folder_path"
    if re.search(pattern, source, re.DOTALL):
        print("  ✓ Docker cp used for folder transfer after robocopy")
    else:
        print("  ✗ Docker cp strategy not found in robocopy method")
        return False
    
    return True


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("ROBOCOPY IMPLEMENTATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_robocopy_method_exists,
        test_robocopy_options,
        test_platform_detection,
        test_fallback_method_exists,
        test_robocopy_error_handling,
        test_status_messages,
        test_staging_directory_cleanup,
        test_docker_cp_single_folder
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n  ✗ Test {test.__name__} raised exception: {e}")
            results.append((test.__name__, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
