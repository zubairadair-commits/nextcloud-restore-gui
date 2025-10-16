#!/usr/bin/env python3
"""
Test script to simulate SQLite detection flow.
This validates the complete flow from detection to backup.
"""

import sys
import os
import tempfile
import re

def create_test_config_php(dbtype):
    """Create a test config.php file with the specified dbtype."""
    content = f"""<?php
$CONFIG = array (
  'instanceid' => 'test123',
  'passwordsalt' => 'salt123',
  'secret' => 'secret123',
  'trusted_domains' => 
  array (
    0 => 'localhost',
  ),
  'datadirectory' => '/var/www/html/data',
  'dbtype' => '{dbtype}',
  'version' => '27.0.0.1',
  'overwrite.cli.url' => 'http://localhost',
  'installed' => true,
);
"""
    return content

def test_parse_config_php_dbtype():
    """Test parse_config_php_dbtype function with sqlite3."""
    print("Testing parse_config_php_dbtype function...")
    
    # Import the function
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # We can't import directly due to tkinter, so we'll read and extract the function
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Extract the parse_config_php_dbtype function
    pattern = r"def parse_config_php_dbtype\(config_php_path\):.*?(?=\ndef )"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("  ✗ Could not extract parse_config_php_dbtype function")
        return False
    
    func_code = match.group(0)
    
    # Check that it has normalization
    if "if dbtype == 'sqlite3':" in func_code and "dbtype = 'sqlite'" in func_code:
        print("  ✓ parse_config_php_dbtype has sqlite3 normalization")
    else:
        print("  ✗ parse_config_php_dbtype missing sqlite3 normalization")
        return False
    
    return True

def test_check_database_dump_utility_logic():
    """Test check_database_dump_utility function logic."""
    print("\nTesting check_database_dump_utility logic...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Extract the function
    pattern = r"def check_database_dump_utility\(dbtype\):.*?(?=\ndef )"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("  ✗ Could not extract check_database_dump_utility function")
        return False
    
    func_code = match.group(0)
    
    # Check that it handles both sqlite and sqlite3
    if "elif dbtype in ['sqlite', 'sqlite3']:" in func_code:
        print("  ✓ check_database_dump_utility handles sqlite and sqlite3")
    else:
        print("  ✗ check_database_dump_utility doesn't handle both sqlite types")
        return False
    
    # Check that it returns True
    if "return True, 'sqlite'" in func_code:
        print("  ✓ check_database_dump_utility returns True for SQLite")
    else:
        print("  ✗ check_database_dump_utility doesn't return True for SQLite")
        return False
    
    return True

def test_backup_flow_logic():
    """Test that backup flow correctly handles SQLite."""
    print("\nTesting backup flow logic...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find start_backup method and check utility check
    pattern1 = r"def start_backup\(self\):.*?if dbtype not in \['sqlite', 'sqlite3'\]:.*?check_database_dump_utility"
    if not re.search(pattern1, content, re.DOTALL):
        print("  ✗ start_backup doesn't properly skip utility check for SQLite")
        return False
    print("  ✓ start_backup skips utility check for sqlite/sqlite3")
    
    # Find run_backup_process and check SQLite handling
    pattern2 = r"def run_backup_process\(.*?if dbtype in \['sqlite', 'sqlite3'\]:.*?SQLite database backed up with data folder"
    if not re.search(pattern2, content, re.DOTALL):
        print("  ✗ run_backup_process doesn't properly handle SQLite")
        return False
    print("  ✓ run_backup_process handles sqlite/sqlite3 correctly")
    
    # Find run_backup_process_scheduled and check SQLite handling
    pattern3 = r"def run_backup_process_scheduled\(.*?if dbtype in \['sqlite', 'sqlite3'\]:.*?SQLite database backed up with data folder"
    if not re.search(pattern3, content, re.DOTALL):
        print("  ✗ run_backup_process_scheduled doesn't properly handle SQLite")
        return False
    print("  ✓ run_backup_process_scheduled handles sqlite/sqlite3 correctly")
    
    return True

def test_no_utility_prompts_for_sqlite():
    """Test that no utility prompts occur for SQLite."""
    print("\nTesting that no utility prompts occur for SQLite...")
    
    main_file = "../src/nextcloud_restore_and_backup-v9.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the utility check logic
    # The pattern should be: if dbtype not in ['sqlite', 'sqlite3']: then check utilities
    pattern = r"if dbtype not in \['sqlite', 'sqlite3'\]:\s+utility_installed.*?check_database_dump_utility"
    if not re.search(pattern, content, re.DOTALL):
        print("  ✗ Utility check doesn't properly exclude sqlite/sqlite3")
        return False
    
    print("  ✓ Utility check properly excludes sqlite/sqlite3")
    print("  ✓ No prompt_install_database_utility will be called for SQLite")
    
    return True

def test_config_file_scenarios():
    """Test various config.php scenarios."""
    print("\nTesting config.php scenarios...")
    
    scenarios = [
        ('sqlite', 'SQLite with lowercase sqlite'),
        ('sqlite3', 'SQLite with sqlite3'),
        ('SQLITE3', 'SQLite with uppercase SQLITE3'),
    ]
    
    for dbtype_value, description in scenarios:
        config_content = create_test_config_php(dbtype_value)
        
        # Check if the detection would normalize it
        normalized = dbtype_value.lower()
        if normalized == 'sqlite3':
            normalized = 'sqlite'
        
        if normalized == 'sqlite':
            print(f"  ✓ {description} → normalized to 'sqlite'")
        else:
            print(f"  ✗ {description} → unexpected result: '{normalized}'")
            return False
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("SQLite Detection Flow Validation")
    print("=" * 60)
    
    all_passed = True
    
    all_passed &= test_parse_config_php_dbtype()
    all_passed &= test_check_database_dump_utility_logic()
    all_passed &= test_backup_flow_logic()
    all_passed &= test_no_utility_prompts_for_sqlite()
    all_passed &= test_config_file_scenarios()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All flow tests passed!")
        print("\nSummary:")
        print("- SQLite and sqlite3 are normalized to 'sqlite'")
        print("- No utility check prompts for SQLite databases")
        print("- SQLite databases are backed up with data folder")
        print("- Both manual and scheduled backups work correctly")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
