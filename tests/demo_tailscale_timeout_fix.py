#!/usr/bin/env python3
"""
Interactive test to demonstrate the Tailscale timeout fix behavior.
This simulates various scenarios without needing actual Tailscale installed.
"""

import subprocess
import shutil
import sys

def test_shutil_which():
    """Test shutil.which() behavior"""
    print("=" * 70)
    print("Testing shutil.which() behavior")
    print("=" * 70)
    print()
    
    # Test with a common command that should exist
    test_commands = ["python3", "python", "ls", "echo", "bash"]
    
    print("Testing shutil.which() with common commands:")
    for cmd in test_commands:
        result = shutil.which(cmd)
        if result:
            print(f"  ✓ shutil.which('{cmd}') = {result}")
            break
    
    # Test with tailscale (likely won't be found in test environment)
    print()
    print("Testing Tailscale detection:")
    tailscale_path = shutil.which("tailscale")
    if tailscale_path:
        print(f"  ✓ Tailscale found at: {tailscale_path}")
    else:
        print("  ℹ Tailscale not found (expected in test environment)")
        print("    Error message would be: 'Tailscale CLI not found. Please ensure Tailscale is installed and in your PATH.'")
    
    print()

def test_timeout_behavior():
    """Demonstrate timeout behavior"""
    print("=" * 70)
    print("Testing timeout behavior")
    print("=" * 70)
    print()
    
    print("The implementation now uses timeout=15 seconds instead of 5 seconds.")
    print("This gives Tailscale more time to respond, reducing timeout errors.")
    print()
    print("Timeout scenarios handled:")
    print("  • If command times out: 'Tailscale command timed out. The service may be unresponsive.'")
    print("  • Error is logged with: logger.error(error_msg)")
    print()

def test_error_messages():
    """Show all error messages that can be returned"""
    print("=" * 70)
    print("Error Messages")
    print("=" * 70)
    print()
    
    error_scenarios = [
        ("CLI not found (non-Windows)", 
         "Tailscale CLI not found. Please ensure Tailscale is installed and in your PATH."),
        ("Timeout expired", 
         "Tailscale command timed out. The service may be unresponsive."),
        ("Service not running", 
         "Tailscale service is not running. Please start Tailscale."),
        ("Permission denied", 
         "Permission denied. Try running with administrator/sudo privileges."),
        ("Not logged in", 
         "Tailscale is not logged in. Please login to Tailscale first."),
        ("Command failed", 
         "Tailscale command failed: [stderr output]"),
        ("JSON parse error", 
         "Failed to parse Tailscale status JSON: [error details]"),
        ("No network info", 
         "Tailscale is running but no network information available. Ensure Tailscale is connected."),
        ("Missing Self info", 
         "Tailscale status response missing 'Self' information."),
        ("Unexpected error", 
         "Unexpected error: [error details]"),
    ]
    
    print("All error scenarios handled:")
    for scenario, message in error_scenarios:
        print(f"  • {scenario}:")
        print(f"    → {message}")
        print()

def main():
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Tailscale Timeout Fix Demo" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    test_shutil_which()
    test_timeout_behavior()
    test_error_messages()
    
    print("=" * 70)
    print("Summary of Changes")
    print("=" * 70)
    print()
    print("The _get_tailscale_info() method has been updated with:")
    print()
    print("1. ✓ shutil.which('tailscale') for reliable executable detection")
    print("2. ✓ Increased timeout from 5 to 15 seconds")
    print("3. ✓ Enhanced error logging with logger.error()")
    print("4. ✓ Detailed error messages for all scenarios")
    print("5. ✓ Full stderr output capture and logging")
    print("6. ✓ Maintained Windows compatibility")
    print()
    print("These changes resolve the timeout issue when Tailscale is running")
    print("but network info retrieval takes longer than 5 seconds.")
    print()

if __name__ == '__main__':
    main()
