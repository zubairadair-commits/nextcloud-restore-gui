# Quick Reference: 600px Centered Layout

## One-Line Summary
Wizard content is centered using `place(relx=0.5, anchor="n")` with a fixed 600px width, and all child widgets use `fill="x", padx=40`.

## Core Implementation

### Content Frame
```python
# Create centered content frame
self.wizard_scrollable_frame = tk.Frame(self.body_frame, width=600)
self.wizard_scrollable_frame.bind('<Configure>', maintain_width)
self.wizard_scrollable_frame.place(relx=0.5, anchor="n", y=10)
```

### Child Widgets
```python
# All widgets use this pattern
widget.pack(pady=X, fill="x", padx=40)
```

## Key Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `width` | 600 | Fixed content block width |
| `relx` | 0.5 | Horizontal center (50% of parent) |
| `anchor` | "n" | Top-center anchor point |
| `y` | 10 | Top padding |
| `fill` | "x" | Widget spans full width |
| `padx` | 40 | Side padding (520px effective width) |

## Layout Hierarchy

```
Window (900x900)
  └─ Body Frame (fills window)
      └─ Content Frame (600px, centered)
          ├─ Widget 1 (fill="x", padx=40)
          ├─ Widget 2 (fill="x", padx=40)
          └─ Widget N (fill="x", padx=40)
```

## Math

- Window width: 900px
- Content width: 600px
- Left margin: (900 - 600) / 2 = 150px
- Right margin: 150px
- Widget padding: 40px each side
- Effective widget width: 600 - (40 * 2) = 520px

## Adding New Content

### Simple Widgets (Labels, Buttons, Entries)
```python
tk.Label(parent, text="My Label", font=("Arial", 12)).pack(pady=5, fill="x", padx=40)
tk.Button(parent, text="My Button", font=("Arial", 11)).pack(pady=5, fill="x", padx=40)
tk.Entry(parent, font=("Arial", 11)).pack(pady=5, fill="x", padx=40)
```

### Frames (Info boxes, Containers)
```python
frame = tk.Frame(parent, bg="#e8f4f8", relief="solid", borderwidth=1)
frame.pack(pady=10, fill="x", padx=40)

# Content inside frame
tk.Label(frame, text="Content", bg="#e8f4f8").pack(fill="x", padx=10)
```

### Grid-Based Forms
```python
form_frame = tk.Frame(parent)
form_frame.pack(pady=10, fill="x", padx=40)

form_frame.grid_columnconfigure(0, weight=0)  # Label column
form_frame.grid_columnconfigure(1, weight=1)  # Entry column

tk.Label(form_frame, text="Field:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
tk.Entry(form_frame).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
```

## Common Patterns

### Page Header
```python
tk.Label(parent, text="Page Title", font=("Arial", 14, "bold")).pack(pady=(20, 5), fill="x", padx=40)
tk.Label(parent, text="Subtitle", font=("Arial", 10), fg="gray").pack(pady=(0, 5), fill="x", padx=40)
```

### Info Box
```python
info = tk.Frame(parent, bg="#e3f2fd", relief="solid", borderwidth=1)
info.pack(pady=10, fill="x", padx=40)
tk.Label(info, text="ℹ️ Info", font=("Arial", 10, "bold"), bg="#e3f2fd").pack(pady=5, fill="x", padx=10)
```

### Navigation Buttons
```python
nav = tk.Frame(parent)
nav.pack(pady=(30, 20), fill="x", padx=40)
tk.Button(nav, text="← Back", width=15).pack(side="left", padx=10)
tk.Button(nav, text="Next →", width=15, bg="#3daee9", fg="white").pack(side="left", padx=10)
```

## Testing

Run the test suite:
```bash
python3 test_centering_600px.py
```

Expected output:
```
======================================================================
Test Results: 6/6 passed
======================================================================
✅ All tests passed!
```

## Visual Validation

Open the application and verify:
1. Content block appears centered with visible margins on both sides
2. At 900x900 window size, margins should be ~150px on each side
3. All widgets align consistently within the content block
4. No horizontal scrollbar appears

## Troubleshooting

### Content not centered
- Check `place()` parameters: `relx=0.5, anchor="n"`
- Verify width is set to 600

### Widgets not aligned
- Check all widgets use `fill="x", padx=40`
- Verify no widgets use `anchor="center"` (should use `fill="x"` instead)

### Content too narrow/wide
- Adjust `width=600` in content frame creation
- Keep `padx=40` for consistent internal spacing

### Frame expands beyond 600px
- Ensure configure binding calls `config(width=600)`
- Check no child widgets have fixed widths that exceed available space

## Performance Notes

- **Memory**: Minimal - single frame, no canvas/scrollbar
- **CPU**: Negligible - place() geometry is efficient
- **Rendering**: Fast - direct frame rendering without canvas coordinate calculations

## Migration from Old Code

If you see this pattern, update it:
```python
# OLD: Canvas/scrollbar approach
container = tk.Frame(self.body_frame)
canvas = tk.Canvas(container)
scrollbar = tk.Scrollbar(container, ...)
scrollable_frame = tk.Frame(canvas, width=850)
# ... many lines of canvas setup ...

# NEW: Simple place approach
self.wizard_scrollable_frame = tk.Frame(self.body_frame, width=600)
self.wizard_scrollable_frame.place(relx=0.5, anchor="n", y=10)
```

If you see this pattern, update it:
```python
# OLD: Nested containers with anchor
entry_container = tk.Frame(parent)
entry_container.pack(pady=5, anchor="center", padx=30)
entry = tk.Entry(entry_container, width=80)
entry.pack()

# NEW: Direct packing with fill
entry = tk.Entry(parent)
entry.pack(pady=5, fill="x", padx=40)
```

## Best Practices

1. **Always use fill="x", padx=40** for direct children of content frame
2. **Never use fixed widths** on entry fields (let fill="x" handle it)
3. **Use consistent padding** (padx=40) across all pages
4. **Test at multiple window sizes** to verify centering maintained
5. **Keep content within 600px** - no need for scrolling

## Files to Reference

- **Implementation**: `nextcloud_restore_and_backup-v9.py` (lines ~995-1010)
- **Documentation**: `CENTERING_IMPLEMENTATION_600PX.md`
- **Comparison**: `BEFORE_AFTER_600PX_CENTERING.md`
- **Tests**: `test_centering_600px.py`
- **Screenshots**: `wizard_centered_600px.png`, `wizard_page2_centered_600px.png`

## Summary

The 600px centered layout is simple, effective, and maintainable:
- ✅ One frame with `place(relx=0.5, anchor="n")`
- ✅ Fixed width of 600px
- ✅ All children use `fill="x", padx=40`
- ✅ No canvas/scrollbar complexity
- ✅ Clear visual centering with margins
