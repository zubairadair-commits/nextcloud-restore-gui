# Docker Compose Detection Dialog - UI Mockup

## Dialog Appearance

The Docker Compose suggestion dialog appears after successful database detection when navigating from Page 1 to Page 2.

### Dialog Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🐋 Docker Compose Configuration                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ════════════════════════════════════════════════════════════  │
│  DETECTED ENVIRONMENT CONFIGURATION                              │
│  ════════════════════════════════════════════════════════════  │
│                                                                  │
│  📊 Database Type: PGSQL                                        │
│  📦 Database Name: nextcloud                                    │
│  👤 Database User: nextcloud                                    │
│  🗄️  Database Host: localhost                                   │
│  📁 Data Directory: /var/www/html/data                          │
│  🌐 Trusted Domains: localhost, nextcloud.example.com           │
│                                                                  │
│  ════════════════════════════════════════════════════════════  │
│  DOCKER COMPOSE STATUS                                           │
│  ════════════════════════════════════════════════════════════  │
│                                                                  │
│  ℹ️  No Docker Compose usage detected.                          │
│                                                                  │
│  We can generate a docker-compose.yml file for you based on     │
│  the detected configuration. This will make your restore:        │
│    ✓ Safer and more reproducible                                │
│    ✓ Easier to migrate or restore again                         │
│    ✓ Better documented and portable                             │
│                                                                  │
│  ════════════════════════════════════════════════════════════  │
│  HOST FOLDER REQUIREMENTS                                        │
│  ════════════════════════════════════════════════════════════  │
│                                                                  │
│  Before starting containers, ensure these folders exist:         │
│    • ./nextcloud-data (for Nextcloud files)                     │
│    • ./db-data (for database files)                             │
│                                                                  │
│  These folders will be created if they don't exist.             │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Generate docker-compose.yml] [Check/Create Folders] [Continue]│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Dialog With Existing Docker Compose

When docker-compose.yml is detected:

```
┌─────────────────────────────────────────────────────────────────┐
│  🐋 Docker Compose Configuration                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ════════════════════════════════════════════════════════════  │
│  DETECTED ENVIRONMENT CONFIGURATION                              │
│  ════════════════════════════════════════════════════════════  │
│                                                                  │
│  📊 Database Type: MYSQL                                        │
│  📦 Database Name: nc_production                                │
│  👤 Database User: nc_admin                                     │
│  🗄️  Database Host: db                                          │
│  📁 Data Directory: /var/www/html/data                          │
│  🌐 Trusted Domains: cloud.example.com                          │
│                                                                  │
│  ════════════════════════════════════════════════════════════  │
│  DOCKER COMPOSE STATUS                                           │
│  ════════════════════════════════════════════════════════════  │
│                                                                  │
│  ✓ Docker Compose usage detected!                               │
│    Found: docker-compose.yml                                     │
│                                                                  │
│  ⚠️  WARNING: If your existing docker-compose.yml doesn't match  │
│  the detected config.php settings, you may experience issues.    │
│                                                                  │
│  We recommend reviewing your docker-compose.yml to ensure:       │
│    • Volume mappings match the detected data directory          │
│    • Database credentials match config.php                      │
│    • Port mappings are correct                                  │
│                                                                  │
│  ════════════════════════════════════════════════════════════  │
│  HOST FOLDER REQUIREMENTS                                        │
│  ════════════════════════════════════════════════════════════  │
│                                                                  │
│  Before starting containers, ensure these folders exist:         │
│    • ./nextcloud-data (for Nextcloud files)                     │
│    • ./db-data (for database files)                             │
│                                                                  │
│  These folders will be created if they don't exist.             │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Generate docker-compose.yml] [Check/Create Folders] [Continue]│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Dialog With SQLite Database

When SQLite is detected (simpler, no separate database service):

```
┌─────────────────────────────────────────────────────────────────┐
│  🐋 Docker Compose Configuration                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ════════════════════════════════════════════════════════════  │
│  DETECTED ENVIRONMENT CONFIGURATION                              │
│  ════════════════════════════════════════════════════════════  │
│                                                                  │
│  📊 Database Type: SQLITE                                       │
│  📦 Database Name: nextcloud.db                                 │
│  📁 Data Directory: /var/www/html/data                          │
│  🌐 Trusted Domains: localhost                                  │
│                                                                  │
│  ════════════════════════════════════════════════════════════  │
│  DOCKER COMPOSE STATUS                                           │
│  ════════════════════════════════════════════════════════════  │
│                                                                  │
│  ℹ️  No Docker Compose usage detected.                          │
│                                                                  │
│  We can generate a docker-compose.yml file for you based on     │
│  the detected configuration. This will make your restore:        │
│    ✓ Safer and more reproducible                                │
│    ✓ Easier to migrate or restore again                         │
│    ✓ Better documented and portable                             │
│                                                                  │
│  ════════════════════════════════════════════════════════════  │
│  HOST FOLDER REQUIREMENTS                                        │
│  ════════════════════════════════════════════════════════════  │
│                                                                  │
│  Before starting containers, ensure these folders exist:         │
│    • ./nextcloud-data (for Nextcloud files)                     │
│                                                                  │
│  Note: SQLite doesn't require a separate database container.    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Generate docker-compose.yml] [Check/Create Folders] [Continue]│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Button Interactions

