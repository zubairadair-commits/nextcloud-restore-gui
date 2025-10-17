#!/usr/bin/env python3
"""
Visual demo of the extraction error dialog.

This creates a minimal standalone version of the error dialog
to show how it looks to the user.
"""

try:
    import tkinter as tk
    from tkinter import messagebox
    import webbrowser
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
    
import platform
import os


def show_demo_error_dialog():
    """Show a demo version of the extraction error dialog."""
    
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Create the error dialog
    win = tk.Toplevel(root)
    win.title("Extraction Tool Required")
    win.geometry("550x400")
    win.configure(bg='white')
    
    # Main message frame
    msg_frame = tk.Frame(win, bg='white')
    msg_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        msg_frame,
        text="⚠️ Cannot Extract Backup Archive",
        font=("Arial", 14, "bold"),
        bg='white',
        fg='#d32f2f'
    )
    title_label.pack(pady=(0, 15))
    
    # Tool information
    tool_name = "GPG (GNU Privacy Guard)"
    explanation = (
        "Your backup file is encrypted (.gpg extension), but GPG is not installed.\n\n"
        "GPG is required to decrypt encrypted backup archives.\n\n"
        "Without GPG, the restore wizard cannot access the backup contents."
    )
    
    # Explanation
    msg_label = tk.Label(
        msg_frame,
        text=f"Required Tool: {tool_name}\n\n{explanation}",
        font=("Arial", 10),
        bg='white',
        justify="left",
        wraplength=500
    )
    msg_label.pack(pady=(0, 15), anchor="w")
    
    # Backup file info
    backup_info = tk.Label(
        msg_frame,
        text="Backup File: nextcloud_backup_20241017.tar.gz.gpg",
        font=("Arial", 9),
        bg='#f5f5f5',
        fg='#666',
        anchor="w",
        padx=10,
        pady=5
    )
    backup_info.pack(fill="x", pady=(0, 15))
    
    # Installation instructions
    install_instructions = (
        "📥 Installation Options:\n\n"
        "• Click 'Install GPG' to download Gpg4win (Windows)\n"
        "• Linux users: Run 'sudo apt install gpg' (Ubuntu/Debian)\n"
        "  or 'sudo yum install gnupg2' (RHEL/CentOS)\n"
        "• Mac users: Run 'brew install gnupg'"
    )
    
    instructions_label = tk.Label(
        msg_frame,
        text=install_instructions,
        font=("Arial", 9),
        bg='#e3f2fd',
        fg='#1565c0',
        justify="left",
        wraplength=500,
        padx=10,
        pady=10
    )
    instructions_label.pack(fill="x", pady=(0, 20))
    
    # Buttons frame
    btn_frame = tk.Frame(msg_frame, bg='white')
    btn_frame.pack(fill="x")
    
    def on_install():
        print("User clicked 'Install GPG'")
        print("  → Opening browser to download GPG")
        messagebox.showinfo(
            "Installation Started",
            "GPG installer would be opened in your browser.\n\n"
            "In the actual app, this downloads and installs GPG.",
            parent=win
        )
        win.destroy()
        root.quit()
    
    def on_cancel():
        print("User clicked 'Cancel'")
        print("  → User will remain on Page 1")
        print("  → Cannot proceed without GPG for encrypted backups")
        win.destroy()
        root.quit()
    
    # Install button (only on Windows in real app)
    if platform.system() == 'Windows' or True:  # Always show for demo
        install_btn = tk.Button(
            btn_frame,
            text="Install GPG",
            font=("Arial", 11, "bold"),
            bg='#4caf50',
            fg='white',
            width=15,
            command=on_install,
            cursor="hand2"
        )
        install_btn.pack(side="left", padx=5)
    
    cancel_btn = tk.Button(
        btn_frame,
        text="Cancel",
        font=("Arial", 11),
        bg='#f5f5f5',
        fg='#333',
        width=15,
        command=on_cancel,
        cursor="hand2"
    )
    cancel_btn.pack(side="left", padx=5)
    
    # Center the window
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f'+{x}+{y}')
    
    # Add some explanatory text below
    info_label = tk.Label(
        root,
        text="Demo: This shows the error dialog that appears when GPG is not installed",
        font=("Arial", 10, "italic"),
        fg='#666'
    )
    
    print("=" * 70)
    print("Visual Demo: Extraction Error Dialog")
    print("=" * 70)
    print()
    print("Scenario: User selects an encrypted backup (.gpg) but GPG is not installed")
    print()
    print("Dialog shows:")
    print("  • Clear error title and icon")
    print("  • Explanation of what GPG is and why it's needed")
    print("  • The backup filename that couldn't be extracted")
    print("  • Installation instructions for different platforms")
    print("  • 'Install GPG' button to download the installer (Windows)")
    print("  • 'Cancel' button to go back")
    print()
    print("User actions:")
    print("  1. Click 'Install GPG' to download and install")
    print("  2. Click 'Cancel' to go back and select a different backup")
    print()
    
    root.mainloop()


