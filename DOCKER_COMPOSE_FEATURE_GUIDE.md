# Docker Compose Detection and Generation Feature

## Overview

This feature enhances the Nextcloud restore workflow by automatically detecting Docker Compose usage and offering to generate a `docker-compose.yml` file based on your backup's `config.php` settings. This makes restores safer, more portable, and easier to reproduce.

## What's New?

### 🔍 Automatic Detection

After extracting and parsing your backup's `config.php`, the system now:

1. **Detects if Docker Compose was used** by checking for:
   - Existing `docker-compose.yml` files in the current directory
   - Docker Compose labels on running containers

2. **Parses complete config.php settings** including:
   - Database type (SQLite, MySQL/MariaDB, PostgreSQL)
   - Database credentials (name, user, host, port)
   - Data directory path
   - Trusted domains

3. **Shows an interactive dialog** with:
   - Detected environment configuration
   - Docker Compose status
   - Host folder requirements
   - Options to generate or update docker-compose.yml

### 🎯 Benefits

✅ **Safer Restores**
- Volume mappings match your original configuration
- Database credentials are automatically correct
- Port mappings are properly configured

✅ **Portable Deployments**
- Easy to migrate to new servers
- Reproducible environment setup
- Well-documented configuration

✅ **Error Prevention**
- Warnings if existing docker-compose.yml doesn't match config.php
- Folder validation before container start
- Clear guidance on required setup steps

## How It Works

### 1. During Backup Selection (Page 1 → Page 2)

When you navigate from Page 1 to Page 2, the system:

```
1. Extracts config.php from backup (lightweight operation)
2. Detects database type (SQLite/MySQL/PostgreSQL)
3. Parses full configuration settings
4. Checks for Docker Compose usage
5. Shows Docker Compose suggestion dialog
```

### 2. Docker Compose Suggestion Dialog

The dialog provides:

**Environment Configuration Section:**
- 📊 Database type and credentials
- 📁 Data directory path
- 🌐 Trusted domains

**Docker Compose Status Section:**
- ✓ If detected: Warnings about potential mismatches
- ℹ️ If not detected: Offers to generate new file

**Host Folder Requirements Section:**
- Lists required folders (./nextcloud-data, ./db-data)
- Provides folder creation utility

**Action Buttons:**
- **Generate docker-compose.yml**: Creates a new compose file
- **Check/Create Folders**: Validates and creates required directories
- **Continue**: Proceeds with restore

### 3. Generated docker-compose.yml

The generated file includes:

```yaml
# Docker Compose configuration for Nextcloud
# Generated based on config.php settings from backup
#
# Detected configuration:
#   - Database type: pgsql
#   - Database name: nextcloud
#   - Data directory: /var/www/html/data
#   - Trusted domains: localhost, nextcloud.example.com

version: '3.8'

services:
  db:
    image: postgres:15
    container_name: nextcloud-db
    restart: unless-stopped
    volumes:
      - ./db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=your_password
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
    ports:
      - "5432:5432"

  nextcloud:
    image: nextcloud
    container_name: nextcloud-app
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - ./nextcloud-data:/var/www/html
    environment:
      - POSTGRES_PASSWORD=your_password
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
      - POSTGRES_HOST=db
    depends_on:
      - db
```

## Configuration Examples

### PostgreSQL Example

```yaml
services:
  db:
    image: postgres:15
    volumes:
      - ./db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
```

### MySQL/MariaDB Example

```yaml
services:
  db:
    image: mariadb:10.11
    command: --transaction-isolation=READ-COMMITTED --log-bin=binlog --binlog-format=ROW
    volumes:
      - ./db-data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_PASSWORD=password
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
```

### SQLite Example

```yaml
services:
  nextcloud:
    image: nextcloud
    volumes:
      - ./nextcloud-data:/var/www/html
    environment:
      - SQLITE_DATABASE=nextcloud
```

## Using the Feature

### Step-by-Step Workflow

1. **Select Backup** (Page 1)
   - Choose your backup file (.tar.gz or .tar.gz.gpg)
   - Enter decryption password if encrypted

2. **Click "Next"**
   - System extracts config.php
   - Detects database type and configuration
   - Shows Docker Compose suggestion dialog

3. **Review Detection Results**
   - Check detected database type
   - Review data directory and trusted domains
   - Note any warnings about existing docker-compose.yml

4. **Choose Action:**

   **Option A: Generate New docker-compose.yml**
   - Click "Generate docker-compose.yml"
   - Choose save location
   - File is created with your configuration

   **Option B: Create Required Folders**
   - Click "Check/Create Folders"
   - System creates ./nextcloud-data and ./db-data
   - Shows confirmation of created/existing folders

   **Option C: Continue Without Changes**
   - Click "Continue"
   - Proceed with restore using existing setup

5. **Complete Restore**
   - Fill in remaining configuration (Pages 2-3)
   - Start restore process

### Using Generated docker-compose.yml

After generating the file:

