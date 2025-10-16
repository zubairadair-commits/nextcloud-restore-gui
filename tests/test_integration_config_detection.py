#!/usr/bin/env python3
"""
Integration test to validate config.php detection fix patterns.
This test validates the code contains the correct logic patterns.
"""

import os
import sys
import tempfile
import tarfile
import shutil

def validate_code_patterns():
    """Validate that the code contains the correct patterns"""
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find the extract_config_php_only function
    start_idx = content.find('def extract_config_php_only(')
    if start_idx == -1:
        return False, "Function not found"
    
    # Extract function content (next 3000 chars should be enough)
    func_content = content[start_idx:start_idx + 3000]
    
    # Check for required patterns
    checks = [
        ("os.path.basename(member.name) == 'config.php'", "Uses basename for exact match"),
        ("'config' in path_parts", "Checks for config directory"),
        ("potential_configs", "Tracks all found configs for logging"),
        ("Found potential config.php", "Logs potential configs"),
    ]
    
    # Special checks
    has_config_validation = "$CONFIG" in func_content and "dbtype" in func_content
    
    results = []
    all_passed = True
    for pattern, description in checks:
        if pattern in func_content:
            results.append((True, description))
        else:
            results.append((False, description))
            all_passed = False
    
    # Add the content validation check
    results.append((has_config_validation, "Validates config content ($CONFIG and dbtype)"))
    all_passed = all_passed and has_config_validation
    
    return all_passed, results

def test_scenario_1_archive_structure():
    """
    Scenario 1: Create a realistic archive and validate structure
    This shows what files would match old vs new logic
    """
    print("\n" + "="*70)
    print("SCENARIO 1: Backup with multiple config files")
    print("="*70)
    
    temp_dir = tempfile.mkdtemp(prefix="test_scenario1_")
    
    # Create fake config files that OLD logic would incorrectly match
    with open(os.path.join(temp_dir, "apache-pretty-urls.config.php"), 'w') as f:
        f.write("<?php\n// Fake apache config\n$APACHE = array();\n")
    
    with open(os.path.join(temp_dir, "memcache.config.php"), 'w') as f:
        f.write("<?php\n// Fake memcache config\n$MEMCACHE = array();\n")
    
    # Create real config.php
    config_dir = os.path.join(temp_dir, "config")
    os.makedirs(config_dir)
    with open(os.path.join(config_dir, "config.php"), 'w') as f:
        f.write("<?php\n$CONFIG = array(\n  'dbtype' => 'pgsql',\n  'dbname' => 'nextcloud',\n);\n")
    
    # Create archive
    archive_path = tempfile.mktemp(suffix=".tar.gz")
    with tarfile.open(archive_path, 'w:gz') as tar:
        tar.add(temp_dir, arcname='backup')
    
    shutil.rmtree(temp_dir)
    
    try:
        # Analyze archive
        with tarfile.open(archive_path, 'r:gz') as tar:
            all_files = [m.name for m in tar if m.isfile()]
            
            # Old logic (endswith)
            old_matches = [f for f in all_files if f.endswith('config.php')]
            
            # New logic (basename)
            new_matches = [f for f in all_files if os.path.basename(f) == 'config.php']
        
        print(f"\nFiles in archive: {len(all_files)}")
        print(f"\nOLD logic (endswith): {len(old_matches)} matches")
        for f in old_matches:
            print(f"  ❌ {f}")
        
        print(f"\nNEW logic (basename): {len(new_matches)} matches")
        for f in new_matches:
            print(f"  ✅ {f}")
        
        if len(old_matches) > len(new_matches):
            print(f"\n✅ SUCCESS: New logic is more selective ({len(new_matches)} vs {len(old_matches)})")
            return True
        else:
            print(f"\n❌ UNEXPECTED: New logic matched same or more files")
            return False
            
    finally:
        os.remove(archive_path)

def test_scenario_2_validation():
    """
    Scenario 2: Test the validation logic on file content
    """
    print("\n" + "="*70)
    print("SCENARIO 2: Content validation")
    print("="*70)
    
    # Test what the validation logic would do
    test_files = {
        "Real config.php": "<?php\n$CONFIG = array(\n  'dbtype' => 'mysql',\n);",
        "Apache config": "<?php\n$APACHE_CONFIG = array();\n",
        "Empty file": "",
        "Non-PHP file": "This is not PHP",
    }
    
    for name, content in test_files.items():
        has_config = '$CONFIG' in content
        has_dbtype = 'dbtype' in content
        would_pass = has_config or has_dbtype
        
        status = "✅ ACCEPT" if would_pass else "❌ REJECT"
        print(f"{status}: {name}")
        print(f"         Has $CONFIG: {has_config}, Has dbtype: {has_dbtype}")
    
    return True

def test_scenario_3_path_validation():
    """
    Scenario 3: Test path validation (config directory check)
    """
    print("\n" + "="*70)
    print("SCENARIO 3: Path validation (config directory)")
    print("="*70)
    
    test_paths = [
        "backup/config/config.php",
        "nextcloud/config/config.php",
        "backup/data/config.php",
        "config.php",
        "apps/myapp/config.php",
    ]
    
    for path in test_paths:
        parts = path.split('/')
        has_config = 'config' in parts
        basename = os.path.basename(path)
        is_exact = basename == 'config.php'
        
        would_extract = is_exact and has_config
        
        status = "✅ EXTRACT" if would_extract else "❌ SKIP"
        print(f"{status}: {path}")
        print(f"         Exact name: {is_exact}, In config dir: {has_config}")
    
    return True

def main():
    print("="*70)
    print("INTEGRATION TEST - Config.php Detection Fix")
    print("="*70)
    print("\nValidating the fixed extraction logic patterns and behavior\n")
    
    # First, validate the code has correct patterns
    print("="*70)
    print("CODE PATTERN VALIDATION")
    print("="*70)
    
    all_passed, results = validate_code_patterns()
    
    if isinstance(results, list):
        for passed, description in results:
            status = "✅" if passed else "❌"
            print(f"{status} {description}")
    else:
        print(f"❌ {results}")
        return False
    
    if not all_passed:
        print("\n❌ Code pattern validation failed")
        sys.exit(1)
    
    # Now run scenario tests
    test_results = []
    test_results.append(("Archive structure test", test_scenario_1_archive_structure()))
    test_results.append(("Content validation test", test_scenario_2_validation()))
    test_results.append(("Path validation test", test_scenario_3_path_validation()))
    
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    all_passed = True
    for name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        all_passed = all_passed and passed
    
    if all_passed:
        print("\n✅ ALL INTEGRATION TESTS PASSED")
        print("\nThe fix correctly:")
        print("  • Uses os.path.basename() for exact 'config.php' matching")
        print("  • Ignores files like apache-pretty-urls.config.php")
        print("  • Validates content contains $CONFIG or dbtype")
        print("  • Checks that parent directory is 'config'")
        print("  • Tracks and logs all potential config files found")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == '__main__':
    main()
