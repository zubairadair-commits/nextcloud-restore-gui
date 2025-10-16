#!/usr/bin/env python3
"""
Demo: Enhanced Tailscale Detection on Windows

This script demonstrates the enhanced Tailscale detection logic
that checks multiple locations to find tailscale.exe on Windows.
"""

import platform
import subprocess
import os

def find_tailscale_exe():
    """
    Find tailscale.exe on Windows by checking multiple locations.
    Returns the full path to tailscale.exe if found, None otherwise.
    
    This is a standalone demo of the detection logic implemented in the main app.
    """
    if platform.system() != "Windows":
        print("This demo is designed for Windows. On this system, we would use 'which tailscale'.")
        return None
    
    print("=" * 70)
    print("Enhanced Tailscale Detection Demo")
    print("=" * 70)
    print()
    
    # Method 1: Check if tailscale is in PATH
    print("Method 1: Checking system PATH...")
    try:
        result = subprocess.run(
            ["where", "tailscale"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            # where command returns one or more paths, take the first one
            path = result.stdout.strip().split('\n')[0]
            if os.path.isfile(path):
                print(f"  ✓ Found in PATH: {path}")
                return path
        print("  ✗ Not found in PATH")
    except Exception as e:
        print(f"  ✗ Error checking PATH: {e}")
    
    print()
    
    # Method 2: Check common installation directories
    print("Method 2: Checking common installation directories...")
    common_locations = [
        r"C:\Program Files\Tailscale\tailscale.exe",
        r"C:\Program Files (x86)\Tailscale\tailscale.exe",
        os.path.expandvars(r"%ProgramFiles%\Tailscale\tailscale.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Tailscale\tailscale.exe"),
        os.path.expandvars(r"%LocalAppData%\Tailscale\tailscale.exe"),
    ]
    
    for location in common_locations:
        print(f"  Checking: {location}")
        if os.path.isfile(location):
            print(f"  ✓ Found: {location}")
            return location
        else:
            print(f"    Not found")
    
    print("  ✗ Not found in common locations")
    print()
    
    # Method 3: Try to query the Windows registry
    print("Method 3: Checking Windows registry...")
    try:
        import winreg
        
        # Check HKEY_LOCAL_MACHINE for installation path
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tailscale IPN"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Tailscale IPN"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Tailscale IPN"),
        ]
        
        for hkey, subkey in registry_paths:
            try:
                print(f"  Checking: {subkey}")
                with winreg.OpenKey(hkey, subkey) as key:
                    # Try to get install location or executable path
                    try:
                        install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
                        exe_path = os.path.join(install_dir, "tailscale.exe")
                        if os.path.isfile(exe_path):
                            print(f"  ✓ Found via registry: {exe_path}")
                            return exe_path
                    except FileNotFoundError:
                        pass
                    
                    try:
                        exe_path, _ = winreg.QueryValueEx(key, "ExecutablePath")
                        if os.path.isfile(exe_path):
                            print(f"  ✓ Found via registry: {exe_path}")
                            return exe_path
                    except FileNotFoundError:
                        pass
            except WindowsError:
                print(f"    Key not found")
        
        print("  ✗ Not found in registry")
    except ImportError:
        print("  ✗ winreg module not available")
    except Exception as e:
        print(f"  ✗ Error checking registry: {e}")
    
    print()
    print("=" * 70)
    print("✗ Tailscale not found on this system")
    print("=" * 70)
    return None

def main():
    """Main demo function"""
    print()
    print("This demo shows the enhanced Tailscale detection logic.")
    print("The app now checks multiple locations to find tailscale.exe:")
    print("  1. System PATH (using 'where' command)")
    print("  2. Common installation directories")
    print("  3. Windows registry")
    print()
    
    if platform.system() != "Windows":
        print("NOTE: This demo is designed for Windows.")
        print("On Linux/Mac, the app uses 'which tailscale' to check if it's installed.")
        print()
        return
    
    tailscale_path = find_tailscale_exe()
    
    print()
    if tailscale_path:
        print("✓ Result: Tailscale would be marked as INSTALLED")
        print(f"  Path: {tailscale_path}")
        print()
        print("The app can now:")
        print("  • Show Tailscale as installed in the Remote Access Setup page")
        print("  • Use the full path to run 'tailscale status' and other commands")
        print("  • Properly detect Tailscale regardless of installation method")
    else:
        print("✗ Result: Tailscale would be marked as NOT INSTALLED")
        print()
        print("The app will:")
        print("  • Show installation instructions in the Remote Access Setup page")
        print("  • Offer to open the Tailscale download page")

if __name__ == "__main__":
    main()
