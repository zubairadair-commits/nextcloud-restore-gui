# Nextcloud Restore GUI

A GUI application for backing up and restoring Nextcloud instances.

## Repository Structure

```
nextcloud-restore-gui/
├── src/                          # Source code
│   └── nextcloud_restore_and_backup-v9.py  # Main application
├── tests/                        # Test scripts and demos
│   ├── test_*.py                # Test files
│   ├── demo_*.py                # Demo scripts
│   └── *.sh                     # Test shell scripts
├── docs/                         # Documentation
│   ├── *.md                     # Markdown documentation files
│   └── *.txt                    # Text documentation files
├── config/                       # Configuration files
│   └── config.example.json      # Example configuration template
├── assets/                       # Images and static files
│   ├── *.png                    # Screenshots and images
│   ├── *.html                   # UI mockups
│   └── *.service                # Service files
├── .gitignore                   # Git ignore rules
└── README.md                     # This file
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/zubairadair-commits/nextcloud-restore-gui.git
   cd nextcloud-restore-gui
   ```

2. Install dependencies (if requirements.txt is available):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:
```bash
python src/nextcloud_restore_and_backup-v9.py
```

## Configuration

Copy the example configuration file to create your own:
```bash
cp config/config.example.json config/config.json
```

Edit `config/config.json` with your specific settings.

## Testing

Run tests from the project root:
```bash
python -m pytest tests/
```

Or run individual test files:
```bash
python tests/test_*.py
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:
- Feature guides
- Implementation summaries
- Visual mockups and comparisons
- Developer guides
- User guides

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See LICENSE file for details.
