# Scrolling Implementation - Quick Reference

## When to Use Scrolling

Add scrolling to a page when:
- Content height exceeds typical window sizes
- Users need access to buttons/controls at bottom
- Forms or configurations have many sections
- Dynamic content may vary in length

---

## Pattern: Canvas + Scrollbar + Mouse Wheel

### Step 1: Create Container
```python
# Replace direct frame packing with container
container = tk.Frame(parent, bg=self.theme_colors['bg'])
container.pack(fill="both", expand=True, padx=20, pady=20)
```

### Step 2: Add Fixed Elements (Optional)
```python
# Elements outside scroll area (e.g., title, back button)
title = tk.Label(
    container,
    text="Page Title",
    font=("Arial", 18, "bold"),
    bg=self.theme_colors['bg'],
    fg=self.theme_colors['fg']
)
title.pack(pady=(0, 10))
```

### Step 3: Create Scrollable Canvas
```python
# Canvas with matching background
canvas = tk.Canvas(
    container, 
    bg=self.theme_colors['bg'], 
    highlightthickness=0  # No border
)

# Vertical scrollbar
scrollbar = tk.Scrollbar(
    container, 
    orient="vertical", 
    command=canvas.yview
)

# Frame to hold content
scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])

# Link canvas and scrollbar
canvas.configure(yscrollcommand=scrollbar.set)

# Pack scrollbar first (right side), then canvas
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Create window in canvas
canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
```

### Step 4: Configure Scroll Region
```python
def configure_scroll(event=None):
    """Update scroll region when content changes"""
    # Set scroll region to encompass all content
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Match frame width to canvas width
    canvas_width = canvas.winfo_width()
    if canvas_width > 1:
        canvas.itemconfig(canvas_window, width=canvas_width)

# Bind to Configure events
scrollable_frame.bind("<Configure>", configure_scroll)
canvas.bind("<Configure>", configure_scroll)
```

### Step 5: Add Mouse Wheel Support
```python
def on_mouse_wheel(event):
    """Handle mouse wheel scrolling - cross-platform"""
    # Windows & macOS
    if event.delta:
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    # Linux scroll down
    elif event.num == 5:
        canvas.yview_scroll(1, "units")
    # Linux scroll up
    elif event.num == 4:
        canvas.yview_scroll(-1, "units")

# Bind to all platforms
canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows/Mac
canvas.bind_all("<Button-4>", on_mouse_wheel)    # Linux up
canvas.bind_all("<Button-5>", on_mouse_wheel)    # Linux down
```

### Step 6: Add Content to Scrollable Frame
```python
# All your content goes in scrollable_frame
# Instead of:
#   self.create_section(main_frame)
# Use:
#   self.create_section(scrollable_frame)

# Example:
config_frame = tk.LabelFrame(
    scrollable_frame,  # ← Use scrollable_frame as parent
    text="Configuration",
    bg=self.theme_colors['bg'],
    fg=self.theme_colors['fg']
)
config_frame.pack(fill="x", pady=10)
```

---

## Complete Template

```python
def show_my_page(self):
    """Show a scrollable page."""
    # Clear current content
    for widget in self.body_frame.winfo_children():
        widget.destroy()
    
    # 1. Create container
    container = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
    container.pack(fill="both", expand=True, padx=20, pady=20)
    
    # 2. Optional: Add fixed header
    title = tk.Label(
        container,
        text="Page Title",
        font=("Arial", 18, "bold"),
        bg=self.theme_colors['bg'],
        fg=self.theme_colors['fg']
    )
    title.pack(pady=(0, 10))
    
    # 3. Create scrollable canvas
    canvas = tk.Canvas(container, bg=self.theme_colors['bg'], highlightthickness=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
    
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    # 4. Configure scroll region
    def configure_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas_width = canvas.winfo_width()
        if canvas_width > 1:
            canvas.itemconfig(canvas_window, width=canvas_width)
    
    scrollable_frame.bind("<Configure>", configure_scroll)
    canvas.bind("<Configure>", configure_scroll)
    
    # 5. Add mouse wheel support
    def on_mouse_wheel(event):
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")
        elif event.num == 4:
            canvas.yview_scroll(-1, "units")
    
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    canvas.bind_all("<Button-4>", on_mouse_wheel)
    canvas.bind_all("<Button-5>", on_mouse_wheel)
    
    # 6. Add your content to scrollable_frame
    tk.Label(
        scrollable_frame,
        text="Your content here",
        bg=self.theme_colors['bg'],
        fg=self.theme_colors['fg']
    ).pack(pady=20)
    
    # ... more widgets ...
    
    # Apply theme
    self.apply_theme_recursive(scrollable_frame)
```

---

## Common Pitfalls

