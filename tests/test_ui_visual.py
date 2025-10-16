#!/usr/bin/env python3
"""
Visual test for UI centering enhancement.
This script will launch the application to allow visual verification.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main application
from nextcloud_restore_and_backup_v9 import NextcloudRestoreWizard

def main():
    print("="*70)
    print("UI Centering Enhancement - Visual Test")
    print("="*70)
    print("\nLaunching application...")
    print("\nPlease verify the following:")
    print("  1. Window opens at 900x900 pixels")
    print("  2. Click 'Restore from Backup' to enter the wizard")
    print("  3. Content appears centered and well-spaced")
    print("  4. Input fields are wider and fill more space")
    print("  5. Buttons are larger and well-proportioned")
    print("  6. Padding/spacing looks balanced")
    print("  7. Test on different window sizes (resize the window)")
    print("\n" + "="*70)
    
    try:
        app = NextcloudRestoreWizard()
        app.mainloop()
    except Exception as e:
        print(f"Error launching application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
