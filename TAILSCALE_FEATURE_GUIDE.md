# Tailscale Remote Access Feature Guide

## Overview

This feature adds secure remote access to your Nextcloud instance using Tailscale VPN. It includes:

- **Top-right UI controls**: Theme toggle icon and dropdown menu button
- **Dropdown menu**: Extensible menu system for advanced features
- **Tailscale setup wizard**: Step-by-step guide for installing and configuring Tailscale
- **Automatic configuration**: Automatically adds Tailscale addresses to Nextcloud's trusted domains

## UI Changes

### Header Layout

The header now includes:
```
┌──────────────────────────────────────────────────────────┐
│         Nextcloud Restore & Backup Utility      ☀️  ☰   │
└──────────────────────────────────────────────────────────┘
```

- **Left**: Empty space (for balance)
- **Center**: Application title
- **Right**: Theme toggle icon (☀️/🌙) and dropdown menu button (☰)

### Theme Toggle

- **Location**: Top-right corner of header (standalone icon)
- **Icons**: 
  - 🌙 (moon) when in light theme → Click to switch to dark theme
  - ☀️ (sun) when in dark theme → Click to switch to light theme
- **Behavior**: Instant theme switching without page reload
- **Previous location**: Removed from landing page to clean up the interface

### Dropdown Menu

- **Location**: Top-right corner of header (next to theme toggle)
- **Icon**: ☰ (hamburger menu)
- **Contents**: 
  - "🌐 Remote Access (Tailscale)" - Currently implemented
  - Expandable for future advanced features
- **Design**: Modal popup positioned below the menu button

## Tailscale Setup Wizard

### Step 1: Initial Status Check

When you click "Remote Access (Tailscale)" in the dropdown menu, the wizard:

1. Checks if Tailscale is installed
2. Checks if Tailscale is running
3. Displays current status with clear visual indicators

**Status Display:**
- ✓ Installed / ✗ Not Installed
- ✓ Running / ✗ Not Running

### Step 2: Installation (if needed)

If Tailscale is not installed:

1. Click "📦 Install Tailscale"
2. A dialog opens with platform-specific instructions
3. Links to official Tailscale download pages
4. Click "Check Installation" to verify installation

**Supported Platforms:**
- **Windows**: Direct link to installer download
- **Linux**: Installation script guide
- **macOS**: Direct link to app download

### Step 3: Start Service (if needed)

If Tailscale is installed but not running:

1. Click "▶️ Start Tailscale"
2. The wizard attempts to start the service
3. May require authentication (browser login)
4. Returns to main wizard after starting

### Step 4: Configure Remote Access

Once Tailscale is running:

1. Click "⚙️ Configure Remote Access"
2. Wizard displays:
   - **Tailscale IP**: Your device's Tailscale IP address
   - **MagicDNS Name**: Your device's Tailscale hostname (if available)
   - **Custom Domain**: Optional field for custom domains

3. Enter any custom domains you want to use (optional)
4. Click "✓ Apply Configuration to Nextcloud"

### Step 5: Automatic Configuration

When you apply the configuration:

1. Wizard finds your running Nextcloud container
2. Reads current `config/config.php`
3. Adds new domains to `trusted_domains` array:
   - Tailscale IP address
   - MagicDNS hostname (if available)
   - Custom domain(s) (if provided)
4. Writes updated config back to container
5. Displays success message with all added domains

## How It Works

### Trusted Domains

Nextcloud requires all access URLs to be listed in the `trusted_domains` configuration. The wizard automatically adds:

```php
'trusted_domains' => array(
    0 => 'localhost',
    1 => '100.101.102.103',      // Tailscale IP
    2 => 'myserver.tailnet.ts.net', // MagicDNS name
    3 => 'mycloud.example.com',  // Custom domain
),
```

### Tailscale Network

Tailscale creates a secure, encrypted network between your devices:

- **No port forwarding required**: Works behind NAT/firewalls
- **Encrypted connections**: All traffic is encrypted
- **Zero-trust security**: Only your authorized devices can connect
- **Simple setup**: No complex VPN configuration

### Access Methods

After configuration, you can access Nextcloud using:

1. **Tailscale IP**: `http://100.101.102.103:8080`
2. **MagicDNS**: `http://myserver.tailnet.ts.net:8080`
3. **Custom domain**: `http://mycloud.example.com:8080`

(Replace port 8080 with your Nextcloud port)

## Benefits

### Security

- **Private network**: Only accessible to authorized devices
- **No public exposure**: Server not exposed to internet
- **Encrypted traffic**: All connections encrypted by default
- **Zero-trust model**: Device authentication required

### Ease of Use

- **Automatic setup**: Wizard handles all configuration
- **No manual editing**: No need to edit config.php manually
- **Status checks**: Clear indication of what's installed/running
- **Platform support**: Works on Windows, Linux, and macOS

### Flexibility

- **Multiple access methods**: IP, hostname, or custom domain
- **Custom domains**: Add your own domain names
- **Expandable**: Menu system ready for future features
- **Clean UI**: Minimal, intuitive interface

## Technical Details

### Tailscale Detection

The wizard uses these commands to check Tailscale:

