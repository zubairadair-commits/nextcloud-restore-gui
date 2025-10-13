#!/usr/bin/env python3
"""
Test script to verify the Remote Access Setup (Tailscale) geometry refactoring.
Validates that:
1. Canvas/scrollbar complexity has been removed
2. Content frame uses .place() for centering
3. All widgets use .pack() geometry manager
4. Debug label is present for visibility
"""

import sys
import os
import re

def test_tailscale_geometry_refactor():
    """Test that Tailscale pages use simplified geometry (no Canvas/scrollbar)"""
    print("=" * 70)
    print("Remote Access Setup (Tailscale) Geometry Refactoring Verification")
    print("=" * 70)
    print()
    
    main_file = "nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Test both functions
    test_results = []
    
    for func_name in ['show_tailscale_wizard', '_show_tailscale_config']:
        print(f"\nTesting {func_name}():")
        print("-" * 70)
        
        # Find method
        method_pattern = rf'def {func_name}\(self\):(.*?)(?=\n    def |\Z)'
        match = re.search(method_pattern, content, re.DOTALL)
        
        if not match:
            print(f"✗ Could not find {func_name} method")
            test_results.append(False)
            continue
        
        method_content = match.group(1)
        
        checks = []
        
        # Check 1: NO Canvas is created (Canvas/scrollbar removed)
        if 'tk.Canvas(' not in method_content and 'canvas = tk.Canvas' not in method_content:
            print("✓ Check 1: Canvas/scrollbar complexity removed")
            checks.append(True)
        else:
            print("✗ Check 1: Canvas still present (should be removed)")
            checks.append(False)
        
        # Check 2: NO Scrollbar is created
        if 'ttk.Scrollbar(' not in method_content and 'scrollbar = ttk.Scrollbar' not in method_content:
            print("✓ Check 2: Scrollbar removed")
            checks.append(True)
        else:
            print("✗ Check 2: Scrollbar still present (should be removed)")
            checks.append(False)
        
        # Check 3: Content frame uses .place() for centering
        if 'content.place(relx=0.5, anchor="n"' in method_content:
            print("✓ Check 3: Content frame uses .place() for centering")
            checks.append(True)
        else:
            print("✗ Check 3: Content frame does NOT use .place() centering")
            checks.append(False)
        
        # Check 4: Content frame has fixed width of 600px
        if 'content = tk.Frame(self.body_frame, bg=self.theme_colors[\'bg\'], width=600)' in method_content:
            print("✓ Check 4: Content frame has 600px width")
            checks.append(True)
        else:
            print("✗ Check 4: Content frame width not set to 600px")
            checks.append(False)
        
        # Check 5: Width maintenance function exists
        if 'def maintain_width(event=None):' in method_content and 'content.config(width=600)' in method_content:
            print("✓ Check 5: Width maintenance function present")
            checks.append(True)
        else:
            print("✗ Check 5: Width maintenance function missing")
            checks.append(False)
        
        # Check 6: Debug label is present and visible (big, colored)
        if '🔍 DEBUG: Content Frame Rendered' in method_content:
            print("✓ Check 6: Debug label present")
            checks.append(True)
        else:
            print("✗ Check 6: Debug label NOT found")
            checks.append(False)
        
        # Check 7: Debug label has visible styling (gold background)
        if 'bg="#FFD700"' in method_content and 'DEBUG: Content Frame Rendered' in method_content:
            print("✓ Check 7: Debug label has visible styling (gold background)")
            checks.append(True)
        else:
            print("✗ Check 7: Debug label styling not as expected")
            checks.append(False)
        
        # Check 8: Widgets use .pack() with fill="x", padx=40 pattern
        pack_fill_x_count = len(re.findall(r'\.pack\(.*?fill="x".*?padx=40', method_content))
        if pack_fill_x_count >= 3:
            print(f"✓ Check 8: Multiple widgets use .pack() with fill='x', padx=40 ({pack_fill_x_count} found)")
            checks.append(True)
        else:
            print(f"✗ Check 8: Insufficient .pack() with fill='x', padx=40 patterns ({pack_fill_x_count} found, need >= 3)")
            checks.append(False)
        
        # Check 9: No .grid() calls (except in specific allowed contexts like grid_columnconfigure)
        grid_calls = re.findall(r'\.grid\([^_]', method_content)
        if len(grid_calls) == 0:
            print("✓ Check 9: No .grid() geometry manager used")
            checks.append(True)
        else:
            print(f"✗ Check 9: .grid() calls found: {len(grid_calls)}")
            checks.append(False)
        
        # Check 10: Loading indicator still present for initial blank prevention
        if 'Loading' in method_content and 'loading_label' in method_content:
            print("✓ Check 10: Loading indicator present")
            checks.append(True)
        else:
            print("✗ Check 10: Loading indicator missing")
            checks.append(False)
        
        all_passed = all(checks)
        test_results.append(all_passed)
        
        if all_passed:
            print(f"\n✅ All checks passed for {func_name}!")
        else:
            print(f"\n❌ Some checks failed for {func_name}")
    
    # Overall result
    print("\n" + "=" * 70)
    if all(test_results):
        print("✅ OVERALL: All geometry refactoring tests passed!")
        print("\nSummary:")
        print("  • Canvas/scrollbar complexity removed")
        print("  • Content frame uses .place() for centering")
        print("  • All widgets use .pack() geometry manager")
        print("  • Debug labels present for visibility")
        print("  • Width maintenance implemented")
        print("  • Loading indicators prevent blank pages")
        return True
    else:
        print("❌ OVERALL: Some geometry refactoring tests failed")
        return False

if __name__ == "__main__":
    success = test_tailscale_geometry_refactor()
    sys.exit(0 if success else 1)
