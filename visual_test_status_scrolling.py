#!/usr/bin/env python3
"""
Visual test to demonstrate:
1. Status text color is yellow (#FFD700)
2. Mouse wheel scrolling works in schedule configuration page
"""

import tkinter as tk
from tkinter import ttk


class StatusColorDemo(tk.Tk):
    """Demo to show yellow status text."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Status Text Color Demo - Yellow (#FFD700)")
        self.geometry("600x400")
        self.configure(bg="#2b2b2b")  # Dark background
        
        # Create main container
        container = tk.Frame(self, bg="#2b2b2b")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            container,
            text="Status Text Color Demonstration",
            font=("Arial", 18, "bold"),
            bg="#2b2b2b",
            fg="white"
        )
        title.pack(pady=20)
        
        # Info
        info = tk.Label(
            container,
            text="The status text below shows the new yellow color (#FFD700)\nagainst a dark background for better contrast:",
            font=("Arial", 11),
            bg="#2b2b2b",
            fg="white",
            justify=tk.CENTER
        )
        info.pack(pady=10)
        
        # Status text examples
        status_frame = tk.Frame(container, bg="#3b3b3b", relief="ridge", borderwidth=2)
        status_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(
            status_frame,
            text="OLD (Blue):",
            font=("Arial", 12, "bold"),
            bg="#3b3b3b",
            fg="white"
        ).pack(pady=10)
        
        tk.Label(
            status_frame,
            text="⏳ Running test backup via Task Scheduler... Please wait...",
            font=("Arial", 11),
            bg="#3b3b3b",
            fg="blue"
        ).pack(pady=5)
        
        tk.Label(
            status_frame,
            text="NEW (Yellow #FFD700):",
            font=("Arial", 12, "bold"),
            bg="#3b3b3b",
            fg="white"
        ).pack(pady=(20, 10))
        
        tk.Label(
            status_frame,
            text="⏳ Running test backup via Task Scheduler... Please wait...",
            font=("Arial", 11),
            bg="#3b3b3b",
            fg="#FFD700"  # Yellow
        ).pack(pady=5)
        
        tk.Label(
            status_frame,
            text="⏳ Running test backup... Please wait...",
            font=("Arial", 11),
            bg="#3b3b3b",
            fg="#FFD700"  # Yellow
        ).pack(pady=5)
        
        # Close button
        tk.Button(
            container,
            text="Close",
            font=("Arial", 12),
            command=self.quit
        ).pack(pady=10)


class ScrollingDemo(tk.Tk):
    """Demo to show mouse wheel scrolling."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Mouse Wheel Scrolling Demo")
        self.geometry("600x500")
        self.configure(bg="#f0f0f0")
        
        # Create main container
        container = tk.Frame(self, bg="#f0f0f0")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title (outside scrollable area)
        title = tk.Label(
            container,
            text="Schedule Backup Configuration (Scrollable)",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title.pack(pady=10)
        
        # Info
        info = tk.Label(
            container,
            text="Try scrolling with your mouse wheel! ↕️",
            font=("Arial", 11),
            bg="#f0f0f0",
            fg="#666666"
        )
        info.pack(pady=5)
        
        # Create scrollable canvas
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
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        # Add mouse wheel scrolling support
        def on_mouse_wheel(event):
            """Handle mouse wheel scrolling"""
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
        
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        canvas.bind_all("<Button-4>", on_mouse_wheel)
        canvas.bind_all("<Button-5>", on_mouse_wheel)
        
        # Add content sections to demonstrate scrolling
        for i in range(15):
            section = tk.LabelFrame(
                scrollable_frame,
                text=f"Section {i+1}",
                font=("Arial", 12, "bold"),
                bg="#e3f2fd",
                fg="#1976d2",
                relief="ridge",
                borderwidth=2,
                padx=10,
                pady=10
            )
            section.pack(pady=10, fill="x", padx=20)
            
            tk.Label(
                section,
                text=f"This is content for section {i+1}.\nScroll down to see more sections!",
                font=("Arial", 10),
                bg="#e3f2fd",
                fg="#333333",
                justify=tk.LEFT
            ).pack(pady=5)
        
        # Close button
        close_btn = tk.Button(
            scrollable_frame,
            text="Close Demo",
            font=("Arial", 12),
            command=self.quit
        )
        close_btn.pack(pady=20)


def main():
    """Show both demos."""
    print("=" * 70)
    print("Visual Test: Status Text Color and Mouse Wheel Scrolling")
    print("=" * 70)
    print()
    print("Opening two demo windows:")
    print("1. Status Text Color Demo - Shows yellow text on dark background")
    print("2. Scrolling Demo - Shows mouse wheel scrolling functionality")
    print()
    print("Close each window when done viewing.")
    print("=" * 70)
    
    # Show status color demo
    print("\n[1/2] Opening Status Text Color Demo...")
    status_demo = StatusColorDemo()
    status_demo.mainloop()
    
    # Show scrolling demo
    print("\n[2/2] Opening Mouse Wheel Scrolling Demo...")
    scrolling_demo = ScrollingDemo()
    scrolling_demo.mainloop()
    
    print("\n✅ Visual tests completed!")


if __name__ == "__main__":
    main()
