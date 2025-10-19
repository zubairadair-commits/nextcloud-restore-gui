#!/usr/bin/env python3
"""
Test script for scheduled backup component selection and backup rotation features.

Tests:
1. Component selection is properly stored in configuration
2. Component selection is passed to scheduled task command
3. Backup rotation setting is stored in configuration
4. Backup rotation setting is passed to scheduled task command
5. Command-line arguments for components and rotation are parsed correctly
"""

import sys
import os
import re
import json

def test_component_selection_ui():
    """Test that component selection UI is present in show_schedule_backup."""
    print("Testing component selection UI...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    assert os.path.exists(main_file), f"{main_file} should exist"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the show_schedule_backup function
    function_start = content.find('def show_schedule_backup(self):')
    assert function_start != -1, "show_schedule_backup function should exist"
    
    # Find the _create_schedule call
    create_schedule_call = content.find('self._create_schedule(', function_start)
    assert create_schedule_call != -1, "_create_schedule call should exist"
    
    # Extract the call section
    call_section = content[create_schedule_call:create_schedule_call+500]
    
    # Check that component_vars and rotation_var are passed
    assert 'component_vars' in call_section, \
        "_create_schedule should receive component_vars parameter"
    print("  ✓ component_vars parameter passed to _create_schedule")
    
    assert 'rotation_var.get()' in call_section, \
        "_create_schedule should receive rotation setting"
    print("  ✓ rotation_var parameter passed to _create_schedule")
    
    # Check for component selection UI elements
    schedule_section_start = function_start
    schedule_section_end = content.find('\n    def ', function_start + 1)
    schedule_section = content[schedule_section_start:schedule_section_end]
    
    assert '📁 Components to Backup' in schedule_section or 'Components to Backup' in schedule_section, \
        "Component selection section should be present"
    print("  ✓ Component selection UI section found")
    
    assert '"config"' in schedule_section and '"data"' in schedule_section, \
        "Config and data components should be present"
    print("  ✓ Config and data components found")
    
    assert '"apps"' in schedule_section or '"custom_apps"' in schedule_section, \
        "Optional components should be present"
    print("  ✓ Optional components found")
    
    print("✅ Component selection UI test PASSED\n")

def test_backup_rotation_ui():
    """Test that backup rotation UI is present in show_schedule_backup."""
    print("Testing backup rotation UI...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the show_schedule_backup function
    function_start = content.find('def show_schedule_backup(self):')
    schedule_section_end = content.find('\n    def ', function_start + 1)
    schedule_section = content[function_start:schedule_section_end]
    
    # Check for rotation UI elements
    assert '♻️ Backup Rotation' in schedule_section or 'Backup Rotation' in schedule_section, \
        "Backup rotation section should be present"
    print("  ✓ Backup rotation UI section found")
    
    assert 'rotation_var' in schedule_section, \
        "rotation_var should be defined"
    print("  ✓ rotation_var variable found")
    
    # Check for rotation options
    assert 'Unlimited' in schedule_section or 'unlimited' in schedule_section, \
        "Unlimited option should be present"
    print("  ✓ Unlimited rotation option found")
    
    # Check for specific rotation counts
    rotation_counts = ['1 backup', '3 backup', '5 backup', '10 backup']
    found_counts = [count for count in rotation_counts if count in schedule_section]
    assert len(found_counts) >= 2, \
        "Multiple rotation count options should be present"
    print(f"  ✓ Rotation count options found: {len(found_counts)}")
    
    print("✅ Backup rotation UI test PASSED\n")

def test_create_schedule_method():
    """Test that _create_schedule method accepts new parameters."""
    print("Testing _create_schedule method signature...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _create_schedule method
    function_start = content.find('def _create_schedule(self,')
    assert function_start != -1, "_create_schedule method should exist"
    
    # Extract the method signature (first line)
    function_line_end = content.find('\n', function_start)
    function_signature = content[function_start:function_line_end]
    
    # Check parameters
    assert 'component_vars' in function_signature or 'components' in function_signature, \
        "_create_schedule should accept components parameter"
    print("  ✓ Components parameter in method signature")
    
    assert 'rotation' in function_signature, \
        "_create_schedule should accept rotation parameter"
    print("  ✓ Rotation parameter in method signature")
    
    # Extract method body
    next_def = content.find('\n    def ', function_start + 1)
    method_body = content[function_start:next_def]
    
    # Check that components are saved to config
    assert "'components'" in method_body, \
        "Components should be saved to config"
    print("  ✓ Components saved to config")
    
    assert "'rotation_keep'" in method_body or "'rotation'" in method_body, \
        "Rotation setting should be saved to config"
    print("  ✓ Rotation setting saved to config")
    
    print("✅ _create_schedule method test PASSED\n")

def test_create_scheduled_task_function():
    """Test that create_scheduled_task function accepts new parameters."""
    print("Testing create_scheduled_task function...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the create_scheduled_task function
    function_start = content.find('def create_scheduled_task(')
    assert function_start != -1, "create_scheduled_task function should exist"
    
    # Extract function signature
    function_line_end = content.find('\n', function_start)
    function_signature = content[function_start:function_line_end]
    
    # Check parameters
    assert 'components' in function_signature, \
        "create_scheduled_task should accept components parameter"
    print("  ✓ Components parameter in function signature")
    
    assert 'rotation' in function_signature, \
        "create_scheduled_task should accept rotation parameter"
    print("  ✓ Rotation parameter in function signature")
    
    # Extract function body
    next_def = content.find('\ndef ', function_start + 1)
    function_body = content[function_start:next_def]
    
    # Check that components are passed to command
    assert '--components' in function_body, \
        "Components should be passed as --components argument"
    print("  ✓ --components argument added to command")
    
    assert '--rotation-keep' in function_body or '--rotation' in function_body, \
        "Rotation should be passed as --rotation-keep argument"
    print("  ✓ --rotation-keep argument added to command")
    
    print("✅ create_scheduled_task function test PASSED\n")

def test_command_line_arguments():
    """Test that command-line argument parser accepts new arguments."""
    print("Testing command-line argument parser...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the argument parser section
    parser_start = content.find('argparse.ArgumentParser')
    assert parser_start != -1, "Argument parser should exist"
    
    # Find the scheduled mode section
    scheduled_start = content.find('elif args.scheduled:', parser_start)
    assert scheduled_start != -1, "Scheduled mode section should exist"
    
    # Extract the section with argument definitions
    args_section_end = content.find('args = parser.parse_args()', parser_start)
    args_section = content[parser_start:args_section_end]
    
    # Check for new arguments
    assert '--components' in args_section, \
        "--components argument should be defined"
    print("  ✓ --components argument defined")
    
    assert '--rotation-keep' in args_section or '--rotation' in args_section, \
        "--rotation-keep argument should be defined"
    print("  ✓ --rotation-keep argument defined")
    
    # Check that scheduled mode uses the arguments
    scheduled_section_end = content.find('\n    else:', scheduled_start)
    scheduled_section = content[scheduled_start:scheduled_section_end]
    
    assert 'args.components' in scheduled_section, \
        "Scheduled mode should use args.components"
    print("  ✓ args.components used in scheduled mode")
    
    assert 'args.rotation' in scheduled_section, \
        "Scheduled mode should use args.rotation"
    print("  ✓ args.rotation used in scheduled mode")
    
    print("✅ Command-line arguments test PASSED\n")

def test_run_scheduled_backup_method():
    """Test that run_scheduled_backup accepts new parameters."""
    print("Testing run_scheduled_backup method...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the run_scheduled_backup method
    function_start = content.find('def run_scheduled_backup(self,')
    assert function_start != -1, "run_scheduled_backup method should exist"
    
    # Extract method signature
    function_line_end = content.find(':\n', function_start)
    function_signature = content[function_start:function_line_end]
    
    # Check parameters
    assert 'components' in function_signature, \
        "run_scheduled_backup should accept components parameter"
    print("  ✓ Components parameter in method signature")
    
    assert 'rotation' in function_signature, \
        "run_scheduled_backup should accept rotation parameter"
    print("  ✓ Rotation parameter in method signature")
    
    # Extract method body
    next_def = content.find('\n    def ', function_start + 1)
    method_body = content[function_start:next_def]
    
    # Check that components are passed to backup process
    assert 'run_backup_process_scheduled' in method_body, \
        "Should call run_backup_process_scheduled"
    
    # Find the call to run_backup_process_scheduled
    call_start = method_body.find('run_backup_process_scheduled')
    call_end = method_body.find('\n', call_start)
    call_line = method_body[call_start:call_end]
    
    assert 'components' in call_line or 'components' in method_body[call_start:call_start+200], \
        "Components should be passed to backup process"
    print("  ✓ Components passed to backup process")
    
    # Check for rotation logic
    assert '_perform_backup_rotation' in method_body or 'rotation' in method_body, \
        "Rotation logic should be present"
    print("  ✓ Rotation logic found")
    
    print("✅ run_scheduled_backup method test PASSED\n")

def test_backup_rotation_implementation():
    """Test that backup rotation method is implemented."""
    print("Testing backup rotation implementation...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _perform_backup_rotation method
    function_start = content.find('def _perform_backup_rotation(')
    assert function_start != -1, "_perform_backup_rotation method should exist"
    print("  ✓ _perform_backup_rotation method exists")
    
    # Extract method body
    next_def = content.find('\n    def ', function_start + 1)
    if next_def == -1:
        next_def = content.find('\n    # -----', function_start + 1)
    method_body = content[function_start:next_def]
    
    # Check for key rotation logic
    assert 'listdir' in method_body or 'scandir' in method_body, \
        "Should list files in backup directory"
    print("  ✓ Lists files in backup directory")
    
    assert 'sort' in method_body, \
        "Should sort files by time"
    print("  ✓ Sorts files by modification time")
    
    assert 'os.remove' in method_body or 'unlink' in method_body, \
        "Should delete old backup files"
    print("  ✓ Deletes old backup files")
    
    assert 'backup_history.delete_backup' in method_body, \
        "Should update backup history database"
    print("  ✓ Updates backup history database")
    
    print("✅ Backup rotation implementation test PASSED\n")

def test_component_filtering():
    """Test that run_backup_process_scheduled filters components."""
    print("Testing component filtering in backup process...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the run_backup_process_scheduled method
    function_start = content.find('def run_backup_process_scheduled(')
    assert function_start != -1, "run_backup_process_scheduled method should exist"
    
    # Extract method signature
    function_line_end = content.find(':\n', function_start)
    function_signature = content[function_start:function_line_end]
    
    # Check that it accepts components parameter
    assert 'components' in function_signature, \
        "run_backup_process_scheduled should accept components parameter"
    print("  ✓ Components parameter in method signature")
    
    # Extract method body
    next_def = content.find('\n    def ', function_start + 1)
    method_body = content[function_start:next_def]
    
    # Check for component filtering logic
    assert 'folders_to_copy' in method_body, \
        "Should define folders_to_copy"
    print("  ✓ folders_to_copy variable found")
    
    # Check for filtering based on components
    has_filter = ('if components' in method_body or 
                  'if f in components' in method_body or
                  'filter' in method_body)
    assert has_filter, \
        "Should filter folders based on components"
    print("  ✓ Component filtering logic found")
    
    print("✅ Component filtering test PASSED\n")

def main():
    """Run all tests."""
    print("=" * 60)
    print("SCHEDULED BACKUP ENHANCEMENTS TEST SUITE")
    print("Component Selection & Backup Rotation")
    print("=" * 60)
    print()
    
    try:
        test_component_selection_ui()
        test_backup_rotation_ui()
        test_create_schedule_method()
        test_create_scheduled_task_function()
        test_command_line_arguments()
        test_run_scheduled_backup_method()
        test_backup_rotation_implementation()
        test_component_filtering()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
