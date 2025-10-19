#!/usr/bin/env python3
"""
Visual demonstration of the beginner-friendly restore workflow enhancements.
This script shows what the new UI looks like without requiring an actual backup.
"""

import tkinter as tk
from tkinter import ttk
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class RestoreWorkflowDemo(tk.Tk):
    """
    Demonstration of the new restore workflow UI.
    Shows the various dialog boxes and progress indicators.
    """
    
    def __init__(self):
        super().__init__()
        self.title("Restore Workflow Enhancement Demo")
        self.geometry("900x800")
        
        # Theme colors (dark mode)
        self.theme_colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'header_bg': '#1e1e1e',
            'header_fg': '#ffffff',
            'button_bg': '#3c3c3c',
            'button_fg': '#ffffff',
            'entry_bg': '#3c3c3c',
            'entry_fg': '#ffffff',
            'info_bg': '#2d3e50',
            'info_fg': '#ecf0f1',
            'hint_fg': '#95a5a6'
        }
        
        self.configure(bg=self.theme_colors['bg'])
        
        # Header
        header = tk.Frame(self, bg=self.theme_colors['header_bg'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Restore Workflow Enhancement Demo",
            font=("Arial", 20, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(pady=20)
        
        # Main content
        self.content_frame = tk.Frame(self, bg=self.theme_colors['bg'])
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.show_menu()
    
    def show_menu(self):
        """Show demo menu"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.content_frame,
            text="Select a Demo to View:",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        demos = [
            ("Enhanced Docker Detection", self.demo_docker_detection),
            ("Wizard Page 1: Quick Restore Mode", self.demo_wizard_page1),
            ("Progress Indicators", self.demo_progress),
            ("Success Dialog with Browser Launch", self.demo_success),
            ("Error Dialog with Suggestions", self.demo_error),
            ("Automated Process Information", self.demo_automated_info)
        ]
        
        for name, func in demos:
            tk.Button(
                self.content_frame,
                text=name,
                font=("Arial", 12),
                bg=self.theme_colors['button_bg'],
                fg=self.theme_colors['button_fg'],
                width=50,
                height=2,
                command=func
            ).pack(pady=10)
        
        tk.Button(
            self.content_frame,
            text="Exit Demo",
            font=("Arial", 12),
            bg="#d32f2f",
            fg="white",
            width=50,
            height=2,
            command=self.quit
        ).pack(pady=20)
    
    def demo_docker_detection(self):
        """Demo Docker detection dialog"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.content_frame, bg=self.theme_colors['bg'])
        frame.pack(expand=True)
        
        tk.Label(
            frame,
            text="🐳 Docker Detection",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        # Detection message
        msg_frame = tk.Frame(frame, bg=self.theme_colors['info_bg'], relief='solid', borderwidth=2)
        msg_frame.pack(pady=20, padx=40, fill='x')
        
        tk.Label(
            msg_frame,
            text="⚠️ Docker Not Found",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['info_bg'],
            fg="#f7b32b"
        ).pack(pady=(15, 5))
        
        tk.Label(
            msg_frame,
            text="Docker is required for restore operations.\n\n"
                 "The application needs Docker to create and manage\n"
                 "containers for your Nextcloud instance.",
            font=("Arial", 11),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg'],
            justify='center'
        ).pack(pady=10)
        
        tk.Label(
            msg_frame,
            text="What would you like to do?",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(10, 5))
        
        # Buttons
        btn_frame = tk.Frame(msg_frame, bg=self.theme_colors['info_bg'])
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="📥 Install Docker",
            font=("Arial", 11),
            bg="#3daee9",
            fg="white",
            width=20,
            height=2
        ).pack(side='left', padx=10)
        
        tk.Button(
            btn_frame,
            text="🔄 I Installed It, Retry",
            font=("Arial", 11),
            bg="#45bf55",
            fg="white",
            width=20,
            height=2
        ).pack(side='left', padx=10)
        
        tk.Label(msg_frame, text="", bg=self.theme_colors['info_bg']).pack(pady=5)
        
        tk.Button(
            frame,
            text="← Back to Menu",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_menu
        ).pack(pady=20)
    
    def demo_wizard_page1(self):
        """Demo wizard page 1 with quick restore info"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Scrollable frame
        canvas = tk.Canvas(self.content_frame, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Page title
        tk.Label(
            scrollable_frame,
            text="Restore Wizard: Page 1 of 3",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=10, padx=40, fill='x')
        
        # Quick Restore Mode info
        info_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['info_bg'], relief='solid', borderwidth=1)
        info_frame.pack(pady=15, fill='x', padx=40)
        
        tk.Label(
            info_frame,
            text="ℹ️ Quick Restore Mode",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(8, 3), padx=10, fill='x')
        
        tk.Label(
            info_frame,
            text="This wizard will guide you through the restore process step-by-step.\n"
                 "All Docker commands and configuration will be handled automatically.",
            font=("Arial", 9),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg'],
            wraplength=500,
            justify='center'
        ).pack(pady=(0, 8), padx=10, fill='x')
        
        # Step 1
        tk.Label(
            scrollable_frame,
            text="Step 1: Select Backup Archive",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(20, 5), padx=40, fill='x')
        
        tk.Label(
            scrollable_frame,
            text="Choose the backup file to restore (.tar.gz.gpg or .tar.gz)",
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(0, 5), padx=40, fill='x')
        
        tk.Entry(
            scrollable_frame,
            font=("Arial", 11),
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg']
        ).pack(pady=5, padx=40, fill='x')
        
        tk.Label(
            scrollable_frame,
            text="💡 Tip: Default backup location is usually in Documents/NextcloudBackups",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(0, 5), padx=40, fill='x')
        
        tk.Button(
            scrollable_frame,
            text="Browse...",
            font=("Arial", 11),
            width=20,
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg']
        ).pack(pady=5, padx=40, fill='x')
        
        # Step 2
        tk.Label(
            scrollable_frame,
            text="Step 2: Decryption Password",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(30, 5), padx=40, fill='x')
        
        tk.Label(
            scrollable_frame,
            text="Enter password if backup is encrypted (.gpg)",
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(0, 5), padx=40, fill='x')
        
        tk.Entry(
            scrollable_frame,
            show="*",
            font=("Arial", 12),
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg']
        ).pack(pady=5, padx=40, fill='x')
        
        # Navigation
        nav_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['bg'])
        nav_frame.pack(pady=30, padx=40, fill='x')
        
        tk.Button(
            nav_frame,
            text="← Back to Menu",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_menu
        ).pack(side='left', padx=10)
        
        tk.Button(
            nav_frame,
            text="Next →",
            font=("Arial", 12, "bold"),
            bg="#3daee9",
            fg="white",
            width=15
        ).pack(side='left', padx=10)
    
    def demo_progress(self):
        """Demo progress indicators"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.content_frame, bg=self.theme_colors['bg'])
        frame.pack(expand=True)
        
        tk.Label(
            frame,
            text="📊 Restore Progress",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        # Progress bar
        progress = ttk.Progressbar(frame, length=600, mode='determinate', maximum=100)
        progress.pack(pady=20)
        progress['value'] = 75
        
        tk.Label(
            frame,
            text="75%",
            font=("Arial", 13),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack()
        
        # Step labels
        steps_frame = tk.Frame(frame, bg=self.theme_colors['bg'])
        steps_frame.pack(pady=30)
        
        steps = [
            ("✓", "Decrypting/extracting backup", "#45bf55"),
            ("✓", "Generating Docker configuration", "#45bf55"),
            ("✓", "Setting up containers", "#45bf55"),
            ("⏳", "Copying files into container", "#3daee9"),
            ("", "Restoring database", "#95a5a6"),
            ("", "Setting permissions", "#95a5a6"),
            ("", "Restore complete!", "#95a5a6")
        ]
        
        for icon, text, color in steps:
            step_frame = tk.Frame(steps_frame, bg=self.theme_colors['bg'])
            step_frame.pack(anchor='w', pady=3)
            
            tk.Label(
                step_frame,
                text=f"{icon} {text}" if icon else f"   {text}",
                font=("Arial", 11),
                bg=self.theme_colors['bg'],
                fg=color,
                anchor='w'
            ).pack(side='left')
        
        # Current operation
        tk.Label(
            frame,
            text="Current operation:",
            font=("Arial", 10, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(30, 5))
        
        tk.Label(
            frame,
            text="Copying config folder to container...",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack()
        
        tk.Button(
            frame,
            text="← Back to Menu",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_menu
        ).pack(pady=30)
    
    def demo_success(self):
        """Demo success dialog"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.content_frame, bg=self.theme_colors['bg'])
        frame.pack(expand=True)
        
        tk.Label(
            frame,
            text="✅ Restore Complete!",
            font=("Arial", 24, "bold"),
            bg=self.theme_colors['bg'],
            fg="#45bf55"
        ).pack(pady=20)
        
        tk.Label(
            frame,
            text="Your Nextcloud instance has been successfully restored from backup.",
            font=("Arial", 14),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=10)
        
        tk.Label(
            frame,
            text="Container: nextcloud-app\nPort: 9000",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(frame, bg=self.theme_colors['bg'])
        button_frame.pack(pady=30)
        
        tk.Button(
            button_frame,
            text="🌐 Open Nextcloud in Browser",
            font=("Arial", 14, "bold"),
            bg="#3daee9",
            fg="white",
            width=30,
            height=2
        ).pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Return to Main Menu",
            font=("Arial", 12),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=30,
            command=self.show_menu
        ).pack(pady=10)
    
    def demo_error(self):
        """Demo error dialog"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Scrollable
        canvas = tk.Canvas(self.content_frame, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(
            scrollable_frame,
            text="❌ Restore Failed",
            font=("Arial", 24, "bold"),
            bg=self.theme_colors['bg'],
            fg="#d32f2f"
        ).pack(pady=20)
        
        tk.Label(
            scrollable_frame,
            text="Error: Docker daemon is not running",
            font=("Arial", 12),
            bg=self.theme_colors['bg'],
            fg="#d32f2f",
            wraplength=600
        ).pack(pady=10, padx=40)
        
        # Suggestions
        suggestions_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['info_bg'], relief='solid', borderwidth=1)
        suggestions_frame.pack(pady=20, fill='x', padx=40)
        
        tk.Label(
            suggestions_frame,
            text="💡 Suggested Actions",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(10, 5))
        
        suggestions = [
            "Ensure Docker is installed and running on your system",
            "Try starting Docker Desktop manually",
            "Check Docker service status: 'docker ps' in terminal",
            "Restart Docker Desktop and try again"
        ]
        
        for suggestion in suggestions:
            tk.Label(
                suggestions_frame,
                text=f"• {suggestion}",
                font=("Arial", 10),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['info_fg'],
                wraplength=550,
                justify='left',
                anchor='w'
            ).pack(pady=2, padx=20, anchor='w')
        
        tk.Label(suggestions_frame, text="", bg=self.theme_colors['info_bg']).pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['bg'])
        button_frame.pack(pady=30)
        
        tk.Button(
            button_frame,
            text="📋 View Logs",
            font=("Arial", 12),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=20
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="🔄 Try Again",
            font=("Arial", 12),
            bg="#f7b32b",
            fg="white",
            width=20
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="← Back to Menu",
            font=("Arial", 12),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=20,
            command=self.show_menu
        ).pack(side='left', padx=10)
    
    def demo_automated_info(self):
        """Demo automated process information"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        frame = tk.Frame(self.content_frame, bg=self.theme_colors['bg'])
        frame.pack(expand=True, fill='both', padx=40)
        
        tk.Label(
            frame,
            text="Step 5: Container Configuration",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        # Automated process info
        info_frame = tk.Frame(frame, bg=self.theme_colors['info_bg'], relief='solid', borderwidth=1)
        info_frame.pack(pady=20, fill='both', expand=True)
        
        tk.Label(
            info_frame,
            text="🔧 Automated Restore Process",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(10, 8))
        
        tk.Label(
            info_frame,
            text="When you click 'Start Restore', the following will happen automatically:",
            font=("Arial", 10),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(0, 10))
        
        steps = [
            "✓ Generate Docker Compose YAML configuration",
            "✓ Create required Docker volumes and networks",
            "✓ Extract and decrypt your backup files",
            "✓ Start database and Nextcloud containers",
            "✓ Copy all files to the container (/var/www/html)",
            "✓ Restore database from backup",
            "✓ Update configuration files automatically",
            "✓ Set proper file permissions",
            "✓ Restart services and validate installation"
        ]
        
        for step in steps:
            tk.Label(
                info_frame,
                text=step,
                font=("Arial", 9),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['info_fg'],
                anchor='w'
            ).pack(anchor='w', pady=1, padx=30)
        
        tk.Label(
            info_frame,
            text="No manual Docker commands or YAML editing required!",
            font=("Arial", 10, "bold"),
            bg=self.theme_colors['info_bg'],
            fg="#45bf55"
        ).pack(pady=(10, 15))
        
        tk.Button(
            frame,
            text="← Back to Menu",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_menu
        ).pack(pady=20)

if __name__ == "__main__":
    app = RestoreWorkflowDemo()
    app.mainloop()
