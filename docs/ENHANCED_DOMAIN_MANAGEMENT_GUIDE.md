# Enhanced Domain Management Guide

## Overview

The Enhanced Domain Management system provides comprehensive tools for managing trusted domains in your Nextcloud instance. This guide covers all new features and how to use them effectively.

## Features

### 1. Visual Domain List with Status Icons

Each domain in the list displays a status icon indicating its current state:

- **✓ Active** (Green): Domain is reachable and working
- **⚠️ Unreachable** (Orange): Domain cannot be resolved (may need DNS configuration)
- **⏳ Pending** (Blue): Status check in progress
- **❌ Error** (Red): Error occurred while checking domain status

### 2. Domain Validation

The system validates all domains before adding them:

- **Format Validation**: Checks for valid domain formats
  - Standard domains: `example.com`, `subdomain.example.com`
  - IP addresses: `192.168.1.100`, `100.x.x.x` (Tailscale)
  - Localhost: `localhost`, `127.0.0.1`
  - Ports: `example.com:8080`

- **Real-time Feedback**: As you type, the system validates your input
  - ✓ Green checkmark for valid domains
  - ⚠️ Orange warning for valid but potentially problematic domains
  - ✗ Red error for invalid formats

- **Duplicate Detection**: Prevents adding domains that already exist

- **Empty Entry Prevention**: Won't allow adding empty domains

### 3. Wildcard Domain Support

The system supports wildcard domains with appropriate warnings:

- **Format**: `*.example.com`
- **Use Case**: Allows all subdomains of example.com
- **Warning**: Wildcard domains are shown with a warning to ensure you understand the security implications

### 4. Add New Domains Instantly

To add a new domain:

1. Type the domain in the "Add New Domain" field
2. Watch for real-time validation feedback
3. Click the **➕ Add** button
4. Confirm the addition
5. The page refreshes automatically to show the new domain

### 5. Remove Domains with Confirmation

To remove a domain:

1. Click the **✕** button next to the domain
2. Confirm the removal in the dialog
3. The page refreshes automatically

**Lockout Prevention**: If you try to remove the last domain, you'll receive a strong warning to prevent accidental lockout.

### 6. Undo Recent Changes

The system tracks all domain changes and allows you to undo them:

1. Click **↶ Undo Last Change**
2. Confirm the undo operation
3. The previous state is restored

**What's Tracked**:
- Adding domains
- Removing domains
- Restoring defaults
- All operations include timestamps and details

### 7. Restore Default Domains

Revert all trusted domains to their original values:

1. Click **↺ Restore Defaults**
2. Review the original domains in the confirmation dialog
3. Confirm to restore
4. All domains are replaced with the original configuration

**Note**: The original domains are captured when you first view the page.

### 8. Manual Status Refresh

Update domain reachability status:

1. Click **🔄 Refresh Status**
2. The cache is cleared
3. The page refreshes with updated status checks

**Cache**: Status checks are cached for 5 minutes to improve performance.

### 9. Interactive Help and Tooltips

Get information about domains and features:

- **Help Button (ℹ️)**: Click for comprehensive domain management help
- **Domain Tooltips**: Hover over any domain to see:
  - Domain name
  - Current status
  - Domain type (Tailscale IP, MagicDNS, Custom, Wildcard, Local)

### 10. Scrollable Domain List

For instances with many domains:
- List automatically becomes scrollable with more than 6 domains
- Maximum height of 300px
- Smooth scrolling with visible scrollbar

## Domain Types Explained

### Tailscale IP
- **Format**: `100.x.x.x`
- **Purpose**: Direct IP access via Tailscale VPN
- **Status**: Usually always active

### MagicDNS Name
- **Format**: `device-name.tailnet.ts.net`
- **Purpose**: Human-readable Tailscale address
- **Status**: Active when Tailscale is running

### Custom Domain
- **Format**: `mycloud.example.com`
- **Purpose**: Your own domain name
- **Status**: Requires DNS configuration

### Wildcard Domain
- **Format**: `*.example.com`
- **Purpose**: Matches all subdomains
- **Warning**: Be cautious with security implications

### Local
- **Format**: `localhost`, `127.0.0.1`
- **Purpose**: Local testing and development
- **Status**: Always active

## Audit and Logging

All domain changes are logged for troubleshooting and audit purposes:

### What's Logged
- **Action**: add, remove, restore_defaults
- **Timestamp**: ISO format timestamp
- **Domain**: The affected domain
- **Previous State**: Complete list of domains before the change

### Log Location
- **File**: `nextcloud_restore_gui.log`
- **Format**: Standard Python logging format
- **Level**: INFO for normal operations, ERROR for failures

### Example Log Entry
```
2025-10-13 15:23:45,123 - INFO - Domain change recorded: {'timestamp': '2025-10-13T15:23:45.123456', 'action': 'add', 'domain': 'mycloud.example.com', 'previous_domains': ['localhost', '100.x.x.x']}
```

