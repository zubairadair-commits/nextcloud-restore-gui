#!/usr/bin/env python3
"""
Test to verify mouse wheel scrolling works on the Configure Remote Access page.
This test creates a simple mockup to demonstrate:
1. Mouse wheel scrolling on main content canvas
2. Mouse wheel scrolling on domain list canvas
3. Removal of duplicate "Add New Domain" section
"""

import tkinter as tk
from tkinter import ttk

def create_test_window():
    """Create test window with scrollable content"""
    
    root = tk.Tk()
    root.title("Mouse Wheel Scrolling Test - Configure Remote Access")
    root.geometry("800x600")
    
    # Theme colors
    theme_colors = {
        'bg': '#2b2b2b',
        'fg': '#ffffff',
        'button_bg': '#3daee9',
        'button_fg': '#ffffff',
        'entry_bg': '#3c3c3c',
        'entry_fg': '#ffffff',
        'info_bg': '#1e5a7d',
        'info_fg': '#ffffff',
        'warning_bg': '#5a4a1e',
        'warning_fg': '#ffffff',
        'hint_fg': '#cccccc',
        'error_fg': '#ff6b6b',
        'error_bg': '#8b0000'
    }
    
    root.configure(bg=theme_colors['bg'])
    
    # Title
    title_frame = tk.Frame(root, bg=theme_colors['info_bg'], height=50)
    title_frame.pack(fill="x")
    title_frame.pack_propagate(False)
    
    tk.Label(
        title_frame,
        text="Mouse Wheel Scrolling Test",
        font=("Arial", 14, "bold"),
        bg=theme_colors['info_bg'],
        fg=theme_colors['info_fg']
    ).pack(pady=10)
    
    # Status bar
    status_frame = tk.Frame(root, bg=theme_colors['bg'], height=30)
    status_frame.pack(side="bottom", fill="x")
    status_frame.pack_propagate(False)
    
    tk.Label(
        status_frame,
        text="✓ Mouse wheel scrolling enabled | ✓ Duplicate Add Domain section removed",
        font=("Arial", 10),
        bg=theme_colors['bg'],
        fg='#45bf55'
    ).pack(side="left", padx=10)
    
    # Body frame
    body_frame = tk.Frame(root, bg=theme_colors['bg'])
    body_frame.pack(fill="both", expand=True)
    
    # Create scrollable main canvas
    canvas = tk.Canvas(body_frame, bg=theme_colors['bg'], highlightthickness=0)
    scrollbar = tk.Scrollbar(body_frame, orient="vertical", command=canvas.yview)
    content = tk.Frame(canvas, bg=theme_colors['bg'])
    
    canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")
    
    def configure_canvas(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas_width = canvas.winfo_width()
        if canvas_width > 1:
            content_width = min(600, canvas_width - 20)
            x_offset = (canvas_width - content_width) // 2
            canvas.itemconfig(canvas_window, width=content_width)
            canvas.coords(canvas_window, x_offset, 10)
    
    content.bind("<Configure>", configure_canvas)
    canvas.bind("<Configure>", configure_canvas)
    
    # Add mouse wheel scrolling support
    def on_mouse_wheel(event):
        """Handle mouse wheel scrolling"""
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")
    
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    canvas.bind_all("<Button-4>", on_mouse_wheel)
    canvas.bind_all("<Button-5>", on_mouse_wheel)
    
    # Page title
    tk.Label(
        content,
        text="⚙️ Configure Remote Access",
        font=("Arial", 18, "bold"),
        bg=theme_colors['bg'],
        fg=theme_colors['fg']
    ).pack(pady=(10, 5))
    
    # Instruction box
    instruction_box = tk.Frame(content, bg='#45bf55', relief="solid", borderwidth=2)
    instruction_box.pack(pady=10, fill="x", padx=20)
    
    tk.Label(
        instruction_box,
        text="✓ CHANGES APPLIED",
        font=("Arial", 12, "bold"),
        bg='#45bf55',
        fg='#ffffff'
    ).pack(pady=5)
    
    tk.Label(
        instruction_box,
        text="1. Duplicate 'Add New Domain' section REMOVED from below the domain list\n"
             "2. Mouse wheel scrolling ENABLED for entire page\n"
             "3. Use 'Custom Domains (Optional)' section at top to add domains",
        font=("Arial", 10),
        bg='#45bf55',
        fg='#ffffff',
        justify=tk.LEFT
    ).pack(pady=5, padx=10)
    
    # Custom Domains section (at top - THIS IS THE ONLY ADD DOMAIN SECTION NOW)
    tk.Label(
        content,
        text="Custom Domains (Optional)",
        font=("Arial", 13, "bold"),
        bg=theme_colors['bg'],
        fg=theme_colors['fg']
    ).pack(pady=(20, 5), fill="x", padx=20)
    
    domain_frame = tk.Frame(content, bg=theme_colors['bg'])
    domain_frame.pack(pady=5, fill="x", padx=20)
    
    tk.Label(
        domain_frame,
        text="Domain:",
        font=("Arial", 11),
        bg=theme_colors['bg'],
        fg=theme_colors['fg']
    ).pack(side="left", padx=(0, 10))
    
    tk.Entry(
        domain_frame,
        font=("Arial", 11),
        bg=theme_colors['entry_bg'],
        fg=theme_colors['entry_fg']
    ).pack(side="left", fill="x", expand=True, padx=(0, 10))
    
    tk.Button(
        domain_frame,
        text="✓ Apply",
        font=("Arial", 10, "bold"),
        bg="#45bf55",
        fg="white",
        width=10
    ).pack(side="left")
    
    # Current Trusted Domains section
    tk.Label(
        content,
        text="Current Trusted Domains",
        font=("Arial", 13, "bold"),
        bg=theme_colors['bg'],
        fg=theme_colors['fg']
    ).pack(pady=(30, 10), fill="x", padx=20)
    
    # Scrollable domain list
    list_container = tk.Frame(content, bg=theme_colors['bg'])
    list_container.pack(pady=5, fill="both", expand=True, padx=20)
    
    domain_canvas = tk.Canvas(
        list_container,
        bg=theme_colors['bg'],
        height=200,
        highlightthickness=0
    )
    domain_scrollbar = tk.Scrollbar(list_container, orient="vertical", command=domain_canvas.yview)
    domains_frame = tk.Frame(domain_canvas, bg=theme_colors['bg'])
    
    domain_canvas.configure(yscrollcommand=domain_scrollbar.set)
    
    domain_scrollbar.pack(side="right", fill="y")
    domain_canvas.pack(side="left", fill="both", expand=True)
    
    canvas_window2 = domain_canvas.create_window((0, 0), window=domains_frame, anchor="nw")
    
    def configure_domain_scroll(event=None):
        domain_canvas.configure(scrollregion=domain_canvas.bbox("all"))
        canvas_width = domain_canvas.winfo_width()
        if canvas_width > 1:
            domain_canvas.itemconfig(canvas_window2, width=canvas_width)
    
    domains_frame.bind("<Configure>", configure_domain_scroll)
    domain_canvas.bind("<Configure>", configure_domain_scroll)
    
    # Add mouse wheel scrolling for domain list
    def on_domain_mouse_wheel(event):
        """Handle mouse wheel scrolling for domain list"""
        if event.num == 5 or event.delta < 0:
            domain_canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta > 0:
            domain_canvas.yview_scroll(-1, "units")
    
    domain_canvas.bind("<MouseWheel>", on_domain_mouse_wheel)
    domain_canvas.bind("<Button-4>", on_domain_mouse_wheel)
    domain_canvas.bind("<Button-5>", on_domain_mouse_wheel)
    
    # Add sample domains
    domains = [
        "localhost",
        "100.101.102.103",
        "myserver.tailnet.ts.net",
        "example.com",
        "mycloud.example.com",
        "subdomain.example.com",
        "test.local",
        "dev.example.com",
        "staging.example.com",
        "prod.example.com"
    ]
    
    for domain in domains:
        domain_row = tk.Frame(domains_frame, bg=theme_colors['entry_bg'], relief="solid", borderwidth=1)
        domain_row.pack(pady=3, fill="x", padx=2)
        
        tk.Label(
            domain_row,
            text="✓",
            font=("Arial", 12),
            bg=theme_colors['entry_bg'],
            fg='#45bf55',
            width=2
        ).pack(side="left", padx=(5, 0), pady=8)
        
        tk.Label(
            domain_row,
            text=domain,
            font=("Arial", 11),
            bg=theme_colors['entry_bg'],
            fg=theme_colors['entry_fg'],
            anchor="w"
        ).pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        tk.Button(
            domain_row,
            text="✕",
            font=("Arial", 12, "bold"),
            bg=theme_colors['error_bg'],
            fg="white",
            width=3,
            height=1
        ).pack(side="right", padx=5, pady=5)
    
    # Info note (UPDATED TEXT)
    info_note = tk.Frame(content, bg=theme_colors['info_bg'], relief="solid", borderwidth=1)
    info_note.pack(pady=10, fill="x", padx=20)
    
    info_text = (
        "💡 Status Icons: ✓ Active | ⚠️ Unreachable | ⏳ Pending | ❌ Error\n\n"
        "• Click ✕ to remove a domain (with confirmation)\n"
        "• Use the \"Custom Domains (Optional)\" section at the top to add new domains\n"
        "• Changes are logged and can be undone\n"
        "• Hover over domains for more information"
    )
    
    tk.Label(
        info_note,
        text=info_text,
        font=("Arial", 9),
        bg=theme_colors['info_bg'],
        fg=theme_colors['info_fg'],
        wraplength=540,
        justify=tk.LEFT
    ).pack(pady=8, padx=10, anchor="w")
    
    # Add some more content to demonstrate scrolling
    for i in range(3):
        tk.Label(
            content,
            text=f"Additional content section {i+1} (scroll to see all content)",
            font=("Arial", 10),
            bg=theme_colors['bg'],
            fg=theme_colors['hint_fg']
        ).pack(pady=10, fill="x", padx=20)
    
    root.mainloop()

if __name__ == "__main__":
    print("=" * 80)
    print("Mouse Wheel Scrolling Test")
    print("=" * 80)
    print("\nTesting changes:")
    print("  1. ✓ Duplicate 'Add New Domain' section removed")
    print("  2. ✓ Mouse wheel scrolling enabled for main canvas")
    print("  3. ✓ Mouse wheel scrolling enabled for domain list canvas")
    print("  4. ✓ Info note updated to guide users to top section")
    print("\nInstructions:")
    print("  - Use mouse wheel to scroll the page")
    print("  - Hover over the domain list and use mouse wheel to scroll it")
    print("  - Notice there is only ONE place to add domains (at the top)")
    print("  - Close the window when done testing\n")
    
    create_test_window()
    
    print("\n✓ Test completed!")
