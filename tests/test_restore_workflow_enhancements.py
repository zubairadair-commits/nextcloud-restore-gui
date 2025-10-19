#!/usr/bin/env python3
"""
Test suite for beginner-friendly restore workflow enhancements.
This tests the new features:
- One-click restore with automated Docker operations
- Post-restore "Open Nextcloud" functionality
- Enhanced error handling with actionable suggestions
- Default path suggestions
- Docker detection and installation prompts
- Automated YAML generation
"""

import sys
import os
from pathlib import Path

# Add the script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_file = os.path.join(os.path.dirname(script_dir), 'src', 'nextcloud_restore_and_backup-v9.py')

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import webbrowser
        import subprocess
        print("  ✓ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_syntax():
    """Test Python syntax is valid"""
    print("\nTesting Python syntax...")
    import py_compile
    try:
        py_compile.compile(src_file, doraise=True)
        print("  ✓ Syntax check passed")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ✗ Syntax error: {e}")
        return False

def test_restore_completion_dialog_exists():
    """Test that show_restore_completion_dialog method exists"""
    print("\nTesting show_restore_completion_dialog method...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        if 'def show_restore_completion_dialog(self, container_name, port):' in content:
            print("  ✓ show_restore_completion_dialog method found")
            return True
        else:
            print("  ✗ show_restore_completion_dialog method not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_restore_error_dialog_exists():
    """Test that show_restore_error_dialog method exists"""
    print("\nTesting show_restore_error_dialog method...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        if 'def show_restore_error_dialog(self, error, traceback_str):' in content:
            print("  ✓ show_restore_error_dialog method found")
            return True
        else:
            print("  ✗ show_restore_error_dialog method not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_error_suggestions_method():
    """Test that get_error_suggestions method exists"""
    print("\nTesting get_error_suggestions method...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        if 'def get_error_suggestions(self, error_msg):' in content:
            print("  ✓ get_error_suggestions method found")
            # Check for suggestion categories
            categories = [
                'docker',
                'password',
                'database',
                'permission',
                'container',
                'port'
            ]
            all_found = True
            for category in categories:
                if f'"{category}"' in content.lower() or f"'{category}'" in content.lower():
                    print(f"    ✓ Found {category} error handling")
                else:
                    print(f"    ✗ Missing {category} error handling")
                    all_found = False
            return all_found
        else:
            print("  ✗ get_error_suggestions method not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_open_nextcloud_method():
    """Test that open_nextcloud_in_browser method exists"""
    print("\nTesting open_nextcloud_in_browser method...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        if 'def open_nextcloud_in_browser(self, port):' in content:
            print("  ✓ open_nextcloud_in_browser method found")
            if 'webbrowser.open' in content:
                print("    ✓ Uses webbrowser module")
                return True
            else:
                print("    ✗ Does not use webbrowser module")
                return False
        else:
            print("  ✗ open_nextcloud_in_browser method not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_enhanced_docker_detection():
    """Test enhanced Docker detection in start_restore"""
    print("\nTesting enhanced Docker detection...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Look for enhanced detection
        if "def start_restore(self):" in content:
            print("  ✓ start_restore method found")
            # Check for Docker installation check
            if "is_tool_installed('docker')" in content:
                print("    ✓ Checks if Docker is installed")
            else:
                print("    ✗ Does not check if Docker is installed")
                return False
            
            # Check for installation prompt
            if "prompt_install_docker_link" in content:
                print("    ✓ Prompts to install Docker if missing")
            else:
                print("    ✗ Does not prompt to install Docker")
                return False
            
            return True
        else:
            print("  ✗ start_restore method not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_automated_process_messaging():
    """Test that automated process information is displayed"""
    print("\nTesting automated process messaging...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Check for information about automated process
        info_messages = [
            "Automated Restore Process",
            "automatically",
            "No manual Docker commands",
            "Quick Restore Mode"
        ]
        
        all_found = True
        for msg in info_messages:
            if msg in content:
                print(f"  ✓ Found message: '{msg}'")
            else:
                print(f"  ✗ Missing message: '{msg}'")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_default_path_suggestions():
    """Test that default path suggestions are shown"""
    print("\nTesting default path suggestions...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Check for default path hints
        if "Default backup location" in content or "Documents/NextcloudBackups" in content:
            print("  ✓ Default path suggestions found")
            return True
        else:
            print("  ✗ Default path suggestions not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_tooltip_integration():
    """Test that tooltips are used for user guidance"""
    print("\nTesting tooltip integration...")
    try:
        with open(src_file, 'r') as f:
            content = f.read()
        
        # Check for ToolTip usage in restore completion dialog
        if 'ToolTip(' in content and 'open_nextcloud_in_browser' in content:
            print("  ✓ Tooltips integrated in new features")
            return True
        else:
            print("  ✗ Tooltips not properly integrated")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def run_all_tests():
    """Run all test functions"""
    print("=" * 60)
    print("Running Restore Workflow Enhancement Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_syntax,
        test_restore_completion_dialog_exists,
        test_restore_error_dialog_exists,
        test_error_suggestions_method,
        test_open_nextcloud_method,
        test_enhanced_docker_detection,
        test_automated_process_messaging,
        test_default_path_suggestions,
        test_tooltip_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
