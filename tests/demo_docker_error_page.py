#!/usr/bin/env python3
"""
Visual demonstration of the new Docker error page (not dialog).
Shows how Docker errors are now displayed as a dedicated page within the main GUI.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import analyze_docker_error for generating error info
from pathlib import Path
import platform
import tempfile

# Mock constants that would normally be imported
DOCKER_ERROR_LOG_PATH = Path(tempfile.gettempdir()) / 'nextcloud_docker_errors.log'

# Simplified theme colors
THEMES = {
    'dark': {
        'bg': '#1e1e1e',
        'fg': '#e0e0e0',
        'header_bg': '#2d2d2d',
        'header_fg': '#ffffff',
        'button_bg': '#2d2d2d',
        'button_fg': '#e0e0e0',
        'entry_bg': '#2d2d2d',
        'entry_fg': '#e0e0e0',
        'info_bg': '#2d3e50',
        'info_fg': '#ecf0f1',
        'hint_fg': '#95a5a6'
    }
}


class DockerErrorPageDemo(tk.Tk):
    """Demonstration of the new Docker error page feature"""
    
    def __init__(self):
        super().__init__()
        self.title("Docker Error Page Demo - Nextcloud Restore GUI")
        self.geometry("900x900")
        
        # Theme setup
        self.current_theme = 'dark'
        self.theme_colors = THEMES[self.current_theme]
        self.configure(bg=self.theme_colors['bg'])
        
        # Header
        header = tk.Frame(self, bg=self.theme_colors['header_bg'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Nextcloud Restore & Backup Utility",
            font=("Arial", 22, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(pady=25)
        
        # Body frame (where error page will be shown)
        self.body_frame = tk.Frame(self, bg=self.theme_colors['bg'])
        self.body_frame.pack(fill='both', expand=True)
        
        self.current_page = 'menu'
        
        self.show_demo_menu()
    
    def show_demo_menu(self):
        """Show demo menu with different error scenarios"""
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        self.current_page = 'menu'
        
        menu_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        menu_frame.pack(fill='both', expand=True, pady=40, padx=40)
        
        # Title
        tk.Label(
            menu_frame,
            text="Docker Error Page Demonstration",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        tk.Label(
            menu_frame,
            text="Select an error scenario to see how it's displayed as a page:",
            font=("Arial", 12),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=10)
        
        # Error scenario buttons
        scenarios = [
            ("Port Conflict Error", self.show_port_conflict_error),
            ("Container Name Conflict", self.show_name_conflict_error),
            ("Docker Not Running", self.show_docker_not_running_error),
            ("Image Not Found", self.show_image_not_found_error),
        ]
        
        for label, command in scenarios:
            tk.Button(
                menu_frame,
                text=label,
                font=("Arial", 14),
                bg=self.theme_colors['button_bg'],
                fg=self.theme_colors['button_fg'],
                width=30,
                height=2,
                command=command
            ).pack(pady=8)
    
    def show_port_conflict_error(self):
        """Show port conflict error page"""
        error_info = {
            'error_type': 'port_conflict',
            'user_message': 'Port 8080 is already in use by another application or container.',
            'suggested_action': (
                'Try one of these alternative ports: 8081, 8082, 8090\n\n'
                'Or stop the application/container using the port:\n'
                '  docker ps (to see running containers)\n'
                '  docker stop <container-name> (to stop conflicting container)'
            ),
            'alternative_port': 8081,
            'is_recoverable': True
        }
        
        stderr_output = (
            'docker: Error response from daemon: driver failed programming external connectivity '
            'on endpoint nextcloud-app: Bind for 0.0.0.0:8080 failed: port is already allocated.\n'
            'ERRO[0000] error waiting for container: context canceled'
        )
        
        self.show_docker_error_page(error_info, stderr_output, 'nextcloud-app', '8080')
    
    def show_name_conflict_error(self):
        """Show container name conflict error page"""
        error_info = {
            'error_type': 'container_name_conflict',
            'user_message': "A container with name 'nextcloud-app' already exists.",
            'suggested_action': (
                'Remove the existing container or choose a different name:\n'
                '  docker rm nextcloud-app (to remove the container)\n'
                '  docker rm -f nextcloud-app (to force remove if running)\n\n'
                'Or choose a different container name in the restore wizard.'
            ),
            'alternative_port': None,
            'is_recoverable': True
        }
        
        stderr_output = (
            'docker: Error response from daemon: Conflict. The container name "/nextcloud-app" '
            'is already in use by container "a3f5c8d2e1b94f7c6a9b8d5e2f1c3a4b".\n'
            'You have to remove (or rename) that container to be able to reuse that name.'
        )
        
        self.show_docker_error_page(error_info, stderr_output, 'nextcloud-app', '8080')
    
    def show_docker_not_running_error(self):
        """Show Docker not running error page"""
        error_info = {
            'error_type': 'docker_not_running',
            'user_message': 'Docker daemon is not running or not accessible.',
            'suggested_action': (
                'Start Docker:\n'
                '  - Windows/Mac: Open Docker Desktop\n'
                '  - Linux: sudo systemctl start docker\n\n'
                'Then retry the restore.'
            ),
            'alternative_port': None,
            'is_recoverable': True
        }
        
        stderr_output = (
            'Cannot connect to the Docker daemon at unix:///var/run/docker.sock. '
            'Is the docker daemon running?'
        )
        
        self.show_docker_error_page(error_info, stderr_output, 'nextcloud-app', '8080')
    
    def show_image_not_found_error(self):
        """Show image not found error page"""
        error_info = {
            'error_type': 'image_not_found',
            'user_message': 'The required Docker image could not be found.',
            'suggested_action': (
                'The image may need to be downloaded. Try:\n'
                '1. Check your internet connection\n'
                '2. Manually pull the image: docker pull nextcloud\n'
                '3. Restart the restore process'
            ),
            'alternative_port': None,
            'is_recoverable': True
        }
        
        stderr_output = (
            'Unable to find image \'nextcloud:latest\' locally\n'
            'docker: Error response from daemon: manifest for nextcloud:latest not found: '
            'manifest unknown: manifest unknown'
        )
        
        self.show_docker_error_page(error_info, stderr_output, 'nextcloud:latest (image)', 'N/A')
    
    def show_docker_error_page(self, error_info, stderr_output, container_name, port):
        """
        Show Docker error as a dedicated page within the main GUI (not a popup dialog).
        This is the actual implementation from the main application.
        """
        # Store error information
        self.current_docker_error = {
            'error_info': error_info,
            'stderr': stderr_output,
            'container_name': container_name,
            'port': port
        }
        
        # Clear the body frame and show error page
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        # Update current page tracking
        self.current_page = 'docker_error'
        
        # Main error container with scrolling
        main_container = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        main_container.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(main_container, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, command=canvas.yview)
        error_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        error_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=error_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header with error icon
        header_frame = tk.Frame(error_frame, bg='#d32f2f', height=100)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="❌ Docker Container Failed",
            font=("Arial", 22, "bold"),
            bg='#d32f2f',
            fg='white'
        ).pack(pady=30)
        
        # Content container with padding
        content_container = tk.Frame(error_frame, bg=self.theme_colors['bg'])
        content_container.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Error type label
        tk.Label(
            content_container,
            text=f"Error Type: {error_info['error_type'].replace('_', ' ').title()}",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(0, 15), anchor='w')
        
        # Container info frame
        info_frame = tk.Frame(content_container, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=2)
        info_frame.pack(fill='x', pady=10)
        
        port_text = port if port else "N/A"
        tk.Label(
            info_frame,
            text=f"Container: {container_name}  |  Port: {port_text}",
            font=("Arial", 11),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=10)
        
        # Error message frame
        error_msg_frame = tk.Frame(content_container, bg='#ffebee', relief="solid", borderwidth=2)
        error_msg_frame.pack(fill='x', pady=15)
        
        tk.Label(
            error_msg_frame,
            text="❌ Error Description",
            font=("Arial", 12, "bold"),
            bg='#ffebee',
            fg='#c62828'
        ).pack(pady=(10, 5), padx=15, anchor='w')
        
        tk.Label(
            error_msg_frame,
            text=error_info['user_message'],
            font=("Arial", 11),
            bg='#ffebee',
            fg='#b71c1c',
            wraplength=780,
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor='w')
        
        # Suggested action frame
        action_frame = tk.Frame(content_container, bg='#e8f5e9', relief="solid", borderwidth=2)
        action_frame.pack(fill='x', pady=15)
        
        tk.Label(
            action_frame,
            text="💡 Suggested Action",
            font=("Arial", 12, "bold"),
            bg='#e8f5e9',
            fg='#2e7d32'
        ).pack(pady=(10, 5), padx=15, anchor='w')
        
        tk.Label(
            action_frame,
            text=error_info['suggested_action'],
            font=("Arial", 10),
            bg='#e8f5e9',
            fg='#1b5e20',
            wraplength=780,
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor='w')
        
        # Alternative port suggestion (if applicable)
        if error_info.get('alternative_port'):
            port_frame = tk.Frame(content_container, bg='#fff3cd', relief="solid", borderwidth=2)
            port_frame.pack(fill='x', pady=15)
            
            tk.Label(
                port_frame,
                text="🔌 Alternative Port Suggestion",
                font=("Arial", 12, "bold"),
                bg='#fff3cd',
                fg='#856404'
            ).pack(pady=(10, 5), padx=15, anchor='w')
            
            tk.Label(
                port_frame,
                text=f"Try using port {error_info['alternative_port']} instead.",
                font=("Arial", 10),
                bg='#fff3cd',
                fg='#856404',
                wraplength=780,
                justify="left"
            ).pack(pady=(0, 10), padx=15, anchor='w')
        
        # Docker error details section (expandable)
        details_section = tk.Frame(content_container, bg=self.theme_colors['bg'])
        details_section.pack(fill='both', expand=True, pady=15)
        
        tk.Label(
            details_section,
            text="📋 Docker Error Output",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(5, 5), anchor='w')
        
        # Text widget for Docker error output
        text_frame = tk.Frame(details_section)
        text_frame.pack(fill='both', expand=True, pady=5)
        
        text_scrollbar = tk.Scrollbar(text_frame)
        text_scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(
            text_frame,
            wrap="word",
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg'],
            font=("Courier", 9),
            height=10,
            yscrollcommand=text_scrollbar.set
        )
        text_widget.pack(fill="both", expand=True)
        text_scrollbar.config(command=text_widget.yview)
        
        text_widget.insert("1.0", stderr_output)
        text_widget.config(state="disabled")
        
        # Log file location
        tk.Label(
            content_container,
            text=f"📁 Error logged to: {DOCKER_ERROR_LOG_PATH}",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(15, 5), anchor='w')
        
        # Button frame
        button_frame = tk.Frame(content_container, bg=self.theme_colors['bg'])
        button_frame.pack(pady=20)
        
        # Back to Menu button (in demo, this is "Return to Main Menu")
        menu_btn = tk.Button(
            button_frame,
            text="Return to Menu",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=22,
            command=self.show_demo_menu
        )
        menu_btn.pack(side="left", padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def apply_theme_recursive(self, widget):
        """Apply theme to widget and all children"""
        pass  # Simplified for demo


if __name__ == "__main__":
    print("=" * 80)
    print("Docker Error Page Demonstration")
    print("=" * 80)
    print("\nThis demo shows how Docker errors are now displayed as a dedicated page")
    print("within the main GUI instead of popup dialogs.")
    print("\nFeatures demonstrated:")
    print("  • Error page displayed within main GUI (not a popup)")
    print("  • Error type and description")
    print("  • Suggested actions for resolution")
    print("  • Alternative port suggestions (when applicable)")
    print("  • Inline Docker error output")
    print("  • 'Return to Main Menu' button for navigation")
    print("\nLaunching demo GUI...")
    print("=" * 80)
    
    app = DockerErrorPageDemo()
    app.mainloop()
