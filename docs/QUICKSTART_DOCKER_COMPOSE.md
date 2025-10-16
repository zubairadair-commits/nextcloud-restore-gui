# Quick Start: Docker Compose Feature

## What's New?

The Nextcloud restore wizard now automatically detects your backup's configuration and can generate a `docker-compose.yml` file for you. This makes restores safer, easier to reproduce, and better documented.

## 5-Minute Quick Start

### Step 1: Start Restore as Normal

```bash
# Run the restore wizard
python3 nextcloud_restore_and_backup-v9.py
```

Click "🛠 Restore from Backup"

### Step 2: Select Your Backup

- Click "Browse" and select your backup file
- Enter decryption password (if encrypted)
- Click "Next"

### Step 3: Docker Compose Dialog Appears! 🎉

After a few seconds, you'll see a new dialog showing:

```
🐋 Docker Compose Configuration

DETECTED ENVIRONMENT CONFIGURATION
📊 Database Type: PGSQL
📦 Database Name: nextcloud
📁 Data Directory: /var/www/html/data
🌐 Trusted Domains: localhost, cloud.example.com

DOCKER COMPOSE STATUS
ℹ️  No Docker Compose usage detected.
We can generate a docker-compose.yml file for you...

[Generate docker-compose.yml] [Check/Create Folders] [Continue]
```

### Step 4: Generate Your docker-compose.yml

1. Click **"Generate docker-compose.yml"**
2. Choose where to save it (default: `./docker-compose.yml`)
3. ✅ Done! File created with your configuration

### Step 5: Create Required Folders (Optional)

Click **"Check/Create Folders"** to automatically create:
- `./nextcloud-data` - For Nextcloud files
- `./db-data` - For database files (if not SQLite)

### Step 6: Continue Restore

Click **"Continue"** and complete the restore wizard as normal.

### Step 7: Use Your Generated docker-compose.yml

```bash
# Review the generated file
cat docker-compose.yml

# Start your containers
docker-compose up -d

# Check they're running
docker-compose ps

# View logs
docker-compose logs -f

# When done testing, stop them
docker-compose down
```

## That's It! 🎉

You now have a perfectly configured docker-compose.yml that matches your backup's original settings.

---

## Common Scenarios

### Scenario A: "I'm restoring on a new server"

Perfect! The generated docker-compose.yml will recreate your exact environment:

```bash
# On new server
1. Copy backup file
2. Run restore wizard
3. Generate docker-compose.yml
4. docker-compose up -d
5. Complete restore
✅ Identical to original setup!
```

### Scenario B: "I already have docker-compose.yml"

The wizard will detect it and warn you about any differences:

```
✓ Docker Compose usage detected
  Found: docker-compose.yml

⚠️  WARNING: If your existing docker-compose.yml 
doesn't match the detected config.php settings, 
you may experience issues.

Recommendations:
• Check volume mappings
• Verify database credentials
• Review port settings
```

You can:
- Keep your existing file (Click "Continue")
- Generate a new one to compare/replace
- Manually update yours based on detected settings

### Scenario C: "I'm using SQLite"

Even simpler! SQLite doesn't need a separate database container:

```yaml
# Generated docker-compose.yml for SQLite
version: '3.8'

services:
  nextcloud:
    image: nextcloud
    ports:
      - "8080:80"
    volumes:
      - ./nextcloud-data:/var/www/html
    environment:
      - SQLITE_DATABASE=nextcloud
```

Just one service, super clean!

---

## Benefits You Get

### ✅ Automatic Configuration
**Before:** "How did I configure this again?"
**After:** Everything documented in docker-compose.yml

### ✅ Easy Migration
**Before:** Manual Docker commands, easy to forget settings
**After:** One file = entire setup. Copy and run anywhere!

### ✅ Error Prevention
**Before:** "Why can't it connect to the database?"
**After:** Validated configuration, clear warnings for issues

### ✅ Reproducible
**Before:** Different setup each time
**After:** Same setup every time with `docker-compose up`

### ✅ Version Controlled
**Before:** Configuration lost if container deleted
**After:** Save docker-compose.yml in Git, never lose config

---

## Tips & Tricks

