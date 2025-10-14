#!/usr/bin/env python3
"""
Demo script to show the scheduled backup UI enhancements.
This creates a simplified version of the UI to demonstrate the new features.
"""

import tkinter as tk
from tkinter import ttk
import os
import platform
from datetime import datetime


def get_system_timezone_info():
    """Get the system's local timezone information as a string."""
    try:
        now = datetime.now()
        local_tz = now.astimezone()
        tz_offset = local_tz.strftime('%z')
        tz_name = local_tz.tzname()
        
        if tz_offset:
            offset_hours = int(tz_offset[:3])
            offset_mins = int(tz_offset[0] + tz_offset[3:5])
            offset_str = f"UTC{offset_hours:+03d}:{abs(offset_mins):02d}"
            if tz_name:
                return f"{offset_str} ({tz_name})"
            return offset_str
        elif tz_name:
            return tz_name
        else:
            return "Local System Time"
    except Exception as e:
        return "Local System Time"


def detect_cloud_sync_folders():
    """Detect common cloud storage sync folders on the system."""
    home = os.path.expanduser("~")
    cloud_folders = {}
    
    # OneDrive detection
    onedrive_paths = [
        os.path.join(home, "OneDrive"),
        os.path.join(home, "OneDrive - Personal"),
    ]
    for path in onedrive_paths:
        if path and os.path.isdir(path):
            cloud_folders['OneDrive'] = path
            break
    
    # Google Drive detection
    google_drive_paths = [
        os.path.join(home, "Google Drive"),
        os.path.join(home, "GoogleDrive"),
        os.path.join(home, "My Drive"),
    ]
    for path in google_drive_paths:
        if os.path.isdir(path):
            cloud_folders['Google Drive'] = path
            break
    
    # Dropbox detection
    dropbox_paths = [os.path.join(home, "Dropbox")]
    for path in dropbox_paths:
        if os.path.isdir(path):
            cloud_folders['Dropbox'] = path
            break
    
    # For demo purposes, add simulated folders if none detected
    if not cloud_folders:
        cloud_folders['OneDrive (demo)'] = os.path.join(home, "OneDrive")
        cloud_folders['Google Drive (demo)'] = os.path.join(home, "Google Drive")
        cloud_folders['Dropbox (demo)'] = os.path.join(home, "Dropbox")
    
    return cloud_folders


