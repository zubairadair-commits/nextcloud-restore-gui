# Scrolling Architecture Diagram

## Visual Hierarchy

```
Window (tk.Tk)
│
└── Container Frame (padding: 20px)
    │
    ├── Title Label (FIXED - outside scroll)
    │   "Schedule Backup Configuration"
    │
    └── Canvas + Scrollbar Layout
        │
        ├── Scrollbar (right side, vertical)
        │   │
        │   ├── command: canvas.yview
        │   └── fill: y
        │
        └── Canvas (left side, fills remaining space)
            │
            ├── bg: #f0f0f0 (theme color)
            ├── highlightthickness: 0 (no border)
            └── yscrollcommand: scrollbar.set
            
            └── Canvas Window
                │
                └── Scrollable Frame (SCROLLABLE - contains all content)
                    │
                    ├── Status Section (create_status_section)
                    │   └── Current backup status info
                    │
                    ├── Config Section (create_config_section)
                    │   ├── Backup Directory
                    │   ├── Frequency selector
                    │   ├── Time picker
                    │   ├── Cloud sync folders
                    │   └── CREATE/UPDATE BUTTON
                    │
                    └── Setup Guide Section (create_setup_guide)
                        └── Cloud storage instructions
```

---

## Event Flow Diagram

### Window Resize or Content Change
```
User resizes window / Content changes
            ↓
    <Configure> event triggered
            ↓
    configure_scroll() function called
            ↓
    ┌──────────────────────────────────┐
    │ canvas.configure(                │
    │   scrollregion=canvas.bbox("all")│
    │ )                                │
    └──────────────────────────────────┘
            ↓
    ┌──────────────────────────────────┐
    │ canvas.itemconfig(               │
    │   canvas_window,                 │
    │   width=canvas_width             │
    │ )                                │
    └──────────────────────────────────┘
            ↓
    Scroll region updated ✅
    Content width adjusted ✅
```

### Mouse Wheel Scroll
```
User scrolls mouse wheel
            ↓
    Platform-specific event triggered
            ↓
    ┌─────────────┬─────────────┬─────────────┐
    │  Windows    │    macOS    │    Linux    │
    │<MouseWheel> │<MouseWheel> │ <Button-4>  │
    │             │             │ <Button-5>  │
    └─────────────┴─────────────┴─────────────┘
            ↓
    on_mouse_wheel() function called
            ↓
    ┌──────────────────────────────────┐
    │ Check event type:                │
    │                                  │
    │ if event.delta:                  │
    │   → Windows/Mac                  │
    │   → Scroll by delta/120 units    │
    │                                  │
    │ elif event.num == 4:             │
    │   → Linux scroll up              │
    │   → Scroll -1 unit               │
    │                                  │
    │ elif event.num == 5:             │
    │   → Linux scroll down            │
    │   → Scroll +1 unit               │
    └──────────────────────────────────┘
            ↓
    canvas.yview_scroll() called
            ↓
    Canvas viewport moves ✅
    User sees different content ✅
```

---

## Component Relationships

```
┌─────────────────────────────────────────────────────────┐
│                    CONTAINER FRAME                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │              TITLE (Fixed Position)               │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌────────────────────────────────────────┐ ┌────────┐ │
│  │            CANVAS                      │ │SCROLL  │ │
│  │  ┌──────────────────────────────────┐ │ │  BAR   │ │
│  │  │    SCROLLABLE FRAME (viewport)   │ │ │        │ │
│  │  │  ┌────────────────────────────┐  │ │ │   ▲    │ │
│  │  │  │  Status Section            │  │ │ │   ║    │ │
│  │  │  └────────────────────────────┘  │ │ │   ║    │ │
│  │  │  ┌────────────────────────────┐  │ │ │   ║    │ │
│  │  │  │  Config Section            │  │ │ │   ║    │ │
│  │  │  │  - Directory               │  │ │ │   ║    │ │
│  │  │  │  - Frequency               │  │ │ │   ║    │ │
│  │  │  │  - Time                    │  │ │ │   ║    │ │
│  │  │  │  - Button                  │  │ │ │   ║    │ │
│  │  │  └────────────────────────────┘  │ │ │   ║    │ │
│  │  │  ┌────────────────────────────┐  │ │ │   ║    │ │
│  │  │  │  Setup Guide Section       │  │ │ │   ║    │ │
│  │  │  └────────────────────────────┘  │ │ │   ▼    │ │
│  │  └──────────────────────────────────┘ │ │        │ │
│  └────────────────────────────────────────┘ └────────┘ │
└─────────────────────────────────────────────────────────┘

Legend:
  ┌─┐  Frame/Container
  ║   Scrollbar track
  ▲▼  Scrollbar thumb (draggable)
```

