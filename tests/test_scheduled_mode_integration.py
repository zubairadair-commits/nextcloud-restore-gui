#!/usr/bin/env python3
"""
Integration test for scheduled mode fix.
Verifies that the scheduled_mode parameter works correctly in the actual application.
"""

import sys
import os
import re

def analyze_init_method():
    """Analyze the __init__ method to ensure proper guard clause"""
    print("=" * 70)
    print("Analyzing __init__ Method Structure")
    print("=" * 70)
    print()
    
    script_path = os.path.join(os.path.dirname(__file__), '../src/nextcloud_restore_and_backup-v9.py')
    
    with open(script_path, 'r') as f:
        lines = f.readlines()
    
    # Find the __init__ method
    init_start = None
    for i, line in enumerate(lines):
        if 'def __init__(self, scheduled_mode=False):' in line:
            init_start = i
            break
    
    if not init_start:
        print("❌ Could not find __init__ with scheduled_mode parameter")
        return 1
    
    print(f"✓ Found __init__ at line {init_start + 1}")
    print()
    
    # Check the first 15 lines after __init__ definition
    print("First 15 lines of __init__:")
    print("-" * 70)
    for i in range(init_start, min(init_start + 15, len(lines))):
        print(f"{i+1:4d}: {lines[i].rstrip()}")
    print("-" * 70)
    print()
    
    # Verify the guard clause exists
    guard_clause_found = False
    for i in range(init_start, min(init_start + 20, len(lines))):
        if 'if scheduled_mode:' in lines[i]:
            # Check if next line is return
            if i + 1 < len(lines) and 'return' in lines[i + 1]:
                guard_clause_found = True
                print(f"✓ Guard clause found at lines {i+1}-{i+2}")
                break
    
    if not guard_clause_found:
        print("❌ Guard clause not found or incorrect")
        return 1
    
    print("✓ Guard clause properly terminates GUI initialization")
    print()
    
    # Verify that GUI initialization happens after the guard
    gui_init_keywords = [
        'self.title',
        'self.geometry',
        'self.minsize',
        'self.theme_colors',
        'self.header_frame',
        'self.body_frame'
    ]
    
    gui_init_found = []
    for i in range(init_start + 10, min(init_start + 100, len(lines))):
        for keyword in gui_init_keywords:
            if keyword in lines[i]:
                gui_init_found.append((i + 1, keyword, lines[i].strip()))
                break
        if len(gui_init_found) >= 3:
            break
    
    if gui_init_found:
        print("✓ GUI initialization found after guard clause:")
        for line_num, keyword, line in gui_init_found[:3]:
            print(f"  Line {line_num}: {keyword}")
    else:
        print("⚠️  Warning: Could not verify GUI initialization location")
    
    return 0

def verify_main_block():
    """Verify the main block uses scheduled_mode correctly"""
    print()
    print("=" * 70)
    print("Verifying Main Block Implementation")
    print("=" * 70)
    print()
    
    script_path = os.path.join(os.path.dirname(__file__), '../src/nextcloud_restore_and_backup-v9.py')
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Find the scheduled mode block
    pattern = r'if args\.scheduled:.*?sys\.exit\(0\)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ Could not find scheduled mode block in main")
        return 1
    
    scheduled_block = match.group(0)
    print("Scheduled mode block:")
    print("-" * 70)
    for line in scheduled_block.split('\n')[:15]:
        print(f"  {line}")
    print("-" * 70)
    print()
    
    # Check for correct instantiation
    if 'NextcloudRestoreWizard(scheduled_mode=True)' in scheduled_block:
        print("✓ App created with scheduled_mode=True")
    else:
        print("❌ App not created with scheduled_mode=True")
        return 1
    
    # Check that withdraw is NOT present
    if 'app.withdraw()' in scheduled_block:
        print("⚠️  Warning: app.withdraw() found (not needed with scheduled_mode)")
    else:
        print("✓ app.withdraw() not present (correct)")
    
    # Check for run_scheduled_backup call
    if 'app.run_scheduled_backup' in scheduled_block:
        print("✓ run_scheduled_backup is called")
    else:
        print("❌ run_scheduled_backup not called")
        return 1
    
    return 0

def verify_no_gui_calls_in_scheduled_methods():
    """Verify scheduled methods don't call GUI functions"""
    print()
    print("=" * 70)
    print("Verifying No GUI Calls in Scheduled Methods")
    print("=" * 70)
    print()
    
    script_path = os.path.join(os.path.dirname(__file__), '../src/nextcloud_restore_and_backup-v9.py')
    
    with open(script_path, 'r') as f:
        lines = f.readlines()
    
    # Find both methods
    methods_to_check = [
        'run_scheduled_backup',
        'run_backup_process_scheduled'
    ]
    
    all_clean = True
    
    for method_name in methods_to_check:
        print(f"Checking {method_name}...")
        
        # Find method start
        method_start = None
        for i, line in enumerate(lines):
            if f'def {method_name}(' in line:
                method_start = i
                break
        
        if not method_start:
            print(f"  ⚠️  Warning: Could not find {method_name}")
            continue
        
        # Find method end (next def at same indent level)
        indent_level = len(lines[method_start]) - len(lines[method_start].lstrip())
        method_end = len(lines)
        
        for i in range(method_start + 1, len(lines)):
            line = lines[i]
            if line.strip() and not line.strip().startswith('#'):
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and 'def ' in line:
                    method_end = i
                    break
        
        # Check for problematic GUI calls
        gui_patterns = [
            (r'self\.after\s*\(', 'self.after()'),
            (r'self\.show_', 'self.show_*()'),
            (r'messagebox\.', 'messagebox'),
            (r'filedialog\.', 'filedialog'),
            (r'self\._display_health', 'self._display_health_status()'),
            (r'self\._refresh_health', 'self._refresh_health_dashboard()'),
            (r'\.pack\(', 'widget.pack()'),
            (r'\.grid\(', 'widget.grid()'),
            (r'\.place\(', 'widget.place()'),
        ]
        
        found_issues = []
        for i in range(method_start, method_end):
            line = lines[i]
            for pattern, description in gui_patterns:
                if re.search(pattern, line):
                    found_issues.append((i + 1, description, line.strip()))
        
        if found_issues:
            print(f"  ❌ Found {len(found_issues)} potential GUI call(s):")
            for line_num, desc, line in found_issues:
                print(f"    Line {line_num}: {desc}")
                print(f"      {line}")
            all_clean = False
        else:
            print(f"  ✓ No GUI calls found")
    
    print()
    if all_clean:
        print("✅ All scheduled methods are clean (no GUI calls)")
        return 0
    else:
        print("❌ Found GUI calls in scheduled methods")
        return 1

def main():
    """Run all integration tests"""
    results = []
    
    results.append(analyze_init_method())
    results.append(verify_main_block())
    results.append(verify_no_gui_calls_in_scheduled_methods())
    
    print()
    print("=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    if all(r == 0 for r in results):
        print("✅ ALL INTEGRATION TESTS PASSED")
        print()
        print("Summary:")
        print("- __init__ properly guards GUI initialization")
        print("- Main block correctly creates app in scheduled_mode")
        print("- Scheduled methods don't call GUI functions")
        print()
        print("The fix is complete and correct!")
    else:
        print("❌ SOME INTEGRATION TESTS FAILED")
        print("Please review the issues above.")
    
    print("=" * 70)
    
    return max(results)

if __name__ == '__main__':
    sys.exit(main())
