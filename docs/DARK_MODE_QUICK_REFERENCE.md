# Dark Mode Quick Reference

## For Developers: Adding Theme Support to New Panels

This guide shows how to ensure new panels/dialogs respect the dark mode theme.

---

## Step 1: Use Theme Colors for All Widgets

### Frame/Container
```python
# ❌ BAD - No background color
frame = tk.Frame(self.body_frame)

# ✅ GOOD - Uses theme background
frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
```

### Labels
```python
# ❌ BAD - No colors specified
label = tk.Label(frame, text="My Label", font=("Arial", 12))

# ✅ GOOD - Uses theme colors
label = tk.Label(frame, text="My Label", font=("Arial", 12),
                bg=self.theme_colors['bg'], fg=self.theme_colors['fg'])

# For hint/secondary text
hint_label = tk.Label(frame, text="Help text", font=("Arial", 10),
                     bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg'])
```

### Entry Fields
```python
# ❌ BAD - Default colors
entry = tk.Entry(frame, font=("Arial", 11))

# ✅ GOOD - Themed entry field
entry = tk.Entry(frame, font=("Arial", 11),
                bg=self.theme_colors['entry_bg'],
                fg=self.theme_colors['entry_fg'],
                insertbackground=self.theme_colors['entry_fg'])  # Cursor color
```

### Buttons
```python
# ❌ BAD - System default button
button = tk.Button(frame, text="Click Me", command=self.action)

# ✅ GOOD - Themed button
button = tk.Button(frame, text="Click Me",
                  bg=self.theme_colors['button_bg'],
                  fg=self.theme_colors['button_fg'],
                  command=self.action)

# For branded primary action buttons (intentional color)
primary_button = tk.Button(frame, text="Start Action",
                          bg="#45bf55",  # Branded green
                          fg="white",
                          command=self.start_action)
```

### Radio Buttons
```python
# ❌ BAD - System defaults
radio = tk.Radiobutton(frame, text="Option 1", variable=var, value="opt1")

# ✅ GOOD - Themed radio button
radio = tk.Radiobutton(frame, text="Option 1", variable=var, value="opt1",
                      bg=self.theme_colors['bg'],
                      fg=self.theme_colors['fg'],
                      selectcolor=self.theme_colors['entry_bg'])
```

### Checkboxes
```python
# ❌ BAD - System defaults
check = tk.Checkbutton(frame, text="Enable Feature", variable=var)

# ✅ GOOD - Themed checkbox
check = tk.Checkbutton(frame, text="Enable Feature", variable=var,
                      bg=self.theme_colors['bg'],
                      fg=self.theme_colors['fg'],
                      selectcolor=self.theme_colors['entry_bg'])
```

### Info/Status Frames
```python
# ❌ BAD - Hardcoded light blue
info_frame = tk.Frame(frame, bg="#e8f4f8", relief="ridge", borderwidth=2)

# ✅ GOOD - Themed info background
info_frame = tk.Frame(frame, bg=self.theme_colors['info_bg'], 
                     relief="ridge", borderwidth=2)

# Info label inside
info_label = tk.Label(info_frame, text="ℹ️ Information",
                     bg=self.theme_colors['info_bg'],
                     fg=self.theme_colors['info_fg'])
```

---

## Step 2: Apply Theme Recursively

At the end of your panel creation method, call:

```python
def my_panel_method(self):
    # Create all widgets...
    frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
    # ... more widgets ...
    
    # Apply theme to all child widgets
    self.apply_theme_recursive(frame)
```

This ensures:
- Any widgets without explicit theme colors get themed
- Child frames and their contents are themed
- Theme switching updates all widgets automatically

---

## Step 3: Theme Color Reference

### Available Theme Colors

