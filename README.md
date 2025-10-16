# Nextcloud Restore GUI

A Python GUI utility for backing up and restoring Nextcloud instances with support for database backup, file backup, and cloud storage management. This automation tool provides an easy-to-use interface for Nextcloud backup and restore operations on Windows and other platforms.

## Features

- **Nextcloud Backup & Restore**: Complete backup and restore functionality for Nextcloud instances
- **Database Backup**: Automated database backup and restoration
- **File Backup**: Comprehensive file and directory backup capabilities
- **Cloud Storage**: Manage cloud storage backups efficiently
- **Tailscale Integration**: Secure remote access to your Nextcloud instance from anywhere using Tailscale VPN
- **GUI Interface**: User-friendly graphical interface built with Python tkinter
- **Automation**: Automated backup/restore processes with minimal user intervention
- **Cross-Platform**: Works on Windows and other operating systems

## Repository Structure

The repository is organized into a clear, professional folder structure:

```
nextcloud-restore-gui/
├── src/                          # Source code
│   └── nextcloud_restore_and_backup-v9.py  # Main application
├── tests/                        # Test scripts and demos (91 files)
│   ├── test_*.py                # Test files
│   ├── demo_*.py                # Demo scripts
│   ├── validate_*.py            # Validation scripts
│   └── *.sh                     # Test shell scripts
├── docs/                         # Documentation (267 files)
│   ├── *.md                     # Markdown documentation files
│   └── *.txt                    # Text documentation files
├── config/                       # Configuration files
│   └── config.example.json      # Example configuration template
├── assets/                       # Images and static files (35 files)
│   ├── *.png                    # Screenshots and images
│   ├── *.html                   # UI mockups
│   └── *.service                # Service files
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

## Download & Run

**Getting Started is Easy!**

1. **Download** the latest release from the [Releases page](https://github.com/zubairadair-commits/nextcloud-restore-gui/releases)
2. **Run** the downloaded EXE file
3. **Follow** the intuitive wizard to backup or restore your Nextcloud instance

The application includes:
- ✅ Automated setup and configuration
- ✅ Built-in Tailscale integration for secure remote access
- ✅ Step-by-step wizard interface
- ✅ No manual installation or dependencies required

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
