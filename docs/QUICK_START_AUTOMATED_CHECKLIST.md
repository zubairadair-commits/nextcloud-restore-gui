# Quick Start: Automated Setup Checklist

## Overview

The automated setup checklist helps you create reliable scheduled backups by validating your configuration before creating the task. This guide shows you how to use all the new features.

---

## 🚀 Creating Your First Scheduled Backup

### Step 1: Open Schedule Backup

1. Launch Nextcloud Restore & Backup Utility
2. Click **"📅 Schedule Backup"** button on main screen

### Step 2: Configure Settings

1. **Choose Backup Directory**
   - Click **Browse** button
   - Select where you want backups saved
   - TIP: Use a cloud sync folder (OneDrive, Google Drive) for automatic cloud backup

2. **Select Frequency**
   - Choose: Daily, Weekly, or Monthly
   - Daily is recommended for critical data

3. **Set Backup Time**
   - Enter time in 24-hour format (HH:MM)
   - Example: 02:00 for 2 AM, 14:30 for 2:30 PM
   - NOTE: Time is in your local system timezone

4. **Configure Encryption** (Optional)
   - Check "Encrypt backups" if desired
   - Enter a strong password
   - IMPORTANT: Remember this password - you'll need it to restore!

### Step 3: Test Your Configuration (Recommended)

Before creating the schedule, test it works:

1. Click **"🧪 Test Run"** button
2. Wait for test to complete (a few seconds)
3. Review the result:
   - ✅ Success: Configuration is correct, proceed to create schedule
   - ❌ Failure: Fix the reported issue and test again

**Example Success Message**:
```
✓ Test backup successful!

Test file created: test_backup_20241014_150530.tar.gz
Size: 234 bytes
Location: C:\Backups\Nextcloud

Your scheduled backup configuration is working correctly.
```

### Step 4: Create the Schedule

1. Click **"Create/Update Schedule"** button
2. **Automatic validation runs** - please wait
3. Review validation results dialog:
   - ✅ All checks passed: Click **Yes** to proceed
   - ❌ Some checks failed: Click **OK**, fix issues, try again

**Example Validation Success**:
```
✅ All Validation Checks Passed

✓ Executable path exists
✓ Start directory is valid
✓ Task arguments are correct
✓ Backup directory is writable
✓ Log file is writable
✓ Task fields are valid

Proceed with creating the scheduled task?
```

4. If validation passes, confirm creation
5. Task is created successfully!

---

## 📊 Monitoring Your Scheduled Backups

### Check Last Run Status

After your first scheduled backup runs:

1. Open **Schedule Backup** screen
2. Look for **"📊 Last Run Status"** section
3. Review information:
   - When last backup ran
   - When next backup is scheduled
   - Most recent backup file details

**Example Display**:
```
Status: Ready
Last Run: 2024-10-14 02:00:15
Next Run: 2024-10-15 02:00:00

✓ Recent Backup Found:
  File: nextcloud_backup_20241014_020015.tar.gz
  Created: 2024-10-14 02:00:45
  Size: 125.67 MB
  Age: 13.1 hours ago
```

### View Logs

To see what happened during backups:

1. In Last Run Status section, click **"📄 View Recent Logs"**
2. Review log entries:
   - SCHEDULED: Scheduled backup events
   - VALIDATION: Validation checks
   - TEST RUN: Test backup runs
3. Look for errors or warnings
4. Click **Close** when done

### Verify Backup is Working

To confirm scheduled backup is functioning:

1. Click **"🔍 Verify Scheduled Backup"** button
2. Wait for verification to complete
3. Review results:
   - ✅ Success: Everything working correctly
   - ⚠ Warning: Backup old or no recent logs
   - ❌ Failure: No recent backup found

---

## 🔧 Troubleshooting Common Issues

### Issue: Validation Fails - "Backup directory is not writable"

**Solution**:
1. Check the directory exists
2. Right-click directory → Properties → Security
3. Ensure your user has "Modify" permission
4. Try a different directory (e.g., Documents folder)

