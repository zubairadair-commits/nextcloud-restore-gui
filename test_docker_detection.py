#!/usr/bin/env python3
"""
Test script for Docker detection functionality.
Tests cross-platform Docker detection and availability checks.
"""

import subprocess
import platform
import os
import sys

def is_docker_running():
    """
    Check if Docker daemon is running by attempting a simple Docker command.
    Returns: True if Docker is running, False otherwise
    """
    try:
        result = subprocess.run(
            ['docker', 'ps'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False

def get_docker_desktop_path():
    """
    Get the path to Docker Desktop executable based on the platform.
    Returns: Path to Docker Desktop or None if not found
    """
    system = platform.system()
    
    if system == "Windows":
        # Common Docker Desktop locations on Windows
        paths = [
            r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
            os.path.expandvars(r"%ProgramFiles%\Docker\Docker\Docker Desktop.exe"),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    elif system == "Darwin":  # macOS
        path = "/Applications/Docker.app"
        if os.path.exists(path):
            return path
    # Linux typically uses docker daemon, not Desktop
    return None

def test_docker_detection():
    """Test Docker detection functionality"""
    print("=" * 60)
    print("Docker Detection Tests")
    print("=" * 60)
    print()
    
    # Test 1: Platform detection
    system = platform.system()
    print(f"✓ Platform: {system}")
    print()
    
    # Test 2: Docker installed check
    try:
        result = subprocess.run(
            ['docker', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ Docker installed: {version}")
        else:
            print("✗ Docker not installed")
            return False
    except FileNotFoundError:
        print("✗ Docker not installed (command not found)")
        return False
    print()
    
    # Test 3: Docker running check
    is_running = is_docker_running()
    if is_running:
        print("✓ Docker daemon is running")
    else:
        print("✗ Docker daemon is NOT running")
        print("  Please start Docker and try again")
    print()
    
    # Test 4: Docker Desktop path detection
    docker_path = get_docker_desktop_path()
    if docker_path:
        print(f"✓ Docker Desktop found at: {docker_path}")
    else:
        if system == "Linux":
            print("ℹ Docker Desktop path detection skipped (Linux uses daemon)")
        else:
            print("✗ Docker Desktop not found at expected locations")
    print()
    
    # Test 5: Docker ps command
    if is_running:
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                containers = result.stdout.strip().split('\n') if result.stdout.strip() else []
                container_count = len([c for c in containers if c])
                print(f"✓ Docker API accessible")
                print(f"  Running containers: {container_count}")
                if container_count > 0:
                    for container in containers[:5]:  # Show first 5
                        if container:
                            print(f"    - {container}")
            else:
                print(f"✗ Docker API error: {result.stderr}")
        except Exception as e:
            print(f"✗ Docker API error: {e}")
    print()
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    if is_running:
        print("✓ All checks passed - Docker is ready")
        return True
    else:
        print("⚠ Docker daemon is not running")
        print("  Start Docker Desktop/daemon and try again")
        return False

if __name__ == '__main__':
    success = test_docker_detection()
    sys.exit(0 if success else 1)
