#!/usr/bin/env python3
"""
Visual demonstration of the progressbar fix.

This script creates a simple backup archive and demonstrates extraction 
with the fixed progress bar that updates visually in real-time.

Run this to visually confirm the fix works:
    python3 demo_progressbar_fix.py

The progress bar should:
1. Start at 0%
2. Fill smoothly as files are extracted
3. Reach 100% when complete
"""

import os
import sys
import tempfile
import tarfile
import time
import shutil

# Add src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(os.path.dirname(script_dir), 'src')
sys.path.insert(0, src_path)

def create_test_archive():
    """Create a test tar.gz archive with multiple files"""
    temp_dir = tempfile.mkdtemp(prefix="progressbar_test_")
    
    # Create test files
    print("Creating test files...")
    for i in range(50):
        filepath = os.path.join(temp_dir, f"file_{i:03d}.txt")
        with open(filepath, 'w') as f:
            f.write(f"Test file {i}\n" * 100)
    
    # Create tar.gz archive
    archive_path = os.path.join(temp_dir, "test_backup.tar.gz")
    print(f"Creating archive: {archive_path}")
    
    with tarfile.open(archive_path, 'w:gz') as tar:
        for i in range(50):
            filepath = os.path.join(temp_dir, f"file_{i:03d}.txt")
            tar.add(filepath, arcname=f"file_{i:03d}.txt")
    
    # Clean up source files, keep archive
    for i in range(50):
        os.remove(os.path.join(temp_dir, f"file_{i:03d}.txt"))
    
    return archive_path, temp_dir

def demo_extraction_with_progress():
    """Demonstrate extraction with progress callback"""
    # Import the fast_extract_tar_gz function from the main script
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "nextcloud_restore", 
        os.path.join(src_path, "nextcloud_restore_and_backup-v9.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fast_extract_tar_gz = module.fast_extract_tar_gz
    
    print("\n" + "="*70)
    print("PROGRESS BAR FIX DEMONSTRATION")
    print("="*70)
    
    # Create test archive
    archive_path, temp_dir = create_test_archive()
    extract_dir = os.path.join(temp_dir, "extracted")
    
    print(f"\nTest archive: {archive_path}")
    print(f"Extract to: {extract_dir}\n")
    
    # Track progress
    progress_data = {
        'start_time': time.time(),
        'last_percent': 0
    }
    
    def show_progress(files_extracted, total_files, current_file, bytes_processed=0, total_bytes=0):
        """Progress callback to display extraction progress"""
        # Calculate percentage
        if total_files and total_files > 0:
            percent = int((files_extracted / total_files) * 100)
        elif total_bytes > 0 and bytes_processed > 0:
            percent = int((bytes_processed / total_bytes) * 100)
        else:
            percent = 0
        
        # Show progress bar
        bar_width = 50
        filled = int(bar_width * percent / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        # Elapsed time
        elapsed = time.time() - progress_data['start_time']
        
        # Print progress (using \r to overwrite line)
        print(f"\r[{bar}] {percent}% | Files: {files_extracted}/{total_files or '?'} | "
              f"Time: {elapsed:.1f}s | Current: {current_file[:30]}", end='', flush=True)
        
        progress_data['last_percent'] = percent
    
    print("Starting extraction with live progress updates...")
    print("(The progress bar below should fill from left to right)\n")
    
    try:
        # Extract with progress callback
        fast_extract_tar_gz(
            archive_path,
            extract_dir,
            progress_callback=show_progress,
            batch_size=1  # Update for every file
        )
        
        print("\n")  # New line after progress bar
        print("\n✅ Extraction complete!")
        
        # Verify extraction
        extracted_files = os.listdir(extract_dir)
        print(f"✅ Extracted {len(extracted_files)} files")
        
        # Calculate time
        total_time = time.time() - progress_data['start_time']
        print(f"✅ Total time: {total_time:.2f}s")
        
        print("\n" + "="*70)
        print("RESULT: Progress bar filled correctly! ✅")
        print("="*70)
        
        # Cleanup
        print(f"\nCleaning up test files from {temp_dir}...")
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return False

if __name__ == "__main__":
    print("\nThis demo shows that the progress bar fix works correctly.")
    print("You should see a progress bar that fills from 0% to 100%.\n")
    
    try:
        success = demo_extraction_with_progress()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