| Color Key | Light Theme | Dark Theme | Usage |
|-----------|-------------|------------|-------|
| `bg` | `#f0f0f0` | `#1e1e1e` | Main backgrounds |
| `fg` | `#000000` | `#e0e0e0` | Primary text |
| `button_bg` | `#e0e0e0` | `#2d2d2d` | Button backgrounds |
| `button_fg` | `#000000` | `#e0e0e0` | Button text |
| `entry_bg` | `#ffffff` | `#2d2d2d` | Input fields |
| `entry_fg` | `#000000` | `#e0e0e0` | Input text |
| `info_bg` | `#e3f2fd` | `#1a3a4a` | Info/status panels |
| `info_fg` | `#000000` | `#e0e0e0` | Info/status text |
| `warning_fg` | `#2e7d32` | `#7cb342` | Success/active states |
| `error_fg` | `#d32f2f` | `#ef5350` | Error states |
| `hint_fg` | `#666666` | `#999999` | Secondary/hint text |

### Access Theme Colors

```python
# In any method of NextcloudRestoreWizard class:
bg_color = self.theme_colors['bg']
text_color = self.theme_colors['fg']
```

---

## Step 4: Testing Your Panel

### Create a Test

Add a test to `test_panel_dark_mode.py`:

```python
def test_my_new_panel_theme():
    """Test that My New Panel uses theme colors"""
    print("\nTEST: My New Panel - Theme Colors")
    
    with open('nextcloud_restore_and_backup-v9.py', 'r') as f:
        content = f.read()
    
    # Find your method
    pattern = r'def my_panel_method\(self\):(.*?)(?=\n    def |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find my_panel_method")
        return False
    
    method_content = match.group(1)
    
    # Check for theme usage
    has_theme = "self.theme_colors['bg']" in method_content
    has_recursive = 'apply_theme_recursive' in method_content
    
    print(f"  - Uses theme colors: {'✓' if has_theme else '✗'}")
    print(f"  - Applies recursively: {'✓' if has_recursive else '✗'}")
    
    if has_theme and has_recursive:
        print("✅ PASS: My New Panel uses theme colors")
        return True
    else:
        print("❌ FAIL: My New Panel missing theme support")
        return False
```

### Manual Testing

1. **Light Mode:**
   - Navigate to your new panel
   - Verify all text is readable (black on light backgrounds)
   - Check entry fields have white backgrounds
   - Verify buttons have appropriate contrast

2. **Dark Mode:**
   - Toggle to dark mode (☀️ button in header)
   - Navigate to your new panel
   - Verify all text is readable (light on dark backgrounds)
   - Check entry fields have dark backgrounds
   - Verify all UI elements are visible

---

## Common Pitfalls

### ❌ Don't Use Hardcoded Colors
```python
# BAD - Will look wrong in dark mode
label = tk.Label(frame, text="Error", fg="red", bg="white")

# BAD - Hardcoded hex colors
status_frame = tk.Frame(frame, bg="#e8f4f8")
```

### ✅ Use Theme Colors Instead
```python
# GOOD - Uses theme colors
label = tk.Label(frame, text="Error", 
                fg=self.theme_colors['error_fg'],
                bg=self.theme_colors['bg'])

# GOOD - Theme-aware info frame
status_frame = tk.Frame(frame, bg=self.theme_colors['info_bg'])
```

### ❌ Don't Skip `apply_theme_recursive`
```python
def my_panel(self):
    frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
    # ... create widgets ...
    # MISSING: self.apply_theme_recursive(frame)
```

Without this, theme switching won't update your panel!

### ✅ Always Call It
```python
def my_panel(self):
    frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
    # ... create widgets ...
    
    # GOOD - Apply theme recursively
    self.apply_theme_recursive(frame)
```

---

## Exceptions: When to Use Hardcoded Colors

### Primary Action Buttons
Branded colors for important actions can be hardcoded:

```python
# OK - Branded primary action button
start_btn = tk.Button(frame, 
                     text="Start Instance",
                     bg="#f7b32b",  # Yellow branding
                     fg="white",
                     command=self.start_action)
```

**When to use:**
- Main call-to-action buttons
- Buttons that should stand out visually
- Branded colors that define the app's identity

**Document in tests:**
```python
# In your test, add to allowed_colors list:
allowed_colors = ['#f7b32b', 'white']  # Branded button
```

### Clickable Links
Blue is standard for links across themes:

