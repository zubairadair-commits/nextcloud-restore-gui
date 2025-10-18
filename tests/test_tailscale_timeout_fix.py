#!/usr/bin/env python3
"""
Test script to verify Tailscale timeout fix implementation.
Validates that _get_tailscale_info() uses the correct timeout and shutil.which().
"""

import sys
import os
import re

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_tailscale_timeout_fix():
    """Test that the timeout fix is properly implemented"""
    print("=" * 70)
    print("Tailscale Timeout Fix Verification Test")
    print("=" * 70)
    print()
    
    # Read the main file
    main_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             "src", "nextcloud_restore_and_backup-v9.py")
    
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    print(f"✓ Main file found: {main_file}")
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Test 1: Check for shutil.which() usage in _get_tailscale_info
    print("\nTest 1: Checking for shutil.which() usage...")
    if 'shutil.which("tailscale")' in content or "shutil.which('tailscale')" in content:
        print("✓ shutil.which('tailscale') is used")
    else:
        print("✗ shutil.which('tailscale') not found")
        all_passed = False
    
    # Test 2: Check for 15 second timeout in _get_tailscale_info
    print("\nTest 2: Checking for 15 second timeout...")
    # Extract the _get_tailscale_info method
    match = re.search(r'def _get_tailscale_info\(self\):.*?(?=\n    def |\Z)', content, re.DOTALL)
    if match:
        method_content = match.group(0)
        if 'timeout=15' in method_content:
            print("✓ timeout=15 is used in subprocess.run()")
        else:
            print("✗ timeout=15 not found in _get_tailscale_info")
            all_passed = False
    else:
        print("✗ _get_tailscale_info method not found")
        all_passed = False
    
    # Test 3: Check for enhanced error logging
    print("\nTest 3: Checking for enhanced error logging...")
    if 'logger.error' in method_content:
        # Count logger.error occurrences in the method
        error_log_count = method_content.count('logger.error')
        if error_log_count >= 2:
            print(f"✓ Enhanced error logging found ({error_log_count} logger.error calls)")
        else:
            print(f"⚠ Limited error logging found ({error_log_count} logger.error calls)")
            # This is not a failure, just a warning
    else:
        print("✗ No error logging found")
        all_passed = False
    
    # Test 4: Check for "Tailscale CLI not found. Please ensure Tailscale is installed and in your PATH."
    print("\nTest 4: Checking for detailed error messages...")
    if "Tailscale CLI not found. Please ensure Tailscale is installed and in your PATH." in method_content:
        print("✓ Detailed 'CLI not found' error message present")
    else:
        print("✗ Expected 'CLI not found' error message not found")
        all_passed = False
    
    # Test 5: Check for timeout error message
    print("\nTest 5: Checking for timeout error message...")
    if "Tailscale command timed out. The service may be unresponsive." in method_content:
        print("✓ Timeout error message present")
    else:
        print("✗ Timeout error message not found")
        all_passed = False
    
    # Test 6: Check that full error output is captured
    print("\nTest 6: Checking for stderr capture...")
    if 'stderr_output = result.stderr.strip()' in method_content or 'result.stderr.strip()' in method_content:
        print("✓ stderr output is captured")
    else:
        print("✗ stderr output capture not found")
        all_passed = False
    
    # Test 7: Verify the changes don't break Windows compatibility
    print("\nTest 7: Checking Windows compatibility...")
    if 'self._find_tailscale_exe()' in method_content and 'platform.system() == "Windows"' in method_content:
        print("✓ Windows compatibility maintained")
    else:
        print("✗ Windows compatibility check failed")
        all_passed = False
    
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print()
    
    if all_passed:
        print("✓ All tests passed!")
        print()
        print("Implementation verified:")
        print("  • shutil.which() is used for reliable executable location")
        print("  • Timeout increased to 15 seconds")
        print("  • Enhanced error logging implemented")
        print("  • Detailed error messages for all error scenarios")
        print("  • Full stderr output is captured and logged")
        print("  • Windows compatibility maintained")
        print()
    else:
        print("✗ Some tests failed. Please review the implementation.")
        print()
    
    return all_passed

if __name__ == '__main__':
    success = test_tailscale_timeout_fix()
    sys.exit(0 if success else 1)
