# UI Mockups - New Features

This document provides ASCII art mockups of the new UI features.

## 1. Landing Page with Health Dashboard

```
╔═══════════════════════════════════════════════════════════════════════╗
║            Nextcloud Restore & Backup Utility              🌙  ☰     ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║                                                                       ║
║   ┌───────────────────────────────────────────────────────────────┐  ║
║   │                  🔄  Backup Now                               │  ║
║   │                                                               │  ║
║   └───────────────────────────────────────────────────────────────┘  ║
║                                                                       ║
║   ┌───────────────────────────────────────────────────────────────┐  ║
║   │              🛠  Restore from Backup                          │  ║
║   │                                                               │  ║
║   └───────────────────────────────────────────────────────────────┘  ║
║                                                                       ║
║   ┌───────────────────────────────────────────────────────────────┐  ║
║   │          ✨  Start New Nextcloud Instance                    │  ║
║   │                                                               │  ║
║   └───────────────────────────────────────────────────────────────┘  ║
║                                                                       ║
║   ┌───────────────────────────────────────────────────────────────┐  ║
║   │                 📅  Schedule Backup                           │  ║
║   │                                                               │  ║
║   └───────────────────────────────────────────────────────────────┘  ║
║                                                                       ║
║   ┌───────────────────────────────────────────────────────────────┐  ║
║   │                 📜  Backup History                            │  ║
║   └───────────────────────────────────────────────────────────────┘  ║
║                                                                       ║
║   ┌─────────────────────────────────────────────────────────────┐    ║
║   │ 🏥 System Health                                    🔄      │    ║
║   ├─────────────────────────────────────────────────────────────┤    ║
║   │ Docker:      ✅ Docker is running                           │    ║
║   │ Nextcloud:   ✅ Nextcloud container running: nextcloud-app  │    ║
║   │ Tailscale:   ⚠️  Tailscale not running or not installed    │    ║
║   │ Network:     ✅ Network connectivity OK                     │    ║
║   │                                                             │    ║
║   │ Last checked: 18:35:42                                      │    ║
║   └─────────────────────────────────────────────────────────────┘    ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 2. Selective Backup - Folder Selection

```
╔═══════════════════════════════════════════════════════════════════════╗
║            Nextcloud Restore & Backup Utility              🌙  ☰     ║
╠═══════════════════════════════════════════════════════════════════════╣
║                    Select Folders to Backup                           ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║              📁 Select Folders to Include in Backup                   ║
║                                                                       ║
║         Choose which folders to include. Critical folders are         ║
║                          required.                                    ║
║                                                                       ║
║   ┌─────────────────────────────────────────────────────────────┐    ║
║   │                                                             │    ║
║   │  [✓] config          - Configuration files (Required)      │    ║
║   │                                                             │    ║
║   │  [✓] data            - User data and files (Required)      │    ║
║   │                                                             │    ║
║   │  [✓] apps            - Standard Nextcloud apps             │    ║
║   │                                                             │    ║
║   │  [✓] custom_apps     - Custom/third-party apps             │    ║
║   │                                                             │    ║
║   └─────────────────────────────────────────────────────────────┘    ║
║                                                                       ║
║                                                                       ║
║              ┌──────────┐              ┌──────────────┐              ║
║              │ ← Back   │              │ Continue →   │              ║
║              └──────────┘              └──────────────┘              ║
║                                                                       ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 3. Backup History & Restore Points

