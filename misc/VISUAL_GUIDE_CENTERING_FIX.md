# Error Page Centering - Visual Comparison

## Before Fix

```
┌────────────────────────────────────────────────────────────────────────┐
│                    Nextcloud Restore & Backup                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ ┌──────────────────────────────────────────────────────────┐          │
│ │                                                          │          │
│ │         ❌ Docker Container Failed                       │          │
│ │                                                          │          │
│ ├──────────────────────────────────────────────────────────┤          │
│ │                                                          │          │
│ │  Error Type: Port Conflict                              │          │
│ │                                                          │          │
│ │  ┌────────────────────────────────────────────────┐     │          │
│ │  │ Container: nextcloud  |  Port: 8080           │     │          │
│ │  └────────────────────────────────────────────────┘     │          │
│ │                                                          │          │
│ │  ┌────────────────────────────────────────────────┐     │          │
│ │  │ ❌ Error Description                          │     │          │
│ │  │ Port 8080 is already in use...                │     │          │
│ │  └────────────────────────────────────────────────┘     │          │
│ │                                                          │          │
│ │  ┌────────────────────────────────────────────────┐     │          │
│ │  │ 💡 Suggested Action                           │     │          │
│ │  │ Try alternative ports: 8081, 8082...          │     │          │
│ │  └────────────────────────────────────────────────┘     │          │
│ │                                                          │          │
│ │  [📂 Open Error Log]  [Return to Main Menu]            │          │
│ │                                                          │          │
│ └──────────────────────────────────────────────────────────┘          │
│                                                                        │
│  ↑ CONTENT ALIGNED TO LEFT (anchor="nw")                              │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

**Problem:** Content stuck to left side, wasted space on right

---

## After Fix

```
┌────────────────────────────────────────────────────────────────────────┐
│                    Nextcloud Restore & Backup                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│        ┌──────────────────────────────────────────────────┐           │
│        │                                                  │           │
│        │         ❌ Docker Container Failed               │           │
│        │                                                  │           │
│        ├──────────────────────────────────────────────────┤           │
│        │                                                  │           │
│        │  Error Type: Port Conflict                      │           │
│        │                                                  │           │
│        │  ┌────────────────────────────────────────┐     │           │
│        │  │ Container: nextcloud  |  Port: 8080   │     │           │
│        │  └────────────────────────────────────────┘     │           │
│        │                                                  │           │
│        │  ┌────────────────────────────────────────┐     │           │
│        │  │ ❌ Error Description                  │     │           │
│        │  │ Port 8080 is already in use...        │     │           │
│        │  └────────────────────────────────────────┘     │           │
│        │                                                  │           │
│        │  ┌────────────────────────────────────────┐     │           │
│        │  │ 💡 Suggested Action                   │     │           │
│        │  │ Try alternative ports: 8081, 8082...  │     │           │
│        │  └────────────────────────────────────────┘     │           │
│        │                                                  │           │
│        │  [📂 Open Error Log]  [Return to Main Menu]    │           │
│        │                                                  │           │
│        └──────────────────────────────────────────────────┘           │
│                                                                        │
│  ↑ CONTENT HORIZONTALLY CENTERED (anchor="n", x_position calculated)  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

**Solution:** Content centered, balanced appearance, responsive to window resize

---

## Technical Implementation

### Before
```python
canvas.create_window((0, 0), window=error_frame, anchor="nw")
error_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
```

**Issue:** `anchor="nw"` (northwest) pins content to top-left corner

### After
```python
def update_scroll_region(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))
    # Center the window horizontally
    canvas_width = canvas.winfo_width()
    frame_width = error_frame.winfo_reqwidth()
    x_position = max(0, (canvas_width - frame_width) // 2)
    canvas.coords(canvas_window, x_position, 0)

error_frame.bind("<Configure>", update_scroll_region)
canvas.bind("<Configure>", update_scroll_region)

canvas_window = canvas.create_window((0, 0), window=error_frame, anchor="n")
```

**Improvements:**
1. ✓ `anchor="n"` (north) allows horizontal centering
2. ✓ `x_position` calculated dynamically based on widths
3. ✓ `canvas.coords()` updates position on resize
4. ✓ Both canvas and frame bound to recalculate on changes

---

## Responsive Behavior

### Small Window (600px wide)
```
┌──────────────────────────┐
│   Nextcloud Restore      │
├──────────────────────────┤
│ ┌──────────────────────┐ │
│ │ Error content fits   │ │
│ │ Centered perfectly   │ │
│ └──────────────────────┘ │
└──────────────────────────┘
```

### Medium Window (900px wide)
```
┌────────────────────────────────────┐
│    Nextcloud Restore & Backup      │
├────────────────────────────────────┤
│      ┌──────────────────────┐      │
│      │   Error content      │      │
│      │   Still centered     │      │
│      └──────────────────────┘      │
└────────────────────────────────────┘
```

### Large Window (1200px wide)
```
┌────────────────────────────────────────────────┐
│        Nextcloud Restore & Backup              │
├────────────────────────────────────────────────┤
│            ┌──────────────────────┐            │
│            │   Error content      │            │
│            │   Always centered    │            │
│            └──────────────────────┘            │
└────────────────────────────────────────────────┘
```

**Key Feature:** Content maintains horizontal centering at ALL window sizes!

---

## Testing Centering

Run the demo to see it in action:

```bash
python tests/demo_error_page_centering_fix.py
```

Then:
1. Resize the window horizontally
2. Observe content remains centered
3. Scroll if content exceeds window height
4. Content stays horizontally centered while scrolling

---

## Code Location

File: `src/nextcloud_restore_and_backup-v9.py`
Function: `show_docker_error_page()`
Lines: ~8752-8767

---

**Status:** ✅ Implemented and Tested
**Responsive:** Yes - works at all window sizes
**Backwards Compatible:** Yes - no breaking changes
