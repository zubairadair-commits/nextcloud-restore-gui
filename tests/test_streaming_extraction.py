#!/usr/bin/env python3
"""
Test script for streaming extraction functionality.
Demonstrates that extraction starts immediately without full archive scan.
"""

import os
import sys
import tempfile
import tarfile
import time
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def create_large_test_archive():
    """Create a test archive with many files to demonstrate streaming"""
    print("Creating test archive with 200 files...")
    temp_dir = tempfile.mkdtemp(prefix="streaming_test_")
    
    # Create directory structure
    config_dir = os.path.join(temp_dir, "config")
    data_dir = os.path.join(temp_dir, "data")
    apps_dir = os.path.join(temp_dir, "apps")
    os.makedirs(config_dir)
    os.makedirs(data_dir)
    os.makedirs(apps_dir)
    
    # Create config.php
    config_content = """<?php
$CONFIG = array (
  'dbtype' => 'mysql',
  'dbname' => 'nextcloud',
);
"""
    with open(os.path.join(config_dir, "config.php"), 'w') as f:
        f.write(config_content)
    
    # Create many files to simulate large backup
    print("Creating test files...")
    for i in range(200):
        if i % 3 == 0:
            file_path = os.path.join(data_dir, f"file_{i:03d}.txt")
        elif i % 3 == 1:
            file_path = os.path.join(apps_dir, f"app_{i:03d}.js")
        else:
            file_path = os.path.join(config_dir, f"config_{i:03d}.xml")
        
        # Create files with varying sizes
        with open(file_path, 'w') as f:
            f.write(f"Content for file {i}\n" * (100 + i * 10))
    
    # Create archive
    print("Compressing to tar.gz...")
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", prefix="streaming_test_", delete=False) as tmp_archive:
        archive_path = tmp_archive.name
    
    with tarfile.open(archive_path, 'w:gz') as tar:
        tar.add(temp_dir, arcname='.')
    
    archive_size = os.path.getsize(archive_path)
    file_count = sum(len(files) for _, _, files in os.walk(temp_dir))
    print(f"✓ Test archive created: {os.path.basename(archive_path)}")
    print(f"  Size: {archive_size / 1024:.1f} KB")
    print(f"  Files: {file_count}")
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    return archive_path, file_count, archive_size

def test_old_extraction_with_scan(archive_path, file_count):
    """Test old approach: full scan before extraction"""
    print("\n" + "="*70)
    print("OLD APPROACH: Full archive scan with getmembers()")
    print("="*70)
    
    extract_dir = tempfile.mkdtemp(prefix="old_extract_")
    
    try:
        start_time = time.time()
        scan_done_time = None
        first_file_time = None
        callback_times = []
        
        print("Opening archive...")
        open_start = time.time()
        
        with tarfile.open(archive_path, 'r:gz') as tar:
            open_time = time.time() - open_start
            print(f"  Archive opened in {open_time:.3f}s")
            
            print("Scanning archive with getmembers()...")
            scan_start = time.time()
            members = tar.getmembers()
            scan_time = time.time() - scan_start
            scan_done_time = time.time() - start_time
            print(f"  ⚠️  BLOCKING: Full scan took {scan_time:.3f}s")
            print(f"  Total time before first file: {scan_done_time:.3f}s")
            
            print("\nExtracting files...")
            for i, member in enumerate(members):
                tar.extract(member, path=extract_dir)
                if first_file_time is None:
                    first_file_time = time.time() - start_time
                
                # Report progress every 50 files
                if (i + 1) % 50 == 0 or (i + 1) == len(members):
                    callback_time = time.time() - start_time
                    callback_times.append(callback_time)
                    print(f"  [{i+1}/{len(members)}] {(i+1)/len(members)*100:.0f}% complete")
        
        total_time = time.time() - start_time
        
        print("\n📊 Results:")
        print(f"  Time to first file: {first_file_time:.3f}s (includes scan delay)")
        print(f"  Total extraction time: {total_time:.3f}s")
        print(f"  Files extracted: {file_count}")
        print(f"  Average rate: {file_count / total_time:.1f} files/s")
        
    finally:
        shutil.rmtree(extract_dir, ignore_errors=True)
    
    return scan_done_time, total_time

