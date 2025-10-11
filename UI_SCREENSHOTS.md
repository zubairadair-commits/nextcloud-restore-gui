# UI Screenshots - Redesigned Restore Workflow

This document shows the new user interface for the redesigned restore workflow.

## Landing Page
![Landing Page](01_landing.png)

The main landing page with three primary options:
- 🔄 Backup Now
- 🛠 Restore from Backup
- ✨ Start New Nextcloud Instance

## Restore Wizard - Multi-Page Form

The restore wizard is now a multi-step process with three pages:

### Page 1: Backup Selection and Decryption
![Wizard Page 1](wizard_page1.png)

**Step 1: Select Backup Archive**
- File path input with browse button
- Supports both encrypted (.tar.gz.gpg) and unencrypted (.tar.gz) backups

**Step 2: Decryption Password**
- Password field for encrypted backups
- Masked input for security
- Only required if backup file ends with .gpg

### Page 2: Database and Admin Configuration
![Wizard Page 2](wizard_page2.png)

**Step 3: Database Configuration**
- Database Host (default: localhost)
- Database Name (default: nextcloud)
- Database User (default: nextcloud)
- Database Password (masked, default: example)

**Step 4: Nextcloud Admin Credentials**
- Admin Username (default: admin)
- Admin Password (masked, default: admin)

### Page 3: Container Configuration
![Wizard Page 3](wizard_page3.png)

**Step 5: Container Configuration**
- Container Name (default: nextcloud-app)
- Container Port (default: 9000)
- Checkbox: "Use existing Nextcloud container if found"

### Navigation Features
- **Next/Back buttons** to navigate between pages
- Data is preserved when moving between pages
- **Start Restore** button appears on the final page
- Progress bar and status updates appear after starting restore
- Error validation on all pages
- Return to Main Menu button on all pages

## Key Improvements

### Before (v9 - Single Page)
- All 5 steps shown on one scrollable page
- Could be overwhelming for users
- Difficult to focus on individual steps

### After (v10 - Multi-Page Wizard)
- ✅ **Multi-page wizard** with clear step progression
- ✅ **Page 1**: Backup selection and decryption (Steps 1-2)
- ✅ **Page 2**: Database and admin configuration (Steps 3-4)
- ✅ **Page 3**: Container configuration (Step 5)
- ✅ **Next/Back navigation** between pages
- ✅ **Data persistence** across page navigation
- ✅ **Focused UI** - users see only relevant fields per page
- ✅ All inputs remain in main window (no pop-ups)
- ✅ Scrollable when needed for each page
- ✅ Clear section organization with descriptions
- ✅ Pre-filled default values
- ✅ Comprehensive validation
- ✅ Better user experience with guided workflow

## Validation Examples

The form validates all inputs before starting the restore:
- Backup file must exist
- Decryption password required for .gpg files
- All database fields must be filled
- Admin credentials must be provided
- Port must be a valid number (1-65535)

Error messages appear directly in the main window in red text, providing clear guidance to the user.

## Technical Details

- Window size: 700x900 (increased from 700x670)
- Scrollable canvas for better usability
- All fields use appropriate input types (text, password, checkbox)
- Default values match previous configuration
- Validation happens before restore starts
- Configuration automatically updates config.php with provided credentials
