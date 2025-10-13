# Nextcloud Remote Access Startup Automation Guide

This guide explains how to configure your system to automatically apply Tailscale trusted domains to Nextcloud on system startup.

## Overview

The startup automation ensures that:
- Tailscale IP address is always trusted by Nextcloud
- MagicDNS hostname is always trusted by Nextcloud
- Custom domains you've configured are always trusted
- Remote access works immediately after system boot

## Prerequisites

- Linux system with systemd (Ubuntu, Debian, Fedora, etc.)
- Docker installed and running
- Nextcloud running in Docker container
- Tailscale installed and configured
- Root/sudo access for installation

## Installation Steps

### 1. Copy the Startup Script

Copy the startup script to the system bin directory:

```bash
sudo cp nextcloud-remote-access-startup.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/nextcloud-remote-access-startup.sh
```

### 2. Install the Systemd Service

Copy the service file to systemd directory:

```bash
sudo cp nextcloud-remote-access.service /etc/systemd/system/
```

### 3. Enable the Service

Enable the service to run on startup:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nextcloud-remote-access.service
```

### 4. Start the Service (Optional)

You can start the service immediately without rebooting:

```bash
sudo systemctl start nextcloud-remote-access.service
```

### 5. Check Service Status

Verify the service is running correctly:

```bash
sudo systemctl status nextcloud-remote-access.service
```

## Adding Custom Domains

To add custom domains that should always be trusted on startup:

1. Create the configuration file:

```bash
sudo nano /etc/nextcloud-remote-access.conf
```

2. Add your custom domains (one per line):

```
mycloud.example.com
cloud.mydomain.org
nextcloud.local
```

3. Save the file and restart the service:

```bash
sudo systemctl restart nextcloud-remote-access.service
```

## Viewing Logs

Check the service logs to see what's happening:

```bash
# View service logs
sudo journalctl -u nextcloud-remote-access.service

# View detailed logs
sudo cat /var/log/nextcloud-remote-access.log
```

## Troubleshooting

### Service fails to start

1. Check if Docker is running:
```bash
sudo systemctl status docker
```

2. Check if Nextcloud container is running:
```bash
docker ps | grep nextcloud
```

3. Check service logs:
```bash
sudo journalctl -xe -u nextcloud-remote-access.service
```

### Domains not being added

1. Verify Tailscale is running:
```bash
tailscale status
```

2. Check if the script can find the Nextcloud container:
```bash
docker ps --format '{{.Names}}' | grep nextcloud
```

3. Manually run the script to see errors:
```bash
sudo /usr/local/bin/nextcloud-remote-access-startup.sh
```

### Permission errors

Ensure the script is executable:
```bash
sudo chmod +x /usr/local/bin/nextcloud-remote-access-startup.sh
```

## Uninstallation

To remove the startup automation:

```bash
# Stop and disable the service
sudo systemctl stop nextcloud-remote-access.service
sudo systemctl disable nextcloud-remote-access.service

# Remove files
sudo rm /etc/systemd/system/nextcloud-remote-access.service
sudo rm /usr/local/bin/nextcloud-remote-access-startup.sh
sudo rm /etc/nextcloud-remote-access.conf
sudo rm /var/log/nextcloud-remote-access.log

# Reload systemd
sudo systemctl daemon-reload
```

## How It Works

1. **Service Start**: The systemd service starts after Docker and Tailscale services are ready
2. **Wait Period**: Script waits 10 seconds for services to fully initialize
3. **Container Detection**: Automatically finds the Nextcloud container
4. **Tailscale Detection**: Retrieves your Tailscale IP and hostname
5. **Domain Addition**: Adds domains to Nextcloud's trusted_domains using the `occ` command
6. **Custom Domains**: Reads and applies any custom domains from the config file
7. **Logging**: All actions are logged for troubleshooting

## Security Considerations

- The script runs with root privileges (required for Docker access)
- Only domains you explicitly configure are added
- The script uses Nextcloud's official `occ` command for safe configuration updates
- All actions are logged for audit purposes

## Advanced Configuration

### Change Container Name

If your Nextcloud container has a different name, edit the script:

```bash
sudo nano /usr/local/bin/nextcloud-remote-access-startup.sh
```

Find the `get_nextcloud_container()` function and add your container name to the list.

### Adjust Timing

If services need more time to start, increase the sleep delay:

```bash
# Change this line in the script
sleep 10  # Increase to 20 or 30 if needed
```

## Support

For issues or questions:
- Check the logs first: `sudo journalctl -u nextcloud-remote-access.service`
- Review the GitHub repository issues
- Ensure all prerequisites are met
- Verify manual domain addition works through the GUI first

## Benefits

✓ **Automatic**: Domains are applied on every system boot  
✓ **Reliable**: Works even after system restarts or updates  
✓ **Flexible**: Supports custom domains via configuration file  
✓ **Safe**: Uses official Nextcloud commands  
✓ **Auditable**: All actions are logged  
✓ **Beginner-friendly**: Simple installation process  

---

*This automation ensures your remote access setup is persistent and always available.*