### Issue: Test Run Fails

**Solution**:
1. Read the error message carefully
2. Check backup directory path is correct
3. Ensure enough disk space available
4. Try disabling encryption temporarily
5. Click "View Recent Logs" for details

### Issue: No Recent Backup Found

**Solution**:
1. Open Windows Task Scheduler:
   - Press Win+R, type `taskschd.msc`, press Enter
2. Find task named **"NextcloudBackup"**
3. Check:
   - Task is Enabled
   - Last Run Time shows recent execution
   - Last Run Result is 0x0 (success)
4. If task never ran:
   - Right-click task → Run
   - Check for errors
5. Review logs for error messages

### Issue: Invalid Time Format

**Solution**:
- Use 24-hour format: HH:MM
- Valid examples: 00:00, 02:00, 14:30, 23:59
- Invalid examples: 25:00, 2:00, 14:60

---

## 💡 Best Practices

### 1. Test First
Always click "Test Run" before creating schedule. This catches issues immediately.

### 2. Use Cloud Sync
Select a cloud sync folder (OneDrive, Google Drive, Dropbox) as backup destination for automatic cloud backup.

### 3. Choose Off-Peak Time
Schedule backups during low-usage periods:
- 2:00 AM for home users
- After business hours for office systems

### 4. Enable Encryption
For sensitive data:
1. Check "Encrypt backups"
2. Use a strong password
3. Store password securely (password manager)

### 5. Regular Verification
Once a week:
1. Open Schedule Backup screen
2. Check Last Run Status
3. Click "Verify Scheduled Backup"
4. Confirm backup is recent and logs look good

### 6. Monitor Disk Space
- Check backup directory has sufficient space
- Delete old backups when disk space low
- Consider backup retention policy

### 7. Test Restore
Periodically:
1. Use "Restore from Backup" feature
2. Test with an old backup
3. Ensure restore process works

---

## ⚙️ Understanding Validation Checks

### What Gets Validated

1. **Executable Path** ✓
   - Confirms backup program exists
   - Ensures path is accessible

2. **Start Directory** ✓
   - Verifies program's parent folder is valid
   - Required for Task Scheduler

3. **Task Arguments** ✓
   - Checks all required arguments present
   - Validates argument format

4. **Backup Directory** ✓
   - Tests directory exists
   - Verifies write permissions
   - Creates test file to confirm

5. **Log File** ✓
   - Ensures log directory accessible
   - Tests log write capability

6. **Task Fields** ✓
   - Validates schedule type (daily/weekly/monthly)
   - Checks time format (HH:MM)
   - Ensures task name not empty

### Why Validation Matters

**Without validation**:
- Task created but fails silently
- No backups despite thinking you're protected
- Issues discovered only when you need restore

**With validation**:
- Issues caught immediately
- Fix before task creation
- Confidence in backup reliability

---

## 📱 Quick Reference

### Button Locations

| Button | Location | Purpose |
|--------|----------|---------|
| 🧪 Test Run | Below configuration | Test configuration instantly |
| Create/Update Schedule | Below configuration | Create task with validation |
| 📄 View Recent Logs | In Last Run Status | View log entries |
| 🔍 Verify Scheduled Backup | Below Last Run Status | Confirm backup working |

### Status Indicators

| Symbol | Meaning |
|--------|---------|
| ✅ | All checks passed |
| ❌ | Validation failed |
| ✓ | Individual check passed |
| ✗ | Individual check failed |
| ⚠ | Warning or caution |

### Common Validation Errors

| Error | Quick Fix |
|-------|-----------|
| Directory not writable | Check permissions or choose different folder |
| Invalid time format | Use HH:MM (e.g., 02:00, 14:30) |
| Executable not found | Reinstall application |
| Log file not writable | Check Documents folder permissions |

---

## 🎯 Success Checklist

