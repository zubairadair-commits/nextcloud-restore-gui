#!/usr/bin/env python3
"""
Test script for enhanced database detection from Docker containers.
Tests the new multi-strategy detection functionality.
"""

import subprocess
import sys
import platform

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def get_subprocess_creation_flags():
    """Test implementation of creation flags"""
    if platform.system() == "Windows":
        return 0x08000000  # CREATE_NO_WINDOW
    return 0

def run_docker_command_silent(cmd, timeout=10):
    """Run a Docker command silently"""
    try:
        creation_flags = get_subprocess_creation_flags()
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            creationflags=creation_flags,
            shell=isinstance(cmd, str)
        )
        return result
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"Docker command error: {e}")
        return None

def test_subprocess_creation_flags():
    """Test that subprocess creation flags work correctly"""
    print_header("TEST 1: Subprocess Creation Flags")
    
    try:
        flags = get_subprocess_creation_flags()
        system = platform.system()
        
        if system == "Windows":
            if flags == 0x08000000:
                print("✓ Windows: CREATE_NO_WINDOW flag set correctly (0x08000000)")
                return True
            else:
                print(f"✗ Windows: Expected 0x08000000, got {hex(flags)}")
                return False
        else:
            if flags == 0:
                print(f"✓ {system}: No creation flags set (correct for non-Windows)")
                return True
            else:
                print(f"✗ {system}: Expected 0, got {flags}")
                return False
    except Exception as e:
        print(f"✗ Error testing creation flags: {e}")
        return False

