#!/usr/bin/env python3
"""
Test suite for background extraction and detection threading improvements.
Verifies that extraction/detection runs in background thread without blocking UI.
"""

import sys
import os

# Add the script directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_script_path():
    """Get the path to the main script"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(test_dir, '..', 'src', 'nextcloud_restore_and_backup-v9.py')
    return script_path

def test_syntax():
    """Test Python syntax is valid"""
    print("\nTesting Python syntax...")
    import py_compile
    try:
        py_compile.compile(get_script_path(), doraise=True)
        print("  ✓ Syntax check passed")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ✗ Syntax error: {e}")
        return False

def test_threading_methods_exist():
    """Test that threading helper methods exist"""
    print("\nTesting threading helper methods...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        required_methods = [
            'def _disable_wizard_navigation(self):',
            'def _enable_wizard_navigation(self):',
            'def _process_detection_results(self, result):',
            'def check_detection_progress():',
        ]
        
        for method in required_methods:
            if method in content:
                print(f"  ✓ Found: {method}")
            else:
                print(f"  ✗ Missing: {method}")
                return False
        
        print("  ✓ All threading helper methods exist")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_no_blocking_sleep_in_main_thread():
    """Test that the blocking while loop with time.sleep is removed"""
    print("\nTesting for blocking code removal...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check that the old blocking pattern is not present
        # Look for the specific pattern in perform_extraction_and_detection
        lines = content.split('\n')
        
        in_perform_extraction = False
        has_blocking_pattern = False
        
        for i, line in enumerate(lines):
            if 'def perform_extraction_and_detection(self):' in line:
                in_perform_extraction = True
            elif in_perform_extraction and line.strip().startswith('def '):
                # Exited the method
                break
            elif in_perform_extraction:
                # Check for blocking pattern: while loop with time.sleep
                if 'while detection_thread.is_alive():' in line:
                    # Check next few lines for time.sleep
                    for j in range(i, min(i+10, len(lines))):
                        if 'time.sleep' in lines[j]:
                            has_blocking_pattern = True
                            print(f"  ✗ Found blocking pattern at line {j+1}: {lines[j].strip()}")
                            break
        
        if not has_blocking_pattern:
            print("  ✓ No blocking while loop with time.sleep found")
            return True
        else:
            print("  ✗ Blocking pattern still exists in perform_extraction_and_detection")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_uses_after_method():
    """Test that .after() method is used for non-blocking progress checks"""
    print("\nTesting for .after() usage...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Look for self.after call in check_detection_progress
        if 'self.after(100, check_detection_progress)' in content:
            print("  ✓ Found non-blocking .after() call in progress checker")
            return True
        else:
            print("  ✗ .after() call not found in progress checker")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_navigation_disable_enable():
    """Test that navigation buttons are disabled/enabled properly"""
    print("\nTesting navigation button disable/enable logic...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        checks = [
            ('self._disable_wizard_navigation()', 'Navigation disabled before detection'),
            ('self._enable_wizard_navigation()', 'Navigation enabled after detection'),
            ("child.config(state='disabled')", 'Button disable implementation'),
            ("child.config(state='normal')", 'Button enable implementation'),
        ]
        
        all_found = True
        for pattern, description in checks:
            if pattern in content:
                print(f"  ✓ {description}: {pattern}")
            else:
                print(f"  ✗ Missing {description}")
                all_found = False
        
        return all_found
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_navigation_happens_after_detection():
    """Test that navigation to Page 2 happens after detection completes"""
    print("\nTesting navigation timing...")
    try:
        with open(get_script_path(), 'r') as f:
            content = f.read()
        
        # Check that navigation happens in _process_detection_results
        if 'self.show_wizard_page(2)' in content:
            # Count occurrences in _process_detection_results
            in_method = False
            count = 0
            for line in content.split('\n'):
                if 'def _process_detection_results(self, result):' in line:
                    in_method = True
                elif in_method and line.strip().startswith('def '):
                    break
                elif in_method and 'self.show_wizard_page(2)' in line:
                    count += 1
            
            if count >= 2:  # Should have at least 2 calls (success and warning cases)
                print(f"  ✓ Navigation to Page 2 happens in _process_detection_results ({count} occurrences)")
                return True
            else:
                print(f"  ✗ Unexpected navigation pattern (found {count} occurrences)")
                return False
        else:
            print("  ✗ Navigation call not found")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("=" * 70)
    print("Background Extraction Threading Tests")
    print("=" * 70)
    
    tests = [
        ("Syntax", test_syntax),
        ("Threading Helper Methods", test_threading_methods_exist),
        ("No Blocking Sleep", test_no_blocking_sleep_in_main_thread),
        ("Uses .after() Method", test_uses_after_method),
        ("Navigation Disable/Enable", test_navigation_disable_enable),
        ("Navigation After Detection", test_navigation_happens_after_detection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test {name} raised exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} | {name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