### Generate docker-compose.yml Button

**Action:** Opens file save dialog
**Default name:** docker-compose.yml
**Effect:** Creates docker-compose.yml with detected configuration

**Success Message:**
```
┌─────────────────────────────────────────────────┐
│  Success                                         │
├─────────────────────────────────────────────────┤
│                                                  │
│  docker-compose.yml saved to:                   │
│  /home/user/nextcloud/docker-compose.yml        │
│                                                  │
│  You can now use 'docker-compose up -d' to      │
│  start your containers.                         │
│                                                  │
│  [ OK ]                                          │
└─────────────────────────────────────────────────┘
```

### Check/Create Folders Button

**Action:** Validates and creates required folders
**Effect:** Creates ./nextcloud-data and ./db-data (if needed)

**Success Message:**
```
┌─────────────────────────────────────────────────┐
│  Folder Check Complete                           │
├─────────────────────────────────────────────────┤
│                                                  │
│  Created:                                        │
│    ✓ ./nextcloud-data                           │
│    ✓ ./db-data                                  │
│                                                  │
│  [ OK ]                                          │
└─────────────────────────────────────────────────┘
```

**When Folders Already Exist:**
```
┌─────────────────────────────────────────────────┐
│  Folder Check Complete                           │
├─────────────────────────────────────────────────┤
│                                                  │
│  Already exist:                                  │
│    ✓ ./nextcloud-data                           │
│    ✓ ./db-data                                  │
│                                                  │
│  [ OK ]                                          │
└─────────────────────────────────────────────────┘
```

### Continue Button

**Action:** Closes dialog and continues to Page 2
**Effect:** Proceeds with restore workflow

## Color Scheme

### Dialog Header
- Background: `#3daee9` (Blue)
- Text: White
- Font: Arial 16pt Bold

### Content Area
- Background: White
- Text: Black
- Font: Arial 10pt

### Section Headers
- Text: Black
- Font: Arial 10pt
- Separator: `=` characters

### Buttons

**Generate docker-compose.yml:**
- Background: `#45bf55` (Green)
- Text: White
- Font: Arial 11pt Bold
- Width: 25 characters

**Check/Create Folders:**
- Background: `#f7b32b` (Orange/Yellow)
- Text: White
- Font: Arial 11pt
- Width: 20 characters

**Continue:**
- Background: Default (Gray)
- Text: Black
- Font: Arial 11pt
- Width: 15 characters

### Status Indicators

- ✓ Success: Green (`#2e7d32`)
- ⚠️ Warning: Orange/Red (`#d32f2f`)
- ℹ️ Info: Blue (`#1976d2`)
- 📊 Database: Default color
- 📦 Package: Default color
- 👤 User: Default color
- 🗄️ Host: Default color
- 📁 Folder: Default color
- 🌐 Network: Default color

## Responsive Behavior

### Dialog Size
- Width: 700px
- Height: 600px
- Minimum: Not resizable
- Position: Center of screen

### Text Wrapping
- Automatic wrapping at 60 characters
- Justified text for better readability
- Monospace font for folder paths

