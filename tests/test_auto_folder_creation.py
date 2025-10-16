#!/usr/bin/env python3
"""
Test suite for automatic host folder creation during restore.
Tests the detect_required_host_folders and create_required_host_folders functions.
"""

import os
import sys
import tempfile
import shutil

# Import functions from main script
sys.path.insert(0, os.path.dirname(__file__))

# Import the module using importlib to handle the dash in filename
import importlib.util
spec = importlib.util.spec_from_file_location(
    "nextcloud_restore",
    os.path.join(os.path.dirname(__file__), "nextcloud_restore_and_backup-v9.py")
)
nextcloud_restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nextcloud_restore)

# Import the functions we need
detect_required_host_folders = nextcloud_restore.detect_required_host_folders
create_required_host_folders = nextcloud_restore.create_required_host_folders
parse_config_php_full = nextcloud_restore.parse_config_php_full

def test_detect_folders_from_config_php():
    """Test folder detection from config.php"""
    print("\n" + "="*60)
    print("TEST: Detect required folders from config.php")
    print("="*60)
    
    # Create temporary config.php with PostgreSQL
    temp_dir = tempfile.mkdtemp(prefix="test_folder_detect_")
    config_dir = os.path.join(temp_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.php")
    
    config_content = """<?php
$CONFIG = array (
  'dbtype' => 'pgsql',
  'dbname' => 'nextcloud_db',
  'dbuser' => 'nc_user',
  'dbpassword' => 'password123',
  'datadirectory' => '/var/www/html/data',
);
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    # Create some backup folders
    for folder in ['config', 'data', 'apps', 'custom_apps']:
        os.makedirs(os.path.join(temp_dir, folder), exist_ok=True)
    
    try:
        # Test detection
        folders = detect_required_host_folders(
            config_php_path=config_path,
            extract_dir=temp_dir
        )
        
        # Verify results
        assert folders['nextcloud_data'] == './nextcloud-data', \
            f"Expected './nextcloud-data', got {folders['nextcloud_data']}"
        assert folders['db_data'] == './db-data', \
            f"Expected './db-data' for PostgreSQL, got {folders['db_data']}"
        assert 'config' in folders['extracted_folders'], \
            "Expected 'config' in extracted folders"
        assert 'data' in folders['extracted_folders'], \
            "Expected 'data' in extracted folders"
        assert 'apps' in folders['extracted_folders'], \
            "Expected 'apps' in extracted folders"
        assert 'custom_apps' in folders['extracted_folders'], \
            "Expected 'custom_apps' in extracted folders"
        
        print("✅ PostgreSQL config detected correctly")
        print(f"  - Nextcloud data: {folders['nextcloud_data']}")
        print(f"  - Database data: {folders['db_data']}")
        print(f"  - Extracted folders: {folders['extracted_folders']}")
        
        return True
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_detect_folders_sqlite():
    """Test folder detection with SQLite (no db-data folder needed)"""
    print("\n" + "="*60)
    print("TEST: Detect required folders for SQLite")
    print("="*60)
    
    # Create temporary config.php with SQLite
    temp_dir = tempfile.mkdtemp(prefix="test_folder_sqlite_")
    config_dir = os.path.join(temp_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.php")
    
    config_content = """<?php
$CONFIG = array (
  'dbtype' => 'sqlite3',
  'datadirectory' => '/var/www/html/data',
);
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    # Create backup folders
    for folder in ['config', 'data']:
        os.makedirs(os.path.join(temp_dir, folder), exist_ok=True)
    
    try:
        # Test detection
        folders = detect_required_host_folders(
            config_php_path=config_path,
            extract_dir=temp_dir
        )
        
        # Verify results - SQLite should NOT need db_data folder
        assert folders['nextcloud_data'] == './nextcloud-data', \
            f"Expected './nextcloud-data', got {folders['nextcloud_data']}"
        assert folders['db_data'] is None, \
            f"Expected no db_data for SQLite, got {folders['db_data']}"
        assert 'config' in folders['extracted_folders'], \
            "Expected 'config' in extracted folders"
        assert 'data' in folders['extracted_folders'], \
            "Expected 'data' in extracted folders"
        
        print("✅ SQLite config detected correctly")
        print(f"  - Nextcloud data: {folders['nextcloud_data']}")
        print(f"  - Database data: {folders['db_data']} (None for SQLite)")
        print(f"  - Extracted folders: {folders['extracted_folders']}")
        
        return True
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_detect_folders_from_compose():
    """Test folder detection from docker-compose.yml"""
    print("\n" + "="*60)
    print("TEST: Detect required folders from docker-compose.yml")
    print("="*60)
    
    # Create temporary docker-compose.yml with custom folder names
    temp_dir = tempfile.mkdtemp(prefix="test_compose_detect_")
    compose_path = os.path.join(temp_dir, "docker-compose.yml")
    
    compose_content = """version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - ./my-db-data:/var/lib/postgresql/data
    
  nextcloud:
    image: nextcloud
    volumes:
      - ./my-nextcloud-data:/var/www/html
"""
    
    with open(compose_path, 'w') as f:
        f.write(compose_content)
    
    try:
        # Test detection
        folders = detect_required_host_folders(
            compose_file_path=compose_path
        )
        
        # Verify custom folder names from compose file
        assert folders['nextcloud_data'] == './my-nextcloud-data', \
            f"Expected './my-nextcloud-data' from compose, got {folders['nextcloud_data']}"
        assert folders['db_data'] == './my-db-data', \
            f"Expected './my-db-data' from compose, got {folders['db_data']}"
        
        print("✅ Docker Compose custom folders detected correctly")
        print(f"  - Nextcloud data: {folders['nextcloud_data']}")
        print(f"  - Database data: {folders['db_data']}")
        
        return True
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        return False
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_create_folders_success():
    """Test successful folder creation"""
    print("\n" + "="*60)
    print("TEST: Create required folders successfully")
    print("="*60)
    
    # Create temporary test directory
    temp_dir = tempfile.mkdtemp(prefix="test_create_folders_")
    
    try:
        # Change to temp directory to create folders there
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        # Create folders dict
        folders_dict = {
            'nextcloud_data': './nextcloud-data',
            'db_data': './db-data',
            'extracted_folders': []
        }
        
        # Test folder creation
        success, created, existing, errors = create_required_host_folders(folders_dict)
        
        # Verify results
        assert success, "Folder creation should succeed"
        assert len(errors) == 0, f"Expected no errors, got {errors}"
        assert './nextcloud-data' in created, "nextcloud-data should be created"
        assert './db-data' in created, "db-data should be created"
        assert len(existing) == 0, "No folders should exist initially"
        
        # Verify folders actually exist
        assert os.path.exists('./nextcloud-data'), "nextcloud-data folder should exist"
        assert os.path.exists('./db-data'), "db-data folder should exist"
        
        # Verify permissions (755)
        stat_info = os.stat('./nextcloud-data')
        mode = oct(stat_info.st_mode)[-3:]
        assert mode == '755', f"Expected permissions 755, got {mode}"
        
        print("✅ Folders created successfully")
        print(f"  - Created: {created}")
        print(f"  - Existing: {existing}")
        print(f"  - Errors: {errors}")
        
        return True
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        return False
    finally:
        # Cleanup
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_create_folders_already_exist():
    """Test folder creation when folders already exist"""
    print("\n" + "="*60)
    print("TEST: Handle existing folders gracefully")
    print("="*60)
    
    # Create temporary test directory
    temp_dir = tempfile.mkdtemp(prefix="test_existing_folders_")
    
    try:
        # Change to temp directory
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        # Pre-create one folder
        os.makedirs('./nextcloud-data', exist_ok=True)
        
        # Create folders dict
        folders_dict = {
            'nextcloud_data': './nextcloud-data',
            'db_data': './db-data',
            'extracted_folders': []
        }
        
        # Test folder creation
        success, created, existing, errors = create_required_host_folders(folders_dict)
        
        # Verify results
        assert success, "Folder creation should succeed"
        assert len(errors) == 0, f"Expected no errors, got {errors}"
        assert './nextcloud-data' in existing, "nextcloud-data should be marked as existing"
        assert './db-data' in created, "db-data should be created"
        
        print("✅ Existing folders handled correctly")
        print(f"  - Created: {created}")
        print(f"  - Existing: {existing}")
        print(f"  - Errors: {errors}")
        
        return True
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        return False
    finally:
        # Cleanup
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_create_folders_sqlite_only():
    """Test folder creation for SQLite (no db-data folder)"""
    print("\n" + "="*60)
    print("TEST: Create folders for SQLite (no db-data)")
    print("="*60)
    
    # Create temporary test directory
    temp_dir = tempfile.mkdtemp(prefix="test_sqlite_folders_")
    
    try:
        # Change to temp directory
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        # Create folders dict for SQLite (no db_data)
        folders_dict = {
            'nextcloud_data': './nextcloud-data',
            'db_data': None,  # SQLite doesn't need separate db folder
            'extracted_folders': []
        }
        
        # Test folder creation
        success, created, existing, errors = create_required_host_folders(folders_dict)
        
        # Verify results
        assert success, "Folder creation should succeed"
        assert len(errors) == 0, f"Expected no errors, got {errors}"
        assert './nextcloud-data' in created, "nextcloud-data should be created"
        assert './db-data' not in created, "db-data should NOT be created for SQLite"
        assert not os.path.exists('./db-data'), "db-data folder should not exist"
        
        print("✅ SQLite folders created correctly (no db-data)")
        print(f"  - Created: {created}")
        print(f"  - Existing: {existing}")
        
        return True
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
        return False
    finally:
        # Cleanup
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("AUTOMATIC FOLDER CREATION - TEST SUITE")
    print("="*60)
    
    tests = [
        ("test_detect_folders_from_config_php", test_detect_folders_from_config_php),
        ("test_detect_folders_sqlite", test_detect_folders_sqlite),
        ("test_detect_folders_from_compose", test_detect_folders_from_compose),
        ("test_create_folders_success", test_create_folders_success),
        ("test_create_folders_already_exist", test_create_folders_already_exist),
        ("test_create_folders_sqlite_only", test_create_folders_sqlite_only),
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
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
