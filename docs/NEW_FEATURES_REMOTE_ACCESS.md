# New Features: Enhanced Remote Access Management

## What's New in This Update

We've significantly enhanced the Tailscale remote access features with two major improvements:

### 1. 🔧 Automatic Startup Management
**Manage Windows Scheduled Tasks directly from the app**

Your Nextcloud remote access can now start automatically with your computer! The app provides a complete interface for managing Windows Scheduled Tasks that run `tailscale serve` at system startup.

**Key Features:**
- ✅ **View Task Status** - See if auto-start is enabled, what port is configured, and when it will run
- ✅ **One-Click Enable/Disable** - Turn auto-start on or off without recreating the task
- ✅ **Safe Removal** - Delete the task completely if you no longer need it
- ✅ **Confirmation Dialogs** - Protects you from accidentally disabling or removing tasks
- ✅ **Real-Time Updates** - Status updates immediately after any changes

**How to Use:**
1. Go to **Remote Access Setup** → **⚙️ Configure Remote Access**
2. Look for the "📅 Scheduled Task Status" panel
3. Use the buttons to Enable, Disable, or Remove the task

### 2. 🔗 Clickable Nextcloud URLs
**One-click access to your Nextcloud from the app**

No more copying and pasting URLs! The app now displays your Nextcloud access URLs as clickable links that open directly in your browser.

**Available URLs:**
- 🏠 **Local Access**: `http://localhost:8080` - For accessing Nextcloud on this computer
- 🌐 **Tailscale IP**: `https://100.64.0.1` - For accessing from other devices via Tailscale
- 📡 **Tailscale Hostname**: `https://my-server.tailnet.ts.net` - For easy-to-remember access

**Visual Feedback:**
- Links are displayed in blue with underline
- Cursor changes to pointing finger when hovering
- Link color changes when you hover over it
- Confirmation message when opening the URL

**Where to Find:**
- **Tailscale Wizard Main Page** - "📡 Current Tailscale Network Info" section
- **Configuration Page** - "📡 Your Tailscale Network Information" section

## Who Benefits from These Features?

### For Beginners
- **No more manual setup** - Everything is managed through the friendly GUI
- **Visual status indicators** - Easy to see if remote access is working
- **One-click access** - No need to remember or type URLs
- **Safe confirmations** - Protects against accidental changes

### For Advanced Users
- **Full task control** - Enable/disable/remove without opening Task Scheduler
- **Quick status check** - See task configuration at a glance
- **Efficient workflow** - Test URLs without leaving the app
- **Cross-platform support** - Works on Windows, Linux, and macOS

## Real-World Use Cases

### Scenario 1: Setting Up Remote Access
**Before:**
1. Enable Tailscale serve in the app
2. Manually create a scheduled task in Windows Task Scheduler
3. Copy the Tailscale URL
4. Paste it in your browser to test

**After:**
1. Enable Tailscale serve in the app (auto-creates scheduled task)
2. Click the blue URL link to test immediately
3. Done! ✨

### Scenario 2: Temporarily Disabling Remote Access
**Before:**
1. Open Task Scheduler
2. Find the Nextcloud task
3. Disable it
4. Remember to re-enable later

**After:**
1. Click "⏸ Disable Auto-Start" in the app
2. Confirm the action
3. Done! Re-enable anytime with one click

### Scenario 3: Accessing Nextcloud from Another Device
**Before:**
1. Check Tailscale IP in terminal/command line
2. Manually construct URL: `https://{ip}`
3. Type or paste URL in browser on other device

**After:**
1. Open the app
2. See your Tailscale URLs displayed clearly
3. Note the URL or use it as a reference
4. Access from any Tailscale-connected device

## Technical Details

### Scheduled Task Configuration
When you enable auto-start, the app creates a Windows Scheduled Task with:
- **Name**: NextcloudTailscaleServe
- **Trigger**: At user logon
- **Action**: Run `tailscale serve --bg --https=443 http://localhost:{port}`
- **Privileges**: Runs with highest available privileges
- **Hidden**: Runs in background without visible window
- **Battery**: Works even on battery power (laptops)

### URL Security
- **Local URLs** use HTTP (localhost is secure within your computer)
- **Tailscale URLs** use HTTPS (encrypted over your Tailscale VPN)
- **No public exposure** - Tailscale URLs only work within your private Tailscale network

