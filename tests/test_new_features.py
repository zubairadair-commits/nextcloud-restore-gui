#!/usr/bin/env python3
"""
Test suite for new features:
- Service Health Checks
- Backup Verification
- Tooltips
- Backup History
- Selective Backup
- Export Functionality
- Responsive Layout
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the script directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import sqlite3
        import json
        from datetime import datetime, timedelta
        from pathlib import Path
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
        py_compile.compile('../src/nextcloud_restore_and_backup-v9.py', doraise=True)
        print("  ✓ Syntax check passed")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ✗ Syntax error: {e}")
        return False

def test_tooltip_class():
    """Test ToolTip class exists and has required methods"""
    print("\nTesting ToolTip class...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        required_methods = [
            'class ToolTip:',
            'def __init__(self, widget, text, delay=',
            'def on_enter(self',
            'def on_leave(self',
            'def show_tooltip(self',
            'def hide_tooltip(self'
        ]
        
        for method in required_methods:
            if method in content:
                print(f"  ✓ Found: {method}")
            else:
                print(f"  ✗ Missing: {method}")
                return False
        
        print("  ✓ ToolTip class structure validated")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_backup_history_manager():
    """Test BackupHistoryManager class"""
    print("\nTesting BackupHistoryManager class...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        required_methods = [
            'class BackupHistoryManager:',
            'def __init__(self, db_path=None)',
            'def _init_database(self)',
            'def add_backup(self',
            'def update_verification(self',
            'def get_all_backups(self',
            'def get_backup_by_id(self'
        ]
        
        for method in required_methods:
            if method in content:
                print(f"  ✓ Found: {method}")
            else:
                print(f"  ✗ Missing: {method}")
                return False
        
        print("  ✓ BackupHistoryManager class structure validated")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_health_check_function():
    """Test service health check function exists"""
    print("\nTesting health check functions...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        required_functions = [
            'def check_service_health():',
            "'nextcloud':",
            "'tailscale':",
            "'docker':",
            "'network':"
        ]
        
        for func in required_functions:
            if func in content:
                print(f"  ✓ Found: {func}")
            else:
                print(f"  ✗ Missing: {func}")
                return False
        
        print("  ✓ Health check function validated")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_backup_verification():
    """Test backup verification function"""
    print("\nTesting backup verification...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        if 'def verify_backup_integrity(backup_path, password=None):' in content:
            print("  ✓ Found verify_backup_integrity function")
        else:
            print("  ✗ Missing verify_backup_integrity function")
            return False
        
        # Check it tests for required components
        checks = [
            'os.path.exists(backup_path)',
            'tarfile.open',
            'has_config',
            'has_data'
        ]
        
        for check in checks:
            if check in content:
                print(f"  ✓ Function checks: {check}")
            else:
                print(f"  ✗ Missing check: {check}")
                return False
        
        print("  ✓ Backup verification function validated")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_ui_methods():
    """Test new UI methods exist"""
    print("\nTesting new UI methods...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        required_methods = [
            'def _add_health_dashboard(self',
            'def _refresh_health_dashboard(self',
            'def _display_health_status(self',
            'def show_backup_history(self',
            'def _create_backup_item(self',
            'def _restore_from_history(self',
            'def _verify_backup_from_history(self',
            'def _export_backup(self',
            'def _show_folder_selection(self',
            'def _show_encryption_dialog(self',
            'def _on_window_resize(self'
        ]
        
        for method in required_methods:
            if method in content:
                print(f"  ✓ Found: {method}")
            else:
                print(f"  ✗ Missing: {method}")
                return False
        
        print("  ✓ All UI methods present")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_tooltips_added():
    """Test that tooltips were added to UI elements"""
    print("\nTesting tooltip integration...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Count tooltip instances
        tooltip_count = content.count('ToolTip(')
        
        if tooltip_count >= 10:
            print(f"  ✓ Found {tooltip_count} tooltip instances (expected >= 10)")
            return True
        else:
            print(f"  ✗ Only found {tooltip_count} tooltip instances (expected >= 10)")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_selective_backup_integration():
    """Test selective backup integration"""
    print("\nTesting selective backup integration...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        checks = [
            'self.selected_backup_folders',
            'folder_vars',
            'tk.Checkbutton',
            'is_critical'
        ]
        
        for check in checks:
            if check in content:
                print(f"  ✓ Found: {check}")
            else:
                print(f"  ✗ Missing: {check}")
                return False
        
        print("  ✓ Selective backup integration validated")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_backup_history_tracking():
    """Test backup history is tracked in backup process"""
    print("\nTesting backup history tracking integration...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        # Check backup process includes history tracking
        if 'self.backup_history.add_backup(' in content:
            print("  ✓ Backup history tracking integrated")
        else:
            print("  ✗ Backup history tracking not found")
            return False
        
        # Check verification is called
        if 'verify_backup_integrity(' in content:
            print("  ✓ Verification function called")
        else:
            print("  ✗ Verification not called")
            return False
        
        # Check verification status is updated
        if 'self.backup_history.update_verification(' in content:
            print("  ✓ Verification status update found")
        else:
            print("  ✗ Verification status update not found")
            return False
        
        print("  ✓ Backup history tracking validated")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_responsive_layout():
    """Test responsive layout features"""
    print("\nTesting responsive layout features...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        checks = [
            'self.bind("<Configure>"',
            'def _on_window_resize(self',
            'minsize(',
            '<MouseWheel>',
            '<Button-4>',  # Linux scroll
            '<Button-5>'   # Linux scroll
        ]
        
        for check in checks:
            if check in content:
                print(f"  ✓ Found: {check}")
            else:
                print(f"  ✗ Missing: {check}")
                return False
        
        print("  ✓ Responsive layout features validated")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_database_schema():
    """Test backup history database schema"""
    print("\nTesting database schema...")
    try:
        with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
            content = f.read()
        
        required_fields = [
            'id INTEGER PRIMARY KEY',
            'backup_path TEXT',
            'timestamp DATETIME',
            'size_bytes INTEGER',
            'encrypted BOOLEAN',
            'database_type TEXT',
            'folders_backed_up TEXT',
            'verification_status TEXT',
            'verification_details TEXT',
            'notes TEXT'
        ]
        
        for field in required_fields:
            if field in content:
                print(f"  ✓ Schema includes: {field}")
            else:
                print(f"  ✗ Schema missing: {field}")
                return False
        
        print("  ✓ Database schema validated")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing New Features Implementation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_syntax,
        test_tooltip_class,
        test_backup_history_manager,
        test_health_check_function,
        test_backup_verification,
        test_ui_methods,
        test_tooltips_added,
        test_selective_backup_integration,
        test_backup_history_tracking,
        test_responsive_layout,
        test_database_schema
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
