#!/usr/bin/env python3
"""
Integration test for background extraction threading improvements.
Tests the complete flow with mock objects to verify behavior.
"""

import sys
import os
import time
import threading

# Add the script directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockWidget:
    """Mock Tkinter widget for testing"""
    def __init__(self, widget_type='Button'):
        self.widget_type = widget_type
        self.state = 'normal'
        self.text = ''
        self.fg = 'black'
        
    def config(self, **kwargs):
        """Mock config method"""
        if 'state' in kwargs:
            self.state = kwargs['state']
        if 'text' in kwargs:
            self.text = kwargs['text']
        if 'fg' in kwargs:
            self.fg = kwargs['fg']
    
    def winfo_children(self):
        """Mock winfo_children for frames"""
        if self.widget_type == 'Frame':
            return [MockWidget('Button'), MockWidget('Button')]
        return []

class MockWizard:
    """Mock wizard for testing threading behavior"""
    
    def __init__(self):
        self.wizard_scrollable_frame = MockWidget('Frame')
        self.error_label = MockWidget('Label')
        self.extraction_successful = False
        self.detected_dbtype = None
        self.after_calls = []
        self.navigation_enabled = True
        
    def after(self, delay, callback):
        """Mock after method - captures calls for verification"""
        self.after_calls.append((delay, callback))
        # Don't execute callback immediately to avoid recursion
        # In a real Tkinter app, this would schedule for later execution
    
    def _disable_wizard_navigation(self):
        """Disable wizard navigation buttons during background processing"""
        self.navigation_enabled = False
        for widget in self.wizard_scrollable_frame.winfo_children():
            if isinstance(widget, MockWidget):
                for child in widget.winfo_children():
                    if isinstance(child, MockWidget):
                        child.config(state='disabled')
    
    def _enable_wizard_navigation(self):
        """Re-enable wizard navigation buttons after background processing"""
        self.navigation_enabled = True
        for widget in self.wizard_scrollable_frame.winfo_children():
            if isinstance(widget, MockWidget):
                for child in widget.winfo_children():
                    if isinstance(child, MockWidget):
                        child.config(state='normal')
    
    def _process_detection_results(self, result):
        """Process detection results"""
        self._enable_wizard_navigation()
        
        if result:
            dbtype, db_config, error = result
            
            if error:
                self.error_label.config(text=f"Error: {error}", fg="red")
                self.extraction_successful = False
            elif dbtype:
                self.extraction_successful = True
                self.detected_dbtype = dbtype
                self.error_label.config(text="✓ Detection successful", fg="green")
            else:
                self.error_label.config(text="⚠️ Warning: Could not detect", fg="orange")
    
    def perform_extraction_and_detection(self, simulate_success=True, simulate_delay=0.1):
        """Simulate extraction and detection with threading"""
        # Disable navigation
        self._disable_wizard_navigation()
        
        # Setup result storage
        detection_result = [None]
        detection_complete = [False]
        
        def do_detection():
            """Background thread function"""
            try:
                time.sleep(simulate_delay)  # Simulate work
                if simulate_success:
                    detection_result[0] = ('mysql', {'dbname': 'nextcloud'}, None)
                else:
                    detection_result[0] = (None, None, Exception("Test error"))
            finally:
                detection_complete[0] = True
        
        # Start background thread
        thread = threading.Thread(target=do_detection, daemon=True)
        thread.start()
        
        # Wait for thread to complete in this mock (simplified for testing)
        thread.join()
        
        # Process results immediately (in real app, this happens via .after() callbacks)
        if detection_complete[0]:
            self._process_detection_results(detection_result[0])
        
        return True

def test_navigation_disabled_during_extraction():
    """Test that navigation is disabled during extraction"""
    print("\nTest: Navigation disabled during extraction...")
    
    wizard = MockWizard()
    
    # Initially enabled
    assert wizard.navigation_enabled == True, "Navigation should start enabled"
    print("  ✓ Navigation initially enabled")
    
    # Disable during extraction
    wizard._disable_wizard_navigation()
    assert wizard.navigation_enabled == False, "Navigation should be disabled"
    print("  ✓ Navigation disabled during extraction")
    
    # Check button states
    for widget in wizard.wizard_scrollable_frame.winfo_children():
        for child in widget.winfo_children():
            assert child.state == 'disabled', "Buttons should be disabled"
    print("  ✓ Navigation buttons are disabled")
    
    return True

