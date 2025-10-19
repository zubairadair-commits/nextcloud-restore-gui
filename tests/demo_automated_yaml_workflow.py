#!/usr/bin/env python3
"""
Visual demonstration of the automated YAML workflow enhancements.
Shows the new Advanced Options section and how YAML files are handled.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class AutomatedYAMLDemo(tk.Tk):
    """
    Demonstration of the automated YAML workflow.
    Shows the Advanced Options section and explains the new behavior.
    """
    
    def __init__(self):
        super().__init__()
        self.title("Automated YAML Workflow Demo")
        self.geometry("900x800")
        
        # Theme colors (matching the main app)
        self.theme_colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'header_bg': '#3daee9',
            'header_fg': '#ffffff',
            'button_bg': '#3c3c3c',
            'button_fg': '#ffffff',
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
            text="🔧 Automated YAML Workflow Demo",
            font=("Arial", 20, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(pady=20)
        
        # Main content with scrollbar
        main_frame = tk.Frame(self, bg=self.theme_colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_frame, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.create_demo_content(scrollable_frame)
    
    def create_demo_content(self, parent):
        """Create the demonstration content"""
        
        # Overview section
        tk.Label(
            parent,
            text="What's New: Seamless YAML Handling",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(0, 10))
        
        tk.Label(
            parent,
            text="The restore workflow now automatically generates and stores Docker Compose YAML files\n"
                 "without interrupting your workflow. No more dialogs or save prompts!",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="center"
        ).pack(pady=(0, 20))
        
        # Before/After comparison
        comparison_frame = tk.Frame(parent, bg=self.theme_colors['bg'])
        comparison_frame.pack(fill='x', pady=20)
        
        # Before column
        before_frame = tk.Frame(comparison_frame, bg='#8b0000', relief='solid', borderwidth=2)
        before_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        tk.Label(
            before_frame,
            text="❌ Before (Old Workflow)",
            font=("Arial", 13, "bold"),
            bg='#8b0000',
            fg='white'
        ).pack(pady=10)
        
        before_items = [
            "1. Select backup file",
            "2. Enter credentials",
            "3. ⚠️ YAML dialog appears",
            "4. User must choose location",
            "5. User must save file",
            "6. User clicks 'Generate'",
            "7. Continue to restore",
            "8. Manual YAML editing often needed"
        ]
        
        for item in before_items:
            tk.Label(
                before_frame,
                text=item,
                font=("Arial", 10),
                bg='#8b0000',
                fg='white',
                anchor='w',
                justify='left'
            ).pack(anchor='w', padx=20, pady=2)
        
        tk.Label(before_frame, text="", bg='#8b0000').pack(pady=5)
        
        # After column
        after_frame = tk.Frame(comparison_frame, bg='#006400', relief='solid', borderwidth=2)
        after_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        tk.Label(
            after_frame,
            text="✅ After (New Workflow)",
            font=("Arial", 13, "bold"),
            bg='#006400',
            fg='white'
        ).pack(pady=10)
        
        after_items = [
            "1. Select backup file",
            "2. Enter credentials",
            "3. ✓ YAML auto-generated silently",
            "4. ✓ Stored in app data folder",
            "5. Continue to restore",
            "6. ✓ Everything just works!",
            "",
            "Advanced users can access YAML",
            "from 'Advanced Options' section"
        ]
        
        for item in after_items:
            tk.Label(
                after_frame,
                text=item,
                font=("Arial", 10),
                bg='#006400',
                fg='white',
                anchor='w',
                justify='left'
            ).pack(anchor='w', padx=20, pady=2)
        
        tk.Label(after_frame, text="", bg='#006400').pack(pady=5)
        
        # Storage location info
        info_frame = tk.Frame(parent, bg=self.theme_colors['info_bg'], relief='solid', borderwidth=1)
        info_frame.pack(fill='x', pady=20, padx=20)
        
        tk.Label(
            info_frame,
            text="📁 Automatic Storage",
            font=("Arial", 13, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(10, 5))
        
        tk.Label(
            info_frame,
            text="YAML files are now automatically saved to:",
            font=("Arial", 10),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['hint_fg']
        ).pack()
        
        tk.Label(
            info_frame,
            text="~/.nextcloud_backup_utility/compose/",
            font=("Courier", 11, "bold"),
            bg=self.theme_colors['info_bg'],
            fg='#45bf55'
        ).pack(pady=5)
        
        tk.Label(
            info_frame,
            text="Files are named with timestamps: docker-compose-20251019_183045.yml",
            font=("Arial", 9),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(0, 10))
        
        # Demo of Advanced Options section
        tk.Label(
            parent,
            text="Advanced Options Section (Demo)",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(20, 10))
        
        self.create_advanced_options_demo(parent)
        
        # Benefits section
        benefits_frame = tk.Frame(parent, bg=self.theme_colors['info_bg'], relief='solid', borderwidth=1)
        benefits_frame.pack(fill='x', pady=20, padx=20)
        
        tk.Label(
            benefits_frame,
            text="✨ Benefits of Automated YAML Handling",
            font=("Arial", 13, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(10, 5))
        
        benefits = [
            "🎯 Beginner-Friendly: No technical YAML knowledge required",
            "⚡ Faster Workflow: No interrupting dialogs or save prompts",
            "🔒 Secure: Files stored in user's private app data folder",
            "📝 Version History: Timestamped files preserve restore configurations",
            "🛠️ Power User Support: Advanced options still available when needed",
            "🚀 Seamless Experience: Focus on restore, not file management"
        ]
        
        for benefit in benefits:
            tk.Label(
                benefits_frame,
                text=benefit,
                font=("Arial", 10),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['info_fg'],
                anchor='w',
                justify='left'
            ).pack(anchor='w', padx=20, pady=3)
        
        tk.Label(benefits_frame, text="", bg=self.theme_colors['info_bg']).pack(pady=5)
    
    def create_advanced_options_demo(self, parent):
        """Demo the Advanced Options section"""
        
        # Advanced Options header with expand/collapse
        advanced_frame = tk.Frame(parent)
        advanced_frame.pack(pady=10, fill="x", padx=40)
        
        # State variable for expansion
        self.advanced_options_expanded = tk.BooleanVar(value=False)
        
        def toggle_advanced_options():
            """Toggle visibility of advanced options"""
            expanded = self.advanced_options_expanded.get()
            if expanded:
                advanced_content_frame.pack(pady=5, fill="x")
            else:
                advanced_content_frame.pack_forget()
        
        # Header button for expand/collapse
        advanced_header_btn = tk.Button(
            advanced_frame,
            text="▶ Advanced Options (for power users)",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=lambda: [
                self.advanced_options_expanded.set(not self.advanced_options_expanded.get()),
                advanced_header_btn.config(
                    text="▼ Advanced Options (for power users)" if self.advanced_options_expanded.get() 
                    else "▶ Advanced Options (for power users)"
                ),
                toggle_advanced_options()
            ],
            relief="flat",
            padx=10,
            pady=5
        )
        advanced_header_btn.pack(fill="x")
        
        # Advanced options content (initially hidden)
        advanced_content_frame = tk.Frame(parent, bg=self.theme_colors['info_bg'], 
                                         relief="solid", borderwidth=1)
        
        tk.Label(
            advanced_content_frame,
            text="Docker Compose Configuration",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(10, 5))
        
        tk.Label(
            advanced_content_frame,
            text="Docker Compose YAML files are automatically generated and stored internally.\n"
                 "Use these options if you need to customize or export the configuration.",
            font=("Arial", 9),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['hint_fg'],
            justify="center"
        ).pack(pady=(0, 10))
        
        # Buttons for YAML operations
        button_frame = tk.Frame(advanced_content_frame, bg=self.theme_colors['info_bg'])
        button_frame.pack(pady=(0, 10))
        
        tk.Button(
            button_frame,
            text="📄 View Generated YAML",
            font=("Arial", 10),
            command=lambda: messagebox.showinfo(
                "View YAML",
                "This would open a dialog showing the most recently\n"
                "generated Docker Compose YAML configuration.",
                parent=self
            ),
            width=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="💾 Export YAML File",
            font=("Arial", 10),
            command=lambda: messagebox.showinfo(
                "Export YAML",
                "This would let you save the YAML file to a custom\n"
                "location of your choice for external use.",
                parent=self
            ),
            width=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="📁 Open YAML Folder",
            font=("Arial", 10),
            command=lambda: messagebox.showinfo(
                "Open Folder",
                "This would open the ~/.nextcloud_backup_utility/compose/\n"
                "folder in your system's file explorer.",
                parent=self
            ),
            width=20
        ).pack(side="left", padx=5)
        
        # Add note about when to use these options
        note_frame = tk.Frame(advanced_content_frame, bg='#3a4f5f', relief='solid', borderwidth=1)
        note_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(
            note_frame,
            text="💡 When to use Advanced Options:",
            font=("Arial", 10, "bold"),
            bg='#3a4f5f',
            fg='#ffffff'
        ).pack(pady=(5, 2))
        
        use_cases = [
            "• Customize container configurations",
            "• Share YAML with team members",
            "• Debug container startup issues",
            "• Manually start containers with docker-compose",
            "• Archive configurations for documentation"
        ]
        
        for use_case in use_cases:
            tk.Label(
                note_frame,
                text=use_case,
                font=("Arial", 9),
                bg='#3a4f5f',
                fg='#ecf0f1',
                anchor='w'
            ).pack(anchor='w', padx=20, pady=1)
        
        tk.Label(note_frame, text="", bg='#3a4f5f').pack(pady=2)


def main():
    """Run the demo"""
    print("\n" + "=" * 60)
    print("Starting Automated YAML Workflow Demo")
    print("=" * 60 + "\n")
    
    app = AutomatedYAMLDemo()
    app.mainloop()


if __name__ == '__main__':
    main()
