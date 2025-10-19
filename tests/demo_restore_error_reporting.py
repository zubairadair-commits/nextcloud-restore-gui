#!/usr/bin/env python3
"""
Visual demonstration of restore error reporting enhancements.
Shows the new error dialog with log file location and "Show Logs" button.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Demo log file path
DEMO_LOG_PATH = Path.home() / 'Documents' / 'NextcloudLogs' / 'nextcloud_restore_gui.log'

class RestoreErrorReportingDemo(tk.Tk):
    """Demonstration of the restore error reporting enhancements"""
    
    def __init__(self):
        super().__init__()
        self.title("Restore Error Reporting Enhancement Demo")
        self.geometry("1000x800")
        
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
            'hint_fg': '#95a5a6',
            'button_active_bg': '#4a4a4a'
        }
        
        self.configure(bg=self.theme_colors['bg'])
        
        # Header
        header = tk.Frame(self, bg=self.theme_colors['header_bg'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Restore Error Reporting Enhancement Demo",
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
            text="Select a Demo Feature to View:",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        demos = [
            ("Enhanced Error Dialog with Log Location", self.demo_error_dialog),
            ("Settings Dialog with Verbose Logging", self.demo_settings),
            ("Log Viewer with Troubleshooting Tips", self.demo_log_viewer_empty),
            ("Log Viewer with Logs", self.demo_log_viewer_with_logs),
            ("Restore Error in Action", self.demo_restore_error_flow)
        ]
        
        for name, func in demos:
            btn = tk.Button(
                self.content_frame,
                text=name,
                font=("Arial", 12),
                bg=self.theme_colors['button_bg'],
                fg=self.theme_colors['button_fg'],
                width=50,
                height=2,
                command=func
            )
            btn.pack(pady=10)
        
        tk.Button(
            self.content_frame,
            text="Exit Demo",
            font=("Arial", 12),
            bg="#d32f2f",
            fg="white",
            width=20,
            command=self.quit
        ).pack(pady=20)
    
    def demo_error_dialog(self):
        """Show enhanced error dialog"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        tk.Label(
            self.content_frame,
            text="Enhanced Error Dialog",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        # Description
        desc = tk.Label(
            self.content_frame,
            text="When a restore fails, the error dialog now includes:\n"
                 "• Clear error message\n"
                 "• Actionable suggestions\n"
                 "• Log file location display\n"
                 "• Prominent 'Show Logs' button",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="left"
        )
        desc.pack(pady=10)
        
        # Simulated error dialog
        error_frame = tk.Frame(self.content_frame, bg=self.theme_colors['bg'])
        error_frame.pack(expand=True, fill="both", pady=20, padx=40)
        
        # Error icon and message
        error_label = tk.Label(
            error_frame,
            text="❌ Restore Failed",
            font=("Arial", 24, "bold"),
            bg=self.theme_colors['bg'],
            fg="#d32f2f"
        )
        error_label.pack(pady=20)
        
        # Error message
        error_text = tk.Label(
            error_frame,
            text="Error: Failed to connect to Docker daemon. Is Docker running?",
            font=("Arial", 12),
            bg=self.theme_colors['bg'],
            fg="#d32f2f",
            wraplength=600,
            justify="left"
        )
        error_text.pack(pady=10)
        
        # Suggestions frame
        suggestions_frame = tk.Frame(error_frame, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
        suggestions_frame.pack(pady=20, fill="x", padx=20)
        
        suggestions_title = tk.Label(
            suggestions_frame,
            text="💡 Suggested Actions",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        )
        suggestions_title.pack(pady=(10, 5))
        
        suggestions = [
            "Ensure Docker is installed and running on your system",
            "Try starting Docker Desktop manually",
            "Check Docker service status: 'docker ps' in terminal"
        ]
        
        for suggestion in suggestions:
            suggestion_label = tk.Label(
                suggestions_frame,
                text=f"• {suggestion}",
                font=("Arial", 10),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['info_fg'],
                wraplength=550,
                justify="left",
                anchor="w"
            )
            suggestion_label.pack(pady=2, padx=20, anchor="w")
        
        # NEW: Log file location info
        log_info_frame = tk.Frame(error_frame, bg=self.theme_colors['bg'])
        log_info_frame.pack(pady=15, fill="x", padx=20)
        
        log_info_label = tk.Label(
            log_info_frame,
            text=f"📁 Error details saved to:\n{DEMO_LOG_PATH}",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="center"
        )
        log_info_label.pack()
        
        # Button frame
        button_frame = tk.Frame(error_frame, bg=self.theme_colors['bg'])
        button_frame.pack(pady=20)
        
        # NEW: Show Logs button (prominent)
        logs_btn = tk.Button(
            button_frame,
            text="📋 Show Logs",
            font=("Arial", 12, "bold"),
            bg="#3daee9",
            fg="white",
            width=20,
            command=lambda: print("Opening log viewer...")
        )
        logs_btn.pack(side="left", padx=10)
        
        # Try again button
        retry_btn = tk.Button(
            button_frame,
            text="🔄 Try Again",
            font=("Arial", 12),
            bg="#f7b32b",
            fg="white",
            width=20,
            command=lambda: print("Retrying...")
        )
        retry_btn.pack(side="left", padx=10)
        
        # Back button
        tk.Button(
            self.content_frame,
            text="← Back to Menu",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_menu,
            width=20
        ).pack(pady=20)
    
    def demo_settings(self):
        """Show settings dialog with verbose logging"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        tk.Label(
            self.content_frame,
            text="Settings Dialog - Verbose Logging",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        # Description
        desc = tk.Label(
            self.content_frame,
            text="New Settings dialog accessible from the dropdown menu (☰)\n"
                 "Allows enabling verbose logging for detailed diagnostics",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="center"
        )
        desc.pack(pady=10)
        
        # Simulated settings dialog
        settings_frame = tk.Frame(self.content_frame, bg=self.theme_colors['bg'], relief="solid", borderwidth=2)
        settings_frame.pack(pady=30, padx=100)
        
        # Header
        header = tk.Frame(settings_frame, bg=self.theme_colors['header_bg'])
        header.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            header,
            text="⚙️ Settings",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(pady=10)
        
        # Content
        content = tk.Frame(settings_frame, bg=self.theme_colors['bg'])
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Logging settings section
        logging_section = tk.LabelFrame(
            content,
            text="Logging Settings",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            padx=15,
            pady=15
        )
        logging_section.pack(fill="x", pady=(0, 15))
        
        # Verbose logging checkbox
        verbose_var = tk.BooleanVar(value=True)
        
        verbose_check = tk.Checkbutton(
            logging_section,
            text="Enable Verbose Logging",
            variable=verbose_var,
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            selectcolor=self.theme_colors['entry_bg']
        )
        verbose_check.pack(anchor="w", pady=(0, 5))
        
        # Description
        verbose_desc = tk.Label(
            logging_section,
            text="When enabled, the application logs additional detailed information\n"
                 "about all operations. This is useful for diagnosing issues but will\n"
                 "generate larger log files. Recommended for troubleshooting.",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="left",
            wraplength=400
        )
        verbose_desc.pack(anchor="w", padx=20)
        
        # Log location
        log_location = tk.Label(
            logging_section,
            text=f"Log file location:\n{DEMO_LOG_PATH}",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="left"
        )
        log_location.pack(anchor="w", pady=(10, 0))
        
        # Buttons
        btn_frame = tk.Frame(settings_frame, bg=self.theme_colors['bg'])
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        tk.Button(
            btn_frame,
            text="Save Settings",
            font=("Arial", 12),
            bg="#45bf55",
            fg="white",
            width=15,
            command=lambda: print("Settings saved!")
        ).pack(side="right", padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 12),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=15
        ).pack(side="right", padx=5)
        
        # Back button
        tk.Button(
            self.content_frame,
            text="← Back to Menu",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_menu,
            width=20
        ).pack(pady=20)
    
    def demo_log_viewer_empty(self):
        """Show log viewer with no logs (troubleshooting tips)"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        tk.Label(
            self.content_frame,
            text="Log Viewer - No Logs Found",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        # Description
        desc = tk.Label(
            self.content_frame,
            text="When no logs are found, the viewer shows helpful troubleshooting tips",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        )
        desc.pack(pady=10)
        
        # Log viewer frame
        viewer_frame = tk.Frame(self.content_frame, bg=self.theme_colors['bg'], relief="solid", borderwidth=2)
        viewer_frame.pack(fill="both", expand=True, pady=20, padx=40)
        
        # Header
        header = tk.Frame(viewer_frame, bg=self.theme_colors['header_bg'])
        header.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            header,
            text="Application Logs",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(side="left", padx=10)
        
        tk.Label(
            header,
            text=f"Log file: {DEMO_LOG_PATH}",
            font=("Arial", 9),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(side="left", padx=10)
        
        # Log content with troubleshooting tips
        text_frame = tk.Frame(viewer_frame, bg=self.theme_colors['bg'])
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        log_text = tk.Text(
            text_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['fg'],
            font=("Courier", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=log_text.yview)
        
        # Insert troubleshooting message
        troubleshooting_msg = """No log entries found.

Troubleshooting Tips:

1. If you just started the application, there may not be any logs yet.
   
2. If you experienced an error, try reproducing the issue - the logs will 
   capture the details automatically.
   
3. The application logs all operations to help diagnose issues:
   - Backup operations
   - Restore operations
   - Docker interactions
   - Configuration changes
   
4. If you need more detailed logs, enable Verbose Logging in Settings.

5. Log files are rotated automatically (max 10MB per file, 5 backup files).

Location: """ + str(DEMO_LOG_PATH)
        
        log_text.insert("1.0", troubleshooting_msg)
        log_text.config(state="disabled")
        
        # Back button
        tk.Button(
            self.content_frame,
            text="← Back to Menu",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_menu,
            width=20
        ).pack(pady=20)
    
    def demo_log_viewer_with_logs(self):
        """Show log viewer with sample logs"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        tk.Label(
            self.content_frame,
            text="Log Viewer - With Logs",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        # Description
        desc = tk.Label(
            self.content_frame,
            text="Sample restore error logs showing detailed information",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        )
        desc.pack(pady=10)
        
        # Log viewer frame
        viewer_frame = tk.Frame(self.content_frame, bg=self.theme_colors['bg'], relief="solid", borderwidth=2)
        viewer_frame.pack(fill="both", expand=True, pady=20, padx=40)
        
        # Header
        header = tk.Frame(viewer_frame, bg=self.theme_colors['header_bg'])
        header.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            header,
            text="Application Logs",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(side="left", padx=10)
        
        # Log content
        text_frame = tk.Frame(viewer_frame, bg=self.theme_colors['bg'])
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        log_text = tk.Text(
            text_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['fg'],
            font=("Courier", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=log_text.yview)
        
        # Sample logs
        sample_logs = """2025-10-19 16:47:53 - INFO - Logging initialized. Log file: ~/Documents/NextcloudLogs/nextcloud_restore_gui.log
2025-10-19 16:48:15 - INFO - ============================================================
2025-10-19 16:48:15 - INFO - RESTORE OPERATION STARTED
2025-10-19 16:48:15 - INFO - Backup Path: /home/user/backups/nextcloud-backup.tar.gz
2025-10-19 16:48:15 - INFO - Has Password: No
2025-10-19 16:48:15 - DEBUG - Container Name: nextcloud-app
2025-10-19 16:48:15 - DEBUG - Container Port: 9000
2025-10-19 16:48:15 - DEBUG - Database Type: pgsql
2025-10-19 16:48:15 - INFO - ============================================================
2025-10-19 16:48:15 - INFO - Step 1/7: Extracting backup...
2025-10-19 16:48:22 - DEBUG - Extraction directory: /tmp/restore_abc123
2025-10-19 16:48:22 - INFO - Step 2/7: Detecting database configuration...
2025-10-19 16:48:23 - INFO - Database type detected: pgsql
2025-10-19 16:48:23 - DEBUG - Database config: {'dbtype': 'pgsql', 'dbname': 'nextcloud', 'dbuser': 'nextcloud'}
2025-10-19 16:48:25 - INFO - Step 3/7: Generating Docker Compose configuration...
2025-10-19 16:48:26 - INFO - Step 4/7: Setting up Docker containers...
2025-10-19 16:48:26 - INFO - Creating PGSQL database container...
2025-10-19 16:48:30 - ERROR - Failed to connect to Docker daemon
2025-10-19 16:48:30 - ERROR - ============================================================
2025-10-19 16:48:30 - ERROR - RESTORE FAILED - Error Details:
2025-10-19 16:48:30 - ERROR - Error Type: ConnectionError
2025-10-19 16:48:30 - ERROR - Error Message: Failed to connect to Docker daemon. Is Docker running?
2025-10-19 16:48:30 - ERROR - Backup Path: /home/user/backups/nextcloud-backup.tar.gz
2025-10-19 16:48:30 - ERROR - Full Traceback:
2025-10-19 16:48:30 - ERROR - Traceback (most recent call last):
2025-10-19 16:48:30 - ERROR -   File "restore.py", line 123, in _restore_auto_thread
2025-10-19 16:48:30 - ERROR -     db_container = self.ensure_db_container()
2025-10-19 16:48:30 - ERROR -   File "restore.py", line 456, in ensure_db_container
2025-10-19 16:48:30 - ERROR -     subprocess.run(['docker', 'run', ...], check=True)
2025-10-19 16:48:30 - ERROR - subprocess.CalledProcessError: Command '['docker', 'run']' returned non-zero exit status 1
2025-10-19 16:48:30 - ERROR - ============================================================"""
        
        log_text.insert("1.0", sample_logs)
        log_text.config(state="disabled")
        
        # Back button
        tk.Button(
            self.content_frame,
            text="← Back to Menu",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_menu,
            width=20
        ).pack(pady=20)
    
    def demo_restore_error_flow(self):
        """Show the complete restore error flow"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        tk.Label(
            self.content_frame,
            text="Complete Restore Error Flow",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=20)
        
        # Flow diagram
        flow_frame = tk.Frame(self.content_frame, bg=self.theme_colors['bg'])
        flow_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        steps = [
            ("1️⃣ Restore Operation Fails", "#d32f2f"),
            ("⬇️", self.theme_colors['fg']),
            ("2️⃣ Error Logged with Full Details", "#f7b32b"),
            ("⬇️", self.theme_colors['fg']),
            ("3️⃣ Error Dialog Shows Summary + Log Location", "#f7b32b"),
            ("⬇️", self.theme_colors['fg']),
            ("4️⃣ User Clicks 'Show Logs' Button", "#3daee9"),
            ("⬇️", self.theme_colors['fg']),
            ("5️⃣ Log Viewer Opens with Details", "#45bf55"),
            ("⬇️", self.theme_colors['fg']),
            ("6️⃣ User Can Troubleshoot and Retry", "#45bf55")
        ]
        
        for step_text, color in steps:
            step_label = tk.Label(
                flow_frame,
                text=step_text,
                font=("Arial", 14, "bold") if "️⃣" in step_text else ("Arial", 18),
                bg=self.theme_colors['bg'],
                fg=color,
                pady=10
            )
            step_label.pack()
        
        # Benefits
        benefits_frame = tk.LabelFrame(
            self.content_frame,
            text="Benefits",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            padx=20,
            pady=15
        )
        benefits_frame.pack(fill="x", padx=40, pady=20)
        
        benefits = [
            "✓ Clear error reporting with actionable suggestions",
            "✓ All errors logged automatically for later review",
            "✓ Log file location always visible on failure",
            "✓ One-click access to detailed logs",
            "✓ Helpful troubleshooting tips when needed",
            "✓ Verbose mode for advanced diagnostics"
        ]
        
        for benefit in benefits:
            tk.Label(
                benefits_frame,
                text=benefit,
                font=("Arial", 11),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['fg'],
                anchor="w",
                justify="left"
            ).pack(anchor="w", pady=3)
        
        # Back button
        tk.Button(
            self.content_frame,
            text="← Back to Menu",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_menu,
            width=20
        ).pack(pady=20)


if __name__ == '__main__':
    app = RestoreErrorReportingDemo()
    app.mainloop()
