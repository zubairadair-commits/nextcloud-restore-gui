#!/usr/bin/env python3
"""
Demonstration script showing the live extraction progress functionality.
Creates a test backup and demonstrates the enhanced progress reporting.
"""

import os
import sys
import time
import tempfile
import tarfile
import shutil

def create_realistic_test_backup():
    """
    Create a realistic test backup with multiple directories and files
    to simulate a real Nextcloud backup
    """
    print("Creating test backup archive...")
    temp_dir = tempfile.mkdtemp(prefix="demo_nextcloud_backup_")
    
    # Create directory structure mimicking Nextcloud backup
    dirs = [
        os.path.join(temp_dir, ".config"),
        os.path.join(temp_dir, ".data", "admin", "files"),
        os.path.join(temp_dir, ".data", "user1", "files"),
        os.path.join(temp_dir, ".apps", "files_external"),
        os.path.join(temp_dir, ".apps", "notes"),
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    # Create config.php
    config_php_content = """<?php
$CONFIG = array (
  'instanceid' => 'demo123abc',
  'passwordsalt' => 'demosalt',
  'secret' => 'demosecret',
  'trusted_domains' => array (
    0 => 'localhost',
  ),
  'datadirectory' => '/var/www/html/data',
  'dbtype' => 'mysql',
  'version' => '27.1.0',
  'overwrite.cli.url' => 'http://localhost',
  'dbname' => 'nextcloud',
  'dbhost' => 'localhost',
  'dbuser' => 'nextcloud',
  'dbpassword' => 'password123',
  'installed' => true,
);
"""
    with open(os.path.join(temp_dir, ".config", "config.php"), 'w') as f:
        f.write(config_php_content)
    
    # Create multiple files simulating user data
    print("Creating test files...")
    file_count = 0
    
    # Admin files
    for i in range(15):
        filepath = os.path.join(temp_dir, ".data", "admin", "files", f"document_{i}.txt")
        with open(filepath, 'w') as f:
            f.write(f"Admin document {i}\n" * 50)
        file_count += 1
    
    # User1 files
    for i in range(20):
        filepath = os.path.join(temp_dir, ".data", "user1", "files", f"photo_{i}.jpg")
        with open(filepath, 'wb') as f:
            f.write(b'JPEG_DATA' * 1000)  # Simulate image data
        file_count += 1
    
    # App files
    for app in ["files_external", "notes"]:
        for i in range(10):
            filepath = os.path.join(temp_dir, ".apps", app, f"file_{i}.json")
            with open(filepath, 'w') as f:
                f.write('{"data": "test"}' * 20)
            file_count += 1
    
    # Create database dump
    print("Creating database dump...")
    db_dump_path = os.path.join(temp_dir, ".nextcloud-db.sql")
    with open(db_dump_path, 'w') as f:
        f.write("-- Database dump\n")
        f.write("CREATE TABLE oc_users (\n")
        f.write("  uid VARCHAR(64) PRIMARY KEY\n")
        f.write(");\n")
        for i in range(100):
            f.write(f"INSERT INTO oc_users VALUES ('user{i}');\n")
    
    # Create tar.gz archive
    print("Compressing to tar.gz...")
    # Use NamedTemporaryFile with delete=False for secure temporary file
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", prefix="nextcloud_demo_backup_", delete=False) as tmp_file:
        archive_path = tmp_file.name
    with tarfile.open(archive_path, 'w:gz') as tar:
        tar.add(temp_dir, arcname='.')
    
    # Get archive info
    archive_size = os.path.getsize(archive_path)
    
    # Count total items in archive
    with tarfile.open(archive_path, 'r:gz') as tar:
        total_items = len(tar.getmembers())
    
    print(f"\n✓ Test backup created successfully!")
    print(f"  Archive: {os.path.basename(archive_path)}")
    print(f"  Size: {archive_size / (1024*1024):.2f} MB")
    print(f"  Total items: {total_items} (files and directories)")
    print(f"  Test files created: {file_count}")
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    return archive_path, archive_size, total_items

def demonstrate_live_extraction(archive_path):
    """
    Demonstrate the live extraction with progress updates
    """
    print("\n" + "="*70)
    print("LIVE EXTRACTION PROGRESS DEMONSTRATION")
    print("="*70)
    print("\nThis demonstrates the enhanced extraction with live progress updates:")
    print("- File-by-file progress tracking")
    print("- Real-time progress percentage")
    print("- Elapsed time and estimated time remaining")
    print("- Current file being extracted")
    print("- Batch updates for UI responsiveness\n")
    
    extract_dir = tempfile.mkdtemp(prefix="demo_extract_")
    
    try:
        start_time = time.time()
        last_update_time = start_time
        
        def progress_callback(files_extracted, total_files, current_file):
            """Callback to display progress"""
            nonlocal last_update_time
            
            # Calculate progress
            percent = (files_extracted / total_files * 100) if total_files > 0 else 0
            
            # Calculate timing
            elapsed = time.time() - start_time
            if files_extracted > 0 and elapsed > 0:
                rate = files_extracted / elapsed
                remaining_files = total_files - files_extracted
                est_remaining = remaining_files / rate if rate > 0 else 0
                
                elapsed_str = format_time(elapsed)
                est_str = format_time(est_remaining)
                
                # Show progress
                progress_bar = create_progress_bar(percent, width=40)
                
                # Only print every 0.5 seconds or at completion to avoid spam
                current_time = time.time()
                if (current_time - last_update_time) >= 0.5 or files_extracted == total_files:
                    # Clear line and print new progress
                    print(f"\r{progress_bar} {percent:5.1f}% | "
                          f"Files: {files_extracted}/{total_files} | "
                          f"Elapsed: {elapsed_str} | "
                          f"Est: {est_str} | "
                          f"Current: {current_file[:30]}", end='', flush=True)
                    last_update_time = current_time
        
        print("Starting extraction with live progress updates...\n")
        
        # Perform extraction with progress
        with tarfile.open(archive_path, 'r:gz') as tar:
            members = tar.getmembers()
            total_files = len(members)
            files_extracted = 0
            batch_count = 0
            batch_size = 10  # Update every 10 files
            
            for member in members:
                tar.extract(member, path=extract_dir)
                files_extracted += 1
                batch_count += 1
                
                if batch_count >= batch_size or files_extracted == total_files:
                    current_file = os.path.basename(member.name) if member.name else "..."
                    progress_callback(files_extracted, total_files, current_file)
                    batch_count = 0
        
        # Final newline after progress bar
        print("\n")
        
        total_time = time.time() - start_time
        print(f"\n✓ Extraction completed successfully!")
        print(f"  Total time: {format_time(total_time)}")
        print(f"  Files extracted: {total_files}")
        print(f"  Average rate: {total_files/total_time:.1f} files/second")
        
        # Show what was extracted
        print(f"\n📁 Extracted to: {extract_dir}")
        
        # Count extracted files
        extracted_count = 0
        for root, dirs, files in os.walk(extract_dir):
            extracted_count += len(files)
        print(f"  Actual files on disk: {extracted_count}")
        
    finally:
        # Clean up
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)

