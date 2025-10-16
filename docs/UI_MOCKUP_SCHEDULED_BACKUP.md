# Scheduled Backup UI Mockups

## 1. Landing Page - Before Scheduling

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                   Nextcloud Restore & Backup Utility                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║                                                                              ║
║                         ┌────────────────────────────┐                      ║
║                         │                            │                      ║
║                         │     🔄 Backup Now         │                      ║
║                         │                            │                      ║
║                         └────────────────────────────┘                      ║
║                                                                              ║
║                         ┌────────────────────────────┐                      ║
║                         │                            │                      ║
║                         │  🛠 Restore from Backup   │                      ║
║                         │                            │                      ║
║                         └────────────────────────────┘                      ║
║                                                                              ║
║                         ┌────────────────────────────┐                      ║
║                         │  ✨ Start New Nextcloud    │                      ║
║                         │      Instance              │                      ║
║                         └────────────────────────────┘                      ║
║                                                                              ║
║                         ┌────────────────────────────┐                      ║
║                         │                            │                      ║
║                         │   📅 Schedule Backup       │  ← NEW BUTTON        ║
║                         │                            │                      ║
║                         └────────────────────────────┘                      ║
║                                                                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 2. Landing Page - With Active Schedule

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                   Nextcloud Restore & Backup Utility                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║                                                                              ║
║                         ┌────────────────────────────┐                      ║
║                         │     🔄 Backup Now         │                      ║
║                         └────────────────────────────┘                      ║
║                                                                              ║
║                         ┌────────────────────────────┐                      ║
║                         │  🛠 Restore from Backup   │                      ║
║                         └────────────────────────────┘                      ║
║                                                                              ║
║                         ┌────────────────────────────┐                      ║
║                         │  ✨ Start New Nextcloud    │                      ║
║                         │      Instance              │                      ║
║                         └────────────────────────────┘                      ║
║                                                                              ║
║                         ┌────────────────────────────┐                      ║
║                         │   📅 Schedule Backup       │                      ║
║                         └────────────────────────────┘                      ║
║                                                                              ║
║                   📅 Scheduled: daily at 02:00  ← STATUS INDICATOR          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 3. Schedule Configuration - No Active Schedule

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                   Nextcloud Restore & Backup Utility                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  [Return to Main Menu]                                                       ║
║                                                                              ║
║                      Schedule Automatic Backups                              ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │                         Current Status                                 │ ║
║  │                                                                        │ ║
║  │                  ✗ No scheduled backup configured                      │ ║
║  │                                                                        │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║                      Configure New Schedule                                  ║
║  ────────────────────────────────────────────────────────────────────────── ║
║                                                                              ║
║  Backup Directory:                                                           ║
║  ┌──────────────────────────────────────────────────────┐  ┌─────────┐     ║
║  │                                                      │  │ Browse  │     ║
║  └──────────────────────────────────────────────────────┘  └─────────┘     ║
║                                                                              ║
║  Frequency:                                                                  ║
║  ◉ Daily        ○ Weekly        ○ Monthly                                   ║
║                                                                              ║
║  Backup Time (HH:MM):                                                        ║
║  ┌──────────┐                                                                ║
║  │  02:00   │                                                                ║
║  └──────────┘                                                                ║
║                                                                              ║
║  ☐ Encrypt backups                                                           ║
║                                                                              ║
║                                                                              ║
║                      ┌───────────────────────────┐                          ║
║                      │  Create/Update Schedule   │                          ║
║                      └───────────────────────────┘                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 4. Schedule Configuration - With Active Schedule

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                   Nextcloud Restore & Backup Utility                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  [Return to Main Menu]                                                       ║
║                                                                              ║
║                      Schedule Automatic Backups                              ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │                         Current Status                                 │ ║
║  │                                                                        │ ║
║  │                  ✓ Scheduled backup is active                          │ ║
║  │                  Frequency: daily                                      │ ║
║  │                  Time: 02:00                                           │ ║
║  │                  Backup Directory: C:\Backups\Nextcloud                │ ║
║  │                                                                        │ ║
║  │          ┌──────────────────┐  ┌──────────────────┐                   │ ║
║  │          │ Disable Schedule │  │ Delete Schedule  │                   │ ║
║  │          └──────────────────┘  └──────────────────┘                   │ ║
║  │                                                                        │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║                      Configure New Schedule                                  ║
║  ────────────────────────────────────────────────────────────────────────── ║
║                                                                              ║
║  Backup Directory:                                                           ║
║  ┌──────────────────────────────────────────────────────┐  ┌─────────┐     ║
║  │ C:\Backups\Nextcloud                                 │  │ Browse  │     ║
║  └──────────────────────────────────────────────────────┘  └─────────┘     ║
║                                                                              ║
║  Frequency:                                                                  ║
║  ◉ Daily        ○ Weekly        ○ Monthly                                   ║
║                                                                              ║
║  Backup Time (HH:MM):                                                        ║
║  ┌──────────┐                                                                ║
║  │  02:00   │                                                                ║
║  └──────────┘                                                                ║
║                                                                              ║
║  ☑ Encrypt backups                                                           ║
║                                                                              ║
║  Encryption Password:                                                        ║
║  ┌──────────────────────────────────────┐                                   ║
║  │ ********                             │                                   ║
║  └──────────────────────────────────────┘                                   ║
║                                                                              ║
║                      ┌───────────────────────────┐                          ║
║                      │  Create/Update Schedule   │                          ║
║                      └───────────────────────────┘                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 5. Success Dialog After Creating Schedule