def test_new_streaming_extraction(archive_path, file_count, archive_size):
    """Test new approach: streaming extraction without upfront scan"""
    print("\n" + "="*70)
    print("NEW APPROACH: Streaming extraction (no upfront scan)")
    print("="*70)
    
    extract_dir = tempfile.mkdtemp(prefix="new_extract_")
    
    try:
        start_time = time.time()
        first_file_time = None
        callback_times = []
        files_extracted = 0
        
        print("Opening archive in streaming mode...")
        open_start = time.time()
        
        # Open archive file to track position
        with open(archive_path, 'rb') as archive_file:
            # Use 'r|gz' for streaming mode (no scan)
            with tarfile.open(fileobj=archive_file, mode='r|gz') as tar:
                open_time = time.time() - open_start
                print(f"  Archive opened in {open_time:.3f}s")
                print("  ✓ NO SCAN: Extraction starts immediately!")
                
                print("\nExtracting files (streaming)...")
                
                for member in tar:
                    tar.extract(member, path=extract_dir)
                    files_extracted += 1
                    
                    # Track position in compressed archive
                    current_position = archive_file.tell()
                    
                    if first_file_time is None:
                        first_file_time = time.time() - start_time
                        print(f"  ✓ First file extracted in {first_file_time:.3f}s")
                    
                    # Report progress every 50 files
                    if files_extracted % 50 == 0 or files_extracted == file_count:
                        callback_time = time.time() - start_time
                        callback_times.append(callback_time)
                        
                        # Calculate progress from compressed bytes
                        byte_progress = (current_position / archive_size * 100) if archive_size > 0 else 0
                        
                        print(f"  [{files_extracted}/?] {byte_progress:.0f}% by compressed size | "
                              f"Elapsed: {callback_time:.1f}s")
        
        total_time = time.time() - start_time
        
        print("\n📊 Results:")
        print(f"  Time to first file: {first_file_time:.3f}s (immediate start!)")
        print(f"  Total extraction time: {total_time:.3f}s")
        print(f"  Files extracted: {files_extracted}")
        print(f"  Average rate: {files_extracted / total_time:.1f} files/s")
        
    finally:
        shutil.rmtree(extract_dir, ignore_errors=True)
    
    return first_file_time, total_time

def main():
    """Run the streaming extraction test"""
    print("="*70)
    print("Streaming Extraction Test")
    print("="*70)
    print()
    print("This test demonstrates the difference between:")
    print("  1. OLD: Full archive scan before extraction (blocking)")
    print("  2. NEW: Streaming extraction (starts immediately)")
    print()
    
    # Create test archive
    archive_path, file_count, archive_size = create_large_test_archive()
    
    try:
        # Test old approach
        old_first_file_time, old_total_time = test_old_extraction_with_scan(archive_path, file_count)
        
        # Test new approach
        new_first_file_time, new_total_time = test_new_streaming_extraction(archive_path, file_count, archive_size)
        
        # Comparison
        print("\n" + "="*70)
        print("COMPARISON")
        print("="*70)
        print()
        print("⏱️  Time to First File:")
        print(f"   OLD: {old_first_file_time:.3f}s (includes blocking scan)")
        print(f"   NEW: {new_first_file_time:.3f}s (immediate)")
        print(f"   IMPROVEMENT: {(old_first_file_time - new_first_file_time):.3f}s faster")
        print()
        print("📊 Key Benefits of Streaming Extraction:")
        print("   ✓ No 'preparing extraction...' delay")
        print("   ✓ Progress bar starts moving immediately")
        print("   ✓ User sees files being extracted right away")
        print("   ✓ Byte-based progress until total count known")
        print("   ✓ Real-time filename updates")
        print()
        print("🎯 User Experience:")
        print("   - OLD: User waits with no visible progress")
        print("   - NEW: User sees immediate activity and progress")
        
        print("\n" + "="*70)
        print("✅ Test completed successfully!")
        print("="*70)
        
    finally:
        # Clean up
        if os.path.exists(archive_path):
            os.remove(archive_path)
            print(f"\n🧹 Cleaned up test archive")

if __name__ == '__main__':
    main()
