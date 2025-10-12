# UI Centering Fix - Technical Diagram

## Visual Layout Structure

### Before Fix (Content Appeared Left-Aligned)

```
┌─────────────────────────────────────────────────────────────────┐
│ Window (700px or more)                                          │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ body_frame (expandable)                                     │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ Canvas (full width)                                     │ │ │
│ │ │                                                         │ │ │
│ │ │ ┌─────────────────────────────────────────────────────┐ │ │ │
│ │ │ │ Scrollable Frame (expands to fill canvas)         │ │ │ │
│ │ │ │                                                     │ │ │ │
│ │ │ │ Step 1: Select Backup Archive                      │ │ │ │
│ │ │ │ [Entry field stretches.....................]        │ │ │ │
│ │ │ │ [Browse...]                                        │ │ │ │
│ │ │ │                                                     │ │ │ │
│ │ │ │ Step 2: Database Configuration                     │ │ │ │
│ │ │ │ Database Name:  [Entry.................]           │ │ │ │
│ │ │ │ Database User:  [Entry.................]           │ │ │ │
│ │ │ │                                                     │ │ │ │
│ │ │ └─────────────────────────────────────────────────────┘ │ │ │
│ │ │                                                         │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

Problem: Frame expands to full width → content appears left-aligned
```

### After Fix (Content Truly Centered)

```
┌─────────────────────────────────────────────────────────────────┐
│ Window (700px or more)                                          │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ body_frame (expandable)                                     │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ container (fill="both", expand=True)                    │ │ │
│ │ │                                                         │ │ │
│ │ │ ┌─────────────────────────────────────────────────────┐ │ │ │
│ │ │ │ Canvas (full width, provides centering context)   │ │ │ │
│ │ │ │                                                     │ │ │ │
│ │ │ │        ┌──────────────────────────┐                │ │ │ │
│ │ │ │        │ Scrollable Frame (700px) │                │ │ │ │
│ │ │ │        │                          │                │ │ │ │
│ │ │ │        │ Step 1: Select Archive   │                │ │ │ │
│ │ │ │        │ [Entry field.........]   │                │ │ │ │
│ │ │ │        │      [Browse...]         │                │ │ │ │
│ │ │ │        │                          │                │ │ │ │
│ │ │ │        │ Step 2: Database Config  │                │ │ │ │
│ │ │ │        │ DB Name: [Entry.......]  │                │ │ │ │
│ │ │ │        │ DB User: [Entry.......]  │                │ │ │ │
│ │ │ │        │                          │                │ │ │ │
│ │ │ │        └──────────────────────────┘                │ │ │ │
│ │ │ │               ↑ Centered block ↑                  │ │ │ │
│ │ │ └─────────────────────────────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

Solution: Frame has fixed 700px width → centered as a block
```

## Frame Hierarchy

### Implementation Structure

```
NextcloudRestoreWizard (tk.Tk)
│
├─ header_frame
│  └─ "Nextcloud Restore & Backup Utility" (title)
│
├─ status_label
│
└─ body_frame (fill="both", expand=True)
    │
    └─ container (NEW - fill="both", expand=True)
        │
        ├─ canvas (side="left", fill="both", expand=True)
        │  │
        │  └─ canvas_window (anchor="n", positioned at center)
        │      │
        │      └─ scrollable_frame (width=700)  ← KEY FIX
        │          │
        │          ├─ Page title label
        │          ├─ Return button
        │          ├─ create_wizard_page1/2/3 content
        │          ├─ Navigation buttons
        │          ├─ Error label
        │          └─ Progress widgets
        │
        └─ scrollbar (side="right", fill="y")
```

## Centering Mathematics

### Coordinate Calculation

```python
# Window dimensions
window_width = 700  # or larger if user resizes
canvas_width = window_width - scrollbar_width  # ~680px

# Center calculation
center_x = canvas_width // 2  # 680 // 2 = 340px

# Frame positioning
canvas.coords(canvas_window, center_x, 0)
# With anchor="n":
#   - Frame's top-center point positioned at (340, 0)
#   - Frame extends 350px left and 350px right of center
#   - Result: Frame perfectly centered
```

### Example at Different Window Sizes

#### Small Window (700px)
```
Canvas width: ~680px
Center X: 340px
Frame: 700px width (extends slightly beyond if needed)
Result: Content fills most of window, centered
```

#### Medium Window (1000px)
```
Canvas width: ~980px
Center X: 490px
Frame: 700px width
Left margin: 140px
Right margin: 140px
Result: Content block centered with margins
```

