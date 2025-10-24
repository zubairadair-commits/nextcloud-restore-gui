# Windows Scheduled Task & Clickable URL Features

## Overview

This document describes the enhancements made to the Nextcloud Restore GUI's Tailscale integration, specifically:

1. **Enhanced Windows Scheduled Task Management** - Full support for creating, monitoring, enabling, disabling, and removing Windows Scheduled Tasks for automatic Tailscale Serve at startup
2. **Clickable Nextcloud URLs** - Interactive hyperlinks in the Tailscale wizard that open Nextcloud URLs in your default browser

## Feature 1: Enhanced Windows Scheduled Task Management

### What It Does

The application can now create a Windows Scheduled Task that automatically runs `tailscale serve --bg --https=443 http://localhost:{port}` at system startup. This ensures that your Nextcloud instance is always accessible via Tailscale after a reboot or user login.

### Key Improvements

#### 1. Task Status Monitoring

The app now displays comprehensive information about the scheduled task:

- **Exists**: Whether the task has been created
- **Enabled/Disabled**: Current state of the task
- **Configured Port**: The port being served by the task
- **Next Run Time**: When the task will next execute
- **Last Run Time**: When the task last executed

#### 2. Task Management UI

A dedicated status panel shows the current task configuration with three management options:

- **⏸ Disable Auto-Start**: Temporarily disable the task without removing it
- **▶️ Enable Auto-Start**: Re-enable a previously disabled task
- **🗑️ Remove Task**: Completely delete the scheduled task

#### 3. Confirmation Dialogs

- Disabling or removing a task requires user confirmation to prevent accidental changes
- Clear, informative messages explain what each action will do
- Success/error messages provide immediate feedback

### How to Use

#### Creating a Scheduled Task

1. Navigate to the Tailscale Configuration wizard from the main menu
2. The app will detect your Nextcloud port automatically
3. Check the "Enable automatic Tailscale serve at startup" checkbox
4. Click "✓ Apply Configuration to Nextcloud"
5. The task will be created and will run at every system login

#### Viewing Task Status

When a scheduled task exists, you'll see a "📅 Scheduled Task Status" panel showing:

```
Status: ✓ Enabled (or ✗ Disabled)
Configured Port: 8080
Next Run: At logon
```

#### Managing the Task

**To Disable (but not remove) the task:**
1. Click "⏸ Disable Auto-Start"
2. Confirm the action
3. The task remains but won't run automatically

**To Re-enable a disabled task:**
1. Click "▶️ Enable Auto-Start"
2. The task will resume running at system startup

**To Remove the task completely:**
1. Click "🗑️ Remove Task"
2. Confirm the deletion
3. The task is permanently removed

### Technical Details

#### Functions Added

**`check_scheduled_task_status()`**
- Queries the Windows Task Scheduler for task information
- Returns a dictionary with task status, configuration, and schedule details
- Works cross-platform (Windows, Linux, macOS)

**`enable_scheduled_task()`**
- Enables a previously disabled scheduled task
- Uses `schtasks /Change /ENABLE` on Windows

**`disable_scheduled_task()`**
- Disables a scheduled task without removing it
- Uses `schtasks /Change /DISABLE` on Windows

**UI Handler Methods:**
- `_disable_scheduled_task()` - UI handler for disabling
- `_enable_scheduled_task()` - UI handler for enabling
- `_remove_scheduled_task()` - UI handler for removal

#### Windows Implementation

The scheduled task is created using PowerShell with the following properties:

```powershell
$action = New-ScheduledTaskAction -Execute 'tailscale.exe' -Argument 'serve --bg --https=443 http://localhost:{port}'
$trigger = New-ScheduledTaskTrigger -AtLogon
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden
```

**Key Properties:**
- **Trigger**: At user logon
- **RunLevel**: Highest (administrator privileges)
- **Hidden**: Task runs in background without window
- **AllowStartIfOnBatteries**: Works on laptops
- **StartWhenAvailable**: Starts if missed during logon

#### Checking Task Status

The app uses `schtasks /Query /TN NextcloudTailscaleServe /FO LIST /V` to get detailed information including:
- Current status (Ready, Running, Disabled)
- Next run time
- Last run time
- Task configuration

## Feature 2: Clickable Nextcloud URLs

### What It Does

The Tailscale wizard now displays clickable hyperlinks for accessing your Nextcloud instance. Clicking a link opens the URL in your default web browser.

### Available URLs

The app displays multiple URLs depending on your configuration:

1. **Local URL**: `http://localhost:{port}` - Always available when Nextcloud is running
2. **Tailscale IP URL**: `https://{tailscale_ip}` - Available when Tailscale is configured and auto-serve is enabled
3. **Tailscale Hostname URL**: `https://{tailscale_hostname}` - Available when MagicDNS is enabled and auto-serve is configured

### Visual Feedback

- Links are displayed in **blue** with **underline** styling
- Cursor changes to **hand pointer** when hovering
- Link color changes to darker blue on hover
- Click feedback: Shows a message confirming the URL is opening

### How to Use

#### In the Tailscale Wizard (Main Page)