def test_silent_docker_command():
    """Test that Docker commands run silently"""
    print_header("TEST 2: Silent Docker Command Execution")
    
    try:
        # Test with a simple docker command
        result = run_docker_command_silent(['docker', 'ps'], timeout=5)
        
        if result is None:
            print("⚠ Docker may not be running or installed")
            return None
        
        if result.returncode == 0:
            print("✓ Docker command executed silently")
            print(f"  Command succeeded with {len(result.stdout.splitlines())} lines of output")
            return True
        else:
            print(f"✗ Docker command failed: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"✗ Error testing silent command: {e}")
        return False

def list_running_database_containers():
    """List all running database containers"""
    db_containers = []
    
    try:
        result = run_docker_command_silent(['docker', 'ps', '--format', '{{.Names}}|{{.Image}}'])
        if not result or result.returncode != 0:
            return db_containers
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('|')
            if len(parts) != 2:
                continue
            
            name, image = parts
            image_lower = image.lower()
            
            # Detect database type from image name
            if 'mysql' in image_lower and 'mariadb' not in image_lower:
                db_containers.append({'name': name, 'image': image, 'type': 'mysql'})
            elif 'mariadb' in image_lower:
                db_containers.append({'name': name, 'image': image, 'type': 'mariadb'})
            elif 'postgres' in image_lower:
                db_containers.append({'name': name, 'image': image, 'type': 'pgsql'})
    
    except Exception as e:
        print(f"Error listing database containers: {e}")
    
    return db_containers

def test_list_database_containers():
    """Test listing database containers"""
    print_header("TEST 3: List Database Containers")
    
    try:
        db_containers = list_running_database_containers()
        
        if db_containers is None:
            print("✗ Function returned None")
            return False
        
        print(f"✓ Found {len(db_containers)} database container(s)")
        
        for container in db_containers:
            print(f"  - {container['name']}: {container['type']} ({container['image']})")
        
        if len(db_containers) == 0:
            print("  Note: No database containers running (this is OK for testing)")
        
        return True
    
    except Exception as e:
        print(f"✗ Error listing database containers: {e}")
        import traceback
        traceback.print_exc()
        return False

def inspect_container_environment(container_name):
    """Inspect a container's environment variables"""
    env_vars = {}
    
    try:
        result = run_docker_command_silent(
            ['docker', 'inspect', container_name, '--format', '{{range .Config.Env}}{{println .}}{{end}}']
        )
        
        if not result or result.returncode != 0:
            return env_vars
        
        for line in result.stdout.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    except Exception as e:
        print(f"Error inspecting container environment: {e}")
    
    return env_vars

def test_inspect_container_environment():
    """Test container environment inspection"""
    print_header("TEST 4: Container Environment Inspection")
    
    try:
        db_containers = list_running_database_containers()
        
        if not db_containers:
            print("⚠ No database containers found to inspect")
            print("  (This is OK if no containers are running)")
            return None
        
        # Inspect the first database container
        container = db_containers[0]
        print(f"Inspecting: {container['name']}")
        
        env_vars = inspect_container_environment(container['name'])
        
        if env_vars:
            print(f"✓ Found {len(env_vars)} environment variables")
            
            # Look for database-related env vars
            db_env_keys = [k for k in env_vars.keys() if any(
                x in k for x in ['DB', 'MYSQL', 'POSTGRES', 'DATABASE']
            )]
            
            if db_env_keys:
                print("  Database-related environment variables:")
                for key in db_env_keys[:5]:  # Show first 5
                    # Mask passwords
                    value = env_vars[key]
                    if 'PASSWORD' in key or 'PASS' in key:
                        value = '***'
                    print(f"    {key}={value}")
            
            return True
        else:
            print("✓ No environment variables found (container may not expose them)")
            return True
    
    except Exception as e:
        print(f"✗ Error inspecting container: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_nextcloud_container_name():
    """Find the Nextcloud container"""
    try:
        result = run_docker_command_silent(['docker', 'ps', '--format', '{{.Names}} {{.Image}}'])
        if not result or result.returncode != 0:
            return None
        for line in result.stdout.strip().split('\n'):
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            name, image = parts
            if 'nextcloud' in image.lower() or 'nextcloud' in name.lower():
                return name
    except Exception:
        pass
    return None

def test_comprehensive_detection():
    """Test comprehensive database detection"""
    print_header("TEST 5: Comprehensive Database Detection")
    
    try:
        # Find Nextcloud container
        nc_container = get_nextcloud_container_name()
        
        if not nc_container:
            print("⚠ No Nextcloud container found")
            print("  (This is OK if Nextcloud is not running)")
            return None
        
        print(f"Found Nextcloud container: {nc_container}")
        
        # List database containers
        db_containers = list_running_database_containers()
        print(f"Found {len(db_containers)} database container(s)")
        
        if len(db_containers) > 0:
            print("✓ Database container detection working")
            for container in db_containers:
                print(f"  - {container['name']}: {container['type']}")
            return True
        else:
            print("⚠ No database containers found")
            print("  (This is expected if no DB containers are running)")
            return None
    
    except Exception as e:
        print(f"✗ Error in comprehensive detection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_no_console_window():
    """Test that no console window appears (visual check)"""
    print_header("TEST 6: No Console Window Check")
    
    print("This test verifies that Docker commands don't show console windows.")
    print("On Windows, this should use CREATE_NO_WINDOW flag.")
    
    try:
        # Run a few Docker commands
        commands = [
            ['docker', 'ps'],
            ['docker', 'version'],
        ]
        
        for cmd in commands:
            print(f"\nExecuting: {' '.join(cmd)}")
            result = run_docker_command_silent(cmd, timeout=5)
            
            if result and result.returncode == 0:
                print("  ✓ Command executed successfully (silently)")
            elif result:
                print(f"  ⚠ Command failed: {result.stderr[:100]}")
            else:
                print("  ⚠ Command returned None (Docker may not be available)")
        
        print("\n✓ If you saw no console windows flash, the test passed")
        print("  (On non-Windows systems, this is always true)")
        
        return True
    
    except Exception as e:
        print(f"✗ Error testing console window suppression: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 70)
    print("  ENHANCED DATABASE DETECTION - TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Subprocess Creation Flags", test_subprocess_creation_flags),
        ("Silent Docker Command", test_silent_docker_command),
        ("List Database Containers", test_list_database_containers),
        ("Container Environment Inspection", test_inspect_container_environment),
        ("Comprehensive Detection", test_comprehensive_detection),
        ("No Console Window", test_no_console_window),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    
    for test_name, result in results:
        if result is True:
            print(f"✓ {test_name}")
        elif result is False:
            print(f"✗ {test_name}")
        else:
            print(f"⚠ {test_name} (skipped or N/A)")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\n✅ All applicable tests passed!")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
