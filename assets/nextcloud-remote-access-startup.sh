#!/bin/bash
#
# Nextcloud Remote Access Startup Script
# This script ensures Tailscale domains are added to Nextcloud trusted_domains on startup
#
# Installation:
#   1. Copy this script to /usr/local/bin/nextcloud-remote-access-startup.sh
#   2. Make it executable: sudo chmod +x /usr/local/bin/nextcloud-remote-access-startup.sh
#   3. Copy nextcloud-remote-access.service to /etc/systemd/system/
#   4. Enable the service: sudo systemctl enable nextcloud-remote-access.service
#   5. Start the service: sudo systemctl start nextcloud-remote-access.service
#

set -e

# Wait for services to be ready
sleep 10

# Configuration file to store domains
CONFIG_FILE="/etc/nextcloud-remote-access.conf"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/log/nextcloud-remote-access.log
}

# Function to get Nextcloud container name
get_nextcloud_container() {
    # Try common container names
    for name in nextcloud-aio-nextcloud nextcloud nextcloud_app; do
        if docker ps --format '{{.Names}}' | grep -q "^${name}$"; then
            echo "$name"
            return 0
        fi
    done
    
    # Try to find any container with nextcloud in the name
    local container=$(docker ps --format '{{.Names}}' | grep -i nextcloud | head -n 1)
    if [ -n "$container" ]; then
        echo "$container"
        return 0
    fi
    
    return 1
}

# Function to add domain to trusted_domains
add_trusted_domain() {
    local container=$1
    local domain=$2
    
    # Check if domain is already in trusted_domains
    if docker exec "$container" grep -q "'$domain'" /var/www/html/config/config.php 2>/dev/null; then
        log "Domain already trusted: $domain"
        return 0
    fi
    
    log "Adding domain to trusted_domains: $domain"
    
    # Use PHP occ command to add trusted domain (safer method)
    if docker exec -u www-data "$container" php occ config:system:set trusted_domains 999 --value="$domain" 2>/dev/null; then
        log "Successfully added domain using occ: $domain"
        return 0
    else
        log "Warning: Could not add domain using occ, domain may already exist or index may need adjustment"
        return 0
    fi
}

# Main execution
log "=== Nextcloud Remote Access Startup ==="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    log "Error: Docker is not running"
    exit 1
fi

# Get Nextcloud container
NEXTCLOUD_CONTAINER=$(get_nextcloud_container)
if [ -z "$NEXTCLOUD_CONTAINER" ]; then
    log "Error: No Nextcloud container found"
    exit 1
fi

log "Found Nextcloud container: $NEXTCLOUD_CONTAINER"

# Check if Tailscale is running
if ! command -v tailscale >/dev/null 2>&1; then
    log "Warning: Tailscale is not installed"
    exit 0
fi

if ! tailscale status >/dev/null 2>&1; then
    log "Warning: Tailscale is not running"
    exit 0
fi

log "Tailscale is running, retrieving network information..."

# Get Tailscale IP
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null | head -n 1)
if [ -n "$TAILSCALE_IP" ]; then
    log "Found Tailscale IP: $TAILSCALE_IP"
    add_trusted_domain "$NEXTCLOUD_CONTAINER" "$TAILSCALE_IP"
fi

# Get Tailscale hostname (MagicDNS)
TAILSCALE_HOSTNAME=$(tailscale status --json 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('Self', {}).get('DNSName', '').rstrip('.'))" 2>/dev/null || echo "")
if [ -n "$TAILSCALE_HOSTNAME" ]; then
    log "Found Tailscale hostname: $TAILSCALE_HOSTNAME"
    add_trusted_domain "$NEXTCLOUD_CONTAINER" "$TAILSCALE_HOSTNAME"
fi

# Load custom domains from config file if it exists
if [ -f "$CONFIG_FILE" ]; then
    log "Loading custom domains from $CONFIG_FILE"
    while IFS= read -r domain; do
        # Skip empty lines and comments
        [[ -z "$domain" || "$domain" =~ ^[[:space:]]*# ]] && continue
        log "Adding custom domain: $domain"
        add_trusted_domain "$NEXTCLOUD_CONTAINER" "$domain"
    done < "$CONFIG_FILE"
fi

log "=== Nextcloud Remote Access Startup Complete ==="
exit 0
