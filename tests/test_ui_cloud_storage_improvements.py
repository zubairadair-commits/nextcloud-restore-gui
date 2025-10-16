#!/usr/bin/env python3
"""
Test script to verify UI improvements for cloud storage and backup history.

Tests:
1. Last Run Status section is removed
2. Cloud Storage Setup Guide dialog functionality
3. Info icon is properly added and functional
4. Backup History list still works correctly
"""

import sys
import os
import re

# Add the repository path to system path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_code_structure():
    """Test that code changes are properly implemented."""
    print("=" * 70)
    print("TESTING CODE STRUCTURE")
    print("=" * 70)
    print()
    
    main_file = '../src/nextcloud_restore_and_backup-v9.py'
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Last Run Status section removed
    tests_total += 1
    print("Test 1: Verify 'Last Run Status' section is removed...")
    if '📊 Last Run Status' not in content:
        print("  ✅ PASSED: 'Last Run Status' section removed")
        tests_passed += 1
    else:
        print("  ❌ FAILED: 'Last Run Status' section still exists")
    
    # Test 2: Static Cloud Storage Setup Guide removed
    tests_total += 1
    print("\nTest 2: Verify static Cloud Storage Setup Guide is removed...")
    pattern = r'help_frame = tk\.Frame\(config_frame.*relief="groove"'
    if not re.search(pattern, content):
        print("  ✅ PASSED: Static guide frame removed")
        tests_passed += 1
    else:
        print("  ❌ FAILED: Static guide frame still exists")
    
    # Test 3: _show_cloud_storage_guide method exists
    tests_total += 1
    print("\nTest 3: Verify _show_cloud_storage_guide method exists...")
    if 'def _show_cloud_storage_guide(self):' in content:
        print("  ✅ PASSED: Method exists")
        tests_passed += 1
    else:
        print("  ❌ FAILED: Method not found")
    
    # Test 4: Method creates Toplevel dialog
    tests_total += 1
    print("\nTest 4: Verify method creates Toplevel dialog...")
    method_start = content.find('def _show_cloud_storage_guide(self):')
    if method_start != -1:
        method_section = content[method_start:method_start+3000]
        if 'dialog = tk.Toplevel(self)' in method_section:
            print("  ✅ PASSED: Creates Toplevel dialog")
            tests_passed += 1
        else:
            print("  ❌ FAILED: Does not create Toplevel")
    else:
        print("  ❌ FAILED: Method not found")
    
    # Test 5: Dialog is modal
    tests_total += 1
    print("\nTest 5: Verify dialog is modal...")
    if method_start != -1:
        method_section = content[method_start:method_start+3000]
        if 'dialog.grab_set()' in method_section:
            print("  ✅ PASSED: Dialog is modal")
            tests_passed += 1
        else:
            print("  ❌ FAILED: Dialog not modal")
    else:
        tests_passed += 0  # Skip if method not found
    
    # Test 6: Dialog contains setup instructions
    tests_total += 1
    print("\nTest 6: Verify dialog contains setup instructions...")
    if method_start != -1:
        method_section = content[method_start:method_start+3000]
        has_onedrive = 'OneDrive:' in method_section
        has_google = 'Google Drive:' in method_section
        has_dropbox = 'Dropbox:' in method_section
        if has_onedrive and has_google and has_dropbox:
            print("  ✅ PASSED: Contains OneDrive, Google Drive, and Dropbox instructions")
            tests_passed += 1
        else:
            print(f"  ❌ FAILED: Missing instructions (OneDrive:{has_onedrive}, Google:{has_google}, Dropbox:{has_dropbox})")
    else:
        print("  ❌ FAILED: Method not found")
    
    # Test 7: Info icon added to cloud folders section
    tests_total += 1
    print("\nTest 7: Verify info icon added to cloud folders section...")
    if 'Click for Cloud Storage Setup Guide' in content:
        print("  ✅ PASSED: Info icon tooltip found")
        tests_passed += 1
    else:
        print("  ❌ FAILED: Info icon tooltip not found")
    
    # Test 8: Info icon triggers dialog
    tests_total += 1
    print("\nTest 8: Verify info icon triggers dialog...")
    if 'info_icon.bind("<Button-1>", lambda e: self._show_cloud_storage_guide())' in content:
        print("  ✅ PASSED: Info icon bound to dialog method")
        tests_passed += 1
    else:
        print("  ❌ FAILED: Info icon not properly bound")
    
    # Test 9: Backup history method still exists
    tests_total += 1
    print("\nTest 9: Verify backup history functionality intact...")
    if 'def show_backup_history(self):' in content:
        print("  ✅ PASSED: show_backup_history method exists")
        tests_passed += 1
    else:
        print("  ❌ FAILED: show_backup_history method not found")
    
    # Test 10: Backup history calls get_all_backups
    tests_total += 1
    print("\nTest 10: Verify backup history displays all backups...")
    history_start = content.find('def show_backup_history(self):')
    if history_start != -1:
        history_section = content[history_start:history_start+3000]
        if 'self.backup_history.get_all_backups()' in history_section or 'backup_history.get_all_backups()' in history_section:
            print("  ✅ PASSED: Calls get_all_backups()")
            tests_passed += 1
        else:
            print("  ❌ FAILED: Does not call get_all_backups()")
    else:
        print("  ❌ FAILED: show_backup_history not found")
    
    print("\n" + "=" * 70)
    print(f"TESTS PASSED: {tests_passed}/{tests_total}")
    print("=" * 70)
    
    return tests_passed == tests_total

