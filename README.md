# Nextcloud Restore GUI

**The easiest way to backup and restore your Nextcloud instance - no technical knowledge required!**

This beginner-friendly application was designed to make Nextcloud backup and restore operations **simple and stress-free**. Whether you're a complete beginner or an experienced user, this tool handles everything for you:

✅ **Automated Docker Installation** - No need to install Docker manually  
✅ **Encryption Tools Setup** - Automatically installs GPG/encryption software when needed  
✅ **Step-by-Step Wizard** - Clear, easy-to-follow interface guides you through every step  
✅ **Minimal User Input** - Just a few clicks to complete backup or restore operations  
✅ **Smart Automation** - Detects your system configuration and handles technical details automatically  

## Why This App Makes Everything Easy

Traditional Nextcloud backup and restore requires:
- 🔧 Manual Docker installation and configuration
- 🔒 Setting up encryption tools (GPG4Win on Windows, etc.)
- 📝 Complex command-line operations
- 💻 Technical knowledge of databases, containers, and file systems

**With this app, you get:**
- 🚀 **One-Click Setup** - The app installs everything you need automatically
- 🎯 **Clear Visual Interface** - No command-line knowledge required
- 🛡️ **Secure by Default** - Encryption is easy to enable with built-in setup
- 🌐 **Remote Access** - Optional Tailscale integration for accessing your backups from anywhere
- ⏰ **Scheduled Backups** - Set it and forget it with automated backup schedules

## Features

- **Complete Nextcloud Backup & Restore**: Full backup and restoration of your entire Nextcloud instance
- **Automated Setup**: Installs Docker, encryption tools, and all dependencies automatically
- **Database Backup**: Automated database backup and restoration
- **File Backup**: Comprehensive file and directory backup capabilities
- **Encrypted Backups**: Easy-to-enable encryption for secure storage
- **Cloud Storage**: Manage cloud storage backups efficiently
- **Tailscale Integration**: Secure remote access to your Nextcloud instance from anywhere
- **Scheduled Backups**: Set up automatic backups on a schedule
- **User-Friendly GUI**: Intuitive graphical interface - no command-line needed
- **Cross-Platform**: Works on Windows, Linux, and other operating systems

## GUI Overview

Experience the simplicity and user-friendliness of our intuitive interface. Below are screenshots showcasing the key features and how easy it is to navigate through the application:

### Main Dashboard
![Landing Page](screenshots/01-landing-page.png)
**The intuitive main dashboard** provides instant access to all essential functions with clearly labeled buttons. No confusing menus or hidden options - everything you need is right at your fingertips. Simply click on any option to get started with backing up, restoring, or managing your Nextcloud instance.

### Restore from Backup
![Restore Wizard](screenshots/02-restore-wizard.png)
**Step-by-step restore wizard** makes recovering your Nextcloud instance effortless. The wizard guides you through each step with clear instructions and helpful tooltips. All technical complexities are handled automatically - just select your backup file and let the application do the rest.

### Backup Your Data
![Backup Wizard](screenshots/03-backup-wizard.png)
**One-click backup wizard** simplifies the entire backup process. The interface clearly shows what will be backed up and where it will be stored. Advanced options are available if needed, but the smart defaults work perfectly for most users. Creating secure backups has never been easier!

### Schedule Automated Backups
![Schedule Backup](screenshots/04-schedule-backup.png)
**Automated backup scheduling** allows you to set up recurring backups with just a few clicks. Choose your preferred schedule (daily, weekly, or custom intervals) and let the application handle everything automatically. The clean interface makes it easy to configure backup retention policies and encryption options.

### Remote Access Setup
![Remote Access](screenshots/05-remote-access.png)
**Seamless Tailscale integration** for secure remote access to your Nextcloud instance from anywhere in the world. The setup process is fully automated - the application detects if Tailscale is installed and guides you through the configuration. Access your backups remotely without complex VPN or port forwarding setups.

### Backup History & Management
![Backup History](screenshots/06-backup-history.png)
**Comprehensive backup history** gives you complete visibility into all your backup operations. View detailed information about each backup, including size, date, and status. Restore from any previous backup point with a single click. The organized layout makes it easy to manage and clean up old backups.

## Getting Started - It's Really This Simple!

**Total Time: Less than 5 minutes from download to your first backup or restore!**

### For Complete Beginners

1. **Download** the latest release from the [Releases page](https://github.com/zubairadair-commits/nextcloud-restore-gui/releases)
2. **Double-click** the downloaded file to run it
3. **Follow the wizard** - It will:
   - ✅ Check if Docker is installed (and install it for you if not)
   - ✅ Install encryption tools if you want encrypted backups
   - ✅ Guide you through backup or restore with clear instructions
   - ✅ Show real-time progress so you know it's working

**That's it!** No technical knowledge, command-line skills, or manual configuration required.

### What Makes This So Easy?

- **Automated Installation**: The app handles installing Docker, GPG encryption tools, and any other dependencies
- **Smart Detection**: It checks what's already on your system and only installs what's missing
- **Clear Instructions**: Every step has helpful tooltips and descriptions
- **Beginner-Friendly**: Designed for people who have never used Docker or command-line tools
- **Safe Defaults**: You can accept the default options and everything will work correctly
- **Error Prevention**: The app validates your input and prevents common mistakes

## How It Handles the Technical Stuff For You

### Automated Docker Installation
- **Windows**: Downloads and installs Docker Desktop automatically
- **Linux**: Uses package managers to install Docker with one click
- **Configuration**: Sets up Docker with optimal settings for Nextcloud

### Encryption Made Easy
- **Automatic Detection**: Checks if GPG is installed on your system
- **One-Click Install**: Downloads and installs GPG4Win on Windows (or equivalent on other systems)
- **Secure Setup**: Configures encryption with strong defaults
- **Optional**: You can skip encryption if you don't need it

### Container Management
- **Automatic**: Handles all Docker container operations
- **Smart**: Detects existing Nextcloud containers
- **Safe**: Stops and starts containers safely during backup/restore
- **No Commands**: All Docker operations happen in the background

### Database Handling
- **Supported**: MySQL/MariaDB, PostgreSQL, SQLite
- **Automatic**: Detects your database type
- **Secure**: Safe backup and restore of all database data
- **No Manual Dumps**: Everything is automated

## Documentation

Comprehensive documentation is available in the `docs/` directory:
- Feature guides
- Implementation summaries
- Visual mockups and comparisons
- Developer guides
- User guides

## For Developers

If you want to contribute to the project or run from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/zubairadair-commits/nextcloud-restore-gui.git
   cd nextcloud-restore-gui
   ```

2. Install dependencies (optional - only needed for testing):
   ```bash
   pip install -r requirements.txt
   ```

3. Run from source:
   ```bash
   python src/nextcloud_restore_and_backup-v9.py
   ```

4. Run tests:
   ```bash
   python -m pytest tests/
   ```

For more details, see the `docs/DEVELOPER_GUIDE.md` file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Keywords

nextcloud, backup, restore, nextcloud-backup, nextcloud-restore, database-backup, file-backup, cloud-storage, python, gui, automation, utility, cloud-app, windows

## License

See LICENSE file for details.