#!/usr/bin/env python3
"""
Demo script to test the improved Docker detection dialogs.
This simulates different Docker error conditions to verify the UI shows appropriate messages.
"""

import tkinter as tk
from tkinter import messagebox
import platform


def create_test_window():
    """Create a test window to demonstrate Docker error detection"""
    root = tk.Tk()
    root.title("Docker Detection Test - Error Scenarios")
    root.geometry("800x600")
    
    # Header
    header = tk.Frame(root, bg="#2c3e50", height=80)
    header.pack(fill='x')
    header.pack_propagate(False)
    
    tk.Label(
        header,
        text="🐳 Docker Detection Error Scenario Demo",
        font=("Arial", 18, "bold"),
        bg="#2c3e50",
        fg="white"
    ).pack(pady=25)
    
    # Content area
    content = tk.Frame(root, bg="#ecf0f1")
    content.pack(fill='both', expand=True, padx=20, pady=20)
    
    tk.Label(
        content,
        text="This demo shows the different error messages users will see\nfor various Docker detection scenarios:",
        font=("Arial", 12),
        bg="#ecf0f1",
        justify='left'
    ).pack(pady=10)
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Docker Running (Success)',
            'status': 'running',
            'message': 'Docker is running',
            'action': None,
            'color': '#27ae60'
        },
        {
            'name': 'Docker Not Installed',
            'status': 'not_installed',
            'message': 'Docker is not installed or not found in system PATH',
            'action': get_not_installed_action(),
            'color': '#e67e22'
        },
        {
            'name': 'Docker Not Running',
            'status': 'not_running',
            'message': 'Docker is not running',
            'action': get_not_running_action(),
            'color': '#e74c3c'
        },
        {
            'name': 'Permission Denied',
            'status': 'permission_denied',
            'message': 'Permission denied - insufficient privileges to access Docker',
            'action': get_permission_denied_action(),
            'color': '#c0392b'
        },
        {
            'name': 'Timeout/Unknown Error',
            'status': 'error',
            'message': 'Docker command timed out',
            'action': 'Docker is starting up - wait a moment and try again',
            'color': '#95a5a6'
        }
    ]
    
    for scenario in scenarios:
        create_scenario_button(content, scenario, root)
    
    # Instructions
    tk.Label(
        content,
        text="\nClick on any scenario to see how the error dialog will appear to users.",
        font=("Arial", 10, "italic"),
        bg="#ecf0f1",
        fg="#7f8c8d"
    ).pack(pady=10)
    
    root.mainloop()


def get_not_installed_action():
    """Get platform-specific installation instructions"""
    system = platform.system()
    if system == 'Windows':
        return (
            "Docker Desktop is not installed or not in your system PATH.\n\n"
            "To install Docker Desktop:\n"
            "1. Visit https://www.docker.com/products/docker-desktop/\n"
            "2. Download Docker Desktop for Windows\n"
            "3. Run the installer and follow the instructions\n"
            "4. Restart your computer after installation\n"
            "5. Launch Docker Desktop and wait for it to start"
        )
    elif system == 'Darwin':
        return (
            "Docker Desktop is not installed or not in your system PATH.\n\n"
            "To install Docker Desktop:\n"
            "1. Visit https://www.docker.com/products/docker-desktop/\n"
            "2. Download Docker Desktop for Mac\n"
            "3. Open the .dmg file and drag Docker to Applications\n"
            "4. Launch Docker Desktop from Applications\n"
            "5. Complete the first-time setup"
        )
    else:
        return (
            "Docker is not installed or not in your system PATH.\n\n"
            "To install Docker on Linux:\n"
            "  # Ubuntu/Debian:\n"
            "  sudo apt-get update\n"
            "  sudo apt-get install docker.io\n\n"
            "  # Fedora/RHEL:\n"
            "  sudo dnf install docker\n\n"
            "After installation, start Docker:\n"
            "  sudo systemctl start docker\n"
            "  sudo systemctl enable docker"
        )


def get_not_running_action():
    """Get platform-specific Docker start instructions"""
    system = platform.system()
    if system == 'Windows':
        return (
            "Start Docker Desktop:\n"
            "1. Open Docker Desktop from the Start menu\n"
            "2. Wait for Docker to fully start (watch the system tray icon)\n"
            "3. Try again once Docker is running"
        )
    elif system == 'Darwin':
        return (
            "Start Docker Desktop:\n"
            "1. Open Docker Desktop from Applications\n"
            "2. Wait for Docker to fully start (check menu bar icon)\n"
            "3. Try again once Docker is running"
        )
    else:
        return (
            "Start the Docker daemon:\n"
            "  sudo systemctl start docker\n\n"
            "To enable Docker to start automatically:\n"
            "  sudo systemctl enable docker\n\n"
            "Check Docker status:\n"
            "  sudo systemctl status docker"
        )


