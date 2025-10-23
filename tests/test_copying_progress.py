#!/usr/bin/env python3
"""
Test suite for live copying progress bar functionality.
Validates that copying progress is reported file-by-file with proper callbacks.
"""

import sys
import os
import tempfile
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

def test_copy_folder_function_exists():
    """Test that copy_folder_to_container_with_progress function exists"""
    print("\nTesting copy_folder_to_container_with_progress function...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check function signature
        if 'def copy_folder_to_container_with_progress(self, local_path, container_name, container_path,' in content:
            print("  ✓ Found copy_folder_to_container_with_progress function")
            return True
        else:
            print("  ✗ copy_folder_to_container_with_progress function not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_copy_progress_callback_parameter():
    """Test that the function accepts progress_callback parameter"""
    print("\nTesting progress_callback parameter...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check for progress_callback in function signature
        if 'progress_callback=None' in content and 'copy_folder_to_container_with_progress' in content:
            print("  ✓ progress_callback parameter found")
            return True
        else:
            print("  ✗ progress_callback parameter not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_file_by_file_copying():
    """Test that files are copied one by one"""
    print("\nTesting file-by-file copying implementation...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check for file iteration
        if 'for filepath, rel_path in all_files:' in content:
            print("  ✓ File iteration loop found")
        else:
            print("  ✗ File iteration loop not found")
            return False
        
        # Check for docker cp command for individual files
        if 'docker cp' in content and 'container_dest' in content:
            print("  ✓ Individual file copy command found")
        else:
            print("  ✗ Individual file copy command not found")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_progress_callback_invocation():
    """Test that progress callback is called during copying"""
    print("\nTesting progress callback invocation...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check for callback invocation in copy function
        if 'if progress_callback' in content and 'files_copied' in content:
            print("  ✓ Progress callback invocation found")
        else:
            print("  ✗ Progress callback invocation not found")
            return False
        
        # Check for file count tracking
        if 'files_copied += 1' in content or 'files_copied = files_copied' in content:
            print("  ✓ File count tracking found")
        else:
            print("  ✗ File count tracking not found")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_thread_safe_ui_updates():
    """Test that UI updates use thread-safe methods"""
    print("\nTesting thread-safe UI updates...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check for self.after() usage in copy progress callback
        if 'self.after(0, update_ui)' in content and 'copy_progress_callback' in content:
            print("  ✓ Thread-safe UI updates using self.after() found")
            return True
        else:
            print("  ✗ Thread-safe UI updates not properly implemented")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_copy_phase_uses_new_function():
    """Test that the restore process uses the new copy function"""
    print("\nTesting integration with restore process...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check that new function is called instead of simple docker cp
        if 'self.copy_folder_to_container_with_progress' in content:
            print("  ✓ New copy function is used in restore process")
        else:
            print("  ✗ New copy function not integrated")
            return False
        
        # Check for copy progress callback definition in restore thread
        if 'def copy_progress_callback(files_copied, total_files, current_file, percent, elapsed):' in content:
            print("  ✓ Copy progress callback defined in restore thread")
            return True
        else:
            print("  ✗ Copy progress callback not properly defined")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_progress_ranges():
    """Test that progress ranges are correctly defined"""
    print("\nTesting progress ranges...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check for 30-60% range comments or usage
        if '30-60% range' in content or 'progress_start=folder_start_progress' in content:
            print("  ✓ Progress range configuration found")
            return True
        else:
            print("  ✗ Progress range not properly configured")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_file_display_in_ui():
    """Test that current file is displayed in UI"""
    print("\nTesting current file display...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check for current file display in process label
        if 'process_label.config(text=f"Copying: {file_display}")' in content or \
           'Copying: {file_display}' in content:
            print("  ✓ Current file display found")
            return True
        else:
            print("  ✗ Current file display not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("Testing Copying Progress Bar Implementation")
    print("="*70)
    
    tests = [
        test_syntax,
        test_copy_folder_function_exists,
        test_copy_progress_callback_parameter,
        test_file_by_file_copying,
        test_progress_callback_invocation,
        test_thread_safe_ui_updates,
        test_copy_phase_uses_new_function,
        test_progress_ranges,
        test_file_display_in_ui,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*70)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
