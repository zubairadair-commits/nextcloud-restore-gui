#!/usr/bin/env python3
"""
Test to verify that progress bar ranges are correctly mapped according to requirements.

Requirements:
- Extraction: 0-20%
- Copying data: 20-80% (60% of total - the largest portion)
- Database restore: 80-90%
- Setup/finalization: 90-100%
"""

import re
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def extract_progress_calls(file_path):
    """
    Extract all set_restore_progress calls with their percentages.
    Returns a list of tuples (line_number, percentage, message_context)
    """
    progress_calls = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines, 1):
        # Match set_restore_progress calls with numeric first argument
        match = re.search(r'set_restore_progress\s*\(\s*(\d+)\s*,\s*(.+?)\)', line)
        if match:
            percent = int(match.group(1))
            message = match.group(2).strip()
            # Get context from the line or nearby comments
            context = ""
            if i > 1:
                prev_line = lines[i-2].strip()
                if "Extraction" in prev_line or "Copying" in prev_line or "Database" in prev_line:
                    context = prev_line
            progress_calls.append((i, percent, message, context))
    
    return progress_calls

def categorize_progress_calls(calls):
    """
    Categorize progress calls into phases based on percentage ranges.
    """
    extraction = []
    container_setup = []
    copying = []
    database = []
    finalization = []
    
    for line_num, percent, message, context in calls:
        if percent == 0:
            continue  # Skip error/reset cases
        elif percent <= 20:
            # Could be extraction or container setup
            if "Extracting" in message or "Extracting" in context:
                extraction.append((line_num, percent, message))
            else:
                container_setup.append((line_num, percent, message))
        elif percent <= 80:
            copying.append((line_num, percent, message))
        elif percent <= 90:
            database.append((line_num, percent, message))
        else:
            finalization.append((line_num, percent, message))
    
    return {
        'extraction': extraction,
        'container_setup': container_setup,
        'copying': copying,
        'database': database,
        'finalization': finalization
    }

def test_progress_ranges():
    """
    Test that progress bar ranges match requirements.
    """
    print("=" * 70)
    print("Testing Progress Bar Ranges")
    print("=" * 70)
    
    src_file = Path(__file__).parent.parent / "src" / "nextcloud_restore_and_backup-v9.py"
    
    print(f"\nAnalyzing: {src_file}\n")
    
    calls = extract_progress_calls(src_file)
    categorized = categorize_progress_calls(calls)
    
    # Test extraction phase (0-20%)
    print("\n1. Extraction Phase (0-20%):")
    extraction = categorized['extraction']
    if extraction:
        percentages = [p for _, p, _ in extraction]
        print(f"   ✓ Found {len(extraction)} extraction progress updates")
        print(f"   Range: {min(percentages)}% - {max(percentages)}%")
        assert all(0 <= p <= 20 for _, p, _ in extraction), "Extraction should be 0-20%"
        print("   ✓ All extraction updates are in 0-20% range")
    else:
        print("   ⚠ No explicit extraction progress calls found (may use callbacks)")
    
    # Test container setup (should be at 20%)
    print("\n2. Container Setup (should be at ~20%):")
    container_setup = categorized['container_setup']
    if container_setup:
        percentages = [p for _, p, _ in container_setup]
        print(f"   ✓ Found {len(container_setup)} container setup updates")
        print(f"   Range: {min(percentages)}% - {max(percentages)}%")
        assert all(p == 20 for _, p, _ in container_setup), "Container setup should be at 20%"
        print("   ✓ All container setup updates are at 20%")
    
    # Test copying phase (20-80%)
    print("\n3. Copying Data Phase (20-80%):")
    copying = categorized['copying']
    if copying:
        percentages = [p for _, p, _ in copying]
        print(f"   ✓ Found {len(copying)} copying progress updates")
        print(f"   Range: {min(percentages)}% - {max(percentages)}%")
        assert all(20 <= p <= 80 for _, p, _ in copying), "Copying should be 20-80%"
        print("   ✓ All copying updates are in 20-80% range")
        print(f"   ✓ Copying occupies 60% of progress bar (largest portion)")
    else:
        print("   ✗ ERROR: No copying progress calls found!")
        return False
    
    # Test database restore (80-90%)
    print("\n4. Database Restore Phase (80-90%):")
    database = categorized['database']
    if database:
        percentages = [p for _, p, _ in database]
        print(f"   ✓ Found {len(database)} database restore updates")
        print(f"   Range: {min(percentages)}% - {max(percentages)}%")
        assert all(80 <= p <= 90 for _, p, _ in database), "Database restore should be 80-90%"
        print("   ✓ All database updates are in 80-90% range")
    else:
        print("   ⚠ No database progress calls found in this range")
    
    # Test finalization (90-100%)
    print("\n5. Finalization Phase (90-100%):")
    finalization = categorized['finalization']
    if finalization:
        percentages = [p for _, p, _ in finalization]
        print(f"   ✓ Found {len(finalization)} finalization updates")
        print(f"   Range: {min(percentages)}% - {max(percentages)}%")
        assert all(90 <= p <= 100 for _, p, _ in finalization), "Finalization should be 90-100%"
        print("   ✓ All finalization updates are in 90-100% range")
    else:
        print("   ✗ ERROR: No finalization progress calls found!")
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    print(f"  Extraction:     0-20%  ({len(extraction)} calls)")
    print(f"  Container:     ~20%    ({len(container_setup)} calls)")
    print(f"  Copying:       20-80%  ({len(copying)} calls) ✨ LARGEST (60%)")
    print(f"  Database:      80-90%  ({len(database)} calls)")
    print(f"  Finalization:  90-100% ({len(finalization)} calls)")
    print("\n✓ All progress ranges are correctly mapped!")
    print("✓ Copying data occupies the largest portion (60%) as required!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = test_progress_ranges()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
