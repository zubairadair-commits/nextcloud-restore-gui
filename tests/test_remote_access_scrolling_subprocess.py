"""
Tests for Remote Access page scrolling and subprocess window suppression.
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock, call
import platform
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Source file path
SOURCE_FILE = os.path.join(os.path.dirname(__file__), '..', 'src', 'nextcloud_restore_and_backup-v9.py')


class TestRemoteAccessScrollingAndSubprocess(unittest.TestCase):
    """Test Remote Access page improvements via source code analysis"""
    
    def test_get_tailscale_info_has_creationflags(self):
        """Test that _get_tailscale_info function includes creationflags in subprocess call"""
        # Read source file
        with open(SOURCE_FILE, 'r') as f:
            source = f.read()
        
        # Find the _get_tailscale_info function
        # Look for the function and the subprocess.run call within it
        func_pattern = r'def _get_tailscale_info\(self\):.*?(?=\n    def |\nclass |\Z)'
        func_match = re.search(func_pattern, source, re.DOTALL)
        
        self.assertIsNotNone(func_match, "_get_tailscale_info function should exist")
        
        func_source = func_match.group(0)
        
        # Check that subprocess.run is called with creationflags
        self.assertIn('subprocess.run', func_source, 
                     "_get_tailscale_info should call subprocess.run")
        self.assertIn('get_subprocess_creation_flags()', func_source,
                     "_get_tailscale_info should call get_subprocess_creation_flags()")
        self.assertIn('creationflags=creation_flags', func_source,
                     "_get_tailscale_info should pass creationflags to subprocess.run")
    
    def test_canvas_scrolling_uses_bind_not_bind_all(self):
        """Test that canvas scrolling uses .bind() instead of bind_all() to avoid conflicts"""
        # Read source file
        with open(SOURCE_FILE, 'r') as f:
            source = f.read()
        
        # Find the _show_tailscale_config function
        func_pattern = r'def _show_tailscale_config\(self\):.*?(?=\n    def |\nclass |\Z)'
        func_match = re.search(func_pattern, source, re.DOTALL)
        
        self.assertIsNotNone(func_match, "_show_tailscale_config function should exist")
        
        func_source = func_match.group(0)
        
        # Check for Canvas creation
        self.assertIn('tk.Canvas', func_source, "Should create a Canvas widget")
        self.assertIn('Scrollbar', func_source, "Should create a Scrollbar")
        
        # Check for proper scrolling setup
        self.assertIn('yscrollcommand', func_source, "Canvas should have yscrollcommand")
        self.assertIn('yview_scroll', func_source, "Should use yview_scroll for scrolling")
        
        # Check that mouse wheel events are bound
        self.assertIn('<MouseWheel>', func_source, "Should bind MouseWheel event")
        self.assertIn('<Button-4>', func_source, "Should bind Button-4 for Linux")
        self.assertIn('<Button-5>', func_source, "Should bind Button-5 for Linux")
        
        # Find the mouse wheel event binding section
        wheel_binding_pattern = r'def on_mouse_wheel.*?(?=\n        \n        logger\.info)'
        wheel_match = re.search(wheel_binding_pattern, func_source, re.DOTALL)
        
        self.assertIsNotNone(wheel_match, "Should have on_mouse_wheel function")
        
        wheel_source = wheel_match.group(0)
        
        # Check that canvas.bind is used, not canvas.bind_all
        self.assertIn('canvas.bind("<MouseWheel>"', wheel_source,
                     "Should use canvas.bind() for MouseWheel")
        self.assertIn('canvas.bind("<Button-4>"', wheel_source,
                     "Should use canvas.bind() for Button-4")
        self.assertIn('canvas.bind("<Button-5>"', wheel_source,
                     "Should use canvas.bind() for Button-5")
        
        # Ensure bind_all is NOT used in main canvas bindings
        # (There might be bind_all in other parts, but not in this section)
        self.assertNotIn('bind_all("<MouseWheel>"', wheel_source,
                        "Should NOT use bind_all() to avoid conflicts with other pages")
    
    def test_mouse_wheel_handler_uses_delta_division(self):
        """Test that mouse wheel handler properly uses event.delta/120 for Windows/Mac"""
        # Read source file
        with open(SOURCE_FILE, 'r') as f:
            source = f.read()
        
        # Find the _show_tailscale_config function
        func_pattern = r'def _show_tailscale_config\(self\):.*?(?=\n    def |\nclass |\Z)'
        func_match = re.search(func_pattern, source, re.DOTALL)
        
        self.assertIsNotNone(func_match, "_show_tailscale_config function should exist")
        
        func_source = func_match.group(0)
        
        # Find the on_mouse_wheel function
        wheel_pattern = r'def on_mouse_wheel\(event\):.*?(?=\n        \n        # Bind)'
        wheel_match = re.search(wheel_pattern, func_source, re.DOTALL)
        
        self.assertIsNotNone(wheel_match, "Should have on_mouse_wheel function")
        
        wheel_source = wheel_match.group(0)
        
        # Check for proper delta handling
        self.assertIn('event.delta', wheel_source, 
                     "Should check event.delta for Windows/Mac")
        self.assertIn('event.delta/120', wheel_source,
                     "Should divide delta by 120 for proper scrolling speed")
        self.assertIn('event.num', wheel_source,
                     "Should check event.num for Linux")
    
    def test_domain_list_canvas_has_scrolling(self):
        """Test that the nested domain list canvas also has proper scrolling"""
        # Read source file
        with open(SOURCE_FILE, 'r') as f:
            source = f.read()
        
        # Find the _display_current_trusted_domains function
        func_pattern = r'def _display_current_trusted_domains\(self, parent\):.*?(?=\n    def |\nclass |\Z)'
        func_match = re.search(func_pattern, source, re.DOTALL)
        
        self.assertIsNotNone(func_match, "_display_current_trusted_domains function should exist")
        
        func_source = func_match.group(0)
        
        # Check for Canvas creation for domain list
        self.assertIn('tk.Canvas', func_source, "Should create a Canvas for domain list")
        
        # Check for separate mouse wheel handler
        self.assertIn('on_domain_mouse_wheel', func_source,
                     "Should have separate mouse wheel handler for domain list")
        
        # Find the domain mouse wheel handler
        domain_wheel_pattern = r'def on_domain_mouse_wheel\(event\):.*?(?=\n            \n            # Bind)'
        domain_wheel_match = re.search(domain_wheel_pattern, func_source, re.DOTALL)
        
        self.assertIsNotNone(domain_wheel_match, "Should have on_domain_mouse_wheel function")
        
        domain_wheel_source = domain_wheel_match.group(0)
        
        # Check for proper delta handling in domain list too
        self.assertIn('event.delta', domain_wheel_source,
                     "Domain list should check event.delta")
        self.assertIn('event.delta/120', domain_wheel_source,
                     "Domain list should divide delta by 120")


class TestSubprocessCreationFlags(unittest.TestCase):
    """Test that all Remote Access subprocess calls use creation flags via source analysis"""
    
    def test_check_scheduled_task_uses_flags(self):
        """Test that check_scheduled_task_status uses creationflags on Windows"""
        # Read source file
        with open(SOURCE_FILE, 'r') as f:
            source = f.read()
        
        # Find the function
        func_pattern = r'def check_scheduled_task_status\(\):.*?(?=\ndef |\nclass |\Z)'
        func_match = re.search(func_pattern, source, re.DOTALL)
        
        self.assertIsNotNone(func_match, "check_scheduled_task_status function should exist")
        
        func_source = func_match.group(0)
        
        # Check that it calls get_subprocess_creation_flags
        self.assertIn('get_subprocess_creation_flags()', func_source,
                     "Should call get_subprocess_creation_flags()")
        
        # Check that it passes creationflags to subprocess.run
        self.assertIn('creationflags=creation_flags', func_source,
                     "Should pass creationflags to subprocess.run")
    
    def test_setup_windows_task_scheduler_uses_flags(self):
        """Test that _setup_windows_task_scheduler uses creationflags"""
        # Read source file
        with open(SOURCE_FILE, 'r') as f:
            source = f.read()
        
        # Find the function
        func_pattern = r'def _setup_windows_task_scheduler\(.*?\):.*?(?=\ndef |\nclass |\Z)'
        func_match = re.search(func_pattern, source, re.DOTALL)
        
        self.assertIsNotNone(func_match, "_setup_windows_task_scheduler function should exist")
        
        func_source = func_match.group(0)
        
        # Check that it uses creationflags
        self.assertIn('get_subprocess_creation_flags()', func_source,
                     "Should call get_subprocess_creation_flags()")
        self.assertIn('creationflags=creation_flags', func_source,
                     "Should pass creationflags to subprocess.run")
    
    def test_disable_scheduled_task_uses_flags(self):
        """Test that disable_scheduled_task uses creationflags on Windows"""
        # Read source file
        with open(SOURCE_FILE, 'r') as f:
            source = f.read()
        
        # Find the function
        func_pattern = r'def disable_scheduled_task\(\):.*?(?=\ndef |\nclass |\Z)'
        func_match = re.search(func_pattern, source, re.DOTALL)
        
        self.assertIsNotNone(func_match, "disable_scheduled_task function should exist")
        
        func_source = func_match.group(0)
        
        # Check that it uses creationflags for Windows operations
        self.assertIn('get_subprocess_creation_flags()', func_source,
                     "Should call get_subprocess_creation_flags()")
    
    def test_enable_scheduled_task_uses_flags(self):
        """Test that enable_scheduled_task uses creationflags on Windows"""
        # Read source file
        with open(SOURCE_FILE, 'r') as f:
            source = f.read()
        
        # Find all enable_scheduled_task functions
        func_pattern = r'def enable_scheduled_task\(.*?\):.*?(?=\ndef |\nclass |\Z)'
        func_matches = re.finditer(func_pattern, source, re.DOTALL)
        
        found_windows_func = False
        for func_match in func_matches:
            func_source = func_match.group(0)
            # Only check Windows-specific functions
            if 'Windows' in func_source:
                found_windows_func = True
                self.assertIn('get_subprocess_creation_flags()', func_source,
                             "Windows-specific enable_scheduled_task should call get_subprocess_creation_flags()")
        
        self.assertTrue(found_windows_func, "Should have at least one Windows-specific enable_scheduled_task function")


if __name__ == '__main__':
    unittest.main()