def get_permission_denied_action():
    """Get platform-specific permission fix instructions"""
    system = platform.system()
    if system == 'Windows':
        return (
            "Run this application as Administrator:\n"
            "1. Right-click the application\n"
            "2. Select 'Run as Administrator'\n\n"
            "Or ensure Docker Desktop is running and you have proper permissions."
        )
    elif system == 'Linux':
        return (
            "Add your user to the docker group:\n"
            "  sudo usermod -aG docker $USER\n\n"
            "Then log out and log back in for changes to take effect.\n\n"
            "Alternatively, run with sudo (not recommended for GUI apps)."
        )
    else:
        return (
            "Ensure Docker Desktop is running and you have proper permissions.\n"
            "You may need to restart Docker Desktop."
        )


def create_scenario_button(parent, scenario, root):
    """Create a button for each scenario"""
    frame = tk.Frame(parent, bg="#ecf0f1")
    frame.pack(fill='x', pady=5)
    
    btn = tk.Button(
        frame,
        text=f"Test: {scenario['name']}",
        font=("Arial", 11),
        bg=scenario['color'],
        fg='white',
        width=40,
        height=2,
        command=lambda: show_error_dialog(root, scenario)
    )
    btn.pack(pady=2)


def show_error_dialog(parent, scenario):
    """Show the error dialog for the scenario"""
    if scenario['status'] == 'running':
        messagebox.showinfo(
            "Docker Status",
            "✓ Docker is running and ready!\n\nNo errors to show for this scenario.",
            parent=parent
        )
        return
    
    # Create custom dialog
    dialog = tk.Toplevel(parent)
    
    status_titles = {
        'not_installed': 'Docker Not Installed',
        'not_running': 'Docker Not Running',
        'permission_denied': 'Docker Permission Error',
        'error': 'Docker Error'
    }
    
    status_icons = {
        'not_installed': '📦',
        'not_running': '⚠',
        'permission_denied': '🔒',
        'error': '❌'
    }
    
    dialog_title = status_titles.get(scenario['status'], 'Docker Issue')
    header_icon = status_icons.get(scenario['status'], '⚠')
    
    dialog.title(dialog_title)
    dialog.geometry("650x450")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (650 // 2)
    y = (dialog.winfo_screenheight() // 2) - (450 // 2)
    dialog.geometry(f"650x450+{x}+{y}")
    
    # Header
    header_frame = tk.Frame(dialog, bg=scenario['color'], height=60)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    tk.Label(
        header_frame,
        text=f"{header_icon} {dialog_title}",
        font=("Arial", 16, "bold"),
        bg=scenario['color'],
        fg="white"
    ).pack(pady=15)
    
    # Content
    content_frame = tk.Frame(dialog)
    content_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    # Show status message
    tk.Label(
        content_frame,
        text=scenario['message'],
        font=("Arial", 13, "bold"),
        wraplength=590,
        justify="left"
    ).pack(pady=(5, 15))
    
    # Show suggested action in a scrollable text area
    if scenario['action']:
        action_frame = tk.Frame(content_frame, relief="solid", borderwidth=1)
        action_frame.pack(fill="both", expand=True, pady=10)
        
        action_text = tk.Text(
            action_frame,
            font=("Arial", 10),
            wrap="word",
            height=10,
            bg="#f8f9fa",
            relief="flat",
            padx=10,
            pady=10
        )
        action_scrollbar = tk.Scrollbar(action_frame, command=action_text.yview)
        action_text.config(yscrollcommand=action_scrollbar.set)
        
        action_scrollbar.pack(side="right", fill="y")
        action_text.pack(side="left", fill="both", expand=True)
        
        action_text.insert("1.0", scenario['action'])
        action_text.config(state="disabled")
    
    # Buttons
    button_frame = tk.Frame(content_frame)
    button_frame.pack(pady=20)
    
    if scenario['status'] == 'not_installed':
        tk.Button(
            button_frame,
            text="Download Docker",
            font=("Arial", 12),
            command=lambda: messagebox.showinfo("Action", "Would open Docker download page"),
            bg="#e67e22",
            fg="white",
            width=20
        ).pack(side="left", padx=5)
    elif scenario['status'] == 'not_running':
        tk.Button(
            button_frame,
            text="Start Docker Desktop",
            font=("Arial", 12),
            command=lambda: messagebox.showinfo("Action", "Would attempt to start Docker"),
            bg="#3daee9",
            fg="white",
            width=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Retry",
            font=("Arial", 12),
            command=lambda: messagebox.showinfo("Action", "Would retry Docker detection"),
            bg="#27ae60",
            fg="white",
            width=15
        ).pack(side="left", padx=5)
    elif scenario['status'] in ['permission_denied', 'error']:
        tk.Button(
            button_frame,
            text="Retry",
            font=("Arial", 12),
            command=lambda: messagebox.showinfo("Action", "Would retry Docker detection"),
            bg="#27ae60",
            fg="white",
            width=15
        ).pack(side="left", padx=5)
    
    tk.Button(
        button_frame,
        text="Close",
        font=("Arial", 12),
        command=dialog.destroy,
        width=15
    ).pack(side="left", padx=5)


if __name__ == '__main__':
    print("=" * 60)
    print("Docker Detection Error Dialog Demo")
    print("=" * 60)
    print("\nThis demo shows the improved Docker detection dialogs.")
    print("Click on different scenarios to see how errors are presented to users.")
    print("\nNote: These are simulations - no actual Docker commands are run.")
    print("=" * 60)
    
    create_test_window()
