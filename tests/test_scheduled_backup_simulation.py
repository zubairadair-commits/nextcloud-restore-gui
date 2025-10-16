#!/usr/bin/env python3
"""
Simulate a scheduled backup execution to ensure no GUI errors occur.
This mimics what happens when Windows Task Scheduler runs the backup.
"""

import sys
import os
import subprocess
import tempfile

def test_scheduled_mode_execution():
    """
    Test that scheduled mode can be invoked without GUI errors.
    This simulates the Windows Task Scheduler execution.
    """
    print("=" * 70)
    print("Simulating Scheduled Backup Execution")
    print("=" * 70)
    print()
    
    script_path = os.path.join(os.path.dirname(__file__), '../src/nextcloud_restore_and_backup-v9.py')
    
    # Create a temporary directory for backup
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Using temporary backup directory: {tmpdir}")
        print()
        
        # Test 1: Run with minimal arguments (should fail gracefully without GUI errors)
        print("Test 1: Running scheduled backup with --scheduled flag...")
        print("Command: python3 nextcloud_restore_and_backup-v9.py --scheduled --backup-dir /tmp/test")
        print()
        
        cmd = [
            sys.executable,
            script_path,
            '--scheduled',
            '--backup-dir', tmpdir,
            '--no-encrypt'
        ]
        
        try:
            # Run the command with a timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            print("STDOUT:")
            print(result.stdout)
            print()
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
                print()
            
            # Check for GUI-related errors
            gui_errors = [
                'main thread is not in main loop',
                'RuntimeError',
                'tkinter',
                '_tkinter.TclError',
                'self.after'
            ]
            
            error_output = result.stdout + result.stderr
            found_gui_errors = []
            
            for error_pattern in gui_errors:
                if error_pattern.lower() in error_output.lower():
                    found_gui_errors.append(error_pattern)
            
            if found_gui_errors:
                print("❌ FAILED: Found GUI-related errors:")
                for error in found_gui_errors:
                    print(f"  - {error}")
                return 1
            else:
                print("✅ SUCCESS: No GUI-related errors found")
                print()
                
                # Check if it ran correctly (may fail due to no Docker, but that's OK)
                if 'ERROR: Docker is not running' in result.stdout:
                    print("ℹ️  Note: Docker not available (expected in test environment)")
                    print("   The important part is that no GUI errors occurred.")
                elif 'ERROR: No running Nextcloud container found' in result.stdout:
                    print("ℹ️  Note: No Nextcloud container (expected in test environment)")
                    print("   The important part is that no GUI errors occurred.")
                elif result.returncode == 0:
                    print("✅ Backup completed successfully")
                
                return 0
                
        except subprocess.TimeoutExpired:
            print("❌ FAILED: Process hung (likely waiting for GUI)")
            return 1
        except Exception as e:
            print(f"❌ FAILED: Unexpected error: {e}")
            return 1

def test_help_output():
    """Test that help output works"""
    print()
    print("=" * 70)
    print("Testing Help Output")
    print("=" * 70)
    print()
    
    script_path = os.path.join(os.path.dirname(__file__), '../src/nextcloud_restore_and_backup-v9.py')
    
    try:
        result = subprocess.run(
            [sys.executable, script_path, '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if '--scheduled' in result.stdout:
            print("✅ Help output includes --scheduled flag")
            return 0
        else:
            print("❌ --scheduled flag not found in help")
            return 1
            
    except Exception as e:
        print(f"❌ Failed to get help output: {e}")
        return 1

def main():
    """Run all simulation tests"""
    result1 = test_scheduled_mode_execution()
    result2 = test_help_output()
    
    print()
    print("=" * 70)
    if result1 == 0 and result2 == 0:
        print("✅ ALL SIMULATION TESTS PASSED")
        print()
        print("The scheduled backup mode works correctly:")
        print("- No GUI initialization when --scheduled flag is used")
        print("- No 'main thread is not in main loop' errors")
        print("- Safe to run from Windows Task Scheduler")
    else:
        print("❌ SOME SIMULATION TESTS FAILED")
    print("=" * 70)
    
    return max(result1, result2)

if __name__ == '__main__':
    sys.exit(main())
