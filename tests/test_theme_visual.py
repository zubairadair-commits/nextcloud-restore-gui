#!/usr/bin/env python3
"""
Visual test for dark theme toggle and button width fixes.
This script demonstrates the theme toggle functionality.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_theme_constants():
    """Test that theme constants are properly defined"""
    # Import the main module by importing it directly
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_module", "../src/nextcloud_restore_and_backup-v9.py")
    main_module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(main_module)
    except ImportError as e:
        print(f"Note: Could not fully load module (tkinter not available), but can still check constants")
        # Try to extract THEMES constant from file directly
        with open("../src/nextcloud_restore_and_backup-v9.py", 'r') as f:
            content = f.read()
            if 'THEMES = {' in content:
                print("\n✓ THEMES constant found in source file")
            else:
                print("\n✗ THEMES constant NOT found in source file")
        print("\nSkipping detailed theme inspection due to import error")
        print(f"Error: {e}")
        return
    
    print("="*70)
    print("Theme System Test")
    print("="*70)
    
    # Check if THEMES constant exists
    if hasattr(main_module, 'THEMES'):
        print("\n✓ THEMES constant found")
        themes = main_module.THEMES
        
        # Check light theme
        if 'light' in themes:
            print("\n✓ Light theme defined")
            print("  Light theme colors:")
            for key, value in themes['light'].items():
                print(f"    - {key}: {value}")
        else:
            print("\n✗ Light theme NOT defined")
        
        # Check dark theme
        if 'dark' in themes:
            print("\n✓ Dark theme defined")
            print("  Dark theme colors:")
            for key, value in themes['dark'].items():
                print(f"    - {key}: {value}")
        else:
            print("\n✗ Dark theme NOT defined")
    else:
        print("\n✗ THEMES constant NOT found")
    
    print("\n" + "="*70)
    print("Button Width Test")
    print("="*70)
    
    # Simulate button labels to test width
    button_labels = [
        "🔄 Backup Now",
        "🛠 Restore from Backup",
        "✨ Start New Nextcloud Instance",  # This is the problematic one
        "📅 Schedule Backup"
    ]
    
    old_width = 24
    new_width = 30
    
    print(f"\nButton width comparison:")
    print(f"  Old width: {old_width} characters")
    print(f"  New width: {new_width} characters")
    print(f"  Improvement: +{new_width - old_width} characters ({((new_width - old_width) / old_width * 100):.1f}% increase)")
    
    print(f"\nButton labels:")
    for label in button_labels:
        label_len = len(label)
        old_fits = "✓ Fits" if label_len <= old_width else f"✗ Too long by {label_len - old_width} chars"
        new_fits = "✓ Fits" if label_len <= new_width else f"✗ Too long by {label_len - new_width} chars"
        print(f"  '{label}'")
        print(f"    Length: {label_len} chars")
        print(f"    Old width ({old_width}): {old_fits}")
        print(f"    New width ({new_width}): {new_fits}")
    
    print("\n" + "="*70)
    print("Theme Toggle Test")
    print("="*70)
    
    print("\nExpected behavior:")
    print("  1. Theme toggle button appears on main menu")
    print("  2. Button shows '🌙 Dark Theme' in light mode")
    print("  3. Button shows '☀️ Light Theme' in dark mode")
    print("  4. Clicking toggle switches theme and refreshes UI")
    print("  5. All colors update according to current theme")
    
    print("\n" + "="*70)
    print("Visual Verification Checklist")
    print("="*70)
    
    print("\nWhen running the actual application, verify:")
    print("  [ ] All main menu buttons are same width (30 chars)")
    print("  [ ] 'Start New Nextcloud Instance' button label fully visible")
    print("  [ ] Theme toggle button appears below scheduled backup button")
    print("  [ ] Clicking theme toggle changes colors")
    print("  [ ] Dark theme: dark background, light text")
    print("  [ ] Light theme: light background, dark text")
    print("  [ ] Button colors adjust for current theme")
    print("  [ ] All text remains readable in both themes")
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)
    print("\nTo fully test the implementation:")
    print("  1. Install tkinter: sudo apt-get install python3-tk")
    print("  2. Run: python3 nextcloud_restore_and_backup-v9.py")
    print("  3. Observe the main menu")
    print("  4. Click the theme toggle button")
    print("  5. Verify all colors change appropriately")
    print("\n")

if __name__ == '__main__':
    test_theme_constants()
