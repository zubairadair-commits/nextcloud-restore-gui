# Quick Start: Scheduled Backups

This guide will help you set up automatic scheduled backups in just a few minutes.

## Prerequisites

✅ Windows operating system (Windows 10 or later)  
✅ Docker Desktop installed and running  
✅ Nextcloud container running  
✅ Nextcloud Restore & Backup Utility installed  

## 5-Minute Setup

### Step 1: Open the Application
Launch the **Nextcloud Restore & Backup Utility**

### Step 2: Click Schedule Backup
On the main page, click the **📅 Schedule Backup** button (purple button at the bottom)

### Step 3: Configure Your Schedule

#### Choose Backup Location
1. Click the **Browse** button next to "Backup Directory"
2. Select a folder where backups will be saved (e.g., `C:\Backups\Nextcloud`)
3. Make sure you have enough disk space

#### Select Frequency
Choose how often to back up:
- **Daily** - Recommended for most users (backup every day)
- **Weekly** - Good for less critical data (backup every Monday)
- **Monthly** - For long-term archival (backup on 1st of each month)

#### Set Backup Time
Enter the time in 24-hour format (HH:MM):
- `02:00` - 2:00 AM (recommended - least disruptive)
- `23:00` - 11:00 PM (before midnight)
- `12:00` - 12:00 PM (noon)

#### (Optional) Enable Encryption
1. Check the **Encrypt backups** checkbox
2. Enter a strong password
3. **IMPORTANT**: Remember this password! You'll need it to restore backups

### Step 4: Create the Schedule
Click the **Create/Update Schedule** button

### Step 5: Confirm Success
You should see a success message:
```
✓ Scheduled backup created successfully!
Frequency: daily
Time: 02:00
Backup Directory: C:\Backups\Nextcloud
```

### Step 6: Verify
Return to the main menu. You should see:
```
📅 Scheduled: daily at 02:00
```

## Done! 🎉

Your backups will now run automatically according to your schedule. Make sure:
- Your computer is on at the scheduled time (or set it to wake from sleep)
- Docker Desktop is running
- Nextcloud container is running

## What Happens Next?

At the scheduled time (e.g., 2:00 AM):
1. Windows Task Scheduler launches the backup utility
2. The app runs silently in the background (no windows appear)
3. It performs a complete backup of your Nextcloud data
4. The backup is saved to your chosen directory
5. (Optional) The backup is encrypted with your password

**Note**: The scheduler automatically detects whether you're running from a Python script (.py) or compiled executable (.exe) and constructs the appropriate command. This ensures reliability in both development and production environments.

## Managing Your Schedule

### View Schedule Status
On the main page, you'll see your schedule status:
```
📅 Scheduled: daily at 02:00
```

### Disable Temporarily
If you need to pause backups:
1. Click **📅 Schedule Backup**
2. Click **Disable Schedule**
3. Schedule is paused but not deleted

### Delete Permanently
To remove the schedule completely:
1. Click **📅 Schedule Backup**
2. Click **Delete Schedule**
3. Confirm deletion

### Update Schedule
To change the time or frequency:
1. Click **📅 Schedule Backup**
2. Modify the settings
3. Click **Create/Update Schedule**
4. New settings replace the old schedule

## Backup Location

Your backups are saved with timestamps:
```
C:\Backups\Nextcloud\
├── nextcloud-backup-20251012_020000.tar.gz
├── nextcloud-backup-20251013_020000.tar.gz
├── nextcloud-backup-20251014_020000.tar.gz
└── ...
```

If encrypted, they'll have a `.gpg` extension:
```
├── nextcloud-backup-20251012_020000.tar.gz.gpg
```

## Troubleshooting

### Schedule Not Running?

**Check Docker is Running**
- Open Docker Desktop
- Ensure it shows "Engine running"
- If not, click "Start"

**Check Computer is On**
- Your computer must be on (not shut down) at scheduled time
- Sleep mode is OK if "Wake timers" are enabled

**Check Task Scheduler**
1. Press `Win + R`
2. Type `taskschd.msc` and press Enter
3. Find "NextcloudBackup" task in the list
4. Check "Last Run Time" and "Last Run Result"

**Check Backup Directory**
- Ensure directory exists
- Ensure you have write permissions
- Ensure sufficient disk space

### Backup Failed?

**Check Database Utilities**
For PostgreSQL backups:
```
pg_dump --version
```
Should show PostgreSQL version. If not found, install PostgreSQL client tools.

For MySQL/MariaDB backups:
```
mysqldump --version
```
Should show MySQL version. If not found, install MySQL client tools.

**Check Container is Running**
```
docker ps
```
Should show your Nextcloud container in the list.

## Tips & Best Practices

### 🕐 Schedule Time
- Choose a time when your computer is on but you're not actively working
- Early morning (2-4 AM) is ideal
- Avoid scheduling during peak usage times

### 💾 Backup Storage
- Use a separate drive if possible (not same as Nextcloud data)
- Consider external drives for additional safety
- Monitor disk space - backups can be large

