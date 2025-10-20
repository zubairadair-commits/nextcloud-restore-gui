#!/usr/bin/env python3
"""
Visual demonstration of the error page centering fix.
Shows how the error page content is now horizontally centered.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

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


class ErrorPageCenteringDemo(tk.Tk):
    """Demonstration of the error page centering fix"""
    
    def __init__(self):
        super().__init__()
        self.title("Error Page Centering Fix Demo")
        self.geometry("900x700")
        
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
            text="Nextcloud Restore & Backup - Error Page Centering Demo",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(pady=25)
        
        # Body frame
        self.body_frame = tk.Frame(self, bg=self.theme_colors['bg'])
        self.body_frame.pack(fill='both', expand=True)
        
        self.show_centered_error_page()
    
    def show_centered_error_page(self):
        """Show the error page with horizontal centering"""
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        # Main error container with scrolling
        main_container = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        main_container.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(main_container, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, command=canvas.yview)
        error_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        # Function to center content in canvas
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Center the window horizontally
            canvas_width = canvas.winfo_width()
            frame_width = error_frame.winfo_reqwidth()
            x_position = max(0, (canvas_width - frame_width) // 2)
            canvas.coords(canvas_window, x_position, 0)
        
        error_frame.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", update_scroll_region)
        
        canvas_window = canvas.create_window((0, 0), window=error_frame, anchor="n")
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
            text="Error Type: Port Conflict",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(0, 15), anchor='w')
        
        # Container info frame
        info_frame = tk.Frame(content_container, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=2)
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(
            info_frame,
            text="Container: nextcloud-test  |  Port: 8080",
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
            text="Port 8080 is already in use by another application or container.",
            font=("Arial", 11),
            bg='#ffebee',
            fg='#b71c1c',
            wraplength=700,
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
            text="Try one of these alternative ports: 8081, 8082, 8090\n\n"
                 "Or stop the application/container using the port.",
            font=("Arial", 10),
            bg='#e8f5e9',
            fg='#1b5e20',
            wraplength=700,
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor='w')
        
        # Info box explaining the centering
        info_box = tk.Frame(content_container, bg='#fff3cd', relief="solid", borderwidth=2)
        info_box.pack(fill='x', pady=20)
        
        tk.Label(
            info_box,
            text="ℹ️ Centering Demo Information",
            font=("Arial", 12, "bold"),
            bg='#fff3cd',
            fg='#856404'
        ).pack(pady=(10, 5), padx=15, anchor='w')
        
        tk.Label(
            info_box,
            text="✓ Error content is now horizontally centered in the window\n"
                 "✓ Resize the window to see the content remain centered\n"
                 "✓ Content uses canvas.coords() to recalculate x-position on resize\n"
                 "✓ Anchor changed from 'nw' (northwest) to 'n' (north/top-center)",
            font=("Arial", 10),
            bg='#fff3cd',
            fg='#856404',
            wraplength=700,
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor='w')
        
        # Button frame
        button_frame = tk.Frame(content_container, bg=self.theme_colors['bg'])
        button_frame.pack(pady=20)
        
        # Return button
        menu_btn = tk.Button(
            button_frame,
            text="Close Demo",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=22,
            command=self.quit
        )
        menu_btn.pack(side="left", padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


if __name__ == '__main__':
    app = ErrorPageCenteringDemo()
    app.mainloop()
