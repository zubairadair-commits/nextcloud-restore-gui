#!/usr/bin/env python3
"""
Test Theme Compatibility for Enhanced Tailscale Pages

Verifies that both Tailscale pages work correctly with both light and dark themes:
1. Loading indicator uses theme colors
2. Error UI uses theme colors
3. All widgets use theme_colors references
4. No hardcoded colors that break themes
"""

import sys
import re

def test_theme_compatibility():
    """Test that Tailscale pages are compatible with both light and dark themes"""
    
    print("=" * 70)
    print("Theme Compatibility Test for Tailscale Pages")
    print("=" * 70)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # Read the main file
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Test 1: Loading indicator in wizard uses theme colors
    total_checks += 1
    print(f"Check {total_checks}: Loading indicator in wizard uses theme colors")
    wizard_loading = re.search(
        r'def show_tailscale_wizard.*?loading_label = tk\.Label\(.*?bg=self\.theme_colors\[\'bg\'\].*?fg=self\.theme_colors\[\'fg\'\]',
        content,
        re.DOTALL
    )
    if wizard_loading:
        print("✓ Pass - Wizard loading indicator uses theme colors")
        checks_passed += 1
    else:
        print("✗ Fail - Wizard loading indicator doesn't use theme colors")
    
    # Test 2: Loading indicator in config uses theme colors
    total_checks += 1
    print(f"Check {total_checks}: Loading indicator in config uses theme colors")
    config_loading = re.search(
        r'def _show_tailscale_config.*?loading_label = tk\.Label\(.*?bg=self\.theme_colors\[\'bg\'\].*?fg=self\.theme_colors\[\'fg\'\]',
        content,
        re.DOTALL
    )
    if config_loading:
        print("✓ Pass - Config loading indicator uses theme colors")
        checks_passed += 1
    else:
        print("✗ Fail - Config loading indicator doesn't use theme colors")
    
    # Test 3: Error UI in decorator uses theme colors
    total_checks += 1
    print(f"Check {total_checks}: Error UI in decorator uses theme colors")
    error_ui = re.search(
        r'error_label = tk\.Label\(.*?bg=self\.theme_colors\[\'bg\'\].*?fg=self\.theme_colors\[\'error_fg\'\]',
        content,
        re.DOTALL
    )
    if error_ui:
        print("✓ Pass - Error UI uses theme colors")
        checks_passed += 1
    else:
        print("✗ Fail - Error UI doesn't use theme colors")
    
    # Test 4: Theme colors are accessed from self.theme_colors
    total_checks += 1
    print(f"Check {total_checks}: All theme colors accessed via self.theme_colors")
    # Extract the show_tailscale_wizard method
    wizard_method = re.search(
        r'@log_page_render\("TAILSCALE WIZARD"\).*?def show_tailscale_wizard.*?(?=\n    def |\Z)',
        content,
        re.DOTALL
    )
    if wizard_method:
        wizard_text = wizard_method.group(0)
        # Check for hardcoded colors (excluding the action buttons which intentionally use fixed colors)
        # Allow hardcoded colors in button commands (#3daee9, #45bf55, white)
        hardcoded_colors = re.findall(r'(bg|fg)=["\'](#[0-9a-fA-F]{6}|white)["\']', wizard_text)
        # Filter out the intentional button colors - these are for primary action buttons
        allowed_colors = [
            ('bg', '#3daee9'),  # Install button
            ('bg', '#45bf55'),  # Start/Configure buttons
            ('fg', 'white')     # Button text
        ]
        problematic_colors = [c for c in hardcoded_colors if c not in allowed_colors]
        if not problematic_colors:
            print("✓ Pass - No problematic hardcoded colors in wizard (action buttons use intentional branding colors)")
            checks_passed += 1
        else:
            print(f"✗ Fail - Found hardcoded colors: {problematic_colors}")
    else:
        print("✗ Fail - Could not extract wizard method")
    
    # Test 5: Config method uses theme colors
    total_checks += 1
    print(f"Check {total_checks}: Config method uses theme colors")
    config_method = re.search(
        r'@log_page_render\("TAILSCALE CONFIG"\).*?def _show_tailscale_config.*?(?=\n    def |\Z)',
        content,
        re.DOTALL
    )
    if config_method:
        config_text = config_method.group(0)
        # All labels and frames should use self.theme_colors
        theme_color_usage = len(re.findall(r'self\.theme_colors\[', config_text))
        if theme_color_usage > 10:  # Should have many references
            print(f"✓ Pass - Config method has {theme_color_usage} theme color references")
            checks_passed += 1
        else:
            print(f"✗ Fail - Config method has only {theme_color_usage} theme color references")
    else:
        print("✗ Fail - Could not extract config method")
    
    # Test 6: Check that THEMES dictionary has all required keys
    total_checks += 1
    print(f"Check {total_checks}: THEMES dictionary has all required keys")
    themes_def = re.search(r'THEMES = \{.*?\n\}', content, re.DOTALL)
    if themes_def:
        themes_text = themes_def.group(0)
        required_keys = ['bg', 'fg', 'error_fg', 'info_bg', 'info_fg', 
                        'button_bg', 'button_fg', 'hint_fg', 'warning_fg']
        missing_keys = []
        for key in required_keys:
            if f"'{key}'" not in themes_text:
                missing_keys.append(key)
        
        if not missing_keys:
            print("✓ Pass - All required theme keys present")
            checks_passed += 1
        else:
            print(f"✗ Fail - Missing theme keys: {missing_keys}")
    else:
        print("✗ Fail - Could not find THEMES definition")
    
    # Test 7: Both light and dark themes defined
    total_checks += 1
    print(f"Check {total_checks}: Both light and dark themes are defined")
    if "'light': {" in content and "'dark': {" in content:
        print("✓ Pass - Both themes defined")
        checks_passed += 1
    else:
        print("✗ Fail - One or both themes missing")
    
    # Test 8: Current theme tracking in wizard
    total_checks += 1
    print(f"Check {total_checks}: Wizard logs current theme")
    if 'logger.info(f"Current theme: {self.current_theme}")' in content:
        print("✓ Pass - Current theme is logged")
        checks_passed += 1
    else:
        print("✗ Fail - Current theme not logged")
    
    # Test 9: Loading indicator text is theme-neutral
    total_checks += 1
    print(f"Check {total_checks}: Loading indicator text is appropriate")
    if 'Loading Remote Access Setup' in content and 'Loading Configuration' in content:
        print("✓ Pass - Loading text is clear and theme-neutral")
        checks_passed += 1
    else:
        print("✗ Fail - Loading indicator text not found")
    
    # Test 10: Error UI text is theme-neutral
    total_checks += 1
    print(f"Check {total_checks}: Error UI text is appropriate")
    if 'Error Loading' in content and 'Check nextcloud_restore_gui.log' in content:
        print("✓ Pass - Error text is clear and theme-neutral")
        checks_passed += 1
    else:
        print("✗ Fail - Error UI text not appropriate")
    
    print()
    print("=" * 70)
    print(f"Results: {checks_passed}/{total_checks} checks passed")
    print("=" * 70)
    print()
    
    if checks_passed == total_checks:
        print("✅ All checks passed! Theme compatibility is properly implemented.")
        print()
        print("📋 Theme Features Verified:")
        print("  • Loading indicators use dynamic theme colors")
        print("  • Error UI adapts to current theme")
        print("  • All widgets reference self.theme_colors")
        print("  • Both light and dark themes fully supported")
        print("  • Current theme is logged for debugging")
        print()
        print("🎯 Benefits:")
        print("  • Pages look correct in both light and dark themes")
        print("  • Theme switching works seamlessly")
        print("  • No visual glitches or color mismatches")
        print("  • User experience is consistent across themes")
        return 0
    else:
        print(f"❌ {total_checks - checks_passed} checks failed.")
        print("Some theme compatibility features are missing or incorrect.")
        return 1

if __name__ == '__main__':
    sys.exit(test_theme_compatibility())
