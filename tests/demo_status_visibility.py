#!/usr/bin/env python3
"""
Visual demo script to show the improved status message visibility.
This script creates a simple GUI to demonstrate the new progress_fg colors
in both light and dark themes with bold font.
"""

import tkinter as tk
from tkinter import ttk

# Theme colors matching the main application
THEMES = {
    'light': {
        'bg': '#f0f0f0',
        'fg': '#000000',
        'progress_fg': '#1565c0',  # Dark blue for light theme - better readability
        'error_fg': '#d32f2f',
    },
    'dark': {
        'bg': '#1e1e1e',
        'fg': '#e0e0e0',
        'progress_fg': '#ffd966',  # Bright yellow for dark theme - high visibility
        'error_fg': '#ef5350',
    }
}

# Old color for comparison
OLD_BLUE = 'blue'

class StatusVisibilityDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Status Message Visibility Improvement Demo")
        self.root.geometry("900x650")
        
        self.current_theme = 'light'
        self.theme_colors = THEMES[self.current_theme]
        
        self.create_ui()
        
    def create_ui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.configure(bg=self.theme_colors['bg'])
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        header_frame.pack(fill='x', pady=20)
        
        title = tk.Label(
            header_frame,
            text="Status Message Visibility Improvement",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        title.pack()
        
        subtitle = tk.Label(
            header_frame,
            text=f"Current Theme: {self.current_theme.title()}",
            font=("Arial", 12),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        subtitle.pack(pady=5)
        
        # Theme toggle button
        toggle_btn = tk.Button(
            header_frame,
            text="Toggle Theme",
            font=("Arial", 11),
            command=self.toggle_theme,
            bg='#3daee9',
            fg='white',
            padx=20,
            pady=5
        )
        toggle_btn.pack(pady=10)
        
        # Main content frame
        content = tk.Frame(self.root, bg=self.theme_colors['bg'])
        content.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Before section
        before_frame = tk.LabelFrame(
            content,
            text="BEFORE (Old Blue Color)",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            padx=20,
            pady=20
        )
        before_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        before_desc = tk.Label(
            before_frame,
            text="Status messages used 'blue' color which had poor visibility,\nespecially on dark backgrounds.",
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            justify=tk.LEFT
        )
        before_desc.pack(anchor='w', pady=(0, 15))
        
        before_msg1 = tk.Label(
            before_frame,
            text="⏳ Extracting and detecting database type...\nPlease wait, this may take a moment...",
            font=("Arial", 12),
            bg=self.theme_colors['bg'],
            fg=OLD_BLUE,  # Old blue color
            justify=tk.LEFT,
            wraplength=600
        )
        before_msg1.pack(anchor='w', pady=10)
        
        before_msg2 = tk.Label(
            before_frame,
            text="⏳ Verifying scheduled backup... Checking backup files and logs...",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=OLD_BLUE,  # Old blue color
            justify=tk.LEFT,
            wraplength=600
        )
        before_msg2.pack(anchor='w', pady=10)
        
        # After section
        after_frame = tk.LabelFrame(
            content,
            text="AFTER (New Progress Color + Bold)",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            padx=20,
            pady=20
        )
        after_frame.pack(fill='both', expand=True)
        
        after_desc = tk.Label(
            after_frame,
            text="Status messages now use theme-appropriate colors with bold font\nfor better visibility and prominence.",
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            justify=tk.LEFT
        )
        after_desc.pack(anchor='w', pady=(0, 15))
        
        after_msg1 = tk.Label(
            after_frame,
            text="⏳ Extracting and detecting database type...\nPlease wait, this may take a moment...",
            font=("Arial", 12, "bold"),  # Bold font
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['progress_fg'],  # New theme-appropriate color
            justify=tk.LEFT,
            wraplength=600
        )
        after_msg1.pack(anchor='w', pady=10)
        
        after_msg2 = tk.Label(
            after_frame,
            text="⏳ Verifying scheduled backup... Checking backup files and logs...",
            font=("Arial", 11, "bold"),  # Bold font
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['progress_fg'],  # New theme-appropriate color
            justify=tk.LEFT,
            wraplength=600
        )
        after_msg2.pack(anchor='w', pady=10)
        
        # Color info
        info_frame = tk.Frame(self.root, bg=self.theme_colors['bg'])
        info_frame.pack(fill='x', pady=10, padx=40)
        
        if self.current_theme == 'light':
            color_info = "Light theme uses dark blue (#1565c0) for better readability"
        else:
            color_info = "Dark theme uses bright yellow (#ffd966) for high visibility"
        
        info_label = tk.Label(
            info_frame,
            text=f"ℹ️  {color_info}",
            font=("Arial", 10, "italic"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        info_label.pack()
        
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.theme_colors = THEMES[self.current_theme]
        self.create_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = StatusVisibilityDemo(root)
    root.mainloop()
