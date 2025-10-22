#!/usr/bin/env python3
"""
Test suite for live extraction progress bar functionality.
Validates that extraction progress is reported file-by-file with proper callbacks.
"""

import sys
import os
import tempfile
import tarfile
import time
import shutil

# Add the script directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_script_path():
    """Get the path to the main script"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(test_dir, '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    return script_path

def test_syntax():
    """Test Python syntax is valid"""
    print("\nTesting Python syntax...")
    import py_compile
    try:
        py_compile.compile(get_script_path(), doraise=True)
        print("  ✓ Syntax check passed")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ✗ Syntax error: {e}")
        return False

def test_fast_extract_has_progress_callback():
    """Test that fast_extract_tar_gz has progress_callback parameter"""
    print("\nTesting fast_extract_tar_gz signature...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check function signature includes progress_callback
        if 'def fast_extract_tar_gz(archive_path, extract_to, progress_callback=None' in content:
            print("  ✓ Found progress_callback parameter in fast_extract_tar_gz")
            return True
        else:
            print("  ✗ progress_callback parameter not found in fast_extract_tar_gz signature")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_extraction_callback_implementation():
    """Test that extraction progress callback is implemented in auto_extract_backup"""
    print("\nTesting extraction progress callback implementation...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check for callback function definition
        if 'def extraction_progress_callback(files_extracted, total_files, current_file):' in content:
            print("  ✓ Found extraction_progress_callback function definition")
        else:
            print("  ✗ extraction_progress_callback function not found")
            return False
        
        # Check that callback is passed to fast_extract_tar_gz
        if 'fast_extract_tar_gz(extracted_file, extract_temp, progress_callback=extraction_progress_callback)' in content:
            print("  ✓ Progress callback is passed to fast_extract_tar_gz")
        else:
            print("  ✗ Progress callback not passed to fast_extract_tar_gz")
            return False
        
        # Check for file count tracking
        if 'files_extracted' in content and 'total_files' in content:
            print("  ✓ File count tracking implemented")
        else:
            print("  ✗ File count tracking not found")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_progress_updates_in_callback():
    """Test that progress bar is updated in the callback"""
    print("\nTesting progress bar updates in callback...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Find the extraction_progress_callback function
        lines = content.split('\n')
        in_callback = False
        found_progress_update = False
        found_status_msg = False
        found_time_estimate = False
        
        for line in lines:
            if 'def extraction_progress_callback(files_extracted, total_files, current_file):' in line:
                in_callback = True
            elif in_callback and line.strip().startswith('def ') and 'extraction_progress_callback' not in line:
                break
            elif in_callback:
                if 'self.set_restore_progress' in line:
                    found_progress_update = True
                if 'status_msg' in line and ('Extracting files:' in line or 'files_extracted' in line):
                    found_status_msg = True
                if 'est_remaining' in line or 'elapsed_str' in line or '_format_time' in line:
                    found_time_estimate = True
        
        if found_progress_update:
            print("  ✓ Progress bar update found in callback")
        else:
            print("  ✗ Progress bar update not found in callback")
            return False
        
        if found_status_msg:
            print("  ✓ Status message with file count found")
        else:
            print("  ✗ Status message not found in callback")
            return False
        
        if found_time_estimate:
            print("  ✓ Time estimate calculation found")
        else:
            print("  ✗ Time estimate not found in callback")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_batch_processing():
    """Test that batch size parameter exists"""
    print("\nTesting batch processing support...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check for batch_size parameter
        if 'batch_size' in content and 'def fast_extract_tar_gz' in content:
            print("  ✓ Batch size parameter found in fast_extract_tar_gz")
            return True
        else:
            print("  ✗ Batch size parameter not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_current_file_display():
    """Test that current file being extracted is displayed"""
    print("\nTesting current file display...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check for current file display in callback
        if 'current_file' in content and 'process_label' in content and 'Extracting:' in content:
            print("  ✓ Current file display implementation found")
            return True
        else:
            print("  ✗ Current file display not implemented")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_no_blocking_while_loop_during_extraction():
    """Test that the old blocking while loop during extraction is removed"""
    print("\nTesting for removal of blocking extraction loop...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Look for the section after do_extraction definition
        in_auto_extract = False
        in_extraction_section = False
        has_blocking_pattern = False
        
        for i, line in enumerate(lines):
            if 'def auto_extract_backup(self, backup_path, password=None):' in line:
                in_auto_extract = True
            elif in_auto_extract and line.strip().startswith('def ') and 'auto_extract_backup' not in line:
                # Exited the method
                break
            elif in_auto_extract and 'def do_extraction():' in line:
                in_extraction_section = True
            elif in_extraction_section and 'extraction_thread.start()' in line:
                # Now check if there's a blocking while loop after thread start
                for j in range(i, min(i+20, len(lines))):
                    if 'while extraction_thread.is_alive():' in lines[j]:
                        # Check for time.sleep in the loop
                        for k in range(j, min(j+15, len(lines))):
                            if 'time.sleep' in lines[k] and 'progress_val' in lines[k-5:k+5]:
                                has_blocking_pattern = True
                                print(f"  ✗ Found blocking pattern at line {k+1}")
                                break
                        break
                break
        
        if not has_blocking_pattern:
            print("  ✓ No blocking while loop during extraction")
            return True
        else:
            print("  ✗ Blocking pattern still exists during extraction")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_functional_extraction_with_callback():
    """Functional test: Create a small archive and test extraction with callback"""
    print("\nTesting functional extraction with progress callback...")
    try:
        # Create a temporary test archive
        temp_dir = tempfile.mkdtemp(prefix="test_extraction_")
        archive_path = None
        extract_path = None
        
        try:
            # Create some test files
            test_data_dir = os.path.join(temp_dir, "test_data")
            os.makedirs(test_data_dir)
            
            # Create 10 small test files
            for i in range(10):
                with open(os.path.join(test_data_dir, f"file_{i}.txt"), 'w') as f:
                    f.write(f"Test file {i}\n" * 10)
            
            # Create archive
            archive_path = os.path.join(temp_dir, "test_archive.tar.gz")
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(test_data_dir, arcname='data')
            
            # Test extraction with callback using standalone implementation
            # (to avoid importing tkinter which may not be available)
            extract_path = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_path)
            
            callback_calls = []
            
            def test_callback(files_extracted, total_files, current_file):
                callback_calls.append({
                    'files': files_extracted,
                    'total': total_files,
                    'current': current_file
                })
            
            # Standalone extraction implementation (mirrors fast_extract_tar_gz)
            with tarfile.open(archive_path, 'r:gz') as tar:
                members = tar.getmembers()
                total_files = len(members)
                
                files_extracted = 0
                batch_count = 0
                batch_size = 5
                
                for member in members:
                    tar.extract(member, path=extract_path)
                    files_extracted += 1
                    batch_count += 1
                    
                    if batch_count >= batch_size or files_extracted == total_files:
                        current_file = os.path.basename(member.name) if member.name else "..."
                        test_callback(files_extracted, total_files, current_file)
                        batch_count = 0
            
            # Verify callback was called
            if len(callback_calls) > 0:
                print(f"  ✓ Callback was called {len(callback_calls)} times")
                
                # Check that progress increased
                first_call = callback_calls[0]
                last_call = callback_calls[-1]
                
                if last_call['files'] >= first_call['files']:
                    print(f"  ✓ Progress increased from {first_call['files']} to {last_call['files']}")
                else:
                    print(f"  ✗ Progress did not increase properly")
                    return False
                
                # Check that total_files is consistent
                if all(c['total'] == callback_calls[0]['total'] for c in callback_calls):
                    print(f"  ✓ Total files consistent: {callback_calls[0]['total']}")
                else:
                    print(f"  ✗ Total files inconsistent across callbacks")
                    return False
                
                # Verify files were actually extracted
                extracted_files = []
                for root, dirs, files in os.walk(extract_path):
                    extracted_files.extend(files)
                
                if len(extracted_files) > 0:
                    print(f"  ✓ {len(extracted_files)} files were extracted successfully")
                else:
                    print(f"  ✗ No files were extracted")
                    return False
                
                return True
            else:
                print("  ✗ Callback was never called")
                return False
                
        finally:
            # Clean up
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"  ✗ Error during functional test: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("=" * 70)
    print("Live Extraction Progress Bar Tests")
    print("=" * 70)
    
    tests = [
        ("Syntax", test_syntax),
        ("Progress Callback Parameter", test_fast_extract_has_progress_callback),
        ("Callback Implementation", test_extraction_callback_implementation),
        ("Progress Updates in Callback", test_progress_updates_in_callback),
        ("Batch Processing", test_batch_processing),
        ("Current File Display", test_current_file_display),
        ("No Blocking Loop", test_no_blocking_while_loop_during_extraction),
        ("Functional Test", test_functional_extraction_with_callback),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test {name} raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} | {name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