---

## Data Flow

### Initialization
```
1. Create container frame
        ↓
2. Create title label (pack in container)
        ↓
3. Create canvas (pack left, fill both, expand)
        ↓
4. Create scrollbar (pack right, fill y)
        ↓
5. Create scrollable_frame (child of canvas)
        ↓
6. Create canvas window (holds scrollable_frame)
        ↓
7. Configure scroll region
        ↓
8. Bind mouse wheel events
        ↓
9. Add content to scrollable_frame
        ↓
10. Initial scroll region calculation
```

---

## Binding Map

### Event Bindings
```
┌──────────────────────────────────────────────────────┐
│ scrollable_frame                                     │
│   → bind("<Configure>", configure_scroll)            │
│   → Triggers when frame size/content changes         │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ canvas                                               │
│   → bind("<Configure>", configure_scroll)            │
│   → Triggers when canvas is resized                  │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ canvas (bind_all for global events)                 │
│   → bind_all("<MouseWheel>", on_mouse_wheel)        │
│      Windows/Mac mouse wheel                         │
│   → bind_all("<Button-4>", on_mouse_wheel)          │
│      Linux scroll up                                 │
│   → bind_all("<Button-5>", on_mouse_wheel)          │
│      Linux scroll down                               │
└──────────────────────────────────────────────────────┘
```

---

## State Management

### Stored References
```python
self.canvas = canvas
self.scrollbar = scrollbar
self.scrollable_frame = scrollable_frame
```

**Purpose:** 
- Allows future cleanup if page is destroyed
- Enables programmatic scrolling if needed
- Reference for debugging

---

## Coordinate System

### Canvas Coordinates
```
  Canvas (visible area)
  ┌─────────────────┐  ← y = 0 (top of visible area)
  │                 │
  │   Viewport      │  ← Shows portion of scrollable_frame
  │                 │
  └─────────────────┘  ← y = canvas_height (bottom of visible)
  
  Scrollable Frame (total content)
  ┌─────────────────┐  ← y = 0 (top of content)
  │   Status        │
  ├─────────────────┤
  │   Config        │
  ├─────────────────┤
  │   Guide         │
  └─────────────────┘  ← y = content_height (bottom of content)
  
  Scroll Region: (0, 0, content_width, content_height)
```

---

## Scroll Position Calculation

### Windows/macOS
```python
# event.delta is typically ±120 per notch
# Divide by 120 to get scroll "units"
# Negate to match expected scroll direction
scroll_amount = -1 * (event.delta / 120)
canvas.yview_scroll(int(scroll_amount), "units")
```

### Linux
```python
# Button-4 = scroll up (negative direction)
# Button-5 = scroll down (positive direction)
if event.num == 4:
    canvas.yview_scroll(-1, "units")  # Scroll up
elif event.num == 5:
    canvas.yview_scroll(1, "units")   # Scroll down
```

---

## Memory Considerations

### Lightweight Components
- Canvas: Single widget, minimal overhead
- Scrollbar: Single widget
- Frame: Container only
- Total: ~3 additional widgets

### No Performance Impact
- No image loading
- No complex calculations
- Standard Tkinter components
- Event-driven (no polling)

---

## Platform-Specific Notes

### Windows
- `event.delta`: Multiple of 120 (standard)
- Scrolling: Smooth and responsive
- Works with both mouse wheel and touchpad

### macOS
- `event.delta`: May vary by hardware
- Scrolling: Natural scroll direction
- Works with Magic Mouse and trackpad

### Linux
- Uses button events (not delta)
- `Button-4`: Scroll up
- `Button-5`: Scroll down
- Works with any mouse wheel

---

## Error Handling

### Safe Guards
```python
# Prevent division by zero
canvas_width = canvas.winfo_width()
if canvas_width > 1:  # Check valid width
    canvas.itemconfig(canvas_window, width=canvas_width)

# Handle both event types
if event.delta:  # Windows/Mac
    # ... handle delta
elif event.num == 5:  # Linux
    # ... handle button
elif event.num == 4:  # Linux
    # ... handle button
```

---

## Summary

This architecture provides:
- ✅ Clean separation of fixed vs scrollable content
- ✅ Cross-platform mouse wheel support
- ✅ Dynamic content adjustment
- ✅ Theme compatibility
- ✅ Minimal performance overhead
- ✅ Maintainable code structure
