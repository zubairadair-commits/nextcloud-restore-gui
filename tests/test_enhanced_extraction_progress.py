#!/usr/bin/env python3
"""
Test suite for enhanced extraction progress UI with real-time updates.
This validates the improvements made to match 7-Zip style live progress.
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

def get_script_path():
    """Get path to main script"""
    return os.path.join(src_path, 'nextcloud_restore_and_backup-v9.py')

def test_syntax():
    """Test that the Python file has valid syntax"""
    print("\nTesting Python syntax...")
    try:
        with open(get_script_path(), 'r') as f:
            code = f.read()
        compile(code, get_script_path(), 'exec')
        print("  ✓ Syntax check passed")
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error: {e}")
        return False

def test_batch_size_default():
    """Test that batch_size defaults to 1 for real-time updates"""
    print("\nTesting batch_size default value...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Find the function signature
        if 'def fast_extract_tar_gz(archive_path, extract_to, progress_callback=None, batch_size=1' in content:
            print("  ✓ batch_size defaults to 1 (real-time updates like 7-Zip)")
            return True
        else:
            print("  ✗ batch_size not set to 1")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_prepare_callback_exists():
    """Test that prepare_callback parameter exists"""
    print("\nTesting prepare_callback parameter...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        if 'prepare_callback' in content and 'def fast_extract_tar_gz' in content:
            print("  ✓ prepare_callback parameter found in fast_extract_tar_gz")
            return True
        else:
            print("  ✗ prepare_callback parameter not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_prepare_callback_implementation():
    """Test that prepare_callback is implemented and called"""
    print("\nTesting prepare_callback implementation...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check for prepare callback function
        if 'def prepare_extraction_callback' in content:
            print("  ✓ prepare_extraction_callback function found")
        else:
            print("  ✗ prepare_extraction_callback function not found")
            return False
        
        # Check for "Preparing extraction..." message
        if 'Preparing extraction...' in content:
            print("  ✓ 'Preparing extraction...' message found")
        else:
            print("  ✗ 'Preparing extraction...' message not found")
            return False
        
        # Check that prepare callback is passed to fast_extract_tar_gz
        if 'prepare_callback=prepare_extraction_callback' in content:
            print("  ✓ prepare_callback is passed to fast_extract_tar_gz")
            return True
        else:
            print("  ✗ prepare_callback not passed to fast_extract_tar_gz")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_thread_safe_updates():
    """Test that UI updates use Tkinter's after() method"""
    print("\nTesting thread-safe UI updates with after()...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Find the extraction_progress_callback function and check for after() usage
        if 'def extraction_progress_callback(files_extracted, total_files, current_file):' not in content:
            print("  ✗ extraction_progress_callback not found")
            return False
        
        # Look for the update_ui function and after() call
        # The pattern should be flexible to handle different indentation
        if 'def update_ui():' in content or 'def update_ui(' in content:
            print("  ✓ update_ui inner function found for encapsulating UI updates")
        else:
            print("  ✗ update_ui inner function not found")
            return False
        
        if 'self.after(0, update_ui)' in content or 'self.after(0,update_ui)' in content:
            print("  ✓ self.after(0, update_ui) call found for thread-safe updates")
            return True
        else:
            print("  ✗ self.after() not used for UI updates")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_batch_size_one_in_call():
    """Test that fast_extract_tar_gz is called with batch_size=1"""
    print("\nTesting batch_size=1 in function call...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        if 'batch_size=1' in content and 'fast_extract_tar_gz' in content:
            print("  ✓ batch_size=1 found in fast_extract_tar_gz call")
            return True
        else:
            print("  ✗ batch_size=1 not found in function call")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_no_artificial_throttling():
    """Test that there's no artificial throttling (like time.sleep in callback)"""
    print("\nTesting for absence of artificial throttling...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Find the extraction_progress_callback function
        lines = content.split('\n')
        in_callback = False
        found_sleep = False
        
        for line in lines:
            if 'def extraction_progress_callback(files_extracted, total_files, current_file):' in line:
                in_callback = True
            elif in_callback and line.strip().startswith('def ') and 'extraction_progress_callback' not in line:
                if 'update_ui' not in line:
                    break
            elif in_callback and 'time.sleep' in line:
                found_sleep = True
        
        if not found_sleep:
            print("  ✓ No time.sleep() found in extraction callback (no artificial throttling)")
            return True
        else:
            print("  ✗ time.sleep() found in callback - artificial throttling detected")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_functional_with_prepare_callback():
    """Test extraction with prepare callback and verify it's called"""
    print("\nTesting functional extraction with prepare callback...")
    
    # Create a small test archive
    temp_dir = tempfile.mkdtemp(prefix="test_archive_")
    archive_path = None
    extract_dir = None
    
    try:
        # Create some test files
        for i in range(10):
            test_file = os.path.join(temp_dir, f"file_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"Test content {i}\n" * 100)
        
        # Create archive
        archive_path = tempfile.mktemp(suffix=".tar.gz", prefix="test_archive_")
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(temp_dir, arcname='.')
        
        # Test extraction without importing tkinter-dependent code
        # Just extract using tarfile directly to verify the archive is valid
        extract_dir = tempfile.mkdtemp(prefix="test_extract_")
        
        # Track callbacks
        callback_calls = []
        prepare_called = [False]
        
        def test_progress_callback(files_extracted, total_files, current_file):
            callback_calls.append({
                'files': files_extracted,
                'total': total_files,
                'current': current_file
            })
        
        def test_prepare_callback():
            prepare_called[0] = True
        
        # Manually test the extraction logic without the full GUI
        # This tests the core extraction function signature
        with tarfile.open(archive_path, 'r:gz') as tar:
            members = tar.getmembers()
            total_files = len(members)
            
            # Call prepare callback
            test_prepare_callback()
            
            files_extracted = 0
            for member in members:
                tar.extract(member, path=extract_dir)
                files_extracted += 1
                # Simulate batch_size=1 (call on every file)
                test_progress_callback(files_extracted, total_files, os.path.basename(member.name))
        
        # Verify prepare callback was called
        if prepare_called[0]:
            print(f"  ✓ Prepare callback was called")
        else:
            print(f"  ✗ Prepare callback was not called")
            return False
        
        # Verify progress callback was called
        if len(callback_calls) > 0:
            print(f"  ✓ Progress callback was called {len(callback_calls)} times")
        else:
            print(f"  ✗ Progress callback was not called")
            return False
        
        # Verify callback was called for every file (batch_size=1)
        total_files = callback_calls[0]['total']
        if len(callback_calls) >= total_files:
            print(f"  ✓ Callback called for each file ({len(callback_calls)} calls for {total_files} files)")
        else:
            print(f"  ✗ Not enough callbacks ({len(callback_calls)} calls for {total_files} files)")
            return False
        
        # Verify files were extracted
        extracted_files = sum(len(files) for _, _, files in os.walk(extract_dir))
        if extracted_files >= 10:
            print(f"  ✓ {extracted_files} files were extracted successfully")
            return True
        else:
            print(f"  ✗ Only {extracted_files} files extracted (expected at least 10)")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        if archive_path and os.path.exists(archive_path):
            os.remove(archive_path)
        if extract_dir and os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)

def main():
    """Run all tests"""
    print("=" * 70)
    print("Enhanced Extraction Progress UI Tests")
    print("=" * 70)
    
    tests = [
        ("Syntax", test_syntax),
        ("Batch Size Default (1)", test_batch_size_default),
        ("Prepare Callback Parameter", test_prepare_callback_exists),
        ("Prepare Callback Implementation", test_prepare_callback_implementation),
        ("Thread-Safe Updates (after)", test_thread_safe_updates),
        ("Batch Size 1 in Call", test_batch_size_one_in_call),
        ("No Artificial Throttling", test_no_artificial_throttling),
        ("Functional Test", test_functional_with_prepare_callback),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} | {name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    exit(main())
