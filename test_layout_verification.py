#!/usr/bin/env python3
"""
Layout verification test for responsive domain list.
This test validates the layout changes without requiring a GUI.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def verify_responsive_layout():
    """Verify that the responsive layout is properly implemented"""
    print_section("Responsive Domain List - Layout Verification")
    
    # Check if main file exists
    main_file = "nextcloud_restore_and_backup-v9.py"
    if not os.path.exists(main_file):
        print("✗ Main file not found")
        return False
    
    # Read file content
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Find the _show_tailscale_config method
    start_idx = content.find('def _show_tailscale_config(self):')
    end_idx = content.find('\n    def ', start_idx + 1)
    config_method = content[start_idx:end_idx] if start_idx != -1 and end_idx != -1 else ""
    
    # Find the _display_current_trusted_domains method
    start_idx = content.find('def _display_current_trusted_domains(self, parent):')
    end_idx = content.find('\n    def ', start_idx + 1)
    display_method = content[start_idx:end_idx] if start_idx != -1 and end_idx != -1 else ""
    
    all_passed = True
    
    print_section("1. Main Content Frame - Responsive Layout")
    
    checks = {
        "Canvas with scrollbar": 'canvas = tk.Canvas(self.body_frame' in config_method,
        "Scrollbar packing": 'scrollbar.pack(side="right", fill="y")' in config_method,
        "Canvas responsive packing": 'canvas.pack(side="left", fill="both", expand=True)' in config_method,
        "Content in canvas window": 'canvas.create_window((0, 0), window=content, anchor="nw")' in config_method,
        "Dynamic width adjustment": 'content_width = min(600, canvas_width - 20)' in config_method,
        "Centering calculation": 'x_offset = (canvas_width - content_width) // 2' in config_method,
        "Canvas configure binding": 'canvas.bind("<Configure>", configure_canvas)' in config_method,
        "Content configure binding": 'content.bind("<Configure>", configure_canvas)' in config_method,
    }
    
    for check_name, result in checks.items():
        if result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print_section("2. Domain List - Empty State Handling")
    
    checks = {
        "Empty check condition": 'if not current_domains:' in display_method,
        "No domains frame": 'no_domains_frame = tk.Frame(parent' in display_method,
        "No domains message": 'No trusted domains configured' in display_method,
        "Help text for empty state": 'Add domains using the form below' in display_method,
        "Conditional domain list": 'else:' in display_method and 'list_container = tk.Frame(parent' in display_method,
    }
    
    for check_name, result in checks.items():
        if result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print_section("3. Domain List Container - Expandable Layout")
    
    checks = {
        "Container with expand": 'list_container.pack(pady=5, fill="both", expand=True, padx=20)' in display_method,
        "Canvas for scrolling": 'canvas = tk.Canvas(' in display_method and 'list_container' in display_method,
        "Domain scrollbar": 'scrollbar = tk.Scrollbar(list_container' in display_method,
        "Scroll region configuration": 'canvas.configure(scrollregion=canvas.bbox("all"))' in display_method,
        "Canvas width adjustment": 'canvas.itemconfig(canvas_window, width=canvas_width)' in display_method,
        "Multiple configure bindings": display_method.count('.bind("<Configure>"') >= 2,
    }
    
    for check_name, result in checks.items():
        if result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    print_section("4. Removed Fixed Width Implementation")
    
    # Check that old implementation is not in _show_tailscale_config
    old_patterns = [
        ('content.place(relx=0.5, anchor="n", y=10)', "Old .place() positioning"),
        ('def maintain_width(event=None):', "Old maintain_width function"),
        ('width=600', "Fixed width in content frame"),
    ]
    
    for pattern, description in old_patterns:
        if pattern in config_method:
            # Special handling for width=600 which might appear in canvas
            if pattern == 'width=600' and 'Frame(self.body_frame, bg=self.theme_colors' in config_method and 'width=600' in config_method:
                print(f"  ✗ {description} - still present in _show_tailscale_config")
                all_passed = False
            elif pattern != 'width=600':
                print(f"  ✗ {description} - still present in _show_tailscale_config")
                all_passed = False
            else:
                print(f"  ✓ {description} - properly removed")
        else:
            print(f"  ✓ {description} - properly removed")
    
    print_section("5. Visual Layout Comparison")
    
    print("\nBEFORE (Fixed Width):")
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│                                                                 │")
    print("│        ┌─────────────[600px fixed]──────────────┐              │")
    print("│        │ Configure Remote Access                │              │")
    print("│        │                                         │              │")
    print("│        │ Current Trusted Domains                │              │")
    print("│        │ [domain list gets cut off]             │              │")
    print("│        │                                         │              │")
    print("│        └─────────────────────────────────────────┘              │")
    print("│                                                                 │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print("Issues:")
    print("  ✗ Content gets cut off when window is small")
    print("  ✗ No scrolling for main content")
    print("  ✗ Fixed 600px width doesn't adapt to window size")
    print("  ✗ No message when domain list is empty")
    
    print("\nAFTER (Responsive with Scrolling):")
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ ┌───────────────────────────────────────────────────────────┐ │ │")
    print("│ │                                                           │ ║ │")
    print("│ │  ┌──────────[max 600px, centered]─────────┐              │ ║ │")
    print("│ │  │ Configure Remote Access                │              │ ║ │")
    print("│ │  │                                         │              │ ║ │")
    print("│ │  │ Current Trusted Domains                │              │ ║ │")
    print("│ │  │ ┌───────────────────────────────────┐  │              │ ║ │")
    print("│ │  │ │ ✓ domain1.com               ✕    │ ║│              │ ║ │")
    print("│ │  │ │ ✓ domain2.com               ✕    │ ║│  [scrolls]   │ ║ │")
    print("│ │  │ │ ✓ domain3.com               ✕    │ ║│              │ ║ │")
    print("│ │  │ └───────────────────────────────────┘  │              │ ║ │")
    print("│ │  │ Add New Domain: [input] [Add]          │              │ ║ │")
    print("│ │  └─────────────────────────────────────────┘              │ ║ │")
    print("│ └───────────────────────────────────────────────────────────┘ │ │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print("Improvements:")
    print("  ✓ Main content scrollable - never gets cut off")
    print("  ✓ Domain list scrollable within content")
    print("  ✓ Responsive width (centered, max 600px)")
    print("  ✓ 'No trusted domains' message when list is empty")
    print("  ✓ Proper expansion with fill='both' and expand=True")
    
    print_section("Test Summary")
    
    if all_passed:
        print("\n✓ All responsive layout features are properly implemented!")
        print("\nKey Improvements:")
        print("  1. Scrollable main content frame prevents cut-off")
        print("  2. Domain list is always visible with its own scrollbar")
        print("  3. Empty state displays clear message")
        print("  4. Layout adapts to window size responsively")
        print("  5. Content centers with max 600px width")
        return True
    else:
        print("\n✗ Some layout features are missing or incorrect.")
        return False

if __name__ == "__main__":
    success = verify_responsive_layout()
    sys.exit(0 if success else 1)
