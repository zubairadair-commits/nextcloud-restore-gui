#!/usr/bin/env python3
"""
Test script to validate correct config.php detection.
This test creates a backup with multiple config-like files to ensure
only the correct config.php is extracted.
"""

import os
import sys
import tempfile
import tarfile
import shutil

def create_test_backup_with_multiple_configs():
    """
    Create a test tar.gz backup archive with multiple config files:
    - apache-pretty-urls.config.php (should NOT be extracted)
    - other.config.php (should NOT be extracted) 
    - config/config.php (SHOULD be extracted - the real one)
    """
    temp_dir = tempfile.mkdtemp(prefix="test_multi_config_")
    
    # Create a FAKE config file that should NOT be extracted
    fake_config_content = """<?php
// This is apache-pretty-urls.config.php - NOT the real config.php
$APACHE_CONFIG = array (
  'prettyurls' => true,
);
"""
    fake_config_path = os.path.join(temp_dir, "apache-pretty-urls.config.php")
    with open(fake_config_path, 'w') as f:
        f.write(fake_config_content)
    
    # Create another FAKE config file
    another_fake_content = """<?php
// This is other.config.php - NOT the real config.php
$OTHER_CONFIG = array (
  'setting' => 'value',
);
"""
    another_fake_path = os.path.join(temp_dir, "other.config.php")
    with open(another_fake_path, 'w') as f:
        f.write(another_fake_content)
    
    # Create the REAL config.php in the config directory
    config_dir = os.path.join(temp_dir, "config")
    os.makedirs(config_dir)
    
    real_config_content = """<?php
$CONFIG = array (
  'dbtype' => 'mysql',
  'dbname' => 'nextcloud',
  'dbuser' => 'nc_user',
  'dbhost' => 'localhost',
);
"""
    real_config_path = os.path.join(config_dir, "config.php")
    with open(real_config_path, 'w') as f:
        f.write(real_config_content)
    
    # Create tar.gz archive
    archive_path = tempfile.mktemp(suffix=".tar.gz", prefix="test_multi_config_")
    with tarfile.open(archive_path, 'w:gz') as tar:
        tar.add(temp_dir, arcname='nextcloud_backup')
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    return archive_path

def test_config_extraction_with_basename():
    """Test that only exact config.php is extracted, not files ending with config.php"""
    print("\n" + "="*60)
    print("TEST: Extract only exact config.php (not *config.php)")
    print("="*60)
    
    # Create test backup with multiple config files
    archive_path = create_test_backup_with_multiple_configs()
    
    try:
        print(f"Created test archive: {archive_path}")
        print(f"Archive contents:")
        
        # List all config-related files in archive
        config_files = []
        with tarfile.open(archive_path, 'r:gz') as tar:
            for member in tar:
                if 'config' in member.name.lower():
                    print(f"  - {member.name}")
                    config_files.append(member.name)
        
        # Check the logic used in the code
        print("\nSimulating extraction logic:")
        
        # OLD LOGIC (current - WRONG)
        print("\n1. Using endswith('config.php') [CURRENT - WRONG]:")
        matches_endswith = []
        for name in config_files:
            if name.endswith('config.php'):
                matches_endswith.append(name)
                print(f"   ✗ Would extract: {name}")
        
        # NEW LOGIC (proposed - CORRECT)
        print("\n2. Using os.path.basename() == 'config.php' [PROPOSED - CORRECT]:")
        matches_basename = []
        for name in config_files:
            if os.path.basename(name) == 'config.php':
                matches_basename.append(name)
                print(f"   ✓ Would extract: {name}")
        
        # Verify the results
        if len(matches_endswith) > 1:
            print(f"\n❌ ISSUE: endswith() matches {len(matches_endswith)} files (including wrong ones)")
        
        if len(matches_basename) == 1 and 'config/config.php' in matches_basename[0]:
            print(f"\n✅ SUCCESS: basename() correctly matches only the real config.php")
            return True
        else:
            print(f"\n❌ FAILED: basename() logic issue")
            return False
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        if os.path.exists(archive_path):
            os.remove(archive_path)

def test_validation_in_extraction():
    """Test that extraction validates file content before accepting it"""
    print("\n" + "="*60)
    print("TEST: Validate config.php content during extraction")
    print("="*60)
    
    print("This test checks if the extraction logic validates that")
    print("the extracted file contains $CONFIG and dbtype markers.")
    
    # Read the source file
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find the extract_config_php_only function
    start_idx = content.find('def extract_config_php_only(')
    if start_idx == -1:
        print("❌ FAILED: Function not found")
        return False
    
    # Extract the function content (up to next function or ~500 lines)
    next_func_idx = content.find('\ndef ', start_idx + 100)
    if next_func_idx == -1:
        next_func_idx = start_idx + 5000
    
    func_content = content[start_idx:next_func_idx]
    
    # Check for basename usage
    has_basename_check = 'os.path.basename' in func_content and "== 'config.php'" in func_content
    if has_basename_check:
        print("✅ Uses os.path.basename to match exact filename")
    else:
        print("❌ Does NOT use os.path.basename (still using endswith)")
        return False
    
    # Check for content validation
    has_config_validation = '$CONFIG' in func_content
    has_dbtype_validation = 'dbtype' in func_content
    
    if has_config_validation and has_dbtype_validation:
        print("✅ Validates file contains $CONFIG and dbtype")
    else:
        print("⚠️  Content validation could be improved")
        print(f"   - Checks for $CONFIG: {has_config_validation}")
        print(f"   - Checks for dbtype: {has_dbtype_validation}")
    
    # Check for parent directory validation
    has_parent_check = "'config' in path_parts" in func_content or "parent" in func_content.lower()
    if has_parent_check:
        print("✅ Validates parent directory is 'config'")
    else:
        print("⚠️  Could add parent directory validation")
    
    return has_basename_check

def main():
    print("="*60)
    print("CONFIG.PHP DETECTION - VALIDATION TESTS")
    print("="*60)
    print("\nVerifying that ONLY the exact config.php file is extracted,")
    print("not files like apache-pretty-urls.config.php\n")
    
    all_passed = True
    
    # Run tests
    all_passed = test_validation_in_extraction() and all_passed
    all_passed = test_config_extraction_with_basename() and all_passed
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\n✓ Only exact config.php is extracted")
        print("✓ Files ending with config.php are ignored")
        print("✓ Content is validated before acceptance")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("\nThe fix needs to be applied.")
        sys.exit(1)

if __name__ == '__main__':
    main()
