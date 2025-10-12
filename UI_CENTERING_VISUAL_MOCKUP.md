# UI Centering Fix - Visual Mockup

This document provides ASCII art mockups showing how the wizard appears before and after the centering fix.

## Before Fix: Content Appears Left-Aligned

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║          Nextcloud Restore & Backup Utility                          ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║ ┌──────────────────────────────────────────────────────────────────┐ ║
║ │                                                                  │ ║
║ │  Restore Wizard: Page 1 of 3                                    │ ║
║ │  [Return to Main Menu]                                          │ ║
║ │                                                                  │ ║
║ │  Step 1: Select Backup Archive                                  │ ║
║ │  Choose the backup file to restore (.tar.gz.gpg or .tar.gz)     │ ║
║ │                                                                  │ ║
║ │  [/path/to/backup/nextcloud-backup-20240101_120000.tar.gz.gpg...│ ║
║ │  [Browse...]                                                     │ ║
║ │                                                                  │ ║
║ │  Step 2: Decryption Password                                    │ ║
║ │  Enter password if backup is encrypted (.gpg)                   │ ║
║ │                                                                  │ ║
║ │  [**********************************]                            │ ║
║ │                                                                  │ ║
║ │  [Next →]                                                        │ ║
║ │                                                                  │ ║
║ └──────────────────────────────────────────────────────────────────┘ ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Problem: Content starts at left edge, looks unbalanced
```

## After Fix: Content Truly Centered

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║          Nextcloud Restore & Backup Utility                          ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║          ┌────────────────────────────────────────┐                  ║
║          │                                        │                  ║
║          │   Restore Wizard: Page 1 of 3         │                  ║
║          │   [Return to Main Menu]                │                  ║
║          │                                        │                  ║
║          │   Step 1: Select Backup Archive       │                  ║
║          │   Choose the backup file to restore   │                  ║
║          │                                        │                  ║
║          │   [/path/to/backup/file.tar.gz.gpg]   │                  ║
║          │        [Browse...]                     │                  ║
║          │                                        │                  ║
║          │   Step 2: Decryption Password         │                  ║
║          │   Enter password if encrypted          │                  ║
║          │                                        │                  ║
║          │   [********************]               │                  ║
║          │                                        │                  ║
║          │        [Next →]                        │                  ║
║          │                                        │                  ║
║          └────────────────────────────────────────┘                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Solution: Content block centered with margins, balanced appearance
```

## Page 2: Database Configuration

### After Fix (Centered)

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║          Nextcloud Restore & Backup Utility                          ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║          ┌────────────────────────────────────────┐                  ║
║          │                                        │                  ║
║          │   Restore Wizard: Page 2 of 3         │                  ║
║          │   [Return to Main Menu]                │                  ║
║          │                                        │                  ║
║          │   Step 3: Database Configuration      │                  ║
║          │                                        │                  ║
║          │   ╔═══════════════════════════════╗   │                  ║
║          │   ║ ℹ️ Database Auto-Detection    ║   │                  ║
║          │   ║ Automatically detects SQLite, ║   │                  ║
║          │   ║ PostgreSQL, or MySQL from     ║   │                  ║
║          │   ║ your backup config.php        ║   │                  ║
║          │   ╚═══════════════════════════════╝   │                  ║
║          │                                        │                  ║
║          │   ⚠️ Enter database credentials        │                  ║
║          │                                        │                  ║
║          │   Database Name:  [nextcloud    ]     │                  ║
║          │   Database User:  [nextcloud    ]     │                  ║
║          │   Database Pass:  [**********  ]     │                  ║
║          │                                        │                  ║
║          │   Step 4: Admin Credentials           │                  ║
║          │                                        │                  ║
║          │   Admin User:     [admin       ]      │                  ║
║          │   Admin Pass:     [**********  ]     │                  ║
║          │                                        │                  ║
║          │   [← Back]         [Next →]            │                  ║
║          │                                        │                  ║
║          └────────────────────────────────────────┘                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Centered: Forms contained within fixed-width block
```

## Page 3: Container Configuration

### After Fix (Centered)

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║          Nextcloud Restore & Backup Utility                          ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║          ┌────────────────────────────────────────┐                  ║
║          │                                        │                  ║
║          │   Restore Wizard: Page 3 of 3         │                  ║
║          │   [Return to Main Menu]                │                  ║
║          │                                        │                  ║
║          │   Step 5: Container Configuration     │                  ║
║          │   Configure Nextcloud container        │                  ║
║          │                                        │                  ║
║          │   Container Name:  [nextcloud-app  ]  │                  ║
║          │   Container Port:  [9000           ]  │                  ║
║          │                                        │                  ║
║          │   ☐ Use existing container if found   │                  ║
║          │                                        │                  ║
║          │   ╔═══════════════════════════════╗   │                  ║
║          │   ║ ℹ️ The restore will:          ║   │                  ║
║          │   ║ • Extract backup archive      ║   │                  ║
║          │   ║ • Start containers            ║   │                  ║
║          │   ║ • Copy files                  ║   │                  ║
║          │   ║ • Import database             ║   │                  ║
║          │   ║ • Set permissions             ║   │                  ║
║          │   ║ • Validate installation       ║   │                  ║
║          │   ╚═══════════════════════════════╝   │                  ║
║          │                                        │                  ║
║          │   [← Back]      [Start Restore]       │                  ║
║          │                                        │                  ║
║          └────────────────────────────────────────┘                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Centered: All elements within constrained content block
```

## Responsive Behavior

### Small Window (700px width)

```
╔═══════════════════════════════════════════════════════╗
║ Nextcloud Restore & Backup Utility                   ║
╠═══════════════════════════════════════════════════════╣
║┌─────────────────────────────────────────────────────┐║
║│  Restore Wizard: Page 1 of 3                        │║
║│  [Return]                                           │║
║│  Step 1: Select Archive                             │║
║│  [/path/to/file.tar.gz.gpg.........]                │║
║│  [Browse...]                                        │║
║│  Step 2: Password                                   │║
║│  [***************]                                  │║
║│  [Next →]                                           │║
║└─────────────────────────────────────────────────────┘║
╚═══════════════════════════════════════════════════════╝
Content fills window (700px = max-width)
```

### Medium Window (1000px width)

```
╔═══════════════════════════════════════════════════════════════════════╗
║ Nextcloud Restore & Backup Utility                                   ║
╠═══════════════════════════════════════════════════════════════════════╣
║         ┌─────────────────────────────────────────────────┐           ║
║         │  Restore Wizard: Page 1 of 3                    │           ║
║         │  [Return]                                       │           ║
║         │  Step 1: Select Archive                         │           ║
║         │  [/path/to/file.tar.gz.gpg.........]            │           ║
║         │  [Browse...]                                    │           ║
║         │  Step 2: Password                               │           ║
║         │  [***************]                              │           ║
║         │  [Next →]                                       │           ║
║         └─────────────────────────────────────────────────┘           ║
╚═══════════════════════════════════════════════════════════════════════╝
        ↑ 150px margin ↑                         ↑ 150px margin ↑
Content centered with auto-margins
```

### Large Window (1400px width)

```
╔═════════════════════════════════════════════════════════════════════════════════╗
║ Nextcloud Restore & Backup Utility                                             ║
╠═════════════════════════════════════════════════════════════════════════════════╣
║              ┌─────────────────────────────────────────────────┐                ║
║              │  Restore Wizard: Page 1 of 3                    │                ║
║              │  [Return]                                       │                ║
║              │  Step 1: Select Archive                         │                ║
║              │  [/path/to/file.tar.gz.gpg.........]            │                ║
║              │  [Browse...]                                    │                ║
║              │  Step 2: Password                               │                ║
║              │  [***************]                              │                ║
║              │  [Next →]                                       │                ║
║              └─────────────────────────────────────────────────┘                ║
╚═════════════════════════════════════════════════════════════════════════════════╝
             ↑ 350px margin ↑                         ↑ 350px margin ↑
Content centered with larger margins
```

## Key Visual Differences

### Before Fix
```
Window Edge                                                    Window Edge
|                                                                      |
|  Content starts here..........................................      |
|                                                                      |
└─ Problem: No left margin, appears left-aligned                     ─┘
```

### After Fix
```
Window Edge                                                    Window Edge
|                                                                      |
|        Content Block (700px)                                        |
|        ┌────────────────────┐                                       |
|        │   Centered!        │                                       |
|        └────────────────────┘                                       |
|        ↑ Auto margin ↑     ↑ Auto margin ↑                         |
└─ Solution: Margins on both sides, true centering                   ─┘
```

## Layout Comparison

### Before: Full-Width Frame
```
Canvas (full width)
└─ Scrollable Frame (expands to fill canvas)
   ├─ Widget 1 (anchor="center" within full width)
   ├─ Widget 2 (anchor="center" within full width)
   └─ Widget 3 (anchor="center" within full width)
   
Result: Widgets centered in full-width frame = appears left-aligned
```

### After: Constrained-Width Frame
```
Canvas (full width)
   Center Line ↓
       Scrollable Frame (700px, positioned at center)
       ├─ Widget 1 (anchor="center" within 700px)
       ├─ Widget 2 (anchor="center" within 700px)
       └─ Widget 3 (anchor="center" within 700px)
       
Result: Frame centered, widgets centered in frame = truly centered
```

## Summary

The fix transforms the wizard from a full-width layout to a constrained-width, centered layout. This achieves:

1. **True block centering** - Entire content area is centered as a unit
2. **Professional appearance** - Balanced margins on both sides
3. **Responsive design** - Margins adjust automatically with window size
4. **Consistent behavior** - Works the same on all 3 wizard pages

The visual result is a clean, balanced interface that meets user expectations for centered content.