#### Large Window (1400px)
```
Canvas width: ~1380px
Center X: 690px
Frame: 700px width
Left margin: 340px
Right margin: 340px
Result: Content block centered with large margins
```

## Dynamic Centering Flow

```
┌─────────────────────────────────────┐
│ User Action: Window Resize          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Event: <Configure> triggered        │
│ - Canvas size changed                │
│ - Scrollable frame configured        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Handler: on_configure(e)            │
│ 1. Update scroll region             │
│ 2. Get canvas.winfo_width()         │
│ 3. Calculate: center = width // 2   │
│ 4. canvas.coords(window, center, 0) │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Result: Frame Re-centered           │
│ - Content block stays centered      │
│ - Margins adjust automatically      │
└─────────────────────────────────────┘
```

## Anchor Point Visualization

### How anchor="n" (North/Top-Center) Works

```
Scrollable Frame (700px width)

        ┌────────────────────────────────┐
        │                                │
        │        ↓ Anchor point          │
        │        (X=center, Y=0)         │
┌───────┼────────●────────────────────────┼───────┐
│       │   350px│        350px           │       │
│       │   ←────┴────→                   │       │
│       │        CONTENT                  │       │
│       │        BLOCK                    │       │
│       │        (700px)                  │       │
│       │                                 │       │
│       └─────────────────────────────────┘       │
│                   Canvas                        │
└─────────────────────────────────────────────────┘
         ↑                                ↑
    Left margin                      Right margin
    (auto-calculated)                (auto-calculated)
```

### Comparison with Other Anchors

```
anchor="nw" (northwest/top-left):
┌●──────────────────┐
│ Content....       │  ← Content pushed to left
│                   │
└───────────────────┘

anchor="n" (north/top-center):
        ●
   ┌────┴────┐
   │ Content │  ← Content centered
   └─────────┘

anchor="center" (center both axes):
   ┌─────────┐
   │    ●    │  ← Would center vertically too (not desired)
   │ Content │
   └─────────┘
```

## Responsive Behavior

### On Window Resize

```
Initial (700px window):
├──────────────────────────────────┤
│ [  Content Block (700px)       ] │
├──────────────────────────────────┤

Enlarged (1000px window):
├────────────────────────────────────────────┤
│      [  Content Block (700px)       ]      │
├────────────────────────────────────────────┤
      ↑ Auto margins ↑           ↑ Auto ↑

Maximized (1400px window):
├────────────────────────────────────────────────────┤
│           [  Content Block (700px)       ]         │
├────────────────────────────────────────────────────┤
           ↑ Larger margins ↑         ↑ Larger ↑
```

## Code Flow Sequence

```
1. Application Start
   ↓
2. create_wizard() called
   ↓
3. Create container frame (NEW)
   container = tk.Frame(body_frame)
   container.pack(fill="both", expand=True)
   ↓
4. Create canvas within container (CHANGED)
   canvas = tk.Canvas(container)
   ↓
5. Create scrollable_frame with width constraint (NEW)
   scrollable_frame = tk.Frame(canvas, width=700)
   ↓
6. Create canvas_window with anchor="n"
   canvas_window = canvas.create_window((0, 0), scrollable_frame, anchor="n")
   ↓
7. Bind configure events
   scrollable_frame.bind("<Configure>", on_configure)
   canvas.bind("<Configure>", on_configure)
   ↓
8. Pack canvas and scrollbar
   canvas.pack(side="left", fill="both", expand=True)
   scrollbar.pack(side="right", fill="y")
   ↓
9. Force initial centering
   canvas_width = canvas.winfo_width()
   canvas.coords(canvas_window, canvas_width // 2, 0)
   ↓
10. Result: Content centered!
```

## Key Technical Points

### 1. Container Frame Purpose
- Provides proper parent for canvas and scrollbar
- Enables expand=True to work correctly
- Creates centering context

### 2. Fixed Width Significance
- `width=700` prevents frame from expanding to full canvas width
- Allows frame to be smaller than canvas
- Makes centering mathematically possible

### 3. Anchor="n" Behavior
- Positions frame by its top-center point
- When X = canvas_width // 2, frame centers horizontally
- Y = 0 keeps content at top (no vertical centering)

### 4. Dynamic Updates
- `on_configure` recalculates center on every resize
- Ensures content stays centered at all window sizes
- No manual adjustment needed

## Summary

The fix transforms the wizard from a full-width layout (where centering was only visual within a wide frame) to a constrained-width layout (where the content block itself is centered). This achieves true block centering that is responsive, maintainable, and visually balanced.
