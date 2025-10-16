# User-Visible Changes: Scheduled Backup Enhancements

This document describes what users will see and experience after these changes are deployed.

---

## Change 1: Windows Task Scheduler Settings

### BEFORE ❌
When you created a scheduled backup and checked Windows Task Scheduler, you would see:

**Task Properties → General Tab:**
```
[ ] Run with highest privileges     ← NOT CHECKED
```

**Task Properties → Settings Tab:**
```
[ ] Run task as soon as possible    ← NOT CHECKED
    after a scheduled start is missed
```

**Result:**
- Backups might fail due to permission issues
- Backups would be skipped if computer was off/asleep at scheduled time
- No automatic catch-up for missed backups

---

### AFTER ✅
When you create a scheduled backup now, Windows Task Scheduler shows:

**Task Properties → General Tab:**
```
[✓] Run with highest privileges     ← AUTOMATICALLY CHECKED
```

**Task Properties → Settings Tab:**
```
[✓] Run task as soon as possible    ← AUTOMATICALLY CHECKED
    after a scheduled start is missed
```

**Result:**
- ✅ Backups run with full necessary permissions
- ✅ Missed backups automatically run when computer is available
- ✅ More reliable backup coverage

---

## Change 2: Backup History Display

### BEFORE ❌

**Main Page:**
```
┌─────────────────────────────────────┐
│  📜 Backup History                  │  ← Click this button
└─────────────────────────────────────┘
```

**Backup History Dialog:**
```
┌─────────────────────────────────────────────────────┐
│  📜 Backup History & Restore Points                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📅 2025-01-15 10:30:00    💾 150.2 MB             │
│  📁 nextcloud-backup-20250115_103000.tar.gz        │
│  Manual backup created via GUI                     │
│                                                     │
│  📅 2025-01-14 09:15:00    💾 148.7 MB             │
│  📁 nextcloud-backup-20250114_091500.tar.gz        │
│  Manual backup created via GUI                     │
│                                                     │
│  ⚠️ Scheduled backups are NOT visible here         │
│  You must check file system to verify them         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Problem:**
- Scheduled backups don't appear in history
- Can't verify if scheduled backups ran successfully
- Must manually check backup folder in file system
- Fragmented user experience

---

### AFTER ✅

**Main Page:**
```
┌─────────────────────────────────────┐
│  📜 Backup History                  │  ← Click this button
└─────────────────────────────────────┘
```

**Backup History Dialog:**
```
┌─────────────────────────────────────────────────────┐
│  📜 Backup History & Restore Points                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📅 2025-01-16 02:00:00    💾 152.1 MB             │
│  📁 nextcloud-backup-20250116_020000.tar.gz        │
│  🔒 Encrypted | DB: PostgreSQL                     │
│  Scheduled backup                  ← NEW INDICATOR │
│                                                     │
│  📅 2025-01-15 10:30:00    💾 150.2 MB             │
│  📁 nextcloud-backup-20250115_103000.tar.gz        │
│  Manual backup                                     │
│                                                     │
│  📅 2025-01-15 02:00:00    💾 151.8 MB             │
│  📁 nextcloud-backup-20250115_020000.tar.gz        │
│  🔒 Encrypted | DB: PostgreSQL                     │
│  Scheduled backup                  ← NEW INDICATOR │
│                                                     │
│  📅 2025-01-14 09:15:00    💾 148.7 MB             │
│  📁 nextcloud-backup-20250114_091500.tar.gz        │
│  Manual backup                                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ All backups (manual + scheduled) visible in one place
- ✅ Most recent backups appear first
- ✅ Can immediately verify scheduled backups ran
- ✅ Scheduled backups clearly marked
- ✅ Shows full metadata (size, encryption, database type)
- ✅ No need to check file system manually
- ✅ Unified, professional experience

---

## User Workflow Examples

### Example 1: Creating a Scheduled Backup

**Steps:**
1. Open the app
2. Click "Schedule Backup" button
3. Configure schedule (daily at 2:00 AM)
4. Click "Create Schedule"

**What Happens Now (Automatically):**
- ✅ Task created in Windows Task Scheduler
- ✅ Task set to run with highest privileges
- ✅ Task configured to run missed backups ASAP
- ✅ Everything configured correctly without manual intervention

**What You Need to Do:**
- Nothing! It's all automatic

---

### Example 2: Verifying Scheduled Backups

**BEFORE - Required Steps:**
1. Open File Explorer
2. Navigate to backup folder
3. Sort by date
4. Check if backup file exists
5. Check file size and timestamp
6. Cannot see if backup was successful or had errors

**AFTER - Simplified Steps:**
1. Open the app
2. Click "📜 Backup History" button
3. See all backups including most recent scheduled backup
4. See full details: timestamp, size, encryption, database type
5. See "Scheduled backup" note

---

### Example 3: Computer Was Off During Scheduled Backup

**Scenario:** 
- Scheduled backup set for 2:00 AM
- Computer was turned off at midnight
- Computer turned on at 8:00 AM

**BEFORE - What Happened:**
- ❌ Backup was skipped
- ❌ No backup created that day
- ❌ Gap in backup coverage

