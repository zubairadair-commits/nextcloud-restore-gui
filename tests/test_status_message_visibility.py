#!/usr/bin/env python3
"""
Test script to verify status message visibility improvements.
Ensures that status messages use the new progress_fg color instead of blue,
and that the font is bold for better prominence.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_themes_have_progress_fg():
    """Test that THEMES dictionary includes progress_fg color for both themes."""
    # Import after path modification
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "nextcloud_restore", 
        os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    )
    module = importlib.util.module_from_spec(spec)
    
    # Get the THEMES constant by reading the file
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        content = f.read()
    
    # Check that progress_fg is defined in both themes
    assert "'progress_fg':" in content or '"progress_fg":' in content, "progress_fg color not found in THEMES"
    
    # Check that it appears at least twice (once for light, once for dark theme)
    progress_fg_count = content.count("'progress_fg':") + content.count('"progress_fg":')
    assert progress_fg_count >= 2, f"progress_fg should be defined in both themes, found {progress_fg_count} times"
    
    print("✓ THEMES dictionary includes progress_fg color for both light and dark themes")

def test_no_blue_status_messages():
    """Test that no status messages use the old blue color."""
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        content = f.read()
    
    # Check for status-related lines with blue color
    lines = content.split('\n')
    blue_status_lines = []
    
    for i, line in enumerate(lines):
        # Look for config() calls with fg="blue" that are related to status messages
        if 'config(' in line and 'fg="blue"' in line:
            # Get some context
            context_start = max(0, i - 3)
            context_end = min(len(lines), i + 3)
            context = '\n'.join(f"Line {j+1}: {lines[j]}" for j in range(context_start, context_end))
            blue_status_lines.append(f"Found blue color at line {i+1}:\n{context}\n")
    
    if blue_status_lines:
        print("✗ Found status messages still using blue color:")
        for line in blue_status_lines:
            print(line)
        assert False, "Status messages should not use blue color"
    else:
        print("✓ No status messages use the old blue color")

def test_bold_font_for_status():
    """Test that status messages use bold font."""
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        content = f.read()
    
    # Check for status messages with progress_fg
    lines = content.split('\n')
    status_messages_with_bold = 0
    
    for i, line in enumerate(lines):
        # Look for lines with progress_fg
        if "progress_fg" in line:
            # Check if font is set to bold in the same config call or nearby
            # Get more lines of context to handle multi-line config calls
            context_start = max(0, i - 2)
            context_end = min(len(lines), i + 5)
            context = '\n'.join(lines[context_start:context_end])
            
            if '"bold"' in context or "'bold'" in context:
                status_messages_with_bold += 1
    
    assert status_messages_with_bold >= 3, f"Expected at least 3 status messages with bold font, found {status_messages_with_bold}"
    print(f"✓ Found {status_messages_with_bold} status messages using bold font")

def test_theme_colors_in_light_theme():
    """Test that light theme has appropriate progress_fg color."""
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        content = f.read()
    
    # Find the light theme section and check progress_fg color
    light_theme_start = content.find("'light': {")
    if light_theme_start == -1:
        light_theme_start = content.find('"light": {')
    
    assert light_theme_start != -1, "Could not find light theme definition"
    
    # Get the light theme section (up to the next theme)
    light_theme_end = content.find("'dark': {", light_theme_start)
    if light_theme_end == -1:
        light_theme_end = content.find('"dark": {', light_theme_start)
    
    light_theme_section = content[light_theme_start:light_theme_end]
    
    # Check that progress_fg is defined
    assert "progress_fg" in light_theme_section, "progress_fg not found in light theme"
    
    # Check that it's not using the old blue color
    assert "#0000ff" not in light_theme_section.lower() or "progress_fg" not in light_theme_section, \
        "Light theme should not use bright blue (#0000ff) for progress_fg"
    
    print("✓ Light theme has appropriate progress_fg color")

def test_theme_colors_in_dark_theme():
    """Test that dark theme has appropriate progress_fg color."""
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
        content = f.read()
    
    # Find the dark theme section
    dark_theme_start = content.find("'dark': {")
    if dark_theme_start == -1:
        dark_theme_start = content.find('"dark": {')
    
    assert dark_theme_start != -1, "Could not find dark theme definition"
    
    # Get the dark theme section (up to the closing brace)
    dark_theme_section = content[dark_theme_start:dark_theme_start + 1000]
    
    # Check that progress_fg is defined
    assert "progress_fg" in dark_theme_section, "progress_fg not found in dark theme"
    
    print("✓ Dark theme has appropriate progress_fg color")

if __name__ == "__main__":
    print("Testing status message visibility improvements...\n")
    
    try:
        test_themes_have_progress_fg()
        test_no_blue_status_messages()
        test_bold_font_for_status()
        test_theme_colors_in_light_theme()
        test_theme_colors_in_dark_theme()
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60)
        
    except AssertionError as e:
        print("\n" + "="*60)
        print(f"✗ Test failed: {e}")
        print("="*60)
        sys.exit(1)
    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ Unexpected error: {e}")
        print("="*60)
        sys.exit(1)