### ❌ Don't: Forget highlightthickness=0
```python
canvas = tk.Canvas(container, bg=self.theme_colors['bg'])
# Result: Visible border around canvas
```

### ✅ Do: Set highlightthickness=0
```python
canvas = tk.Canvas(container, bg=self.theme_colors['bg'], highlightthickness=0)
# Result: Clean, borderless appearance
```

---

### ❌ Don't: Pack canvas before scrollbar
```python
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
# Result: Scrollbar may not appear properly
```

### ✅ Do: Pack scrollbar first
```python
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
# Result: Correct layout
```

---

### ❌ Don't: Use only Windows mouse wheel binding
```python
canvas.bind_all("<MouseWheel>", on_mouse_wheel)
# Result: Doesn't work on Linux
```

### ✅ Do: Bind all platforms
```python
canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows/Mac
canvas.bind_all("<Button-4>", on_mouse_wheel)    # Linux
canvas.bind_all("<Button-5>", on_mouse_wheel)    # Linux
# Result: Works everywhere
```

---

### ❌ Don't: Forget to update scroll region
```python
# No configure_scroll function
# Result: Scroll region doesn't adjust when content changes
```

### ✅ Do: Bind Configure events
```python
def configure_scroll(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas_width = canvas.winfo_width()
    if canvas_width > 1:
        canvas.itemconfig(canvas_window, width=canvas_width)

scrollable_frame.bind("<Configure>", configure_scroll)
canvas.bind("<Configure>", configure_scroll)
# Result: Dynamic scroll region
```

---

## Theme Compatibility

### Light Theme
```python
canvas = tk.Canvas(container, bg='#f0f0f0', highlightthickness=0)
scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
```

### Dark Theme
```python
canvas = tk.Canvas(container, bg='#1e1e1e', highlightthickness=0)
scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
```

### Dynamic Theme (Best Practice)
```python
canvas = tk.Canvas(
    container, 
    bg=self.theme_colors['bg'], 
    highlightthickness=0
)
scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
```

---

## Mouse Wheel Event Reference

### Windows & macOS
- **Event:** `<MouseWheel>`
- **Attribute:** `event.delta`
- **Values:** 
  - Positive (scroll up): typically +120
  - Negative (scroll down): typically -120
  - May vary by hardware

### Linux
- **Events:** `<Button-4>` (up), `<Button-5>` (down)
- **Attribute:** `event.num`
- **Values:**
  - Scroll up: event.num == 4
  - Scroll down: event.num == 5

---

## Testing Checklist

- [ ] Canvas created with `highlightthickness=0`
- [ ] Scrollbar properly linked to canvas
- [ ] `scrollable_frame` created as child of canvas
- [ ] Canvas window created with `anchor="nw"`
- [ ] `configure_scroll` function updates scroll region
- [ ] Width adjustment in `configure_scroll`
- [ ] Configure events bound to both canvas and frame
- [ ] `on_mouse_wheel` function handles `event.delta`
- [ ] `on_mouse_wheel` function handles `event.num`
- [ ] Windows binding: `<MouseWheel>`
- [ ] Linux bindings: `<Button-4>` and `<Button-5>`
- [ ] All content uses `scrollable_frame` as parent
- [ ] Theme colors applied consistently
- [ ] Test on small window size (e.g., 500x400)

---

## Performance Considerations

### Good Performance ✅
- Canvas with moderate content (< 1000 widgets)
- Properly configured scroll region
- Efficient widget packing
- Minimal redraws

### Potential Issues ⚠️
- Thousands of widgets in scroll area
- Complex nested frames
- Heavy images in scrollable area
- Frequent scroll region updates

---

## Real Example from Schedule Backup

```python
# Before: Simple frame
main_frame = tk.Frame(self, bg="#f0f0f0")
main_frame.pack(fill="both", expand=True, padx=20, pady=20)
self.create_config_section(main_frame)

# After: Scrollable with mouse wheel
container = tk.Frame(self, bg="#f0f0f0")
container.pack(fill="both", expand=True, padx=20, pady=20)

canvas = tk.Canvas(container, bg="#f0f0f0", highlightthickness=0)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

# ... (full setup as shown above) ...

self.create_config_section(scrollable_frame)  # ← Changed parent
```

---

## Summary

**Key Points:**
1. Use Canvas + Scrollbar for scrollable content
2. Add mouse wheel support for all platforms
3. Configure scroll region dynamically
4. Keep theme colors consistent
5. Test on small window sizes

**When Done Right:**
- ✅ Works on Windows, Mac, Linux
- ✅ Smooth mouse wheel scrolling
- ✅ All content accessible
- ✅ Theme-compatible
- ✅ Clean visual appearance
