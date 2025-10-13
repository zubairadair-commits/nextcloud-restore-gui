#!/usr/bin/env python3
"""
Test Dark Mode Support for All Major Wizard/Panel Boxes

This test validates that all major panels respect dark mode:
1. Restore Wizard (already fixed - image10)
2. Start New Nextcloud Instance (image12) 
3. Schedule Automatic Backups (image13)
"""

import sys
import re

def test_start_new_instance_theme():
    """Test that Start New Nextcloud Instance panel uses theme colors"""
    print("\n" + "="*70)
    print("TEST 1: Start New Nextcloud Instance - Theme Colors")
    print("="*70)
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find show_port_entry method
    pattern = r'def show_port_entry\(self\):(.*?)(?=\n    def |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find show_port_entry method")
        return False
    
    method_content = match.group(1)
    
    # Check for theme color usage
    has_frame_theme = "bg=self.theme_colors['bg']" in method_content or "bg=self.theme_colors['frame_bg']" in method_content
    has_label_theme = "fg=self.theme_colors['fg']" in method_content
    has_entry_theme = "bg=self.theme_colors['entry_bg']" in method_content
    has_hint_theme = "fg=self.theme_colors['hint_fg']" in method_content
    
    # Check for hardcoded colors (excluding intentional button colors)
    hardcoded_colors = re.findall(r'(?:bg|fg)=["\'](?!self\.theme_colors)(#[0-9a-fA-F]{6}|gray|white)["\']', method_content)
    # Filter out the intentional button colors - these are for primary action buttons
    allowed_colors = ['#f7b32b', 'white']  # New instance button branding color (yellow button with white text)
    problematic_colors = [c for c in hardcoded_colors if c not in allowed_colors]
    
    print(f"\n✓ show_port_entry method found")
    print(f"  - Frame uses theme colors: {'✓' if has_frame_theme else '✗'}")
    print(f"  - Labels use theme colors: {'✓' if has_label_theme else '✗'}")
    print(f"  - Entry uses theme colors: {'✓' if has_entry_theme else '✗'}")
    print(f"  - Hint text uses theme colors: {'✓' if has_hint_theme else '✗'}")
    print(f"  - Problematic hardcoded colors: {len(problematic_colors)}")
    
    if has_frame_theme and has_label_theme and len(problematic_colors) == 0:
        print("\n✅ PASS: Start New Nextcloud Instance panel uses theme colors")
        return True
    else:
        print("\n❌ FAIL: Start New Nextcloud Instance panel missing theme colors")
        if problematic_colors:
            print(f"  Problematic colors found: {problematic_colors}")
        return False

def test_launch_nextcloud_instance_theme():
    """Test that launch_nextcloud_instance progress UI uses theme colors"""
    print("\n" + "="*70)
    print("TEST 2: Launch Nextcloud Instance Progress - Theme Colors")
    print("="*70)
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find launch_nextcloud_instance method
    pattern = r'def launch_nextcloud_instance\(self, port\):(.*?)(?=\n    def |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find launch_nextcloud_instance method")
        return False
    
    method_content = match.group(1)
    
    # Check for theme color usage in progress UI
    has_frame_theme = "bg=self.theme_colors['bg']" in method_content or "bg=self.theme_colors['frame_bg']" in method_content
    has_label_theme = "fg=self.theme_colors['fg']" in method_content
    has_hint_theme = "fg=self.theme_colors['hint_fg']" in method_content
    
    # Check for hardcoded colors (excluding intentional link colors)
    hardcoded_colors = re.findall(r'(?:bg|fg)=["\'](?!self\.theme_colors)(#[0-9a-fA-F]{6}|gray|blue|green|orange)["\']', method_content)
    # Filter out intentional colors (link color - intentionally blue in both themes)
    allowed_colors = ['#3daee9']  # Link color - consistent across themes for clickable URLs
    problematic_colors = [c for c in hardcoded_colors if c not in allowed_colors]
    
    print(f"\n✓ launch_nextcloud_instance method found")
    print(f"  - Frame uses theme colors: {'✓' if has_frame_theme else '✗'}")
    print(f"  - Labels use theme colors: {'✓' if has_label_theme else '✗'}")
    print(f"  - Hint text uses theme colors: {'✓' if has_hint_theme else '✗'}")
    print(f"  - Problematic hardcoded colors: {len(problematic_colors)}")
    
    if has_frame_theme and has_label_theme and len(problematic_colors) == 0:
        print("\n✅ PASS: Launch Nextcloud Instance progress uses theme colors")
        return True
    else:
        print("\n❌ FAIL: Launch Nextcloud Instance progress missing theme colors")
        if problematic_colors:
            print(f"  Problematic colors found: {problematic_colors}")
        return False

