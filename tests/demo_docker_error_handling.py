#!/usr/bin/env python3
"""
Visual demonstration of Docker error handling enhancements.
Shows the new Docker error dialogs with detailed error information, suggestions, and log locations.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class DockerErrorHandlingDemo(tk.Tk):
    """Demonstration of the Docker error handling enhancements"""
    
    def __init__(self):
        super().__init__()
        self.title("Docker Error Handling Enhancement Demo")
        self.geometry("1100x850")
        
        # Theme colors (dark mode)
        self.theme_colors = {
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
            'hint_fg': '#95a5a6',
            'button_active_bg': '#3d3d3d'
        }
        
        self.configure(bg=self.theme_colors['bg'])
        
        # Header
        header = tk.Frame(self, bg=self.theme_colors['header_bg'], height=100)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🐳 Docker Error Handling Enhancement Demo",
            font=("Arial", 22, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(pady=30)
        
        # Main content
        self.content_frame = tk.Frame(self, bg=self.theme_colors['bg'])
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.show_menu()
    
    def show_menu(self):
        """Show demo menu"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Introduction
        intro_frame = tk.Frame(self.content_frame, bg=self.theme_colors['info_bg'], relief='solid', borderwidth=2)
        intro_frame.pack(fill='x', pady=15, padx=20)
        
        tk.Label(
            intro_frame,
            text="📋 What's New in Docker Error Handling",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(10, 5))
        
        features = [
            "✅ Detailed error analysis with type detection",
            "✅ Actionable suggestions for each error type",
            "✅ Alternative port suggestions for port conflicts",
            "✅ Dedicated Docker error log file",
            "✅ 'Show Docker Error Details' button for full error information",
            "✅ User-friendly error messages with recovery steps"
        ]
        
        for feature in features:
            tk.Label(
                intro_frame,
                text=feature,
                font=("Arial", 10),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['info_fg'],
                anchor='w'
            ).pack(pady=2, padx=20, anchor='w')
        
        tk.Label(
            intro_frame,
            text="",
            bg=self.theme_colors['info_bg']
        ).pack(pady=5)
        
        tk.Label(
            self.content_frame,
            text="Select an Error Scenario to View:",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        # Demo scenarios
        scenarios = [
            ("Port Conflict Error", self.demo_port_conflict),
            ("Image Not Found Error", self.demo_image_not_found),
            ("Container Name Conflict", self.demo_container_name_conflict),
            ("Network Configuration Error", self.demo_network_error),
            ("Volume Mount Error", self.demo_volume_error),
            ("Docker Not Running Error", self.demo_docker_not_running),
            ("Permission Denied Error", self.demo_permission_error),
            ("Disk Space Error", self.demo_disk_space_error),
        ]
        
        for name, func in scenarios:
            btn = tk.Button(
                self.content_frame,
                text=name,
                font=("Arial", 11),
                bg=self.theme_colors['button_bg'],
                fg=self.theme_colors['button_fg'],
                width=40,
                height=2,
                command=func
            )
            btn.pack(pady=5)
        
        tk.Button(
            self.content_frame,
            text="Exit Demo",
            font=("Arial", 11, "bold"),
            bg='#d32f2f',
            fg='white',
            width=20,
            command=self.quit
        ).pack(pady=20)
    
    def demo_port_conflict(self):
        """Demo: Port conflict error"""
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
        
        stderr = (
            'docker: Error response from daemon: driver failed programming external connectivity '
            'on endpoint nextcloud-app: Bind for 0.0.0.0:8080 failed: port is already allocated.\n'
            'ERRO[0000] error waiting for container: context canceled'
        )
        
        self.show_docker_container_error_dialog(error_info, stderr, "nextcloud-app", 8080)
    
    def demo_image_not_found(self):
        """Demo: Image not found error"""
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
        
        stderr = (
            'Unable to find image \'nextcloud:latest\' locally\n'
            'docker: Error response from daemon: manifest for nextcloud:latest not found: '
            'manifest unknown: manifest unknown.'
        )
        
        self.show_docker_container_error_dialog(error_info, stderr, "nextcloud-app", 8080)
    
    def demo_container_name_conflict(self):
        """Demo: Container name conflict"""
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
        
        stderr = (
            'docker: Error response from daemon: Conflict. The container name "/nextcloud-app" '
            'is already in use by container "a3f5c8d2e1b9". You have to remove (or rename) that '
            'container to be able to reuse that name.\n'
            'See \'docker run --help\'.'
        )
        
        self.show_docker_container_error_dialog(error_info, stderr, "nextcloud-app", 8080)
    
    def demo_network_error(self):
        """Demo: Network configuration error"""
        error_info = {
            'error_type': 'network_error',
            'user_message': 'Docker network configuration error.',
            'suggested_action': (
                'Try creating the default bridge network:\n'
                '  docker network create bridge\n\n'
                'Or restart Docker Desktop/daemon.'
            ),
            'alternative_port': None,
            'is_recoverable': True
        }
        
        stderr = (
            'docker: Error response from daemon: network bridge not found.\n'
            'See \'docker run --help\'.'
        )
        
        self.show_docker_container_error_dialog(error_info, stderr, "nextcloud-app", 8080)
    
    def demo_volume_error(self):
        """Demo: Volume mount error"""
        error_info = {
            'error_type': 'volume_error',
            'user_message': 'Failed to mount volume or directory.',
            'suggested_action': (
                'Check that:\n'
                '1. The directory exists and is accessible\n'
                '2. You have proper permissions\n'
                '3. The path is correct (absolute path required)'
            ),
            'alternative_port': None,
            'is_recoverable': True
        }
        
        stderr = (
            'docker: Error response from daemon: error while creating mount source path '
            '\'/invalid/path/data\': mkdir /invalid/path: permission denied.\n'
            'See \'docker run --help\'.'
        )
        
        self.show_docker_container_error_dialog(error_info, stderr, "nextcloud-app", 8080)
    
    def demo_docker_not_running(self):
        """Demo: Docker daemon not running"""
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
        
        stderr = (
            'Cannot connect to the Docker daemon at unix:///var/run/docker.sock. '
            'Is the docker daemon running?'
        )
        
        self.show_docker_container_error_dialog(error_info, stderr, "nextcloud-app", 8080)
    
    def demo_permission_error(self):
        """Demo: Permission denied"""
        error_info = {
            'error_type': 'permission_error',
            'user_message': 'Permission denied - insufficient privileges to run Docker.',
            'suggested_action': (
                'Run with proper permissions:\n'
                '  - Windows: Run as Administrator\n'
                '  - Linux: Add user to docker group or use sudo\n'
                '    sudo usermod -aG docker $USER\n'
                '    (logout and login again after running this)'
            ),
            'alternative_port': None,
            'is_recoverable': True
        }
        
        stderr = (
            'Got permission denied while trying to connect to the Docker daemon socket at '
            'unix:///var/run/docker.sock: Post "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/create": '
            'dial unix /var/run/docker.sock: connect: permission denied'
        )
        
        self.show_docker_container_error_dialog(error_info, stderr, "nextcloud-app", 8080)
    
    def demo_disk_space_error(self):
        """Demo: Disk space error"""
        error_info = {
            'error_type': 'disk_space_error',
            'user_message': 'Insufficient disk space for Docker operation.',
            'suggested_action': (
                'Free up disk space:\n'
                '  - Remove unused Docker images: docker image prune -a\n'
                '  - Remove stopped containers: docker container prune\n'
                '  - Check available disk space: df -h (Linux) or dir (Windows)'
            ),
            'alternative_port': None,
            'is_recoverable': True
        }
        
        stderr = (
            'docker: Error response from daemon: thin pool has 12345 free data blocks which '
            'is less than minimum required 163840 free data blocks. Create more free space '
            'in thin pool or use dm.min_free_space option to change behavior'
        )
        
        self.show_docker_container_error_dialog(error_info, stderr, "nextcloud-app", 8080)
    
    def show_docker_container_error_dialog(self, error_info, stderr_output, container_name, port):
        """
        Show error dialog when Docker container creation fails.
        Includes "Show Docker Error Details" button.
        """
        # Demo Docker error log path
        docker_error_log_path = Path.home() / 'Documents' / 'NextcloudLogs' / 'nextcloud_docker_errors.log'
        
        # Create a modal dialog
        error_dialog = tk.Toplevel(self)
        error_dialog.title("Docker Container Creation Failed")
        error_dialog.geometry("700x500")
        error_dialog.configure(bg=self.theme_colors['bg'])
        error_dialog.transient(self)
        error_dialog.grab_set()
        
        # Center the dialog
        error_dialog.update_idletasks()
        x = (error_dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (error_dialog.winfo_screenheight() // 2) - (500 // 2)
        error_dialog.geometry(f"+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(error_dialog, bg='#d32f2f', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="❌ Docker Container Failed",
            font=("Arial", 18, "bold"),
            bg='#d32f2f',
            fg='white'
        ).pack(pady=25)
        
        # Content frame
        content_frame = tk.Frame(error_dialog, bg=self.theme_colors['bg'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Error type label
        tk.Label(
            content_frame,
            text=f"Error Type: {error_info['error_type'].replace('_', ' ').title()}",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(0, 10))
        
        # Container info
        info_frame = tk.Frame(content_frame, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(
            info_frame,
            text=f"Container: {container_name}  |  Port: {port}",
            font=("Arial", 10),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=8)
        
        # Error message
        tk.Label(
            content_frame,
            text=error_info['user_message'],
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg='#d32f2f',
            wraplength=640,
            justify="left"
        ).pack(pady=10)
        
        # Suggested action frame
        action_frame = tk.Frame(content_frame, bg='#e8f5e9', relief="solid", borderwidth=1)
        action_frame.pack(fill='x', pady=15)
        
        tk.Label(
            action_frame,
            text="💡 Suggested Action:",
            font=("Arial", 11, "bold"),
            bg='#e8f5e9',
            fg='#2e7d32'
        ).pack(pady=(8, 3), padx=10, anchor='w')
        
        tk.Label(
            action_frame,
            text=error_info['suggested_action'],
            font=("Arial", 9),
            bg='#e8f5e9',
            fg='#1b5e20',
            wraplength=620,
            justify="left"
        ).pack(pady=(0, 8), padx=15, anchor='w')
        
        # Alternative port suggestion (if applicable)
        if error_info.get('alternative_port'):
            port_label = tk.Label(
                content_frame,
                text=f"🔌 Try alternative port: {error_info['alternative_port']}",
                font=("Arial", 10, "bold"),
                bg=self.theme_colors['bg'],
                fg='#f7b32b'
            )
            port_label.pack(pady=5)
        
        # Log location
        tk.Label(
            content_frame,
            text=f"📁 Error logged to: {docker_error_log_path}",
            font=("Arial", 8),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(15, 5))
        
        # Button frame
        button_frame = tk.Frame(content_frame, bg=self.theme_colors['bg'])
        button_frame.pack(pady=15)
        
        # Show Docker Error Details button
        details_btn = tk.Button(
            button_frame,
            text="📋 Show Docker Error Details",
            font=("Arial", 11, "bold"),
            bg="#3daee9",
            fg="white",
            width=25,
            command=lambda: self.show_docker_error_details(error_info, stderr_output)
        )
        details_btn.pack(side="left", padx=5)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=15,
            command=error_dialog.destroy
        )
        close_btn.pack(side="left", padx=5)
    
    def show_docker_error_details(self, error_info, stderr_output):
        """
        Show detailed Docker error information in a popup window with actionable guidance.
        """
        docker_error_log_path = Path.home() / 'Documents' / 'NextcloudLogs' / 'nextcloud_docker_errors.log'
        
        details_window = tk.Toplevel(self)
        details_window.title("Docker Error Details")
        details_window.geometry("900x700")
        details_window.configure(bg=self.theme_colors['bg'])
        
        # Title with error type
        title_frame = tk.Frame(details_window, bg=self.theme_colors['header_bg'])
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text=f"🐳 Docker Error: {error_info['error_type'].replace('_', ' ').title()}",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        )
        title_label.pack(pady=15)
        
        # Main content with scrollbar
        main_frame = tk.Frame(details_window, bg=self.theme_colors['bg'])
        main_frame.pack(expand=True, fill="both", padx=15, pady=5)
        
        canvas = tk.Canvas(main_frame, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # User-friendly error message
        error_msg_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=2)
        error_msg_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            error_msg_frame,
            text="❌ Error Description",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        tk.Label(
            error_msg_frame,
            text=error_info['user_message'],
            font=("Arial", 11),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg'],
            wraplength=820,
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor="w")
        
        # Suggested action
        action_frame = tk.Frame(scrollable_frame, bg='#e8f5e9', relief="solid", borderwidth=2)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            action_frame,
            text="💡 Suggested Action",
            font=("Arial", 12, "bold"),
            bg='#e8f5e9',
            fg='#2e7d32'
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        tk.Label(
            action_frame,
            text=error_info['suggested_action'],
            font=("Arial", 10),
            bg='#e8f5e9',
            fg='#1b5e20',
            wraplength=820,
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor="w")
        
        # Alternative port suggestion (if applicable)
        if error_info.get('alternative_port'):
            port_frame = tk.Frame(scrollable_frame, bg='#fff3cd', relief="solid", borderwidth=2)
            port_frame.pack(fill="x", padx=10, pady=10)
            
            tk.Label(
                port_frame,
                text="🔌 Alternative Port Suggestion",
                font=("Arial", 12, "bold"),
                bg='#fff3cd',
                fg='#856404'
            ).pack(pady=(10, 5), padx=10, anchor="w")
            
            tk.Label(
                port_frame,
                text=f"Try using port {error_info['alternative_port']} instead.",
                font=("Arial", 10),
                bg='#fff3cd',
                fg='#856404',
                wraplength=820,
                justify="left"
            ).pack(pady=(0, 10), padx=15, anchor="w")
        
        # Raw Docker error output
        raw_error_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['bg'])
        raw_error_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(
            raw_error_frame,
            text="📋 Raw Docker Error Output",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(5, 5), anchor="w")
        
        text_frame = tk.Frame(raw_error_frame)
        text_frame.pack(fill="both", expand=True)
        
        text_scrollbar = tk.Scrollbar(text_frame)
        text_scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(
            text_frame,
            wrap="word",
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg'],
            font=("Courier", 9),
            height=8,
            yscrollcommand=text_scrollbar.set
        )
        text_widget.pack(fill="both", expand=True)
        text_scrollbar.config(command=text_widget.yview)
        
        text_widget.insert("1.0", stderr_output)
        text_widget.config(state="disabled")
        
        # Docker error log file location
        log_location_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['bg'])
        log_location_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            log_location_frame,
            text=f"📁 Docker errors are logged to:\n{docker_error_log_path}",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="left"
        ).pack(anchor="w")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button frame at bottom
        button_frame = tk.Frame(details_window, bg=self.theme_colors['bg'])
        button_frame.pack(fill="x", padx=15, pady=15)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 10),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=details_window.destroy
        )
        close_btn.pack(side="right", padx=5)


if __name__ == "__main__":
    print("=" * 80)
    print("Docker Error Handling Enhancement Demo")
    print("=" * 80)
    print("\nThis demo showcases the enhanced Docker error handling features:")
    print("  • Detailed error analysis with type detection")
    print("  • Actionable suggestions for recovery")
    print("  • Alternative port suggestions")
    print("  • Dedicated error log file")
    print("  • 'Show Docker Error Details' dialog")
    print("\nStarting GUI demo...")
    print("=" * 80)
    
    app = DockerErrorHandlingDemo()
    app.mainloop()
