# Visual Comparison: Dark Mode Panel Fixes

## Overview

This document provides a visual comparison of the panels before and after applying dark mode fixes.

---

## 1. Start New Nextcloud Instance Panel (image12)

### Before Dark Mode Fix

```
┌─────────────────────────────────────────────────────────┐
│  Nextcloud Restore & Backup Utility          [🌙] [☰]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  [Return to Main Menu]                           │  │  ← System button color
│  │                                                   │  │
│  │  Select a port to access Nextcloud in your      │  │  ← Black text (hard to read)
│  │  browser.                                        │  │
│  │                                                   │  │
│  │  The port determines the address you use to      │  │  ← Hardcoded gray (not themed)
│  │  reach Nextcloud. For example, if you choose     │  │
│  │  port 8080, you'll go to http://localhost:8080   │  │
│  │                                                   │  │
│  │  [8080 ▼]                                        │  │  ← Combobox with default styling
│  │                                                   │  │
│  │  [Start Nextcloud Instance]                      │  │  ← Yellow button (branded)
│  │                                                   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Start New Nextcloud Instance                           │
└─────────────────────────────────────────────────────────┘

Issues:
- Frame has no background color (defaults to system color)
- Labels use default foreground (black text invisible on dark background)
- Hint text uses hardcoded "gray" (poor contrast in dark mode)
- Entry fields use default colors (white background)
```

### After Dark Mode Fix

**Light Theme:**
```
┌─────────────────────────────────────────────────────────┐
│  Nextcloud Restore & Backup Utility          [🌙] [☰]  │  ← #f0f0f0 background
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  [Return to Main Menu]                           │  │  ← #e0e0e0 bg, #000 fg
│  │                                                   │  │
│  │  Select a port to access Nextcloud in your      │  │  ← #f0f0f0 bg, #000 fg
│  │  browser.                                        │  │
│  │                                                   │  │
│  │  The port determines the address you use to      │  │  ← #f0f0f0 bg, #666 fg
│  │  reach Nextcloud. For example, if you choose     │  │     (themed hint color)
│  │  port 8080, you'll go to http://localhost:8080   │  │
│  │                                                   │  │
│  │  [8080 ▼]                                        │  │  ← Combobox
│  │  [____________________]                          │  │  ← #fff bg, #000 fg (if custom)
│  │                                                   │  │
│  │  [Start Nextcloud Instance]                      │  │  ← #f7b32b bg (branded)
│  │                                                   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Start New Nextcloud Instance                           │
└─────────────────────────────────────────────────────────┘
```

**Dark Theme:**
```
┌─────────────────────────────────────────────────────────┐
│  Nextcloud Restore & Backup Utility          [☀️] [☰]  │  ← #252525 header
├─────────────────────────────────────────────────────────┤
│  #1e1e1e background (dark gray)                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  [Return to Main Menu]                           │  │  ← #2d2d2d bg, #e0e0e0 fg
│  │                                                   │  │
│  │  Select a port to access Nextcloud in your      │  │  ← #1e1e1e bg, #e0e0e0 fg
│  │  browser.                                        │  │     (light text on dark)
│  │                                                   │  │
│  │  The port determines the address you use to      │  │  ← #1e1e1e bg, #999 fg
│  │  reach Nextcloud. For example, if you choose     │  │     (themed hint color)
│  │  port 8080, you'll go to http://localhost:8080   │  │
│  │                                                   │  │
│  │  [8080 ▼]                                        │  │  ← Combobox
│  │  [____________________]                          │  │  ← #2d2d2d bg, #e0e0e0 fg
│  │                                                   │  │     (if custom entry shown)
│  │                                                   │  │
│  │  [Start Nextcloud Instance]                      │  │  ← #f7b32b bg (branded)
│  │                                                   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Start New Nextcloud Instance                           │
└─────────────────────────────────────────────────────────┘

Improvements:
✓ Frame has dark background (#1e1e1e)
✓ Labels use light text (#e0e0e0) - readable
✓ Hint text uses themed color (#999999) - appropriate contrast
✓ Entry fields have dark background (#2d2d2d) with light text
✓ Automatic theme updates via apply_theme_recursive
```

---

## 2. Launch Nextcloud Instance Progress