1. Go to "Remote Access Setup" from the main menu
2. If Tailscale is running, you'll see a "📡 Current Tailscale Network Info" section
3. Under "🌐 Access Nextcloud via:", clickable URLs are displayed
4. Click any URL to open it in your default browser

#### In the Tailscale Configuration Page

1. Go to "⚙️ Configure Remote Access"
2. The "📡 Your Tailscale Network Information" section shows available URLs
3. Click any URL to open Nextcloud in your browser

### Smart URL Display

The app intelligently shows URLs based on your setup:

- **Auto-serve not configured**: Shows hint text like "https://{ip} (enable auto-serve below to use)"
- **Auto-serve configured**: Shows clickable HTTPS links
- **Local access**: Always shows local HTTP link when Nextcloud port is detected

### Technical Details

#### Functions Added

**`_create_clickable_url(parent, display_text, url)`**
- Creates a clickable label widget for the Tailscale wizard
- Binds click event to open URL in browser
- Adds hover effects for visual feedback

**`_create_clickable_url_config(parent, display_text, url)`**
- Creates a clickable label widget for the configuration page
- Similar functionality to `_create_clickable_url()` but with config page styling

#### Implementation Details

**URL Format:**
- Local: `http://localhost:{port}`
- Tailscale IP: `https://{tailscale_ip}`
- Tailscale Hostname: `https://{tailscale_hostname}`

**Click Handler:**
```python
def open_url(event):
    try:
        webbrowser.open(url)
        messagebox.showinfo("Opening URL", f"Opening {url} in your default browser...")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open URL: {e}\n\nPlease manually navigate to:\n{url}")
```

**Hover Effects:**
```python
def on_enter(event):
    url_label.config(fg="#2980b9")  # Darker blue on hover

def on_leave(event):
    url_label.config(fg="#3daee9")  # Original blue
```

## Testing

A comprehensive test suite (`tests/test_scheduled_task_and_urls.py`) validates:

### Scheduled Task Management Tests

- ✓ Task status check function exists
- ✓ Status dictionary contains all required fields
- ✓ Enable/disable/remove functions implemented
- ✓ Windows schtasks commands used correctly
- ✓ UI handler methods implemented
- ✓ Confirmation dialogs present
- ✓ Page refresh after management actions
- ✓ Status panel displays all information
- ✓ Management buttons created with correct commands

### Clickable URL Tests

- ✓ Clickable URL helper methods exist
- ✓ Browser open functionality implemented
- ✓ Hand cursor and underline styling
- ✓ Blue link colors used
- ✓ Click and hover events bound
- ✓ Port detection integrated
- ✓ URL section displayed in both pages
- ✓ Local, IP, and hostname URLs shown
- ✓ Conditional display based on task status

Run tests with:
```bash
python tests/test_scheduled_task_and_urls.py
```

## Platform Support

### Windows
- ✅ Full scheduled task management support
- ✅ Uses PowerShell for task creation
- ✅ Uses `schtasks` for task management
- ✅ All features tested and working

### Linux
- ✅ Uses systemd services for auto-start
- ✅ Task status checking via `systemctl`
- ✅ Enable/disable via `systemctl enable/disable`

### macOS
- ✅ Uses LaunchAgents for auto-start
- ✅ Task status via plist file existence
- ✅ Enable/disable via `launchctl load/unload`

## Security Considerations

1. **Administrator Privileges**: Task creation requires admin rights on Windows
2. **Confirmation Dialogs**: All destructive actions require user confirmation
3. **Error Handling**: Comprehensive error messages for debugging
4. **Logging**: All task management actions are logged

## Troubleshooting

### Task Creation Fails

**Issue**: "Failed to create scheduled task: Access is denied"

**Solution**: Run the application as Administrator on Windows

---

**Issue**: Task appears disabled even though it was enabled

**Solution**: 
1. Open Task Scheduler (`taskschd.msc`)
2. Find "NextcloudTailscaleServe" under Task Scheduler Library
3. Right-click and select "Enable"

### URLs Not Clickable

**Issue**: URLs appear as plain text

**Solution**: Ensure Nextcloud container is running and port is detected

---

**Issue**: Tailscale URLs show "enable auto-serve" message

**Solution**: Enable automatic Tailscale serve in the configuration wizard

### Browser Doesn't Open

**Issue**: Clicking URL doesn't open browser

**Solution**: 
1. Check your default browser is set correctly
2. Try manually navigating to the URL
3. Check the application logs for errors

## Future Enhancements

Potential improvements for future versions:

1. **Task Run History**: Show recent task execution history
2. **Test Task**: Button to manually run the task immediately
3. **Multiple Ports**: Support serving multiple Nextcloud instances
4. **Schedule Options**: Allow custom schedules beyond "At Logon"
5. **URL Validation**: Test URLs before displaying as clickable
6. **Copy to Clipboard**: Button to copy URLs to clipboard

## References

- [Windows Task Scheduler Documentation](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [Tailscale Serve Documentation](https://tailscale.com/kb/1242/tailscale-serve/)
- [Python webbrowser module](https://docs.python.org/3/library/webbrowser.html)
- [tkinter Event Handling](https://docs.python.org/3/library/tkinter.html#bindings-and-events)