class ScheduledBackupDemo(tk.Tk):
    """Demo window showing scheduled backup UI enhancements."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Scheduled Backup UI Demo - Enhanced UX")
        self.geometry("800x900")
        self.configure(bg="#f0f0f0")
        
        # Create main container for padding
        container = tk.Frame(self, bg="#f0f0f0")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title (outside scrollable area for better UX)
        title = tk.Label(
            container,
            text="Schedule Backup Configuration",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title.pack(pady=(0, 10))
        
        # Create scrollable canvas for all content
        canvas = tk.Canvas(container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_scroll(event=None):
            """Update scroll region when content changes"""
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make scrollable_frame width match canvas width
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        # Add mouse wheel scrolling support for Windows
        def on_mouse_wheel(event):
            """Handle mouse wheel scrolling"""
            # Windows and macOS use event.delta
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            # Linux uses event.num (Button-4 = scroll up, Button-5 = scroll down)
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
        
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows/Mac
        canvas.bind_all("<Button-4>", on_mouse_wheel)    # Linux scroll up
        canvas.bind_all("<Button-5>", on_mouse_wheel)    # Linux scroll down
        
        # Store references for potential cleanup
        self.canvas = canvas
        self.scrollbar = scrollbar
        self.scrollable_frame = scrollable_frame
        
        # Current Status section
        self.create_status_section(scrollable_frame)
        
        # Configuration section
        self.create_config_section(scrollable_frame)
        
        # Setup Guide section
        self.create_setup_guide(scrollable_frame)
        
    def create_status_section(self, parent):
        """Create the current status display."""
        status_frame = tk.LabelFrame(
            parent,
            text="Current Status",
            font=("Arial", 14, "bold"),
            bg="#e3f2fd",
            fg="#1976d2",
            relief="ridge",
            borderwidth=2,
            padx=10,
            pady=10
        )
        status_frame.pack(fill="x", pady=10)
        
        # Example active schedule
        tz_info = get_system_timezone_info()
        status_text = (
            f"✓ Scheduled backup is active\n"
            f"Frequency: daily\n"
            f"Time: 02:00 ({tz_info})\n"
            f"Backup Directory: /home/user/OneDrive/Nextcloud-Backups\n"
            f"☁️ Cloud Sync: OneDrive (automatic sync enabled)"
        )
        
        status_label = tk.Label(
            status_frame,
            text=status_text,
            font=("Arial", 11),
            bg="#e3f2fd",
            fg="#333333",
            justify=tk.LEFT
        )
        status_label.pack(pady=5)
        
    def create_config_section(self, parent):
        """Create the configuration section."""
        config_frame = tk.LabelFrame(
            parent,
            text="Configure New Schedule",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            relief="ridge",
            borderwidth=2,
            padx=15,
            pady=10
        )
        config_frame.pack(fill="both", expand=True, pady=10)
        
        # Backup directory with info icon
        dir_label_frame = tk.Frame(config_frame, bg="#ffffff")
        dir_label_frame.pack(pady=5, anchor="w")
        
        tk.Label(
            dir_label_frame,
            text="Backup Directory:",
            font=("Arial", 11),
            bg="#ffffff"
        ).pack(side="left")
        
        info_label = tk.Label(
            dir_label_frame,
            text="ℹ️",
            font=("Arial", 11),
            bg="#ffffff",
            fg="#1976d2",
            cursor="hand2"
        )
        info_label.pack(side="left", padx=5)
        
        # Bind tooltip simulation
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            msg = (
                "Choose where to save your backups:\n\n"
                "• Local folder: Backups saved only on this computer\n"
                "• Cloud sync folder: Backups automatically sync to cloud\n\n"
                "Cloud Storage Options:\n"
                "✓ OneDrive, Google Drive, Dropbox, iCloud Drive\n"
                "✓ Select your cloud provider's local sync folder\n"
                "✓ Files will automatically upload to the cloud\n\n"
                "Note: Large backups may take time to sync."
            )
            
            tk.Label(
                tooltip,
                text=msg,
                background="#ffffcc",
                foreground="#000000",
                relief=tk.SOLID,
                borderwidth=1,
                font=("Arial", 9),
                justify=tk.LEFT,
                padx=10,
                pady=5
            ).pack()
            
            def hide_tooltip(e=None):
                tooltip.destroy()
            
            tooltip.bind("<Leave>", hide_tooltip)
            info_label.bind("<Leave>", hide_tooltip)
            self.after(5000, hide_tooltip)
        
        info_label.bind("<Enter>", show_tooltip)
        
        # Directory entry
        dir_entry_frame = tk.Frame(config_frame, bg="#ffffff")
        dir_entry_frame.pack(fill="x", pady=5)
        
        dir_var = tk.StringVar(value="")
        dir_entry = tk.Entry(
            dir_entry_frame,
            textvariable=dir_var,
            font=("Arial", 11),
            width=50
        )
        dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_btn = tk.Button(
            dir_entry_frame,
            text="Browse",
            font=("Arial", 10)
        )
        browse_btn.pack(side="right")
        
        # Detected cloud folders
        cloud_folders = detect_cloud_sync_folders()
        if cloud_folders:
            cloud_label = tk.Label(
                config_frame,
                text="📁 Detected Cloud Sync Folders:",
                font=("Arial", 9, "italic"),
                bg="#ffffff",
                fg="#666666"
            )
            cloud_label.pack(pady=(10, 5), anchor="w")
            
            for cloud_name, cloud_path in cloud_folders.items():
                cloud_btn = tk.Button(
                    config_frame,
                    text=f"☁️ {cloud_name}: {cloud_path}",
                    font=("Arial", 9),
                    bg="#e8f5e9",
                    fg="#333333",
                    anchor="w",
                    relief=tk.FLAT,
                    cursor="hand2",
                    command=lambda p=cloud_path: dir_var.set(p)
                )
                cloud_btn.pack(fill="x", pady=2)
        
        # Frequency
        tk.Label(
            config_frame,
            text="Frequency:",
            font=("Arial", 11),
            bg="#ffffff"
        ).pack(pady=(15, 5), anchor="w")
        
        freq_var = tk.StringVar(value="daily")
        freq_frame = tk.Frame(config_frame, bg="#ffffff")
        freq_frame.pack(anchor="w")
        
        for freq in ['daily', 'weekly', 'monthly']:
            tk.Radiobutton(
                freq_frame,
                text=freq.capitalize(),
                variable=freq_var,
                value=freq,
                font=("Arial", 11),
                bg="#ffffff"
            ).pack(side="left", padx=10)
        
        # Time with timezone
        time_label_frame = tk.Frame(config_frame, bg="#ffffff")
        time_label_frame.pack(pady=(15, 5), anchor="w")
        
        tk.Label(
            time_label_frame,
            text="Backup Time (HH:MM):",
            font=("Arial", 11),
            bg="#ffffff"
        ).pack(side="left")
        
        tz_info = get_system_timezone_info()
        tz_label = tk.Label(
            time_label_frame,
            text=f"  [{tz_info}]",
            font=("Arial", 9),
            bg="#ffffff",
            fg="#1976d2"
        )
        tz_label.pack(side="left")
        
        time_entry = tk.Entry(
            config_frame,
            font=("Arial", 11),
            width=10
        )
        time_entry.insert(0, "02:00")
        time_entry.pack(pady=5, anchor="w")
        
        # Create schedule button
        create_btn = tk.Button(
            config_frame,
            text="Create/Update Schedule",
            font=("Arial", 13, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10
        )
        create_btn.pack(pady=20)
        
    def create_setup_guide(self, parent):
        """Create the cloud storage setup guide."""
        guide_frame = tk.LabelFrame(
            parent,
            text="💡 Cloud Storage Setup Guide",
            font=("Arial", 12, "bold"),
            bg="#fff3e0",
            fg="#e65100",
            relief="groove",
            borderwidth=2,
            padx=15,
            pady=10
        )
        guide_frame.pack(fill="x", pady=10)
        
        guide_text = (
            "To sync backups to cloud storage:\n\n"
            "OneDrive:\n"
            "  1. Install OneDrive desktop app\n"
            "  2. Sign in and select folders to sync\n"
            "  3. Choose a folder inside your OneDrive folder above\n\n"
            "Google Drive:\n"
            "  1. Install Google Drive for Desktop\n"
            "  2. Sign in and configure sync settings\n"
            "  3. Choose a folder inside your Google Drive folder above\n\n"
            "Dropbox:\n"
            "  1. Install Dropbox desktop app\n"
            "  2. Sign in and select folders to sync\n"
            "  3. Choose a folder inside your Dropbox folder above\n\n"
            "Note: Backups will automatically upload to the cloud after creation.\n"
            "Large backups may take time to sync depending on your internet speed."
        )
        
        guide_label = tk.Label(
            guide_frame,
            text=guide_text,
            font=("Arial", 9),
            bg="#fff3e0",
            fg="#333333",
            justify=tk.LEFT
        )
        guide_label.pack()


def main():
    """Run the demo."""
    print("=" * 70)
    print("Scheduled Backup UI Demo")
    print("=" * 70)
    print()
    print("This demo shows the enhanced scheduled backup UI with:")
    print("  • Timezone display next to time picker")
    print("  • Cloud storage folder detection")
    print("  • Info tooltips (hover over ℹ️ icon)")
    print("  • One-click cloud folder selection")
    print("  • Cloud sync status indicators")
    print("  • Setup guide for cloud providers")
    print()
    print(f"System Timezone: {get_system_timezone_info()}")
    print()
    
    cloud_folders = detect_cloud_sync_folders()
    print(f"Detected Cloud Folders: {len(cloud_folders)}")
    for name, path in cloud_folders.items():
        print(f"  • {name}: {path}")
    print()
    print("Starting UI demo window...")
    print("=" * 70)
    
    app = ScheduledBackupDemo()
    app.mainloop()


if __name__ == "__main__":
    main()