### Before Dark Mode Fix

```
┌─────────────────────────────────────────────────────────┐
│  Nextcloud Restore & Backup Utility                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                                                         │
│           ⠋ Pulling Nextcloud image...                  │  ← Hardcoded "blue"
│                                                         │
│           This may take a few minutes                   │  ← Hardcoded "gray"
│                                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘

After completion:
┌─────────────────────────────────────────────────────────┐
│  Nextcloud Restore & Backup Utility                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│           ✓ Nextcloud is ready!                         │  ← Hardcoded "green"
│                                                         │
│           Access it at:                                 │  ← Black text
│                                                         │
│           http://localhost:8080                         │  ← Hardcoded "#3daee9" (blue link)
│                                                         │
│           Container ID: nextcloud                       │  ← Hardcoded "gray"
│                                                         │
│           [Return to Main Menu]                         │  ← System button
│                                                         │
└─────────────────────────────────────────────────────────┘

Issues:
- Progress frame has no background
- Status labels use hardcoded colors (blue, gray, green)
- Result frame has no background
- Container info uses hardcoded gray
```

### After Dark Mode Fix

**Dark Theme Progress:**
```
┌─────────────────────────────────────────────────────────┐
│  Nextcloud Restore & Backup Utility          [☀️] [☰]  │  ← #252525 header
├─────────────────────────────────────────────────────────┤
│  #1e1e1e background                                    │
│                                                         │
│           ⠋ Pulling Nextcloud image...                  │  ← #e0e0e0 fg (themed)
│                                                         │
│           This may take a few minutes                   │  ← #999 fg (themed hint)
│                                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘

**Dark Theme Ready State:**
┌─────────────────────────────────────────────────────────┐
│  Nextcloud Restore & Backup Utility          [☀️] [☰]  │  ← #252525 header
├─────────────────────────────────────────────────────────┤
│  #1e1e1e background                                    │
│                                                         │
│           ✓ Nextcloud is ready!                         │  ← #7cb342 fg (themed success)
│                                                         │
│           Access it at:                                 │  ← #e0e0e0 fg (themed)
│                                                         │
│           http://localhost:8080                         │  ← #3daee9 fg (blue link)
│                                                         │  │     (intentional for clickability)
│                                                         │
│           Container ID: nextcloud                       │  ← #999 fg (themed hint)
│                                                         │
│           [Return to Main Menu]                         │  ← #2d2d2d bg, #e0e0e0 fg
│                                                         │
└─────────────────────────────────────────────────────────┘

**Dark Theme Initializing State:**
┌─────────────────────────────────────────────────────────┐
│  Nextcloud Restore & Backup Utility          [☀️] [☰]  │
├─────────────────────────────────────────────────────────┤
│  #1e1e1e background                                    │
│                                                         │
│           ⚠ Nextcloud container is starting             │  ← #7cb342 fg (themed warning)
│                                                         │
│           The service is still initializing.            │  ← #999 fg (themed hint)
│           The link will become available when ready.    │
│                                                         │
│           Access it at:                                 │  ← #e0e0e0 fg (themed)
│                                                         │
│           http://localhost:8080                         │  ← #999 fg (disabled state)
│                                                         │
│           Container ID: nextcloud                       │  ← #999 fg (themed hint)
│                                                         │
│           ⏳ Waiting for Nextcloud to become ready...   │  ← #e0e0e0 fg (themed)
│                                                         │
│           [Return to Main Menu]                         │  ← #2d2d2d bg, #e0e0e0 fg
│                                                         │
└─────────────────────────────────────────────────────────┘

Improvements:
✓ Progress frame has dark background (#1e1e1e)
✓ Status labels use themed colors (#e0e0e0, #999999)
✓ Result frame has dark background
✓ Success indicator uses themed green (#7cb342)
✓ Container info uses themed hint color (#999999)
✓ URL link keeps consistent blue (#3daee9) for clickability
✓ Automatic theme updates via apply_theme_recursive
```

---

## 3. Schedule Automatic Backups Panel (image13)

### Before Dark Mode Fix

