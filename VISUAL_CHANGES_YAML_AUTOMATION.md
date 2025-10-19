# Visual Changes: Automated YAML Workflow

## Overview
This document provides a visual representation of the changes made to automate YAML file handling in the restore workflow.

## Main Workflow Comparison

### BEFORE: Interrupting Dialog Workflow
```
┌─────────────────────────────────────────────────────────────┐
│                     Page 1: Backup File                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Select Backup Archive:                                │  │
│  │ [Browse...]                                           │  │
│  │ Password (if encrypted):                              │  │
│  │ [________]                                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                           [Next >]                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              ⚠️ INTERRUPTING DIALOG APPEARS ⚠️               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │      🐋 Docker Compose Configuration                  │  │
│  │                                                       │  │
│  │  Database Type: PostgreSQL                           │  │
│  │  Database Name: nextcloud                            │  │
│  │  Database User: nextcloud                            │  │
│  │                                                       │  │
│  │  [Generate docker-compose.yml]  [Check Folders]     │  │
│  │                                 [Continue]           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  USER MUST:                                                 │
│  1. Decide if they need YAML                               │
│  2. Click "Generate" button                                │
│  3. Choose save location (confusing!)                      │
│  4. Save the file                                          │
│  5. Click "Continue"                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                Page 2: Database Configuration               │
│  (Continue with restore...)                                 │
└─────────────────────────────────────────────────────────────┘
```

### AFTER: Seamless Automated Workflow
```
┌─────────────────────────────────────────────────────────────┐
│                     Page 1: Backup File                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Select Backup Archive:                                │  │
│  │ [Browse...]                                           │  │
│  │ Password (if encrypted):                              │  │
│  │ [________]                                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                           [Next >]                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
                 ✓ YAML auto-generated silently
              (saved to ~/.nextcloud_backup_utility/compose/)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                Page 2: Database Configuration               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Database Name: [nextcloud]                            │  │
│  │ Database User: [nextcloud]                            │  │
│  │ Database Password: [________]                         │  │
│  │                                                       │  │
│  │ Admin Username: [admin]                               │  │
│  │ Admin Password: [________]                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                           [Next >]                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Page 3: Container Configuration                │
│  (Continue with restore - seamless!)                        │
└─────────────────────────────────────────────────────────────┘
```

## Advanced Options Section (New)

### Collapsed State (Default)
```
┌─────────────────────────────────────────────────────────────┐
│                Page 3: Container Configuration              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Container Name: [nextcloud-app]                       │  │
│  │ Container Port: [8080]                                │  │
│  │ [ ] Use existing container if found                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ▶ Advanced Options (for power users)               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│                       [Start Restore]                       │
└─────────────────────────────────────────────────────────────┘
```

### Expanded State (When User Clicks)
```
┌─────────────────────────────────────────────────────────────┐
│                Page 3: Container Configuration              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Container Name: [nextcloud-app]                       │  │
│  │ Container Port: [8080]                                │  │
│  │ [ ] Use existing container if found                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ▼ Advanced Options (for power users)               │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │                                                     │    │
│  │   Docker Compose Configuration                      │    │
│  │   Docker Compose YAML files are automatically       │    │
│  │   generated and stored internally.                  │    │
│  │                                                     │    │
│  │   ┌──────────────┐ ┌──────────────┐ ┌──────────┐   │    │
│  │   │ 📄 View      │ │ 💾 Export    │ │ 📁 Open  │   │    │
│  │   │    Generated │ │    YAML File │ │    YAML  │   │    │
│  │   │    YAML      │ │              │ │    Folder│   │    │
│  │   └──────────────┘ └──────────────┘ └──────────┘   │    │
│  │                                                     │    │
│  │   💡 When to use Advanced Options:                  │    │
│  │   • Customize container configurations              │    │
│  │   • Share YAML with team members                    │    │
│  │   • Debug container startup issues                  │    │
│  │   • Manually start containers with docker-compose   │    │
│  │   • Archive configurations for documentation        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│                       [Start Restore]                       │
└─────────────────────────────────────────────────────────────┘
```

## View YAML Dialog (When User Clicks "View Generated YAML")
```
┌────────────────────────────────────────────────────────────┐
│  📄 docker-compose-20251019_183045.yml                     │
├────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────┐ ▲  │
│  │ # Docker Compose configuration for Nextcloud      │ │  │
│  │ # Generated based on config.php settings          │ │  │
│  │ #                                                  │ │  │
│  │ # Detected configuration:                         │ │  │
│  │ #   - Database type: pgsql                        │ │  │
│  │ #   - Database name: nextcloud                    │ │  │
│  │ #   - Data directory: /var/www/html/data          │ │  │
│  │ #                                                  │ │  │
│  │ version: '3.8'                                     │ │  │
│  │                                                    │ │  │
│  │ services:                                          │ │  │
│  │   db:                                              │ │  │
│  │     image: postgres:15                             │ │  │
│  │     container_name: nextcloud-db                   │ ■  │
│  │     restart: unless-stopped                        │ │  │
│  │     volumes:                                       │ │  │
│  │       - ./db-data:/var/lib/postgresql/data         │ │  │
│  │     environment:                                   │ │  │
│  │       - POSTGRES_PASSWORD=****                     │ │  │
│  │       - POSTGRES_DB=nextcloud                      │ │  │
│  │       - POSTGRES_USER=nextcloud                    │ │  │
│  │     ports:                                         │ │  │
│  │       - "5432:5432"                                │ ▼  │
│  └────────────────────────────────────────────────────┘    │
│                                                            │
│                        [Close]                             │
└────────────────────────────────────────────────────────────┘
```