Before first scheduled run:
- [ ] Test Run completed successfully
- [ ] Validation passed all checks
- [ ] Schedule created in Task Scheduler
- [ ] Backup directory has sufficient space
- [ ] Encryption password recorded (if enabled)

After first scheduled run:
- [ ] Last Run Status shows recent backup
- [ ] Backup file exists in directory
- [ ] Backup file size reasonable
- [ ] Verification check passes
- [ ] Logs show successful completion

Weekly maintenance:
- [ ] Check Last Run Status
- [ ] Verify recent backup exists
- [ ] Review logs for errors
- [ ] Confirm sufficient disk space
- [ ] Test restore if possible

---

## 🆘 Getting Help

### Built-in Help

1. **Tooltips**: Hover over ℹ️ icons for help
2. **Error Messages**: Read carefully, they explain the issue
3. **View Logs**: Check for detailed error information

### Self-Service Troubleshooting

1. Run "Test Run" to isolate issues
2. Check "View Recent Logs" for errors
3. Verify Windows Task Scheduler shows task
4. Confirm backup directory permissions
5. Ensure sufficient disk space

### Documentation

- `AUTOMATED_SETUP_CHECKLIST.md` - Complete feature documentation
- `SCHEDULED_BACKUP_FEATURE.md` - Original scheduled backup guide
- `UI_MOCKUP_AUTOMATED_CHECKLIST.md` - Visual UI guide

---

## 📈 Advanced Usage

### Multiple Scheduled Backups

Currently one schedule supported. For multiple:
1. Create first schedule via app
2. Manually duplicate in Task Scheduler with different name
3. Adjust schedule and directory for each

### Custom Schedule Types

For custom frequencies not in UI:
1. Create daily/weekly/monthly schedule in app
2. Open Task Scheduler (Win+R → taskschd.msc)
3. Find "NextcloudBackup" task
4. Right-click → Properties → Triggers → Edit
5. Customize schedule as needed

### Backup Retention

To prevent disk space issues:
1. Regularly delete old backups manually, or
2. Use Windows Storage Sense to auto-delete old files, or
3. Script automatic cleanup (advanced)

### Cloud Sync Monitoring

If using cloud sync folder:
1. Check cloud provider's sync status
2. Ensure backups appear in cloud
3. Monitor cloud storage quota
4. Verify sync completes before next backup

---

## 🎓 Learning More

### Understanding Logs

Log entries format:
```
YYYY-MM-DD HH:MM:SS - LEVEL - CONTEXT: Message
```

Log levels:
- **INFO**: Normal operation
- **WARNING**: Potential issue, but not critical
- **ERROR**: Problem occurred

Log contexts:
- **VALIDATION**: Pre-creation checks
- **TEST RUN**: Test backup execution
- **SCHEDULED**: Scheduled backup execution
- **VERIFICATION**: Post-run verification

### Task Scheduler Basics

View your scheduled task:
1. Press Win+R
2. Type `taskschd.msc`
3. Press Enter
4. Find "NextcloudBackup" in task list

Task properties:
- **General**: Task name, description
- **Triggers**: When task runs
- **Actions**: What task does
- **Conditions**: Requirements for running
- **Settings**: Additional options
- **History**: Past run records

---

## ✨ Tips for Success

1. **Start Simple**: First schedule with default settings
2. **Test First**: Always use Test Run before creating schedule
3. **Monitor Initially**: Check after first few runs
4. **Document Password**: If using encryption, store password safely
5. **Regular Reviews**: Weekly verification recommended
6. **Disk Space**: Monitor backup directory space
7. **Cloud Sync**: Use for automatic off-site backup
8. **Restore Testing**: Periodically test restore process

---

## 🏁 Summary

The automated setup checklist ensures your scheduled backups work correctly by:

1. ✓ Validating configuration before task creation
2. ✓ Providing instant testing capability
3. ✓ Showing last run status and results
4. ✓ Offering easy log access
5. ✓ Verifying backups are working

Follow this guide to set up reliable, automated Nextcloud backups with confidence!
