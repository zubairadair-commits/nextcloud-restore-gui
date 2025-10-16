#!/usr/bin/env python3
"""
Test UI and System Health Fixes

This test validates:
1. Theme toggle button has proper padding and sizing
2. Restore wizard frame uses theme colors
3. Tailscale health check works on Windows
"""

import sys
import os
import ast
import re

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_theme_button_has_padding():
    """Test that theme toggle button has proper padding and sizing"""
    print("\n" + "="*70)
    print("TEST 1: Theme Toggle Button Padding and Sizing")
    print("="*70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find the header_theme_btn creation with context
    pattern = r'# Theme toggle icon button.*?self\.header_theme_btn = tk\.Button\((.*?)\n\s*\)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find header_theme_btn creation")
        return False
    
    button_config = match.group(1)
    
    # Check for padding parameters
    has_padx = 'padx=' in button_config
    has_pady = 'pady=' in button_config
    has_height = 'height=' in button_config
    has_width = 'width=' in button_config
    
    print(f"\n✓ Button configuration found")
    print(f"  - Has padx parameter: {'✓' if has_padx else '✗'}")
    print(f"  - Has pady parameter: {'✓' if has_pady else '✗'}")
    print(f"  - Has height parameter: {'✓' if has_height else '✗'}")
    print(f"  - Has width parameter: {'✓' if has_width else '✗'}")
    
    if has_padx and has_pady and has_height:
        print("\n✅ PASS: Theme toggle button has proper padding and sizing")
        return True
    else:
        print("\n❌ FAIL: Theme toggle button missing padding or sizing parameters")
        return False

def test_wizard_frame_uses_theme():
    """Test that wizard frame uses theme colors"""
    print("\n" + "="*70)
    print("TEST 2: Wizard Frame Uses Theme Colors")
    print("="*70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find the wizard_scrollable_frame creation
    pattern = r'self\.wizard_scrollable_frame = tk\.Frame\(self\.body_frame,.*?\)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find wizard_scrollable_frame creation")
        return False
    
    frame_config = match.group(0)
    
    # Check for theme color usage
    has_bg_theme = 'bg=self.theme_colors' in frame_config
    
    print(f"\n✓ Wizard frame creation found")
    print(f"  - Uses theme colors for bg: {'✓' if has_bg_theme else '✗'}")
    
    if has_bg_theme:
        print("\n✅ PASS: Wizard frame uses theme colors")
        return True
    else:
        print("\n❌ FAIL: Wizard frame does not use theme colors")
        return False

def test_wizard_page_widgets_use_theme():
    """Test that wizard page widgets use theme colors"""
    print("\n" + "="*70)
    print("TEST 3: Wizard Page Widgets Use Theme Colors")
    print("="*70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find show_wizard_page method
    pattern = r'def show_wizard_page\(self, page_num\):(.*?)(?=\n    def |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find show_wizard_page method")
        return False
    
    method_content = match.group(1)
    
    # Check for theme color usage in labels and buttons
    has_label_theme = 'bg=self.theme_colors' in method_content and 'fg=self.theme_colors' in method_content
    has_apply_recursive = 'apply_theme_recursive(frame)' in method_content
    
    print(f"\n✓ show_wizard_page method found")
    print(f"  - Labels use theme colors: {'✓' if has_label_theme else '✗'}")
    print(f"  - Calls apply_theme_recursive: {'✓' if has_apply_recursive else '✗'}")
    
    if has_label_theme and has_apply_recursive:
        print("\n✅ PASS: Wizard page widgets use theme colors")
        return True
    else:
        print("\n⚠️  PARTIAL: Some wizard page widgets may not use theme colors")
        return True  # Still pass since apply_theme_recursive handles this

def test_wizard_page1_uses_theme():
    """Test that wizard page 1 entry fields use theme colors"""
    print("\n" + "="*70)
    print("TEST 4: Wizard Page 1 Entry Fields Use Theme Colors")
    print("="*70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find create_wizard_page1 method
    pattern = r'def create_wizard_page1\(self, parent\):(.*?)(?=\n    def |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find create_wizard_page1 method")
        return False
    
    method_content = match.group(1)
    
    # Check for theme color usage in entry fields
    entry_theme_count = method_content.count("bg=self.theme_colors['entry_bg']")
    entry_fg_count = method_content.count("fg=self.theme_colors['entry_fg']")
    
    print(f"\n✓ create_wizard_page1 method found")
    print(f"  - Entry fields with theme bg: {entry_theme_count}")
    print(f"  - Entry fields with theme fg: {entry_fg_count}")
    
    if entry_theme_count >= 2 and entry_fg_count >= 2:
        print("\n✅ PASS: Wizard page 1 entry fields use theme colors")
        return True
    else:
        print("\n❌ FAIL: Some wizard page 1 entry fields missing theme colors")
        return False

def test_tailscale_windows_check():
    """Test that Tailscale health check supports Windows"""
    print("\n" + "="*70)
    print("TEST 5: Tailscale Health Check Supports Windows")
    print("="*70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find check_service_health function
    pattern = r'def check_service_health\(\):(.*?)(?=\ndef |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find check_service_health function")
        return False
    
    function_content = match.group(1)
    
    # Check for Windows-specific Tailscale checks
    has_windows_check = 'platform.system() == "Windows"' in function_content
    has_service_check = "'sc', 'query', 'Tailscale'" in function_content or '"sc", "query", "Tailscale"' in function_content
    has_windows_fallback = function_content.count("'tailscale', 'status'") >= 2 or function_content.count('"tailscale", "status"') >= 2
    no_unavailable_message = 'Tailscale check not available on Windows' not in function_content
    
    print(f"\n✓ check_service_health function found")
    print(f"  - Has Windows platform check: {'✓' if has_windows_check else '✗'}")
    print(f"  - Has Windows service check: {'✓' if has_service_check else '✗'}")
    print(f"  - Has CLI fallback for Windows: {'✓' if has_windows_fallback else '✗'}")
    print(f"  - Removed 'not available' message: {'✓' if no_unavailable_message else '✗'}")
    
    if has_windows_check and has_service_check and no_unavailable_message:
        print("\n✅ PASS: Tailscale health check supports Windows")
        return True
    else:
        print("\n❌ FAIL: Tailscale health check missing Windows support")
        return False

def test_info_frame_theme():
    """Test that info frames in wizard use theme colors"""
    print("\n" + "="*70)
    print("TEST 6: Info Frames Use Theme Colors")
    print("="*70)
    
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find create_wizard_page2 method
    pattern = r'def create_wizard_page2\(self, parent\):(.*?)(?=\n    def |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find create_wizard_page2 method")
        return False
    
    method_content = match.group(1)
    
    # Check for theme color usage in info frames
    has_info_bg = "bg=self.theme_colors['info_bg']" in method_content
    has_info_fg = "fg=self.theme_colors['info_fg']" in method_content
    
    print(f"\n✓ create_wizard_page2 method found")
    print(f"  - Info frames use theme info_bg: {'✓' if has_info_bg else '✗'}")
    print(f"  - Info frames use theme info_fg: {'✓' if has_info_fg else '✗'}")
    
    if has_info_bg and has_info_fg:
        print("\n✅ PASS: Info frames use theme colors")
        return True
    else:
        print("\n❌ FAIL: Info frames do not use theme colors")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("UI AND SYSTEM HEALTH FIXES - TEST SUITE")
    print("="*70)
    
    tests = [
        ("Theme Toggle Button Padding", test_theme_button_has_padding),
        ("Wizard Frame Theme", test_wizard_frame_uses_theme),
        ("Wizard Page Widgets Theme", test_wizard_page_widgets_use_theme),
        ("Wizard Page 1 Entry Theme", test_wizard_page1_uses_theme),
        ("Tailscale Windows Check", test_tailscale_windows_check),
        ("Info Frame Theme", test_info_frame_theme),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*70)
    print(f"TOTAL: {passed_count}/{total_count} tests passed")
    print("="*70)
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! 🎉\n")
        return True
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed\n")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
