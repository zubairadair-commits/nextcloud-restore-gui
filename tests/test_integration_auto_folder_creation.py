#!/usr/bin/env python3
"""
Integration test for automatic folder creation during restore workflow.

This test simulates the restore workflow to verify that folders are 
automatically created at the right time in the process.
"""

import os
import sys
import tempfile
import shutil
import tarfile

# Import functions from main script
import importlib.util
spec = importlib.util.spec_from_file_location(
    "nextcloud_restore",
    os.path.join(os.path.dirname(__file__), "nextcloud_restore_and_backup-v9.py")
)
nextcloud_restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nextcloud_restore)

detect_required_host_folders = nextcloud_restore.detect_required_host_folders
create_required_host_folders = nextcloud_restore.create_required_host_folders
parse_config_php_full = nextcloud_restore.parse_config_php_full

def create_mock_backup(temp_dir):
    """Create a mock backup archive for testing"""
    backup_dir = os.path.join(temp_dir, "nextcloud_backup")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create config directory with config.php
    config_dir = os.path.join(backup_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    
    config_content = """<?php
$CONFIG = array (
  'dbtype' => 'pgsql',
  'dbname' => 'nextcloud_db',
  'dbuser' => 'nextcloud',
  'dbpassword' => 'secure_pass',
  'dbhost' => 'db',
  'dbport' => '5432',
  'datadirectory' => '/var/www/html/data',
  'trusted_domains' => 
  array (
    0 => 'localhost',
    1 => 'nextcloud.example.com',
  ),
);
"""
    
    with open(os.path.join(config_dir, "config.php"), 'w') as f:
        f.write(config_content)
    
    # Create other directories
    for folder in ['data', 'apps', 'custom_apps']:
        folder_path = os.path.join(backup_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        # Create a dummy file in each folder
        with open(os.path.join(folder_path, "test.txt"), 'w') as f:
            f.write(f"Test file in {folder}")
    
    # Create database dump
    with open(os.path.join(backup_dir, "nextcloud_db.sql"), 'w') as f:
        f.write("-- Mock database dump\nCREATE TABLE test (id INT);\n")
    
    # Create tar archive
    archive_path = os.path.join(temp_dir, "nextcloud_backup.tar.gz")
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(backup_dir, arcname="nextcloud_backup")
    
    return archive_path, backup_dir

def test_integration_restore_workflow():
    """
    Integration test: Simulate restore workflow with auto-folder creation.
    
    Workflow:
    1. Extract backup
    2. Detect database type from config.php
    3. Auto-detect required folders
    4. Auto-create host folders (THIS IS WHAT WE'RE TESTING)
    5. Verify folders were created correctly
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: Restore Workflow with Auto-Folder Creation")
    print("="*60)
    
    # Create temporary workspace
    temp_dir = tempfile.mkdtemp(prefix="test_integration_restore_")
    work_dir = os.path.join(temp_dir, "work")
    os.makedirs(work_dir, exist_ok=True)
    
    try:
        print("\n1. Creating mock backup archive...")
        archive_path, backup_dir = create_mock_backup(temp_dir)
        print(f"   ✓ Created backup at: {archive_path}")
        
        print("\n2. Extracting backup (simulating restore step 1)...")
        extract_dir = os.path.join(work_dir, "extracted")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(extract_dir)
        actual_extract = os.path.join(extract_dir, "nextcloud_backup")
        print(f"   ✓ Extracted to: {actual_extract}")
        
        print("\n3. Detecting database type from config.php...")
        config_path = os.path.join(actual_extract, "config", "config.php")
        assert os.path.exists(config_path), "config.php should exist"
        
        config = parse_config_php_full(config_path)
        assert config is not None, "Config parsing should succeed"
        dbtype = config.get('dbtype', '').lower()
        print(f"   ✓ Detected database type: {dbtype}")
        assert dbtype == 'pgsql', f"Expected 'pgsql', got '{dbtype}'"
        
        print("\n4. Auto-detecting required folders...")
        # Change to work directory (simulate being in the target directory)
        old_cwd = os.getcwd()
        os.chdir(work_dir)
        
        folders_dict = detect_required_host_folders(
            config_php_path=config_path,
            compose_file_path=None,
            extract_dir=actual_extract
        )
        
        print(f"   ✓ Detected folders:")
        print(f"     - Nextcloud data: {folders_dict['nextcloud_data']}")
        print(f"     - Database data: {folders_dict['db_data']}")
        print(f"     - Extracted folders: {folders_dict['extracted_folders']}")
        
        # Verify detection results
        assert folders_dict['nextcloud_data'] == './nextcloud-data'
        assert folders_dict['db_data'] == './db-data'  # PostgreSQL needs this
        assert 'config' in folders_dict['extracted_folders']
        assert 'data' in folders_dict['extracted_folders']
        assert 'apps' in folders_dict['extracted_folders']
        assert 'custom_apps' in folders_dict['extracted_folders']
        
        print("\n5. Auto-creating host folders (MAIN TEST)...")
        success, created, existing, errors = create_required_host_folders(folders_dict)
        
        print(f"   ✓ Folder creation result:")
        print(f"     - Success: {success}")
        print(f"     - Created: {created}")
        print(f"     - Existing: {existing}")
        print(f"     - Errors: {errors}")
        
        # Verify creation was successful
        assert success, "Folder creation should succeed"
        assert len(errors) == 0, f"Should have no errors, got: {errors}"
        assert './nextcloud-data' in created, "nextcloud-data should be created"
        assert './db-data' in created, "db-data should be created"
        
        print("\n6. Verifying folders exist on disk...")
        assert os.path.exists('./nextcloud-data'), "nextcloud-data should exist"
        assert os.path.exists('./db-data'), "db-data should exist"
        assert os.path.isdir('./nextcloud-data'), "nextcloud-data should be a directory"
        assert os.path.isdir('./db-data'), "db-data should be a directory"
        print(f"   ✓ All folders exist and are directories")
        
        print("\n7. Verifying folder permissions...")
        for folder in ['./nextcloud-data', './db-data']:
            stat_info = os.stat(folder)
            mode = oct(stat_info.st_mode)[-3:]
            print(f"   ✓ {folder}: {mode}")
            assert mode == '755', f"Expected 755, got {mode}"
        
        print("\n" + "="*60)
        print("✅ INTEGRATION TEST PASSED")
        print("="*60)
        print("\nSummary:")
        print("  ✓ Backup extracted successfully")
        print("  ✓ Database type detected from config.php")
        print("  ✓ Required folders auto-detected")
        print("  ✓ Host folders auto-created before container start")
        print("  ✓ Folders have correct permissions (755)")
        print("\nThe restore workflow with auto-folder creation works correctly!")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_integration_sqlite_workflow():
    """
    Integration test for SQLite restore (no db-data folder needed).
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: SQLite Restore (No DB Folder)")
    print("="*60)
    
    # Create temporary workspace
    temp_dir = tempfile.mkdtemp(prefix="test_integration_sqlite_")
    work_dir = os.path.join(temp_dir, "work")
    os.makedirs(work_dir, exist_ok=True)
    
    try:
        print("\n1. Creating mock SQLite backup...")
        backup_dir = os.path.join(temp_dir, "nextcloud_backup")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create config with SQLite
        config_dir = os.path.join(backup_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        config_content = """<?php
$CONFIG = array (
  'dbtype' => 'sqlite3',
  'datadirectory' => '/var/www/html/data',
);
"""
        
        with open(os.path.join(config_dir, "config.php"), 'w') as f:
            f.write(config_content)
        
        # Create data directory with SQLite database
        data_dir = os.path.join(backup_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, "owncloud.db"), 'w') as f:
            f.write("mock sqlite database")
        
        # Create archive
        archive_path = os.path.join(temp_dir, "nextcloud_backup.tar.gz")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(backup_dir, arcname="nextcloud_backup")
        
        print("   ✓ Created SQLite backup")
        
        print("\n2. Extracting backup...")
        extract_dir = os.path.join(work_dir, "extracted")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(extract_dir)
        actual_extract = os.path.join(extract_dir, "nextcloud_backup")
        
        print("\n3. Detecting database type (should be SQLite)...")
        config_path = os.path.join(actual_extract, "config", "config.php")
        config = parse_config_php_full(config_path)
        dbtype = config.get('dbtype', '').lower()
        print(f"   ✓ Detected: {dbtype}")
        assert dbtype in ['sqlite', 'sqlite3'], f"Expected SQLite, got '{dbtype}'"
        
        print("\n4. Auto-detecting folders (SQLite should not need db-data)...")
        old_cwd = os.getcwd()
        os.chdir(work_dir)
        
        folders_dict = detect_required_host_folders(
            config_php_path=config_path,
            extract_dir=actual_extract
        )
        
        print(f"   ✓ Nextcloud data: {folders_dict['nextcloud_data']}")
        print(f"   ✓ Database data: {folders_dict['db_data']}")
        
        assert folders_dict['nextcloud_data'] == './nextcloud-data'
        assert folders_dict['db_data'] is None, "SQLite should NOT need db-data folder"
        
        print("\n5. Creating folders...")
        success, created, existing, errors = create_required_host_folders(folders_dict)
        
        assert success, "Folder creation should succeed"
        assert './nextcloud-data' in created
        assert './db-data' not in created, "db-data should NOT be created for SQLite"
        assert not os.path.exists('./db-data'), "db-data folder should not exist"
        
        print(f"   ✓ Created: {created}")
        print(f"   ✓ db-data correctly NOT created for SQLite")
        
        print("\n" + "="*60)
        print("✅ SQLITE INTEGRATION TEST PASSED")
        print("="*60)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

def run_all_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("AUTO-FOLDER CREATION - INTEGRATION TEST SUITE")
    print("="*60)
    
    tests = [
        ("test_integration_restore_workflow", test_integration_restore_workflow),
        ("test_integration_sqlite_workflow", test_integration_sqlite_workflow),
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
    print("INTEGRATION TEST SUMMARY")
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
        print("\n✅ ALL INTEGRATION TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_integration_tests())
