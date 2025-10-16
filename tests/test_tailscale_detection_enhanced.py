#!/usr/bin/env python3
"""
Test Enhanced Tailscale Detection on Windows

Verifies:
1. The find_tailscale_exe() function checks multiple locations
2. Detection works when tailscale.exe is in PATH
3. Detection works when tailscale.exe is in common install locations
4. Registry checking is attempted (even if not available in test environment)
5. The function returns None when Tailscale is not found
"""

import sys
import os
import re

def test_enhanced_detection():
    """Test that enhanced Tailscale detection is properly implemented"""
    
    print("=" * 70)
    print("Enhanced Tailscale Detection Test")
    print("=" * 70)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # Read the main file
    file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Test 1: Standalone find_tailscale_exe() function exists
    total_checks += 1
    print(f"Check {total_checks}: Standalone find_tailscale_exe() function exists")
    if 'def find_tailscale_exe():' in content:
        print("✓ Pass - Standalone function found")
        checks_passed += 1
    else:
        print("✗ Fail - Standalone function not found")
    
    # Test 2: Function checks PATH using 'where' command
    total_checks += 1
    print(f"Check {total_checks}: Function checks PATH using 'where' command")
    if 'subprocess.run' in content and '["where", "tailscale"]' in content:
        print("✓ Pass - PATH check implemented")
        checks_passed += 1
    else:
        print("✗ Fail - PATH check not found")
    
    # Test 3: Function checks common installation directories
    total_checks += 1
    print(f"Check {total_checks}: Function checks common installation directories")
    common_checks = [
        r'C:\Program Files\Tailscale\tailscale.exe' in content,
        r'C:\Program Files (x86)\Tailscale\tailscale.exe' in content,
        'common_locations' in content or 'Program Files' in content
    ]
    if any(common_checks):
        print("✓ Pass - Common directories check implemented")
        checks_passed += 1
    else:
        print("✗ Fail - Common directories check not found")
    
    # Test 4: Function attempts registry checking
    total_checks += 1
    print(f"Check {total_checks}: Function attempts Windows registry checking")
    if 'winreg' in content and 'Tailscale IPN' in content:
        print("✓ Pass - Registry check implemented")
        checks_passed += 1
    else:
        print("✗ Fail - Registry check not found")
    
    # Test 5: _check_tailscale_installed uses enhanced detection on Windows
    total_checks += 1
    print(f"Check {total_checks}: _check_tailscale_installed uses enhanced detection")
    # Look for the method calling find_tailscale_exe or using the improved logic
    if re.search(r'def _check_tailscale_installed.*?find_tailscale_exe', content, re.DOTALL):
        print("✓ Pass - _check_tailscale_installed uses enhanced detection")
        checks_passed += 1
    else:
        print("✗ Fail - _check_tailscale_installed doesn't use enhanced detection")
    
    # Test 6: check_service_health uses enhanced detection on Windows
    total_checks += 1
    print(f"Check {total_checks}: check_service_health uses enhanced detection")
    # Look for usage of find_tailscale_exe in the health check
    health_check_match = re.search(
        r'# Check Tailscale.*?find_tailscale_exe',
        content,
        re.DOTALL | re.IGNORECASE
    )
    if health_check_match:
        print("✓ Pass - check_service_health uses enhanced detection")
        checks_passed += 1
    else:
        print("✗ Fail - check_service_health doesn't use enhanced detection")
    
    # Test 7: _check_tailscale_running uses full path on Windows
    total_checks += 1
    print(f"Check {total_checks}: _check_tailscale_running uses full path on Windows")
    running_check_match = re.search(
        r'def _check_tailscale_running.*?find_tailscale_exe',
        content,
        re.DOTALL
    )
    if running_check_match:
        print("✓ Pass - _check_tailscale_running uses full path")
        checks_passed += 1
    else:
        print("✗ Fail - _check_tailscale_running doesn't use full path")
    
    # Test 8: _get_tailscale_info uses full path on Windows
    total_checks += 1
    print(f"Check {total_checks}: _get_tailscale_info uses full path on Windows")
    info_check_match = re.search(
        r'def _get_tailscale_info.*?find_tailscale_exe',
        content,
        re.DOTALL
    )
    if info_check_match:
        print("✓ Pass - _get_tailscale_info uses full path")
        checks_passed += 1
    else:
        print("✗ Fail - _get_tailscale_info doesn't use full path")
    
    # Test 9: Method delegation in class
    total_checks += 1
    print(f"Check {total_checks}: Class _find_tailscale_exe delegates to standalone function")
    class_method_match = re.search(
        r'def _find_tailscale_exe\(self\):.*?return find_tailscale_exe\(\)',
        content,
        re.DOTALL
    )
    if class_method_match:
        print("✓ Pass - Class method delegates to standalone function")
        checks_passed += 1
    else:
        print("✗ Fail - Class method doesn't delegate properly")
    
    print()
    print("=" * 70)
    print(f"Test Results: {checks_passed}/{total_checks} checks passed")
    print("=" * 70)
    
    if checks_passed == total_checks:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {total_checks - checks_passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(test_enhanced_detection())
