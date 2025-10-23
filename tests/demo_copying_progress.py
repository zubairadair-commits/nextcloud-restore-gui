#!/usr/bin/env python3
"""
Demonstration script showing the live copying progress functionality.
Simulates the file-by-file copying with progress updates.
"""

import os
import sys
import time
import tempfile
import shutil

def create_test_folders():
    """
    Create test folder structure simulating extracted Nextcloud backup
    """
    print("Creating test folder structure...")
    temp_dir = tempfile.mkdtemp(prefix="demo_nextcloud_extract_")
    
    # Create directory structure mimicking Nextcloud
    folders = {
        "config": 15,
        "data": 120,
        "apps": 80,
        "custom_apps": 25
    }
    
    total_files = 0
    
    for folder_name, file_count in folders.items():
        folder_path = os.path.join(temp_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Create subdirectories
        for i in range(3):
            subdir = os.path.join(folder_path, f"subdir_{i}")
            os.makedirs(subdir, exist_ok=True)
            
            # Create files in subdirectories
            files_per_subdir = file_count // 3
            for j in range(files_per_subdir):
                filepath = os.path.join(subdir, f"file_{j}.txt")
                with open(filepath, 'w') as f:
                    f.write(f"Test data for {folder_name}/subdir_{i}/file_{j}.txt\n" * 10)
                total_files += 1
    
    print(f"✓ Created test structure with {total_files} files in {len(folders)} folders")
    print(f"  Location: {temp_dir}")
    return temp_dir, total_files, folders

def simulate_copy_progress(folder_name, file_count, progress_start, progress_end):
    """
    Simulate copying files with progress updates
    """
    print(f"\n{'='*70}")
    print(f"Copying {folder_name} folder ({file_count} files)")
    print(f"Progress range: {progress_start}% - {progress_end}%")
    print(f"{'='*70}")
    
    start_time = time.time()
    files_copied = 0
    
    # Simulate copying files one by one
    for i in range(file_count):
        files_copied += 1
        elapsed = time.time() - start_time
        
        # Calculate progress
        file_percent = (files_copied / file_count) * 100
        current_progress = progress_start + int((progress_end - progress_start) * (files_copied / file_count))
        
        # Calculate time estimates
        if elapsed > 0:
            rate = files_copied / elapsed
            remaining_files = file_count - files_copied
            est_remaining = remaining_files / rate if rate > 0 else 0
            
            elapsed_str = format_time(elapsed)
            est_str = format_time(est_remaining)
        else:
            elapsed_str = "0s"
            est_str = "calculating..."
        
        # Simulate current file being copied
        current_file = f"{folder_name}/subdir_{i % 3}/file_{i}.txt"
        if len(current_file) > 60:
            file_display = "..." + current_file[-57:]
        else:
            file_display = current_file
        
        # Print progress update (every 5 files to match implementation)
        if files_copied % 5 == 0 or files_copied == file_count:
            status_msg = f"Copying {folder_name}: {files_copied}/{file_count} files | Elapsed: {elapsed_str} | Est: {est_str}"
            print(f"[{current_progress:3d}%] {status_msg}")
            print(f"       Current file: {file_display}")
        
        # Simulate copy delay (faster for demo)
        time.sleep(0.02)
    
    total_time = time.time() - start_time
    print(f"\n✓ Completed copying {folder_name}: {files_copied} files in {format_time(total_time)}")

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

def demonstrate_copying_progress():
    """
    Demonstrate the copying progress with live updates
    """
    print("\n" + "="*70)
    print("DEMONSTRATION: Live File-by-File Copying Progress")
    print("="*70)
    print("\nThis demo simulates the copying phase of Nextcloud restore (30-60%)")
    print("Showing live progress updates as files are copied to the container.\n")
    
    # Create test structure
    temp_dir, total_files, folders = create_test_folders()
    
    try:
        print(f"\nTotal files to copy: {total_files} across {len(folders)} folders")
        print("Progress will update live as each file is copied...\n")
        
        # Wait a bit before starting
        time.sleep(1)
        
        # Simulate copying each folder
        folder_list = [
            ("config", folders["config"], 30, 37),
            ("data", folders["data"], 37, 45),
            ("apps", folders["apps"], 45, 52),
            ("custom_apps", folders["custom_apps"], 52, 60),
        ]
        
        overall_start = time.time()
        
        for folder_name, file_count, start_pct, end_pct in folder_list:
            simulate_copy_progress(folder_name, file_count, start_pct, end_pct)
            time.sleep(0.5)  # Brief pause between folders
        
        overall_elapsed = time.time() - overall_start
        
        print("\n" + "="*70)
        print("COPYING PHASE COMPLETE")
        print("="*70)
        print(f"✓ Copied {total_files} files in {format_time(overall_elapsed)}")
        print(f"✓ Progress: 30% → 60% (completed)")
        print("\nKey Features Demonstrated:")
        print("  • Live progress updates during copying")
        print("  • File count tracking (X/Y files)")
        print("  • Current file display")
        print("  • Elapsed and estimated time")
        print("  • Smooth progress bar updates (30-60% range)")
        print("  • Thread-safe UI updates (using self.after())")
        
    finally:
        # Clean up
        print("\nCleaning up test files...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("✓ Cleanup complete")

def show_progress_comparison():
    """
    Show before/after comparison
    """
    print("\n" + "="*70)
    print("BEFORE vs AFTER COMPARISON")
    print("="*70)
    
    print("\n📊 BEFORE (Old Implementation):")
    print("  • Progress updated based on elapsed time estimate")
    print("  • No visibility into which files are being copied")
    print("  • Only showed folder name")
    print("  • Progress would sometimes 'stick' at one value")
    print("  • Example: 'Copying data (128.5MB)...' [stuck at 37%]")
    
    print("\n📊 AFTER (New Implementation):")
    print("  • Live updates for every 5 files copied")
    print("  • Shows exact file count: 'Copying data: 45/120 files'")
    print("  • Displays current file: 'Copying: data/photos/img_0045.jpg'")
    print("  • Progress bar moves smoothly: 37% → 38% → 39% → ...")
    print("  • Accurate time estimates based on actual copy rate")
    print("  • Thread-safe updates keep UI responsive")
    
    print("\n📈 Progress Range:")
    print("  0-20%  : Extraction (already enhanced)")
    print("  20-30% : Transition")
    print("  30-60% : Copying files ✨ NEW: Live file-by-file updates")
    print("  60-75% : Database restore")
    print("  75-100%: Config updates and finalization")

if __name__ == "__main__":
    try:
        demonstrate_copying_progress()
        show_progress_comparison()
        
        print("\n" + "="*70)
        print("✓ Demo completed successfully!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