```bash
# Check installation
which tailscale  # Linux/macOS
where tailscale  # Windows

# Check status
tailscale status

# Get network info
tailscale status --json
```

### Configuration Update

The wizard updates `config.php` by:

1. Reading current file from container
2. Parsing `trusted_domains` array with regex
3. Adding new domains (avoiding duplicates)
4. Writing updated config back to container

```bash
docker exec <container> cat /var/www/html/config/config.php
# ... parse and update ...
docker exec <container> sh -c "cat > /var/www/html/config/config.php << 'EOF'
<updated config>
EOF"
```

### Error Handling

The wizard handles:

- Missing Tailscale installation
- Service not running
- Authentication failures
- Container not found
- Configuration read/write errors
- Invalid domains
- Permission issues

## Future Enhancements

The dropdown menu system is designed to be expandable. Future features could include:

- **Firewall configuration**: Automatic port opening
- **SSL certificate setup**: Let's Encrypt integration
- **Backup scheduling**: Advanced scheduling options
- **Performance monitoring**: Resource usage tracking
- **Plugin management**: Nextcloud app installation
- **User management**: Nextcloud user administration
- **Security scanning**: Vulnerability checks

## Troubleshooting

### Tailscale Not Detected

If the wizard says Tailscale is not installed:

1. Verify installation: `tailscale version`
2. Check PATH environment variable
3. Restart terminal/application
4. Reinstall Tailscale if needed

### Service Won't Start

If Tailscale service won't start:

1. Check system logs: `journalctl -u tailscaled` (Linux)
2. Verify permissions: May need sudo/admin rights
3. Start manually: `sudo systemctl start tailscaled` (Linux)
4. Check Tailscale status page: https://status.tailscale.com

### Configuration Fails

If configuration update fails:

1. Verify Nextcloud container is running: `docker ps`
2. Check container name matches
3. Verify config.php exists in container
4. Check container permissions
5. Try manual edit if needed

### Can't Access Nextcloud

If you can't access Nextcloud via Tailscale:

1. Verify Tailscale is running on both devices
2. Check Tailscale IP: `tailscale ip`
3. Verify Nextcloud port (usually 8080)
4. Check trusted_domains in config.php
5. Restart Nextcloud container if needed

## Support

For more information:

- **Tailscale Documentation**: https://tailscale.com/kb
- **Nextcloud Documentation**: https://docs.nextcloud.com
- **Docker Documentation**: https://docs.docker.com

## Security Notes

### Best Practices

1. **Keep Tailscale updated**: Update regularly for security patches
2. **Use strong auth**: Enable two-factor authentication
3. **Limit device access**: Remove unused devices from Tailscale network
4. **Monitor access**: Check Tailscale admin console regularly
5. **Regular backups**: Continue backing up Nextcloud data

### Privacy

- Tailscale coordination server knows your device IPs but can't see your traffic
- All data is encrypted end-to-end
- No third-party can intercept your Nextcloud traffic
- Your data never leaves your devices except encrypted

### Compliance

Tailscale is suitable for:

- Personal use
- Small business use
- HIPAA-compliant deployments (Business plan)
- GDPR compliance
- SOC 2 Type II certified

## Visual Design

### Color Scheme

All UI elements follow the application's theme system:

**Light Theme:**
- Background: #f0f0f0
- Text: #000000
- Buttons: #e0e0e0
- Info boxes: #e3f2fd (light blue)
- Success: #7cb342 (green)
- Error: #d32f2f (red)

**Dark Theme:**
- Background: #1e1e1e
- Text: #e0e0e0
- Buttons: #2d2d2d
- Info boxes: #1a3a4a (dark blue)
- Success: #7cb342 (green)
- Error: #ef5350 (red)

### Accessibility

- **Clear visual hierarchy**: Titles, subtitles, and content clearly distinguished
- **Color contrast**: All text meets WCAG AA standards
- **Icon usage**: Icons paired with text for clarity
- **Button sizing**: Large, easy-to-click buttons
- **Status indicators**: Visual (✓/✗) and textual feedback
- **Error messages**: Clear, actionable error descriptions

## Implementation Notes

### Code Structure

The feature is implemented in `nextcloud_restore_and_backup-v9.py`:

- `show_dropdown_menu()`: Creates dropdown menu popup
- `show_tailscale_wizard()`: Main wizard entry point
- `_check_tailscale_installed()`: Installation check
- `_check_tailscale_running()`: Service status check
- `_install_tailscale()`: Installation guide dialog
- `_start_tailscale()`: Service start method
- `_show_tailscale_config()`: Configuration wizard
- `_get_tailscale_info()`: Retrieve network information
- `_apply_tailscale_config()`: Update Nextcloud config
- `_update_trusted_domains()`: Modify config.php

### Dependencies

- **Python 3**: Required for script execution
- **tkinter**: GUI framework (usually included with Python)
- **Docker**: Required for Nextcloud container access
- **Tailscale**: Optional, installed via wizard if needed

### Testing

Run the test script to verify implementation:

```bash
python3 test_tailscale_feature.py
```

This checks:
- UI element presence
- Method implementations
- Theme integration
- Tailscale feature completeness
