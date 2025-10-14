# Test Run Button - Quick Reference

## What Changed?

The **🧪 Test Run** button has been moved from the "Configure New Schedule" section to the **"Current Status" section**, where it appears alongside the **Disable Schedule** and **Delete Schedule** buttons.

---

## Where to Find It

### Location: Current Status Section

When you open the Schedule Backup page, look in the **Current Status** box at the top.

**Active Schedule:**
```
┌─────────────────────────────────────────────┐
│ Current Status                              │
│                                             │
│ ✓ Scheduled backup is active                │
│ Frequency: daily                            │
│ Time: 02:00                                 │
│                                             │
│ [🧪 Test Run] [Disable] [Delete]           │
│    ↑ HERE!                                  │
└─────────────────────────────────────────────┘
```

**No Schedule:**
```
┌─────────────────────────────────────────────┐
│ Current Status                              │
│                                             │
│ ✗ No scheduled backup configured            │
│                                             │
│ [🧪 Test Run] (disabled)                   │
│    ↑ HERE!                                  │
└─────────────────────────────────────────────┘
```

---

## How It Works

### When Schedule is Active (Enabled)

**Appearance:**
- 🔵 **Blue button** (#3498db)
- White text
- Clickable cursor on hover

**What it does:**
1. Immediately runs a backup using your **saved schedule configuration**
2. Shows inline progress: "⏳ Running test backup..."
3. Shows inline result: "✅ Success!" or "❌ Failed: [reason]"
4. **No pop-up windows** - all feedback appears on the same page

**Tooltip:**
> "Click to immediately run a backup using the current schedule configuration.  
> This will verify that your scheduled backup is working correctly."

### When No Schedule Exists (Disabled)

**Appearance:**
- ⚫ **Gray button** (#d3d3d3)
- Gray text (#808080)
- Not clickable

**Why it's disabled:**
You need to create a schedule first before you can test it.

**Tooltip:**
> "Test Run is disabled because no backup schedule is configured.  
> Please create a schedule first to enable this feature."

---

## Step-by-Step Usage

### Testing Your Existing Schedule

1. **Navigate to Schedule Page**
   - Click "📅 Schedule Backup" from main menu

2. **Find Test Run Button**
   - Look in the "Current Status" section at the top
   - It should be blue if you have an active schedule

3. **Click Test Run**
   - Click the blue "🧪 Test Run" button
   - Watch for inline message below

4. **View Progress**
   - You'll see: "⏳ Running test backup using schedule configuration... Please wait..."
   - Progress appears in blue text

5. **Check Results**
   - **Success** (green): "✅ Test Backup Successful! [details]"
   - **Error** (red): "❌ Test Backup Failed: [reason]"

6. **No Pop-ups!**
   - All messages appear inline on the same page
   - You can continue working without dismissing dialogs

### Creating a Schedule to Enable Test Run

If the Test Run button is gray (disabled):

1. Scroll down to "Configure New Schedule"
2. Fill in:
   - Backup Directory
   - Frequency (Daily/Weekly/Monthly)
   - Time
   - Encryption settings (optional)
3. Click "Create/Update Schedule"
4. The Test Run button will now be enabled (blue)

---

## Button Positioning

The Test Run button is always the **first (leftmost)** button in the Current Status section:

```
Position 1: 🧪 Test Run      ← Primary action
Position 2: Disable Schedule  ← Secondary action
Position 3: Delete Schedule   ← Destructive action
```

This positioning makes it easy to find and indicates it's the primary testing action.

---

## Inline Feedback Examples

### Progress Message (Blue)
```
⏳ Running test backup using schedule configuration... Please wait...
```

### Success Message (Green)
```
✅ Test Backup Successful!

Backup file: nextcloud_backup_test_20241014_152030.tar.gz
Size: 125.67 MB
Location: C:\Backups\Nextcloud

Your scheduled backup configuration is working correctly.
```

### Error Message (Red)
```
❌ Test Backup Failed:
Backup directory does not exist: C:\Backups\Nextcloud
Please verify the directory exists and is accessible.
```

---

## Frequently Asked Questions

### Q: Where did the Test Run button go?
**A:** It moved from the "Configure New Schedule" section to the "Current Status" section, where it's grouped with other schedule management buttons.

### Q: Why is the Test Run button gray?
**A:** It's disabled because no schedule is configured. Create a schedule first, and the button will become blue and clickable.

### Q: What configuration does Test Run use?
**A:** It uses your **saved schedule configuration** - the settings from your active schedule, not the form fields in the Configure section.

### Q: Will Test Run show a pop-up?
**A:** No! All feedback appears inline on the same page. No blocking dialogs.

### Q: Can I test my schedule immediately after creating it?
**A:** Yes! As soon as you create a schedule, the Test Run button becomes enabled (blue) and you can click it immediately.

### Q: What happens when I click Test Run?
**A:** It immediately runs a backup using your schedule configuration and shows you the results inline - success, error, or warnings.

### Q: Does Test Run affect my scheduled backups?
**A:** No, it only runs a one-time test backup. Your regular schedule remains active.

### Q: How do I know if the test was successful?
**A:** You'll see a green success message (✅) with details about the backup file, size, and location.

### Q: What if the test fails?
**A:** You'll see a red error message (❌) explaining what went wrong, so you can fix the issue before your scheduled backup runs.

---

## Benefits of the New Positioning

1. **✅ Better Context**: Button is with other schedule management actions
2. **✅ Clear Purpose**: Obviously tests the existing schedule, not a new configuration
3. **✅ State Management**: Disabled when no schedule exists (prevents confusion)
4. **✅ Visual Grouping**: Grouped with related buttons (Disable, Delete)
5. **✅ Primary Position**: Leftmost position indicates primary action
6. **✅ Helpful Tooltips**: Explain functionality and limitations
7. **✅ Inline Feedback**: Non-intrusive, professional UX

---

## Troubleshooting

### Test Run is Gray (Disabled)
**Solution:** Create a schedule first
1. Scroll to "Configure New Schedule"
2. Fill in all required fields
3. Click "Create/Update Schedule"
4. Test Run will become enabled

### Test Run Shows Error
**Common Issues:**
- Backup directory doesn't exist → Create the directory
- Permission denied → Check folder permissions
- Disk full → Free up space
- Invalid configuration → Update schedule settings

### No Feedback After Clicking Test Run
**Solution:** Wait a moment
- Test backup may take several seconds
- You'll see a blue progress message first
- Then a green success or red error message

---

## Summary

**Location:** Current Status section (top of page)  
**Position:** First button (leftmost)  
**States:** Blue (enabled) or Gray (disabled)  
**Action:** Runs immediate test backup using saved schedule config  
**Feedback:** Inline messages (no pop-ups)  
**Tooltip:** Context-aware help text  

**Quick Tip:** Hover over the button to see a tooltip explaining what it does!

---

## Related Features

- **View Recent Logs**: See detailed logs of backup operations
- **Verify Scheduled Backup**: Check if scheduled task is configured correctly
- **Last Run Status**: See when the last scheduled backup ran

All these features work together to help you manage and verify your scheduled backups.

---

## Need More Help?

- See `TEST_RUN_BUTTON_VISUAL_DEMO.md` for visual examples
- See `BEFORE_AFTER_TEST_RUN_BUTTON.md` for detailed comparison
- Run `python3 demo_test_run_button.py` for interactive demo (GUI environments)
