#!/usr/bin/env python3
"""
Unit tests for comprehensive Docker status detection functionality.
Tests the detect_docker_status() logic without importing the full GUI app.
"""

import sys
import subprocess
import platform
from unittest.mock import Mock, patch


def get_subprocess_creation_flags():
    """Get subprocess creation flags for Windows (prevent console window)"""
    return 0x08000000 if platform.system() == 'Windows' else 0


def detect_docker_status():
    """
    Comprehensive Docker detection that checks installation and running status.
    This is a copy of the function from the main app for testing purposes.
    """
    try:
        creation_flags = get_subprocess_creation_flags()
        
        result = subprocess.run(
            ['docker', 'ps'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
            creationflags=creation_flags
        )
        
        if result.returncode == 0:
            return {
                'status': 'running',
                'message': 'Docker is running',
                'suggested_action': None,
                'stderr': ''
            }
        
        stderr_lower = result.stderr.lower()
        system = platform.system()
        
        if 'permission denied' in stderr_lower or 'access denied' in stderr_lower:
            if system == 'Windows':
                suggested_action = (
                    "Run this application as Administrator:\n"
                    "1. Right-click the application\n"
                    "2. Select 'Run as Administrator'"
                )
            elif system == 'Linux':
                suggested_action = (
                    "Add your user to the docker group:\n"
                    "  sudo usermod -aG docker $USER\n\n"
                    "Then log out and log back in."
                )
            else:
                suggested_action = "Ensure Docker Desktop is running and you have proper permissions."
            
            return {
                'status': 'permission_denied',
                'message': 'Permission denied - insufficient privileges to access Docker',
                'suggested_action': suggested_action,
                'stderr': result.stderr
            }
        
        if ('cannot connect' in stderr_lower or 
            'is not running' in stderr_lower or 
            'daemon' in stderr_lower or
            'connect' in stderr_lower):
            
            if system == 'Windows':
                suggested_action = "Start Docker Desktop from the Start menu"
            elif system == 'Darwin':
                suggested_action = "Start Docker Desktop from Applications"
            else:
                suggested_action = "Start the Docker daemon:\n  sudo systemctl start docker"
            
            return {
                'status': 'not_running',
                'message': 'Docker is not running',
                'suggested_action': suggested_action,
                'stderr': result.stderr
            }
        
        return {
            'status': 'error',
            'message': 'Docker command failed with an unexpected error',
            'suggested_action': 'Try restarting Docker',
            'stderr': result.stderr
        }
        
    except FileNotFoundError:
        system = platform.system()
        
        if system == 'Windows':
            suggested_action = (
                "To install Docker Desktop:\n"
                "1. Visit https://www.docker.com/products/docker-desktop/\n"
                "2. Download Docker Desktop for Windows"
            )
        elif system == 'Darwin':
            suggested_action = (
                "To install Docker Desktop:\n"
                "1. Visit https://www.docker.com/products/docker-desktop/\n"
                "2. Download Docker Desktop for Mac"
            )
        else:
            suggested_action = (
                "To install Docker on Linux:\n"
                "  sudo apt-get install docker.io"
            )
        
        return {
            'status': 'not_installed',
            'message': 'Docker is not installed or not found in system PATH',
            'suggested_action': suggested_action,
            'stderr': ''
        }
    
    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'message': 'Docker command timed out',
            'suggested_action': 'Docker is starting up - wait and try again',
            'stderr': ''
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Unexpected error while checking Docker: {str(e)}',
            'suggested_action': 'Try restarting Docker',
            'stderr': str(e)
        }


def is_docker_running():
    """
    Check if Docker daemon is running.
    Returns: True if Docker is running, False otherwise
    """
    status = detect_docker_status()
    return status['status'] == 'running'


def test_docker_running_success():
    """Test detection when Docker is running successfully"""
    print("\n" + "=" * 60)
    print("Test: Docker Running Successfully")
    print("=" * 60)
    
    # Mock successful docker ps command
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS   PORTS   NAMES\n"
    mock_result.stderr = ""
    
    with patch('subprocess.run', return_value=mock_result):
        status = detect_docker_status()
        
        assert status['status'] == 'running', f"Expected 'running', got '{status['status']}'"
        assert status['message'] == 'Docker is running'
        assert status['suggested_action'] is None
        print("✓ Docker running detection test passed")
        print(f"  Status: {status['status']}")
        print(f"  Message: {status['message']}")


def test_docker_permission_denied():
    """Test detection of permission denied errors"""
    print("\n" + "=" * 60)
    print("Test: Permission Denied Error")
    print("=" * 60)
    
    # Mock permission denied error
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "permission denied while trying to connect to the Docker daemon socket"
    
    with patch('subprocess.run', return_value=mock_result):
        status = detect_docker_status()
        
        assert status['status'] == 'permission_denied', f"Expected 'permission_denied', got '{status['status']}'"
        assert 'permission' in status['message'].lower()
        assert status['suggested_action'] is not None
        assert len(status['suggested_action']) > 0
        print("✓ Permission denied detection test passed")
        print(f"  Status: {status['status']}")
        print(f"  Message: {status['message']}")
        print(f"  Suggested action (first 100 chars): {status['suggested_action'][:100]}...")


