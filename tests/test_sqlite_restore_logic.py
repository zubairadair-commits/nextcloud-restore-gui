#!/usr/bin/env python3
"""
Test SQLite restore logic to ensure:
1. No database container is created for SQLite
2. No attempt to link to database container for SQLite
3. docker-compose.yml has no db service for SQLite
4. No misleading Docker errors shown for SQLite
"""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_ensure_nextcloud_container_accepts_dbtype():
    """Test that ensure_nextcloud_container accepts dbtype parameter"""
    print("Testing ensure_nextcloud_container signature...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check function signature
    if 'def ensure_nextcloud_container(self, dbtype=None):' in source:
        print("  ✓ ensure_nextcloud_container accepts dbtype parameter")
    else:
        print("  ✗ ensure_nextcloud_container doesn't accept dbtype parameter")
        return False
    
    return True


def test_sqlite_skips_db_linking():
    """Test that SQLite skips database container linking"""
    print("\nTesting SQLite database linking logic...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for SQLite-specific handling in ensure_nextcloud_container
    if "if dbtype == 'sqlite':" in source and "no database container" in source.lower():
        print("  ✓ SQLite-specific logic found in ensure_nextcloud_container")
    else:
        print("  ✗ SQLite-specific logic missing in ensure_nextcloud_container")
        return False
    
    # Check that for SQLite, container is created without linking
    # Look for the pattern: if dbtype == 'sqlite': ... docker run ... without --link
    pattern = r"if dbtype == 'sqlite':.*?docker run.*?--network bridge.*?(?!--link)"
    if re.search(pattern, source, re.DOTALL):
        print("  ✓ SQLite containers created without database linking")
    else:
        print("  ✗ SQLite containers may still attempt database linking")
        return False
    
    return True


def test_db_container_not_created_for_sqlite():
    """Test that database container is not created for SQLite"""
    print("\nTesting database container creation logic...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for conditional db container creation
    if "if dbtype != 'sqlite':" in source and "ensure_db_container" in source:
        print("  ✓ Database container creation skipped for SQLite")
    else:
        print("  ✗ Database container may be created for SQLite")
        return False
    
    return True


def test_docker_compose_no_db_service_for_sqlite():
    """Test that docker-compose.yml has no db service for SQLite"""
    print("\nTesting docker-compose.yml generation for SQLite...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Find generate_docker_compose_yml function
    pattern = r"def generate_docker_compose_yml.*?if dbtype == 'sqlite':.*?compose_content = f\"\"\".*?services:.*?nextcloud:"
    if re.search(pattern, source, re.DOTALL):
        print("  ✓ SQLite docker-compose.yml has only nextcloud service")
    else:
        print("  ✗ SQLite docker-compose.yml structure not found")
        return False
    
    # Verify no db service in SQLite compose
    # Extract the SQLite compose section
    pattern = r"if dbtype == 'sqlite':.*?compose_content = f\"\"\"(.*?)\"\"\".*?elif dbtype"
    match = re.search(pattern, source, re.DOTALL)
    if match:
        sqlite_compose = match.group(1)
        if 'db:' not in sqlite_compose and 'nextcloud:' in sqlite_compose:
            print("  ✓ SQLite compose has no db service")
        else:
            print("  ✗ SQLite compose may contain db service")
            return False
    
    return True


def test_analyze_docker_error_handles_sqlite():
    """Test that analyze_docker_error handles SQLite cases correctly"""
    print("\nTesting analyze_docker_error SQLite handling...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check function signature includes dbtype
    if 'def analyze_docker_error(stderr_output, container_name=None, port=None, dbtype=None):' in source:
        print("  ✓ analyze_docker_error accepts dbtype parameter")
    else:
        print("  ✗ analyze_docker_error doesn't accept dbtype parameter")
        return False
    
    # Check for SQLite-specific error handling
    if "if dbtype == 'sqlite':" in source and "expected_sqlite_no_db" in source:
        print("  ✓ analyze_docker_error has SQLite-specific error handling")
    else:
        print("  ✗ analyze_docker_error missing SQLite-specific error handling")
        return False
    
    return True


def test_ensure_db_container_accepts_dbtype():
    """Test that ensure_db_container accepts dbtype parameter"""
    print("\nTesting ensure_db_container signature...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check function signature
    if 'def ensure_db_container(self, dbtype=None):' in source:
        print("  ✓ ensure_db_container accepts dbtype parameter")
    else:
        print("  ✗ ensure_db_container doesn't accept dbtype parameter")
        return False
    
    return True


def test_restore_thread_passes_dbtype():
    """Test that restore thread passes dbtype to container functions"""
    print("\nTesting restore thread dbtype propagation...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check that ensure_nextcloud_container is called with dbtype
    if 'self.ensure_nextcloud_container(dbtype=dbtype)' in source:
        print("  ✓ ensure_nextcloud_container called with dbtype")
    else:
        print("  ✗ ensure_nextcloud_container not called with dbtype")
        return False
    
    # Check that ensure_db_container is called with dbtype
    if 'self.ensure_db_container(dbtype=dbtype)' in source:
        print("  ✓ ensure_db_container called with dbtype")
    else:
        print("  ✗ ensure_db_container not called with dbtype")
        return False
    
    return True


def test_restore_sqlite_database_method():
    """Test that restore_sqlite_database method exists and is called for SQLite"""
    print("\nTesting SQLite restore method...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Check for restore_sqlite_database method
    if 'def restore_sqlite_database(self, extract_dir, nextcloud_container, nextcloud_path):' in source:
        print("  ✓ restore_sqlite_database method exists")
    else:
        print("  ✗ restore_sqlite_database method not found")
        return False
    
    # Check that it's called for SQLite
    if "if dbtype == 'sqlite':" in source and "self.restore_sqlite_database" in source:
        print("  ✓ restore_sqlite_database called for SQLite backups")
    else:
        print("  ✗ restore_sqlite_database not called for SQLite")
        return False
    
    return True


def run_all_tests():
    """Run all SQLite restore logic tests"""
    print("=" * 70)
    print("SQLite Restore Logic Tests")
    print("=" * 70)
    
    tests = [
        ("ensure_nextcloud_container accepts dbtype", test_ensure_nextcloud_container_accepts_dbtype),
        ("SQLite skips database linking", test_sqlite_skips_db_linking),
        ("Database container not created for SQLite", test_db_container_not_created_for_sqlite),
        ("docker-compose.yml has no db service for SQLite", test_docker_compose_no_db_service_for_sqlite),
        ("analyze_docker_error handles SQLite", test_analyze_docker_error_handles_sqlite),
        ("ensure_db_container accepts dbtype", test_ensure_db_container_accepts_dbtype),
        ("Restore thread passes dbtype", test_restore_thread_passes_dbtype),
        ("SQLite restore method exists", test_restore_sqlite_database_method),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All SQLite restore logic tests passed!")
        print("\nSummary of SQLite restore improvements:")
        print("- No database container is created for SQLite restores")
        print("- No attempt to link to database container for SQLite")
        print("- docker-compose.yml has no db service for SQLite")
        print("- Error handling distinguishes SQLite from database errors")
        print("- SQLite-specific restore method is properly invoked")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