### 🔐 Encryption
- **Always use encryption** for sensitive data
- Store password in a secure password manager
- Test restore with encrypted backup to verify password works

### 📅 Frequency
- **Daily** - For production/critical data
- **Weekly** - For development/testing environments
- **Monthly** - For archival/historical records

### 🧪 Test Restores
- Periodically test restoring from backup
- Verify data integrity
- Ensure encryption password works

### 🗑️ Cleanup Old Backups
- Manually delete old backups when disk space is low
- Keep at least 3-7 recent backups
- Consider monthly archival to external storage

## Example Schedules

### For Home Users (Daily Evening Backup)
```
Frequency: Daily
Time: 22:00 (10:00 PM)
Encrypt: Yes
Directory: D:\Backups\Nextcloud
```

### For Small Business (Daily Night Backup)
```
Frequency: Daily
Time: 02:00 (2:00 AM)
Encrypt: Yes
Directory: \\NAS\Backups\Nextcloud
```

### For Development (Weekly Backup)
```
Frequency: Weekly
Time: 23:00 (11:00 PM)
Encrypt: No
Directory: C:\Dev\Backups\Nextcloud
```

## Advanced Usage

### Multiple Backup Locations
Currently not supported through GUI. Workaround:
1. Create first schedule through GUI
2. Manually create additional tasks in Task Scheduler pointing to different directories

### Custom Schedule (e.g., Twice Daily)
Not supported through GUI. Workaround:
1. Create first schedule for morning backup
2. Use Task Scheduler to create second task for evening backup

### Email Notifications
Not currently supported. Future enhancement planned.

### Automated Cleanup
Not currently supported. Manual cleanup required. Future enhancement planned.

## Support

If you encounter issues:

1. **Check Docker**: Ensure Docker Desktop is running
2. **Check Logs**: Look at Task Scheduler history for errors
3. **Check Permissions**: Ensure write access to backup directory
4. **Check Documentation**: Review SCHEDULED_BACKUP_FEATURE.md
5. **Check Disk Space**: Ensure sufficient space for backups

## Next Steps

After setting up scheduled backups:

1. ✅ Test the schedule by temporarily changing time to 1-2 minutes from now
2. ✅ Verify backup file is created in your chosen directory
3. ✅ Test restoring from a scheduled backup to verify it works
4. ✅ Document your encryption password in a secure location
5. ✅ Set up monitoring to check backup success (optional)

## Comparison: Manual vs Scheduled Backups

| Feature | Manual Backup | Scheduled Backup |
|---------|--------------|------------------|
| **Frequency** | When you remember | Automatic |
| **Convenience** | Must click button | Set and forget |
| **Reliability** | Depends on you | Very reliable |
| **Notification** | GUI dialog | Silent execution |
| **Best For** | On-demand, testing | Production use |

## Security Notes

⚠️ **Password Storage**
- Encryption password is stored in plain text in configuration file
- Configuration file location: `%USERPROFILE%\.nextcloud_backup\schedule_config.json`
- Only accessible by your user account (OS permissions)
- **Recommendation**: Use a strong, unique password

⚠️ **Backup Security**
- Store backups on encrypted drives if possible
- Use file encryption for backup directory
- Limit access to backup directory
- Regularly verify backup integrity

## FAQ

**Q: Can I schedule backups on macOS or Linux?**  
A: Not currently. Windows only. Future versions may support macOS (launchd) and Linux (cron).

**Q: Will scheduled backups wake my computer from sleep?**  
A: Yes, if "Wake timers" are enabled in Windows power settings. Otherwise, computer must be on.

**Q: How much disk space do I need?**  
A: At least 2-3x your Nextcloud data size. For example, if Nextcloud uses 10GB, allocate 20-30GB for backups.

**Q: Can I have multiple schedules?**  
A: Not currently through GUI. Only one schedule at a time. Future enhancement planned.

**Q: What if backup fails?**  
A: Check Task Scheduler history for error details. Common issues: Docker not running, insufficient disk space, missing database utilities.

**Q: Can I backup to network drive?**  
A: Yes! Use UNC path like `\\NAS\Backups\Nextcloud` or mapped drive letter.

**Q: Does scheduled backup include database?**  
A: Yes! Same complete backup as manual backup: config, data, apps, and database.

**Q: How do I disable password prompt?**  
A: Scheduled backups never show password prompts. Password is read from configuration file.

**Q: Can I backup to cloud storage?**  
A: Not directly. Backup to local directory first, then use cloud sync tool (OneDrive, Google Drive, etc.) to upload.

## Related Documentation

- **SCHEDULED_BACKUP_FEATURE.md** - Complete feature documentation
- **UI_MOCKUP_SCHEDULED_BACKUP.md** - UI mockups and visual guide
- **Main README** - General application documentation

---

**Version**: 1.1  
**Last Updated**: October 2025  
**Platform**: Windows 10/11  
**Status**: Production Ready ✅

**What's New in v1.1:**
- Smart detection of Python scripts (.py) vs executables (.exe)
- Automatic Python interpreter invocation for script-based installations
- Enhanced reliability for both development and production use
