#!/usr/bin/env python3
"""
Test Enhanced Debug Logging for Tailscale Pages

Verifies:
1. Granular logging throughout widget creation
2. Minimal loading indicator at page start
3. Enhanced decorator with fallback UI
4. Logging checkpoints at key widget creation steps
"""

import sys
import re

def test_enhanced_logging():
    """Test that enhanced debug logging is properly implemented"""
    
    print("=" * 70)
    print("Enhanced Debug Logging Test for Tailscale Pages")
    print("=" * 70)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # Read the main file
    with open('../src/nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Test 1: Enhanced decorator with minimal error UI
    total_checks += 1
    print(f"Check {total_checks}: Enhanced decorator has minimal error UI fallback")
    if 'Last resort: create minimal error UI' in content:
        if 'Error Loading' in content and 'error_label = tk.Label' in content:
            print("✓ Pass - Decorator creates minimal error UI as last resort")
            checks_passed += 1
        else:
            print("✗ Fail - Minimal error UI not properly implemented")
    else:
        print("✗ Fail - Last resort error UI not found")
    
    # Test 2: Loading indicator in show_tailscale_wizard
    total_checks += 1
    print(f"Check {total_checks}: show_tailscale_wizard has loading indicator")
    wizard_match = re.search(
        r'def show_tailscale_wizard.*?loading_label = tk\.Label.*?Loading Remote Access Setup',
        content,
        re.DOTALL
    )
    if wizard_match:
        print("✓ Pass - Loading indicator found in show_tailscale_wizard")
        checks_passed += 1
    else:
        print("✗ Fail - Loading indicator not found")
    
    # Test 3: Loading indicator in _show_tailscale_config
    total_checks += 1
    print(f"Check {total_checks}: _show_tailscale_config has loading indicator")
    config_match = re.search(
        r'def _show_tailscale_config.*?loading_label = tk\.Label.*?Loading Configuration',
        content,
        re.DOTALL
    )
    if config_match:
        print("✓ Pass - Loading indicator found in _show_tailscale_config")
        checks_passed += 1
    else:
        print("✗ Fail - Loading indicator not found")
    
    # Test 4: Container frame logging in wizard
    total_checks += 1
    print(f"Check {total_checks}: Container frame creation is logged in wizard")
    if 'logger.info("TAILSCALE WIZARD: Creating container frame")' in content:
        print("✓ Pass - Container frame creation logged")
        checks_passed += 1
    else:
        print("✗ Fail - Container frame creation not logged")
    
    # Test 5: Canvas creation logging in wizard
    total_checks += 1
    print(f"Check {total_checks}: Canvas creation is logged in wizard")
    if 'logger.info("TAILSCALE WIZARD: Creating scrollable canvas and frame")' in content:
        print("✓ Pass - Canvas creation logged")
        checks_passed += 1
    else:
        print("✗ Fail - Canvas creation not logged")
    
    # Test 6: Content frame logging in wizard
    total_checks += 1
    print(f"Check {total_checks}: Content frame creation is logged in wizard")
    if 'logger.info("TAILSCALE WIZARD: Creating content frame")' in content:
        print("✓ Pass - Content frame creation logged")
        checks_passed += 1
    else:
        print("✗ Fail - Content frame creation not logged")
    
    # Test 7: Title labels logging in wizard
    total_checks += 1
    print(f"Check {total_checks}: Title labels creation is logged in wizard")
    if 'logger.info("TAILSCALE WIZARD: Creating title labels")' in content:
        print("✓ Pass - Title labels creation logged")
        checks_passed += 1
    else:
        print("✗ Fail - Title labels creation not logged")
    
    # Test 8: Info box logging in wizard
    total_checks += 1
    print(f"Check {total_checks}: Info box creation is logged in wizard")
    if 'logger.info("TAILSCALE WIZARD: Creating info box")' in content:
        print("✓ Pass - Info box creation logged")
        checks_passed += 1
    else:
        print("✗ Fail - Info box creation not logged")
    
    # Test 9: Status check logging in wizard
    total_checks += 1
    print(f"Check {total_checks}: Tailscale status check is logged in wizard")
    if 'logger.info("TAILSCALE WIZARD: Checking Tailscale installation status")' in content:
        if 'logger.info(f"TAILSCALE WIZARD: Status - Installed: {ts_installed}, Running: {ts_running}")' in content:
            print("✓ Pass - Status check and results logged")
            checks_passed += 1
        else:
            print("✗ Fail - Status results not logged")
    else:
        print("✗ Fail - Status check not logged")
    
    # Test 10: Action buttons logging in wizard
    total_checks += 1
    print(f"Check {total_checks}: Action buttons creation is logged in wizard")
    if 'logger.info("TAILSCALE WIZARD: Creating action buttons")' in content:
        print("✓ Pass - Action buttons creation logged")
        checks_passed += 1
    else:
        print("✗ Fail - Action buttons creation not logged")
    
    # Test 11: All widgets complete logging in wizard
    total_checks += 1
    print(f"Check {total_checks}: Widget completion is logged in wizard")
    if 'logger.info("TAILSCALE WIZARD: All widgets created successfully")' in content:
        print("✓ Pass - Widget completion logged")
        checks_passed += 1
    else:
        print("✗ Fail - Widget completion not logged")
    
    # Test 12: Container frame logging in config
    total_checks += 1
    print(f"Check {total_checks}: Container frame creation is logged in config")
    if 'logger.info("TAILSCALE CONFIG: Creating container frame")' in content:
        print("✓ Pass - Container frame creation logged in config")
        checks_passed += 1
    else:
        print("✗ Fail - Container frame creation not logged in config")
    
    # Test 13: Canvas creation logging in config
    total_checks += 1
    print(f"Check {total_checks}: Canvas creation is logged in config")
    if 'logger.info("TAILSCALE CONFIG: Creating scrollable canvas and frame")' in content:
        print("✓ Pass - Canvas creation logged in config")
        checks_passed += 1
    else:
        print("✗ Fail - Canvas creation not logged in config")
    
    # Test 14: Tailscale info retrieval logging in config
    total_checks += 1
    print(f"Check {total_checks}: Tailscale info retrieval is logged in config")
    if 'logger.info("TAILSCALE CONFIG: Retrieving Tailscale network information")' in content:
        if 'logger.info(f"TAILSCALE CONFIG: Retrieved - IP: {ts_ip}, Hostname: {ts_hostname}")' in content:
            print("✓ Pass - Tailscale info retrieval and results logged")
            checks_passed += 1
        else:
            print("✗ Fail - Tailscale info results not logged")
    else:
        print("✗ Fail - Tailscale info retrieval not logged")
    
    # Test 15: All widgets complete logging in config
    total_checks += 1
    print(f"Check {total_checks}: Widget completion is logged in config")
    if 'logger.info("TAILSCALE CONFIG: All widgets created successfully")' in content:
        print("✓ Pass - Widget completion logged in config")
        checks_passed += 1
    else:
        print("✗ Fail - Widget completion not logged in config")
    
    # Test 16: Canvas packing confirmation in wizard
    total_checks += 1
    print(f"Check {total_checks}: Canvas packing is confirmed in wizard")
    if 'logger.info("TAILSCALE WIZARD: Canvas and scrollbar packed successfully")' in content:
        print("✓ Pass - Canvas packing confirmed")
        checks_passed += 1
    else:
        print("✗ Fail - Canvas packing not confirmed")
    
    # Test 17: Canvas packing confirmation in config
    total_checks += 1
    print(f"Check {total_checks}: Canvas packing is confirmed in config")
    if 'logger.info("TAILSCALE CONFIG: Canvas and scrollbar packed successfully")' in content:
        print("✓ Pass - Canvas packing confirmed in config")
        checks_passed += 1
    else:
        print("✗ Fail - Canvas packing not confirmed in config")
    
    # Test 18: Minimal loading indicator is destroyed before content
    total_checks += 1
    print(f"Check {total_checks}: Loading indicator is properly cleaned up")
    loading_cleanup_wizard = re.search(
        r'loading_label\.pack\(expand=True\).*?loading_label\.destroy\(\)',
        content,
        re.DOTALL
    )
    if loading_cleanup_wizard:
        print("✓ Pass - Loading indicator is destroyed before content creation")
        checks_passed += 1
    else:
        print("✗ Fail - Loading indicator cleanup not found")
    
    print()
    print("=" * 70)
    print(f"Results: {checks_passed}/{total_checks} checks passed")
    print("=" * 70)
    print()
    
    if checks_passed == total_checks:
        print("✅ All checks passed! Enhanced debug logging is properly implemented.")
        print()
        print("📋 What was enhanced:")
        print("  • Decorator creates minimal error UI as last resort fallback")
        print("  • Loading indicator shows immediately on page load")
        print("  • Granular logging at every major widget creation step")
        print("  • Canvas and scrollbar packing is confirmed")
        print("  • Tailscale status and info retrieval is logged")
        print("  • Widget completion is explicitly logged")
        print()
        print("🎯 Benefits:")
        print("  • Page never appears blank (loading indicator or error UI)")
        print("  • Detailed diagnostic trail for troubleshooting")
        print("  • Easy to identify exactly where failures occur")
        print("  • Users always see feedback during page load")
        return 0
    else:
        print(f"❌ {total_checks - checks_passed} checks failed.")
        print("Some enhanced logging features are missing or incomplete.")
        return 1

if __name__ == '__main__':
    sys.exit(test_enhanced_logging())
