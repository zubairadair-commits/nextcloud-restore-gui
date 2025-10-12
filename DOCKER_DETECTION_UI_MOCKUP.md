# Docker Detection Dialog - UI Mockup

## Dialog Appearance

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ╔════════════════════════════════════════════════════════╗  │
│  ║                                                        ║  │
│  ║            ⚠ Docker Not Running                       ║  │
│  ║                                                        ║  │
│  ╚════════════════════════════════════════════════════════╝  │
│                        (Red header)                          │
│                                                              │
│                                                              │
│     Docker is not currently running on your system.         │
│                                                              │
│     This utility requires Docker to manage Nextcloud        │
│     containers.                                             │
│                                                              │
│     Would you like to start Docker Desktop now?             │
│                (Windows/Mac only)                            │
│                                                              │
│                                                              │
│                                                              │
│        ┌─────────────────────┐  ┌──────────────┐           │
│        │ Start Docker Desktop│  │    Retry     │           │
│        │    (blue button)    │  │(green button)│           │
│        └─────────────────────┘  └──────────────┘           │
│                                                              │
│                      ┌──────────────┐                       │
│                      │    Cancel    │                       │
│                      │ (gray button)│                       │
│                      └──────────────┘                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
         Window Size: 600x350 pixels, Centered on screen
```

## Dialog Elements

### Header
- **Background**: Red (#e74c3c) - Warning color
- **Text**: "⚠ Docker Not Running"
- **Font**: Arial, 16pt, Bold, White
- **Height**: 60 pixels

### Content Area
- **Background**: White
- **Padding**: 30 pixels all sides
- **Text**: Arial, 12pt, Black
- **Line spacing**: 10 pixels between paragraphs

### Buttons

#### "Start Docker Desktop" (Windows/Mac only)
- **Color**: Blue (#3daee9)
- **Text Color**: White
- **Font**: Arial, 12pt
- **Width**: 20 characters (approximately 200px)
- **Action**: Launches Docker Desktop, shows success message

#### "Retry"
- **Color**: Green (#27ae60)
- **Text Color**: White
- **Font**: Arial, 12pt
- **Width**: 15 characters (approximately 150px)
- **Action**: Checks Docker status again

#### "Cancel"
- **Color**: Light Gray
- **Text Color**: Black
- **Font**: Arial, 12pt
- **Width**: 15 characters (approximately 150px)
- **Action**: Returns to main menu

## Platform-Specific Variations

### Windows
```
Message:
  Docker is not currently running on your system.
  
  This utility requires Docker to manage Nextcloud containers.
  
  Would you like to start Docker Desktop now?

Buttons:
  [Start Docker Desktop]  [Retry]  [Cancel]
```

### macOS
```
Message:
  Docker is not currently running on your system.
  
  This utility requires Docker to manage Nextcloud containers.
  
  Would you like to start Docker Desktop now?

Buttons:
  [Start Docker Desktop]  [Retry]  [Cancel]
```

### Linux
```
Message:
  Docker is not currently running on your system.
  
  This utility requires Docker to manage Nextcloud containers.
  
  Please start the Docker daemon using:
    sudo systemctl start docker
  
  Then click 'Retry' to continue.

Buttons:
  [Retry]  [Cancel]
  (No "Start Docker Desktop" button on Linux)
```

## Success Message (After Clicking "Start Docker Desktop")

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ╔════════════════════════════════════════════════════════╗  │
│  ║                                                        ║  │
│  ║            ⚠ Docker Not Running                       ║  │
│  ║                                                        ║  │
│  ╚════════════════════════════════════════════════════════╝  │
│                                                              │
│                                                              │
│     Docker is not currently running on your system.         │
│                                                              │
│     This utility requires Docker to manage Nextcloud        │
│     containers.                                             │
│                                                              │
│     Would you like to start Docker Desktop now?             │
│                                                              │
│                                                              │
│     ✓ Docker Desktop is starting...                         │
│       Please wait 10-20 seconds, then click 'Retry'.        │
│                    (green text)                              │
│                                                              │
│                                                              │
│        ┌─────────────────────┐  ┌──────────────┐           │
│        │ Start Docker Desktop│  │    Retry     │           │
│        └─────────────────────┘  └──────────────┘           │
│                                                              │
│                      ┌──────────────┐                       │
│                      │    Cancel    │                       │
│                      └──────────────┘                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## User Interaction Flow

### Flow 1: Successful Docker Start
```
┌─────────────────┐
│ User clicks     │
│ "Backup Now"    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Docker    │
│ is_docker_      │
│ running()       │
└────────┬────────┘
         │
         ▼ (False)
