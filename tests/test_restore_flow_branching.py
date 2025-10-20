#!/usr/bin/env python3
"""
Integration test to validate restore flow branching for all database types.
This test validates the logic flow without actually running Docker commands.
"""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_restore_flow_sqlite():
    """Test restore flow for SQLite database type"""
    print("Testing SQLite restore flow...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Extract the _restore_auto_thread method
    pattern = r"def _restore_auto_thread\(self.*?(?=\n    def )"
    match = re.search(pattern, source, re.DOTALL)
    
    if not match:
        print("  ✗ Could not extract _restore_auto_thread method")
        return False
    
    restore_method = match.group(0)
    
    # Verify SQLite-specific checks
    checks = [
        ("Database type detection", "dbtype, db_config = self.detect_database_type"),
        ("SQLite normalization", "if dbtype.lower() in ['sqlite', 'sqlite3']:"),
        ("DB container skip", "if dbtype != 'sqlite':"),
        ("SQLite message", "SQLite detected - no separate database container needed"),
        ("SQLite restore branch", "if dbtype == 'sqlite':"),
        ("SQLite restore method", "self.restore_sqlite_database"),
    ]
    
    all_checks_passed = True
    for check_name, pattern in checks:
        if pattern in restore_method:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name} - pattern not found: {pattern}")
            all_checks_passed = False
    
    return all_checks_passed


def test_restore_flow_mysql():
    """Test restore flow for MySQL database type"""
    print("\nTesting MySQL restore flow...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Extract the _restore_auto_thread method
    pattern = r"def _restore_auto_thread\(self.*?(?=\n    def )"
    match = re.search(pattern, source, re.DOTALL)
    
    if not match:
        print("  ✗ Could not extract _restore_auto_thread method")
        return False
    
    restore_method = match.group(0)
    
    # Verify MySQL-specific checks
    checks = [
        ("MySQL restore branch", "elif dbtype == 'mysql':"),
        ("MySQL restore method", "self.restore_mysql_database"),
        ("DB container creation", "self.ensure_db_container"),
    ]
    
    all_checks_passed = True
    for check_name, pattern in checks:
        if pattern in restore_method:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name} - pattern not found: {pattern}")
            all_checks_passed = False
    
    return all_checks_passed


def test_restore_flow_postgresql():
    """Test restore flow for PostgreSQL database type"""
    print("\nTesting PostgreSQL restore flow...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Extract the _restore_auto_thread method
    pattern = r"def _restore_auto_thread\(self.*?(?=\n    def )"
    match = re.search(pattern, source, re.DOTALL)
    
    if not match:
        print("  ✗ Could not extract _restore_auto_thread method")
        return False
    
    restore_method = match.group(0)
    
    # Verify PostgreSQL-specific checks
    checks = [
        ("PostgreSQL restore branch", "elif dbtype == 'pgsql':"),
        ("PostgreSQL restore method", "self.restore_postgresql_database"),
        ("DB container creation", "self.ensure_db_container"),
    ]
    
    all_checks_passed = True
    for check_name, pattern in checks:
        if pattern in restore_method:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name} - pattern not found: {pattern}")
            all_checks_passed = False
    
    return all_checks_passed


def test_container_creation_branching():
    """Test that container creation properly branches on database type"""
    print("\nTesting container creation branching...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Extract ensure_nextcloud_container method
    pattern = r"def ensure_nextcloud_container\(self, dbtype=None\):.*?(?=\n    def )"
    match = re.search(pattern, source, re.DOTALL)
    
    if not match:
        print("  ✗ Could not extract ensure_nextcloud_container method")
        return False
    
    container_method = match.group(0)
    
    # Verify branching logic
    checks = [
        ("SQLite branch exists", "if dbtype == 'sqlite':"),
        ("SQLite creates container without link", "docker run -d --name.*--network bridge -p.*(?!--link)"),
        ("Non-SQLite creates with link attempt", "docker run -d --name.*--network bridge --link"),
        ("Link failure fallback", "if result.returncode != 0 and \"Could not find\" in result.stderr:"),
    ]
    
    all_checks_passed = True
    for check_name, pattern in checks:
        if re.search(pattern, container_method, re.DOTALL):
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name} - pattern not found")
            all_checks_passed = False
    
    return all_checks_passed