### Platform Support
| Platform | Scheduled Task | URL Display |
|----------|----------------|-------------|
| Windows  | ✅ Full support | ✅ Yes      |
| Linux    | ✅ Systemd service | ✅ Yes   |
| macOS    | ✅ LaunchAgent | ✅ Yes      |

## Screenshots

### Scheduled Task Status Panel
```
┌─────────────────────────────────────────────────────────────────┐
│  📅 Scheduled Task Status                                       │
│                                                                   │
│  Status: ✓ Enabled                                              │
│  Configured Port: 8080                                           │
│  Next Run: At logon                                              │
│                                                                   │
│  [⏸ Disable Auto-Start] [🗑️ Remove Task]                       │
└─────────────────────────────────────────────────────────────────┘
```

### Clickable URLs
```
┌─────────────────────────────────────────────────────────────────┐
│  🌐 Access Nextcloud via:                                       │
│                                                                   │
│  Local: http://localhost:8080            [← Clickable!]        │
│  Tailscale IP: https://100.64.0.1        [← Clickable!]        │
│  Tailscale Hostname: https://my-server...  [← Clickable!]      │
└─────────────────────────────────────────────────────────────────┘
```

## Frequently Asked Questions

### Q: Will the scheduled task run even if I'm not logged in?
**A:** The task is set to run at user logon, so it starts when you log in to Windows. It won't run if you're not logged in (this is by design for security).

### Q: What happens if I disable the task?
**A:** The task remains configured but won't run automatically. You can re-enable it anytime with one click. Your Nextcloud will still work locally.

### Q: Why aren't Tailscale URLs clickable?
**A:** Tailscale URLs only become clickable after you enable auto-start (the scheduled task). This is because `tailscale serve` must be running for the HTTPS URLs to work.

### Q: Can I have different ports for local and Tailscale access?
**A:** The same port is used for both. Tailscale serve proxies your local Nextcloud port (e.g., 8080) to HTTPS on port 443.

### Q: What if I need to change the port?
**A:** You can:
1. Remove the existing task
2. Change your Nextcloud container's port
3. Create a new scheduled task with the new port

### Q: Is it safe to remove the task?
**A:** Yes! Removing the task only disables auto-start. Your Nextcloud will continue to work normally, you'll just need to manually run `tailscale serve` if you want remote access.

## Migration Notes

If you previously set up Tailscale serve manually:

### For Manual Task Scheduler Users
The app can now manage your task! However, if you created a task with a different name, the app won't see it. We recommend:
1. Remove your manually-created task
2. Let the app create a new one called "NextcloudTailscaleServe"
3. Use the app to manage it from now on

### For Command-Line Users
If you've been running `tailscale serve` manually, the scheduled task automates this for you. The command is exactly the same, just automated at logon.

## Troubleshooting

### Issue: "Access Denied" when creating task
**Solution:** Run the app as Administrator on Windows. Right-click the app and select "Run as administrator".

### Issue: Task shows as disabled even though I enabled it
**Solution:** 
1. Check the status panel - it should update automatically
2. If not, close and reopen the Remote Access wizard
3. The status should refresh

### Issue: Clicking URL does nothing
**Solution:**
1. Ensure Nextcloud is running (`docker ps` to check)
2. Verify your default browser is set correctly
3. Try copying the URL and pasting it manually to test

### Issue: Tailscale URLs show "(enable auto-serve below)"
**Solution:** This is expected! Enable the "Enable automatic Tailscale serve at startup" checkbox and apply the configuration. The URLs will then become clickable.

## Feedback and Support

We'd love to hear about your experience with these new features:

- 💬 **Questions?** Open an issue on GitHub
- 🐛 **Found a bug?** Please report it with details
- 💡 **Feature idea?** Let us know what you'd like to see
- ⭐ **Like it?** Give us a star on GitHub!

## Learn More

For detailed technical documentation, see:
- [Complete Feature Documentation](SCHEDULED_TASK_AND_CLICKABLE_URLS.md)
- [UI Changes Guide](UI_CHANGES_SCHEDULED_TASK_URLS.md)
- [Tailscale Serve Documentation](https://tailscale.com/kb/1242/tailscale-serve/)

---

**Thank you for using Nextcloud Restore GUI!** These features were designed to make remote access setup as simple and intuitive as possible. Enjoy the improved workflow! 🎉
