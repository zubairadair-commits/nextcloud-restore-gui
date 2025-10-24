# UI Changes Guide - Scheduled Task Management & Clickable URLs

## Overview

This document describes the visual changes made to the Nextcloud Restore GUI's Tailscale wizard interface.

## 1. Enhanced Tailscale Configuration Page

### New Scheduled Task Status Panel

When a scheduled task exists, a new status panel appears in the Tailscale Configuration wizard:

```
┌─────────────────────────────────────────────────────────────────┐
│  📅 Scheduled Task Status                                       │
│                                                                   │
│  Status: ✓ Enabled                                              │
│  Configured Port: 8080                                           │
│  Next Run: At logon                                              │
│                                                                   │
│  [⏸ Disable Auto-Start] [🗑️ Remove Task]                       │
└─────────────────────────────────────────────────────────────────┘
```

**When Disabled:**
```
┌─────────────────────────────────────────────────────────────────┐
│  📅 Scheduled Task Status                                       │
│                                                                   │
│  Status: ✗ Disabled                                             │
│  Configured Port: 8080                                           │
│                                                                   │
│  [▶️ Enable Auto-Start] [🗑️ Remove Task]                       │
└─────────────────────────────────────────────────────────────────┘
```

### Location

The status panel appears:
- **In the Tailscale Configuration wizard** (`⚙️ Configure Remote Access`)
- **Above the auto-serve checkbox section**
- **Only when a scheduled task exists**

### Button States

1. **When Task is Enabled**:
   - Show "⏸ Disable Auto-Start" button
   - Show "🗑️ Remove Task" button (red)

2. **When Task is Disabled**:
   - Show "▶️ Enable Auto-Start" button (green)
   - Show "🗑️ Remove Task" button (red)

3. **When No Task Exists**:
   - No status panel shown
   - Only the checkbox "Enable automatic Tailscale serve at startup (create new task)" is shown

## 2. Clickable Nextcloud URLs

### Tailscale Wizard Main Page

When Tailscale is running, the network information now includes clickable URLs:

```
┌─────────────────────────────────────────────────────────────────┐
│  📡 Current Tailscale Network Info                              │
│                                                                   │
│  IP Address: 100.64.0.1                                          │
│  Hostname: my-server.tailnet-abc.ts.net                          │
│                                                                   │
│  🌐 Access Nextcloud via:                                       │
│                                                                   │
│  Local: http://localhost:8080                                    │
│  Tailscale IP: https://100.64.0.1                                │
│  Tailscale Hostname: https://my-server.tailnet-abc.ts.net       │
└─────────────────────────────────────────────────────────────────┘
```

**URLs are displayed as:**
- Blue text with underline
- Hand cursor on hover
- Darker blue on hover
- Clickable to open in browser

**When auto-serve is not configured:**
```
│  🌐 Access Nextcloud via:                                       │
│                                                                   │
│  Local: http://localhost:8080                                    │
│  Tailscale IP: https://100.64.0.1 (configure auto-serve below)  │
│  Tailscale Hostname: https://my-server... (configure auto-serve)│
```

### Tailscale Configuration Page

Similar URL display in the configuration wizard:

```
┌─────────────────────────────────────────────────────────────────┐
│  📡 Your Tailscale Network Information                          │
│                                                                   │
│  Tailscale IP: 100.64.0.1                                        │
│  MagicDNS Name: my-server.tailnet-abc.ts.net                     │
│                                                                   │
│  🌐 Access Nextcloud via:                                       │
│                                                                   │
│  Local: http://localhost:8080                                    │
│  Tailscale IP: https://100.64.0.1                                │
│  Tailscale Hostname: https://my-server.tailnet-abc.ts.net       │
│                                                                   │
│  Use these addresses to access Nextcloud from any device on      │
│  your Tailscale network.                                         │
└─────────────────────────────────────────────────────────────────┘
```

### Visual Indicators

#### Link Styling
- **Font**: Arial, 9pt (wizard) or 10pt (config), underlined
- **Color**: #3daee9 (bright blue)
- **Hover Color**: #2980b9 (darker blue)
- **Cursor**: Hand pointer (pointing finger)

#### Feedback Messages
When clicking a URL, a dialog appears:

```
┌──────────────────────────────────┐
│  Opening URL                      │
│                                   │
│  Opening http://localhost:8080    │
│  in your default browser...       │
│                                   │
│           [ OK ]                  │
└──────────────────────────────────┘
```

## 3. Confirmation Dialogs

### Disable Task Confirmation