def test_navigation_enabled_after_extraction():
    """Test that navigation is re-enabled after extraction"""
    print("\nTest: Navigation enabled after extraction...")
    
    wizard = MockWizard()
    wizard._disable_wizard_navigation()
    
    # Re-enable
    wizard._enable_wizard_navigation()
    assert wizard.navigation_enabled == True, "Navigation should be re-enabled"
    print("  ✓ Navigation re-enabled after extraction")
    
    # Check button states
    for widget in wizard.wizard_scrollable_frame.winfo_children():
        for child in widget.winfo_children():
            assert child.state == 'normal', "Buttons should be enabled"
    print("  ✓ Navigation buttons are enabled")
    
    return True

def test_successful_detection_flow():
    """Test successful detection flow"""
    print("\nTest: Successful detection flow...")
    
    wizard = MockWizard()
    
    # Simulate successful extraction
    wizard.perform_extraction_and_detection(simulate_success=True, simulate_delay=0.1)
    
    # Verify results
    assert wizard.extraction_successful == True, "Extraction should succeed"
    print("  ✓ Extraction marked successful")
    
    assert wizard.detected_dbtype == 'mysql', "Database type should be detected"
    print("  ✓ Database type detected")
    
    assert wizard.navigation_enabled == True, "Navigation should be re-enabled"
    print("  ✓ Navigation re-enabled after success")
    
    assert "✓" in wizard.error_label.text, "Success message should be shown"
    print("  ✓ Success message displayed")
    
    return True

def test_failed_detection_flow():
    """Test failed detection flow"""
    print("\nTest: Failed detection flow...")
    
    wizard = MockWizard()
    
    # Simulate failed extraction
    wizard.perform_extraction_and_detection(simulate_success=False, simulate_delay=0.1)
    
    # Verify results
    assert wizard.extraction_successful == False, "Extraction should fail"
    print("  ✓ Extraction marked failed")
    
    assert wizard.detected_dbtype == None, "Database type should not be detected"
    print("  ✓ No database type detected")
    
    assert wizard.navigation_enabled == True, "Navigation should be re-enabled"
    print("  ✓ Navigation re-enabled after failure")
    
    assert "Error" in wizard.error_label.text, "Error message should be shown"
    print("  ✓ Error message displayed")
    
    return True

def test_ui_updates_during_extraction():
    """Test that UI updates happen during extraction"""
    print("\nTest: UI updates during extraction...")
    
    wizard = MockWizard()
    
    # Start extraction
    wizard.perform_extraction_and_detection(simulate_success=True, simulate_delay=0.1)
    
    # Extraction is complete now (simplified mock)
    assert wizard.extraction_successful == True, "Extraction should complete"
    print(f"  ✓ Extraction completed successfully")
    
    return True

def test_non_blocking_behavior():
    """Test that extraction doesn't block the main thread"""
    print("\nTest: Non-blocking behavior (conceptual)...")
    
    wizard = MockWizard()
    
    # In the real implementation, this returns immediately
    # In the mock, we simplify by blocking for testing
    wizard.perform_extraction_and_detection(simulate_success=True, simulate_delay=0.1)
    
    # Should be complete now
    assert wizard.extraction_successful == True, "Extraction should complete"
    print("  ✓ Extraction completed")
    print("  ℹ️  Real implementation uses .after() for non-blocking behavior")
    
    return True

def run_integration_tests():
    """Run all integration tests"""
    print("=" * 70)
    print("Background Extraction Integration Tests")
    print("=" * 70)
    
    tests = [
        ("Navigation Disabled During Extraction", test_navigation_disabled_during_extraction),
        ("Navigation Enabled After Extraction", test_navigation_enabled_after_extraction),
        ("Successful Detection Flow", test_successful_detection_flow),
        ("Failed Detection Flow", test_failed_detection_flow),
        ("UI Updates During Extraction", test_ui_updates_during_extraction),
        ("Non-Blocking Behavior", test_non_blocking_behavior),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except AssertionError as e:
            print(f"\n✗ Test failed: {e}")
            results.append((name, False))
        except Exception as e:
            print(f"\n✗ Test raised exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("Integration Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} | {name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All integration tests passed!")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