def test_dialog_functionality():
    """Test the dialog functionality by analyzing code structure."""
    print("\n" + "=" * 70)
    print("TESTING DIALOG FUNCTIONALITY")
    print("=" * 70)
    print()
    
    try:
        # Read the code
        method_code = open('../src/nextcloud_restore_and_backup-v9.py').read()
        method_start = method_code.find('def _show_cloud_storage_guide(self):')
        
        if method_start == -1:
            print("Test 1: Dialog method exists")
            print("  ❌ FAILED: Method not found")
            return False
        
        print("Test 1: Dialog method exists and is callable")
        print("  ✅ PASSED: Method can be located")
        
        # Extract method content
        method_end = method_code.find('\n    def ', method_start + 1)
        if method_end == -1:
            method_end = method_start + 3000  # Just get a chunk
        method_content = method_code[method_start:method_end]
        
        # Test 2: Dialog structure
        print("\nTest 2: Dialog creates proper window structure")
        has_toplevel = 'tk.Toplevel' in method_content
        has_title = 'dialog.title' in method_content
        has_geometry = 'dialog.geometry' in method_content
        
        if has_toplevel and has_title and has_geometry:
            print("  ✅ PASSED: Creates Toplevel with title and geometry")
        else:
            print(f"  ❌ FAILED: Missing structure (Toplevel:{has_toplevel}, title:{has_title}, geometry:{has_geometry})")
            return False
        
        # Test 3: Dialog is modal
        print("\nTest 3: Dialog is modal")
        if 'grab_set()' in method_content:
            print("  ✅ PASSED: Dialog grabs focus (modal)")
        else:
            print("  ❌ FAILED: Dialog not modal")
            return False
        
        # Test 4: Dialog is centered
        print("\nTest 4: Dialog is centered on screen")
        if 'winfo_screenwidth' in method_content and 'winfo_screenheight' in method_content:
            print("  ✅ PASSED: Dialog centers on screen")
        else:
            print("  ❌ FAILED: Dialog not centered")
            return False
        
        # Test 5: Has close button
        print("\nTest 5: Dialog has close button")
        if 'Close' in method_content and 'dialog.destroy' in method_content:
            print("  ✅ PASSED: Has close button")
        else:
            print("  ❌ FAILED: Missing close button")
            return False
        
        print("\n" + "=" * 70)
        print("DIALOG FUNCTIONALITY TESTS PASSED")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during dialog test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Integration test for the changes."""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST")
    print("=" * 70)
    print()
    
    main_file = '../src/nextcloud_restore_and_backup-v9.py'
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    print("Test 1: Verify scheduled backup page structure...")
    schedule_method_start = content.find('def show_schedule_backup(self):')
    if schedule_method_start != -1:
        print("  ✅ PASSED: show_schedule_backup method exists")
        
        # Check that Last Run Status is not in this method
        schedule_method_end = content.find('\n    def ', schedule_method_start + 1)
        if schedule_method_end == -1:
            schedule_method_end = len(content)
        schedule_section = content[schedule_method_start:schedule_method_end]
        
        if '📊 Last Run Status' not in schedule_section:
            print("  ✅ PASSED: Last Run Status not in schedule method")
        else:
            print("  ❌ FAILED: Last Run Status still in schedule method")
            return False
    else:
        print("  ❌ FAILED: show_schedule_backup not found")
        return False
    
    print("\nTest 2: Verify cloud storage section has info icon...")
    if 'Detected Cloud Sync Folders' in schedule_section:
        print("  ✅ PASSED: Cloud folders section exists")
        
        # Check for info icon
        cloud_section_start = schedule_section.find('Detected Cloud Sync Folders')
        cloud_section = schedule_section[cloud_section_start:cloud_section_start+1000]
        
        if 'info_icon' in cloud_section and '_show_cloud_storage_guide' in cloud_section:
            print("  ✅ PASSED: Info icon added and triggers guide")
        else:
            print("  ❌ FAILED: Info icon not properly configured")
            return False
    else:
        print("  ❌ FAILED: Cloud folders section not found")
        return False
    
    print("\nTest 3: Verify dialog method is accessible...")
    if '_show_cloud_storage_guide' in content:
        print("  ✅ PASSED: Dialog method accessible")
    else:
        print("  ❌ FAILED: Dialog method not accessible")
        return False
    
    print("\n" + "=" * 70)
    print("INTEGRATION TESTS PASSED")
    print("=" * 70)
    return True

def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "UI CLOUD STORAGE IMPROVEMENTS TEST" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    all_passed = True
    
    # Run tests
    try:
        code_passed = test_code_structure()
        dialog_passed = test_dialog_functionality()
        integration_passed = test_integration()
        
        all_passed = code_passed and dialog_passed and integration_passed
        
        print("\n" + "=" * 70)
        print("FINAL RESULTS")
        print("=" * 70)
        print(f"Code Structure Tests:  {'✅ PASSED' if code_passed else '❌ FAILED'}")
        print(f"Dialog Functionality:  {'✅ PASSED' if dialog_passed else '❌ FAILED'}")
        print(f"Integration Tests:     {'✅ PASSED' if integration_passed else '❌ FAILED'}")
        print("=" * 70)
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED! 🎉")
            print("\nChanges successfully implemented:")
            print("  ✓ 'Last Run Status' box removed")
            print("  ✓ Info icon (ℹ️) added to cloud folders section")
            print("  ✓ Cloud Storage Setup Guide now on-demand via dialog")
            print("  ✓ Backup History list functionality preserved")
            print("\nThe UI is cleaner and help is available on-demand!")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED")
            return 1
            
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