def test_docker_not_running():
    """Test detection when Docker daemon is not running"""
    print("\n" + "=" * 60)
    print("Test: Docker Not Running")
    print("=" * 60)
    
    # Mock Docker not running error
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?"
    
    with patch('subprocess.run', return_value=mock_result):
        status = detect_docker_status()
        
        assert status['status'] == 'not_running', f"Expected 'not_running', got '{status['status']}'"
        assert 'not running' in status['message'].lower()
        assert status['suggested_action'] is not None
        print("✓ Docker not running detection test passed")
        print(f"  Status: {status['status']}")
        print(f"  Message: {status['message']}")
        print(f"  Suggested action (first 100 chars): {status['suggested_action'][:100]}...")


def test_docker_not_installed():
    """Test detection when Docker is not installed"""
    print("\n" + "=" * 60)
    print("Test: Docker Not Installed")
    print("=" * 60)
    
    # Mock FileNotFoundError when docker command is not found
    with patch('subprocess.run', side_effect=FileNotFoundError("docker command not found")):
        status = detect_docker_status()
        
        assert status['status'] == 'not_installed', f"Expected 'not_installed', got '{status['status']}'"
        assert 'not installed' in status['message'].lower() or 'not found' in status['message'].lower()
        assert status['suggested_action'] is not None
        assert 'docker.com' in status['suggested_action'].lower() or 'install' in status['suggested_action'].lower()
        print("✓ Docker not installed detection test passed")
        print(f"  Status: {status['status']}")
        print(f"  Message: {status['message']}")
        print(f"  Suggested action (first 150 chars): {status['suggested_action'][:150]}...")


def test_docker_timeout():
    """Test detection when Docker command times out"""
    print("\n" + "=" * 60)
    print("Test: Docker Command Timeout")
    print("=" * 60)
    
    # Mock timeout error
    with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('docker', 5)):
        status = detect_docker_status()
        
        assert status['status'] == 'error', f"Expected 'error', got '{status['status']}'"
        assert 'timeout' in status['message'].lower() or 'timed out' in status['message'].lower()
        assert status['suggested_action'] is not None
        print("✓ Docker timeout detection test passed")
        print(f"  Status: {status['status']}")
        print(f"  Message: {status['message']}")


def test_platform_specific_suggestions():
    """Test that suggestions are platform-specific"""
    print("\n" + "=" * 60)
    print("Test: Platform-Specific Suggestions")
    print("=" * 60)
    
    current_platform = platform.system()
    print(f"Current platform: {current_platform}")
    
    # Test not running error with platform-specific suggestions
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Cannot connect to the Docker daemon"
    
    with patch('subprocess.run', return_value=mock_result):
        status = detect_docker_status()
        
        if current_platform == 'Windows':
            assert 'Docker Desktop' in status['suggested_action']
            assert 'Start menu' in status['suggested_action'] or 'Administrator' in status['suggested_action']
        elif current_platform == 'Darwin':
            assert 'Docker Desktop' in status['suggested_action']
            assert 'Applications' in status['suggested_action']
        elif current_platform == 'Linux':
            assert 'systemctl' in status['suggested_action'] or 'docker' in status['suggested_action']
        
        print("✓ Platform-specific suggestions test passed")
        print(f"  Platform: {current_platform}")
        print(f"  Suggested action contains platform-specific instructions")


def test_is_docker_running_compatibility():
    """Test that is_docker_running() still works and uses detect_docker_status()"""
    print("\n" + "=" * 60)
    print("Test: is_docker_running() Backward Compatibility")
    print("=" * 60)
    
    # Test when Docker is running
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""
    
    with patch('subprocess.run', return_value=mock_result):
        result = is_docker_running()
        assert result == True, "Expected is_docker_running() to return True when Docker is running"
        print("✓ is_docker_running() returns True when Docker is running")
    
    # Test when Docker is not running
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stderr = "Cannot connect to the Docker daemon"
    
    with patch('subprocess.run', return_value=mock_result):
        result = is_docker_running()
        assert result == False, "Expected is_docker_running() to return False when Docker is not running"
        print("✓ is_docker_running() returns False when Docker is not running")
    
    print("✓ Backward compatibility test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DOCKER STATUS DETECTION COMPREHENSIVE TESTS")
    print("=" * 60)
    
    tests = [
        test_docker_running_success,
        test_docker_permission_denied,
        test_docker_not_running,
        test_docker_not_installed,
        test_docker_timeout,
        test_platform_specific_suggestions,
        test_is_docker_running_compatibility,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ Test error: {test.__name__}")
            print(f"  Error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
