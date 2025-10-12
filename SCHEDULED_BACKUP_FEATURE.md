# Scheduled Backup Feature Documentation

## Overview
The Nextcloud Restore & Backup Utility now supports automatic scheduled backups through Windows Task Scheduler. Users can configure, enable, disable, and delete backup schedules directly from the GUI without needing to manually interact with Windows Task Scheduler.

## Key Features

### 1. GUI-Based Schedule Configuration
- **No manual Task Scheduler usage required** - Everything is managed from the application
- **Visual status indicators** - See at a glance if backups are scheduled
- **Easy management** - Enable, disable, or delete schedules with one click

### 2. Flexible Scheduling Options
- **Daily backups** - Run backup every day at specified time
- **Weekly backups** - Run backup once per week (default: Monday)
- **Monthly backups** - Run backup once per month (default: 1st)
- **Custom time** - Set any time in HH:MM format (e.g., 02:00 for 2 AM)

### 3. Encryption Support
- **Optional encryption** - Choose whether to encrypt scheduled backups
- **Password management** - Store encryption password securely in configuration
- **Consistent with manual backups** - Same encryption method as manual backups

### 4. Silent Execution
- **No console windows** - Uses subprocess.CREATE_NO_WINDOW flag
- **Background operation** - Runs completely silently when triggered by scheduler
- **Log-based feedback** - Scheduled backups log to console for monitoring

## User Interface

### Landing Page
The main landing page now includes a new button:

```
┌────────────────────────────────────────┐
│   Nextcloud Restore & Backup Utility   │
├────────────────────────────────────────┤
│                                        │
│   ┌──────────────────────────────┐    │
│   │     🔄 Backup Now           │    │
│   └──────────────────────────────┘    │
│                                        │
│   ┌──────────────────────────────┐    │
│   │  🛠 Restore from Backup     │    │
│   └──────────────────────────────┘    │
│                                        │
│   ┌──────────────────────────────┐    │
│   │ ✨ Start New Nextcloud      │    │
│   │    Instance                  │    │
│   └──────────────────────────────┘    │
│                                        │
│   ┌──────────────────────────────┐    │
│   │  📅 Schedule Backup          │    │ ← NEW!
│   └──────────────────────────────┘    │
│                                        │
│  📅 Scheduled: daily at 02:00         │ ← Status shown if scheduled
│                                        │
└────────────────────────────────────────┘
```

### Schedule Configuration Screen

When clicking "Schedule Backup", users see:

```
┌────────────────────────────────────────────────────────────┐
│              Schedule Automatic Backups                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              Current Status                          │ │
│  │  ✓ Scheduled backup is active                       │ │
│  │  Frequency: daily                                    │ │
│  │  Time: 02:00                                         │ │
│  │  Backup Directory: C:\Backups                        │ │
│  │                                                      │ │
│  │  [Disable Schedule]  [Delete Schedule]               │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Configure New Schedule                                    │
│  ─────────────────────────────────────────────────────── │
│                                                            │
│  Backup Directory:                                         │
│  [C:\Backups\Nextcloud              ] [Browse]            │
│                                                            │
│  Frequency:                                                │
│  ○ Daily    ○ Weekly    ○ Monthly                         │
│                                                            │
│  Backup Time (HH:MM):                                      │
│  [02:00]                                                   │
│                                                            │
│  ☑ Encrypt backups                                         │
│                                                            │
│  Encryption Password:                                      │
│  [********]                                                │
│                                                            │
│           [Create/Update Schedule]                         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Technical Implementation

### Command-Line Arguments
The application supports the following arguments for scheduled execution:

```bash
# Run scheduled backup
nextcloud_restore_and_backup-v9.exe --scheduled --backup-dir "C:\Backups"

# Run with encryption
nextcloud_restore_and_backup-v9.exe --scheduled --backup-dir "C:\Backups" --encrypt --password "mypassword"

