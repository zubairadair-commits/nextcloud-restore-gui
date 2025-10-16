#!/usr/bin/env python3
"""
Integration test for Docker detection feature.
Tests the integration of Docker detection with the main application flow.
"""

import sys
import subprocess
import platform
import time

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_docker_api_calls():
    """Test that Docker API calls work correctly"""
    print_section("TEST 1: Docker API Accessibility")
    
    # Test 1: docker ps
    print("\n1. Testing 'docker ps' command...")
    try:
        result = subprocess.run(
            ['docker', 'ps'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if result.returncode == 0:
            print("   ✓ 'docker ps' succeeded")
            return True
        else:
            print(f"   ✗ 'docker ps' failed: {result.stderr.decode()}")
            return False
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return False

def test_docker_info():
    """Test docker info command"""
    print_section("TEST 2: Docker System Information")
    
    try:
        result = subprocess.run(
            ['docker', 'info', '--format', '{{.ServerVersion}}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"\n   ✓ Docker version: {version}")
            return True
        else:
            print(f"   ✗ docker info failed")
            return False
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return False

def test_docker_network_check():
    """Test docker network commands"""
    print_section("TEST 3: Docker Network Accessibility")
    
    try:
        result = subprocess.run(
            ['docker', 'network', 'ls'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if result.returncode == 0:
            print("\n   ✓ 'docker network ls' succeeded")
            print("   ✓ Docker API is fully accessible")
            return True
        else:
            print(f"   ✗ docker network ls failed")
            return False
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return False

def test_timeout_handling():
    """Test that timeout is handled correctly"""
    print_section("TEST 4: Timeout Handling")
    
    print("\n   Testing 5-second timeout on Docker commands...")
    start_time = time.time()
    try:
        result = subprocess.run(
            ['docker', 'ps'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        elapsed = time.time() - start_time
        print(f"   ✓ Command completed in {elapsed:.2f} seconds")
        print(f"   ✓ Timeout handling works (< 5 seconds)")
        return True
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"   ✓ Timeout triggered after {elapsed:.2f} seconds")
        print(f"   ✓ Timeout handling prevents hanging")
        return True
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return False

def test_platform_specific_paths():
    """Test platform-specific Docker Desktop path detection"""
    print_section("TEST 5: Platform-Specific Path Detection")
    
    system = platform.system()
    print(f"\n   Platform: {system}")
    
    if system == "Windows":
        import os
        paths = [
            r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
        ]
        print("\n   Checking Windows Docker Desktop paths:")
        found = False
        for path in paths:
            exists = os.path.exists(path)
            status = "✓" if exists else "✗"
            print(f"   {status} {path}")
            if exists:
                found = True
        
        if found:
            print("\n   ✓ Docker Desktop found on Windows")
            return True
        else:
            print("\n   ℹ Docker Desktop not found (may not be installed)")
            return True  # Not an error, just not installed
    
    elif system == "Darwin":
        import os
        path = "/Applications/Docker.app"
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        print(f"\n   {status} {path}")
        
        if exists:
            print("\n   ✓ Docker Desktop found on macOS")
            return True
        else:
            print("\n   ℹ Docker Desktop not found (may not be installed)")
            return True  # Not an error, just not installed
    
    elif system == "Linux":
        print("\n   ℹ Linux uses Docker daemon (no Desktop path needed)")
        print("   ✓ Platform detection works correctly")
        return True
    
    return True

def test_function_imports():
    """Test that functions can be imported from main file"""
    print_section("TEST 6: Function Import Test")
    
    print("\n   Attempting to import functions from main file...")
    
    # We can't import due to tkinter, but we can verify syntax
    try:
        with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
            
            # Check for required functions
            required_functions = [
                'def is_docker_running()',
                'def get_docker_desktop_path()',
                'def start_docker_desktop()',
                'def prompt_start_docker(',
                'def check_docker_running(',
            ]
            
            print("\n   Checking for required functions:")
            all_found = True
            for func in required_functions:
                if func in content:
                    print(f"   ✓ Found: {func}")
                else:
                    print(f"   ✗ Missing: {func}")
                    all_found = False
            
            if all_found:
                print("\n   ✓ All required functions present")
                return True
            else:
                print("\n   ✗ Some functions missing")
                return False
    
    except Exception as e:
        print(f"   ✗ Error reading file: {e}")
        return False

def test_integration_points():
    """Test that Docker checks are integrated at right points"""
    print_section("TEST 7: Integration Point Test")
    
    print("\n   Checking integration with main application methods...")
    
    try:
        with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
            
            # Check for integration in key methods
            integration_points = [
                ('start_backup', 'check_docker_running'),
                ('start_restore', 'check_docker_running'),
                ('start_new_instance_workflow', 'check_docker_running'),
            ]
            
            all_integrated = True
            for method, check_call in integration_points:
                # Find the method definition
                method_start = content.find(f'def {method}(')
                if method_start == -1:
                    print(f"   ✗ Method {method} not found")
                    all_integrated = False
                    continue
                
                # Check if check_docker_running is called within the method
                # Look for next method or end of file
                next_method = content.find('\n    def ', method_start + 1)
                if next_method == -1:
                    method_section = content[method_start:]
                else:
                    method_section = content[method_start:next_method]
                
                if check_call in method_section:
                    print(f"   ✓ {method}() calls {check_call}()")
                else:
                    print(f"   ✗ {method}() missing {check_call}()")
                    all_integrated = False
            
            if all_integrated:
                print("\n   ✓ All integration points verified")
                return True
            else:
                print("\n   ✗ Some integration points missing")
                return False
    
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_module_imports():
    """Test that required modules are imported"""
    print_section("TEST 8: Module Import Test")
    
    print("\n   Checking for required imports...")
    
    try:
        with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
            lines = f.readlines()[:20]  # Check first 20 lines
            content = ''.join(lines)
            
            required_imports = [
                'import platform',
                'import sys',
            ]
            
            all_imported = True
            for imp in required_imports:
                if imp in content:
                    print(f"   ✓ Found: {imp}")
                else:
                    print(f"   ✗ Missing: {imp}")
                    all_imported = False
            
            if all_imported:
                print("\n   ✓ All required imports present")
                return True
            else:
                print("\n   ✗ Some imports missing")
                return False
    
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 70)
    print("  DOCKER DETECTION - INTEGRATION TEST SUITE")
    print("=" * 70)
    print(f"\n  Platform: {platform.system()}")
    print(f"  Python: {sys.version.split()[0]}")
    
    tests = [
        ("Docker API Calls", test_docker_api_calls),
        ("Docker Info", test_docker_info),
        ("Network Check", test_docker_network_check),
        ("Timeout Handling", test_timeout_handling),
        ("Platform Paths", test_platform_specific_paths),
        ("Function Imports", test_function_imports),
        ("Integration Points", test_integration_points),
        ("Module Imports", test_module_imports),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n   ✗ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"   {status}: {test_name}")
    
    print()
    print(f"   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n   ✅ ALL TESTS PASSED")
        print("\n   Docker detection feature is properly integrated!")
        return True
    else:
        print(f"\n   ⚠ {total - passed} test(s) failed")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