```
┌─────────────────────────────────────────────────────────────────────┐
│  Nextcloud Restore & Backup Utility                   [🌙] [☰]     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                       [Return to Main Menu]                         │
│                                                                     │
│                   Schedule Automatic Backups                        │  ← Black text
│                                                                     │
│    ╔═══════════════════════════════════════════════════════════╗  │
│    ║  Current Status                                           ║  │  ← Hardcoded #e8f4f8
│    ║                                                           ║  │     (light blue)
│    ║  ✓ Scheduled backup is active                            ║  │  ← Hardcoded #27ae60
│    ║  Frequency: daily                                        ║  │     (green)
│    ║  Time: 02:00                                             ║  │
│    ║  Backup Directory: /backup/path                          ║  │
│    ║                                                           ║  │
│    ║  [Disable Schedule]  [Delete Schedule]                   ║  │  ← System buttons
│    ╚═══════════════════════════════════════════════════════════╝  │
│                                                                     │
│              Configure New Schedule                                 │  ← Black text
│                                                                     │
│    Backup Directory:                                                │  ← Black text
│    [_________________________________________________] [Browse]     │  ← White entry
│                                                                     │
│    Frequency:                                                       │  ← Black text
│    ⚪ Daily    ⚪ Weekly    ⚪ Monthly                               │  ← System radio
│                                                                     │
│    Backup Time (HH:MM):                                             │  ← Black text
│    [_____]                                                          │  ← White entry
│                                                                     │
│    ☐ Encrypt backups                                               │  ← System checkbox
│                                                                     │
│    Encryption Password:                                             │  ← Black text
│    [______________________________]                                 │  ← White entry
│                                                                     │
│    ⚠️ Note: Scheduled backups are currently only supported         │  ← Hardcoded #e67e22
│    on Windows                                                       │     (orange)
│                                                                     │
│                  [Create/Update Schedule]                           │  ← #27ae60 (green)
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Issues:
- Main frame has no background color
- Status frame uses hardcoded light blue (#e8f4f8)
- Status text uses hardcoded green (#27ae60) and red (#e74c3c)
- All labels use default black text (invisible in dark mode)
- Entry fields use default white backgrounds
- Radio buttons and checkboxes use system colors
- Warning label uses hardcoded orange (#e67e22)
```

### After Dark Mode Fix

**Dark Theme:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  Nextcloud Restore & Backup Utility          [☀️] [☰]              │  ← #252525 header
├─────────────────────────────────────────────────────────────────────┤
│  #1e1e1e background (dark gray)                                    │
│                       [Return to Main Menu]                         │  ← #2d2d2d bg, #e0e0e0 fg
│                                                                     │
│                   Schedule Automatic Backups                        │  ← #e0e0e0 fg (themed)
│                                                                     │
│    ╔═══════════════════════════════════════════════════════════╗  │
│    ║  Current Status                                           ║  │  ← #1a3a4a bg (dark blue)
│    ║                                                           ║  │     #e0e0e0 fg (themed)
│    ║  ✓ Scheduled backup is active                            ║  │  ← #7cb342 fg (themed success)
│    ║  Frequency: daily                                        ║  │
│    ║  Time: 02:00                                             ║  │
│    ║  Backup Directory: /backup/path                          ║  │
│    ║                                                           ║  │
│    ║  [Disable Schedule]  [Delete Schedule]                   ║  │  ← #2d2d2d bg, #e0e0e0 fg
│    ╚═══════════════════════════════════════════════════════════╝  │
│                                                                     │
│              Configure New Schedule                                 │  ← #e0e0e0 fg (themed)
│                                                                     │
│    Backup Directory:                                                │  ← #e0e0e0 fg (themed)
│    [_________________________________________________] [Browse]     │  ← #2d2d2d bg, #e0e0e0 fg
│                                                                     │  │   (themed entry)
│    Frequency:                                                       │  ← #e0e0e0 fg (themed)
│    ⚪ Daily    ⚪ Weekly    ⚪ Monthly                               │  ← #1e1e1e bg, #e0e0e0 fg
│                                                                     │     #2d2d2d selectcolor
│    Backup Time (HH:MM):                                             │  ← #e0e0e0 fg (themed)
│    [_____]                                                          │  ← #2d2d2d bg, #e0e0e0 fg
│                                                                     │
│    ☐ Encrypt backups                                               │  ← #1e1e1e bg, #e0e0e0 fg
│                                                                     │     #2d2d2d selectcolor
│    Encryption Password:                                             │  ← #e0e0e0 fg (themed)
│    [______________________________]                                 │  ← #2d2d2d bg, #e0e0e0 fg
│                                                                     │
│    ⚠️ Note: Scheduled backups are currently only supported         │  ← #7cb342 fg (themed warning)
│    on Windows                                                       │
│                                                                     │
│                  [Create/Update Schedule]                           │  ← #27ae60 bg (branded green)
│                                                                     │     white fg
└─────────────────────────────────────────────────────────────────────┘