if __name__ == '__main__':
    # Check if we're in a GUI environment
    if not HAS_TKINTER:
        print("Cannot show GUI in this environment (tkinter not available)")
        print()
        print("The error dialog would look like this:")
        print()
        print("┌─────────────────────────────────────────────────────────┐")
        print("│           ⚠️ Cannot Extract Backup Archive             │")
        print("├─────────────────────────────────────────────────────────┤")
        print("│                                                         │")
        print("│ Required Tool: GPG (GNU Privacy Guard)                 │")
        print("│                                                         │")
        print("│ Your backup file is encrypted (.gpg extension), but    │")
        print("│ GPG is not installed.                                  │")
        print("│                                                         │")
        print("│ GPG is required to decrypt encrypted backup archives.  │")
        print("│                                                         │")
        print("│ Without GPG, the restore wizard cannot access the      │")
        print("│ backup contents.                                       │")
        print("│                                                         │")
        print("│ ┌─────────────────────────────────────────────────┐   │")
        print("│ │ Backup File: nextcloud_backup_20241017.tar.gz.gpg   │")
        print("│ └─────────────────────────────────────────────────┘   │")
        print("│                                                         │")
        print("│ 📥 Installation Options:                               │")
        print("│                                                         │")
        print("│ • Click 'Install GPG' to download Gpg4win (Windows)   │")
        print("│ • Linux: Run 'sudo apt install gpg' (Ubuntu/Debian)   │")
        print("│ • Mac: Run 'brew install gnupg'                       │")
        print("│                                                         │")
        print("│    [Install GPG]    [Cancel]                           │")
        print("└─────────────────────────────────────────────────────────┘")
    else:
        try:
            show_demo_error_dialog()
        except Exception as e:
            print("Cannot show GUI in this environment")
            print(f"Error: {e}")
            print()
            print("The error dialog would look like this:")
            print()
            print("┌─────────────────────────────────────────────────────────┐")
            print("│           ⚠️ Cannot Extract Backup Archive             │")
            print("├─────────────────────────────────────────────────────────┤")
            print("│                                                         │")
            print("│ Required Tool: GPG (GNU Privacy Guard)                 │")
            print("│                                                         │")
            print("│ Your backup file is encrypted (.gpg extension), but    │")
            print("│ GPG is not installed.                                  │")
            print("│                                                         │")
            print("│ GPG is required to decrypt encrypted backup archives.  │")
            print("│                                                         │")
            print("│ Without GPG, the restore wizard cannot access the      │")
            print("│ backup contents.                                       │")
            print("│                                                         │")
            print("│ ┌─────────────────────────────────────────────────┐   │")
            print("│ │ Backup File: nextcloud_backup_20241017.tar.gz.gpg   │")
            print("│ └─────────────────────────────────────────────────┘   │")
            print("│                                                         │")
            print("│ 📥 Installation Options:                               │")
            print("│                                                         │")
            print("│ • Click 'Install GPG' to download Gpg4win (Windows)   │")
            print("│ • Linux: Run 'sudo apt install gpg' (Ubuntu/Debian)   │")
            print("│ • Mac: Run 'brew install gnupg'                       │")
            print("│                                                         │")
            print("│    [Install GPG]    [Cancel]                           │")
            print("└─────────────────────────────────────────────────────────┘")