```python
# OK - Consistent link color
link_label = tk.Label(frame,
                     text="http://example.com",
                     fg="#3daee9",  # Blue for clickability
                     cursor="hand2")
```

**Why:** Users expect links to be blue - it's a web standard.

---

## Quick Checklist

When adding a new panel, verify:

- [ ] Main frame uses `bg=self.theme_colors['bg']`
- [ ] All labels use `bg=self.theme_colors['bg']` and `fg=self.theme_colors['fg']`
- [ ] Entry fields use `entry_bg` and `entry_fg` theme colors
- [ ] Buttons use `button_bg` and `button_fg` (or branded colors)
- [ ] Info/status frames use `info_bg` and `info_fg`
- [ ] Hint text uses `hint_fg` for reduced emphasis
- [ ] Success indicators use `warning_fg` color
- [ ] Error indicators use `error_fg` color
- [ ] `apply_theme_recursive()` is called at end of method
- [ ] Test added to validate theme support
- [ ] Tested manually in both light and dark modes

---

## Example: Complete Themed Panel

```python
def show_my_feature(self):
    """Show my new feature panel with proper theme support."""
    # Clear current content
    for widget in self.body_frame.winfo_children():
        widget.destroy()
    
    # Main frame with theme background
    frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
    frame.pack(pady=20, fill="both", expand=True)
    
    # Back button
    tk.Button(
        frame,
        text="Return to Main Menu",
        font=("Arial", 12),
        bg=self.theme_colors['button_bg'],
        fg=self.theme_colors['button_fg'],
        command=self.show_landing
    ).pack(pady=8)
    
    # Title
    tk.Label(
        frame,
        text="My Feature",
        font=("Arial", 18, "bold"),
        bg=self.theme_colors['bg'],
        fg=self.theme_colors['fg']
    ).pack(pady=15)
    
    # Info frame
    info_frame = tk.Frame(frame, bg=self.theme_colors['info_bg'],
                         relief="ridge", borderwidth=2)
    info_frame.pack(pady=10, fill="x", padx=40)
    
    tk.Label(
        info_frame,
        text="ℹ️ Information about my feature",
        font=("Arial", 11),
        bg=self.theme_colors['info_bg'],
        fg=self.theme_colors['info_fg']
    ).pack(pady=10)
    
    # Config section
    config_frame = tk.Frame(frame, bg=self.theme_colors['bg'])
    config_frame.pack(pady=20, fill="x", padx=40)
    
    # Label
    tk.Label(
        config_frame,
        text="Configuration:",
        font=("Arial", 12, "bold"),
        bg=self.theme_colors['bg'],
        fg=self.theme_colors['fg']
    ).pack(pady=5)
    
    # Entry field
    entry_var = tk.StringVar()
    entry = tk.Entry(
        config_frame,
        textvariable=entry_var,
        font=("Arial", 11),
        bg=self.theme_colors['entry_bg'],
        fg=self.theme_colors['entry_fg'],
        insertbackground=self.theme_colors['entry_fg']
    )
    entry.pack(pady=5, fill="x")
    
    # Hint text
    tk.Label(
        config_frame,
        text="Enter your configuration value",
        font=("Arial", 10),
        bg=self.theme_colors['bg'],
        fg=self.theme_colors['hint_fg']
    ).pack(pady=(0, 10))
    
    # Primary action button (branded color)
    tk.Button(
        config_frame,
        text="Save Configuration",
        font=("Arial", 13, "bold"),
        bg="#45bf55",  # Branded green
        fg="white",
        command=lambda: self.save_config(entry_var.get())
    ).pack(pady=20)
    
    # Apply theme recursively to ensure all widgets are themed
    self.apply_theme_recursive(frame)
```

---

## Summary

**Golden Rules:**
1. Always use `self.theme_colors[...]` for colors
2. Always call `self.apply_theme_recursive(frame)` at the end
3. Test in both light and dark modes
4. Document any intentional hardcoded colors

**Result:**
- Users get consistent theme experience
- Dark mode works perfectly
- Theme switching updates automatically
- Professional, polished appearance