Improvements:
✓ Main frame has dark background (#1e1e1e)
✓ Status frame uses themed info background (#1a3a4a - dark blue)
✓ Status text uses themed success color (#7cb342)
✓ All labels use themed light text (#e0e0e0)
✓ Entry fields have dark backgrounds (#2d2d2d) with light text
✓ Radio buttons themed: #1e1e1e bg, #e0e0e0 fg, #2d2d2d selectcolor
✓ Checkboxes themed: #1e1e1e bg, #e0e0e0 fg, #2d2d2d selectcolor
✓ Warning label uses themed warning color (#7cb342)
✓ Buttons use themed colors (#2d2d2d bg, #e0e0e0 fg)
✓ Create button keeps branded green (#27ae60) with white text
✓ Automatic theme updates via apply_theme_recursive

**Inactive Status (No Schedule):**
╔═══════════════════════════════════════════════════════════╗
║  Current Status                                           ║  ← #1a3a4a bg (dark blue)
║                                                           ║     #e0e0e0 fg (themed)
║  ✗ No scheduled backup configured                        ║  ← #ef5350 fg (themed error)
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Color Theme Reference

### Light Theme Colors
| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Background | Light Gray | `#f0f0f0` | Main panel backgrounds |
| Foreground | Black | `#000000` | Primary text |
| Button BG | Light Gray | `#e0e0e0` | Button backgrounds |
| Button FG | Black | `#000000` | Button text |
| Entry BG | White | `#ffffff` | Input field backgrounds |
| Entry FG | Black | `#000000` | Input field text |
| Info BG | Light Blue | `#e3f2fd` | Status/info panels |
| Info FG | Black | `#000000` | Status/info text |
| Warning FG | Green | `#2e7d32` | Success/active indicators |
| Error FG | Red | `#d32f2f` | Error indicators |
| Hint FG | Gray | `#666666` | Secondary/hint text |

### Dark Theme Colors
| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Background | Dark Gray | `#1e1e1e` | Main panel backgrounds |
| Foreground | Light Gray | `#e0e0e0` | Primary text |
| Button BG | Dark Gray | `#2d2d2d` | Button backgrounds |
| Button FG | Light Gray | `#e0e0e0` | Button text |
| Entry BG | Dark Gray | `#2d2d2d` | Input field backgrounds |
| Entry FG | Light Gray | `#e0e0e0` | Input field text |
| Info BG | Dark Blue | `#1a3a4a` | Status/info panels |
| Info FG | Light Gray | `#e0e0e0` | Status/info text |
| Warning FG | Light Green | `#7cb342` | Success/active indicators |
| Error FG | Light Red | `#ef5350` | Error indicators |
| Hint FG | Light Gray | `#999999` | Secondary/hint text |

### Intentional Branding Colors (consistent across themes)
| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| New Instance Button | Yellow/Orange | `#f7b32b` | Primary action |
| Create Schedule Button | Green | `#27ae60` | Primary action |
| URL Links | Blue | `#3daee9` | Clickable links |

---

## Summary

All three panels now provide:

1. **Proper Dark Mode Support**: All backgrounds, text, and UI elements use theme-appropriate colors
2. **Consistent Experience**: Visual hierarchy and color meanings are maintained across themes
3. **Better Readability**: Appropriate contrast ratios for all text elements
4. **Professional Appearance**: Uniform styling with no jarring color mismatches
5. **Automatic Updates**: Theme changes are applied instantly via `apply_theme_recursive()`

The application now delivers a cohesive, professional dark mode experience throughout all major UI components.