## Security Features

### Lockout Prevention
- **Last Domain Warning**: Strong confirmation required to remove the last domain
- **Clear Messaging**: Explains consequences of removing all domains
- **Cancellation**: Easy to cancel at any point

### Change Tracking
- **Complete History**: Every change is recorded
- **Undo Capability**: Revert mistakes immediately
- **Restore Defaults**: Safety net to return to working configuration

### Validation
- **Format Checking**: Prevents invalid domains
- **Duplicate Prevention**: Avoids configuration errors
- **Warning System**: Alerts for potentially problematic configurations

## Best Practices

### 1. Test Before Production
- Add a test domain first
- Verify you can access Nextcloud through it
- Then remove old domains if needed

### 2. Keep Multiple Domains
- Maintain at least 2-3 working domains
- Include both IP and DNS-based domains
- Reduces risk of lockout

### 3. Document Your Domains
- Keep a list of your domains separately
- Note which devices/users use each domain
- Include purpose and configuration details

### 4. Regular Status Checks
- Use the Refresh Status button periodically
- Monitor for unreachable domains
- Update DNS if domains show as unreachable

### 5. Use Undo Feature
- If something breaks after a change, undo immediately
- Review what went wrong
- Try again with correct configuration

### 6. Backup Original Configuration
- The system saves original domains automatically
- You can always restore to working state
- Keep external backup of config.php as extra safety

## Troubleshooting

### Domain Shows as Unreachable
1. **Check DNS**: Verify domain resolves correctly
2. **Check Network**: Ensure you can ping/access the domain
3. **Wait and Refresh**: DNS changes take time to propagate
4. **Check Tailscale**: Ensure Tailscale is running if using Tailscale domains

### Cannot Add Domain
1. **Check Format**: Ensure domain format is valid
2. **Check Duplicates**: Domain might already exist
3. **Check Container**: Ensure Nextcloud container is running
4. **Check Permissions**: Verify Docker permissions

### Undo Not Available
1. **No Changes Made**: Undo only appears after changes
2. **History Cleared**: Restarting the app clears history
3. **Use Restore Defaults**: Alternative recovery method

### Locked Out of Nextcloud
If you accidentally remove all domains:

1. **Docker Exec Method**:
   ```bash
   docker exec -it nextcloud-app bash
   vi /var/www/html/config/config.php
   # Edit trusted_domains array to add your domain
   ```

2. **Restore from Backup**:
   - Restore config.php from your last backup
   - Restart the Nextcloud container

3. **Add Domain via OCC**:
   ```bash
   docker exec -u www-data nextcloud-app php occ config:system:set trusted_domains 0 --value="localhost"
   ```

## Advanced Features

### Wildcard Domains
Enable access from any subdomain:
```
*.example.com
```
Matches: `cloud.example.com`, `test.example.com`, etc.

**Security Warning**: Wildcard domains allow broader access. Use only if you control all subdomains.

### Port-Specific Domains
Specify custom ports:
```
example.com:8080
100.64.1.100:8443
```

### IPv6 Support
IPv6 addresses are supported:
```
[2001:db8::1]
[::1]  # IPv6 localhost
```

## Integration with Nextcloud

### Direct config.php Sync
The system reads from and writes directly to Nextcloud's config.php:
- **Location**: `/var/www/html/config/config.php` (in container)
- **Format**: PHP array
- **Validation**: Syntax checked before writing

### No Service Restart Required
Changes take effect immediately without restarting:
- Nextcloud reads config.php on each request
- No downtime during domain updates
- Instant reflection of changes

### Compatibility
Works with all Nextcloud versions that support trusted_domains configuration (all modern versions).

## Future Enhancements

Planned features for future releases:
- **Batch Operations**: Add/remove multiple domains at once
- **Import/Export**: Save/load domain configurations
- **Domain Testing**: Test access from each domain
- **Usage Statistics**: Track which domains are most used
- **Mobile API**: Integration with mobile companion app

## Getting Help

If you need assistance:

1. **Click Help Button (ℹ️)**: In-app help dialog
2. **Check Logs**: Review `nextcloud_restore_gui.log`
3. **Read Documentation**: This guide and other docs
4. **GitHub Issues**: Report bugs or request features

## Summary

The Enhanced Domain Management system provides:
- ✓ Visual status indicators
- ✓ Comprehensive validation
- ✓ Easy add/remove with confirmation
- ✓ Undo and restore capabilities
- ✓ Complete audit logging
- ✓ Lockout prevention
- ✓ Help and tooltips
- ✓ Scrollable list for many domains
- ✓ Real-time status checking
- ✓ Wildcard support with warnings

All features maintain the clean, centered UI design and work seamlessly with dark/light themes.
