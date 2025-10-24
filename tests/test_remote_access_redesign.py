"""
Tests for the redesigned Remote Access configuration page.
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Since the main file uses tkinter, we need to mock it
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

class TestRemoteAccessRedesign(unittest.TestCase):
    """Test the redesigned remote access page functionality"""
    
    def test_run_tailscale_serve_now_function_exists(self):
        """Test that the new run_tailscale_serve_now function exists"""
        # Read the source file directly
        source_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')
        with open(source_path, 'r') as f:
            content = f.read()
            
        self.assertIn('def run_tailscale_serve_now(port):', content, 
                      "run_tailscale_serve_now function should be defined")
        self.assertIn('tailscale serve --bg --https=443', content,
                      "Function should execute tailscale serve command")
    
    def test_enable_remote_access_auto_method_exists(self):
        """Test that the _enable_remote_access_auto method exists"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            content = f.read()
            
        self.assertIn('def _enable_remote_access_auto(self, parent, canvas, ts_ip, ts_hostname, port):', content,
                      "_enable_remote_access_auto method should be defined")
        self.assertIn('setup_tailscale_serve_startup(port, enable=True)', content,
                      "Method should call setup_tailscale_serve_startup")
        self.assertIn('run_tailscale_serve_now(port)', content,
                      "Method should call run_tailscale_serve_now")
    
    def test_simplified_ui_elements_present(self):
        """Test that the simplified UI elements are present in the code"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            content = f.read()
        
        # Check for status indicators
        self.assertIn('System Status', content, 
                      "Should have System Status section")
        self.assertIn('Tailscale Running Status', content,
                      "Should check Tailscale running status")
        self.assertIn('Nextcloud Port Detected', content,
                      "Should check Nextcloud port detection")
        self.assertIn('Scheduled Task Status', content,
                      "Should check scheduled task status")
        
        # Check for main action button
        self.assertIn('Enable Remote Access', content,
                      "Should have Enable Remote Access button")
        
        # Check for troubleshooting section
        self.assertIn('_create_troubleshooting_section', content,
                      "Should have troubleshooting section")
        self.assertIn('Show Troubleshooting & Advanced Options', content,
                      "Should have collapsible troubleshooting")
    
    def test_clickable_urls_with_status(self):
        """Test that URLs are displayed with status indicators"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            content = f.read()
        
        self.assertIn('_create_clickable_url_with_status', content,
                      "Should have method to create URLs with status")
        self.assertIn('is_ready', content,
                      "Should track URL readiness status")
        self.assertIn('tooltip', content,
                      "Should display tooltips for URLs")
    
    def test_automatic_workflow_steps(self):
        """Test that the automatic workflow includes all required steps"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            content = f.read()
        
        # Check for the three main steps in _enable_remote_access_auto
        self.assertIn('Creating scheduled task for Tailscale Serve', content,
                      "Step 1: Should create scheduled task")
        self.assertIn('Starting Tailscale Serve immediately', content,
                      "Step 2: Should start Tailscale Serve immediately")
        self.assertIn('Configuring Nextcloud trusted domains', content,
                      "Step 3: Should configure trusted domains")
    
    def test_error_detection_and_feedback(self):
        """Test that common issues are detected and shown"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            content = f.read()
        
        # Check for error detection
        self.assertIn('Start Tailscale First', content,
                      "Should detect when Tailscale is not running")
        self.assertIn('Start Nextcloud First', content,
                      "Should detect when Nextcloud is not running")
        self.assertIn('already running', content,
                      "Should handle case when serve is already running")
    
    def test_status_indicators_logic(self):
        """Test that status indicators show correct colors"""
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py'), 'r') as f:
            content = f.read()
        
        # Check for green/red indicators
        self.assertIn('#45bf55', content,
                      "Should use green color for success")
        self.assertIn('error_fg', content,
                      "Should use error color for failures")
        self.assertIn('status_icon = "✓"', content,
                      "Should use checkmark for success")
        self.assertIn('status_icon = "✗"', content,
                      "Should use X mark for failure")

if __name__ == '__main__':
    unittest.main()