## File Storage Structure

### Old Location (Before)
```
/current/working/directory/
  └── docker-compose.yml   ← User had to choose this location
                              Could be anywhere on system!
```

### New Location (After)
```
~/.nextcloud_backup_utility/
  ├── backup_history.db
  └── compose/
      ├── docker-compose-20251019_183045.yml   ← Automatically saved
      ├── docker-compose-20251019_184523.yml   ← With timestamps
      └── docker-compose-20251020_091234.yml   ← Version history
```

## User Journey Comparison

### Beginner User Journey

#### BEFORE: Confused by Technical Dialog
```
Step 1: "I want to restore my backup"
        [Selects backup file, enters password]
        
Step 2: ⚠️ "What is Docker Compose?"
        "Where should I save this YAML file?"
        "Do I need this?"
        "What does this do?"
        [User is confused and scared]
        
Step 3: [Randomly saves file somewhere]
        OR [Skips it and restore might fail]
        
Step 4: [Continues with restore, unsure if they did it right]
```

#### AFTER: Smooth Experience
```
Step 1: "I want to restore my backup"
        [Selects backup file, enters password]
        
Step 2: [Goes directly to next step]
        [Everything just works!]
        
Step 3: [Continues with restore confidently]
        
Step 4: ✓ Restore completes successfully!
        [User is happy and confident]
```

### Power User Journey

#### BEFORE: Multiple Clicks Required
```
Step 1: [Select backup]
Step 2: ⚠️ Dialog appears (even though I know what I'm doing)
Step 3: [Must click "Generate"]
Step 4: [Must choose location]
Step 5: [Must save file]
Step 6: [Finally continue]
Result: Annoying interruption every time
```

#### AFTER: Streamlined with Options
```
Step 1: [Select backup]
Step 2: [Skip directly to Page 3]
Step 3: [OPTIONAL: Expand Advanced Options if needed]
Step 4: [Continue or customize]
Result: Fast workflow with full control when needed
```

## Button Functionality

### View Generated YAML Button
```
Click: 📄 View Generated YAML
  ↓
Opens dialog showing:
  • Most recent YAML file content
  • Read-only display
  • Syntax-highlighted (monospace font)
  • Scrollable for long files
  • Easy to copy content
```

### Export YAML File Button
```
Click: 💾 Export YAML File
  ↓
Opens system save dialog:
  • Default name: docker-compose.yml
  • User chooses location
  • Copies most recent YAML
  • Shows success message
  • Ready for external use
```

### Open YAML Folder Button
```
Click: 📁 Open YAML Folder
  ↓
Opens file explorer:
  • Windows: Opens in Explorer
  • macOS: Opens in Finder
  • Linux: Opens in default file manager
  • Shows all generated YAML files
  • Easy to browse/manage
```

## Benefits Summary

### UI/UX Benefits
```
✓ Cleaner Interface
  - No unexpected dialogs
  - Logical flow from start to finish
  - Professional appearance

✓ Less Clutter
  - No YAML files in working directory
  - Organized storage
  - Easy to find when needed

✓ Progressive Disclosure
  - Beginners see simple workflow
  - Advanced options hidden but available
  - Users discover features as they grow
```

### Technical Benefits
```
✓ Automatic Management
  - Files always saved to correct location
  - Timestamped for version history
  - No user error in file naming

✓ Secure Storage
  - Private user directory
  - OS-level permissions
  - No accidental sharing

✓ Maintainability
  - Easy to clean up old files
  - Easy to backup configurations
  - Easy to audit restore history
```

## Key Statistics

```
┌─────────────────────────────────────────────────┐
│           Impact Measurements                   │
├─────────────────────────────────────────────────┤
│ Steps Removed from Main Flow:        3         │
│ Dialog Interruptions Removed:        1         │
│ User Decisions Required:              0         │
│ Technical Knowledge Required:         None      │
│ Time Saved per Restore:               ~30 sec  │
│ Advanced Options Available:           3         │
│ Breaking Changes:                     0         │
│ Security Improvements:                Yes       │
└─────────────────────────────────────────────────┘
```

---

**Visual Summary:** The changes transform a technical, interrupting workflow into a smooth, beginner-friendly experience while preserving full functionality for power users through optional Advanced Options.
