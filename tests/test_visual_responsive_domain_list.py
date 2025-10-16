#!/usr/bin/env python3
"""
Visual test for responsive domain list in Configure Remote Access page.
This creates a mock UI to demonstrate:
1. Responsive layout that adapts to window size
2. Scrollable domain list with many domains
3. "No trusted domains" message for empty list
4. Proper centering with max width
"""

import tkinter as tk
from tkinter import ttk
import sys

def create_mock_remote_access_page(root, num_domains=0):
    """Create a mock of the Configure Remote Access page"""
    
    # Theme colors (matching the main app)
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
    
    # Title frame
    title_frame = tk.Frame(root, bg=theme_colors['info_bg'], height=50)
    title_frame.pack(fill="x")
    title_frame.pack_propagate(False)
    
    tk.Label(
        title_frame,
        text="Nextcloud Restore GUI - Configure Remote Access",
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
        text=f"Status: Responsive Layout Test - {num_domains} domains",
        font=("Arial", 10),
        bg=theme_colors['bg'],
        fg=theme_colors['hint_fg']
    ).pack(side="left", padx=10)
    
    # Body frame (main content area)
    body_frame = tk.Frame(root, bg=theme_colors['bg'])
    body_frame.pack(fill="both", expand=True)
    
    # Create scrollable content frame (NEW RESPONSIVE IMPLEMENTATION)
    canvas = tk.Canvas(body_frame, bg=theme_colors['bg'], highlightthickness=0)
    scrollbar = tk.Scrollbar(body_frame, orient="vertical", command=canvas.yview)
    content = tk.Frame(canvas, bg=theme_colors['bg'])
    
    # Configure canvas scrolling
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack scrollbar and canvas with responsive layout
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    # Create window in canvas for content
    canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")
    
    # Update scroll region and canvas width when frame size changes
    def configure_canvas(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Make content frame width match canvas width for centering
        canvas_width = canvas.winfo_width()
        if canvas_width > 1:  # Only update if canvas has been rendered
            # Center content with max width of 600px
            content_width = min(600, canvas_width - 20)
            x_offset = (canvas_width - content_width) // 2
            canvas.itemconfig(canvas_window, width=content_width)
            canvas.coords(canvas_window, x_offset, 10)
    
    content.bind("<Configure>", configure_canvas)
    canvas.bind("<Configure>", configure_canvas)
    
    # Add mouse wheel scrolling support for the main canvas
    def on_mouse_wheel(event):
        """Handle mouse wheel scrolling for the canvas"""
        # Windows and MacOS
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")
    
    # Bind mouse wheel events (both Windows/Mac and Linux)
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows and MacOS
    canvas.bind_all("<Button-4>", on_mouse_wheel)    # Linux scroll up
    canvas.bind_all("<Button-5>", on_mouse_wheel)    # Linux scroll down
    
    # Page title
    tk.Label(
        content,
        text="⚙️ Configure Remote Access",
        font=("Arial", 18, "bold"),
        bg=theme_colors['bg'],
        fg=theme_colors['fg']
    ).pack(pady=(10, 5), fill="x", padx=40)
    
    # Info box
    info_frame = tk.Frame(content, bg=theme_colors['info_bg'], relief="solid", borderwidth=1)
    info_frame.pack(pady=10, fill="x", padx=40)
    
    tk.Label(
        info_frame,
        text="📡 Your Tailscale Network Information",
        font=("Arial", 12, "bold"),
        bg=theme_colors['info_bg'],
        fg=theme_colors['info_fg']
    ).pack(pady=(10, 5), padx=10, anchor="w")
    
    tk.Label(
        info_frame,
        text="Tailscale IP: 100.101.102.103\nMagicDNS Name: myserver.tailnet.ts.net",
        font=("Arial", 11),
        bg=theme_colors['info_bg'],
        fg=theme_colors['info_fg'],
        justify=tk.LEFT
    ).pack(pady=(5, 10), padx=20, anchor="w")
    
    # Current Trusted Domains Section
    tk.Label(
        content,
        text="Current Trusted Domains",
        font=("Arial", 13, "bold"),
        bg=theme_colors['bg'],
        fg=theme_colors['fg']
    ).pack(pady=(30, 10), fill="x", padx=20)
    
    tk.Label(
        content,
        text="These domains are currently configured for Nextcloud access:",
        font=("Arial", 10),
        bg=theme_colors['bg'],
        fg=theme_colors['hint_fg']
    ).pack(pady=(0, 10), anchor="w", padx=20)
    
    # Management controls
    controls_frame = tk.Frame(content, bg=theme_colors['bg'])
    controls_frame.pack(pady=(0, 10), fill="x", padx=20)
    
    tk.Button(
        controls_frame,
        text="🔄 Refresh Status",
        font=("Arial", 9),
        bg=theme_colors['button_bg'],
        fg=theme_colors['button_fg']
    ).pack(side="left", padx=(0, 5))
    
    # Generate domain list or empty message
    if num_domains == 0:
        # NEW: Display "No trusted domains configured" message
        no_domains_frame = tk.Frame(content, bg=theme_colors['warning_bg'], relief="solid", borderwidth=1)
        no_domains_frame.pack(pady=10, fill="x", padx=20)
        
        tk.Label(
            no_domains_frame,
            text="No trusted domains configured",
            font=("Arial", 12, "bold"),
            bg=theme_colors['warning_bg'],
            fg=theme_colors['warning_fg']
        ).pack(pady=15, padx=10)
        
        tk.Label(
            no_domains_frame,
            text="Add domains using the form below to allow access to your Nextcloud instance.",
            font=("Arial", 10),
            bg=theme_colors['warning_bg'],
            fg=theme_colors['warning_fg'],
            wraplength=540
        ).pack(pady=(0, 15), padx=10)
    else:
        # NEW: Scrollable domains list with responsive layout
        list_container = tk.Frame(content, bg=theme_colors['bg'])
        list_container.pack(pady=5, fill="both", expand=True, padx=20)
        
        # Create canvas and scrollbar for domain list
        domain_canvas = tk.Canvas(
            list_container,
            bg=theme_colors['bg'],
            height=min(300, num_domains * 50),  # Max height 300px
            highlightthickness=0
        )
        domain_scrollbar = tk.Scrollbar(list_container, orient="vertical", command=domain_canvas.yview)
        domains_frame = tk.Frame(domain_canvas, bg=theme_colors['bg'])
        
        # Configure canvas
        domain_canvas.configure(yscrollcommand=domain_scrollbar.set)
        
        # Pack scrollbar and canvas
        domain_scrollbar.pack(side="right", fill="y")
        domain_canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas
        canvas_window = domain_canvas.create_window((0, 0), window=domains_frame, anchor="nw")
        
        # Update scroll region and canvas width when frame size changes
        def configure_domain_scroll(event=None):
            domain_canvas.configure(scrollregion=domain_canvas.bbox("all"))
            canvas_width = domain_canvas.winfo_width()
            if canvas_width > 1:
                domain_canvas.itemconfig(canvas_window, width=canvas_width)
        
        domains_frame.bind("<Configure>", configure_domain_scroll)
        domain_canvas.bind("<Configure>", configure_domain_scroll)
        
        # Add mouse wheel scrolling support for the domain list canvas
        def on_domain_mouse_wheel(event):
            """Handle mouse wheel scrolling for the domain list canvas"""
            # Windows and MacOS
            if event.num == 5 or event.delta < 0:
                domain_canvas.yview_scroll(1, "units")
            if event.num == 4 or event.delta > 0:
                domain_canvas.yview_scroll(-1, "units")
        
        # Bind mouse wheel events for domain list
        domain_canvas.bind("<MouseWheel>", on_domain_mouse_wheel)  # Windows and MacOS
        domain_canvas.bind("<Button-4>", on_domain_mouse_wheel)    # Linux scroll up
        domain_canvas.bind("<Button-5>", on_domain_mouse_wheel)    # Linux scroll down
        
        # Generate mock domains
        domain_names = [
            "localhost",
            "100.101.102.103",
            "myserver.tailnet.ts.net",
            "example.com",
            "mycloud.example.com",
            "subdomain.example.com",
            "192.168.1.100",
            "another-domain.com",
            "test.local",
            "*.wildcard.example.com",
            "dev.example.com",
            "staging.example.com",
            "prod.example.com",
            "api.example.com",
            "app.example.com"
        ]
        
        status_icons = ['✓', '✓', '✓', '⚠️', '✓', '⚠️', '✓', '✓', '⏳', '⚠️', '✓', '✓', '✓', '⚠️', '✓']
        status_colors = ['#45bf55', '#45bf55', '#45bf55', '#ff9800', '#45bf55', '#ff9800', '#45bf55', 
                        '#45bf55', '#2196f3', '#ff9800', '#45bf55', '#45bf55', '#45bf55', '#ff9800', '#45bf55']
        
        for i in range(min(num_domains, len(domain_names))):
            domain = domain_names[i]
            status_icon = status_icons[i]
            status_color = status_colors[i]
            
            domain_row = tk.Frame(domains_frame, bg=theme_colors['entry_bg'], relief="solid", borderwidth=1)
            domain_row.pack(pady=3, fill="x", padx=2)
            
            # Status icon
            tk.Label(
                domain_row,
                text=status_icon,
                font=("Arial", 12),
                bg=theme_colors['entry_bg'],
                fg=status_color,
                width=2
            ).pack(side="left", padx=(5, 0), pady=8)
            
            # Domain label
            tk.Label(
                domain_row,
                text=domain,
                font=("Arial", 11),
                bg=theme_colors['entry_bg'],
                fg=theme_colors['entry_fg'],
                anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=10, pady=8)
            
            # Remove button
            tk.Button(
                domain_row,
                text="✕",
                font=("Arial", 12, "bold"),
                bg=theme_colors['error_bg'],
                fg="white",
                width=3,
                height=1
            ).pack(side="right", padx=5, pady=5)
    
    # Info note
    info_note = tk.Frame(content, bg=theme_colors['info_bg'], relief="solid", borderwidth=1)
    info_note.pack(pady=10, fill="x", padx=20)
    
    info_text = (
        "💡 Status Icons: ✓ Active | ⚠️ Unreachable | ⏳ Pending\n\n"
        "• Click ✕ to remove a domain (with confirmation)\n"
        "• Use the \"Custom Domains (Optional)\" section at the top to add new domains\n"
        "• Changes are logged and can be undone"
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

def main():
    """Run visual tests for different scenarios"""
    
    scenarios = [
        ("Empty Domain List", 0),
        ("Short Domain List (3 domains)", 3),
        ("Medium Domain List (7 domains)", 7),
        ("Long Domain List (15 domains)", 15)
    ]
    
    print("=" * 80)
    print("Visual Test for Responsive Domain List")
    print("=" * 80)
    print("\nThis test will display multiple windows showing different scenarios:")
    for name, count in scenarios:
        print(f"  - {name}")
    print("\nResize each window to see the responsive behavior!")
    print("Close each window to move to the next test.\n")
    
    for scenario_name, num_domains in scenarios:
        print(f"Showing: {scenario_name}")
        
        root = tk.Tk()
        root.title(f"Responsive Domain List Test - {scenario_name}")
        root.geometry("800x600")
        
        create_mock_remote_access_page(root, num_domains)
        
        # Add resize instructions
        instruction_label = tk.Label(
            root,
            text=f"📏 Resize this window to test responsiveness! ({scenario_name})",
            font=("Arial", 10, "bold"),
            bg="#FFD700",
            fg="#000000"
        )
        instruction_label.pack(side="top", fill="x")
        
        root.mainloop()
    
    print("\n✓ Visual tests completed!")
    print("The responsive layout should:")
    print("  1. Always keep domains visible with scrolling")
    print("  2. Center content with max 600px width")
    print("  3. Expand/contract smoothly when resized")
    print("  4. Show clear message when no domains exist")

if __name__ == "__main__":
    main()