**AFTER - What Happens:**
- ✅ Task detects it missed the 2:00 AM schedule
- ✅ Task runs automatically at 8:00 AM (ASAP after system available)
- ✅ Backup is created
- ✅ Backup appears in history
- ✅ No gap in backup coverage

---

## How to Verify Changes (Windows Only)

### Verify Task Scheduler Settings

1. Create a scheduled backup via the app
2. Press `Win + R`, type `taskschd.msc`, press Enter
3. Navigate to "Task Scheduler Library"
4. Find your scheduled task (e.g., "NextcloudBackup")
5. Right-click → Properties

**Check General Tab:**
```
┌─────────────────────────────────────────┐
│  General | Triggers | Actions | ...    │
├─────────────────────────────────────────┤
│  Name: NextcloudBackup                  │
│                                         │
│  Security options:                      │
│  ○ Run only when user is logged on     │
│  ● Run whether user is logged on or not│
│                                         │
│  [✓] Run with highest privileges  ← CHECK THIS │
│                                         │
└─────────────────────────────────────────┘
```

**Check Settings Tab:**
```
┌─────────────────────────────────────────┐
│  General | Triggers | Actions | ...    │
├─────────────────────────────────────────┤
│  [✓] Run task as soon as possible      │  ← CHECK THIS
│      after a scheduled start is missed │
│                                         │
│  [ ] Stop the task if it runs longer   │
│      than: [3 days]                    │
│                                         │
└─────────────────────────────────────────┘
```

### Verify Backup History

1. Wait for a scheduled backup to run (or create one manually)
2. Open the Nextcloud Restore & Backup Utility
3. Click "📜 Backup History" button
4. Look for recent backups

**What to Check:**
- ✅ Scheduled backup appears in the list
- ✅ Shows correct timestamp (when it was created)
- ✅ Shows file size in MB
- ✅ Shows encryption status (🔒 if encrypted)
- ✅ Shows database type (PostgreSQL, MySQL, etc.)
- ✅ Shows note: "Scheduled backup"
- ✅ Most recent backup is at the top

---

## Frequently Asked Questions

### Q: Do I need to do anything different when creating scheduled backups?
**A:** No. The changes are automatic. Just create scheduled backups as you normally would, and the new settings will be applied automatically.

### Q: Will my existing scheduled tasks get these new settings?
**A:** Existing tasks will continue to work as before. To get the new settings, delete and recreate the scheduled task using the app.

### Q: Can I still see manual backups in the history?
**A:** Yes! The history shows ALL backups - both manual and scheduled. They're all in one list, sorted by most recent first.

### Q: How can I tell if a backup was scheduled or manual?
**A:** Scheduled backups have a note that says "Scheduled backup". Manual backups will show "Manual backup" or a custom note if you added one.

### Q: Do I need to manually refresh the backup history to see new backups?
**A:** No. When you open the Backup History dialog, it automatically shows the most recent backups including any new scheduled backups.

### Q: What if I'm on Linux or Mac?
**A:** The backup history feature works on all platforms. The Task Scheduler features (highest privileges, missed task handling) are Windows-only, as scheduled backup support is currently Windows-only in this app.

---

## Summary of Benefits

| Benefit | Description |
|---------|-------------|
| **Better Reliability** | Backups run with proper permissions and handle missed schedules |
| **Better Visibility** | All backups visible in one place, no file system checking needed |
| **Better Verification** | Can immediately confirm scheduled backups are running |
| **Better User Experience** | Professional, unified interface for backup management |
| **Automatic Configuration** | No manual Task Scheduler configuration needed |
| **No Breaking Changes** | Everything works as before, just better |

---

## Visual Comparison

### Task Scheduler
```
BEFORE:                        AFTER:
┌────────────────────┐        ┌────────────────────┐
│ Run with highest   │        │ Run with highest   │
│ privileges:        │        │ privileges:        │
│ [ ] Not set        │   →    │ [✓] Enabled        │
│                    │        │                    │
│ Run missed tasks:  │        │ Run missed tasks:  │
│ [ ] Not set        │        │ [✓] Enabled        │
└────────────────────┘        └────────────────────┘
```

### Backup History
```
BEFORE:                        AFTER:
┌────────────────────┐        ┌────────────────────┐
│ Backup History     │        │ Backup History     │
├────────────────────┤        ├────────────────────┤
│ Manual backups     │        │ Manual backups     │
│ only               │   →    │ + Scheduled        │
│                    │        │ backups            │
│ Must check file    │        │ All in one view    │
│ system for         │        │                    │
│ scheduled backups  │        │                    │
└────────────────────┘        └────────────────────┘
```

---

## Conclusion

These changes make scheduled backups more reliable and easier to manage:

1. ✅ **Automatic Configuration:** Task Scheduler settings applied automatically
2. ✅ **Unified History:** All backups visible in one place
3. ✅ **Immediate Verification:** Can instantly confirm backups are working
4. ✅ **Better Reliability:** Proper permissions and missed task handling
5. ✅ **No Extra Work:** Everything happens automatically

The user experience is now more professional, more reliable, and easier to use.
