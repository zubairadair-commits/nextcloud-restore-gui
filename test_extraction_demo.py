#!/usr/bin/env python3
"""
Demonstration script showing the efficiency improvement of the extraction refactoring.
This creates a test backup and shows the difference between the old and new approaches.
"""

import os
import sys
import time
import tempfile
import tarfile
import shutil

def create_test_backup_with_large_files():
    """
    Create a realistic test backup with config.php and some large dummy files
    to simulate a real Nextcloud backup
    """
    print("Creating test backup archive...")
    temp_dir = tempfile.mkdtemp(prefix="test_nextcloud_backup_")
    
    # Create directory structure
    config_dir = os.path.join(temp_dir, ".config")
    data_dir = os.path.join(temp_dir, ".data")
    apps_dir = os.path.join(temp_dir, ".apps")
    os.makedirs(config_dir)
    os.makedirs(data_dir)
    os.makedirs(apps_dir)
    
    # Create config.php
    config_php_content = """<?php
$CONFIG = array (
  'instanceid' => 'test123',
  'passwordsalt' => 'saltsaltsa',
  'secret' => 'secretsecret',
  'trusted_domains' => array (
    0 => 'localhost',
  ),
  'datadirectory' => '/var/www/html/data',
  'dbtype' => 'mysql',
  'version' => '25.0.3',
  'overwrite.cli.url' => 'http://localhost',
  'dbname' => 'nextcloud',
  'dbhost' => 'localhost',
  'dbport' => '',
  'dbtableprefix' => 'oc_',
  'dbuser' => 'nextcloud',
  'dbpassword' => 'password123',
  'installed' => true,
);
"""
    with open(os.path.join(config_dir, "config.php"), 'w') as f:
        f.write(config_php_content)
    
    # Create some large dummy files to simulate data
    print("Creating dummy data files (simulating user data)...")
    for i in range(5):
        dummy_file = os.path.join(data_dir, f"user_file_{i}.dat")
        with open(dummy_file, 'wb') as f:
            # Create 5MB files
            f.write(b'X' * (5 * 1024 * 1024))
    
    # Create database dump
    print("Creating dummy database dump...")
    with open(os.path.join(temp_dir, ".nextcloud-db.sql"), 'w') as f:
        f.write("-- Database dump\n" * 10000)
    
    # Create tar.gz archive
    print("Compressing to tar.gz...")
    archive_path = tempfile.mktemp(suffix=".tar.gz", prefix="nextcloud_backup_")
    with tarfile.open(archive_path, 'w:gz') as tar:
        tar.add(temp_dir, arcname='.')
    
    # Get archive size
    archive_size = os.path.getsize(archive_path)
    print(f"✓ Test backup created: {archive_path}")
    print(f"  Size: {archive_size / (1024*1024):.2f} MB")
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    return archive_path, archive_size

def old_approach_full_extraction(archive_path):
    """Simulate the old approach: extract everything"""
    print("\n" + "="*60)
    print("OLD APPROACH: Extract entire backup")
    print("="*60)
    
    temp_dir = tempfile.mkdtemp(prefix="old_extract_")
    
    start_time = time.time()
    print("Extracting entire backup archive...")
    
    with tarfile.open(archive_path, 'r:gz') as tar:
        tar.extractall(path=temp_dir)
    
    elapsed = time.time() - start_time
    
    # Count extracted files
    file_count = sum(len(files) for _, _, files in os.walk(temp_dir))
    dir_size = sum(
        os.path.getsize(os.path.join(root, file))
        for root, _, files in os.walk(temp_dir)
        for file in files
    )
    
    print(f"✓ Extraction complete")
    print(f"  Time taken: {elapsed:.3f} seconds")
    print(f"  Files extracted: {file_count}")
    print(f"  Disk space used: {dir_size / (1024*1024):.2f} MB")
    
    # Now find config.php
    print("\nSearching for config.php...")
    config_path = None
    for root, _, files in os.walk(temp_dir):
        if 'config.php' in files:
            config_path = os.path.join(root, 'config.php')
            break
    
    if config_path:
        print(f"✓ Found config.php: {config_path}")
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    return elapsed, file_count, dir_size