### Tip 1: Save docker-compose.yml to Version Control

```bash
git add docker-compose.yml
git commit -m "Add Nextcloud docker-compose configuration"
git push
```

Now your setup is backed up and versioned!

### Tip 2: Customize Ports to Avoid Conflicts

Edit the generated file if you need different ports:

```yaml
services:
  nextcloud:
    ports:
      - "9000:80"  # Change from 8080 to 9000
```

### Tip 3: Add Resource Limits

Enhance the generated file with limits:

```yaml
services:
  db:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
```

### Tip 4: Use Environment Files for Secrets

Instead of hardcoded passwords:

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

### Tip 5: Test First

Always test the generated configuration before using in production:

```bash
# Start in foreground to see logs
docker-compose up

# If all looks good, run in background
docker-compose up -d
```

---

## Troubleshooting

### Dialog Doesn't Appear

**Possible reasons:**
- config.php not found in backup
- Backup is corrupted
- Parsing failed

**Solution:** Check console output for errors. The wizard will still work, just without the Docker Compose feature.

### "Permission Denied" Creating Folders

**Solution:**
```bash
# Create folders manually with proper permissions
mkdir -p nextcloud-data db-data
chmod 755 nextcloud-data db-data
```

### Generated File Has Wrong Password

**Solution:** This is intentional for security. Edit the file and update passwords:

```yaml
environment:
  - POSTGRES_PASSWORD=your_actual_password  # Change this
```

Or use an .env file (recommended).

### Containers Won't Start

**Check:**
```bash
# Are ports available?
netstat -tlnp | grep 8080

# Are volumes accessible?
ls -la nextcloud-data db-data

# View detailed error messages
docker-compose logs
```

---

## FAQs

**Q: Do I have to use the generated docker-compose.yml?**
A: No! It's completely optional. You can click "Continue" and use your existing setup.

**Q: Will this work with my existing Docker containers?**
A: Yes! The detection works with both running containers and standalone setups.

**Q: Can I edit the generated file?**
A: Absolutely! The generated file is a starting point. Customize it for your needs.

**Q: Does this work with encrypted backups?**
A: Yes! Works with both .tar.gz and .tar.gz.gpg files.

**Q: What if I use a different Docker orchestration tool?**
A: The detection still works, and the generated file shows you the correct configuration to use in your tool.

**Q: Will this slow down my restore?**
A: No! Detection adds less than 1 second. The dialog is optional and doesn't block the restore.

---

## What Gets Generated?

### For PostgreSQL:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: nextcloud-db
    volumes:
      - ./db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
    ports:
      - "5432:5432"

  nextcloud:
    image: nextcloud
    container_name: nextcloud-app
    ports:
      - "8080:80"
    volumes:
      - ./nextcloud-data:/var/www/html
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
      - POSTGRES_HOST=db
    depends_on:
      - db
```

### For MySQL/MariaDB:

```yaml
version: '3.8'

services:
  db:
    image: mariadb:10.11
    command: --transaction-isolation=READ-COMMITTED --log-bin=binlog
    volumes:
      - ./db-data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_PASSWORD=password
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
```

### For SQLite:

```yaml
version: '3.8'

services:
  nextcloud:
    image: nextcloud
    volumes:
      - ./nextcloud-data:/var/www/html
    environment:
      - SQLITE_DATABASE=nextcloud
```

---

## Need More Help?

- 📖 **Full Documentation:** See `DOCKER_COMPOSE_FEATURE_GUIDE.md`
- 🧪 **Testing Guide:** See `test_integration_docker_compose.md`
- 🎨 **UI Details:** See `DOCKER_COMPOSE_UI_MOCKUP.md`
- 📊 **Implementation:** See `IMPLEMENTATION_SUMMARY_DOCKER_COMPOSE.md`

---

## Summary

The new Docker Compose feature takes 30 seconds to use and saves hours of configuration work. Just:

1. ▶️ Start restore
2. 🔍 Let it detect your config
3. 📝 Click "Generate docker-compose.yml"
4. ✅ Done!

Your entire Nextcloud environment, perfectly configured, ready to deploy anywhere. 🚀

**Happy restoring!** 🎉
