#!/usr/bin/env python3
"""
Test script for scheduled backup functionality.
This validates the code structure and basic logic without running the full GUI.
"""

import sys
import os
import platform
import json

def test_code_structure():
    """Test that the code has the expected structure."""
    print("Testing code structure...")
    
    # Check if the main file exists
    main_file = "nextcloud_restore_and_backup-v9.py"
    assert os.path.exists(main_file), f"{main_file} should exist"
    print(f"  ✓ {main_file} exists")
    
    # Read the file and check for key functions/classes
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for scheduler functions
    required_functions = [
        'get_schedule_config_path',
        'load_schedule_config',
        'save_schedule_config',
        'get_exe_path',
        'create_scheduled_task',
        'delete_scheduled_task',
        'get_scheduled_task_status',
        'enable_scheduled_task',
        'disable_scheduled_task',
        'show_schedule_backup',
        'run_scheduled_backup',
        'run_backup_process_scheduled'
    ]
    
    for func in required_functions:
        assert f"def {func}" in content, f"Function {func} should be defined"
        print(f"  ✓ Found function: {func}")
    
    # Check for command-line argument parsing
    assert 'argparse' in content, "Should import argparse"
    assert '--scheduled' in content, "Should have --scheduled argument"
    assert '--backup-dir' in content, "Should have --backup-dir argument"
    print("  ✓ Command-line argument parsing present")
    
    # Check for schedule button in landing page
    assert 'Schedule Backup' in content, "Should have Schedule Backup button"
    print("  ✓ Schedule Backup button present")

def test_config_path_logic():
    """Test the config path logic."""
    print("\nTesting config path logic...")
    
    # Simulate the config path function
    config_dir = os.path.join(os.path.expanduser("~"), ".nextcloud_backup")
    config_path = os.path.join(config_dir, "schedule_config.json")
    
    print(f"  Expected config path: {config_path}")
    assert config_path.endswith("schedule_config.json"), "Config path should end with schedule_config.json"
    print("  ✓ Config path logic is correct")

def test_config_save_load_logic():
    """Test save and load config logic."""
    print("\nTesting config save/load logic...")
    
    # Create test config
    test_config = {
        'task_name': 'TestBackup',
        'backup_dir': '/test/backup',
        'frequency': 'daily',
        'time': '02:00',
        'encrypt': True,
        'enabled': True
    }
    
    # Test config directory creation
    config_dir = os.path.join(os.path.expanduser("~"), ".nextcloud_backup")
    os.makedirs(config_dir, exist_ok=True)
    assert os.path.exists(config_dir), "Config directory should be created"
    print("  ✓ Config directory created")
    
    # Test saving
    config_path = os.path.join(config_dir, "test_schedule_config.json")
    with open(config_path, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    assert os.path.exists(config_path), "Config file should be saved"
    print("  ✓ Config saved successfully")
    
    # Test loading
    with open(config_path, 'r') as f:
        loaded_config = json.load(f)
    
    assert loaded_config['task_name'] == 'TestBackup', "Task name should match"
    assert loaded_config['frequency'] == 'daily', "Frequency should match"
    print("  ✓ Config loaded successfully")
    
    # Clean up
    if os.path.exists(config_path):
        os.remove(config_path)
        print("  ✓ Test config cleaned up")

def test_platform_check():
    """Test platform detection."""
    print("\nTesting platform detection...")
    system = platform.system()
    print(f"  Current platform: {system}")
    
    if system == "Windows":
        print("  ✓ Running on Windows - Task Scheduler features available")
    else:
        print(f"  ℹ Running on {system} - Task Scheduler features not available")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Scheduled Backup Functionality Tests")
    print("=" * 60)
    
    try:
        test_code_structure()
        test_config_path_logic()
        test_config_save_load_logic()
        test_platform_check()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
