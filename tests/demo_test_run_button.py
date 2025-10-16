#!/usr/bin/env python3
"""
Visual demo of Test Run button implementation.
Shows the button placement in both active and inactive schedule states.
"""

import tkinter as tk
from tkinter import ttk


class ToolTip:
    """Tooltip widget for displaying help text."""
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None
        
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
    
    def on_enter(self, event=None):
        """Schedule tooltip to appear after delay"""
        self.after_id = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event=None):
        """Hide tooltip and cancel scheduled appearance"""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.hide_tooltip()
    
    def show_tooltip(self):
        """Display the tooltip window"""
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffcc",
            foreground="#000000",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 9),
            justify=tk.LEFT,
            padx=5,
            pady=3,
            wraplength=300
        )
        label.pack()
    
    def hide_tooltip(self):
        """Hide the tooltip window"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class TestRunButtonDemo(tk.Tk):
    """Demo window showing Test Run button placement."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Test Run Button Demo - Schedule Backup")
        self.geometry("900x700")
        self.configure(bg="#f0f0f0")
        
        # Create notebook for different states
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Active Schedule
        self.create_active_schedule_tab()
        
        # Tab 2: No Schedule
        self.create_no_schedule_tab()
        
        # Tab 3: Test Run Feedback
        self.create_test_run_feedback_tab()
    
    def create_active_schedule_tab(self):
        """Create tab showing active schedule with enabled Test Run button."""
        frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(frame, text="Active Schedule")
        
        # Title
        tk.Label(
            frame,
            text="Schedule Automatic Backups",
            font=("Arial", 18, "bold"),
            bg="#ffffff"
        ).pack(pady=15)
        
        # Current Status section
        status_frame = tk.Frame(frame, bg="#e8f4f8", relief="ridge", borderwidth=2)
        status_frame.pack(pady=10, fill="x", padx=40)
        
        tk.Label(
            status_frame,
            text="Current Status",
            font=("Arial", 14, "bold"),
            bg="#e8f4f8"
        ).pack(pady=5)
        
        status_text = (
            "✓ Scheduled backup is active\n"
            "Frequency: daily\n"
            "Time: 02:00 (UTC-5 Eastern Time)\n"
            "Backup Directory: C:\\Backups\\Nextcloud\n"
            "☁️ Cloud Sync: OneDrive (automatic sync enabled)"
        )
        
        tk.Label(
            status_frame,
            text=status_text,
            font=("Arial", 11),
            bg="#e8f4f8",
            justify=tk.LEFT
        ).pack(pady=5)
        
        # Buttons frame - THIS IS WHERE TEST RUN NOW APPEARS
        btn_frame = tk.Frame(status_frame, bg="#e8f4f8")
        btn_frame.pack(pady=10)
        
        # Test Run button (ENABLED - in Current Status section)
        test_run_btn = tk.Button(
            btn_frame,
            text="🧪 Test Run",
            font=("Arial", 11),
            bg="#3498db",  # Blue background
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        test_run_btn.pack(side="left", padx=5)
        
        ToolTip(test_run_btn,
               "Click to immediately run a backup using the current schedule configuration.\n"
               "This will verify that your scheduled backup is working correctly.")
        
        # Disable Schedule button
        tk.Button(
            btn_frame,
            text="Disable Schedule",
            font=("Arial", 11),
            bg="#f0f0f0",
            padx=10,
            pady=5
        ).pack(side="left", padx=5)
        
        # Delete Schedule button
        tk.Button(
            btn_frame,
            text="Delete Schedule",
            font=("Arial", 11),
            bg="#f0f0f0",
            padx=10,
            pady=5
        ).pack(side="left", padx=5)
        
        # Add explanation
        explanation_frame = tk.Frame(frame, bg="#fffacd", relief="solid", borderwidth=1)
        explanation_frame.pack(pady=20, fill="x", padx=40)
        
        tk.Label(
            explanation_frame,
            text="✨ NEW: Test Run Button",
            font=("Arial", 12, "bold"),
            bg="#fffacd"
        ).pack(pady=5)
        
        explanation_text = (
            "• Positioned in Current Status section (near Disable/Delete)\n"
            "• Enabled when schedule is active\n"
            "• Blue background (#3498db) indicates it's clickable\n"
            "• Tooltip explains its purpose\n"
            "• Uses current schedule configuration when clicked\n"
            "• Shows inline feedback (no pop-ups)"
        )
        
        tk.Label(
            explanation_frame,
            text=explanation_text,
            font=("Arial", 10),
            bg="#fffacd",
            justify=tk.LEFT
        ).pack(pady=5, padx=10)
    
    def create_no_schedule_tab(self):
        """Create tab showing no schedule with disabled Test Run button."""
        frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(frame, text="No Schedule")
        
        # Title
        tk.Label(
            frame,
            text="Schedule Automatic Backups",
            font=("Arial", 18, "bold"),
            bg="#ffffff"
        ).pack(pady=15)
        
        # Current Status section
        status_frame = tk.Frame(frame, bg="#e8f4f8", relief="ridge", borderwidth=2)
        status_frame.pack(pady=10, fill="x", padx=40)
        
        tk.Label(
            status_frame,
            text="Current Status",
            font=("Arial", 14, "bold"),
            bg="#e8f4f8"
        ).pack(pady=5)
        
        tk.Label(
            status_frame,
            text="✗ No scheduled backup configured",
            font=("Arial", 11),
            bg="#e8f4f8",
            fg="#e74c3c"
        ).pack(pady=5)
        
        # Buttons frame with DISABLED Test Run
        btn_frame = tk.Frame(status_frame, bg="#e8f4f8")
        btn_frame.pack(pady=10)
        
        # Test Run button (DISABLED - grayed out)
        test_run_btn = tk.Button(
            btn_frame,
            text="🧪 Test Run",
            font=("Arial", 11),
            bg="#d3d3d3",  # Gray background
            fg="#808080",  # Gray text
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        test_run_btn.pack(side="left", padx=5)
        
        ToolTip(test_run_btn,
               "Test Run is disabled because no backup schedule is configured.\n"
               "Please create a schedule first to enable this feature.")
        
        # Add explanation
        explanation_frame = tk.Frame(frame, bg="#fffacd", relief="solid", borderwidth=1)
        explanation_frame.pack(pady=20, fill="x", padx=40)
        
        tk.Label(
            explanation_frame,
            text="✨ Disabled State",
            font=("Arial", 12, "bold"),
            bg="#fffacd"
        ).pack(pady=5)
        
        explanation_text = (
            "• Test Run button is still visible but disabled\n"
            "• Gray background (#d3d3d3) indicates it's not clickable\n"
            "• Gray text (#808080) reinforces disabled state\n"
            "• Tooltip explains why it's disabled\n"
            "• Helps users understand they need to create a schedule first\n"
            "• Consistent with UI design principles"
        )
        
        tk.Label(
            explanation_frame,
            text=explanation_text,
            font=("Arial", 10),
            bg="#fffacd",
            justify=tk.LEFT
        ).pack(pady=5, padx=10)
    
    def create_test_run_feedback_tab(self):
        """Create tab showing inline feedback examples."""
        frame = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(frame, text="Inline Feedback")
        
        # Title
        tk.Label(
            frame,
            text="Test Run Inline Feedback Examples",
            font=("Arial", 18, "bold"),
            bg="#ffffff"
        ).pack(pady=15)
        
        # Example 1: Progress
        progress_frame = tk.Frame(frame, bg="#e8f4f8", relief="ridge", borderwidth=2)
        progress_frame.pack(pady=10, fill="x", padx=40)
        
        tk.Label(
            progress_frame,
            text="Progress Message",
            font=("Arial", 12, "bold"),
            bg="#e8f4f8"
        ).pack(pady=5)
        
        tk.Label(
            progress_frame,
            text="⏳ Running test backup using schedule configuration... Please wait...",
            font=("Arial", 11),
            bg="#e8f4f8",
            fg="blue",
            wraplength=700
        ).pack(pady=10, padx=10)
        
        # Example 2: Success
        success_frame = tk.Frame(frame, bg="#e8f4f8", relief="ridge", borderwidth=2)
        success_frame.pack(pady=10, fill="x", padx=40)
        
        tk.Label(
            success_frame,
            text="Success Message",
            font=("Arial", 12, "bold"),
            bg="#e8f4f8"
        ).pack(pady=5)
        
        success_text = (
            "✅ Test Backup Successful!\n\n"
            "Backup file: nextcloud_backup_test_20241014_152030.tar.gz\n"
            "Size: 125.67 MB\n"
            "Location: C:\\Backups\\Nextcloud\n\n"
            "Your scheduled backup configuration is working correctly."
        )
        
        tk.Label(
            success_frame,
            text=success_text,
            font=("Arial", 11),
            bg="#e8f4f8",
            fg="green",
            wraplength=700,
            justify=tk.LEFT
        ).pack(pady=10, padx=10)
        
        # Example 3: Error
        error_frame = tk.Frame(frame, bg="#e8f4f8", relief="ridge", borderwidth=2)
        error_frame.pack(pady=10, fill="x", padx=40)
        
        tk.Label(
            error_frame,
            text="Error Message",
            font=("Arial", 12, "bold"),
            bg="#e8f4f8"
        ).pack(pady=5)
        
        error_text = (
            "❌ Test Backup Failed:\n"
            "Backup directory does not exist: C:\\Backups\\Nextcloud\n"
            "Please verify the directory exists and is accessible."
        )
        
        tk.Label(
            error_frame,
            text=error_text,
            font=("Arial", 11),
            bg="#e8f4f8",
            fg="#e74c3c",
            wraplength=700,
            justify=tk.LEFT
        ).pack(pady=10, padx=10)
        
        # Add explanation
        explanation_frame = tk.Frame(frame, bg="#fffacd", relief="solid", borderwidth=1)
        explanation_frame.pack(pady=20, fill="x", padx=40)
        
        tk.Label(
            explanation_frame,
            text="✨ Inline Feedback Benefits",
            font=("Arial", 12, "bold"),
            bg="#fffacd"
        ).pack(pady=5)
        
        explanation_text = (
            "• No pop-up windows that block interaction\n"
            "• Messages appear directly on the page\n"
            "• Color-coded for easy recognition (blue/green/red)\n"
            "• Users can see full context while viewing results\n"
            "• Messages stay visible until next action\n"
            "• Professional, modern UI experience"
        )
        
        tk.Label(
            explanation_frame,
            text=explanation_text,
            font=("Arial", 10),
            bg="#fffacd",
            justify=tk.LEFT
        ).pack(pady=5, padx=10)


def main():
    """Run the demo."""
    print("=" * 70)
    print("TEST RUN BUTTON - VISUAL DEMO")
    print("=" * 70)
    print()
    print("This demo shows the Test Run button implementation:")
    print()
    print("Tab 1: Active Schedule")
    print("  • Shows Test Run button ENABLED in Current Status section")
    print("  • Positioned alongside Disable Schedule and Delete Schedule")
    print("  • Blue background indicates it's active and clickable")
    print("  • Hover over button to see tooltip")
    print()
    print("Tab 2: No Schedule")
    print("  • Shows Test Run button DISABLED when no schedule exists")
    print("  • Gray background and text indicate disabled state")
    print("  • Hover to see tooltip explaining why it's disabled")
    print()
    print("Tab 3: Inline Feedback")
    print("  • Shows examples of inline feedback messages")
    print("  • Progress, success, and error states")
    print("  • No pop-up windows!")
    print()
    print("=" * 70)
    print()
    
    app = TestRunButtonDemo()
    app.mainloop()


if __name__ == "__main__":
    main()
