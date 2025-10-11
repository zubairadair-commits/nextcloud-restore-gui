# Canvas Centering Fix

## Issue
The wizard pages were displaying with all form elements left-aligned despite previous attempts to center them. The header was centered, but the form content appeared on the left side of the window.

## Root Cause
The issue was in the `create_wizard()` method where the canvas window was created with `anchor="nw"` (northwest/top-left):

```python
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
```

This caused the entire scrollable frame to be anchored to the top-left corner of the canvas, making all content appear left-aligned regardless of individual element `anchor="center"` settings.

## Solution
Changed the canvas window anchor from `"nw"` to `"n"` (north/top-center) and added dynamic horizontal centering:

```python
# Create window with north (top-center) anchor for horizontal centering
self.canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
```

Added dynamic repositioning that recalculates the center position whenever the canvas is resized:

```python
def on_configure(e):
    canvas.configure(scrollregion=canvas.bbox("all"))
    # Center the window horizontally
    canvas_width = canvas.winfo_width()
    if canvas_width > 1:  # Only update if canvas has been rendered
        canvas.coords(self.canvas_window, canvas_width // 2, 0)

# Bind both scrollable_frame and canvas to re-center on resize
scrollable_frame.bind("<Configure>", on_configure)
canvas.bind("<Configure>", on_configure)
```

## Result
- All form elements (labels, inputs, buttons) are now horizontally centered on all wizard pages
- The centering is responsive and adapts to window resizing
- Vertical alignment remains unchanged
- All previous functionality is preserved

## Technical Details
- The `anchor="n"` parameter centers the window horizontally while keeping it at the top (Y=0)
- The `canvas.coords()` method dynamically updates the X coordinate to `canvas_width // 2`
- The center position is recalculated on both canvas resize and scrollable_frame configuration changes
- This ensures proper centering regardless of window size or content changes
