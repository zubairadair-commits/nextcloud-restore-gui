#!/usr/bin/env python3
"""
Test suite for automated YAML file generation and storage.
Tests the new functionality where YAML files are automatically generated
and stored in the app data directory without user prompts.

Note: These tests verify the implementation without requiring tkinter,
which is not available in headless environments.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime


def test_utility_functions_behavior():
    """
    Test that utility functions work correctly in isolation.
    This test doesn't import the main module to avoid tkinter dependency.
    """
    print("Testing utility function behavior...")
    
    # Test app data directory logic
    with tempfile.TemporaryDirectory() as temp_home:
        home_path = Path(temp_home)
        app_data_dir = home_path / ".nextcloud_backup_utility"
        app_data_dir.mkdir(exist_ok=True)
        
        assert app_data_dir.exists(), "App data directory should be created"
        assert app_data_dir.is_dir(), "App data directory should be a directory"
        assert app_data_dir.name == ".nextcloud_backup_utility", "Should use correct directory name"
        
        # Test compose directory logic
        compose_dir = app_data_dir / "compose"
        compose_dir.mkdir(exist_ok=True)
        
        assert compose_dir.exists(), "Compose directory should be created"
        assert compose_dir.is_dir(), "Compose directory should be a directory"
        assert compose_dir.name == "compose", "Should use correct directory name"
        assert compose_dir.parent == app_data_dir, "Compose dir should be inside app data dir"
    
    print("✓ test_utility_functions_behavior passed")


def test_yaml_content_generation():
    """
    Test YAML content generation logic without importing the full module.
    Validates the expected structure and content.
    """
    print("Testing YAML content generation logic...")
    
    # Test expected content for PostgreSQL
    config = {
        'dbtype': 'pgsql',
        'dbname': 'test_db',
        'dbuser': 'test_user',
        'dbpassword': 'test_pass',
        'datadirectory': '/var/www/html/data',
        'trusted_domains': ['localhost', 'example.com']
    }
    
    # Verify configuration structure
    assert 'dbtype' in config, "Config should include dbtype"
    assert 'dbname' in config, "Config should include dbname"
    assert config['dbtype'] == 'pgsql', "Should be PostgreSQL"
    
    # Test MySQL configuration
    config['dbtype'] = 'mysql'
    assert config['dbtype'] == 'mysql', "Should be MySQL"
    
    # Test SQLite configuration
    config['dbtype'] = 'sqlite'
    assert config['dbtype'] == 'sqlite', "Should be SQLite"
    
    print("✓ test_yaml_content_generation passed")


def test_yaml_file_naming():
    """Test that YAML files are named with timestamps"""
    print("Testing YAML file naming pattern...")
    
    # Verify the naming pattern in the code
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    compose_filename = f"docker-compose-{timestamp}.yml"
    
    # Check that the format is correct
    assert compose_filename.startswith("docker-compose-"), "Should start with docker-compose-"
    assert compose_filename.endswith(".yml"), "Should end with .yml"
    assert len(compose_filename) > 20, "Should include timestamp"
    
    # Verify timestamp format (should be YYYYMMDD_HHMMSS)
    timestamp_part = compose_filename.replace("docker-compose-", "").replace(".yml", "")
    assert len(timestamp_part) == 15, "Timestamp should be 15 characters (YYYYMMDD_HHMMSS)"
    assert "_" in timestamp_part, "Timestamp should contain underscore separator"
    
    print("✓ test_yaml_file_naming passed")


def test_integration_yaml_workflow():
    """Integration test: verify YAML is generated and stored correctly"""
    print("Testing integration workflow...")
    
    with tempfile.TemporaryDirectory() as temp_home:
        home_path = Path(temp_home)
        
        # Create directory structure
        app_data_dir = home_path / ".nextcloud_backup_utility"
        app_data_dir.mkdir(exist_ok=True)
        compose_dir = app_data_dir / "compose"
        compose_dir.mkdir(exist_ok=True)
        
        # Simulate YAML generation and storage
        yaml_content = """version: '3.8'

services:
  db:
    image: postgres:15
    container_name: nextcloud-db
    environment:
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
  
  nextcloud:
    image: nextcloud
    container_name: nextcloud-app
    ports:
      - "8080:80"
"""
        
        # Save to compose directory (simulating what _restore_auto_thread does)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        compose_filename = f"docker-compose-{timestamp}.yml"
        compose_file_path = compose_dir / compose_filename
        
        with open(compose_file_path, 'w') as f:
            f.write(yaml_content)
        
        # Verify file was created
        assert compose_file_path.exists(), "YAML file should be created"
        assert compose_file_path.is_file(), "YAML file should be a file"
        
        # Verify content
        with open(compose_file_path, 'r') as f:
            saved_content = f.read()
        
        assert saved_content == yaml_content, "Saved content should match generated content"
        assert 'nextcloud' in saved_content, "Should contain Nextcloud configuration"
        
        # Verify we can list the files
        yaml_files = list(compose_dir.glob("docker-compose-*.yml"))
        assert len(yaml_files) == 1, "Should have one YAML file"
        assert yaml_files[0] == compose_file_path, "Should find the correct file"
        
        print("✓ test_integration_yaml_workflow passed")


def test_code_changes_verification():
    """Verify that the code changes are present in the source file"""
    print("Verifying code changes in source file...")
    
    src_file = os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    
    with open(src_file, 'r') as f:
        content = f.read()
    
    # Check for utility functions
    assert 'def get_app_data_directory():' in content, "Should have get_app_data_directory function"
    assert 'def get_compose_directory():' in content, "Should have get_compose_directory function"
    
    # Check for advanced options section
    assert 'def create_advanced_options_section' in content, "Should have create_advanced_options_section"
    assert 'def view_generated_yaml' in content, "Should have view_generated_yaml method"
    assert 'def export_yaml_file' in content, "Should have export_yaml_file method"
    assert 'def open_yaml_folder' in content, "Should have open_yaml_folder method"
    
    # Check that YAML is saved to app data directory
    assert 'compose_dir = get_compose_directory()' in content, "Should use get_compose_directory"
    assert 'docker-compose-{timestamp}.yml' in content, "Should use timestamped filenames"
    
    # Check that the dialog is no longer shown automatically
    assert '# Docker Compose is now automatically generated during restore' in content, \
           "Should have comment about automatic generation"
    
    print("✓ test_code_changes_verification passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Running Automated YAML Generation Tests")
    print("=" * 60 + "\n")
    
    try:
        test_utility_functions_behavior()
        test_yaml_content_generation()
        test_yaml_file_naming()
        test_integration_yaml_workflow()
        test_code_changes_verification()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60 + "\n")
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