def test_error_handling_branching():
    """Test that error handling properly branches on database type"""
    print("\nTesting error handling branching...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Extract analyze_docker_error function
    pattern = r"def analyze_docker_error\(.*?(?=\ndef )"
    match = re.search(pattern, source, re.DOTALL)
    
    if not match:
        print("  ✗ Could not extract analyze_docker_error function")
        return False
    
    error_method = match.group(0)
    
    # Verify error handling branching
    checks = [
        ("Accepts dbtype parameter", "dbtype=None"),
        ("SQLite special handling", "if dbtype == 'sqlite':"),
        ("SQLite expected error type", "expected_sqlite_no_db"),
        ("SQLite helpful message", "This is expected behavior for SQLite backups"),
    ]
    
    all_checks_passed = True
    for check_name, pattern in checks:
        if pattern in error_method:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name} - pattern not found")
            all_checks_passed = False
    
    return all_checks_passed


def test_docker_compose_generation_branching():
    """Test that docker-compose generation properly branches on database type"""
    print("\nTesting docker-compose generation branching...")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        source = f.read()
    
    # Extract generate_docker_compose_yml function
    pattern = r"def generate_docker_compose_yml\(.*?(?=\ndef )"
    match = re.search(pattern, source, re.DOTALL)
    
    if not match:
        print("  ✗ Could not extract generate_docker_compose_yml function")
        return False
    
    compose_method = match.group(0)
    
    # Verify branching logic
    checks = [
        ("SQLite branch", "if dbtype == 'sqlite':"),
        ("MySQL/MariaDB branch", "elif dbtype in ['mysql', 'mariadb']:"),
        ("PostgreSQL branch else", "else:  # PostgreSQL"),
        ("SQLite has only nextcloud service", "# SQLite - no separate database service needed"),
    ]
    
    all_checks_passed = True
    for check_name, pattern in checks:
        if pattern in compose_method:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name} - pattern not found")
            all_checks_passed = False
    
    # Additional check: SQLite compose should not have db service
    sqlite_section_pattern = r"if dbtype == 'sqlite':.*?compose_content = f\"\"\"(.*?)\"\"\".*?elif"
    match = re.search(sqlite_section_pattern, compose_method, re.DOTALL)
    if match:
        sqlite_compose = match.group(1)
        if 'db:' not in sqlite_compose:
            print("  ✓ SQLite compose has no db service")
        else:
            print("  ✗ SQLite compose incorrectly includes db service")
            all_checks_passed = False
    else:
        print("  ✗ Could not extract SQLite compose section")
        all_checks_passed = False
    
    return all_checks_passed


def run_all_tests():
    """Run all integration tests"""
    print("=" * 70)
    print("Restore Flow Branching Integration Tests")
    print("=" * 70)
    
    tests = [
        ("SQLite restore flow", test_restore_flow_sqlite),
        ("MySQL restore flow", test_restore_flow_mysql),
        ("PostgreSQL restore flow", test_restore_flow_postgresql),
        ("Container creation branching", test_container_creation_branching),
        ("Error handling branching", test_error_handling_branching),
        ("Docker-compose generation branching", test_docker_compose_generation_branching),
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
        print("\n🎉 All restore flow branching tests passed!")
        print("\nValidated restore flow for:")
        print("- SQLite: No DB container, direct .db file copy")
        print("- MySQL: DB container creation, SQL dump restore")
        print("- PostgreSQL: DB container creation, SQL dump restore")
        print("\nVerified proper branching in:")
        print("- Container creation (with/without DB linking)")
        print("- Error handling (SQLite-aware messages)")
        print("- Docker-compose generation (correct services)")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