def create_progress_bar(percent, width=40):
    """Create a text-based progress bar"""
    filled = int(width * percent / 100)
    empty = width - filled
    bar = '█' * filled + '░' * empty
    return f"[{bar}]"

def format_time(seconds):
    """Format time in seconds to human-readable format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

def compare_with_old_approach():
    """Show comparison with old approach"""
    print("\n" + "="*70)
    print("COMPARISON WITH OLD APPROACH")
    print("="*70)
    
    print("\nOLD APPROACH (Before this change):")
    print("  ❌ Progress bar updated only in steps (10%, 12%, 14%, 16%, 18%)")
    print("  ❌ No visibility into which files are being extracted")
    print("  ❌ No accurate time estimates during extraction")
    print("  ❌ User sees static progress for long periods")
    print("  ❌ Can't tell if extraction is stuck or progressing")
    
    print("\nNEW APPROACH (After this change):")
    print("  ✅ Progress bar updates continuously as files are extracted")
    print("  ✅ Shows exact file count (e.g., 150/1000 files)")
    print("  ✅ Displays current file being extracted")
    print("  ✅ Real-time elapsed time and estimated time remaining")
    print("  ✅ Batch updates prevent UI slowdown")
    print("  ✅ User always knows extraction is progressing")
    print("  ✅ Can see if a particular file is taking long to extract")

def main():
    """Main demonstration"""
    print("="*70)
    print("NEXTCLOUD RESTORE - LIVE EXTRACTION PROGRESS DEMO")
    print("="*70)
    print("\nThis demonstration shows the enhanced extraction progress features:")
    print("✨ Live file-by-file progress updates")
    print("✨ Real-time elapsed and estimated time")
    print("✨ Current file being extracted")
    print("✨ Smooth, responsive progress bar")
    print()
    
    # Create test backup
    archive_path = None
    try:
        archive_path, size, total_items = create_realistic_test_backup()
        
        # Wait a moment
        print("\nStarting demonstration in 2 seconds...")
        time.sleep(2)
        
        # Demonstrate live extraction
        demonstrate_live_extraction(archive_path)
        
        # Show comparison
        compare_with_old_approach()
        
        print("\n" + "="*70)
        print("BENEFITS FOR USERS")
        print("="*70)
        print("\n🎯 Better User Experience:")
        print("  • Users can see extraction is actively progressing")
        print("  • No more wondering if the app has frozen")
        print("  • Clear visibility into what's happening")
        print("  • Accurate time estimates help users plan")
        
        print("\n🛡️ Improved Reliability:")
        print("  • Can identify if extraction is stuck on a file")
        print("  • Better feedback for troubleshooting")
        print("  • Progress is saved between batches")
        
        print("\n⚡ Performance:")
        print("  • Background threading keeps UI responsive")
        print("  • Batch updates prevent UI slowdown")
        print("  • No blocking during extraction")
        
        print("\n✅ This enhancement successfully improves user feedback")
        print("   and reliability for all restore operations!\n")
        
    finally:
        # Clean up
        if archive_path and os.path.exists(archive_path):
            os.remove(archive_path)
            print(f"🧹 Cleaned up test archive")

if __name__ == '__main__':
    main()