# Run without encryption
nextcloud_restore_and_backup-v9.exe --scheduled --backup-dir "C:\Backups" --no-encrypt
```

### Windows Task Scheduler Integration
The application uses the `schtasks` command-line utility to:
- Create scheduled tasks
- Delete scheduled tasks
- Query task status
- Enable/disable tasks

Example task creation command:
```bash
schtasks /Create /TN "NextcloudBackup" /TR "C:\path\to\app.exe --scheduled --backup-dir C:\Backups" /ST 02:00 /SC DAILY /F
```

### Configuration Storage
Schedule configuration is stored in JSON format at:
```
%USERPROFILE%\.nextcloud_backup\schedule_config.json
```

Example configuration:
```json
{
  "task_name": "NextcloudBackup",
  "backup_dir": "C:\\Backups",
  "frequency": "daily",
  "time": "02:00",
  "encrypt": true,
  "password": "encrypted_password",
  "enabled": true,
  "created_at": "2025-10-12T22:30:00"
}
```

## Security Considerations

### Password Storage
- Passwords are stored in plain text in the configuration file
- Configuration file is stored in user's home directory
- File permissions are set by the OS (user-only access on most systems)
- **Recommendation**: Use a strong password and ensure system security

### Silent Execution
- Scheduled backups run with CREATE_NO_WINDOW flag
- No console windows appear during execution
- All output is logged for monitoring purposes

## Usage Guide

### Setting Up a Scheduled Backup

1. **Launch the application**
   - Open Nextcloud Restore & Backup Utility

2. **Click "Schedule Backup"**
   - Click the "📅 Schedule Backup" button on the main page

3. **Configure the schedule**
   - Select backup directory using Browse button
   - Choose frequency (daily, weekly, or monthly)
   - Set the time (24-hour format, e.g., 02:00 for 2 AM)
   - Optionally enable encryption and set password

4. **Create the schedule**
   - Click "Create/Update Schedule" button
   - Confirm the success message

5. **Verify the schedule**
   - Return to main page to see schedule status
   - Or check Windows Task Scheduler (optional)

### Managing Scheduled Backups

#### Disable a Schedule
1. Click "Schedule Backup" button
2. Click "Disable Schedule" button
3. Schedule is paused but not deleted

#### Delete a Schedule
1. Click "Schedule Backup" button
2. Click "Delete Schedule" button
3. Confirm deletion
4. Schedule is completely removed

#### Update a Schedule
1. Click "Schedule Backup" button
2. Modify the configuration settings
3. Click "Create/Update Schedule" button
4. New settings replace old schedule

## Platform Support

### Windows
✅ **Fully Supported**
- Uses Windows Task Scheduler
- All features available
- Tested on Windows 10/11

### macOS
⚠️ **Not Currently Supported**
- Could be implemented using `launchd`
- Future enhancement

### Linux
⚠️ **Not Currently Supported**
- Could be implemented using `cron`
- Future enhancement

## Troubleshooting

### Schedule Not Running
1. **Check Docker is running**
   - Scheduled backups require Docker to be running
   - Start Docker Desktop before scheduled time

2. **Check Task Scheduler**
   - Open Windows Task Scheduler
   - Look for "NextcloudBackup" task
   - Check task history for errors

3. **Check Permissions**
   - Ensure user has permission to write to backup directory
   - Ensure user has permission to access Docker

### Backup Fails Silently
1. **Check Docker Containers**
   - Ensure Nextcloud container is running
   - Ensure database container is running (if applicable)

2. **Check Disk Space**
   - Ensure sufficient disk space in backup directory
   - Ensure sufficient disk space in temp directory

3. **Check Database Utilities**
   - For PostgreSQL: Ensure pg_dump is available
   - For MySQL/MariaDB: Ensure mysqldump is available

## Future Enhancements

### Planned Features
- [ ] Email notifications on backup success/failure
- [ ] Backup retention policies (auto-delete old backups)
- [ ] Multiple schedule support (e.g., daily + weekly)
- [ ] macOS support using launchd
- [ ] Linux support using cron
- [ ] Backup verification after scheduled run
- [ ] Cloud upload integration (S3, Azure, etc.)

### Security Enhancements
- [ ] Encrypted password storage using OS keyring
- [ ] Two-factor authentication for schedule creation
- [ ] Audit log of scheduled backup operations

## API Reference

### Functions

#### `create_scheduled_task(task_name, schedule_type, schedule_time, backup_dir, encrypt, password="")`
Creates a Windows scheduled task for automatic backups.

**Parameters:**
- `task_name` (str): Name for the scheduled task
- `schedule_type` (str): 'daily', 'weekly', or 'monthly'
- `schedule_time` (str): Time in HH:MM format
- `backup_dir` (str): Directory to save backups
- `encrypt` (bool): Enable encryption
- `password` (str): Encryption password (optional)

**Returns:** `(success: bool, message: str)` tuple

#### `delete_scheduled_task(task_name)`
Deletes a Windows scheduled task.

**Parameters:**
- `task_name` (str): Name of the scheduled task

**Returns:** `(success: bool, message: str)` tuple

#### `get_scheduled_task_status(task_name)`
Gets the status of a Windows scheduled task.

**Parameters:**
- `task_name` (str): Name of the scheduled task

**Returns:** `dict` with status info or `None` if not found

#### `enable_scheduled_task(task_name)`
Enables a Windows scheduled task.

**Parameters:**
- `task_name` (str): Name of the scheduled task

**Returns:** `(success: bool, message: str)` tuple

#### `disable_scheduled_task(task_name)`
Disables a Windows scheduled task.

**Parameters:**
- `task_name` (str): Name of the scheduled task

**Returns:** `(success: bool, message: str)` tuple

## Change Log

### Version 1.0 (Current)
- Initial implementation of scheduled backup feature
- Windows Task Scheduler integration
- GUI-based schedule configuration
- Support for daily, weekly, monthly schedules
- Encryption support in scheduled backups
- Silent execution with CREATE_NO_WINDOW flag
- Configuration persistence in JSON format

## Support

For issues or questions about the scheduled backup feature:
1. Check this documentation first
2. Review the troubleshooting section
3. Check Windows Task Scheduler for task details
4. Review application logs for error messages
5. Open an issue on GitHub with detailed information

## License

This feature is part of the Nextcloud Restore & Backup Utility and follows the same license as the main project.