┌─────────────────┐
│ Show Dialog:    │
│ "Docker Not     │
│  Running"       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User clicks     │
│ "Start Docker   │
│  Desktop"       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Launch Docker   │
│ Show success    │
│ message         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User waits      │
│ 10-20 seconds   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User clicks     │
│ "Retry"         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Docker    │
│ is_docker_      │
│ running()       │
└────────┬────────┘
         │
         ▼ (True)
┌─────────────────┐
│ Proceed with    │
│ Backup          │
└─────────────────┘
```

### Flow 2: User Cancels
```
┌─────────────────┐
│ User clicks     │
│ "Restore"       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Docker    │
└────────┬────────┘
         │
         ▼ (False)
┌─────────────────┐
│ Show Dialog     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User clicks     │
│ "Cancel"        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Return to       │
│ Main Menu       │
└─────────────────┘
```

## Dialog Positioning

- **Center of screen**: Calculated using screen dimensions
- **Fixed size**: 600x350 pixels (does not resize)
- **Modal**: Blocks interaction with main window
- **On top**: Always stays above parent window
- **Transient**: Closes with parent window

## Color Scheme

| Element                    | Color Code | RGB           | Purpose          |
|----------------------------|------------|---------------|------------------|
| Header Background          | #e74c3c    | 231, 76, 60   | Warning/Alert    |
| Header Text                | #ffffff    | 255, 255, 255 | High contrast    |
| Start Docker Desktop Button| #3daee9    | 61, 174, 233  | Primary action   |
| Retry Button               | #27ae60    | 39, 174, 96   | Positive action  |
| Success Message Text       | #27ae60    | 39, 174, 96   | Success feedback |
| Cancel Button              | #cccccc    | 204, 204, 204 | Secondary action |
| Body Background            | #ffffff    | 255, 255, 255 | Clean, neutral   |
| Body Text                  | #000000    | 0, 0, 0       | High readability |

## Accessibility

- **High Contrast**: Red header with white text
- **Clear Icons**: Warning symbol (⚠) for immediate recognition
- **Large Text**: 12-16pt fonts for readability
- **Button Size**: Large enough for easy clicking
- **Spacing**: Adequate padding between elements
- **Modal**: Focus locked to dialog until dismissed

## Technical Implementation

```python
dialog = tk.Toplevel(parent)
dialog.title("Docker Not Running")
dialog.geometry("600x350")
dialog.transient(parent)
dialog.grab_set()

# Center the dialog
x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
y = (dialog.winfo_screenheight() // 2) - (350 // 2)
dialog.geometry(f"600x350+{x}+{y}")

# Header with red background
header_frame = tk.Frame(dialog, bg="#e74c3c", height=60)

# Content area with message
content_frame = tk.Frame(dialog)

# Button frame with action buttons
button_frame = tk.Frame(content_frame)
```

## Comparison: Before vs After

### Before (Without Docker Detection)
```
User clicks "Backup Now"
        ↓
Application tries to run Docker command
        ↓
Error: "Container not found" or "Docker daemon not running"
        ↓
Confusing error message
        ↓
User doesn't know what to do
```

### After (With Docker Detection)
```
User clicks "Backup Now"
        ↓
Check if Docker is running
        ↓
Docker not running
        ↓
Clear dialog: "Docker Not Running"
        ↓
User clicks "Start Docker Desktop"
        ↓
Docker launches automatically
        ↓
User clicks "Retry"
        ↓
Backup proceeds successfully
```

## Summary

The Docker detection dialog provides:
- ✅ Clear visual hierarchy (red header = warning)
- ✅ Helpful message explaining the issue
- ✅ Actionable buttons with clear purposes
- ✅ Platform-specific guidance
- ✅ Success feedback when Docker is launched
- ✅ Easy retry mechanism
- ✅ Safe cancellation option
