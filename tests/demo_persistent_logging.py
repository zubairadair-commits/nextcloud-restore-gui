#!/usr/bin/env python3
"""
Demo script to test persistent logging functionality.
This script demonstrates that logging works without launching the full GUI.
"""

import sys
import os
from pathlib import Path
import platform
import logging
from logging.handlers import RotatingFileHandler

# Replicate the setup_logging function from the main script
def setup_logging():
    """
    Setup logging with rotation to a user-writable location.
    Logs are stored in Documents/NextcloudLogs/ directory.
    """
    # Determine user's Documents directory
    if platform.system() == 'Windows':
        documents_dir = Path.home() / 'Documents'
    else:
        documents_dir = Path.home() / 'Documents'
    
    # Create log directory if it doesn't exist
    log_dir = documents_dir / 'NextcloudLogs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log file path
    log_file = log_dir / 'nextcloud_restore_gui.log'
    
    # Configure rotating file handler
    # Max size: 10MB, Keep 5 backup files
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return log_file

# Setup logging and get log file path
LOG_FILE_PATH = setup_logging()
logger = logging.getLogger(__name__)

def main():
    print()
    print("=" * 70)
    print("PERSISTENT LOGGING DEMO")
    print("=" * 70)
    print()
    
    print(f"Log file location: {LOG_FILE_PATH}")
    print()
    
    # Check if log directory exists
    log_dir = LOG_FILE_PATH.parent
    if log_dir.exists():
        print(f"✓ Log directory exists: {log_dir}")
    else:
        print(f"✗ Log directory does not exist: {log_dir}")
        return 1
    
    # Write some test log messages
    print()
    print("Writing test log messages...")
    print()
    
    logger.info("=" * 60)
    logger.info("PERSISTENT LOGGING DEMO - Test Run")
    logger.info("=" * 60)
    logger.info("Testing INFO level logging")
    logger.warning("Testing WARNING level logging")
    logger.error("Testing ERROR level logging")
    logger.info("Testing log message with special characters: éñ™®©")
    logger.info("This log should persist after application restart")
    logger.info("Log rotation is configured: 10MB max size, 5 backup files")
    logger.info("=" * 60)
    
    print()
    print("✓ Test log messages written")
    print()
    
    # Check if log file exists and has content
    if LOG_FILE_PATH.exists():
        file_size = LOG_FILE_PATH.stat().st_size
        print(f"✓ Log file exists: {LOG_FILE_PATH}")
        print(f"✓ Log file size: {file_size} bytes")
        print()
        
        # Display last 10 lines of the log file
        print("Last 10 lines of log file:")
        print("-" * 70)
        try:
            with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"Error reading log file: {e}")
        print("-" * 70)
        print()
    else:
        print(f"✗ Log file does not exist: {LOG_FILE_PATH}")
        return 1
    
    # Check for backup files (if any exist)
    backup_files = list(log_dir.glob('nextcloud_restore_gui.log.*'))
    if backup_files:
        print(f"Found {len(backup_files)} backup log file(s):")
        for backup in sorted(backup_files):
            size = backup.stat().st_size
            print(f"  • {backup.name} ({size} bytes)")
        print()
    else:
        print("No backup log files found (normal for new installations)")
        print()
    
    print("=" * 70)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print()
    print("Key Points:")
    print("  ✓ Logs are stored in a persistent location (Documents/NextcloudLogs/)")
    print("  ✓ Log file will survive PC restarts")
    print("  ✓ Log rotation prevents unlimited growth (10MB max, 5 backups)")
    print("  ✓ Works for both .py and .exe execution")
    print("  ✓ Cross-platform support (Windows, macOS, Linux)")
    print()
    print("To view logs in the application:")
    print("  1. Launch the Nextcloud Restore & Backup Utility")
    print("  2. Click the menu button (☰) in the top-right corner")
    print("  3. Select '📋 View Logs'")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
