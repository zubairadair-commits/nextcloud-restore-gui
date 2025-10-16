# Nextcloud Restore GUI

A GUI application for backing up and restoring Nextcloud instances.

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

Run the main application from the repository root:
```bash
python src/nextcloud_restore_and_backup-v9.py
```

Or from the src directory:
```bash
cd src
python nextcloud_restore_and_backup-v9.py
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