```
╔═══════════════════════════════════════════════════════════════════════╗
║            Nextcloud Restore & Backup Utility              🌙  ☰     ║
╠═══════════════════════════════════════════════════════════════════════╣
║                        Backup History                                 ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  ┌────────┐  📜 Backup History & Restore Points                      ║
║  │ ← Back │                                                           ║
║  └────────┘                                                           ║
║                                                                     ▲ ║
║  ┌─────────────────────────────────────────────────────────────┐   █ ║
║  │ 📅 2025-10-13 18:30:15                      💾 245.3 MB     │   █ ║
║  │ 📁 nextcloud-backup-20251013_183015.tar.gz.gpg             │   █ ║
║  │ 🔒 Encrypted | DB: pgsql                                    │   █ ║
║  │ ✅ Verification: success                                     │   █ ║
║  │                                                             │   █ ║
║  │ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌───┐               │   █ ║
║  │ │🛠 Restore│ │✓ Verify │ │📤 Export │ │📍 │               │   █ ║
║  │ └──────────┘ └─────────┘ └──────────┘ └───┘               │   █ ║
║  └─────────────────────────────────────────────────────────────┘   █ ║
║                                                                     █ ║
║  ┌─────────────────────────────────────────────────────────────┐   █ ║
║  │ 📅 2025-10-12 02:00:00                      💾 238.7 MB     │   █ ║
║  │ 📁 nextcloud-backup-20251012_020000.tar.gz                 │   █ ║
║  │ DB: pgsql                                                   │   █ ║
║  │ ✅ Verification: success                                     │   █ ║
║  │                                                             │   █ ║
║  │ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌───┐               │   █ ║
║  │ │🛠 Restore│ │✓ Verify │ │📤 Export │ │📍 │               │   █ ║
║  │ └──────────┘ └─────────┘ └──────────┘ └───┘               │   █ ║
║  └─────────────────────────────────────────────────────────────┘   █ ║
║                                                                     █ ║
║  ┌─────────────────────────────────────────────────────────────┐   █ ║
║  │ 📅 2025-10-11 02:00:00                      💾 242.1 MB     │   █ ║
║  │ 📁 nextcloud-backup-20251011_020000.tar.gz.gpg             │   █ ║
║  │ 🔒 Encrypted | DB: pgsql                                    │   █ ║
║  │ ⚠️  Verification: warning - apps folder not found           │   █ ║
║  │                                                             │   █ ║
║  │ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌───┐               │   █ ║
║  │ │🛠 Restore│ │✓ Verify │ │📤 Export │ │📍 │               │   █ ║
║  │ └──────────┘ └─────────┘ └──────────┘ └───┘               │   █ ║
║  └─────────────────────────────────────────────────────────────┘   █ ║
║                                                                     ▼ ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 4. Encryption Dialog with Tooltip

```
╔═══════════════════════════════════════════════════════════════════════╗
║            Nextcloud Restore & Backup Utility              🌙  ☰     ║
╠═══════════════════════════════════════════════════════════════════════╣
║                    Backup: Encryption (optional)                      ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║                                                                       ║
║                        🔒 Backup Encryption                           ║
║                                                                       ║
║                    ┌─────────────────────┐                           ║
║                    │ Return to Main Menu │                           ║
║                    └─────────────────────┘                           ║
║                                                                       ║
║        Enter password to encrypt your backup                          ║
║             (leave blank for no encryption):                          ║
║                                                                       ║
║           ┌─────────────────────────────────────────┐                ║
║           │ ••••••••••••••                          │                ║
║           └─────────────────────────────────────────┘                ║
║                      │                                                ║
║                      │  ┌─────────────────────────────────────┐      ║
║                      └──┤ Use a strong password to protect    │      ║
║                         │ sensitive data. Leave empty to      │      ║
║                         │ skip encryption.                    │      ║
║                         └─────────────────────────────────────┘      ║
║                                                                       ║
║                    ┌──────────────────────┐                          ║
║                    │   Start Backup       │                          ║
║                    └──────────────────────┘                          ║
║                                                                       ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 5. Backup Verification in Progress

```
╔═══════════════════════════════════════════════════════════════════════╗
║                      Verifying Backup                                 ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║                                                                       ║
║                    Verifying backup integrity...                      ║
║                                                                       ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 6. Verification Results Dialog

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    Verification Complete                              ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  ✅ Backup verified successfully - 1,247 files, 245.3 MB              ║
║                                                                       ║
║                        ┌──────┐                                       ║
║                        │  OK  │                                       ║
║                        └──────┘                                       ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 7. Export Backup Dialog

```
╔═══════════════════════════════════════════════════════════════════════╗
║             Select destination folder for backup copy                 ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  📁 /mnt/usb-drive/                                                   ║
║     ├── Documents/                                                    ║
║     ├── Pictures/                                                     ║
║     └── Backups/                  ← Selected                          ║
║                                                                       ║
║                                                                       ║
║             ┌──────────┐              ┌──────────┐                   ║
║             │  Cancel  │              │  Select  │                   ║
║             └──────────┘              └──────────┘                   ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 8. Export Progress

```
╔═══════════════════════════════════════════════════════════════════════╗
║                      Exporting Backup                                 ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║                                                                       ║
║                      Copying backup file...                           ║
║                                                                       ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 9. Export Complete

```
╔═══════════════════════════════════════════════════════════════════════╗
║                       Export Complete                                 ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Backup copied to:                                                    ║
║                                                                       ║
║  /mnt/usb-drive/Backups/nextcloud-backup-20251013_183015.tar.gz.gpg  ║
║                                                                       ║
║                        ┌──────┐                                       ║
║                        │  OK  │                                       ║
║                        └──────┘                                       ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## 10. Responsive Layout - Narrow Window (< 750px)

