# Automated Restore Process Guide

## Overview

The Nextcloud Restore & Backup Utility now provides a **fully automated restore process** that requires minimal user input and handles all technical steps automatically.

## What's Automated

### 1. Backup Extraction
- **Automatic decryption** of GPG-encrypted backups using provided password
- **Fast extraction** of tar.gz archives to temporary directory
- Progress monitoring during extraction

### 2. Container Management
- **Automatic database container startup** with correct credentials
- **Automatic Nextcloud container startup** linked to database
- **Container linking** for proper Docker networking (--link flag)
- Support for using existing containers or creating new ones

### 3. File Restoration
- **Automatic copying** of config folder to `/var/www/html/config`
- **Automatic copying** of data folder to `/var/www/html/data`
- **Automatic copying** of apps and custom_apps folders
- Proper handling of folder structure (uses `docker cp` with `/./` syntax)
- Removal of existing folders before copying to prevent nesting

### 4. Database Import
- **Automatic database import** from `nextcloud-db.sql` file
- Uses credentials provided by user (must match original setup)
- **Validation** that tables were imported successfully (checks for `oc_` prefix)
- Clear error messages if import fails

### 5. Configuration Update
- **Automatic update** of `config.php` with correct database credentials
- Sets database host to container name for proper networking
- Updates database name, user, and password
- Maintains database type (PostgreSQL)

### 6. Permission Setting
- **Automatic execution** of `chown -R www-data:www-data` on config and data folders
- Ensures Nextcloud can read/write all files
- Handles errors gracefully with warnings

### 7. Validation
- **Validates** that `config.php` exists after restore
- **Validates** that data folder exists after restore
- **Validates** that database tables were imported
- Clear error messages if validation fails

### 8. Container Restart
- **Automatic restart** of Nextcloud container after all changes
- 3-second wait for container to fully start
- Ensures all changes take effect

## User Input Required

### Step 1: Backup File Selection
- Select the backup archive (.tar.gz or .tar.gz.gpg)
- Enter decryption password if backup is encrypted

### Step 2: Database Credentials
**Important:** These must match your ORIGINAL database credentials from when the backup was created.

- Database Name (default: nextcloud)
- Database User (default: nextcloud)
- Database Password (default: example)

These credentials are stored in your backup and must match exactly.

### Step 3: Container Configuration
- Container Name (default: nextcloud-app)
- Container Port (default: 9000)
- Option to use existing container if found

## What Happens During Restore

The restore process follows these steps automatically:

1. ✅ **Extract backup** - Decrypt (if needed) and extract archive
2. ✅ **Start database container** - PostgreSQL with your credentials
3. ✅ **Start Nextcloud container** - Linked to database for networking
4. ✅ **Copy config folder** - To `/var/www/html/config`
5. ✅ **Copy data folder** - To `/var/www/html/data`
6. ✅ **Copy apps folders** - apps and custom_apps
7. ✅ **Import database** - From nextcloud-db.sql
8. ✅ **Validate database** - Check that tables exist
9. ✅ **Update config.php** - Set correct database credentials
10. ✅ **Validate files** - Check config.php and data folder exist
11. ✅ **Set permissions** - chown -R www-data:www-data
12. ✅ **Restart container** - Apply all changes
13. ✅ **Complete** - Nextcloud is ready to use!

## Docker Environment Requirements

### Container Networking
- Containers are automatically linked using Docker's `--link` flag
- Database container name becomes the hostname for Nextcloud
- No manual network configuration needed

### Volumes
- Files are copied directly into containers using `docker cp`
- No need to manually mount volumes
- All paths are automatically determined

### Images Used
- **Nextcloud**: `nextcloud:latest`
- **Database**: `postgres:latest`

## Error Handling

### Clear Error Messages
Every error includes:
- What failed
- Why it failed
- What you need to do to fix it

### Validation Failures
If validation fails, restore stops immediately with clear error:
- "Error: config.php not found after restore"
- "Error: data folder not found after restore"
- "Database restore failed: [specific error]"

### Warnings vs Errors
- **Errors** stop the restore process
- **Warnings** allow restore to continue but notify of issues
  - Permission setting failures
  - Container restart failures
  - Config update failures

## Troubleshooting

### Database Import Fails
- Verify you entered the ORIGINAL database credentials
- Check that credentials match what's in your backup's config.php
- Ensure PostgreSQL container is running: `docker ps | grep postgres`

### Files Not Copied Correctly
- Check container is running: `docker ps | grep nextcloud`
- Verify backup archive contains config and data folders
- Check Docker logs: `docker logs nextcloud-app`

### Container Won't Start
- Check if port is already in use: `docker ps | grep [port]`
- Verify Docker is running: `docker ps`
- Check Docker logs for errors

### Permission Issues
- Container may need manual permission fix: 
  ```bash
  docker exec nextcloud-app chown -R www-data:www-data /var/www/html/config /var/www/html/data
  ```

## Benefits of Full Automation

### For First-Time Users
- No need to understand Docker commands
- No manual file copying
- No manual database import
- No manual configuration editing
- Clear guidance at every step

### For Experienced Users
- Saves time on manual steps
- Reduces errors from manual operations
- Consistent restore process every time
- Easy to verify what was done (check logs)

### Reliability
- Every step is validated
- Errors are caught early
- Clear feedback throughout
- Automatic rollback on critical failures

## Docker Commands Used Internally

For reference, here are the Docker commands the utility runs automatically:

```bash
# Start database container
docker run -d --name nextcloud-db \
  -e POSTGRES_DB=nextcloud \
  -e POSTGRES_USER=nextcloud \
  -e POSTGRES_PASSWORD=[your password] \
  -p 5432:5432 postgres

# Start Nextcloud container (linked to database)
docker run -d --name nextcloud-app \
  --link nextcloud-db:db \
  -p 9000:80 nextcloud

# Copy files into container
docker exec nextcloud-app rm -rf /var/www/html/config
docker cp backup/config/. nextcloud-app:/var/www/html/config/

# Import database
docker exec -i nextcloud-db bash -c "PGPASSWORD=[password] psql -U [user] -d [dbname]" < nextcloud-db.sql

# Update config.php
docker exec nextcloud-app bash -c "php /tmp/update_config.php"

# Set permissions
docker exec nextcloud-app chown -R www-data:www-data /var/www/html/config /var/www/html/data

# Restart container
docker restart nextcloud-app
```

You don't need to run these yourself - the utility handles everything!

## Next Steps After Restore

1. Access Nextcloud at `http://localhost:[port]` (default: http://localhost:9000)
2. Log in with your admin credentials
3. Verify your data is present
4. Check that apps are working
5. Review settings and configurations

## Support

If you encounter issues:
1. Check the error message in the utility
2. Review Docker logs: `docker logs nextcloud-app`
3. Verify containers are running: `docker ps`
4. Check this guide for troubleshooting steps
5. Report issues with full error messages for help
