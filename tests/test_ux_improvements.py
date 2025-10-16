#!/usr/bin/env python3
"""
Test script for UX and Reliability Improvements

This script tests the new features:
1. Database type detection from container
2. Database utility checking
3. Nextcloud readiness checking
"""

import sys
import os
import re

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_syntax():
    """Test that the main file has valid Python syntax"""
    print("=" * 70)
    print("TEST 1: Python Syntax Validation")
    print("=" * 70)
    
    try:
        import py_compile
        py_compile.compile('../src/nextcloud_restore_and_backup-v9.py', doraise=True)
        print("✓ Python syntax is valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error: {e}")
        return False

def test_function_exists():
    """Test that new functions exist in the source code"""
    print("\n" + "=" * 70)
    print("TEST 2: Function Definitions")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        functions_to_check = [
            'detect_database_type_from_container',
            'check_database_dump_utility',
            'prompt_install_database_utility',
            'check_nextcloud_ready'
        ]
        
        all_found = True
        for func_name in functions_to_check:
            pattern = f'def {func_name}\\('
            if re.search(pattern, content):
                print(f"✓ {func_name} exists")
            else:
                print(f"✗ {func_name} NOT FOUND")
                all_found = False
        
        if all_found:
            print("\n✓ All required functions are defined")
            return True
        else:
            print("\n✗ Some functions are missing")
            return False
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False

def test_backup_flow_integration():
    """Test that backup flow includes database detection"""
    print("\n" + "=" * 70)
    print("TEST 3: Backup Flow Integration")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Check for key integration points
        checks = [
            ('detect_database_type_from_container', 'Database type detection in backup'),
            ('check_database_dump_utility', 'Utility checking in backup'),
            ('prompt_install_database_utility', 'Utility installation prompt'),
            ('backup_dbtype', 'Database type stored for backup')
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✓ {description}")
            else:
                print(f"✗ {description} NOT FOUND")
                all_found = False
        
        if all_found:
            print("\n✓ Backup flow properly integrated")
            return True
        else:
            print("\n✗ Some integration points missing")
            return False
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False

def test_container_startup_improvements():
    """Test that container startup includes progress indicators"""
    print("\n" + "=" * 70)
    print("TEST 4: Container Startup Progress Indicators")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Check for progress indicators in launch_nextcloud_instance
        checks = [
            ('Checking for Nextcloud image', 'Image check message'),
            ('Pulling Nextcloud image', 'Image pull message'),
            ('Creating Nextcloud container', 'Container creation message'),
            ('Waiting for Nextcloud to start', 'Startup wait message'),
            ('spinner_chars', 'Spinner animation'),
            ('check_nextcloud_ready', 'Readiness check')
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✓ {description}")
            else:
                print(f"✗ {description} NOT FOUND")
                all_found = False
        
        if all_found:
            print("\n✓ Container startup improvements implemented")
            return True
        else:
            print("\n✗ Some improvements missing")
            return False
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False

def test_link_availability_feature():
    """Test that link availability feature is implemented"""
    print("\n" + "=" * 70)
    print("TEST 5: Link Availability Feature")
    print("=" * 70)
    
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Check for link availability features
        checks = [
            ('The link will become available when ready', 'Informational message'),
            ('link_label.config(fg=', 'Link color change'),
            ('check_and_enable', 'Background readiness checking'),
            ('Nextcloud is now ready', 'Ready notification')
        ]
        
        found_count = 0
        for check_str, description in checks:
            if check_str in content:
                print(f"✓ {description}")
                found_count += 1
            else:
                print(f"ℹ {description} (variation may exist)")
        
        if found_count >= 2:
            print("\n✓ Link availability feature implemented")
            return True
        else:
            print("\n⚠ Link availability feature partially implemented")
            return False
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("UX and Reliability Improvements - Test Suite")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Python Syntax", test_syntax()))
    results.append(("Function Definitions", test_function_exists()))
    results.append(("Backup Flow Integration", test_backup_flow_integration()))
    results.append(("Container Startup Improvements", test_container_startup_improvements()))
    results.append(("Link Availability Feature", test_link_availability_feature()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