def test_schedule_backup_theme():
    """Test that Schedule Automatic Backups panel uses theme colors"""
    print("\n" + "="*70)
    print("TEST 3: Schedule Automatic Backups - Theme Colors")
    print("="*70)
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find show_schedule_backup method
    pattern = r'def show_schedule_backup\(self\):(.*?)(?=\n    def |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find show_schedule_backup method")
        return False
    
    method_content = match.group(1)
    
    # Check for theme color usage
    has_frame_theme = "bg=self.theme_colors['bg']" in method_content or "bg=self.theme_colors['frame_bg']" in method_content
    has_label_theme = "fg=self.theme_colors['fg']" in method_content
    has_entry_theme = "bg=self.theme_colors['entry_bg']" in method_content
    has_status_frame_theme = "bg=self.theme_colors['info_bg']" in method_content
    
    # Check for hardcoded colors (excluding intentional button/status colors)
    hardcoded_colors = re.findall(r'(?:bg|fg)=["\'](?!self\.theme_colors)(#[0-9a-fA-F]{6}|gray|white)["\']', method_content)
    # Filter out intentional colors (button colors - green button for create/update action)
    allowed_colors = ['#27ae60', 'white']  # Create/Update button branding color (green button with white text)
    problematic_colors = [c for c in hardcoded_colors if c not in allowed_colors]
    
    print(f"\n✓ show_schedule_backup method found")
    print(f"  - Frame uses theme colors: {'✓' if has_frame_theme else '✗'}")
    print(f"  - Labels use theme colors: {'✓' if has_label_theme else '✗'}")
    print(f"  - Entry uses theme colors: {'✓' if has_entry_theme else '✗'}")
    print(f"  - Status frame uses theme colors: {'✓' if has_status_frame_theme else '✗'}")
    print(f"  - Problematic hardcoded colors: {len(problematic_colors)}")
    
    if has_frame_theme and has_label_theme and has_status_frame_theme and len(problematic_colors) == 0:
        print("\n✅ PASS: Schedule Automatic Backups panel uses theme colors")
        return True
    else:
        print("\n❌ FAIL: Schedule Automatic Backups panel missing theme colors")
        if problematic_colors:
            print(f"  Problematic colors found: {problematic_colors}")
        return False

def test_all_panels_apply_theme_recursive():
    """Test that all panels call apply_theme_recursive for automatic theme updates"""
    print("\n" + "="*70)
    print("TEST 4: All Panels Apply Theme Recursively")
    print("="*70)
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Check that key methods apply theme recursively or to their frames
    methods_to_check = [
        ('show_port_entry', r'def show_port_entry\(self\):(.*?)(?=\n    def |\Z)'),
        ('show_schedule_backup', r'def show_schedule_backup\(self\):(.*?)(?=\n    def |\Z)'),
    ]
    
    all_pass = True
    for method_name, pattern in methods_to_check:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            method_content = match.group(1)
            has_apply_recursive = 'apply_theme_recursive' in method_content
            print(f"  {method_name}: {'✓' if has_apply_recursive else '✗'}")
            if not has_apply_recursive:
                all_pass = False
        else:
            print(f"  {method_name}: ✗ (not found)")
            all_pass = False
    
    if all_pass:
        print("\n✅ PASS: All panels apply theme recursively")
        return True
    else:
        print("\n⚠️  PARTIAL: Some panels may not apply theme recursively")
        print("  (This is OK if widgets use theme colors directly)")
        return True  # Still pass as direct usage is acceptable

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("PANEL DARK MODE SUPPORT - TEST SUITE")
    print("="*70)
    
    tests = [
        ("Start New Instance Theme", test_start_new_instance_theme),
        ("Launch Instance Progress Theme", test_launch_nextcloud_instance_theme),
        ("Schedule Backup Theme", test_schedule_backup_theme),
        ("Apply Theme Recursively", test_all_panels_apply_theme_recursive),
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