```
╔══════════════════════════════════════════════════════════════╗
║                         Success                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Scheduled backup created successfully!                      ║
║                                                              ║
║  Frequency: daily                                            ║
║  Time: 02:00                                                 ║
║  Backup Directory: C:\Backups\Nextcloud                      ║
║                                                              ║
║  Your backups will run automatically according to            ║
║  this schedule.                                              ║
║                                                              ║
║                         ┌────────┐                           ║
║                         │   OK   │                           ║
║                         └────────┘                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## 6. Confirmation Dialog for Delete

```
╔══════════════════════════════════════════════════════════════╗
║                      Confirm Delete                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Are you sure you want to delete the scheduled backup?       ║
║                                                              ║
║  This will remove the scheduled task completely.             ║
║                                                              ║
║                                                              ║
║              ┌─────────┐         ┌─────────┐                ║
║              │   Yes   │         │   No    │                ║
║              └─────────┘         └─────────┘                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## 7. Non-Windows Warning (macOS/Linux)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                   Nextcloud Restore & Backup Utility                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  [Return to Main Menu]                                                       ║
║                                                                              ║
║                      Schedule Automatic Backups                              ║
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │                         Current Status                                 │ ║
║  │                                                                        │ ║
║  │                  ✗ No scheduled backup configured                      │ ║
║  │                                                                        │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║                      Configure New Schedule                                  ║
║  ────────────────────────────────────────────────────────────────────────── ║
║                                                                              ║
║  Backup Directory:                                                           ║
║  ┌──────────────────────────────────────────────────────────┐  ┌─────────┐ ║
║  │                                                          │  │ Browse  │ ║
║  └──────────────────────────────────────────────────────────┘  └─────────┘ ║
║                                                                              ║
║  Frequency:                                                                  ║
║  ◉ Daily        ○ Weekly        ○ Monthly                                   ║
║                                                                              ║
║  Backup Time (HH:MM):                                                        ║
║  ┌──────────┐                                                                ║
║  │  02:00   │                                                                ║
║  └──────────┘                                                                ║
║                                                                              ║
║  ☐ Encrypt backups                                                           ║
║                                                                              ║
║  ⚠️ Note: Scheduled backups are currently only supported on Windows         ║
║                                                                              ║
║                      ┌───────────────────────────┐                          ║
║                      │  Create/Update Schedule   │                          ║
║                      └───────────────────────────┘                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Key UI Elements

### Colors
- **Purple (#9b59b6)**: Schedule Backup button background
- **Green (#27ae60)**: Success messages and active status
- **Red (#e74c3c)**: Warning messages and inactive status
- **Blue (#3daee9)**: Informational elements
- **Orange (#e67e22)**: Platform warnings

### Buttons
1. **📅 Schedule Backup** (Landing page) - Opens schedule configuration
2. **Browse** - Opens directory selection dialog
3. **Create/Update Schedule** - Creates or updates the schedule
4. **Disable Schedule** - Temporarily disables the schedule
5. **Delete Schedule** - Permanently removes the schedule
6. **Return to Main Menu** - Goes back to landing page

### Status Indicators
- ✓ (Green checkmark) - Schedule is active
- ✗ (Red X) - No schedule configured
- 📅 (Calendar icon) - Schedule information

### Input Fields
1. **Backup Directory** - Text entry with Browse button
2. **Frequency** - Radio buttons (Daily/Weekly/Monthly)
3. **Backup Time** - Text entry (HH:MM format)
4. **Encrypt backups** - Checkbox
5. **Encryption Password** - Password entry (shown only when encryption enabled)

## User Flow Diagrams

### Creating a Schedule
```
Start
  ↓
Click "📅 Schedule Backup"
  ↓
See "No scheduled backup configured"
  ↓
Fill in backup directory
  ↓
Select frequency (daily/weekly/monthly)
  ↓
Set time (HH:MM)
  ↓
(Optional) Enable encryption + enter password
  ↓
Click "Create/Update Schedule"
  ↓
See success dialog
  ↓
Return to main menu
  ↓
See schedule status indicator
  ↓
End
```

### Disabling a Schedule
```
Start
  ↓
Click "📅 Schedule Backup"
  ↓
See "✓ Scheduled backup is active"
  ↓
Click "Disable Schedule"
  ↓
Schedule disabled (not deleted)
  ↓
UI refreshes to show disabled state
  ↓
End
```

### Deleting a Schedule
```
Start
  ↓
Click "📅 Schedule Backup"
  ↓
See "✓ Scheduled backup is active"
  ↓
Click "Delete Schedule"
  ↓
See confirmation dialog
  ↓
Click "Yes"
  ↓
Schedule deleted from Windows Task Scheduler
  ↓
Config file deleted
  ↓
Return to main menu
  ↓
No schedule status indicator shown
  ↓
End
```

### Scheduled Backup Execution
```
Windows Task Scheduler triggers at scheduled time
  ↓
Launch app with --scheduled flag
  ↓
App runs in hidden mode (no GUI window)
  ↓
Check if Docker is running
  ↓
Find Nextcloud container
  ↓
Detect database type
  ↓
Run backup process
  ↓
Log progress to console
  ↓
Save backup to configured directory
  ↓
(Optional) Encrypt backup
  ↓
Exit
```

## Responsive Behavior

The UI is designed to work at different window sizes:
- Minimum width: 700px
- Minimum height: 700px
- Default size: 900x900px
- All elements maintain proper spacing and alignment
- Text wraps appropriately for smaller windows

## Accessibility

- Clear, large buttons with emoji icons for visual recognition
- Distinct colors for different states (active/inactive/warning)
- Descriptive labels for all input fields
- Confirmation dialogs for destructive actions
- Status indicators use both color and text