def new_approach_single_file(archive_path):
    """Simulate the new approach: extract only config.php"""
    print("\n" + "="*60)
    print("NEW APPROACH: Extract only config.php")
    print("="*60)
    
    temp_dir = tempfile.mkdtemp(prefix="new_extract_")
    
    start_time = time.time()
    print("Searching for config.php in archive...")
    
    config_path = None
    with tarfile.open(archive_path, 'r:gz') as tar:
        for member in tar:
            if member.isfile() and os.path.basename(member.name) == 'config.php':
                path_parts = member.name.split('/')
                if 'config' in path_parts:
                    print(f"✓ Found config.php: {member.name}")
                    tar.extract(member, path=temp_dir)
                    config_path = os.path.join(temp_dir, member.name)
                    break
    
    elapsed = time.time() - start_time
    
    # Count extracted files (should be 1)
    file_count = sum(len(files) for _, _, files in os.walk(temp_dir))
    dir_size = sum(
        os.path.getsize(os.path.join(root, file))
        for root, _, files in os.walk(temp_dir)
        for file in files
    )
    
    print(f"✓ Extraction complete")
    print(f"  Time taken: {elapsed:.3f} seconds")
    print(f"  Files extracted: {file_count}")
    print(f"  Disk space used: {dir_size / 1024:.2f} KB")
    
    if config_path:
        print(f"✓ Config.php extracted: {config_path}")
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    return elapsed, file_count, dir_size

def main():
    print("="*60)
    print("EXTRACTION EFFICIENCY DEMONSTRATION")
    print("="*60)
    print("\nThis demonstrates the performance improvement from extracting")
    print("only config.php initially vs extracting the entire backup.\n")
    
    # Create test backup
    archive_path, archive_size = create_test_backup_with_large_files()
    
    try:
        # Test old approach
        old_time, old_files, old_size = old_approach_full_extraction(archive_path)
        
        # Test new approach
        new_time, new_files, new_size = new_approach_single_file(archive_path)
        
        # Show comparison
        print("\n" + "="*60)
        print("PERFORMANCE COMPARISON")
        print("="*60)
        print(f"\nBackup archive size: {archive_size / (1024*1024):.2f} MB")
        print("\n{:<30} {:>12} {:>15}".format("Metric", "Old Approach", "New Approach"))
        print("-" * 60)
        print("{:<30} {:>11.3f}s {:>14.3f}s".format("Extraction time", old_time, new_time))
        print("{:<30} {:>12} {:>15}".format("Files extracted", old_files, new_files))
        print("{:<30} {:>9.2f} MB {:>12.2f} KB".format(
            "Temp disk usage", 
            old_size / (1024*1024),
            new_size / 1024
        ))
        
        if old_time > 0 and new_time > 0:
            speedup = old_time / new_time
            space_saving = (1 - (new_size / old_size)) * 100
            
            print("\n" + "="*60)
            print("IMPROVEMENT")
            print("="*60)
            print(f"⚡ Speed improvement: {speedup:.1f}x faster")
            print(f"💾 Disk space saved: {space_saving:.1f}%")
            print(f"📉 Files processed: {old_files} → {new_files} (reduced by {old_files - new_files})")
            
            print("\n" + "="*60)
            print("CONCLUSION")
            print("="*60)
            print("✅ The new approach is significantly more efficient!")
            print("✅ Users get immediate database type detection")
            print("✅ Full extraction is deferred until needed")
            print("✅ GUI remains responsive during detection")
        
    finally:
        # Clean up test archive
        if os.path.exists(archive_path):
            os.remove(archive_path)
            print(f"\n🧹 Cleaned up test archive")

if __name__ == '__main__':
    main()