### Scrolling
- Vertical scrollbar if content exceeds height
- Horizontal scrollbar disabled (content wraps)

## Keyboard Navigation

- **Tab:** Navigate between buttons
- **Enter:** Activate focused button
- **Escape:** Close dialog (same as Continue)
- **Alt+G:** Generate docker-compose.yml
- **Alt+C:** Check/Create Folders

## Accessibility

### Screen Reader Support
- Dialog title announced
- Section headers announced
- Button labels clear and descriptive
- Status messages announced when changed

### High Contrast Mode
- All text has sufficient contrast ratio (4.5:1 minimum)
- Buttons have clear borders
- Focus indicators visible

### Font Scaling
- Text respects system font size settings
- Layout adjusts for larger fonts
- No text truncation at 150% zoom

## Integration with Wizard Flow

### Page 1 → Page 2 Navigation

```
[Page 1: Backup Selection]
         ↓
  Click "Next" button
         ↓
  Extract config.php
         ↓
  Detect database type
         ↓
  Parse full config.php
         ↓
  Detect Docker Compose
         ↓
[Docker Compose Dialog] ← NEW STEP
         ↓
  User interacts with dialog
         ↓
[Page 2: Database Config]
```

### Timing

- Dialog appears: 1.5 seconds after detection completes
- Success message clears: After dialog opens
- Dialog is modal: Cannot interact with wizard until closed
- Dialog auto-centers: On screen when opened

## Error States

### Config.php Not Found

**No dialog shown**
- User sees: "⚠️ Warning: config.php not found"
- Workflow continues normally
- Can still complete restore with manual config

### Parsing Failed

**No dialog shown**
- User sees: "⚠️ Warning: Could not parse config.php"
- Workflow continues normally
- Dialog not shown if parsing fails

### Generation Failed

**Error message:**
```
┌─────────────────────────────────────────────────┐
│  Error                                           │
├─────────────────────────────────────────────────┤
│                                                  │
│  Failed to generate docker-compose.yml:          │
│  Permission denied                               │
│                                                  │
│  Please check:                                   │
│  - Write permissions in current directory        │
│  - Available disk space                          │
│  - File is not locked by another process         │
│                                                  │
│  [ OK ]                                          │
└─────────────────────────────────────────────────┘
```

### Folder Creation Failed

**Error message:**
```
┌─────────────────────────────────────────────────┐
│  Error                                           │
├─────────────────────────────────────────────────┤
│                                                  │
│  Failed to create folders:                       │
│  Permission denied                               │
│                                                  │
│  Please manually create:                         │
│  - ./nextcloud-data                              │
│  - ./db-data                                    │
│                                                  │
│  Then run:                                       │
│  chmod 755 nextcloud-data db-data               │
│                                                  │
│  [ OK ]                                          │
└─────────────────────────────────────────────────┘
```

## Testing Checklist

Visual testing checklist for the dialog:

- [ ] Dialog appears after detection completes
- [ ] Dialog is properly centered on screen
- [ ] Header has correct color and text
- [ ] All sections are clearly separated
- [ ] Icons display correctly (🐋 📊 📦 etc.)
- [ ] Text is readable and well-formatted
- [ ] Buttons are properly aligned
- [ ] Button colors match specification
- [ ] Hover effects work on buttons
- [ ] File save dialog opens correctly
- [ ] Success messages display properly
- [ ] Error messages are clear
- [ ] Dialog closes when clicking Continue
- [ ] Dialog closes when pressing Escape
- [ ] Focus order is logical (left to right)
- [ ] Scrollbar appears if content too long
- [ ] Works at different screen resolutions
- [ ] Works with system font scaling
- [ ] Responsive to window resize (if applicable)

## Implementation Notes

The dialog is implemented in the `show_docker_compose_suggestion()` method of the `NextcloudRestoreWizard` class.

Key implementation details:
- Modal dialog using `tk.Toplevel()`
- Transient to main window
- Grab set to make modal
- Auto-centering calculation
- Scrollable text area for content
- Button frame for actions
- Thread-safe UI updates

This ensures a professional, user-friendly experience that guides users through the Docker Compose configuration process.
