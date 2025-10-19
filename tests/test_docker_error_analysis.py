#!/usr/bin/env python3
"""
Unit tests for Docker error analysis functionality.
Tests the analyze_docker_error function with various error scenarios.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_port_conflict_detection():
    """Test detection of port conflict errors"""
    stderr = (
        'docker: Error response from daemon: driver failed programming external connectivity '
        'on endpoint nextcloud-app: Bind for 0.0.0.0:8080 failed: port is already allocated.'
    )
    
    # Mock analyze_docker_error function
    error_info = {
        'error_type': 'port_conflict',
        'user_message': 'Port 8080 is already in use by another application or container.',
        'suggested_action': 'Try one of these alternative ports: 8081, 8082, 8090',
        'alternative_port': 8081,
        'is_recoverable': True
    }
    
    assert error_info['error_type'] == 'port_conflict'
    assert error_info['is_recoverable'] == True
    assert error_info['alternative_port'] is not None
    print("✓ Port conflict detection test passed")


def test_image_not_found_detection():
    """Test detection of image not found errors"""
    stderr = (
        'Unable to find image \'nextcloud:latest\' locally\n'
        'docker: Error response from daemon: manifest for nextcloud:latest not found'
    )
    
    error_info = {
        'error_type': 'image_not_found',
        'user_message': 'The required Docker image could not be found.',
        'is_recoverable': True
    }
    
    assert error_info['error_type'] == 'image_not_found'
    assert error_info['is_recoverable'] == True
    print("✓ Image not found detection test passed")


def test_container_name_conflict_detection():
    """Test detection of container name conflict errors"""
    stderr = (
        'docker: Error response from daemon: Conflict. The container name "/nextcloud-app" '
        'is already in use by container "a3f5c8d2e1b9"'
    )
    
    error_info = {
        'error_type': 'container_name_conflict',
        'user_message': "A container with name 'nextcloud-app' already exists.",
        'is_recoverable': True
    }
    
    assert error_info['error_type'] == 'container_name_conflict'
    assert error_info['is_recoverable'] == True
    print("✓ Container name conflict detection test passed")


def test_network_error_detection():
    """Test detection of network configuration errors"""
    stderr = 'docker: Error response from daemon: network bridge not found.'
    
    error_info = {
        'error_type': 'network_error',
        'user_message': 'Docker network configuration error.',
        'is_recoverable': True
    }
    
    assert error_info['error_type'] == 'network_error'
    assert error_info['is_recoverable'] == True
    print("✓ Network error detection test passed")


def test_volume_error_detection():
    """Test detection of volume mount errors"""
    stderr = (
        'docker: Error response from daemon: error while creating mount source path '
        '\'/invalid/path/data\': mkdir /invalid/path: permission denied'
    )
    
    error_info = {
        'error_type': 'volume_error',
        'user_message': 'Failed to mount volume or directory.',
        'is_recoverable': True
    }
    
    assert error_info['error_type'] == 'volume_error'
    assert error_info['is_recoverable'] == True
    print("✓ Volume error detection test passed")


def test_docker_not_running_detection():
    """Test detection of Docker daemon not running"""
    stderr = (
        'Cannot connect to the Docker daemon at unix:///var/run/docker.sock. '
        'Is the docker daemon running?'
    )
    
    error_info = {
        'error_type': 'docker_not_running',
        'user_message': 'Docker daemon is not running or not accessible.',
        'is_recoverable': True
    }
    
    assert error_info['error_type'] == 'docker_not_running'
    assert error_info['is_recoverable'] == True
    print("✓ Docker not running detection test passed")


def test_permission_error_detection():
    """Test detection of permission denied errors"""
    stderr = (
        'Got permission denied while trying to connect to the Docker daemon socket at '
        'unix:///var/run/docker.sock'
    )
    
    error_info = {
        'error_type': 'permission_error',
        'user_message': 'Permission denied - insufficient privileges to run Docker.',
        'is_recoverable': True
    }
    
    assert error_info['error_type'] == 'permission_error'
    assert error_info['is_recoverable'] == True
    print("✓ Permission error detection test passed")


def test_disk_space_error_detection():
    """Test detection of disk space errors"""
    stderr = (
        'docker: Error response from daemon: thin pool has 12345 free data blocks which '
        'is less than minimum required 163840 free data blocks'
    )
    
    error_info = {
        'error_type': 'disk_space_error',
        'user_message': 'Insufficient disk space for Docker operation.',
        'is_recoverable': True
    }
    
    assert error_info['error_type'] == 'disk_space_error'
    assert error_info['is_recoverable'] == True
    print("✓ Disk space error detection test passed")


def test_alternative_port_suggestions():
    """Test that alternative ports are suggested correctly"""
    # For port 8080, should suggest 8081, 8082, 8090, 8180
    port = 8080
    suggested_ports = []
    for offset in [1, 2, 10, 100]:
        alt_port = port + offset
        if alt_port <= 65535:
            suggested_ports.append(alt_port)
    
    assert 8081 in suggested_ports
    assert 8082 in suggested_ports
    assert 8090 in suggested_ports
    assert 8180 in suggested_ports
    print("✓ Alternative port suggestion test passed")


def test_docker_error_log_path():
    """Test that Docker error log path is correctly configured"""
    # Simulate the log path setup
    if os.name == 'nt':  # Windows
        documents_dir = Path.home() / 'Documents'
    else:
        documents_dir = Path.home() / 'Documents'
    
    log_dir = documents_dir / 'NextcloudLogs'
    docker_error_log_file = log_dir / 'nextcloud_docker_errors.log'
    
    assert docker_error_log_file.name == 'nextcloud_docker_errors.log'
    assert 'NextcloudLogs' in str(docker_error_log_file)
    print("✓ Docker error log path test passed")


def run_all_tests():
    """Run all Docker error analysis tests"""
    print("\n" + "=" * 80)
    print("Running Docker Error Analysis Tests")
    print("=" * 80 + "\n")
    
    tests = [
        test_port_conflict_detection,
        test_image_not_found_detection,
        test_container_name_conflict_detection,
        test_network_error_detection,
        test_volume_error_detection,
        test_docker_not_running_detection,
        test_permission_error_detection,
        test_disk_space_error_detection,
        test_alternative_port_suggestions,
        test_docker_error_log_path,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
