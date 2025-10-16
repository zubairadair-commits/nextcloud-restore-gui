# Quick Start: Enhanced Domain Management

This guide helps you get started with the new Enhanced Domain Management features quickly.

## Getting Started

### Accessing Domain Management

1. Launch the Nextcloud Restore & Backup Utility
2. Click **"Configure Tailscale Remote Access"** or **"⚙️ Tailscale Network"** from the landing page
3. Scroll down to the **"Current Trusted Domains"** section

You'll see all your configured domains with status icons.

## Common Tasks

### Adding a New Domain

**Quick Steps:**
1. Find the "Add New Domain:" field
2. Type your domain (e.g., `mycloud.example.com`)
3. Watch for the validation checkmark (✓) or error (✗)
4. Click **➕ Add**
5. Confirm the addition
6. Done! Page refreshes automatically

**Example:**
```
Add New Domain: [mycloud.example.com] [➕ Add]
✓ Valid domain format
```

### Removing a Domain

**Quick Steps:**
1. Find the domain you want to remove
2. Click the **✕** button next to it
3. Confirm in the dialog
4. Done! Page refreshes automatically

**Warning:** Be careful not to remove all domains!

### Undo a Mistake

**Quick Steps:**
1. Click **↶ Undo Last Change** button
2. Confirm the undo
3. Done! Previous state restored

### Restore Original Configuration

**Quick Steps:**
1. Click **↺ Restore Defaults** button
2. Review the original domains
3. Confirm restoration
4. Done! Back to original setup

## Understanding Status Icons

- **✓ Green**: Domain is working - no action needed
- **⚠️ Orange**: Domain unreachable - check DNS/network
- **⏳ Blue**: Status check in progress - wait a moment
- **❌ Red**: Error checking - may need attention

## Validation Guide

### What's Accepted ✓

- **Standard domains**: `example.com`, `subdomain.example.com`
- **IP addresses**: `192.168.1.100`, `100.64.1.100`
- **Localhost**: `localhost`, `127.0.0.1`
- **With ports**: `example.com:8080`
- **Wildcards**: `*.example.com` (with warning)

### What's Rejected ✗

- Empty or whitespace only
- Spaces in domain names
- Invalid characters (!, @, #, etc.)
- Double dots (..)
- Starting/ending with hyphen
- Port numbers outside 1-65535

## Tips & Tricks

### Hover for Information
Hover over any domain to see:
- Full domain name
- Current status
- Domain type (Tailscale IP, MagicDNS, Custom, etc.)

### Get Help Anytime
Click the **ℹ️** button next to "Current Trusted Domains" for comprehensive help.

### Refresh Status
If a domain shows as unreachable but you know it works:
1. Click **🔄 Refresh Status**
2. Wait for page refresh
3. Status will update

### Keep Multiple Domains
**Best Practice**: Always keep at least 2-3 working domains to avoid lockout.

## Troubleshooting

### "Domain already exists"
The domain is already in the list. Check existing domains or refresh the page.

### "Invalid domain format"
Check your domain syntax:
- No spaces
- Valid characters only
- Proper format (example.com)

### "No running Nextcloud container"
Ensure your Nextcloud container is running:
```bash
docker ps | grep nextcloud
```

### Domain shows as unreachable
1. Check DNS: `nslookup yourdomain.com`
2. Wait for DNS propagation (up to 48 hours)
3. Verify network connectivity
4. Click Refresh Status button

## Safety Features

### Lockout Prevention
Removing the last domain triggers a strong warning. The system won't let you accidentally lock yourself out without confirmation.

### Undo Capability
All changes are tracked. Click Undo to revert mistakes immediately.

### Restore Defaults
Keep your original configuration safe. One click to restore if something goes wrong.

### Change Logging
All operations are logged to `nextcloud_restore_gui.log` for troubleshooting.

## Advanced Features

### Wildcard Domains
Add `*.example.com` to allow all subdomains. You'll see a warning - acknowledge it if you understand the security implications.

### Domain with Port
Specify a custom port: `example.com:8443` for non-standard configurations.

### Status Caching
Status checks are cached for 5 minutes to improve performance. Use Refresh Status to clear cache.

## Need More Help?

- **In-App Help**: Click the ℹ️ button
- **Full Guide**: See ENHANCED_DOMAIN_MANAGEMENT_GUIDE.md
- **Logs**: Check nextcloud_restore_gui.log
- **Demo**: Run demo_domain_validation.py to test validation

## Summary

**To add a domain:**
Type → Validate → Add → Confirm → Done

**To remove a domain:**
Click ✕ → Confirm → Done

**Made a mistake:**
Click Undo → Confirm → Done

**Need to recover:**
Click Restore Defaults → Confirm → Done

All operations are safe, reversible, and logged!