```
┌────────────────────────────────────────────────────────────┐
│  Disable Auto-Start                                         │
│                                                              │
│  Are you sure you want to disable automatic Tailscale      │
│  serve at startup?                                          │
│                                                              │
│  You can re-enable it later from this page.                │
│                                                              │
│              [ Yes ]    [ No ]                              │
└────────────────────────────────────────────────────────────┘
```

### Remove Task Confirmation

```
┌────────────────────────────────────────────────────────────┐
│  Remove Task                                                │
│                                                              │
│  Are you sure you want to completely remove the            │
│  scheduled task?                                            │
│                                                              │
│  This will delete the task and it will need to be          │
│  recreated to re-enable auto-start.                        │
│                                                              │
│              [ Yes ]    [ No ]                              │
└────────────────────────────────────────────────────────────┘
```

### Success Messages

**After Disabling:**
```
┌────────────────────────────────────┐
│  Success                            │
│                                     │
│  Scheduled task disabled            │
│  successfully.                      │
│                                     │
│           [ OK ]                    │
└────────────────────────────────────┘
```

**After Enabling:**
```
┌────────────────────────────────────┐
│  Success                            │
│                                     │
│  Scheduled task enabled             │
│  successfully.                      │
│                                     │
│           [ OK ]                    │
└────────────────────────────────────┘
```

**After Removing:**
```
┌────────────────────────────────────┐
│  Success                            │
│                                     │
│  Scheduled task removed             │
│  successfully.                      │
│                                     │
│           [ OK ]                    │
└────────────────────────────────────┘
```

## 4. Auto-Serve Checkbox Enhancement

The checkbox text now adapts based on whether a task exists:

**When no task exists:**
```
☐ Enable automatic Tailscale serve at startup (create new task)
```

**When a task exists:**
```
☑ Enable automatic Tailscale serve at startup (update configuration)
```

The checkbox is:
- **Checked by default** when no task exists
- **Reflects current task state** when a task exists (checked if enabled, unchecked if disabled)

## 5. Port Override Behavior

The port entry field now intelligently uses:
1. **Port from existing task** (if task exists)
2. **Auto-detected port** (if no task exists but Nextcloud is running)
3. **Empty** (if no port can be detected)

```
Port (override): [8080     ] (leave empty to use detected port)
```

## 6. Color Scheme

### Status Colors
- **Enabled/Success**: Green (`#45bf55`) or theme warning color
- **Disabled/Error**: Red (`#e74c3c`) or theme error color
- **Info/Neutral**: Theme info colors

### Button Colors
- **Enable Button**: Green background (`#45bf55`), white text
- **Disable Button**: Default theme button colors
- **Remove Button**: Red background (`#e74c3c`), white text
- **Apply Configuration**: Green background (`#45bf55`), white text

### Link Colors
- **Normal**: Bright blue (`#3daee9`)
- **Hover**: Darker blue (`#2980b9`)
- **Inactive**: Hint/gray color (when auto-serve not configured)

## 7. Responsive Behavior

### Page Refresh
After any task management action (enable, disable, remove), the entire Tailscale Configuration page refreshes to show the updated status.

### Dynamic Display
- Status panel only appears when a task exists
- URLs show as clickable only when appropriate (local always, Tailscale when auto-serve configured)
- Management buttons change based on current task state

## 8. Layout Improvements

### Spacing
- Status panel has 10px vertical padding
- Management buttons have 5px horizontal spacing
- URL section has clear separation with spacing

### Alignment
- All content is left-aligned within the panel
- Buttons are left-aligned in their container
- URLs are indented slightly from the section title

## 9. Accessibility

### Visual Cues
- Hover effects on clickable elements
- Clear status indicators (✓ and ✗)
- Descriptive button labels with emojis

### User Feedback
- Confirmation dialogs before destructive actions
- Success/error messages after actions
- Clear explanatory text for each feature

## 10. Dark Mode Support

All new UI elements respect the existing theme system:
- Status panels use `theme_colors['info_bg']` and `theme_colors['info_fg']`
- Links work in both light and dark themes
- Button colors contrast appropriately

## Summary of Changes

### New Visual Elements
1. ✅ Scheduled Task Status Panel (with status indicators)
2. ✅ Three management buttons (Enable, Disable, Remove)
3. ✅ Clickable URL section with 3 URL types
4. ✅ Enhanced checkbox text
5. ✅ Confirmation dialogs
6. ✅ Success/error messages

### Improved User Experience
1. ✅ Visual feedback on all actions
2. ✅ Clear status information
3. ✅ One-click URL access
4. ✅ Safe management with confirmations
5. ✅ Responsive UI updates
6. ✅ Adaptive port configuration

### Color and Style Consistency
1. ✅ Follows existing theme system
2. ✅ Standard button colors
3. ✅ Consistent spacing and alignment
4. ✅ Professional appearance