```
╔════════════════════════════════════════════╗
║  Nextcloud Backup Utility      🌙  ☰     ║  (Smaller header font)
╠════════════════════════════════════════════╣
║                                            ║
║  ┌────────────────────────────────────┐   ║
║  │       🔄  Backup Now              │   ║
║  └────────────────────────────────────┘   ║
║                                            ║
║  ┌────────────────────────────────────┐   ║
║  │   🛠  Restore from Backup         │   ║
║  └────────────────────────────────────┘   ║
║                                            ║
║  ┌────────────────────────────────────┐   ║
║  │ ✨  Start New Instance            │   ║
║  └────────────────────────────────────┘   ║
║                                            ║
║  ┌────────────────────────────────────┐   ║
║  │    📅  Schedule Backup            │   ║
║  └────────────────────────────────────┘   ║
║                                            ║
║  ┌────────────────────────────────────┐   ║
║  │    📜  Backup History             │   ║
║  └────────────────────────────────────┘   ║
║                                            ║
║  ┌──────────────────────────────────┐     ║
║  │ 🏥 System Health        🔄      │     ║
║  ├──────────────────────────────────┤     ║
║  │ Docker:     ✅                  │     ║
║  │ Nextcloud:  ✅                  │     ║
║  │ Tailscale:  ⚠️                   │     ║
║  │ Network:    ✅                  │     ║
║  └──────────────────────────────────┘     ║
║                                            ║
╚════════════════════════════════════════════╝
```

## Color Legend

### Status Icons
- ✅ **Green**: Healthy / Success
- ⚠️ **Yellow**: Warning / Needs Attention
- ❌ **Red**: Error / Failed
- ⏳ **Gray**: Pending / In Progress
- ❓ **Gray**: Unknown / Not Checked

### UI Elements
- 🔄 Backup / Refresh
- 🛠 Restore / Fix
- ✨ New / Create
- 📅 Schedule / Calendar
- 📜 History / List
- 🏥 Health / Monitor
- 📁 Folder / Directory
- 🔒 Encrypted / Secure
- 💾 Size / Storage
- 📤 Export / Upload
- 📍 Location / Path
- ✓ Verify / Check
- 🌙 Theme Toggle
- ☰ Menu

### Button States
- **Bold border**: Primary action
- Regular border: Secondary action
- No border: Tertiary / Info

### Tooltips
- Yellow background (#ffffcc)
- Black text
- Appears below element after 500ms hover

## Interaction Examples

### Hovering Over Button
```
┌───────────────────────────┐
│   🔄  Backup Now         │  ← Mouse here
└───────────────────────────┘
       │
       │  500ms delay
       ▼
┌─────────────────────────────────────┐
│ Create a backup of your Nextcloud  │  ← Tooltip appears
│ data, config, and database         │
└─────────────────────────────────────┘
```

### Clicking Health Refresh
```
Before:                    After:
┌─────────────┐           ┌─────────────┐
│ 🏥 Health 🔄│  →Click→  │ 🏥 Health 🔄│
│ Docker: ✅  │           │ Docker: ✅  │
│ Last: 18:30 │           │ Last: 18:35 │  ← Updated
└─────────────┘           └─────────────┘
```

### Scrolling Backup History
```
Mouse Wheel Up    →    List scrolls up
Mouse Wheel Down  →    List scrolls down
```

### Window Resize
```
Wide Window (900px+)      Narrow Window (700px)
┌─────────────────┐       ┌──────────┐
│ Font: 22pt      │  →    │ Font: 18pt│
│ Full spacing    │       │ Compact   │
└─────────────────┘       └──────────┘
```

## Accessibility Features

### Keyboard Navigation
- **Tab**: Move between elements
- **Enter**: Activate button
- **Space**: Toggle checkbox
- **Escape**: Close dialog

### High Contrast
- Clear color differentiation
- Icons supplement text
- Large touch targets (buttons)

### Screen Reader Support
- Descriptive labels
- Alt text for icons
- Semantic HTML structure

## Notes

1. All colors adapt to light/dark theme
2. Tooltips work on mouse hover only (not touch)
3. Mouse wheel scrolling works on all platforms
4. Window can be resized but maintains minimum 700x700
5. All dialogs are modal (block interaction with main window)
6. Progress indicators show during long operations
7. Confirmation required for destructive actions