```bash
# Review the generated file
cat docker-compose.yml

# Create required folders (if not done via UI)
mkdir -p nextcloud-data db-data

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## Warnings and Validation

### Config.php vs Docker Compose Mismatch

The system warns you if:

❌ **Volume mappings don't match**
- config.php specifies `/mnt/data` but compose uses `./nextcloud-data`

❌ **Database credentials differ**
- config.php has different user/password than compose file

❌ **Port conflicts exist**
- Existing compose file uses different ports

### Host Folder Validation

Before container start, ensure:

✅ **./nextcloud-data exists**
- Will contain Nextcloud files (config, apps, data)
- Should have proper permissions

✅ **./db-data exists** (for MySQL/PostgreSQL)
- Will contain database files
- Should have proper permissions

## Migration Scenarios

### Scenario 1: Migrate to New Server

1. Copy backup to new server
2. Run restore wizard
3. Generate docker-compose.yml from backup
4. Review and adjust ports if needed
5. Run `docker-compose up -d`
6. Complete restore process

### Scenario 2: Disaster Recovery

1. Install Docker on recovery system
2. Run restore wizard with backup
3. Generate docker-compose.yml automatically
4. System creates correct environment
5. Restore completes with matching configuration

### Scenario 3: Development/Testing

1. Use production backup
2. Generate docker-compose.yml
3. Modify ports to avoid conflicts (8080 instead of 80)
4. Run test environment in parallel
5. Easy to tear down and recreate

## Technical Details

### Detection Logic

**File Detection:**
```python
# Checks for these files in current directory
compose_files = [
    'docker-compose.yml',
    'docker-compose.yaml', 
    'compose.yml',
    'compose.yaml'
]
```

**Label Detection:**
```python
# Checks running containers for compose labels
docker ps --format '{{.Labels}}'
# Looks for: com.docker.compose.*
```

### Config Parsing

Extracts from config.php:
- `dbtype` → Database type (sqlite/mysql/pgsql)
- `dbname` → Database name
- `dbuser` → Database username
- `dbpassword` → Database password
- `dbhost` → Database host
- `dbport` → Database port
- `datadirectory` → Nextcloud data directory
- `trusted_domains` → Array of allowed domains

### Generation Logic

```python
def generate_docker_compose_yml(config, nextcloud_port, db_port):
    """
    Creates compose file with:
    - Appropriate database image (postgres/mariadb/none)
    - Environment variables from config
    - Volume mappings
    - Port mappings
    - Service dependencies
    """
```

## Testing

The feature includes comprehensive unit tests:

```bash
# Run test suite
python3 test_docker_compose_detection.py
```

**Test Coverage:**
- ✅ Parse full config.php with all settings (PostgreSQL)
- ✅ Parse config.php with MySQL database
- ✅ Generate docker-compose.yml for PostgreSQL
- ✅ Generate docker-compose.yml for MySQL
- ✅ Generate docker-compose.yml for SQLite
- ✅ Detect existing docker-compose.yml file
- ✅ Detect absence of docker-compose.yml

**All 7/7 tests pass** ✓

## Troubleshooting

### Issue: Dialog doesn't appear

**Possible causes:**
- config.php not found in backup
- config.php parsing failed
- Detection disabled

**Solution:**
- Check console output for parsing errors
- Verify backup contains config/config.php
- Ensure backup is not corrupted

### Issue: Generated compose file has wrong settings

**Possible causes:**
- config.php has non-standard format
- Custom database configuration
- Special characters in passwords

**Solution:**
- Manually edit generated docker-compose.yml
- Verify config.php settings are correct
- Check for regex parsing issues

### Issue: Folder validation fails

**Possible causes:**
- Insufficient permissions
- Disk space full
- Parent directory doesn't exist

**Solution:**
```bash
# Check permissions
ls -la .

# Create folders manually
mkdir -p nextcloud-data db-data

# Set permissions
chmod 755 nextcloud-data db-data
```

## Best Practices

### 1. Always Review Generated Files

Before using a generated docker-compose.yml:
- Review database passwords
- Check port mappings for conflicts
- Verify volume paths
- Adjust resource limits if needed

### 2. Keep Configuration in Version Control

```bash
# Initialize git repository
git init
git add docker-compose.yml
git commit -m "Initial Nextcloud configuration"
```

### 3. Use Environment Files for Secrets

Instead of hardcoding passwords:

```yaml
# docker-compose.yml
services:
  db:
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
```

```bash
# .env file (add to .gitignore!)
DB_PASSWORD=your_secure_password
```

### 4. Document Custom Changes

Add comments to docker-compose.yml:
```yaml
services:
  nextcloud:
    ports:
      - "9000:80"  # Custom port to avoid conflict with existing service
```

### 5. Test Before Production

Always test the generated configuration:
1. Generate docker-compose.yml
2. Start containers: `docker-compose up -d`
3. Verify services are running: `docker-compose ps`
4. Check logs: `docker-compose logs`
5. Test connectivity
6. Only then proceed with production restore

## Future Enhancements

Potential improvements for future versions:

- [ ] Support for custom networks
- [ ] Redis/Memcache service detection
- [ ] Automatic backup schedule configuration
- [ ] Environment variable file generation
- [ ] Health check configuration
- [ ] Resource limit recommendations
- [ ] SSL/TLS certificate configuration
- [ ] Backup verification before restore

## Support

For issues or questions:
1. Check console output for detailed error messages
2. Review this guide for common scenarios
3. Verify backup integrity
4. Check Docker and docker-compose versions
5. Consult Nextcloud documentation for specific configurations

## Summary

The Docker Compose detection and generation feature provides:

✅ **Automatic environment detection** from backups
✅ **Smart docker-compose.yml generation** based on config.php
✅ **Interactive guidance** for configuration decisions
✅ **Validation and warnings** for potential issues
✅ **Better portability** for migrations and disaster recovery
✅ **Comprehensive testing** with 7/7 unit tests passing

This makes Nextcloud restores safer, easier, and more reliable while maintaining compatibility with existing workflows.
