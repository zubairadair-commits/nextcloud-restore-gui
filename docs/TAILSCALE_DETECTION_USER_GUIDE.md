# Tailscale Detection - User Guide

## What Changed?

The Nextcloud Restore GUI now **automatically detects** Tailscale installation on Windows, no matter how you installed it!

## Why This Matters

**Before:**
- App only found Tailscale if it was in your system PATH
- Some installation methods didn't add Tailscale to PATH
- Users saw "Not Installed" even when Tailscale was installed
- Had to manually troubleshoot

**After:**
- App checks multiple locations automatically
- Works with all installation methods
- Accurate installation status
- Just works! ✓

## How It Works

The app now intelligently searches for Tailscale in three places:

### 1. System PATH
First, it checks if `tailscale.exe` is in your system PATH (the quick check).

### 2. Common Installation Folders
If not found in PATH, it checks these standard locations:
- `C:\Program Files\Tailscale`
- `C:\Program Files (x86)\Tailscale`
- Your user's `AppData\Local\Tailscale` folder

### 3. Windows Registry
If still not found, it checks the Windows registry for Tailscale's installation path.

## What You'll See

### When Tailscale IS Installed

In the Remote Access Setup page, you'll see:

```
🌐 Remote Access Setup

Tailscale Installation: ✓ Installed
Tailscale Status: ✓ Running  (or ✗ Not Running)

[⚙️ Configure Remote Access]  ← Button to set up access
```

### When Tailscale is NOT Installed

```
🌐 Remote Access Setup

Tailscale Installation: ✗ Not Installed

[📦 Install Tailscale]  ← Button to download installer
```

## Supported Installation Methods

✓ **MSI Installer** (official download)
✓ **Microsoft Store** version
✓ **Portable/ZIP** installation
✓ **Custom directory** installation
✓ **Chocolatey** package manager
✓ **Scoop** package manager
✓ **WinGet** package manager

All installation methods are now detected correctly!

## Troubleshooting

### Q: I installed Tailscale but the app says "Not Installed"

**A:** Try these steps:
1. Close and reopen the Nextcloud Restore GUI app
2. Verify Tailscale is actually installed (look for it in Start Menu)
3. Try clicking "Refresh" if available
4. Check if `tailscale.exe` exists in:
   - `C:\Program Files\Tailscale`
   - `C:\Program Files (x86)\Tailscale`

### Q: The app detects Tailscale but says "Not Running"

**A:** This is normal! It means:
- ✓ Tailscale **is** installed correctly
- ✗ Tailscale service is not currently running

**To fix:** Click the "▶️ Start Tailscale" button or start it from your system tray.

### Q: I moved Tailscale to a custom folder

**A:** The app will try to find it! If you installed Tailscale:
1. Make sure it's properly installed (not just extracted files)
2. The registry should have the installation path
3. Restart the Nextcloud Restore GUI app

## For Advanced Users

### Detection Order

The app checks locations in this order:
1. System PATH (fastest)
2. Standard directories (most common)
3. Windows Registry (most reliable)

### What Gets Detected

The app looks specifically for `tailscale.exe` (the CLI tool), not the Tailscale system tray app or service.

### Registry Keys Checked

- `HKEY_LOCAL_MACHINE\SOFTWARE\Tailscale IPN`
- `HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Tailscale IPN` (32-bit on 64-bit)
- `HKEY_CURRENT_USER\SOFTWARE\Tailscale IPN`

## Tips for Best Results

1. **Use Official Installer**: The MSI installer from tailscale.com always works perfectly
2. **Restart After Installing**: Always restart the Nextcloud app after installing Tailscale
3. **Don't Move Files**: If you must move Tailscale, reinstall it properly instead
4. **Check System Tray**: The Tailscale icon in your system tray confirms it's installed

## Need Help?

If you're still having issues:

1. Check the app's log file:
   - Location: `Documents\NextcloudLogs\nextcloud_restore_gui.log`
   - Look for "Tailscale" entries to see what the app detected

2. Verify Tailscale installation:
   - Open Command Prompt
   - Type: `where tailscale`
   - If found, you'll see the path

3. Check Windows Settings:
   - Go to Settings → Apps → Apps & features
   - Search for "Tailscale"
   - Verify it's listed

## Related Features

Once Tailscale is detected, you can:
- ✓ Configure remote access to your Nextcloud
- ✓ Add Tailscale domains to trusted domains
- ✓ Use Tailscale IP or MagicDNS hostname
- ✓ Access Nextcloud securely from anywhere

## Summary

The enhanced Tailscale detection means you can focus on using your Nextcloud instead of troubleshooting installation detection. The app now works with any Tailscale installation method and provides accurate status information.

**Just install Tailscale however you prefer, and the app will find it!** ✓
