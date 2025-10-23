import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import threading
import subprocess
import os
import tarfile
import time
import tempfile
import shutil
import webbrowser
import traceback
import re
import platform
import sys
import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import shlex

# Configure persistent logging with rotation
# Log file location: Documents/NextcloudLogs/nextcloud_restore_gui.log
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
    
    # Console handler - only add in scheduled/test-run mode to avoid terminal window in GUI mode
    # Check command-line arguments to determine if we're in non-GUI mode
    is_non_gui_mode = '--scheduled' in sys.argv or '--test-run' in sys.argv
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    
    # Only add console handler for scheduled/test-run modes
    if is_non_gui_mode:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        root_logger.addHandler(console_handler)
    
    return log_file

# Setup logging and get log file path
LOG_FILE_PATH = setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"Logging initialized. Log file: {LOG_FILE_PATH}")

# Setup Docker error logging with dedicated file
def setup_docker_error_logging():
    """
    Setup dedicated Docker error logging file.
    Returns the path to the Docker error log file.
    """
    if platform.system() == 'Windows':
        documents_dir = Path.home() / 'Documents'
    else:
        documents_dir = Path.home() / 'Documents'
    
    log_dir = documents_dir / 'NextcloudLogs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    docker_error_log_file = log_dir / 'nextcloud_docker_errors.log'
    return docker_error_log_file

DOCKER_ERROR_LOG_PATH = setup_docker_error_logging()

def safe_widget_update(widget, update_func, error_context="widget update"):
    """
    Safely update a widget, catching TclError if the widget has been destroyed.
    
    Args:
        widget: The widget to update (or None)
        update_func: A callable that performs the update
        error_context: Description of what's being updated (for logging)
    
    Returns:
        True if update succeeded, False otherwise
    """
    if widget is None:
        logger.debug(f"Skipping {error_context}: widget is None")
        return False
    
    try:
        # Check if widget still exists
        if not widget.winfo_exists():
            logger.debug(f"Skipping {error_context}: widget no longer exists")
            return False
        
        # Perform the update
        update_func()
        return True
    except tk.TclError as e:
        # Widget was destroyed between existence check and update
        logger.debug(f"TclError during {error_context}: {e}")
        return False
    except Exception as e:
        # Log unexpected errors but don't crash
        logger.error(f"Unexpected error during {error_context}: {e}")
        return False

def log_docker_error(error_type, error_message, container_name=None, port=None, additional_info=None):
    """
    Log Docker error to dedicated error log file with timestamp and context.
    
    Args:
        error_type: Type of error (e.g., 'port_conflict', 'image_not_found', 'container_start_failed')
        error_message: The actual error message from Docker
        container_name: Name of the container that failed (if applicable)
        port: Port that caused the issue (if applicable)
        additional_info: Any additional context information
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"\n{'='*80}\n"
    log_entry += f"[{timestamp}] Docker Error: {error_type}\n"
    log_entry += f"{'='*80}\n"
    
    if container_name:
        log_entry += f"Container: {container_name}\n"
    if port:
        log_entry += f"Port: {port}\n"
    
    log_entry += f"Error Message:\n{error_message}\n"
    
    if additional_info:
        log_entry += f"\nAdditional Information:\n{additional_info}\n"
    
    log_entry += f"{'='*80}\n"
    
    # Write to dedicated Docker error log
    try:
        with open(DOCKER_ERROR_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to write to Docker error log: {e}")
    
    # Also log to main log
    logger.error(f"Docker Error ({error_type}): {error_message}")

def analyze_docker_error(stderr_output, container_name=None, port=None, dbtype=None):
    """
    Analyze Docker error output and return structured error information.
    
    Args:
        stderr_output: Docker error message
        container_name: Name of the container
        port: Port number
        dbtype: Database type ('sqlite', 'mysql', 'pgsql') - helps classify errors correctly
    
    Returns:
        dict with keys:
            - error_type: Type of error detected
            - user_message: User-friendly error message
            - suggested_action: Recommended action to resolve the issue
            - alternative_port: Suggested alternative port (if port conflict)
            - is_recoverable: Whether the error can be resolved by user action
    """
    error_info = {
        'error_type': 'unknown',
        'user_message': 'An unknown error occurred while creating the Docker container.',
        'suggested_action': 'Please check Docker logs for more details.',
        'alternative_port': None,
        'is_recoverable': False
    }
    
    stderr_lower = stderr_output.lower()
    
    # No such container error - this is a logic/config error, not Docker not running
    if 'no such container' in stderr_lower:
        error_info['error_type'] = 'container_not_found'
        error_info['user_message'] = "The specified container does not exist."
        error_info['is_recoverable'] = True
        
        # Provide context-specific guidance
        if container_name and 'db' in container_name.lower():
            # Special handling for SQLite - this is expected, not an error
            if dbtype == 'sqlite':
                error_info['error_type'] = 'expected_sqlite_no_db'
                error_info['user_message'] = "SQLite configuration detected - no separate database container needed."
                error_info['suggested_action'] = (
                    "This is expected behavior for SQLite backups.\n\n"
                    "SQLite stores the database in a file within the data folder,\n"
                    "so no separate database container is required.\n\n"
                    "The restore will continue normally."
                )
                error_info['is_recoverable'] = True
                return error_info
            
            error_info['suggested_action'] = (
                f"The database container '{container_name}' was not found.\n\n"
                "This may be because:\n"
                "1. You are using SQLite (which doesn't need a separate database container)\n"
                "2. The database container hasn't been created yet\n"
                "3. The container name is incorrect\n\n"
                "If you're restoring a SQLite backup, this is expected and the restore should continue.\n"
                "For MySQL/PostgreSQL, ensure the database container is running:\n"
                f"  docker ps (to check running containers)\n"
                f"  docker start {container_name} (to start the container if it exists but is stopped)"
            )
        else:
            error_info['suggested_action'] = (
                f"Container '{container_name}' does not exist.\n\n"
                "Check running and stopped containers:\n"
                "  docker ps -a\n\n"
                "If the container exists but is stopped, start it:\n"
                f"  docker start {container_name}"
            )
        return error_info
    
    # Port conflict detection
    if 'bind' in stderr_lower and ('already' in stderr_lower or 'in use' in stderr_lower):
        error_info['error_type'] = 'port_conflict'
        error_info['user_message'] = f"Port {port} is already in use by another application or container."
        error_info['is_recoverable'] = True
        
        # Suggest alternative ports
        if port:
            suggested_ports = []
            for offset in [1, 2, 10, 100]:
                alt_port = int(port) + offset
                if alt_port <= 65535:
                    suggested_ports.append(alt_port)
            
            if suggested_ports:
                error_info['alternative_port'] = suggested_ports[0]
                error_info['suggested_action'] = (
                    f"Try one of these alternative ports: {', '.join(map(str, suggested_ports[:3]))}\n\n"
                    "Or stop the application/container using the port:\n"
                    "  docker ps (to see running containers)\n"
                    "  docker stop <container-name> (to stop conflicting container)"
                )
        else:
            error_info['suggested_action'] = (
                "Check which application is using the port and stop it, "
                "or choose a different port for your Nextcloud container."
            )
    
    # Image not found
    elif 'not found' in stderr_lower or 'no such image' in stderr_lower:
        error_info['error_type'] = 'image_not_found'
        error_info['user_message'] = "The required Docker image could not be found."
        error_info['is_recoverable'] = True
        error_info['suggested_action'] = (
            "The image may need to be downloaded. Try:\n"
            "1. Check your internet connection\n"
            "2. Manually pull the image: docker pull nextcloud\n"
            "3. Restart the restore process"
        )
    
    # Container name conflict
    elif 'name' in stderr_lower and ('already' in stderr_lower or 'in use' in stderr_lower or 'conflict' in stderr_lower):
        error_info['error_type'] = 'container_name_conflict'
        error_info['user_message'] = f"A container with name '{container_name}' already exists."
        error_info['is_recoverable'] = True
        error_info['suggested_action'] = (
            f"Remove the existing container or choose a different name:\n"
            f"  docker rm {container_name} (to remove the container)\n"
            f"  docker rm -f {container_name} (to force remove if running)\n\n"
            "Or choose a different container name in the restore wizard."
        )
    
    # Network errors
    elif 'network' in stderr_lower and ('not found' in stderr_lower or 'error' in stderr_lower):
        error_info['error_type'] = 'network_error'
        error_info['user_message'] = "Docker network configuration error."
        error_info['is_recoverable'] = True
        error_info['suggested_action'] = (
            "Try creating the default bridge network:\n"
            "  docker network create bridge\n\n"
            "Or restart Docker Desktop/daemon."
        )
    
    # Volume/mount errors
    elif 'mount' in stderr_lower or 'volume' in stderr_lower:
        error_info['error_type'] = 'volume_error'
        error_info['user_message'] = "Failed to mount volume or directory."
        error_info['is_recoverable'] = True
        error_info['suggested_action'] = (
            "Check that:\n"
            "1. The directory exists and is accessible\n"
            "2. You have proper permissions\n"
            "3. The path is correct (absolute path required)"
        )
    
    # Docker daemon not running
    elif 'daemon' in stderr_lower or 'connect' in stderr_lower or 'cannot connect' in stderr_lower:
        error_info['error_type'] = 'docker_not_running'
        error_info['user_message'] = "Docker daemon is not running or not accessible."
        error_info['is_recoverable'] = True
        error_info['suggested_action'] = (
            "Start Docker:\n"
            "  - Windows/Mac: Open Docker Desktop\n"
            "  - Linux: sudo systemctl start docker\n\n"
            "Then retry the restore."
        )
    
    # Permission denied
    elif 'permission denied' in stderr_lower or 'access denied' in stderr_lower:
        error_info['error_type'] = 'permission_error'
        error_info['user_message'] = "Permission denied - insufficient privileges to run Docker."
        error_info['is_recoverable'] = True
        error_info['suggested_action'] = (
            "Run with proper permissions:\n"
            "  - Windows: Run as Administrator\n"
            "  - Linux: Add user to docker group or use sudo\n"
            "    sudo usermod -aG docker $(whoami)\n"
            "    (logout and login again after running this)"
        )
    
    # Resource exhaustion
    elif 'no space' in stderr_lower or 'disk' in stderr_lower:
        error_info['error_type'] = 'disk_space_error'
        error_info['user_message'] = "Insufficient disk space for Docker operation."
        error_info['is_recoverable'] = True
        error_info['suggested_action'] = (
            "Free up disk space:\n"
            "  - Remove unused Docker images: docker image prune -a\n"
            "  - Remove stopped containers: docker container prune\n"
            "  - Check available disk space: df -h (Linux) or dir (Windows)"
        )
    
    return error_info

DOCKER_INSTALLER_URL = "https://www.docker.com/products/docker-desktop/"
GPG_DOWNLOAD_URL = "https://files.gpg4win.org/gpg4win-latest.exe"

# --- Utility Functions ---
def get_app_data_directory():
    """
    Get the application data directory for storing internal files.
    Creates the directory if it doesn't exist.
    
    Returns:
        Path: Path to the app data directory (~/.nextcloud_backup_utility)
    """
    home_dir = Path.home()
    app_data_dir = home_dir / ".nextcloud_backup_utility"
    app_data_dir.mkdir(exist_ok=True)
    return app_data_dir

def get_compose_directory():
    """
    Get the directory for storing docker-compose.yml files.
    Creates the directory if it doesn't exist.
    
    Returns:
        Path: Path to the compose directory (~/.nextcloud_backup_utility/compose)
    """
    app_data_dir = get_app_data_directory()
    compose_dir = app_data_dir / "compose"
    compose_dir.mkdir(exist_ok=True)
    return compose_dir

# --- Tooltip System for In-App Help ---
class ToolTip:
    """
    Tooltip widget that appears on hover to provide contextual help.
    """
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None
        
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
    
    def on_enter(self, event=None):
        """Schedule tooltip to appear after delay"""
        self.after_id = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event=None):
        """Hide tooltip and cancel scheduled appearance"""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.hide_tooltip()
    
    def show_tooltip(self):
        """Display the tooltip window"""
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffcc",
            foreground="#000000",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 9),
            justify=tk.LEFT,
            padx=5,
            pady=3
        )
        label.pack()
    
    def hide_tooltip(self):
        """Hide the tooltip window"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# --- Backup History Manager ---
class BackupHistoryManager:
    """
    Manages backup history using SQLite database.
    Tracks backup metadata including size, timestamp, verification status, and notes.
    """
    def __init__(self, db_path=None):
        if db_path is None:
            # Use user's home directory for cross-platform compatibility
            home_dir = Path.home()
            config_dir = home_dir / ".nextcloud_backup_utility"
            config_dir.mkdir(exist_ok=True)
            self.db_path = config_dir / "backup_history.db"
        else:
            self.db_path = Path(db_path)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_path TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                size_bytes INTEGER,
                encrypted BOOLEAN,
                database_type TEXT,
                folders_backed_up TEXT,
                verification_status TEXT,
                verification_details TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_backup(self, backup_path, database_type=None, folders=None, encrypted=False, notes=""):
        """Add a new backup record"""
        logger.info(f"BACKUP HISTORY: Adding backup to database: {backup_path}")
        logger.info(f"BACKUP HISTORY: Database location: {self.db_path}")
        logger.info(f"BACKUP HISTORY: Database type: {database_type}, Encrypted: {encrypted}, Notes: {notes}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get file size
        size_bytes = 0
        if os.path.exists(backup_path):
            size_bytes = os.path.getsize(backup_path)
        
        # Convert folders list to JSON string
        folders_json = json.dumps(folders) if folders else "[]"
        
        cursor.execute('''
            INSERT INTO backups 
            (backup_path, timestamp, size_bytes, encrypted, database_type, folders_backed_up, notes, verification_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (backup_path, datetime.now().isoformat(), size_bytes, encrypted, 
              database_type, folders_json, notes, "pending"))
        
        backup_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"BACKUP HISTORY: Successfully added backup with ID {backup_id} (size: {size_bytes} bytes)")
        
        return backup_id
    
    def update_verification(self, backup_id, status, details=""):
        """Update verification status of a backup"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE backups 
            SET verification_status = ?, verification_details = ?
            WHERE id = ?
        ''', (status, details, backup_id))
        
        conn.commit()
        conn.close()
    
    def get_all_backups(self, limit=50):
        """Retrieve all backups, most recent first"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, backup_path, timestamp, size_bytes, encrypted, 
                   database_type, folders_backed_up, verification_status, 
                   verification_details, notes
            FROM backups
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_backup_by_id(self, backup_id):
        """Get a specific backup record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, backup_path, timestamp, size_bytes, encrypted, 
                   database_type, folders_backed_up, verification_status, 
                   verification_details, notes
            FROM backups
            WHERE id = ?
        ''', (backup_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result
    
    def delete_backup(self, backup_id):
        """Delete a backup record from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM backups WHERE id = ?', (backup_id,))
        
        conn.commit()
        conn.close()
        logger.info(f"BACKUP HISTORY: Deleted backup record with ID {backup_id}")

# --- Service Health Check Functions ---
def find_tailscale_exe():
    """
    Find tailscale.exe on Windows by checking multiple locations.
    Returns the full path to tailscale.exe if found, None otherwise.
    """
    if platform.system() != "Windows":
        return None
    
    # Method 1: Check if tailscale is in PATH
    try:
        creation_flags = get_subprocess_creation_flags()
        result = subprocess.run(
            ["where", "tailscale"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=creation_flags
        )
        if result.returncode == 0 and result.stdout.strip():
            # where command returns one or more paths, take the first one
            path = result.stdout.strip().split('\n')[0]
            if os.path.isfile(path):
                return path
    except Exception:
        pass
    
    # Method 2: Check common installation directories
    common_locations = [
        r"C:\Program Files\Tailscale\tailscale.exe",
        r"C:\Program Files (x86)\Tailscale\tailscale.exe",
        os.path.expandvars(r"%ProgramFiles%\Tailscale\tailscale.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Tailscale\tailscale.exe"),
        os.path.expandvars(r"%LocalAppData%\Tailscale\tailscale.exe"),
    ]
    
    for location in common_locations:
        if os.path.isfile(location):
            return location
    
    # Method 3: Try to query the Windows registry
    try:
        import winreg
        
        # Check HKEY_LOCAL_MACHINE for installation path
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tailscale IPN"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Tailscale IPN"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Tailscale IPN"),
        ]
        
        for hkey, subkey in registry_paths:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    # Try to get install location or executable path
                    try:
                        install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
                        exe_path = os.path.join(install_dir, "tailscale.exe")
                        if os.path.isfile(exe_path):
                            return exe_path
                    except FileNotFoundError:
                        pass
                    
                    try:
                        exe_path, _ = winreg.QueryValueEx(key, "ExecutablePath")
                        if os.path.isfile(exe_path):
                            return exe_path
                    except FileNotFoundError:
                        pass
            except WindowsError:
                pass
    except ImportError:
        # winreg not available (shouldn't happen on Windows, but just in case)
        pass
    except Exception:
        pass
    
    return None

def check_service_health():
    """
    Check health of various services and return status dictionary.
    Returns dict with service names as keys and status dicts as values.
    """
    health_status = {
        'nextcloud': {'status': 'unknown', 'message': '', 'checked_at': datetime.now()},
        'tailscale': {'status': 'unknown', 'message': '', 'checked_at': datetime.now()},
        'docker': {'status': 'unknown', 'message': '', 'checked_at': datetime.now()},
        'network': {'status': 'unknown', 'message': '', 'checked_at': datetime.now()},
    }
    
    # Check Docker
    try:
        result = run_docker_command_silent(['docker', 'ps'], timeout=5)
        if result and result.returncode == 0:
            health_status['docker'] = {
                'status': 'healthy',
                'message': 'Docker is running',
                'checked_at': datetime.now()
            }
        else:
            health_status['docker'] = {
                'status': 'error',
                'message': 'Docker is not responding',
                'checked_at': datetime.now()
            }
    except Exception as e:
        health_status['docker'] = {
            'status': 'error',
            'message': f'Docker check failed: {str(e)}',
            'checked_at': datetime.now()
        }
    
    # Check Nextcloud container
    try:
        containers = get_nextcloud_container_name()
        if containers:
            health_status['nextcloud'] = {
                'status': 'healthy',
                'message': f'Nextcloud container running: {containers}',
                'checked_at': datetime.now()
            }
        else:
            health_status['nextcloud'] = {
                'status': 'warning',
                'message': 'No Nextcloud container detected',
                'checked_at': datetime.now()
            }
    except Exception as e:
        health_status['nextcloud'] = {
            'status': 'error',
            'message': f'Failed to check Nextcloud: {str(e)}',
            'checked_at': datetime.now()
        }
    
    # Check Tailscale
    try:
        if platform.system() == "Windows":
            # Find Tailscale executable using enhanced detection
            tailscale_path = find_tailscale_exe()
            
            if tailscale_path:
                # Tailscale is installed, check if it's running
                # Try Windows service check first
                try:
                    creation_flags = get_subprocess_creation_flags()
                    result = subprocess.run(
                        ['sc', 'query', 'Tailscale'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        creationflags=creation_flags
                    )
                    if result.returncode == 0 and 'RUNNING' in result.stdout:
                        health_status['tailscale'] = {
                            'status': 'healthy',
                            'message': 'Tailscale service is running',
                            'checked_at': datetime.now()
                        }
                    elif result.returncode == 0 and 'STOPPED' in result.stdout:
                        health_status['tailscale'] = {
                            'status': 'warning',
                            'message': 'Tailscale service is stopped',
                            'checked_at': datetime.now()
                        }
                    else:
                        # Service not found, try CLI as fallback
                        raise subprocess.SubprocessError("Service check inconclusive")
                except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                    # Fallback to CLI check using full path
                    creation_flags = get_subprocess_creation_flags()
                    result = subprocess.run(
                        [tailscale_path, 'status'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        creationflags=creation_flags
                    )
                    if result.returncode == 0:
                        health_status['tailscale'] = {
                            'status': 'healthy',
                            'message': 'Tailscale is running',
                            'checked_at': datetime.now()
                        }
                    else:
                        health_status['tailscale'] = {
                            'status': 'warning',
                            'message': 'Tailscale not running',
                            'checked_at': datetime.now()
                        }
            else:
                # Tailscale not found
                health_status['tailscale'] = {
                    'status': 'warning',
                    'message': 'Tailscale not installed',
                    'checked_at': datetime.now()
                }
        else:
            # Unix/Linux/Mac - use CLI directly
            creation_flags = get_subprocess_creation_flags()
            result = subprocess.run(
                ['tailscale', 'status'],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=creation_flags
            )
            if result.returncode == 0:
                health_status['tailscale'] = {
                    'status': 'healthy',
                    'message': 'Tailscale is running',
                    'checked_at': datetime.now()
                }
            else:
                health_status['tailscale'] = {
                    'status': 'warning',
                    'message': 'Tailscale not running or not installed',
                    'checked_at': datetime.now()
                }
    except Exception:
        health_status['tailscale'] = {
            'status': 'warning',
            'message': 'Tailscale not installed',
            'checked_at': datetime.now()
        }
    
    # Check network connectivity
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        health_status['network'] = {
            'status': 'healthy',
            'message': 'Network connectivity OK',
            'checked_at': datetime.now()
        }
    except Exception:
        health_status['network'] = {
            'status': 'error',
            'message': 'No network connectivity',
            'checked_at': datetime.now()
        }
    
    return health_status

def verify_backup_integrity(backup_path, password=None):
    """
    Verify backup file integrity by testing archive extraction.
    Returns (status, details) tuple where status is 'success', 'warning', or 'error'.
    """
    try:
        if not os.path.exists(backup_path):
            return ('error', f'Backup file not found: {backup_path}')
        
        # Check file size
        file_size = os.path.getsize(backup_path)
        if file_size == 0:
            return ('error', 'Backup file is empty')
        
        # Test if it's encrypted
        is_encrypted = backup_path.endswith('.gpg')
        
        if is_encrypted and not password:
            return ('warning', 'Encrypted backup - password required for full verification')
        
        # Test archive integrity
        test_file = backup_path
        temp_decrypted = None
        
        try:
            if is_encrypted and password:
                # Decrypt to temp file for testing
                temp_decrypted = tempfile.mktemp(suffix='.tar.gz')
                result = decrypt_file_gpg(backup_path, temp_decrypted, password)
                if not result:
                    return ('error', 'Failed to decrypt backup - incorrect password or corrupted file')
                test_file = temp_decrypted
            
            # Test tar.gz integrity
            with tarfile.open(test_file, 'r:gz') as tar:
                # List members to verify structure
                members = tar.getmembers()
                if len(members) == 0:
                    return ('error', 'Backup archive is empty')
                
                # Check for key folders
                has_config = any('config/' in m.name for m in members)
                has_data = any('data/' in m.name for m in members)
                
                if not has_config:
                    return ('warning', 'Backup may be incomplete - config folder not found')
                if not has_data:
                    return ('warning', 'Backup may be incomplete - data folder not found')
                
                return ('success', f'Backup verified successfully - {len(members)} files, {file_size / (1024*1024):.1f} MB')
        
        finally:
            if temp_decrypted and os.path.exists(temp_decrypted):
                os.remove(temp_decrypted)
    
    except tarfile.TarError as e:
        return ('error', f'Corrupted archive: {str(e)}')
    except Exception as e:
        return ('error', f'Verification failed: {str(e)}')

# --- Customizable container and DB settings ---
NEXTCLOUD_IMAGE = "nextcloud"
POSTGRES_IMAGE = "postgres"
NEXTCLOUD_CONTAINER_NAME = "nextcloud-app"
POSTGRES_CONTAINER_NAME = "nextcloud-db"
POSTGRES_DB = "nextcloud"
POSTGRES_USER = "nextcloud"
POSTGRES_PASSWORD = "example"
POSTGRES_PORT = 5432

# --- Theme Color Definitions ---
THEMES = {
    'light': {
        'bg': '#f0f0f0',
        'fg': '#000000',
        'button_bg': '#e0e0e0',
        'button_fg': '#000000',
        'button_active_bg': '#d0d0d0',
        'entry_bg': '#ffffff',
        'entry_fg': '#000000',
        'frame_bg': '#f0f0f0',
        'header_bg': '#f0f0f0',
        'header_fg': '#000000',
        'status_fg': '#000000',
        'info_bg': '#e3f2fd',
        'info_fg': '#000000',
        'warning_bg': '#e8f5e9',
        'warning_fg': '#2e7d32',
        'error_fg': '#d32f2f',
        'hint_fg': '#666666',
        'progress_fg': '#1565c0',  # Dark blue for light theme - better readability than bright blue
        # Button-specific colors (maintain original button colors but adjust for theme)
        'backup_btn': '#3daee9',
        'restore_btn': '#45bf55',
        'new_instance_btn': '#f7b32b',
        'schedule_btn': '#9b59b6',
    },
    'dark': {
        'bg': '#1e1e1e',
        'fg': '#e0e0e0',
        'button_bg': '#2d2d2d',
        'button_fg': '#e0e0e0',
        'button_active_bg': '#3d3d3d',
        'entry_bg': '#2d2d2d',
        'entry_fg': '#e0e0e0',
        'frame_bg': '#1e1e1e',
        'header_bg': '#252525',
        'header_fg': '#e0e0e0',
        'status_fg': '#b0b0b0',
        'info_bg': '#1a3a4a',
        'info_fg': '#e0e0e0',
        'warning_bg': '#2a3a2a',
        'warning_fg': '#7cb342',
        'error_fg': '#ef5350',
        'hint_fg': '#999999',
        'progress_fg': '#ffd966',  # Bright yellow for dark theme - high visibility
        # Button-specific colors (darker versions for dark theme)
        'backup_btn': '#2c8ab8',
        'restore_btn': '#378d44',
        'new_instance_btn': '#c89020',
        'schedule_btn': '#7b4a85',
    }
}

# --- Page Rendering Decorator for Logging and Error Handling ---
def log_page_render(page_name):
    """
    Decorator to add diagnostic logging and error handling to page rendering methods.
    Logs entry, exit, and any exceptions that occur during page rendering.
    Ensures minimal fallback UI is always shown if rendering fails.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            logger.info("=" * 60)
            logger.info(f"{page_name}: Starting page render")
            logger.info(f"Current theme: {self.current_theme}")
            try:
                result = func(self, *args, **kwargs)
                logger.info(f"{page_name}: Page render complete successfully")
                logger.info("=" * 60)
                return result
            except Exception as e:
                logger.error("=" * 60)
                logger.error(f"{page_name}: ERROR during page render: {e}")
                logger.error(f"{page_name}: Traceback: {traceback.format_exc()}")
                logger.error("=" * 60)
                # Show error message to user
                messagebox.showerror(
                    "Page Rendering Error",
                    f"Failed to render {page_name} page:\n{str(e)}\n\nCheck nextcloud_restore_gui.log for details."
                )
                # Try to show landing page as fallback
                try:
                    logger.info(f"{page_name}: Attempting fallback to landing page")
                    self.show_landing()
                except:
                    logger.error(f"{page_name}: Fallback to landing page also failed")
                    # Last resort: create minimal error UI so page is never blank
                    try:
                        logger.info(f"{page_name}: Creating minimal error UI as last resort")
                        for widget in self.body_frame.winfo_children():
                            widget.destroy()
                        error_label = tk.Label(
                            self.body_frame,
                            text=f"⚠️ Error Loading {page_name}\n\nCheck nextcloud_restore_gui.log for details.\n\nPlease restart the application.",
                            font=("Arial", 14, "bold"),
                            bg=self.theme_colors['bg'],
                            fg=self.theme_colors['error_fg'],
                            justify=tk.CENTER
                        )
                        error_label.pack(expand=True)
                        logger.info(f"{page_name}: Minimal error UI created successfully")
                    except Exception as final_error:
                        logger.error(f"{page_name}: Even minimal error UI failed: {final_error}")
        return wrapper
    return decorator

# --- Silent subprocess execution utilities ---
def get_subprocess_creation_flags():
    """
    Get the appropriate creation flags for subprocess to prevent console windows on Windows.
    Returns: creation flags for subprocess or 0 if not on Windows
    """
    if platform.system() == "Windows":
        # CREATE_NO_WINDOW flag prevents console window from appearing
        return 0x08000000  # CREATE_NO_WINDOW
    return 0

def run_docker_command_silent(cmd, timeout=10):
    """
    Run a Docker command silently (no console window on Windows).
    Args:
        cmd: Command as list or string
        timeout: Timeout in seconds
    Returns: subprocess.CompletedProcess result or None on error
    """
    try:
        creation_flags = get_subprocess_creation_flags()
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            creationflags=creation_flags,
            shell=isinstance(cmd, str)
        )
        return result
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"Docker command error: {e}")
        return None

def list_running_database_containers():
    """
    List all running database containers (MySQL, MariaDB, PostgreSQL).
    Returns: list of dicts with container info: {'name': str, 'image': str, 'type': str}
    """
    db_containers = []
    
    try:
        result = run_docker_command_silent(['docker', 'ps', '--format', '{{.Names}}|{{.Image}}'])
        if not result or result.returncode != 0:
            return db_containers
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('|')
            if len(parts) != 2:
                continue
            
            name, image = parts
            image_lower = image.lower()
            
            # Detect database type from image name
            if 'mysql' in image_lower and 'mariadb' not in image_lower:
                db_containers.append({'name': name, 'image': image, 'type': 'mysql'})
            elif 'mariadb' in image_lower:
                db_containers.append({'name': name, 'image': image, 'type': 'mariadb'})
            elif 'postgres' in image_lower:
                db_containers.append({'name': name, 'image': image, 'type': 'pgsql'})
    
    except Exception as e:
        print(f"Error listing database containers: {e}")
    
    return db_containers

def inspect_container_environment(container_name):
    """
    Inspect a container's environment variables to gather database info.
    Returns: dict with environment variables or empty dict on error
    """
    env_vars = {}
    
    try:
        result = run_docker_command_silent(
            ['docker', 'inspect', container_name, '--format', '{{range .Config.Env}}{{println .}}{{end}}']
        )
        
        if not result or result.returncode != 0:
            return env_vars
        
        for line in result.stdout.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    except Exception as e:
        print(f"Error inspecting container environment: {e}")
    
    return env_vars

def detect_db_from_container_inspection(nextcloud_container, db_containers):
    """
    Detect database type by inspecting running containers and their relationships.
    
    Args:
        nextcloud_container: Name of the Nextcloud container
        db_containers: List of database containers from list_running_database_containers()
    
    Returns: (dbtype, db_info) where dbtype is 'mysql', 'mariadb', 'pgsql' or None
             db_info is a dict with container details
    """
    # Strategy 1: Check Nextcloud container's config.php (existing method)
    dbtype_from_config, db_config = detect_database_type_from_container(nextcloud_container)
    
    if dbtype_from_config:
        # Try to match with running database containers
        for db_container in db_containers:
            if db_container['type'] == dbtype_from_config:
                print(f"✓ Matched database type {dbtype_from_config} with container {db_container['name']}")
                return dbtype_from_config, {
                    'container': db_container['name'],
                    'image': db_container['image'],
                    'config': db_config
                }
        
        # Config.php has dbtype but no matching container found
        # Return the dbtype anyway, it might be correct
        return dbtype_from_config, {'config': db_config}
    
    # Strategy 2: If config.php didn't work, check if there's only one DB container
    if len(db_containers) == 1:
        db_container = db_containers[0]
        dbtype = 'mysql' if db_container['type'] in ['mysql', 'mariadb'] else db_container['type']
        print(f"✓ Found single database container: {db_container['name']} ({db_container['type']})")
        
        # Inspect environment for additional info
        env_vars = inspect_container_environment(db_container['name'])
        
        return dbtype, {
            'container': db_container['name'],
            'image': db_container['image'],
            'env': env_vars
        }
    
    # Strategy 3: Multiple DB containers - check network connections
    if len(db_containers) > 1:
        # Get Nextcloud container's networks
        result = run_docker_command_silent(
            ['docker', 'inspect', nextcloud_container, '--format', '{{range $net, $config := .NetworkSettings.Networks}}{{$net}} {{end}}']
        )
        
        if result and result.returncode == 0:
            nc_networks = set(result.stdout.strip().split())
            
            # Check which DB container shares a network with Nextcloud
            for db_container in db_containers:
                result = run_docker_command_silent(
                    ['docker', 'inspect', db_container['name'], '--format', '{{range $net, $config := .NetworkSettings.Networks}}{{$net}} {{end}}']
                )
                
                if result and result.returncode == 0:
                    db_networks = set(result.stdout.strip().split())
                    shared_networks = nc_networks & db_networks
                    
                    if shared_networks:
                        dbtype = 'mysql' if db_container['type'] in ['mysql', 'mariadb'] else db_container['type']
                        print(f"✓ Found database container on shared network: {db_container['name']} ({db_container['type']})")
                        
                        env_vars = inspect_container_environment(db_container['name'])
                        
                        return dbtype, {
                            'container': db_container['name'],
                            'image': db_container['image'],
                            'networks': list(shared_networks),
                            'env': env_vars
                        }
    
    return None, None

def is_tool_installed(tool):
    try:
        creation_flags = get_subprocess_creation_flags()
        subprocess.run([tool, '--version'], check=True, stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, creationflags=creation_flags)
        return True
    except Exception:
        return False

def check_database_dump_utility(dbtype):
    """
    Check if the required database dump utility is available.
    Returns: (is_installed, utility_name) tuple
    """
    if dbtype in ['mysql', 'mariadb']:
        utility = 'mysqldump'
        installed = is_tool_installed(utility)
        return installed, utility
    elif dbtype == 'pgsql':
        utility = 'pg_dump'
        installed = is_tool_installed(utility)
        return installed, utility
    elif dbtype in ['sqlite', 'sqlite3']:
        # SQLite doesn't need external tools, database is in the data folder
        return True, 'sqlite'
    else:
        return False, 'unknown'

def prompt_install_database_utility(parent, dbtype, utility_name):
    """
    Prompt user to install the required database dump utility.
    Returns: True if user wants to retry, False to cancel
    """
    system = platform.system()
    
    if dbtype in ['mysql', 'mariadb']:
        instructions = {
            'Windows': (
                f"MySQL Client Tools (including {utility_name}) are required for backup.\n\n"
                "Installation options:\n"
                "1. Download MySQL Installer from: https://dev.mysql.com/downloads/installer/\n"
                "2. Or install via Chocolatey: choco install mysql\n"
                "3. Or use Docker: The utility is available inside MySQL/MariaDB containers\n\n"
                "After installation, restart the application."
            ),
            'Darwin': (
                f"MySQL Client Tools (including {utility_name}) are required for backup.\n\n"
                "Installation:\n"
                "• Install via Homebrew: brew install mysql-client\n"
                "• Or: brew install mysql\n\n"
                "After installation, restart the application."
            ),
            'Linux': (
                f"MySQL Client Tools (including {utility_name}) are required for backup.\n\n"
                "Installation:\n"
                "• Ubuntu/Debian: sudo apt-get install mysql-client\n"
                "• Fedora/RHEL: sudo dnf install mysql\n"
                "• Arch: sudo pacman -S mysql-clients\n\n"
                "After installation, restart the application."
            )
        }
    elif dbtype == 'pgsql':
        instructions = {
            'Windows': (
                f"PostgreSQL Client Tools (including {utility_name}) are required for backup.\n\n"
                "Installation options:\n"
                "1. Download PostgreSQL from: https://www.postgresql.org/download/windows/\n"
                "2. Or install via Chocolatey: choco install postgresql\n"
                "3. Or use Docker: The utility is available inside PostgreSQL containers\n\n"
                "After installation, restart the application."
            ),
            'Darwin': (
                f"PostgreSQL Client Tools (including {utility_name}) are required for backup.\n\n"
                "Installation:\n"
                "• Install via Homebrew: brew install postgresql\n\n"
                "After installation, restart the application."
            ),
            'Linux': (
                f"PostgreSQL Client Tools (including {utility_name}) are required for backup.\n\n"
                "Installation:\n"
                "• Ubuntu/Debian: sudo apt-get install postgresql-client\n"
                "• Fedora/RHEL: sudo dnf install postgresql\n"
                "• Arch: sudo pacman -S postgresql\n\n"
                "After installation, restart the application."
            )
        }
    else:
        instructions = {
            'Windows': f"Database utility '{utility_name}' is required but installation instructions are not available.",
            'Darwin': f"Database utility '{utility_name}' is required but installation instructions are not available.",
            'Linux': f"Database utility '{utility_name}' is required but installation instructions are not available."
        }
    
    instruction_text = instructions.get(system, instructions.get('Linux', ''))
    
    result = messagebox.askokcancel(
        "Database Utility Required",
        instruction_text + "\n\nClick OK after installing to retry, or Cancel to abort.",
        parent=parent
    )
    
    return result

def detect_docker_status():
    """
    Comprehensive Docker detection that checks installation and running status.
    Analyzes errors to provide specific, actionable feedback.
    
    Returns:
        dict with keys:
            - status: 'running', 'not_running', 'permission_denied', 'not_installed', 'error'
            - message: User-friendly message describing the status
            - suggested_action: Platform-specific instructions to resolve issues
            - stderr: Raw error output (if applicable)
    """
    try:
        creation_flags = get_subprocess_creation_flags()
        
        # Try to run 'docker ps' to check if Docker is running
        result = subprocess.run(
            ['docker', 'ps'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
            creationflags=creation_flags
        )
        
        # Success - Docker is running
        if result.returncode == 0:
            return {
                'status': 'running',
                'message': 'Docker is running',
                'suggested_action': None,
                'stderr': ''
            }
        
        # Docker command ran but failed - analyze stderr to determine why
        stderr_lower = result.stderr.lower()
        system = platform.system()
        
        # Check for permission denied
        if 'permission denied' in stderr_lower or 'access denied' in stderr_lower:
            if system == 'Windows':
                suggested_action = (
                    "Run this application as Administrator:\n"
                    "1. Right-click the application\n"
                    "2. Select 'Run as Administrator'\n\n"
                    "Or ensure Docker Desktop is running and you have proper permissions."
                )
            elif system == 'Linux':
                suggested_action = (
                    "Add your user to the docker group:\n"
                    "  sudo usermod -aG docker $(whoami)\n\n"
                    "Then log out and log back in for changes to take effect.\n\n"
                    "Alternatively, run with sudo (not recommended for GUI apps)."
                )
            else:  # macOS
                suggested_action = (
                    "Ensure Docker Desktop is running and you have proper permissions.\n"
                    "You may need to restart Docker Desktop."
                )
            
            return {
                'status': 'permission_denied',
                'message': 'Permission denied - insufficient privileges to access Docker',
                'suggested_action': suggested_action,
                'stderr': result.stderr
            }
        
        # Check for Docker not running / cannot connect
        if ('cannot connect' in stderr_lower or 
            'is not running' in stderr_lower or 
            'daemon' in stderr_lower or
            'connect' in stderr_lower):
            
            if system == 'Windows':
                suggested_action = (
                    "Start Docker Desktop:\n"
                    "1. Open Docker Desktop from the Start menu\n"
                    "2. Wait for Docker to fully start (watch the system tray icon)\n"
                    "3. Try again once Docker is running"
                )
            elif system == 'Darwin':  # macOS
                suggested_action = (
                    "Start Docker Desktop:\n"
                    "1. Open Docker Desktop from Applications\n"
                    "2. Wait for Docker to fully start (check menu bar icon)\n"
                    "3. Try again once Docker is running"
                )
            else:  # Linux
                suggested_action = (
                    "Start the Docker daemon:\n"
                    "  sudo systemctl start docker\n\n"
                    "To enable Docker to start automatically:\n"
                    "  sudo systemctl enable docker\n\n"
                    "Check Docker status:\n"
                    "  sudo systemctl status docker"
                )
            
            return {
                'status': 'not_running',
                'message': 'Docker is not running',
                'suggested_action': suggested_action,
                'stderr': result.stderr
            }
        
        # Unknown error from docker command
        return {
            'status': 'error',
            'message': 'Docker command failed with an unexpected error',
            'suggested_action': (
                f"Error output: {result.stderr}\n\n"
                "Try:\n"
                "1. Restarting Docker Desktop/daemon\n"
                "2. Checking Docker logs for more information\n"
                "3. Reinstalling Docker if the problem persists"
            ),
            'stderr': result.stderr
        }
        
    except FileNotFoundError:
        # Docker command not found - not installed or not in PATH
        system = platform.system()
        
        if system == 'Windows':
            suggested_action = (
                "Docker Desktop is not installed or not in your system PATH.\n\n"
                "To install Docker Desktop:\n"
                "1. Visit https://www.docker.com/products/docker-desktop/\n"
                "2. Download Docker Desktop for Windows\n"
                "3. Run the installer and follow the instructions\n"
                "4. Restart your computer after installation\n"
                "5. Launch Docker Desktop and wait for it to start"
            )
        elif system == 'Darwin':  # macOS
            suggested_action = (
                "Docker Desktop is not installed or not in your system PATH.\n\n"
                "To install Docker Desktop:\n"
                "1. Visit https://www.docker.com/products/docker-desktop/\n"
                "2. Download Docker Desktop for Mac\n"
                "3. Open the .dmg file and drag Docker to Applications\n"
                "4. Launch Docker Desktop from Applications\n"
                "5. Complete the first-time setup"
            )
        else:  # Linux
            suggested_action = (
                "Docker is not installed or not in your system PATH.\n\n"
                "To install Docker on Linux:\n"
                "  # Ubuntu/Debian:\n"
                "  sudo apt-get update\n"
                "  sudo apt-get install docker.io\n\n"
                "  # Fedora/RHEL:\n"
                "  sudo dnf install docker\n\n"
                "  # Arch Linux:\n"
                "  sudo pacman -S docker\n\n"
                "After installation, start and enable Docker:\n"
                "  sudo systemctl start docker\n"
                "  sudo systemctl enable docker"
            )
        
        return {
            'status': 'not_installed',
            'message': 'Docker is not installed or not found in system PATH',
            'suggested_action': suggested_action,
            'stderr': ''
        }
    
    except subprocess.TimeoutExpired:
        # Docker command timed out
        return {
            'status': 'error',
            'message': 'Docker command timed out',
            'suggested_action': (
                "The Docker command took too long to respond.\n\n"
                "This might indicate:\n"
                "1. Docker is starting up - wait a moment and try again\n"
                "2. Docker is experiencing issues - try restarting Docker\n"
                "3. System performance issues - check system resources"
            ),
            'stderr': ''
        }
    
    except Exception as e:
        # Unexpected error
        return {
            'status': 'error',
            'message': f'Unexpected error while checking Docker: {str(e)}',
            'suggested_action': (
                "An unexpected error occurred.\n\n"
                "Try:\n"
                "1. Restarting Docker\n"
                "2. Checking if Docker is properly installed\n"
                "3. Reviewing system logs for more information"
            ),
            'stderr': str(e)
        }

def is_docker_running():
    """
    Check if Docker daemon is running by attempting a simple Docker command.
    Returns: True if Docker is running, False otherwise
    
    Note: For detailed error information, use detect_docker_status() instead.
    """
    status = detect_docker_status()
    return status['status'] == 'running'

def check_nextcloud_ready(port, timeout=120):
    """
    Check if Nextcloud is ready by polling the HTTP endpoint.
    Returns: True if ready, False if timeout
    """
    import urllib.request
    import urllib.error
    import socket
    
    url = f"http://localhost:{port}"
    start_time = time.time()
    
    print(f"Checking if Nextcloud is ready at {url}...")
    
    while time.time() - start_time < timeout:
        try:
            # Try to connect to the Nextcloud service
            response = urllib.request.urlopen(url, timeout=5)
            # If we get any response, Nextcloud is at least responding
            print(f"✓ Nextcloud is responding (HTTP {response.getcode()})")
            return True
        except urllib.error.HTTPError as e:
            # HTTP errors (like 404, 500) still mean the server is up
            if e.code in [200, 302, 404, 500, 503]:
                print(f"✓ Nextcloud is responding (HTTP {e.code})")
                return True
        except (urllib.error.URLError, socket.timeout, ConnectionRefusedError, socket.error):
            # Connection refused or timeout - service not ready yet
            pass
        except Exception as e:
            print(f"Check error: {e}")
        
        time.sleep(2)
    
    print(f"✗ Nextcloud did not become ready within {timeout} seconds")
    return False

def get_docker_desktop_path():
    """
    Get the path to Docker Desktop executable based on the platform.
    Returns: Path to Docker Desktop or None if not found
    """
    system = platform.system()
    
    if system == "Windows":
        # Common Docker Desktop locations on Windows
        paths = [
            r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
            os.path.expandvars(r"%ProgramFiles%\Docker\Docker\Docker Desktop.exe"),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    elif system == "Darwin":  # macOS
        path = "/Applications/Docker.app"
        if os.path.exists(path):
            return path
    # Linux typically uses docker daemon, not Desktop
    return None

def start_docker_desktop():
    """
    Attempt to start Docker Desktop based on the platform.
    Starts Docker silently in the background with minimal window visibility.
    
    Note: Docker Desktop may still briefly show its window during startup as this
    is controlled by the Docker Desktop application itself. The flags used here
    minimize but may not completely eliminate window visibility.
    
    Returns: True if launch was attempted, False otherwise
    """
    docker_path = get_docker_desktop_path()
    if not docker_path:
        logger.debug("Docker Desktop path not found, cannot auto-start")
        return False
    
    try:
        system = platform.system()
        if system == "Windows":
            logger.info(f"Starting Docker Desktop on Windows silently: {docker_path}")
            # Use STARTUPINFO to start Docker Desktop minimized
            # Note: SW_HIDE (0) doesn't work well with Docker Desktop as it manages its own windows
            # SW_SHOWMINNOACTIVE (7) is more reliable - starts minimized without focus
            import subprocess
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 7  # SW_SHOWMINNOACTIVE - minimized, no activation
            creation_flags = get_subprocess_creation_flags()
            
            # Start Docker Desktop
            subprocess.Popen(
                [docker_path], 
                shell=False, 
                creationflags=creation_flags,
                startupinfo=startupinfo,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            logger.info("Docker Desktop started minimized. Window may briefly appear during startup.")
            
        elif system == "Darwin":  # macOS
            logger.info("Starting Docker Desktop on macOS in background")
            # Use -g flag to run in background without bringing the app to foreground
            # Use -j flag to hide the app from the Dock (may not work for all macOS versions)
            subprocess.Popen(
                ['open', '-g', '-j', '-a', 'Docker'],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            logger.info("Docker Desktop started in background. GUI managed by Docker Desktop itself.")
            
        return True
    except Exception as e:
        logger.error(f"Failed to start Docker Desktop: {e}")
        return False

def prompt_start_docker(parent):
    """
    Show a dialog prompting the user to start Docker with context-specific messages.
    Uses detect_docker_status() to show appropriate error messages and instructions.
    Returns: True if user wants to retry, False to cancel
    """
    # Get detailed Docker status
    docker_status = detect_docker_status()
    system = platform.system()
    docker_path = get_docker_desktop_path()
    
    # Determine dialog title and header based on status
    status_titles = {
        'not_installed': 'Docker Not Installed',
        'not_running': 'Docker Not Running',
        'permission_denied': 'Docker Permission Error',
        'error': 'Docker Error'
    }
    
    status_icons = {
        'not_installed': '📦',
        'not_running': '⚠',
        'permission_denied': '🔒',
        'error': '❌'
    }
    
    dialog_title = status_titles.get(docker_status['status'], 'Docker Issue')
    header_icon = status_icons.get(docker_status['status'], '⚠')
    
    dialog = tk.Toplevel(parent)
    dialog.title(dialog_title)
    dialog.geometry("650x450")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (650 // 2)
    y = (dialog.winfo_screenheight() // 2) - (450 // 2)
    dialog.geometry(f"650x450+{x}+{y}")
    
    # Header with appropriate color based on error type
    header_colors = {
        'not_installed': '#e67e22',  # Orange for not installed
        'not_running': '#e74c3c',     # Red for not running
        'permission_denied': '#c0392b',  # Dark red for permission
        'error': '#95a5a6'            # Gray for generic error
    }
    header_bg = header_colors.get(docker_status['status'], '#e74c3c')
    
    header_frame = tk.Frame(dialog, bg=header_bg, height=60)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    tk.Label(
        header_frame,
        text=f"{header_icon} {dialog_title}",
        font=("Arial", 16, "bold"),
        bg=header_bg,
        fg="white"
    ).pack(pady=15)
    
    # Content
    content_frame = tk.Frame(dialog)
    content_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    # Show status message
    tk.Label(
        content_frame,
        text=docker_status['message'],
        font=("Arial", 13, "bold"),
        wraplength=590,
        justify="left"
    ).pack(pady=(5, 15))
    
    # Show suggested action in a scrollable text area for long messages
    action_frame = tk.Frame(content_frame, relief="solid", borderwidth=1)
    action_frame.pack(fill="both", expand=True, pady=10)
    
    action_text = tk.Text(
        action_frame,
        font=("Arial", 10),
        wrap="word",
        height=10,
        bg="#f8f9fa",
        relief="flat",
        padx=10,
        pady=10
    )
    action_scrollbar = tk.Scrollbar(action_frame, command=action_text.yview)
    action_text.config(yscrollcommand=action_scrollbar.set)
    
    action_scrollbar.pack(side="right", fill="y")
    action_text.pack(side="left", fill="both", expand=True)
    
    if docker_status['suggested_action']:
        action_text.insert("1.0", docker_status['suggested_action'])
    action_text.config(state="disabled")  # Make read-only
    
    result = {"retry": False}
    
    def on_start_docker():
        if start_docker_desktop():
            tk.Label(
                content_frame,
                text="\n✓ Docker Desktop is starting...\nPlease wait 10-20 seconds, then click 'Retry'.",
                font=("Arial", 11),
                fg="#27ae60"
            ).pack(pady=5)
            # Wait a bit for Docker to start
            dialog.after(2000, lambda: None)
        else:
            messagebox.showerror(
                "Error",
                "Could not start Docker Desktop automatically.\nPlease start it manually.",
                parent=dialog
            )
    
    def on_retry():
        result["retry"] = True
        dialog.destroy()
    
    def on_cancel():
        result["retry"] = False
        dialog.destroy()
    
    def on_open_website():
        """Open Docker download website"""
        webbrowser.open(DOCKER_INSTALLER_URL)
    
    # Buttons - context-specific based on Docker status
    button_frame = tk.Frame(content_frame)
    button_frame.pack(pady=20)
    
    # Show different buttons based on status
    if docker_status['status'] == 'not_installed':
        # For not installed, show "Download Docker" button
        tk.Button(
            button_frame,
            text="Download Docker",
            font=("Arial", 12),
            command=on_open_website,
            bg="#e67e22",
            fg="white",
            width=20
        ).pack(side="left", padx=5)
    elif docker_status['status'] == 'not_running' and docker_path:
        # For not running with Docker Desktop installed, show "Start Docker Desktop"
        tk.Button(
            button_frame,
            text="Start Docker Desktop",
            font=("Arial", 12),
            command=on_start_docker,
            bg="#3daee9",
            fg="white",
            width=20
        ).pack(side="left", padx=5)
    
    # Always show Retry button (except for not_installed status)
    if docker_status['status'] != 'not_installed':
        tk.Button(
            button_frame,
            text="Retry",
            font=("Arial", 12),
            command=on_retry,
            bg="#27ae60",
            fg="white",
            width=15
        ).pack(side="left", padx=5)
    
    tk.Button(
        button_frame,
        text="Cancel",
        font=("Arial", 12),
        command=on_cancel,
        width=15
    ).pack(side="left", padx=5)
    
    parent.wait_window(dialog)
    return result["retry"]

def prompt_install_docker_link(parent, status_label, install_callback):
    for widget in parent.body_frame.winfo_children():
        widget.destroy()
    status_label.config(text="Docker is required to run Nextcloud. Please install Docker Desktop.")
    install_frame = tk.Frame(parent.body_frame)
    install_frame.pack(pady=30)
    tk.Label(
        install_frame,
        text="Docker allows this utility to run Nextcloud in containers.\n"
             "Please download and install Docker Desktop from the official site below, then click 'Continue' when ready.",
        font=("Arial", 13), wraplength=500, justify="left"
    ).pack(pady=10)
    def open_site():
        webbrowser.open(DOCKER_INSTALLER_URL)
    tk.Button(install_frame, text="Open Docker Website", font=("Arial", 12), command=open_site, bg="#3daee9", fg="white", width=22).pack(pady=8)
    tk.Button(install_frame, text="Continue", font=("Arial", 12), command=install_callback, width=22).pack(pady=8)

def prompt_install_gpg(parent):
    win = tk.Toplevel(parent)
    win.title("GPG Required")
    win.geometry("500x320")
    msg = ("GPG (GNU Privacy Guard) is required to encrypt or decrypt your backup archive.\n\n"
           "GPG makes sure your backup remains secure and private.\n\n"
           "Would you like to install Gpg4win now?")
    tk.Label(win, text=msg, wraplength=480, justify="left").pack(pady=15)
    def start_install():
        win.destroy()
        webbrowser.open(GPG_DOWNLOAD_URL)
    tk.Button(win, text="Install Gpg4win", command=start_install).pack(pady=10)
    tk.Button(win, text="Cancel", command=win.destroy).pack()
    win.transient(parent)
    win.grab_set()
    parent.wait_window(win)

def encrypt_file_gpg(unencrypted_path, encrypted_path, passphrase):
    creation_flags = get_subprocess_creation_flags()
    result = subprocess.run([
        'gpg', '--batch', '--yes', '--passphrase', passphrase,
        '-c', '--cipher-algo', 'AES256',
        '-o', encrypted_path, unencrypted_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flags)
    if result.returncode != 0:
        raise Exception(result.stderr.decode() or "GPG encryption failed")

def decrypt_file_gpg(encrypted_path, decrypted_path, passphrase):
    creation_flags = get_subprocess_creation_flags()
    result = subprocess.run([
        'gpg', '--batch', '--yes', '--passphrase', passphrase,
        '-o', decrypted_path, '-d', encrypted_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flags)
    if result.returncode != 0:
        raise Exception(result.stderr.decode() or "GPG decryption failed")

def check_gpg_available():
    """
    Check if GPG is available on the system.
    
    Returns:
        tuple: (bool, str) - (is_available, error_message)
    """
    try:
        creation_flags = get_subprocess_creation_flags()
        result = subprocess.run(
            ['gpg', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            creationflags=creation_flags
        )
        if result.returncode == 0:
            logger.info("GPG is available on the system")
            return True, ""
        else:
            logger.warning("GPG command failed")
            return False, "GPG command failed to execute"
    except FileNotFoundError:
        logger.error("GPG not found on system")
        return False, "GPG (GNU Privacy Guard) is not installed"
    except subprocess.TimeoutExpired:
        logger.error("GPG check timed out")
        return False, "GPG check timed out"
    except Exception as e:
        logger.error(f"Error checking GPG availability: {e}")
        return False, f"Error checking GPG: {str(e)}"

def check_tarfile_available():
    """
    Check if tarfile module can open tar.gz archives.
    
    Returns:
        tuple: (bool, str) - (is_available, error_message)
    """
    try:
        # tarfile is a standard library module, but verify it works
        import tarfile
        # Try to check if it supports gzip
        if not hasattr(tarfile, 'open'):
            return False, "tarfile module is not properly available"
        logger.info("tarfile module is available")
        return True, ""
    except ImportError:
        logger.error("tarfile module not available")
        return False, "Python tarfile module is not available"
    except Exception as e:
        logger.error(f"Error checking tarfile availability: {e}")
        return False, f"Error checking tarfile: {str(e)}"

def show_extraction_error_dialog(parent, missing_tool, backup_path):
    """
    Show a user-friendly error dialog when extraction tools are missing.
    
    Args:
        parent: Parent window for the dialog
        missing_tool: The missing tool ('gpg', 'tarfile', etc.)
        backup_path: Path to the backup file that failed to extract
    
    Returns:
        str: User action ('install', 'cancel', 'continue')
    """
    result = ['cancel']  # Default to cancel
    
    def show_dialog():
        win = tk.Toplevel(parent)
        win.title("Extraction Tool Required")
        win.geometry("550x400")
        win.configure(bg='white')
        
        # Main message frame
        msg_frame = tk.Frame(win, bg='white')
        msg_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            msg_frame,
            text="⚠️ Cannot Extract Backup Archive",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#d32f2f'
        )
        title_label.pack(pady=(0, 15))
        
        # Prepare message based on missing tool
        if missing_tool == 'gpg':
            tool_name = "GPG (GNU Privacy Guard)"
            explanation = (
                "Your backup file is encrypted (.gpg extension), but GPG is not installed.\n\n"
                "GPG is required to decrypt encrypted backup archives.\n\n"
                "Without GPG, the restore wizard cannot access the backup contents."
            )
            install_instructions = (
                "📥 Installation Options:\n\n"
                "• Click 'Install GPG' to download Gpg4win (Windows)\n"
                "• Linux users: Run 'sudo apt install gpg' (Ubuntu/Debian)\n"
                "  or 'sudo yum install gnupg2' (RHEL/CentOS)\n"
                "• Mac users: Run 'brew install gnupg'"
            )
            can_auto_install = platform.system() == 'Windows'
        elif missing_tool == 'tarfile':
            tool_name = "Python tarfile module"
            explanation = (
                "The Python tarfile module required for extracting .tar.gz archives\n"
                "is not available or not functioning properly.\n\n"
                "This is unusual as tarfile is part of Python's standard library."
            )
            install_instructions = (
                "📥 Troubleshooting:\n\n"
                "• Ensure you're using a standard Python installation\n"
                "• Try reinstalling Python from python.org\n"
                "• Contact support if the issue persists"
            )
            can_auto_install = False
        else:
            tool_name = missing_tool
            explanation = (
                f"The required tool '{missing_tool}' is not available.\n\n"
                "This tool is needed to extract your backup archive."
            )
            install_instructions = (
                "📥 Please install the required tool manually and try again."
            )
            can_auto_install = False
        
        # Explanation
        msg_label = tk.Label(
            msg_frame,
            text=f"Required Tool: {tool_name}\n\n{explanation}",
            font=("Arial", 10),
            bg='white',
            justify="left",
            wraplength=500
        )
        msg_label.pack(pady=(0, 15), anchor="w")
        
        # Backup file info
        backup_info = tk.Label(
            msg_frame,
            text=f"Backup File: {os.path.basename(backup_path)}",
            font=("Arial", 9),
            bg='#f5f5f5',
            fg='#666',
            anchor="w",
            padx=10,
            pady=5
        )
        backup_info.pack(fill="x", pady=(0, 15))
        
        # Installation instructions
        instructions_label = tk.Label(
            msg_frame,
            text=install_instructions,
            font=("Arial", 9),
            bg='#e3f2fd',
            fg='#1565c0',
            justify="left",
            wraplength=500,
            padx=10,
            pady=10
        )
        instructions_label.pack(fill="x", pady=(0, 20))
        
        # Buttons frame
        btn_frame = tk.Frame(msg_frame, bg='white')
        btn_frame.pack(fill="x")
        
        def on_install():
            result[0] = 'install'
            win.destroy()
        
        def on_cancel():
            result[0] = 'cancel'
            win.destroy()
        
        # Show install button only for tools that can be auto-installed
        if can_auto_install:
            install_btn = tk.Button(
                btn_frame,
                text="Install GPG",
                font=("Arial", 11, "bold"),
                bg='#4caf50',
                fg='white',
                width=15,
                command=on_install,
                cursor="hand2"
            )
            install_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 11),
            bg='#f5f5f5',
            fg='#333',
            width=15,
            command=on_cancel,
            cursor="hand2"
        )
        cancel_btn.pack(side="left", padx=5)
        
        # Center the window
        win.transient(parent)
        win.grab_set()
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f'+{x}+{y}')
        
        parent.wait_window(win)
    
    # Show dialog in main thread
    parent.after(0, show_dialog)
    # Wait for dialog to complete
    import time
    while result[0] == 'cancel' and parent.winfo_exists():
        parent.update()
        time.sleep(0.1)
        break
    
    return result[0]

def thread_safe_askstring(parent, title, prompt, **kwargs):
    """
    Thread-safe wrapper for simpledialog.askstring.
    Can be called from any thread - ensures dialog is shown in main thread.
    """
    result = [None]  # Use list to store result (mutable)
    event = threading.Event()
    
    def _ask():
        result[0] = simpledialog.askstring(title, prompt, **kwargs)
        event.set()
    
    parent.after(0, _ask)
    event.wait()
    return result[0]

def find_config_php_recursive(directory):
    """
    Recursively search for config.php in any subdirectory.
    Returns the full path to config.php if found, None otherwise.
    """
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename == 'config.php':
                    # Found config.php - verify it's in a config directory or contains database config
                    config_path = os.path.join(root, filename)
                    # Quick check if this looks like a Nextcloud config.php
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            content = f.read(100)  # Read first 100 chars
                            if '$CONFIG' in content or 'dbtype' in content:
                                print(f"Found config.php at: {config_path}")
                                return config_path
                    except Exception:
                        continue
        print(f"config.php not found in {directory}")
        return None
    except Exception as e:
        print(f"Error searching for config.php: {e}")
        return None

def detect_database_type_from_container(container_name):
    """
    Detect database type from a running Nextcloud container by reading its config.php.
    Returns: (dbtype, db_config_dict) or (None, None) if detection fails
    dbtype can be: 'sqlite', 'pgsql', 'mysql'
    """
    try:
        # Try to read config.php from the running container (silently)
        result = run_docker_command_silent(
            f'docker exec {container_name} cat /var/www/html/config/config.php'
        )
        
        if not result or result.returncode != 0:
            if result:
                print(f"Could not read config.php from container: {result.stderr}")
            return None, None
        
        content = result.stdout
        
        # Look for 'dbtype' => 'value' pattern (with single or double quotes)
        dbtype_match = re.search(r"['\"]dbtype['\"] => ['\"]([^'\"]+)['\"]", content)
        if not dbtype_match:
            print("Could not find dbtype in config.php")
            return None, None
        
        dbtype = dbtype_match.group(1).lower()
        
        # Normalize sqlite3 to sqlite for consistent handling
        if dbtype == 'sqlite3':
            dbtype = 'sqlite'
        
        # Also extract other DB config for reference
        db_config = {'dbtype': dbtype}
        
        # Extract dbname
        dbname_match = re.search(r"['\"]dbname['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbname_match:
            db_config['dbname'] = dbname_match.group(1)
        
        # Extract dbuser
        dbuser_match = re.search(r"['\"]dbuser['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbuser_match:
            db_config['dbuser'] = dbuser_match.group(1)
        
        # Extract dbhost
        dbhost_match = re.search(r"['\"]dbhost['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbhost_match:
            db_config['dbhost'] = dbhost_match.group(1)
        
        print(f"✓ Detected database type from container: {dbtype}")
        return dbtype, db_config
        
    except subprocess.TimeoutExpired:
        print("Timeout reading config.php from container")
        return None, None
    except Exception as e:
        print(f"Error detecting database type from container: {e}")
        return None, None

def parse_config_php_dbtype(config_php_path):
    """
    Parse config.php file and extract the database type.
    Returns: (dbtype, db_config_dict) or (None, None) if parsing fails
    dbtype can be: 'sqlite', 'pgsql', 'mysql'
    """
    try:
        if not os.path.exists(config_php_path):
            return None, None
        
        with open(config_php_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for 'dbtype' => 'value' pattern (with single or double quotes)
        dbtype_match = re.search(r"['\"]dbtype['\"] => ['\"]([^'\"]+)['\"]", content)
        if not dbtype_match:
            return None, None
        
        dbtype = dbtype_match.group(1).lower()
        
        # Normalize sqlite3 to sqlite for consistent handling
        if dbtype == 'sqlite3':
            dbtype = 'sqlite'
        
        # Also extract other DB config for reference
        db_config = {'dbtype': dbtype}
        
        # Extract dbname
        dbname_match = re.search(r"['\"]dbname['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbname_match:
            db_config['dbname'] = dbname_match.group(1)
        
        # Extract dbuser
        dbuser_match = re.search(r"['\"]dbuser['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbuser_match:
            db_config['dbuser'] = dbuser_match.group(1)
        
        # Extract dbhost
        dbhost_match = re.search(r"['\"]dbhost['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbhost_match:
            db_config['dbhost'] = dbhost_match.group(1)
        
        return dbtype, db_config
    except Exception as e:
        print(f"Error parsing config.php: {e}")
        return None, None

def parse_config_php_full(config_php_path):
    """
    Parse config.php file and extract all relevant settings for Docker Compose generation.
    Returns: dict with config settings or None if parsing fails
    """
    try:
        if not os.path.exists(config_php_path):
            return None
        
        with open(config_php_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        config = {}
        
        # Extract database settings
        dbtype_match = re.search(r"['\"]dbtype['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbtype_match:
            config['dbtype'] = dbtype_match.group(1).lower()
        
        dbname_match = re.search(r"['\"]dbname['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbname_match:
            config['dbname'] = dbname_match.group(1)
        
        dbuser_match = re.search(r"['\"]dbuser['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbuser_match:
            config['dbuser'] = dbuser_match.group(1)
        
        dbpassword_match = re.search(r"['\"]dbpassword['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbpassword_match:
            config['dbpassword'] = dbpassword_match.group(1)
        
        dbhost_match = re.search(r"['\"]dbhost['\"] => ['\"]([^'\"]+)['\"]", content)
        if dbhost_match:
            config['dbhost'] = dbhost_match.group(1)
        
        dbport_match = re.search(r"['\"]dbport['\"] => ['\"]?([^'\"]+)['\"]?", content)
        if dbport_match:
            config['dbport'] = dbport_match.group(1)
        
        # Extract data directory
        datadirectory_match = re.search(r"['\"]datadirectory['\"] => ['\"]([^'\"]+)['\"]", content)
        if datadirectory_match:
            config['datadirectory'] = datadirectory_match.group(1)
        
        # Extract trusted domains (array format)
        trusted_domains = []
        trusted_domains_pattern = r"['\"]trusted_domains['\"]\s*=>\s*array\s*\((.*?)\)"
        td_match = re.search(trusted_domains_pattern, content, re.DOTALL)
        if td_match:
            domains_str = td_match.group(1)
            # Extract individual domain entries
            domain_entries = re.findall(r"['\"]([^'\"]+)['\"]", domains_str)
            trusted_domains = domain_entries
        config['trusted_domains'] = trusted_domains
        
        return config
    except Exception as e:
        print(f"Error parsing full config.php: {e}")
        return None

def detect_docker_compose_usage():
    """
    Detect if Docker Compose was used to start the current containers.
    Returns: (is_compose, compose_file_path) tuple
    """
    try:
        # Check if docker-compose.yml exists in current directory
        compose_files = ['docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml']
        for filename in compose_files:
            if os.path.exists(filename):
                print(f"✓ Found Docker Compose file: {filename}")
                return True, filename
        
        # Check running containers for Docker Compose labels
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Labels}}'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if 'com.docker.compose' in line:
                    print("✓ Detected Docker Compose labels on running containers")
                    return True, None
        
        return False, None
    except Exception as e:
        print(f"Error detecting Docker Compose usage: {e}")
        return False, None

def generate_docker_compose_yml(config, nextcloud_port=8080, db_port=5432):
    """
    Generate docker-compose.yml content based on config.php settings.
    
    Args:
        config: dict with config.php settings
        nextcloud_port: port to expose Nextcloud on
        db_port: port to expose database on (if applicable)
    
    Returns:
        str: docker-compose.yml content
    """
    dbtype = config.get('dbtype', 'pgsql')
    dbname = config.get('dbname', 'nextcloud')
    dbuser = config.get('dbuser', 'nextcloud')
    dbpassword = config.get('dbpassword', 'changeme')
    datadirectory = config.get('datadirectory', '/var/www/html/data')
    trusted_domains = config.get('trusted_domains', ['localhost'])
    
    # Determine database service configuration
    if dbtype == 'sqlite':
        # SQLite - no separate database service needed
        compose_content = f"""version: '3.8'

services:
  nextcloud:
    image: nextcloud
    container_name: nextcloud-app
    ports:
      - "{nextcloud_port}:80"
    volumes:
      - ./nextcloud-data:/var/www/html
    restart: unless-stopped
    environment:
      - SQLITE_DATABASE={dbname}
"""
    elif dbtype in ['mysql', 'mariadb']:
        # MySQL/MariaDB
        compose_content = f"""version: '3.8'

services:
  db:
    image: mariadb:10.11
    container_name: nextcloud-db
    restart: unless-stopped
    command: --transaction-isolation=READ-COMMITTED --log-bin=binlog --binlog-format=ROW
    volumes:
      - ./db-data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD={dbpassword}
      - MYSQL_PASSWORD={dbpassword}
      - MYSQL_DATABASE={dbname}
      - MYSQL_USER={dbuser}
    ports:
      - "{db_port}:3306"

  nextcloud:
    image: nextcloud
    container_name: nextcloud-app
    restart: unless-stopped
    ports:
      - "{nextcloud_port}:80"
    volumes:
      - ./nextcloud-data:/var/www/html
    environment:
      - MYSQL_PASSWORD={dbpassword}
      - MYSQL_DATABASE={dbname}
      - MYSQL_USER={dbuser}
      - MYSQL_HOST=db
    depends_on:
      - db
"""
    else:  # PostgreSQL
        compose_content = f"""version: '3.8'

services:
  db:
    image: postgres:15
    container_name: nextcloud-db
    restart: unless-stopped
    volumes:
      - ./db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD={dbpassword}
      - POSTGRES_DB={dbname}
      - POSTGRES_USER={dbuser}
    ports:
      - "{db_port}:5432"

  nextcloud:
    image: nextcloud
    container_name: nextcloud-app
    restart: unless-stopped
    ports:
      - "{nextcloud_port}:80"
    volumes:
      - ./nextcloud-data:/var/www/html
    environment:
      - POSTGRES_PASSWORD={dbpassword}
      - POSTGRES_DB={dbname}
      - POSTGRES_USER={dbuser}
      - POSTGRES_HOST=db
    depends_on:
      - db
"""
    
    # Add comments about configuration
    header = f"""# Docker Compose configuration for Nextcloud
# Generated based on config.php settings from backup
#
# Detected configuration:
#   - Database type: {dbtype}
#   - Database name: {dbname}
#   - Data directory: {datadirectory}
#   - Trusted domains: {', '.join(trusted_domains)}
#
# IMPORTANT: Ensure the following directories exist before starting:
#   - ./nextcloud-data (will contain Nextcloud files)
"""
    if dbtype not in ['sqlite', 'sqlite3']:
        header += "#   - ./db-data (will contain database files)\n"
    
    header += "#\n# To start: docker-compose up -d\n# To stop: docker-compose down\n\n"
    
    return header + compose_content

def detect_required_host_folders(config_php_path=None, compose_file_path=None, extract_dir=None):
    """
    Detect required host folders based on config.php and docker-compose.yml.
    
    Args:
        config_php_path: Path to config.php file (optional)
        compose_file_path: Path to docker-compose.yml file (optional)
        extract_dir: Path to extracted backup directory (optional)
    
    Returns:
        dict: Dictionary with folder information
            {
                'nextcloud_data': './nextcloud-data',  # Main volume mount
                'db_data': './db-data',  # Database volume mount (if applicable)
                'extracted_folders': ['config', 'data', 'apps', 'custom_apps']  # Folders in backup
            }
    """
    folders = {
        'nextcloud_data': './nextcloud-data',
        'db_data': None,
        'extracted_folders': []
    }
    
    # Detect database type from config.php to determine if db_data is needed
    dbtype = None
    if config_php_path and os.path.exists(config_php_path):
        config = parse_config_php_full(config_php_path)
        if config:
            dbtype = config.get('dbtype', '').lower()
            
            # If not SQLite, we need a database data folder
            if dbtype and dbtype not in ['sqlite', 'sqlite3']:
                folders['db_data'] = './db-data'
    
    # Check for folders that exist in the extracted backup
    if extract_dir and os.path.exists(extract_dir):
        standard_folders = ['config', 'data', 'apps', 'custom_apps']
        for folder in standard_folders:
            folder_path = os.path.join(extract_dir, folder)
            if os.path.isdir(folder_path):
                folders['extracted_folders'].append(folder)
    
    # Parse docker-compose.yml if it exists to detect custom volume mappings
    if compose_file_path and os.path.exists(compose_file_path):
        try:
            with open(compose_file_path, 'r') as f:
                content = f.read()
                
            # Look for volume mappings like ./nextcloud-data:/var/www/html
            volume_pattern = r'\s+-\s+\./([\w\-]+):/var/www/html'
            match = re.search(volume_pattern, content)
            if match:
                folders['nextcloud_data'] = f'./{match.group(1)}'
            
            # Look for database volume mappings
            db_volume_patterns = [
                r'\s+-\s+\./([\w\-]+):/var/lib/postgresql/data',  # PostgreSQL
                r'\s+-\s+\./([\w\-]+):/var/lib/mysql'  # MySQL/MariaDB
            ]
            for pattern in db_volume_patterns:
                match = re.search(pattern, content)
                if match:
                    folders['db_data'] = f'./{match.group(1)}'
                    break
        except Exception as e:
            print(f"Warning: Could not parse docker-compose.yml: {e}")
    
    return folders

def create_required_host_folders(folders_dict):
    """
    Create required host folders with proper error handling.
    
    Args:
        folders_dict: Dictionary from detect_required_host_folders()
    
    Returns:
        tuple: (success: bool, created: list, existing: list, errors: list)
    """
    created = []
    existing = []
    errors = []
    
    # Create main nextcloud data folder
    nextcloud_data = folders_dict.get('nextcloud_data')
    if nextcloud_data:
        try:
            if os.path.exists(nextcloud_data):
                existing.append(nextcloud_data)
            else:
                os.makedirs(nextcloud_data, mode=0o755, exist_ok=True)
                created.append(nextcloud_data)
                print(f"✓ Created folder: {nextcloud_data}")
        except Exception as e:
            error_msg = f"Failed to create {nextcloud_data}: {e}"
            errors.append(error_msg)
            print(f"✗ {error_msg}")
    
    # Create database data folder if needed
    db_data = folders_dict.get('db_data')
    if db_data:
        try:
            if os.path.exists(db_data):
                existing.append(db_data)
            else:
                os.makedirs(db_data, mode=0o755, exist_ok=True)
                created.append(db_data)
                print(f"✓ Created folder: {db_data}")
        except Exception as e:
            error_msg = f"Failed to create {db_data}: {e}"
            errors.append(error_msg)
            print(f"✗ {error_msg}")
    
    success = len(errors) == 0
    return success, created, existing, errors

def thread_safe_askinteger(parent, title, prompt, **kwargs):
    """
    Thread-safe wrapper for simpledialog.askinteger.
    Can be called from any thread - ensures dialog is shown in main thread.
    """
    result = [None]  # Use list to store result (mutable)
    event = threading.Event()
    
    def _ask():
        result[0] = simpledialog.askinteger(title, prompt, **kwargs)
        event.set()
    
    parent.after(0, _ask)
    event.wait()
    return result[0]

def get_nextcloud_container_name():
    try:
        result = run_docker_command_silent(['docker', 'ps', '--format', '{{.Names}} {{.Image}}'])
        if not result or result.returncode != 0:
            return None
        for line in result.stdout.strip().split('\n'):
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            name, image = parts
            if NEXTCLOUD_IMAGE in image.lower() or name == NEXTCLOUD_CONTAINER_NAME:
                return name
    except Exception:
        pass
    return None

def get_postgres_container_name():
    try:
        result = run_docker_command_silent(['docker', 'ps', '--format', '{{.Names}} {{.Image}}'])
        if not result or result.returncode != 0:
            return None
        for line in result.stdout.strip().split('\n'):
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            name, image = parts
            if POSTGRES_IMAGE in image and (name == POSTGRES_CONTAINER_NAME or "postgres" in image):
                return name
    except Exception:
        pass
    return None

def check_container_network(container_name, network_name="bridge"):
    """Check if a container is connected to a specific network"""
    try:
        result = run_docker_command_silent(
            ['docker', 'inspect', container_name, '--format', '{{range $net, $config := .NetworkSettings.Networks}}{{$net}} {{end}}']
        )
        if result and result.returncode == 0:
            networks = result.stdout.strip().split()
            return network_name in networks
    except Exception as e:
        print(f"Error checking container network: {e}")
    return False

def attach_container_to_network(container_name, network_name="bridge"):
    """Attach a container to a specific network with error handling"""
    try:
        # First check if already connected
        if check_container_network(container_name, network_name):
            print(f"Container {container_name} is already connected to {network_name} network")
            return True
        
        # Try to connect the container to the network
        result = run_docker_command_silent(
            ['docker', 'network', 'connect', network_name, container_name]
        )
        
        if result.returncode == 0:
            print(f"Successfully attached {container_name} to {network_name} network")
            return True
        else:
            print(f"Failed to attach {container_name} to {network_name} network: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error attaching container to network: {e}")
        return False

def get_nextcloud_port():
    """
    Detect the port mapping for the Nextcloud container.
    Returns the host port that maps to container port 80, or None if not found.
    """
    try:
        container_name = get_nextcloud_container_name()
        if not container_name:
            return None
        
        # Get port mappings from docker inspect
        result = run_docker_command_silent(
            ['docker', 'inspect', container_name, '--format', '{{range $p, $conf := .NetworkSettings.Ports}}{{if eq $p "80/tcp"}}{{(index $conf 0).HostPort}}{{end}}{{end}}']
        )
        
        if result and result.returncode == 0 and result.stdout.strip():
            port = result.stdout.strip()
            if port.isdigit():
                return int(port)
        
        # Fallback: try docker port command
        result = run_docker_command_silent(
            ['docker', 'port', container_name, '80']
        )
        
        if result and result.returncode == 0 and result.stdout.strip():
            # Output format: "0.0.0.0:8080" or ":::8080"
            port_mapping = result.stdout.strip()
            if ':' in port_mapping:
                port = port_mapping.split(':')[-1]
                if port.isdigit():
                    return int(port)
    
    except Exception as e:
        logger.error(f"Error detecting Nextcloud port: {e}")
    
    return None

def setup_tailscale_serve_startup(port, enable=True):
    """
    Set up automatic 'tailscale serve' to run at system startup.
    
    Args:
        port: The port number to serve (e.g., 8080)
        enable: If True, enable startup; if False, disable/remove startup
    
    Returns:
        tuple: (success: bool, message: str)
    """
    system = platform.system()
    
    try:
        tailscale_path = find_tailscale_exe() if system == "Windows" else "tailscale"
        if system == "Windows" and not tailscale_path:
            return False, "Tailscale executable not found"
        
        serve_cmd = f'"{tailscale_path}" serve --bg --https=443 http://localhost:{port}' if system == "Windows" else f'tailscale serve --bg --https=443 http://localhost:{port}'
        
        if system == "Windows":
            return _setup_windows_task_scheduler(tailscale_path, port, enable)
        elif system == "Linux":
            return _setup_linux_systemd_service(port, enable)
        elif system == "Darwin":
            return _setup_macos_launchagent(port, enable)
        else:
            return False, f"Unsupported platform: {system}"
    
    except Exception as e:
        logger.error(f"Error setting up tailscale serve startup: {e}")
        return False, f"Error: {str(e)}"

def _setup_windows_task_scheduler(tailscale_path, port, enable):
    """Set up Windows Task Scheduler for tailscale serve"""
    task_name = "NextcloudTailscaleServe"
    
    try:
        if enable:
            # Create the task
            # Use PowerShell to create a more reliable scheduled task
            # The task runs at logon with highest privileges and hidden window
            ps_script = f'''
$action = New-ScheduledTaskAction -Execute '"{tailscale_path}"' -Argument 'serve --bg --https=443 http://localhost:{port}'
$trigger = New-ScheduledTaskTrigger -AtLogon
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden
Register-ScheduledTask -TaskName '{task_name}' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
'''
            
            creation_flags = get_subprocess_creation_flags()
            result = subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=creation_flags
            )
            
            if result.returncode == 0:
                logger.info(f"Windows scheduled task '{task_name}' created successfully")
                return True, f"Auto-start configured successfully. Tailscale will serve on port {port} at login."
            else:
                logger.error(f"Failed to create scheduled task: {result.stderr}")
                return False, f"Failed to create scheduled task: {result.stderr}"
        else:
            # Delete the task
            creation_flags = get_subprocess_creation_flags()
            result = subprocess.run(
                ['schtasks', '/Delete', '/TN', task_name, '/F'],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=creation_flags
            )
            
            if result.returncode == 0:
                logger.info(f"Windows scheduled task '{task_name}' deleted successfully")
                return True, "Auto-start disabled successfully."
            else:
                # Task might not exist, which is fine
                return True, "Auto-start disabled (task may not have existed)."
    
    except Exception as e:
        logger.error(f"Error managing Windows scheduled task: {e}")
        return False, f"Error: {str(e)}"

def _setup_linux_systemd_service(port, enable):
    """Set up Linux systemd service for tailscale serve"""
    service_name = "nextcloud-tailscale-serve.service"
    service_path = f"/etc/systemd/system/{service_name}"
    
    try:
        if enable:
            # Create systemd service file
            service_content = f"""[Unit]
Description=Tailscale Serve for Nextcloud
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/tailscale serve --bg --https=443 http://localhost:{port}
ExecStop=/usr/bin/tailscale serve reset
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
            
            # Write service file (requires sudo)
            temp_file = f"/tmp/{service_name}"
            with open(temp_file, 'w') as f:
                f.write(service_content)
            
            # Move to systemd directory and enable service
            commands = [
                ['sudo', 'mv', temp_file, service_path],
                ['sudo', 'chmod', '644', service_path],
                ['sudo', 'systemctl', 'daemon-reload'],
                ['sudo', 'systemctl', 'enable', service_name],
                ['sudo', 'systemctl', 'start', service_name]
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    logger.error(f"Command failed: {' '.join(cmd)}: {result.stderr}")
                    return False, f"Failed to set up service: {result.stderr}"
            
            logger.info(f"Linux systemd service '{service_name}' created and enabled")
            return True, f"Auto-start configured successfully. Tailscale will serve on port {port} at boot."
        else:
            # Disable and remove service
            commands = [
                ['sudo', 'systemctl', 'stop', service_name],
                ['sudo', 'systemctl', 'disable', service_name],
                ['sudo', 'rm', '-f', service_path],
                ['sudo', 'systemctl', 'daemon-reload']
            ]
            
            for cmd in commands:
                subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            logger.info(f"Linux systemd service '{service_name}' disabled and removed")
            return True, "Auto-start disabled successfully."
    
    except Exception as e:
        logger.error(f"Error managing Linux systemd service: {e}")
        return False, f"Error: {str(e)}"

def _setup_macos_launchagent(port, enable):
    """Set up macOS LaunchAgent for tailscale serve"""
    agent_label = "com.nextcloud.tailscale-serve"
    agent_plist = os.path.expanduser(f"~/Library/LaunchAgents/{agent_label}.plist")
    
    try:
        if enable:
            # Create LaunchAgent plist
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{agent_label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/tailscale</string>
        <string>serve</string>
        <string>--bg</string>
        <string>--https=443</string>
        <string>http://localhost:{port}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/nextcloud-tailscale-serve.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/nextcloud-tailscale-serve-error.log</string>
</dict>
</plist>
"""
            
            # Ensure LaunchAgents directory exists
            os.makedirs(os.path.dirname(agent_plist), exist_ok=True)
            
            # Write plist file
            with open(agent_plist, 'w') as f:
                f.write(plist_content)
            
            # Load the agent
            result = subprocess.run(
                ['launchctl', 'load', agent_plist],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"macOS LaunchAgent '{agent_label}' created and loaded")
                return True, f"Auto-start configured successfully. Tailscale will serve on port {port} at login."
            else:
                logger.error(f"Failed to load LaunchAgent: {result.stderr}")
                return False, f"Failed to load LaunchAgent: {result.stderr}"
        else:
            # Unload and remove agent
            if os.path.exists(agent_plist):
                subprocess.run(['launchctl', 'unload', agent_plist], 
                             capture_output=True, text=True, timeout=10)
                os.remove(agent_plist)
            
            logger.info(f"macOS LaunchAgent '{agent_label}' unloaded and removed")
            return True, "Auto-start disabled successfully."
    
    except Exception as e:
        logger.error(f"Error managing macOS LaunchAgent: {e}")
        return False, f"Error: {str(e)}"

# ----------- EXTRACTION USING PYTHON TARFILE MODULE -----------
def extract_config_php_only(archive_path, extract_to):
    """
    Efficiently extract only the config.php file from a tar.gz archive.
    
    This function searches for config.php in the archive and extracts only the first
    matching file, avoiding the overhead of extracting the entire backup which can be
    several gigabytes in size.
    
    Rationale: During early database detection, we only need to read config.php to
    determine the database type (SQLite, MySQL, or PostgreSQL). This allows the GUI
    to show/hide the appropriate input fields without extracting the full backup.
    
    Args:
        archive_path: Path to the .tar.gz backup archive
        extract_to: Directory where config.php should be extracted
    
    Returns:
        Path to extracted config.php file, or None if not found
    
    Raises:
        Exception: If archive is corrupted, unreadable, or extraction fails
    """
    os.makedirs(extract_to, exist_ok=True)
    print(f"🔍 Searching for config.php in archive: {os.path.basename(archive_path)}")
    print(f"📂 Extraction target directory: {extract_to}")
    
    try:
        with tarfile.open(archive_path, 'r:gz') as tar:
            # Track all potential config.php files found for better logging
            potential_configs = []
            
            # Iterate through archive members to find config.php
            # This is efficient as it doesn't extract anything until we find the target
            for member in tar:
                # Check if this is a config.php file by exact basename match
                # This prevents matching files like "apache-pretty-urls.config.php"
                if member.isfile() and os.path.basename(member.name) == 'config.php':
                    potential_configs.append(member.name)
                    print(f"📄 Found potential config.php: {member.name}")
                    
                    # Validate: check if path contains 'config' directory
                    # This helps ensure we get the Nextcloud config.php in config/ folder
                    path_parts = member.name.split('/')
                    if 'config' in path_parts:
                        # Get the parent directory name for logging
                        parent_dir = os.path.dirname(member.name)
                        print(f"✓ Parent directory validation passed")
                        print(f"  - Full path: {member.name}")
                        print(f"  - Parent directory: {parent_dir}")
                        print(f"  - Contains 'config' directory: Yes")
                        
                        # Extract only this single file to validate its content
                        print(f"📦 Extracting config.php to: {extract_to}")
                        tar.extract(member, path=extract_to)
                        extracted_path = os.path.join(extract_to, member.name)
                        print(f"✓ Extraction complete: {extracted_path}")
                        
                        # Validate the file content before accepting it
                        # Check for $CONFIG and dbtype to confirm it's a real Nextcloud config
                        print(f"🔍 Validating file content...")
                        try:
                            with open(extracted_path, 'r', encoding='utf-8') as f:
                                content = f.read(200)  # Read first 200 chars for validation
                                if '$CONFIG' in content or 'dbtype' in content:
                                    print(f"✓ Content validation passed")
                                    print(f"  - Contains '$CONFIG': {'$CONFIG' in content}")
                                    print(f"  - Contains 'dbtype': {'dbtype' in content}")
                                    print(f"✓ Using config.php from: {member.name}")
                                    return extracted_path
                                else:
                                    print(f"✗ Content validation failed")
                                    print(f"  - File {member.name} doesn't contain $CONFIG or dbtype")
                                    print(f"  - Skipping this file and continuing search")
                        except Exception as e:
                            print(f"⚠️ Could not validate {member.name}: {e}")
                            continue
                    else:
                        print(f"✗ Parent directory validation failed")
                        print(f"  - Path: {member.name}")
                        print(f"  - Parent directory: {os.path.dirname(member.name)}")
                        print(f"  - Reason: Path does not contain 'config' directory")
                        print(f"  - Skipping this file")
            
            # If we get here, config.php was not found in the archive
            print(f"✗ No valid config.php found in archive")
            if potential_configs:
                print(f"⚠️ Summary: Found {len(potential_configs)} config.php file(s) but none passed all validation checks:")
                for config in potential_configs:
                    print(f"   - {config}")
                print(f"   Possible reasons:")
                print(f"   - Not in a 'config' directory")
                print(f"   - Doesn't contain $CONFIG or dbtype markers")
            else:
                print("⚠️ No files named exactly 'config.php' found in archive")
                print(f"   (Files ending with 'config.php' but with different basenames are excluded)")
            return None
            
    except tarfile.ReadError as e:
        raise Exception(f"Invalid or corrupted archive: {e}")
    except OSError as e:
        if e.errno == 28:  # ENOSPC - No space left on device
            raise Exception(f"No space left on device: {e}")
        elif e.errno == 13:  # EACCES - Permission denied
            raise Exception(f"Permission denied: {e}")
        else:
            raise Exception(f"File system error during extraction: {e}")
    except Exception as e:
        raise Exception(f"Extraction failed: {e}")


def fast_extract_tar_gz(archive_path, extract_to, progress_callback=None, batch_size=1, prepare_callback=None):
    """
    Extract tar.gz archive using streaming extraction with live progress updates.
    
    This function uses streaming extraction to start extracting files immediately
    without an upfront full scan of the archive. Progress is tracked by bytes
    read/extracted, and the UI shows the current filename as each file is processed.
    
    Key features:
    - Streaming extraction: starts immediately without full archive scan
    - Byte-based progress: tracks actual bytes read for accurate progress
    - Real-time filename updates: shows current file being extracted
    - Adaptive progress: switches to file count when total is discovered
    - Non-blocking: no 'preparing extraction...' delay
    
    Args:
        archive_path: Path to the .tar.gz backup archive
        extract_to: Directory where all files should be extracted
        progress_callback: Optional callback function(files_extracted, total_files, current_file, 
                          bytes_processed, total_bytes) that gets called after each batch of files
        batch_size: Number of files to extract before calling the progress callback
                   (default: 1 for real-time updates)
        prepare_callback: Optional callback function() called before opening archive
    
    Raises:
        Exception: If archive is corrupted, unreadable, or extraction fails
    """
    os.makedirs(extract_to, exist_ok=True)
    
    # Get archive size for progress tracking
    # Note: We track position in compressed stream, not uncompressed file sizes
    archive_size = os.path.getsize(archive_path)
    
    try:
        # Call prepare callback for immediate feedback (non-blocking)
        if prepare_callback:
            prepare_callback()
        
        # Open archive file to track read position
        with open(archive_path, 'rb') as archive_file:
            # Open tarfile in streaming mode (doesn't scan entire archive upfront)
            with tarfile.open(fileobj=archive_file, mode='r|gz') as tar:
                # Streaming mode: we don't know total file count upfront
                # Track progress by compressed bytes read from archive
                files_extracted = 0
                total_files = None  # Unknown until we finish
                batch_count = 0
                last_position = 0
                
                # If no progress callback, extract all at once
                if progress_callback is None:
                    for member in tar:
                        tar.extract(member, path=extract_to)
                    print(f"✓ Successfully extracted full archive to {extract_to}")
                    return
                
                # Stream through archive members as they're read
                for member in tar:
                    # Extract this file
                    tar.extract(member, path=extract_to)
                    files_extracted += 1
                    batch_count += 1
                    
                    # Get current position in compressed archive
                    current_position = archive_file.tell()
                    
                    # Call progress callback after each batch
                    if batch_count >= batch_size:
                        current_file = os.path.basename(member.name) if member.name else "..."
                        # Report with None for total_files since we don't know yet
                        # Use current position in archive for byte-based progress
                        progress_callback(files_extracted, total_files, current_file, 
                                        current_position, archive_size)
                        batch_count = 0
                        last_position = current_position
                
                # Final callback with complete information
                if progress_callback and (batch_count > 0 or files_extracted == 0):
                    current_file = "Complete"
                    total_files = files_extracted  # Now we know the total
                    current_position = archive_file.tell()
                    progress_callback(files_extracted, total_files, current_file,
                                    current_position, archive_size)
            
        print(f"✓ Successfully extracted {files_extracted} files to {extract_to}")
    except tarfile.ReadError as e:
        raise Exception(f"Invalid or corrupted archive: {e}")
    except OSError as e:
        if e.errno == 28:  # ENOSPC - No space left on device
            raise Exception(f"No space left on device: {e}")
        elif e.errno == 13:  # EACCES - Permission denied
            raise Exception(f"Permission denied: {e}")
        else:
            raise Exception(f"File system error during extraction: {e}")
    except Exception as e:
        raise Exception(f"Extraction failed: {e}")

# --- Scheduled Backup Functions (Windows Task Scheduler Integration) ---

def get_system_timezone_info():
    """Get the system's local timezone information as a string."""
    try:
        # Get the local timezone offset
        now = datetime.now()
        local_tz = now.astimezone()
        tz_offset = local_tz.strftime('%z')
        tz_name = local_tz.tzname()
        
        # Format: "UTC+05:00 (PST)" or "UTC-04:00 (EDT)"
        if tz_offset:
            offset_hours = int(tz_offset[:3])
            offset_mins = int(tz_offset[0] + tz_offset[3:5])
            offset_str = f"UTC{offset_hours:+03d}:{abs(offset_mins):02d}"
            if tz_name:
                return f"{offset_str} ({tz_name})"
            return offset_str
        elif tz_name:
            return tz_name
        else:
            return "Local System Time"
    except Exception as e:
        logger.warning(f"Could not determine timezone: {e}")
        return "Local System Time"

def detect_cloud_sync_folders():
    """
    Detect common cloud storage sync folders on the system.
    Returns a dict with cloud provider names and their sync folder paths.
    """
    home = os.path.expanduser("~")
    cloud_folders = {}
    
    # OneDrive detection (Windows, Mac, Linux)
    onedrive_paths = [
        os.path.join(home, "OneDrive"),
        os.path.join(home, "OneDrive - Personal"),
        os.path.join(home, "Library", "CloudStorage") if platform.system() == "Darwin" else None,
    ]
    for path in onedrive_paths:
        if path and os.path.isdir(path):
            cloud_folders['OneDrive'] = path
            break
    
    # Google Drive detection (Windows, Mac, Linux)
    google_drive_paths = [
        os.path.join(home, "Google Drive"),
        os.path.join(home, "GoogleDrive"),
        os.path.join(home, "My Drive"),
    ]
    for path in google_drive_paths:
        if os.path.isdir(path):
            cloud_folders['Google Drive'] = path
            break
    
    # Dropbox detection
    dropbox_paths = [
        os.path.join(home, "Dropbox"),
    ]
    for path in dropbox_paths:
        if os.path.isdir(path):
            cloud_folders['Dropbox'] = path
            break
    
    # iCloud Drive (Mac)
    if platform.system() == "Darwin":
        icloud_path = os.path.join(home, "Library", "Mobile Documents", "com~apple~CloudDocs")
        if os.path.isdir(icloud_path):
            cloud_folders['iCloud Drive'] = icloud_path
    
    return cloud_folders

def get_schedule_config_path():
    """Get the path to the schedule configuration file."""
    config_dir = os.path.join(os.path.expanduser("~"), ".nextcloud_backup")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "schedule_config.json")

def load_schedule_config():
    """Load the schedule configuration from file."""
    config_path = get_schedule_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading schedule config: {e}")
    return None

def save_schedule_config(config):
    """Save the schedule configuration to file."""
    config_path = get_schedule_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving schedule config: {e}")
        return False

def get_exe_path():
    """Get the path to the current executable or script."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return sys.executable
    else:
        # Running as script
        return os.path.abspath(sys.argv[0])

def validate_scheduled_task_setup(task_name, schedule_type, schedule_time, backup_dir, encrypt, password=""):
    """
    Validate all aspects of scheduled task setup before creating it.
    Returns a dict with validation results for each check.
    
    Args:
        task_name: Name for the scheduled task
        schedule_type: 'daily', 'weekly', 'monthly', or 'custom'
        schedule_time: Time in HH:MM format
        backup_dir: Directory to save backups
        encrypt: Boolean for encryption
        password: Encryption password (optional)
    
    Returns: dict with validation results
        {
            'exe_path_exists': (bool, message),
            'start_dir_valid': (bool, message),
            'arguments_valid': (bool, message),
            'backup_dir_writable': (bool, message),
            'log_file_writable': (bool, message),
            'task_fields_valid': (bool, message),
            'all_valid': bool,
            'errors': [list of error messages]
        }
    """
    results = {
        'all_valid': True,
        'errors': []
    }
    
    # 1. Check backup script or EXE path exists
    try:
        exe_path = get_exe_path()
        if os.path.exists(exe_path):
            results['exe_path_exists'] = (True, f"✓ Executable path exists: {exe_path}")
            logger.info(f"VALIDATION: Executable path verified: {exe_path}")
        else:
            results['exe_path_exists'] = (False, f"✗ Executable path not found: {exe_path}")
            results['all_valid'] = False
            results['errors'].append(f"Executable path not found: {exe_path}")
            logger.error(f"VALIDATION FAILED: Executable path not found: {exe_path}")
    except Exception as e:
        results['exe_path_exists'] = (False, f"✗ Error checking executable path: {e}")
        results['all_valid'] = False
        results['errors'].append(f"Error checking executable path: {e}")
        logger.error(f"VALIDATION FAILED: Error checking executable path: {e}")
    
    # 2. Validate 'Start in' directory (parent directory of executable)
    try:
        exe_path = get_exe_path()
        start_dir = os.path.dirname(exe_path)
        if os.path.isdir(start_dir):
            results['start_dir_valid'] = (True, f"✓ Start directory is valid: {start_dir}")
            logger.info(f"VALIDATION: Start directory verified: {start_dir}")
        else:
            results['start_dir_valid'] = (False, f"✗ Start directory not found: {start_dir}")
            results['all_valid'] = False
            results['errors'].append(f"Start directory not found: {start_dir}")
            logger.error(f"VALIDATION FAILED: Start directory not found: {start_dir}")
    except Exception as e:
        results['start_dir_valid'] = (False, f"✗ Error checking start directory: {e}")
        results['all_valid'] = False
        results['errors'].append(f"Error checking start directory: {e}")
        logger.error(f"VALIDATION FAILED: Error checking start directory: {e}")
    
    # 3. Validate arguments for scheduled task
    try:
        args = [
            "--scheduled",
            "--backup-dir", backup_dir,
            "--encrypt" if encrypt else "--no-encrypt"
        ]
        if encrypt and password:
            args.extend(["--password", password])
        
        # Verify all required arguments are present
        has_scheduled = "--scheduled" in args
        has_backup_dir = "--backup-dir" in args and backup_dir in args
        has_encrypt_flag = "--encrypt" in args or "--no-encrypt" in args
        
        if has_scheduled and has_backup_dir and has_encrypt_flag:
            results['arguments_valid'] = (True, f"✓ Task arguments are correct: {' '.join(args[:4])}")
            logger.info(f"VALIDATION: Task arguments verified: {args}")
        else:
            missing = []
            if not has_scheduled:
                missing.append("--scheduled")
            if not has_backup_dir:
                missing.append("--backup-dir")
            if not has_encrypt_flag:
                missing.append("encryption flag")
            
            results['arguments_valid'] = (False, f"✗ Missing required arguments: {', '.join(missing)}")
            results['all_valid'] = False
            results['errors'].append(f"Missing required arguments: {', '.join(missing)}")
            logger.error(f"VALIDATION FAILED: Missing required arguments: {missing}")
    except Exception as e:
        results['arguments_valid'] = (False, f"✗ Error validating arguments: {e}")
        results['all_valid'] = False
        results['errors'].append(f"Error validating arguments: {e}")
        logger.error(f"VALIDATION FAILED: Error validating arguments: {e}")
    
    # 4. Check backup destination is writable
    try:
        if not os.path.exists(backup_dir):
            results['backup_dir_writable'] = (False, f"✗ Backup directory does not exist: {backup_dir}")
            results['all_valid'] = False
            results['errors'].append(f"Backup directory does not exist: {backup_dir}")
            logger.error(f"VALIDATION FAILED: Backup directory does not exist: {backup_dir}")
        elif not os.path.isdir(backup_dir):
            results['backup_dir_writable'] = (False, f"✗ Backup path is not a directory: {backup_dir}")
            results['all_valid'] = False
            results['errors'].append(f"Backup path is not a directory: {backup_dir}")
            logger.error(f"VALIDATION FAILED: Backup path is not a directory: {backup_dir}")
        else:
            # Try to create a test file
            test_file = os.path.join(backup_dir, '.nextcloud_backup_test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                results['backup_dir_writable'] = (True, f"✓ Backup directory is writable: {backup_dir}")
                logger.info(f"VALIDATION: Backup directory is writable: {backup_dir}")
            except Exception as write_error:
                results['backup_dir_writable'] = (False, f"✗ Backup directory is not writable: {write_error}")
                results['all_valid'] = False
                results['errors'].append(f"Backup directory is not writable: {write_error}")
                logger.error(f"VALIDATION FAILED: Backup directory is not writable: {write_error}")
    except Exception as e:
        results['backup_dir_writable'] = (False, f"✗ Error checking backup directory: {e}")
        results['all_valid'] = False
        results['errors'].append(f"Error checking backup directory: {e}")
        logger.error(f"VALIDATION FAILED: Error checking backup directory: {e}")
    
    # 5. Check log file location is writable and can write test entry
    try:
        log_file = LOG_FILE_PATH
        log_dir = os.path.dirname(log_file)
        
        if not os.path.exists(log_dir):
            # Try to create the log directory
            try:
                os.makedirs(log_dir, exist_ok=True)
                results['log_file_writable'] = (True, f"✓ Log directory created: {log_dir}")
                logger.info(f"VALIDATION: Log directory created: {log_dir}")
            except Exception as mkdir_error:
                results['log_file_writable'] = (False, f"✗ Cannot create log directory: {mkdir_error}")
                results['all_valid'] = False
                results['errors'].append(f"Cannot create log directory: {mkdir_error}")
                logger.error(f"VALIDATION FAILED: Cannot create log directory: {mkdir_error}")
        else:
            # Try to write a test log entry
            try:
                logger.info("VALIDATION: Testing log file write capability")
                results['log_file_writable'] = (True, f"✓ Log file is writable: {log_file}")
            except Exception as write_error:
                results['log_file_writable'] = (False, f"✗ Cannot write to log file: {write_error}")
                results['all_valid'] = False
                results['errors'].append(f"Cannot write to log file: {write_error}")
                logger.error(f"VALIDATION FAILED: Cannot write to log file: {write_error}")
    except Exception as e:
        results['log_file_writable'] = (False, f"✗ Error checking log file: {e}")
        results['all_valid'] = False
        results['errors'].append(f"Error checking log file: {e}")
        logger.error(f"VALIDATION FAILED: Error checking log file: {e}")
    
    # 6. Validate Task Scheduler entry fields
    try:
        # Validate schedule_type
        valid_schedule_types = ['daily', 'weekly', 'monthly']
        if schedule_type not in valid_schedule_types:
            results['task_fields_valid'] = (False, f"✗ Invalid schedule type: {schedule_type}. Must be one of: {', '.join(valid_schedule_types)}")
            results['all_valid'] = False
            results['errors'].append(f"Invalid schedule type: {schedule_type}")
            logger.error(f"VALIDATION FAILED: Invalid schedule type: {schedule_type}")
        else:
            # Validate time format
            try:
                datetime.strptime(schedule_time, "%H:%M")
                # Validate task name
                if not task_name or len(task_name.strip()) == 0:
                    results['task_fields_valid'] = (False, f"✗ Task name cannot be empty")
                    results['all_valid'] = False
                    results['errors'].append("Task name cannot be empty")
                    logger.error("VALIDATION FAILED: Task name cannot be empty")
                else:
                    results['task_fields_valid'] = (True, f"✓ Task fields are valid (name: {task_name}, type: {schedule_type}, time: {schedule_time})")
                    logger.info(f"VALIDATION: Task fields verified: {task_name}, {schedule_type}, {schedule_time}")
            except ValueError:
                results['task_fields_valid'] = (False, f"✗ Invalid time format: {schedule_time}. Must be HH:MM (e.g., 02:00)")
                results['all_valid'] = False
                results['errors'].append(f"Invalid time format: {schedule_time}")
                logger.error(f"VALIDATION FAILED: Invalid time format: {schedule_time}")
    except Exception as e:
        results['task_fields_valid'] = (False, f"✗ Error validating task fields: {e}")
        results['all_valid'] = False
        results['errors'].append(f"Error validating task fields: {e}")
        logger.error(f"VALIDATION FAILED: Error validating task fields: {e}")
    
    # Log overall validation result
    if results['all_valid']:
        logger.info("VALIDATION: All checks passed successfully")
    else:
        logger.error(f"VALIDATION FAILED: {len(results['errors'])} error(s) found")
    
    return results

def run_test_backup(backup_dir, encrypt, password=""):
    """
    Run a test backup to verify the configuration works.
    Only backs up the schedule config file, then immediately deletes it.
    Returns (success, message) tuple.
    """
    logger.info("TEST RUN: Starting test backup of config file")
    
    try:
        # Get the schedule config file path
        config_path = get_schedule_config_path()
        
        # Check if config file exists
        if not os.path.exists(config_path):
            logger.error("TEST RUN: Schedule config file not found")
            return False, "Test backup failed: Schedule configuration file not found."
        
        # Create a test backup of the config file
        test_backup_name = f"test_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        test_backup_path = os.path.join(backup_dir, test_backup_name)
        
        # Create tar.gz archive with just the config file
        with tarfile.open(test_backup_path, 'w:gz') as tar:
            tar.add(config_path, arcname='schedule_config.json')
        
        # Verify the backup was created
        if os.path.exists(test_backup_path):
            file_size = os.path.getsize(test_backup_path)
            logger.info(f"TEST RUN: Config backup created successfully: {test_backup_path} ({file_size} bytes)")
            
            # Immediately delete the test backup
            try:
                os.remove(test_backup_path)
                logger.info("TEST RUN: Config backup deleted after successful test")
            except Exception as cleanup_error:
                logger.warning(f"TEST RUN: Failed to delete test backup: {cleanup_error}")
                # Still return success since the backup itself worked
            
            return True, f"✓ Test backup successful!\n\nConfig file backed up: schedule_config.json\nTest backup size: {file_size} bytes\nLocation verified: {backup_dir}\nBackup immediately deleted (as expected)\n\nYour scheduled backup configuration is working correctly."
        else:
            logger.error("TEST RUN: Test backup file was not created")
            return False, "Test backup failed: Backup file was not created."
    
    except Exception as e:
        logger.error(f"TEST RUN: Test backup failed with error: {e}")
        return False, f"Test backup failed: {e}"

def create_scheduled_task(task_name, schedule_type, schedule_time, backup_dir, encrypt, password="", components=None, rotation_keep=0):
    """
    Create a Windows scheduled task for automatic backups.
    
    Args:
        task_name: Name for the scheduled task
        schedule_type: 'daily', 'weekly', 'monthly', or 'custom'
        schedule_time: Time in HH:MM format
        backup_dir: Directory to save backups
        encrypt: Boolean for encryption
        password: Encryption password (optional)
        components: Dict of component selections (optional)
        rotation_keep: Number of backups to keep (0 = unlimited)
    
    Returns: (success, message) tuple
    """
    if platform.system() != "Windows":
        return False, "Scheduled backups are only supported on Windows at this time."
    
    try:
        # Get the executable path
        exe_path = get_exe_path()
        
        # Ensure backup_dir is safely quoted (prevents argument splitting with spaces)
        backup_dir_quoted = '"' + backup_dir.strip('"') + '"'
        
        # Build the command arguments for scheduled execution
        args = [
            "--scheduled",
            "--backup-dir", backup_dir_quoted,
            "--encrypt" if encrypt else "--no-encrypt"
        ]
        
        if encrypt and password:
            args.extend(["--password", password])
        
        # Add component selection if provided
        if components:
            selected_components = [k for k, v in components.items() if v]
            if selected_components:
                args.extend(["--components", ",".join(selected_components)])
        
        # Add rotation setting
        if rotation_keep > 0:
            args.extend(["--rotation-keep", str(rotation_keep)])
        
        # Build the full command
        # Detect if running as .py script or .exe executable
        if exe_path.lower().endswith('.py'):
            # For Python scripts, invoke through Python interpreter
            command = f'python "{exe_path}" {" ".join(args)}'
        else:
            # For compiled executables (.exe), run directly
            command = f'"{exe_path}" {" ".join(args)}'
        
        # Map schedule_type to schtasks frequency
        if schedule_type == "daily":
            schedule_args = ["/SC", "DAILY"]
        elif schedule_type == "weekly":
            schedule_args = ["/SC", "WEEKLY", "/D", "MON"]  # Default to Monday
        elif schedule_type == "monthly":
            schedule_args = ["/SC", "MONTHLY", "/D", "1"]  # Default to 1st of month
        else:
            return False, f"Unsupported schedule type: {schedule_type}"
        
        # Create the scheduled task using schtasks
        creation_flags = get_subprocess_creation_flags()
        
        # Delete existing task if it exists
        subprocess.run(
            ["schtasks", "/Delete", "/TN", task_name, "/F"],
            creationflags=creation_flags,
            capture_output=True,
            text=True
        )
        
        # Create new task
        # Note: /SC (schedule type) must come BEFORE /ST (start time) per schtasks requirements
        schtasks_cmd = [
            "schtasks", "/Create",
            "/TN", task_name,
            "/TR", command
        ]
        schtasks_cmd.extend(schedule_args)  # Add /SC and /D parameters
        schtasks_cmd.extend([
            "/ST", schedule_time,
            "/F"  # Force creation, overwrite if exists
        ])
        
        print("Scheduled Task Command:", schtasks_cmd)
        result = subprocess.run(
            schtasks_cmd,
            creationflags=creation_flags,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, f"Scheduled task '{task_name}' created successfully."
        else:
            return False, f"Failed to create task: {result.stderr}"
    
    except Exception as e:
        return False, f"Error creating scheduled task: {e}"

def delete_scheduled_task(task_name):
    """
    Delete a Windows scheduled task.
    
    Args:
        task_name: Name of the scheduled task to delete
    
    Returns: (success, message) tuple
    """
    if platform.system() != "Windows":
        return False, "Scheduled backups are only supported on Windows at this time."
    
    try:
        creation_flags = get_subprocess_creation_flags()
        
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", task_name, "/F"],
            creationflags=creation_flags,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, f"Scheduled task '{task_name}' deleted successfully."
        else:
            # Check if task doesn't exist
            if "cannot find the file" in result.stderr.lower() or "does not exist" in result.stderr.lower():
                return True, "Scheduled task was not found (may already be deleted)."
            return False, f"Failed to delete task: {result.stderr}"
    
    except Exception as e:
        return False, f"Error deleting scheduled task: {e}"

def get_scheduled_task_status(task_name):
    """
    Get the status of a Windows scheduled task.
    
    Args:
        task_name: Name of the scheduled task
    
    Returns: dict with status info or None if not found
    """
    if platform.system() != "Windows":
        return None
    
    try:
        creation_flags = get_subprocess_creation_flags()
        
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name, "/FO", "LIST", "/V"],
            creationflags=creation_flags,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Parse the output
            lines = result.stdout.strip().split('\n')
            status = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    status[key] = value
            
            return {
                'exists': True,
                'status': status.get('Status', 'Unknown'),
                'next_run': status.get('Next Run Time', 'Unknown'),
                'last_run': status.get('Last Run Time', 'Unknown'),
                'task_state': status.get('Task To Run', 'Unknown')
            }
        else:
            return {'exists': False}
    
    except Exception as e:
        print(f"Error checking task status: {e}")
        return None

def enable_scheduled_task(task_name):
    """Enable a Windows scheduled task."""
    if platform.system() != "Windows":
        return False, "Scheduled backups are only supported on Windows at this time."
    
    try:
        creation_flags = get_subprocess_creation_flags()
        
        result = subprocess.run(
            ["schtasks", "/Change", "/TN", task_name, "/ENABLE"],
            creationflags=creation_flags,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, f"Scheduled task '{task_name}' enabled."
        else:
            return False, f"Failed to enable task: {result.stderr}"
    
    except Exception as e:
        return False, f"Error enabling scheduled task: {e}"

def get_last_backup_info(backup_dir):
    """
    Get information about the most recent backup in the directory.
    Returns dict with backup info or None if no backups found.
    """
    try:
        if not os.path.exists(backup_dir) or not os.path.isdir(backup_dir):
            return None
        
        # Find all backup files (tar.gz)
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.tar.gz') and not filename.startswith('test_backup_'):
                filepath = os.path.join(backup_dir, filename)
                if os.path.isfile(filepath):
                    backup_files.append({
                        'name': filename,
                        'path': filepath,
                        'size': os.path.getsize(filepath),
                        'modified': os.path.getmtime(filepath)
                    })
        
        if not backup_files:
            return None
        
        # Get the most recent backup
        latest_backup = max(backup_files, key=lambda x: x['modified'])
        
        # Format the time
        modified_time = datetime.fromtimestamp(latest_backup['modified'])
        size_mb = latest_backup['size'] / (1024 * 1024)
        
        return {
            'name': latest_backup['name'],
            'path': latest_backup['path'],
            'size': latest_backup['size'],
            'size_mb': size_mb,
            'modified': modified_time,
            'age_hours': (datetime.now() - modified_time).total_seconds() / 3600
        }
    except Exception as e:
        logger.error(f"Error getting last backup info: {e}")
        return None

def get_recent_log_entries(num_lines=50):
    """
    Get recent log entries from the log file.
    Returns list of log lines or empty list if error.
    """
    try:
        log_file = LOG_FILE_PATH
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Return last num_lines
        return lines[-num_lines:] if len(lines) > num_lines else lines
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        return []

def verify_scheduled_backup_ran(backup_dir, task_name):
    """
    Verify that a scheduled backup actually ran by checking:
    1. Backup file exists in the directory
    2. Log file contains recent backup entries
    
    Returns dict with verification results.
    """
    results = {
        'backup_file_exists': False,
        'log_entry_exists': False,
        'backup_info': None,
        'recent_logs': [],
        'success': False,
        'message': ''
    }
    
    try:
        # Check for backup file
        backup_info = get_last_backup_info(backup_dir)
        if backup_info:
            results['backup_file_exists'] = True
            results['backup_info'] = backup_info
            
            # Check if backup is recent (within last 48 hours)
            if backup_info['age_hours'] < 48:
                results['message'] += f"✓ Recent backup found: {backup_info['name']}\n"
                results['message'] += f"  Created: {backup_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                results['message'] += f"  Size: {backup_info['size_mb']:.2f} MB\n"
            else:
                results['message'] += f"⚠ Last backup is {backup_info['age_hours']:.1f} hours old\n"
        else:
            results['message'] += "✗ No backup files found in directory\n"
        
        # Check log file for recent scheduled backup entries
        log_entries = get_recent_log_entries(100)
        scheduled_entries = [line for line in log_entries if 'SCHEDULED' in line or 'scheduled' in line]
        
        if scheduled_entries:
            results['log_entry_exists'] = True
            results['recent_logs'] = scheduled_entries[-10:]  # Last 10 scheduled entries
            results['message'] += f"✓ Found {len(scheduled_entries)} scheduled backup log entries\n"
        else:
            results['message'] += "⚠ No scheduled backup entries found in recent logs\n"
        
        # Determine overall success
        results['success'] = results['backup_file_exists'] and results['log_entry_exists']
        
        if results['success']:
            results['message'] += "\n✓ Verification successful: Scheduled backup is working correctly"
        elif results['backup_file_exists']:
            results['message'] += "\n⚠ Backup file exists but no recent log entries found"
        else:
            results['message'] += "\n✗ Verification failed: No recent backup found"
        
        logger.info(f"VERIFICATION: Scheduled backup verification completed. Success: {results['success']}")
        
    except Exception as e:
        results['message'] = f"Error during verification: {e}"
        logger.error(f"VERIFICATION: Error during verification: {e}")
    
    return results

def disable_scheduled_task(task_name):
    """Disable a Windows scheduled task."""
    if platform.system() != "Windows":
        return False, "Scheduled backups are only supported on Windows at this time."
    
    try:
        creation_flags = get_subprocess_creation_flags()
        
        result = subprocess.run(
            ["schtasks", "/Change", "/TN", task_name, "/DISABLE"],
            creationflags=creation_flags,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, f"Scheduled task '{task_name}' disabled."
        else:
            return False, f"Failed to disable task: {result.stderr}"
    
    except Exception as e:
        return False, f"Error disabling scheduled task: {e}"

def run_scheduled_task_now(task_name):
    """
    Trigger a Windows scheduled task to run immediately.
    
    Args:
        task_name: Name of the scheduled task to run
    
    Returns: (success, message) tuple
    """
    if platform.system() != "Windows":
        return False, "Scheduled tasks are only supported on Windows at this time."
    
    try:
        logger.info(f"Triggering scheduled task '{task_name}' to run now...")
        creation_flags = get_subprocess_creation_flags()
        
        result = subprocess.run(
            ["schtasks", "/Run", "/TN", task_name],
            creationflags=creation_flags,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Scheduled task '{task_name}' triggered successfully")
            return True, f"Scheduled task '{task_name}' started successfully."
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            logger.error(f"Failed to trigger task '{task_name}': {error_msg}")
            return False, f"Failed to trigger task: {error_msg}"
    
    except Exception as e:
        logger.error(f"Error triggering scheduled task '{task_name}': {e}")
        return False, f"Error triggering scheduled task: {e}"

def get_scheduled_task_command(task_name):
    """
    Get the command (action) configured in a Windows scheduled task.
    
    Args:
        task_name: Name of the scheduled task
    
    Returns: Command string from the task, or None if not found or error
    """
    if platform.system() != "Windows":
        return None
    
    try:
        creation_flags = get_subprocess_creation_flags()
        
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name, "/FO", "LIST", "/V"],
            creationflags=creation_flags,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Parse the output to find "Task To Run" field
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key == "Task To Run":
                        return value
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting scheduled task command: {e}")
        return None

def extract_path_from_task_command(command):
    """
    Extract the executable/script path from a scheduled task command.
    
    Handles both formats:
    - Python script: python "C:\\path\\to\\script.py" --args
    - Executable: "C:\\path\\to\\app.exe" --args
    
    Args:
        command: Full command string from scheduled task
    
    Returns: Extracted path or None if unable to parse
    """
    if not command:
        return None
    
    try:
        # Pattern 1: python "path" or python.exe "path"
        if command.lower().startswith('python'):
            # Find the quoted path after python
            match = re.search(r'python(?:\.exe)?\s+"([^"]+)"', command, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Pattern 2: "path" (for .exe files)
        match = re.search(r'^"([^"]+)"', command)
        if match:
            return match.group(1)
        
        # Pattern 3: unquoted path at start (less common)
        parts = command.split()
        if parts and os.path.exists(parts[0]):
            return parts[0]
        
        return None
    
    except Exception as e:
        logger.error(f"Error extracting path from command: {e}")
        return None

def check_and_repair_scheduled_task(task_name="NextcloudBackup"):
    """
    Check if the app has been moved and automatically repair the scheduled task.
    
    This function:
    1. Gets the current executable path
    2. Queries the scheduled task to get its configured path
    3. Compares the two paths
    4. If different, updates the scheduled task to use the new path
    
    Args:
        task_name: Name of the scheduled task to check
    
    Returns: (repaired, message) tuple
        - repaired: True if task was repaired, False if no repair needed or error
        - message: Descriptive message about what happened
    """
    if platform.system() != "Windows":
        return False, "Scheduled task repair only supported on Windows"
    
    try:
        # Get current executable path
        current_path = get_exe_path()
        
        # Get the scheduled task command
        task_command = get_scheduled_task_command(task_name)
        
        if not task_command:
            # No scheduled task exists or couldn't query it
            return False, "No scheduled task found or unable to query"
        
        # Extract the path from the task command
        task_path = extract_path_from_task_command(task_command)
        
        if not task_path:
            logger.warning(f"Unable to extract path from task command: {task_command}")
            return False, "Unable to parse scheduled task command"
        
        # Normalize paths for comparison (handle case differences, separators, etc.)
        current_path_norm = os.path.normcase(os.path.normpath(current_path))
        task_path_norm = os.path.normcase(os.path.normpath(task_path))
        
        # Check if paths are different
        if current_path_norm == task_path_norm:
            # Paths match, no repair needed
            return False, "Scheduled task path is current"
        
        # Paths differ - need to repair!
        logger.info(f"App moved detected: {task_path} -> {current_path}")
        
        # Get the full task status to extract other parameters
        task_status = get_scheduled_task_status(task_name)
        if not task_status or not task_status.get('exists'):
            return False, "Unable to get task details for repair"
        
        # Parse the existing command to extract arguments
        # We need to preserve the backup directory, encryption settings, etc.
        backup_dir = None
        encrypt = False
        password = ""
        
        # Try to extract arguments from the existing command
        if '--backup-dir' in task_command:
            match = re.search(r'--backup-dir\s+"?([^"\s]+)"?', task_command)
            if match:
                backup_dir = match.group(1).strip('"')
        
        if '--encrypt' in task_command:
            encrypt = True
        
        if '--password' in task_command:
            match = re.search(r'--password\s+"?([^"\s]+)"?', task_command)
            if match:
                password = match.group(1).strip('"')
        
        if not backup_dir:
            logger.error("Unable to extract backup directory from existing task")
            return False, "Unable to extract task parameters for repair"
        
        # Extract schedule time from task status
        # The time is typically in the format "Next Run Time: 12/31/2024 2:00:00 AM"
        schedule_time = "02:00"  # default
        if 'next_run' in task_status and task_status['next_run'] != 'Unknown':
            try:
                # Try to parse time from next run string
                time_match = re.search(r'(\d{1,2}:\d{2})', task_status['next_run'])
                if time_match:
                    schedule_time = time_match.group(1)
            except:
                pass
        
        # Determine schedule type from the task (default to daily)
        schedule_type = "daily"
        
        # Recreate the scheduled task with the new path
        success, message = create_scheduled_task(
            task_name=task_name,
            schedule_type=schedule_type,
            schedule_time=schedule_time,
            backup_dir=backup_dir,
            encrypt=encrypt,
            password=password
        )
        
        if success:
            return True, f"Scheduled task repaired: Updated path from\n{task_path}\nto\n{current_path}"
        else:
            return False, f"Failed to repair scheduled task: {message}"
    
    except Exception as e:
        logger.error(f"Error checking/repairing scheduled task: {e}")
        return False, f"Error during repair: {str(e)}"

# ---------------------------------------------------------------

class NextcloudRestoreWizard(tk.Tk):
    def __init__(self, scheduled_mode=False):
        super().__init__()
        
        # Store scheduled mode flag
        self.scheduled_mode = scheduled_mode
        
        # Initialize BackupHistoryManager before any early returns
        # This is essential for both GUI and scheduled mode backups
        self.backup_history = BackupHistoryManager()
        logger.info(f"Backup history manager initialized. Database: {self.backup_history.db_path}")
        
        # If in scheduled mode, skip all GUI initialization
        if scheduled_mode:
            return
        
        self.title("Nextcloud Restore & Backup Utility")
        self.geometry("900x900")  # Wider window for better content display
        self.minsize(700, 700)  # Set minimum window size to prevent excessive collapsing

        # Initialize theme
        self.current_theme = 'dark'
        self.theme_colors = THEMES[self.current_theme]
        
        # Initialize verbose logging mode (can be toggled in settings)
        self.verbose_logging = False
        
        # Configure root window
        self.configure(bg=self.theme_colors['bg'])

        self.header_frame = tk.Frame(self, bg=self.theme_colors['header_bg'])
        
        # Create container for header content with grid layout
        header_content = tk.Frame(self.header_frame, bg=self.theme_colors['header_bg'])
        header_content.pack(fill="x", expand=True, padx=10, pady=10)
        
        # Configure grid columns: left spacer, center title, right controls
        header_content.grid_columnconfigure(0, weight=1)  # Left spacer
        header_content.grid_columnconfigure(1, weight=0)  # Center title
        header_content.grid_columnconfigure(2, weight=1)  # Right spacer
        
        # Left spacer (empty)
        tk.Frame(header_content, bg=self.theme_colors['header_bg']).grid(row=0, column=0, sticky="ew")
        
        # Center title
        self.header_label = tk.Label(
            header_content, 
            text="Nextcloud Restore & Backup Utility", 
            font=("Arial", 22, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        )
        self.header_label.grid(row=0, column=1)
        
        # Right controls frame
        right_controls = tk.Frame(header_content, bg=self.theme_colors['header_bg'])
        right_controls.grid(row=0, column=2, sticky="e", padx=(10, 0))
        
        # Theme toggle icon button
        theme_icon = "☀️" if self.current_theme == 'dark' else "🌙"
        self.header_theme_btn = tk.Button(
            right_controls, 
            text=theme_icon, 
            font=("Arial", 18),
            width=2,
            height=1,
            bg=self.theme_colors['button_bg'], 
            fg=self.theme_colors['button_fg'],
            command=self.toggle_theme,
            relief=tk.FLAT,
            cursor="hand2",
            padx=2,
            pady=2
        )
        self.header_theme_btn.pack(side="left", padx=5)
        
        # Dropdown menu button
        self.header_menu_btn = tk.Button(
            right_controls, 
            text="☰", 
            font=("Arial", 20),
            width=2,
            bg=self.theme_colors['button_bg'], 
            fg=self.theme_colors['button_fg'],
            command=self.show_dropdown_menu,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.header_menu_btn.pack(side="left", padx=5)
        
        self.header_frame.pack(fill="x")

        self.status_label = tk.Label(
            self, 
            text="", 
            font=("Arial", 14),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['status_fg']
        )
        self.status_label.pack(pady=(0,10))

        self.body_frame = tk.Frame(self, bg=self.theme_colors['bg'])
        self.body_frame.pack(fill="both", expand=True)

        self.restore_password = None  # store password for restore workflow
        self.restore_backup_path = None
        self.restore_steps = [
            "Decrypting/extracting backup ...",
            "Generating Docker configuration ...",
            "Setting up containers ...",
            "Copying files into container ...",
            "Restoring database ...",
            "Setting permissions ...",
            "Restore complete!"
        ]
        
        # Multi-page wizard state
        self.wizard_page = 1
        self.wizard_data = {}
        
        # Extraction and detection state tracking
        self.extraction_attempted = False  # Track if extraction has been attempted
        self.extraction_successful = False  # Track if extraction succeeded
        self.current_backup_path = None  # Track which backup we extracted
        
        # Database auto-detection
        self.detected_dbtype = None
        self.detected_db_config = None
        self.db_auto_detected = False
        
        # Docker Compose detection
        self.detected_full_config = None
        self.detected_compose_usage = False
        self.detected_compose_file = None
        
        # Store references to database credential UI elements for conditional display
        # These will be set in create_wizard_page2()
        self.db_credential_packed_widgets = []  # Packed widgets (warning/instruction labels)
        self.db_credential_frame = None  # Frame containing grid widgets
        self.db_sqlite_message_label = None  # Label to show SQLite-specific message
        
        # Track current page for theme toggle and navigation
        self.current_page = 'landing'  # Possible values: 'landing', 'tailscale_wizard', 'tailscale_config', 'schedule_backup', 'wizard'
        
        # Domain management state
        self.domain_change_history = []  # Track changes for undo functionality
        self.original_domains = None  # Store original domains for restore defaults
        self.domain_status_cache = {}  # Cache domain status checks
        
        # Service health state (backup_history is initialized earlier for both GUI and scheduled mode)
        self.last_health_check = None
        self.health_check_cache = None
        
        # Bind window resize for responsive behavior
        self.bind("<Configure>", self._on_window_resize)
        self.last_window_size = (900, 900)
        
        # Check and repair scheduled task if app has been moved
        self.after(1000, self._check_scheduled_task_on_startup)

        self.show_landing()

    def check_docker_running(self):
        """
        Check if Docker is running and automatically attempt to start it if not.
        Uses background thread to avoid UI freezing during Docker startup.
        Returns: True if Docker is already running, False if not (including if starting)
        """
        # First check if Docker is already running
        if is_docker_running():
            return True
        
        # Docker is not running - attempt to start it automatically
        docker_status = detect_docker_status()
        
        # Only try to auto-start if Docker is installed but not running
        if docker_status['status'] == 'not_running':
            logger.info("Docker is not running, attempting to start Docker Desktop automatically...")
            
            # Try to start Docker Desktop in background thread to keep UI responsive
            def start_docker_background():
                """Background thread function to start Docker and wait for it"""
                # Update UI on main thread to show Docker is starting
                self.after(0, lambda: self.status_label.config(
                    text="🐳 Docker is starting in the background... Please wait",
                    fg=self.theme_colors['info_fg']
                ))
                
                if start_docker_desktop():
                    logger.info("Docker Desktop start command issued, waiting for Docker to become available...")
                    
                    # Wait for Docker to start (with retries)
                    max_wait_time = 30  # seconds
                    check_interval = 3  # seconds
                    elapsed = 0
                    
                    while elapsed < max_wait_time:
                        time.sleep(check_interval)
                        elapsed += check_interval
                        
                        # Check if Docker is running
                        if is_docker_running():
                            logger.info(f"Docker started successfully after {elapsed} seconds")
                            # Update UI on main thread with success message
                            self.after(0, lambda: self.status_label.config(
                                text="✓ Docker started successfully! You can now proceed with backup or restore.",
                                fg='#45bf55'
                            ))
                            return
                        
                        # Update status with elapsed time using after() for thread safety
                        # Create a proper closure by defining update function with current elapsed value
                        def update_status(current_elapsed):
                            self.status_label.config(
                                text=f"🐳 Docker is starting... {current_elapsed} seconds elapsed",
                                fg=self.theme_colors['info_fg']
                            )
                        
                        self.after(0, lambda e=elapsed: update_status(e))
                        logger.debug(f"Waiting for Docker to start... ({elapsed}s/{max_wait_time}s)")
                    
                    # Docker didn't start in time
                    error_msg = "Docker Desktop is starting but not ready yet. Please wait a moment and try again."
                    logger.error(error_msg)
                    self.after(0, lambda: self.status_label.config(
                        text=error_msg, 
                        fg=self.theme_colors['error_fg']
                    ))
                else:
                    # Could not start Docker Desktop (not found or error)
                    error_msg = "Could not start Docker automatically. Please start Docker Desktop manually."
                    logger.error(error_msg)
                    self.after(0, lambda: self.status_label.config(
                        text=error_msg, 
                        fg=self.theme_colors['error_fg']
                    ))
            
            # Start Docker in background thread to keep UI responsive
            threading.Thread(target=start_docker_background, daemon=True).start()
            return False  # Return False as Docker is not running yet (starting in background)
        else:
            # Docker is not installed or other error
            error_msg = docker_status['message']
            logger.error(f"Docker check failed: {error_msg}")
            self.status_label.config(text=error_msg, fg=self.theme_colors['error_fg'])
            return False

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        old_theme = self.current_theme
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.theme_colors = THEMES[self.current_theme]
        logger.info(f"THEME TOGGLE: Changed theme from {old_theme} to {self.current_theme}")
        
        # Update header theme icon
        theme_icon = "☀️" if self.current_theme == 'dark' else "🌙"
        self.header_theme_btn.config(text=theme_icon)
        
        self.apply_theme()
        logger.info("THEME TOGGLE: Applied theme to UI elements")
        # Refresh the current screen - maintain user's current page
        logger.info(f"THEME TOGGLE: Refreshing current page: {self.current_page}")
        self.refresh_current_page()
    
    def refresh_current_page(self):
        """Refresh the current page after theme change or other updates"""
        logger.info(f"REFRESH PAGE: Starting refresh for page: {self.current_page}")
        if self.current_page == 'tailscale_wizard':
            logger.info("REFRESH PAGE: Calling show_tailscale_wizard()")
            self.show_tailscale_wizard()
        elif self.current_page == 'tailscale_config':
            logger.info("REFRESH PAGE: Calling _show_tailscale_config()")
            self._show_tailscale_config()
        elif self.current_page == 'schedule_backup':
            logger.info("REFRESH PAGE: Calling show_schedule_backup()")
            self.show_schedule_backup()
        elif self.current_page == 'docker_error':
            # Docker error page - re-display the error
            logger.info("REFRESH PAGE: Calling show_docker_error_page()")
            if hasattr(self, 'current_docker_error'):
                self.show_docker_error_page(
                    self.current_docker_error['error_info'],
                    self.current_docker_error['stderr'],
                    self.current_docker_error['container_name'],
                    self.current_docker_error['port']
                )
        elif self.current_page == 'wizard':
            # Restore wizard - maintain current wizard page
            logger.info("REFRESH PAGE: Calling create_wizard()")
            self.create_wizard()
            if hasattr(self, 'wizard_page') and self.wizard_page > 1:
                logger.info(f"REFRESH PAGE: Restoring wizard page {self.wizard_page}")
                self.show_wizard_page(self.wizard_page)
        else:
            # Default to landing page for any other state
            logger.info("REFRESH PAGE: Calling show_landing() (default)")
            self.show_landing()
        logger.info("REFRESH PAGE: Page refresh complete")
    
    def show_dropdown_menu(self):
        """Show dropdown menu with advanced features"""
        # Create a toplevel menu window
        menu_window = tk.Toplevel(self)
        menu_window.title("Advanced Features")
        menu_window.transient(self)
        menu_window.resizable(False, False)
        
        # Position menu near the dropdown button
        menu_btn_x = self.header_menu_btn.winfo_rootx()
        menu_btn_y = self.header_menu_btn.winfo_rooty()
        menu_btn_height = self.header_menu_btn.winfo_height()
        
        # Set position below the menu button
        menu_window.geometry(f"+{menu_btn_x - 180}+{menu_btn_y + menu_btn_height + 5}")
        
        # Apply theme to menu window
        menu_window.configure(bg=self.theme_colors['bg'])
        
        # Menu frame
        menu_frame = tk.Frame(menu_window, bg=self.theme_colors['bg'], relief=tk.RAISED, borderwidth=2)
        menu_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Menu title
        tk.Label(
            menu_frame,
            text="Advanced Features",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(10, 5), padx=10)
        
        # Separator
        ttk.Separator(menu_frame, orient="horizontal").pack(fill="x", padx=10, pady=5)
        
        # Remote Access option
        tailscale_btn = tk.Button(
            menu_frame,
            text="🌐 Remote Access",
            font=("Arial", 11),
            width=25,
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=lambda: [menu_window.destroy(), self.show_tailscale_wizard()],
            relief=tk.FLAT,
            cursor="hand2",
            anchor="w",
            padx=10
        )
        tailscale_btn.pack(pady=5, padx=10, fill="x")
        
        # Add hover effects
        def on_enter(e):
            tailscale_btn.config(bg=self.theme_colors['button_active_bg'])
        
        def on_leave(e):
            tailscale_btn.config(bg=self.theme_colors['button_bg'])
        
        tailscale_btn.bind("<Enter>", on_enter)
        tailscale_btn.bind("<Leave>", on_leave)
        
        # View Logs option
        logs_btn = tk.Button(
            menu_frame,
            text="📋 View Logs",
            font=("Arial", 11),
            width=25,
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=lambda: [menu_window.destroy(), self.show_log_viewer()],
            relief=tk.FLAT,
            cursor="hand2",
            anchor="w",
            padx=10
        )
        logs_btn.pack(pady=5, padx=10, fill="x")
        
        # Add hover effects for logs button
        def on_enter_logs(e):
            logs_btn.config(bg=self.theme_colors['button_active_bg'])
        
        def on_leave_logs(e):
            logs_btn.config(bg=self.theme_colors['button_bg'])
        
        logs_btn.bind("<Enter>", on_enter_logs)
        logs_btn.bind("<Leave>", on_leave_logs)
        
        # Settings option
        settings_btn = tk.Button(
            menu_frame,
            text="⚙️ Settings",
            font=("Arial", 11),
            width=25,
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=lambda: [menu_window.destroy(), self.show_settings()],
            relief=tk.FLAT,
            cursor="hand2",
            anchor="w",
            padx=10
        )
        settings_btn.pack(pady=5, padx=10, fill="x")
        
        # Add hover effects for settings button
        def on_enter_settings(e):
            settings_btn.config(bg=self.theme_colors['button_active_bg'])
        
        def on_leave_settings(e):
            settings_btn.config(bg=self.theme_colors['button_bg'])
        
        settings_btn.bind("<Enter>", on_enter_settings)
        settings_btn.bind("<Leave>", on_leave_settings)
        
        # Close button
        close_btn = tk.Button(
            menu_frame,
            text="Close",
            font=("Arial", 10),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=menu_window.destroy,
            width=10
        )
        close_btn.pack(pady=(10, 10))
        
        # Make menu modal
        menu_window.grab_set()
    
    def show_settings(self):
        """Show settings dialog with verbose logging and other options"""
        logger.info("Opening settings dialog")
        
        # Create settings window
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("600x400")
        settings_window.transient(self)
        settings_window.resizable(False, False)
        
        # Apply theme
        settings_window.configure(bg=self.theme_colors['bg'])
        
        # Header frame
        header_frame = tk.Frame(settings_window, bg=self.theme_colors['header_bg'])
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Title
        tk.Label(
            header_frame,
            text="⚙️ Settings",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(pady=10)
        
        # Content frame
        content_frame = tk.Frame(settings_window, bg=self.theme_colors['bg'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Logging settings section
        logging_section = tk.LabelFrame(
            content_frame,
            text="Logging Settings",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            padx=15,
            pady=15
        )
        logging_section.pack(fill="x", pady=(0, 15))
        
        # Verbose logging checkbox
        verbose_var = tk.BooleanVar(value=self.verbose_logging)
        
        verbose_check = tk.Checkbutton(
            logging_section,
            text="Enable Verbose Logging",
            variable=verbose_var,
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            selectcolor=self.theme_colors['entry_bg'],
            activebackground=self.theme_colors['bg'],
            activeforeground=self.theme_colors['fg']
        )
        verbose_check.pack(anchor="w", pady=(0, 5))
        
        # Description label
        verbose_desc = tk.Label(
            logging_section,
            text="When enabled, the application logs additional detailed information\n"
                 "about all operations. This is useful for diagnosing issues but will\n"
                 "generate larger log files. Recommended for troubleshooting.",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="left",
            wraplength=500
        )
        verbose_desc.pack(anchor="w", padx=20)
        
        # Log file location info
        log_location_label = tk.Label(
            logging_section,
            text=f"Log file location:\n{LOG_FILE_PATH}",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="left"
        )
        log_location_label.pack(anchor="w", pady=(10, 0))
        
        # Button frame
        button_frame = tk.Frame(settings_window, bg=self.theme_colors['bg'])
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        def save_settings():
            # Update verbose logging setting
            old_value = self.verbose_logging
            self.verbose_logging = verbose_var.get()
            
            # Update logging level
            if self.verbose_logging:
                logger.setLevel(logging.DEBUG)
                for handler in logger.handlers:
                    handler.setLevel(logging.DEBUG)
                logger.info("Verbose logging enabled")
            else:
                logger.setLevel(logging.INFO)
                for handler in logger.handlers:
                    handler.setLevel(logging.INFO)
                logger.info("Verbose logging disabled")
            
            if old_value != self.verbose_logging:
                messagebox.showinfo(
                    "Settings Saved",
                    f"Verbose logging has been {'enabled' if self.verbose_logging else 'disabled'}.\n\n"
                    "The new setting will take effect immediately.",
                    parent=settings_window
                )
            
            settings_window.destroy()
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save Settings",
            font=("Arial", 12),
            bg="#45bf55",
            fg="white",
            width=15,
            command=save_settings
        )
        save_btn.pack(side="right", padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 12),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=15,
            command=settings_window.destroy
        )
        cancel_btn.pack(side="right", padx=5)
        
        # Make settings window modal
        settings_window.grab_set()
    
    def show_log_viewer(self):
        """Show log viewer window with current log contents"""
        logger.info("Opening log viewer")
        
        # Create log viewer window
        log_window = tk.Toplevel(self)
        log_window.title("Application Logs")
        log_window.geometry("900x600")
        log_window.transient(self)
        
        # Apply theme
        log_window.configure(bg=self.theme_colors['bg'])
        
        # Header frame
        header_frame = tk.Frame(log_window, bg=self.theme_colors['header_bg'])
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Title
        tk.Label(
            header_frame,
            text="Application Logs",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(side="left", padx=10)
        
        # Log file path label
        tk.Label(
            header_frame,
            text=f"Log file: {LOG_FILE_PATH}",
            font=("Arial", 9),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        ).pack(side="left", padx=10)
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(log_window, bg=self.theme_colors['bg'])
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Text widget
        log_text = tk.Text(
            text_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['fg'],
            font=("Courier", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=log_text.yview)
        
        # Read and display log contents
        def load_logs():
            try:
                if LOG_FILE_PATH.exists():
                    with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
                        log_contents = f.read()
                    log_text.delete(1.0, tk.END)
                    if log_contents.strip():
                        log_text.insert(1.0, log_contents)
                        # Scroll to bottom to show most recent logs
                        log_text.see(tk.END)
                    else:
                        # Log file exists but is empty
                        no_logs_message = """No log entries found.

Troubleshooting Tips:

1. If you just started the application, there may not be any logs yet.
   
2. If you experienced an error, try reproducing the issue - the logs will 
   capture the details automatically.
   
3. The application logs all operations to help diagnose issues:
   - Backup operations
   - Restore operations
   - Docker interactions
   - Configuration changes
   
4. If you need more detailed logs, enable Verbose Logging in Settings.

5. Log files are rotated automatically (max 10MB per file, 5 backup files).

Location: """ + str(LOG_FILE_PATH)
                        log_text.insert(1.0, no_logs_message)
                else:
                    # Log file doesn't exist
                    no_file_message = """Log file not found.

The log file will be created automatically when you perform operations.

Expected location: """ + str(LOG_FILE_PATH) + """

Troubleshooting:

1. Check if the Documents folder exists and is writable
2. Try performing a backup or restore operation to generate logs
3. If problems persist, check file permissions on the Documents folder
4. On Windows, ensure the application has write access to your Documents folder
5. On Linux/Mac, check that ~/Documents is accessible

Need Help?

• Check the GitHub repository for issues and documentation
• Enable Verbose Logging in Settings for more detailed information
• Report issues with log file creation on GitHub
"""
                    log_text.delete(1.0, tk.END)
                    log_text.insert(1.0, no_file_message)
            except Exception as e:
                error_message = f"""Error reading log file: {str(e)}

Troubleshooting:

1. Check if the log file location is accessible:
   {LOG_FILE_PATH}

2. Verify file permissions (the application needs read access)

3. Try closing other applications that might be using the log file

4. On Windows, check if antivirus is blocking access

5. Try running the application with appropriate permissions

If the problem persists, please report this issue on GitHub.
"""
                log_text.delete(1.0, tk.END)
                log_text.insert(1.0, error_message)
        
        # Button frame
        button_frame = tk.Frame(log_window, bg=self.theme_colors['bg'])
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Refresh button
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=load_logs,
            width=12
        )
        refresh_btn.pack(side="left", padx=5)
        
        # Open log folder button
        def open_log_folder():
            try:
                creation_flags = get_subprocess_creation_flags()
                log_folder = LOG_FILE_PATH.parent
                if platform.system() == 'Windows':
                    os.startfile(log_folder)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.Popen(['open', log_folder])
                else:  # Linux
                    subprocess.Popen(['xdg-open', log_folder])
                logger.info(f"Opened log folder: {log_folder}")
            except Exception as e:
                logger.error(f"Failed to open log folder: {str(e)}")
                messagebox.showerror("Error", f"Could not open log folder: {str(e)}")
        
        open_folder_btn = tk.Button(
            button_frame,
            text="📁 Open Log Folder",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=open_log_folder,
            width=15
        )
        open_folder_btn.pack(side="left", padx=5)
        
        # Clear logs button
        def clear_logs():
            result = messagebox.askyesno(
                "Clear Logs",
                "Are you sure you want to clear all logs?\n\nThis action cannot be undone.",
                parent=log_window
            )
            if result:
                try:
                    # Clear the log file
                    with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
                        f.write("")
                    logger.info("Log file cleared by user")
                    load_logs()
                    messagebox.showinfo("Success", "Logs cleared successfully.", parent=log_window)
                except Exception as e:
                    logger.error(f"Failed to clear logs: {str(e)}")
                    messagebox.showerror("Error", f"Could not clear logs: {str(e)}", parent=log_window)
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear Logs",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=clear_logs,
            width=12
        )
        clear_btn.pack(side="left", padx=5)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=log_window.destroy,
            width=12
        )
        close_btn.pack(side="right", padx=5)
        
        # Load logs initially
        load_logs()
    
    def apply_theme(self):
        """Apply the current theme to all root-level widgets and recursively to children"""
        self.configure(bg=self.theme_colors['bg'])
        self.header_frame.config(bg=self.theme_colors['header_bg'])
        self.header_label.config(
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        )
        self.header_theme_btn.config(
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg']
        )
        self.header_menu_btn.config(
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg']
        )
        self.status_label.config(
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['status_fg']
        )
        self.body_frame.config(bg=self.theme_colors['bg'])
        
        # Apply theme recursively to all children in body_frame and header_frame
        self.apply_theme_recursive(self.body_frame)
        self.apply_theme_recursive(self.header_frame)
    
    def apply_theme_recursive(self, parent):
        """
        Recursively apply theme to all child widgets
        Args:
            parent: The parent widget to start from
        """
        try:
            for child in parent.winfo_children():
                widget_class = child.winfo_class()
                
                if widget_class == 'Frame':
                    # Apply frame background
                    try:
                        current_bg = child.cget('bg')
                        # Only update if it's using default or theme-able colors
                        if current_bg in ['', 'SystemButtonFace', '#f0f0f0', '#1e1e1e', '#e3f2fd', '#e8f5e9', '#e8f4f8', '#1a3a4a', '#2a3a2a']:
                            child.config(bg=self.theme_colors['bg'])
                    except tk.TclError:
                        pass
                    # Recursively apply to frame's children
                    self.apply_theme_recursive(child)
                
                elif widget_class == 'Label':
                    # Apply label colors
                    try:
                        current_bg = child.cget('bg')
                        current_fg = child.cget('fg')
                        # Only update if using default colors
                        if current_bg in ['', 'SystemButtonFace', '#f0f0f0', '#1e1e1e', '#e3f2fd', '#e8f5e9', '#e8f4f8', '#1a3a4a', '#2a3a2a']:
                            child.config(bg=self.theme_colors['bg'])
                        if current_fg in ['', 'SystemButtonText', 'black', '#000000']:
                            child.config(fg=self.theme_colors['fg'])
                        # Special colors like error, hint, etc. are preserved
                    except tk.TclError:
                        pass
                
                elif widget_class == 'Button':
                    # Apply button colors (skip themed buttons with custom colors)
                    try:
                        current_bg = child.cget('bg')
                        # Only update generic buttons, not the themed main buttons
                        if current_bg in ['', 'SystemButtonFace', '#e0e0e0', '#2d2d2d']:
                            child.config(
                                bg=self.theme_colors['button_bg'],
                                fg=self.theme_colors['button_fg'],
                                activebackground=self.theme_colors['button_active_bg']
                            )
                    except tk.TclError:
                        pass
                
                elif widget_class == 'Entry':
                    # Apply entry colors
                    try:
                        child.config(
                            bg=self.theme_colors['entry_bg'],
                            fg=self.theme_colors['entry_fg'],
                            insertbackground=self.theme_colors['entry_fg']
                        )
                    except tk.TclError:
                        pass
                
                elif widget_class in ['Text', 'Listbox']:
                    # Apply to text widgets
                    try:
                        child.config(
                            bg=self.theme_colors['entry_bg'],
                            fg=self.theme_colors['entry_fg']
                        )
                    except tk.TclError:
                        pass
                
                # Continue recursion for container widgets
                elif hasattr(child, 'winfo_children'):
                    self.apply_theme_recursive(child)
                    
        except Exception as e:
            # Silently continue if a widget fails to update
            pass
    
    def apply_theme_to_widget(self, widget, widget_type='frame', **kwargs):
        """
        Apply theme colors to a specific widget
        Args:
            widget: The widget to apply theme to
            widget_type: Type of widget ('frame', 'label', 'button', 'entry', etc.)
            **kwargs: Additional color overrides (e.g., bg='#custom')
        """
        try:
            if widget_type == 'frame':
                widget.config(bg=kwargs.get('bg', self.theme_colors['bg']))
            elif widget_type == 'label':
                widget.config(
                    bg=kwargs.get('bg', self.theme_colors['bg']),
                    fg=kwargs.get('fg', self.theme_colors['fg'])
                )
            elif widget_type == 'button':
                # Check if it's a themed button (with custom color)
                if 'bg' in kwargs and kwargs['bg'] in [
                    THEMES['light']['backup_btn'], 
                    THEMES['light']['restore_btn'],
                    THEMES['light']['new_instance_btn'],
                    THEMES['light']['schedule_btn']
                ]:
                    # Map light theme button color to dark theme equivalent
                    color_map = {
                        THEMES['light']['backup_btn']: self.theme_colors['backup_btn'],
                        THEMES['light']['restore_btn']: self.theme_colors['restore_btn'],
                        THEMES['light']['new_instance_btn']: self.theme_colors['new_instance_btn'],
                        THEMES['light']['schedule_btn']: self.theme_colors['schedule_btn'],
                    }
                    bg_color = color_map.get(kwargs.get('bg'), self.theme_colors['button_bg'])
                else:
                    bg_color = kwargs.get('bg', self.theme_colors['button_bg'])
                
                widget.config(
                    bg=bg_color,
                    fg=kwargs.get('fg', 'white' if 'bg' in kwargs else self.theme_colors['button_fg']),
                    activebackground=kwargs.get('activebackground', self.theme_colors['button_active_bg'])
                )
            elif widget_type == 'entry':
                widget.config(
                    bg=kwargs.get('bg', self.theme_colors['entry_bg']),
                    fg=kwargs.get('fg', self.theme_colors['entry_fg']),
                    insertbackground=kwargs.get('insertbackground', self.theme_colors['entry_fg'])
                )
        except tk.TclError:
            # Widget doesn't support these options
            pass

    def show_landing(self):
        # Clean up wizard mouse wheel bindings if coming from wizard
        if hasattr(self, 'wizard_canvas'):
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
        
        self.current_page = 'landing'
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        self.status_label.config(text="")
        landing_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        landing_frame.pack(fill="both", expand=True)
        
        # Create buttons with increased width for better label visibility
        button_width = 30  # Increased from 24 to 30 for better text visibility
        
        self.backup_btn = tk.Button(
            landing_frame, text="🔄 Backup Now", font=("Arial", 16, "bold"),
            height=2, width=button_width, bg=self.theme_colors['backup_btn'], fg="white", 
            command=self.start_backup
        )
        self.backup_btn.pack(pady=(18,6))
        ToolTip(self.backup_btn, "Create a backup of your Nextcloud data, config, and database")
        
        self.restore_btn = tk.Button(
            landing_frame, text="🛠 Restore from Backup", font=("Arial", 16, "bold"),
            height=2, width=button_width, bg=self.theme_colors['restore_btn'], fg="white", 
            command=self.start_restore
        )
        self.restore_btn.pack(pady=6)
        ToolTip(self.restore_btn, "Restore your Nextcloud from a previous backup file")
        
        self.new_btn = tk.Button(
            landing_frame, text="✨ Start New Nextcloud Instance", font=("Arial", 16, "bold"),
            height=2, width=button_width, bg=self.theme_colors['new_instance_btn'], fg="white", 
            command=self.start_new_instance_workflow
        )
        self.new_btn.pack(pady=(6,12))
        ToolTip(self.new_btn, "Set up a brand new Nextcloud instance with Docker")
        
        # Add scheduled backup button
        self.schedule_btn = tk.Button(
            landing_frame, text="📅 Schedule Backup", font=("Arial", 16, "bold"),
            height=2, width=button_width, bg=self.theme_colors['schedule_btn'], fg="white", 
            command=self.show_schedule_backup
        )
        self.schedule_btn.pack(pady=(6,12))
        ToolTip(self.schedule_btn, "Configure automatic backups to run on a schedule")
        
        # Add backup history button
        backup_history_btn = tk.Button(
            landing_frame, text="📜 Backup History", font=("Arial", 14),
            width=button_width, bg=self.theme_colors['button_bg'], fg=self.theme_colors['button_fg'],
            command=self.show_backup_history
        )
        backup_history_btn.pack(pady=6)
        ToolTip(backup_history_btn, "View and manage previous backups")
        
        # Show schedule status if exists
        self._update_schedule_status_label(landing_frame)
        
        # Add service health dashboard
        self._add_health_dashboard(landing_frame)

    # ----- Backup logic -----
    def start_backup(self):
        # Check if Docker is running before proceeding
        if not self.check_docker_running():
            self.show_landing()
            return
        
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        self.status_label.config(text="Backup Wizard: Select backup destination folder.")
        backup_dir = filedialog.askdirectory(title="Select backup destination folder")
        if not backup_dir:
            self.show_landing()
            return

        # --- Detect nextcloud container ---
        container_names = get_nextcloud_container_name()
        chosen_container = None
        if not container_names:
            messagebox.showerror("Error", "No running Nextcloud container found. Please start your Nextcloud container before backup.")
            self.show_landing()
            return
        else:
            chosen_container = container_names

        # Enhanced database type detection with multiple strategies
        self.status_label.config(text="Detecting database type...")
        self.update_idletasks()
        
        # Strategy 1: List all database containers
        print("Scanning for database containers...")
        db_containers = list_running_database_containers()
        
        # Strategy 2: Use comprehensive inspection method
        dbtype = None
        db_config = None
        db_info = None
        
        if db_containers:
            print(f"Found {len(db_containers)} database container(s)")
            dbtype, db_info = detect_db_from_container_inspection(chosen_container, db_containers)
            if db_info and 'config' in db_info:
                db_config = db_info['config']
        
        # If comprehensive detection didn't work, try simple config.php reading
        if not dbtype:
            print("Trying direct config.php detection...")
            dbtype, db_config = detect_database_type_from_container(chosen_container)
        
        if dbtype:
            # Successfully detected - show info to user
            db_type_display = {
                'pgsql': 'PostgreSQL',
                'mysql': 'MySQL/MariaDB',
                'sqlite': 'SQLite'
            }.get(dbtype, dbtype)
            
            info_msg = f"✓ Detected database: {db_type_display}"
            if db_config and 'dbname' in db_config:
                info_msg += f"\n  Database name: {db_config['dbname']}"
            if db_info and 'container' in db_info:
                info_msg += f"\n  Container: {db_info['container']}"
            
            print(info_msg)
            self.status_label.config(text=f"Database detected: {db_type_display}")
            self.update_idletasks()
        else:
            # Could not detect - ask user only as last resort
            print("Could not auto-detect database type, asking user...")
            response = messagebox.askyesnocancel(
                "Database Type Unknown",
                "Could not automatically detect the database type from your Nextcloud container.\n\n"
                "Is your Nextcloud using PostgreSQL?\n"
                "• Yes = PostgreSQL (default)\n"
                "• No = MySQL/MariaDB\n"
                "• Cancel = Abort backup\n\n"
                "Note: SQLite databases are backed up automatically with the data folder."
            )
            if response is None:  # Cancel
                self.show_landing()
                return
            elif response:  # Yes = PostgreSQL
                dbtype = 'pgsql'
            else:  # No = MySQL
                dbtype = 'mysql'
        
        # Check if required database dump utility is available
        if dbtype not in ['sqlite', 'sqlite3']:
            utility_installed, utility_name = check_database_dump_utility(dbtype)
            
            while not utility_installed:
                # Prompt user to install the utility
                retry = prompt_install_database_utility(self, dbtype, utility_name)
                if not retry:
                    # User cancelled
                    self.show_landing()
                    return
                # Check again after user says they installed it
                utility_installed, utility_name = check_database_dump_utility(dbtype)
                if not utility_installed:
                    messagebox.showwarning(
                        "Utility Not Found",
                        f"The utility '{utility_name}' is still not found.\n"
                        "Please ensure it's installed and in your system PATH."
                    )
        
        # Store detected database type for backup process
        self.backup_dbtype = dbtype
        self.backup_db_config = db_config
        
        # Show folder selection dialog
        self._show_folder_selection(backup_dir, chosen_container, dbtype, db_config)

    def _show_folder_selection(self, backup_dir, container_name, dbtype, db_config):
        """Show folder selection UI for selective backup"""
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        self.status_label.config(text="Select Folders to Backup")
        
        main_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        main_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="📁 Select Folders to Include in Backup",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        title_label.pack(pady=(10, 15))
        
        # Info text
        info_label = tk.Label(
            main_frame,
            text="Choose which folders to include. Critical folders are required.",
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        )
        info_label.pack(pady=(0, 15))
        
        # Folder options with checkboxes
        folder_frame = tk.Frame(main_frame, bg=self.theme_colors['bg'])
        folder_frame.pack(pady=10)
        
        folder_vars = {}
        folders = [
            ("config", True, "Configuration files (Required)"),
            ("data", True, "User data and files (Required)"),
            ("apps", False, "Standard Nextcloud apps"),
            ("custom_apps", False, "Custom/third-party apps"),
        ]
        
        for folder, is_critical, description in folders:
            row_frame = tk.Frame(folder_frame, bg=self.theme_colors['bg'])
            row_frame.pack(fill="x", pady=5)
            
            var = tk.BooleanVar(value=True)
            folder_vars[folder] = (var, is_critical)
            
            cb = tk.Checkbutton(
                row_frame,
                text=f"{folder}",
                variable=var,
                font=("Arial", 11, "bold" if is_critical else "normal"),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['fg'],
                selectcolor=self.theme_colors['entry_bg'],
                state=tk.DISABLED if is_critical else tk.NORMAL
            )
            cb.pack(side="left", padx=(0, 10))
            
            desc_label = tk.Label(
                row_frame,
                text=f"- {description}",
                font=("Arial", 9),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['hint_fg'],
                anchor="w"
            )
            desc_label.pack(side="left")
            
            if is_critical:
                ToolTip(cb, "This folder is required for a complete backup")
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.theme_colors['bg'])
        button_frame.pack(pady=20)
        
        back_btn = tk.Button(
            button_frame,
            text="← Back",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_landing
        )
        back_btn.pack(side="left", padx=5)
        
        continue_btn = tk.Button(
            button_frame,
            text="Continue →",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['backup_btn'],
            fg="white",
            command=lambda: self._show_encryption_dialog(
                backup_dir, container_name, dbtype, db_config, folder_vars
            )
        )
        continue_btn.pack(side="left", padx=5)
        ToolTip(continue_btn, "Proceed to encryption options")
    
    def _show_encryption_dialog(self, backup_dir, container_name, dbtype, db_config, folder_vars):
        """Show encryption password dialog"""
        # Store selected folders for backup process
        self.selected_backup_folders = [
            (folder, is_critical)
            for folder, (var, is_critical) in folder_vars.items()
            if var.get()
        ]
        
        # Store database info for backup
        self.backup_dbtype = dbtype
        self.backup_db_config = db_config
        
        self.ask_encryption_password_inline(backup_dir, container_name)
    
    def ask_encryption_password_inline(self, backup_dir, container_name):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        frame.pack(pady=30, fill="both", expand=True)
        
        tk.Label(
            frame,
            text="🔒 Backup Encryption",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(20, 10))
        
        btn_back = tk.Button(
            frame,
            text="← Back",
            font=("Arial", 10),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_landing
        )
        btn_back.pack(pady=8, anchor="center")
        
        tk.Label(
            frame,
            text="Enter password to encrypt your backup (leave blank for no encryption):",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=10, anchor="center")
        
        # Create a container for the password entry to control its width responsively
        pwd_container = tk.Frame(frame, bg=self.theme_colors['bg'])
        pwd_container.pack(pady=8, fill="x", padx=100)
        pwd_entry = tk.Entry(
            pwd_container,
            font=("Arial", 13),
            show="*",
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg']
        )
        pwd_entry.pack(fill="x", expand=True)
        ToolTip(pwd_entry, "Use a strong password to protect sensitive data. Leave empty to skip encryption.")
        
        def submit_pwd():
            encryption_password = pwd_entry.get()
            encrypt = bool(encryption_password)
            self.progressbar = ttk.Progressbar(self.body_frame, length=520, mode='determinate', maximum=10)
            self.progressbar.pack(pady=10)
            self.progress_message = tk.Label(
                self.body_frame,
                text="",
                font=("Arial", 13),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['fg']
            )
            self.progress_message.pack(pady=10)
            threading.Thread(target=self.run_backup_process, args=(backup_dir, encrypt, encryption_password, container_name), daemon=True).start()
        
        tk.Button(
            frame,
            text="Start Backup",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['backup_btn'],
            fg="white",
            command=submit_pwd
        ).pack(pady=10)

    def set_progress(self, step, msg):
        if hasattr(self, "progressbar") and self.progressbar:
            self.progressbar['value'] = step
        if hasattr(self, "progress_message") and self.progress_message:
            self.progress_message.config(text=msg)
        self.status_label.config(text=msg)
        self.update_idletasks()

    def run_backup_process(self, backup_dir, encrypt, encryption_password, container_name):
        NEXTCLOUD_PATH = "/var/www/html"
        try:
            self.set_progress(1, "Preparing backup ...")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_temp = os.path.join(tempfile.gettempdir(), f"ncbackup_{timestamp}")
            os.makedirs(backup_temp, exist_ok=True)
            backup_file = os.path.join(backup_dir, f"nextcloud-backup-{timestamp}.tar.gz")
            encrypted_file = backup_file + ".gpg"

            # Use selected folders if available, otherwise use defaults
            if hasattr(self, 'selected_backup_folders') and self.selected_backup_folders:
                folders_to_copy = self.selected_backup_folders
            else:
                folders_to_copy = [
                    ("config", True),
                    ("data", True),
                    ("apps", False),
                    ("custom_apps", False),
                ]
            copied_folders = []
            skipped_folders = []
            for idx, (folder, is_critical) in enumerate(folders_to_copy, start=2):
                self.set_progress(idx, f"Checking and copying '{folder}' ...")
                check = subprocess.run(
                    f'docker exec {container_name} test -d {NEXTCLOUD_PATH}/{folder}',
                    shell=True
                )
                if check.returncode == 0:
                    try:
                        subprocess.run(
                            f'docker cp {container_name}:{NEXTCLOUD_PATH}/{folder} {backup_temp}/{folder}',
                            shell=True, check=True
                        )
                        copied_folders.append(folder)
                        self.set_progress(idx, f"Copied '{folder}'")
                    except Exception as cp_err:
                        self.set_progress(idx, f"Failed to copy '{folder}' but continuing ...")
                else:
                    if is_critical:
                        self.set_progress(0, f"CRITICAL FOLDER '{folder}' IS MISSING! Backup aborted.")
                        messagebox.showerror("Backup failed", f"Critical folder '{folder}' is missing from container.\nBackup cannot continue.")
                        if hasattr(self, "progressbar") and self.progressbar:
                            self.progressbar.destroy()
                            self.progressbar = None
                        if hasattr(self, "progress_message") and self.progress_message:
                            self.progress_message.destroy()
                            self.progress_message = None
                        shutil.rmtree(backup_temp, ignore_errors=True)
                        self.show_landing()
                        return
                    else:
                        skipped_folders.append(folder)
                        self.set_progress(idx, f"Skipping '{folder}' (not found; not critical)")

            # Database backup - handle different database types
            dbtype = getattr(self, 'backup_dbtype', 'pgsql')  # Default to PostgreSQL if not set
            db_config = getattr(self, 'backup_db_config', {})
            
            if dbtype in ['sqlite', 'sqlite3']:
                # SQLite database is already backed up with the data folder
                self.set_progress(6, "SQLite database backed up with data folder")
                print("✓ SQLite database backup: included in data folder")
            else:
                # MySQL or PostgreSQL - need to dump
                db_name = dbtype.upper() if dbtype == 'pgsql' else 'MySQL/MariaDB'
                self.set_progress(6, f"Dumping {db_name} database ...")
                dump_file = os.path.join(backup_temp, "nextcloud-db.sql")
                db_dump_result = None
                
                try:
                    if dbtype == 'pgsql':
                        # PostgreSQL dump
                        db_container = get_postgres_container_name() or POSTGRES_CONTAINER_NAME
                        db_name_actual = db_config.get('dbname', POSTGRES_DB)
                        db_user = db_config.get('dbuser', POSTGRES_USER)
                        db_password = POSTGRES_PASSWORD  # We don't have the actual password from config
                        
                        db_dump_cmd = f'docker exec {db_container} bash -c "PGPASSWORD=\'{db_password}\' pg_dump -U {db_user} {db_name_actual}"'
                    elif dbtype in ['mysql', 'mariadb']:
                        # MySQL/MariaDB dump
                        # Try to find MySQL container or use the database host from config
                        db_host = db_config.get('dbhost', 'db')
                        db_name_actual = db_config.get('dbname', 'nextcloud')
                        db_user = db_config.get('dbuser', 'nextcloud')
                        
                        # Try dumping from Nextcloud container if it has mysql client
                        db_dump_cmd = f'docker exec {container_name} bash -c "mysqldump -h {db_host} -u {db_user} -p{POSTGRES_PASSWORD} {db_name_actual}"'
                    else:
                        raise Exception(f"Unsupported database type: {dbtype}")
                    
                    with open(dump_file, "w", encoding="utf8") as f:
                        proc = subprocess.Popen(db_dump_cmd, shell=True, stdout=f, stderr=subprocess.PIPE)
                        proc.wait()
                        db_dump_result = proc.returncode
                        
                except Exception as e:
                    print(f"Database dump error: {e}")
                    db_dump_result = 1
                
                if db_dump_result != 0:
                    self.set_progress(0, f"CRITICAL: Database backup failed! Backup aborted.")
                    messagebox.showerror("Backup failed", f"Could not dump {db_name} database. Backup cannot continue.\n\nPlease ensure:\n- Database container is running\n- Database credentials are correct\n- Database dump utility is available")
                    shutil.rmtree(backup_temp, ignore_errors=True)
                    if hasattr(self, "progressbar") and self.progressbar:
                        self.progressbar.destroy()
                        self.progressbar = None
                    if hasattr(self, "progress_message") and self.progress_message:
                        self.progress_message.destroy()
                        self.progress_message = None
                    self.show_landing()
                    return

            self.set_progress(7, "Creating archive ...")
            shutil.make_archive(backup_file.replace('.tar.gz',''), 'gztar', backup_temp)
            if encrypt and encryption_password:
                self.set_progress(8, "Encrypting archive ...")
                encrypt_file_gpg(backup_file, encrypted_file, encryption_password)
                os.remove(backup_file)
                final_file = encrypted_file
            else:
                final_file = backup_file
            self.set_progress(9, "Cleaning up temp files ...")
            shutil.rmtree(backup_temp, ignore_errors=True)

            summary = (
                f"Backup finished!\n\n"
                f"Critical folders backed up:\n"
                f"- config\n"
                f"- data\n"
                f"- database\n"
            )
            if copied_folders:
                summary += f"\nOther folders backed up:\n" + "\n".join(f"- {f}" for f in copied_folders if f not in ["config", "data"])
            if skipped_folders:
                summary += (
                    f"\nSkipped non-critical folders (these are usually safe to skip):\n"
                    + "\n".join(f"- {f}" for f in skipped_folders)
                    + "\n"
                    + "Missing these folders will only affect extra/custom apps. Your data and config are safe."
                )
            summary += f"\n\nBackup saved to:\n{final_file}"

            # Add backup to history
            logger.info(f"GUI BACKUP: Adding to history - File: {final_file}")
            folders_list = ['config', 'data'] + [f for f in copied_folders if f not in ['config', 'data']]
            backup_id = self.backup_history.add_backup(
                backup_path=final_file,
                database_type=dbtype,
                folders=folders_list,
                encrypted=bool(encrypt and encryption_password),
                notes=""
            )
            logger.info(f"GUI BACKUP: Successfully added to history with ID {backup_id}")
            
            # Run backup verification
            self.set_progress(10, "Verifying backup integrity...")
            verification_status, verification_details = verify_backup_integrity(
                final_file,
                encryption_password if encrypt else None
            )
            self.backup_history.update_verification(backup_id, verification_status, verification_details)
            
            # Add verification result to summary
            verification_icon = {'success': '✅', 'warning': '⚠️', 'error': '❌'}.get(verification_status, '❓')
            summary += f"\n\n{verification_icon} Verification: {verification_details}"
            
            self.set_progress(10, "Backup complete!")
            messagebox.showinfo("Backup Complete", summary)
        except Exception as e:
            tb = traceback.format_exc()
            self.set_progress(0, "Backup failed")
            self.error_label.config(text=f"Backup failed:\n{e}\n{tb}")
            print(tb)
        if hasattr(self, "progressbar") and self.progressbar:
            self.progressbar.destroy()
            self.progressbar = None
        if hasattr(self, "progress_message") and self.progress_message:
            self.progress_message.destroy()
            self.progress_message = None
        self.show_landing()

    # --- Restore logic with in-GUI password, progress bar, live file output, and error label ---
    def start_restore(self):
        # Enhanced Docker detection with installation prompt
        if not is_tool_installed('docker'):
            # Docker is not installed at all
            for widget in self.body_frame.winfo_children():
                widget.destroy()
            self.status_label.config(text="Docker Required for Restore")
            
            # Show installation prompt
            def proceed_after_install():
                # Check if Docker is now installed
                if not is_tool_installed('docker'):
                    messagebox.showerror(
                        "Docker Not Found",
                        "Docker is still not installed. Please install Docker and try again.",
                        parent=self
                    )
                    self.show_landing()
                    return
                # Check if Docker is running
                if not self.check_docker_running():
                    self.show_landing()
                    return
                # Proceed to wizard
                self.current_page = 'wizard'
                for widget in self.body_frame.winfo_children():
                    widget.destroy()
                self.status_label.config(text="Restore Wizard: Select backup archive to restore.")
                self.create_wizard()
            
            prompt_install_docker_link(self, self.status_label, proceed_after_install)
            return
        
        # Docker is installed, check if it's running
        if not self.check_docker_running():
            self.show_landing()
            return
        
        self.current_page = 'wizard'
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        self.status_label.config(text="Restore Wizard: Select backup archive to restore.")
        self.create_wizard()

    def create_wizard(self):
        """Create multi-page restore wizard with scrollable canvas"""
        # Reset wizard state
        self.wizard_page = 1
        
        # Create canvas with scrollbar for scrollable content
        self.wizard_canvas = tk.Canvas(
            self.body_frame,
            bg=self.theme_colors['bg'],
            highlightthickness=0
        )
        self.wizard_scrollbar = tk.Scrollbar(
            self.body_frame,
            orient="vertical",
            command=self.wizard_canvas.yview
        )
        
        # Create frame inside canvas for content
        self.wizard_scrollable_frame = tk.Frame(
            self.wizard_canvas,
            width=600,
            bg=self.theme_colors['bg']
        )
        
        # Configure canvas
        self.wizard_canvas.configure(yscrollcommand=self.wizard_scrollbar.set)
        
        # Pack scrollbar and canvas
        self.wizard_scrollbar.pack(side="right", fill="y")
        self.wizard_canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas
        self.wizard_canvas_window = self.wizard_canvas.create_window(
            (0, 0),
            window=self.wizard_scrollable_frame,
            anchor="nw"
        )
        
        # Configure scroll region when content changes
        def configure_scroll_region(event=None):
            self.wizard_canvas.configure(scrollregion=self.wizard_canvas.bbox("all"))
            # Center the content horizontally
            canvas_width = self.wizard_canvas.winfo_width()
            if canvas_width > 1:
                content_width = min(600, canvas_width - 20)
                x_offset = (canvas_width - content_width) // 2
                self.wizard_canvas.itemconfig(self.wizard_canvas_window, width=content_width)
                self.wizard_canvas.coords(self.wizard_canvas_window, x_offset, 10)
        
        self.wizard_scrollable_frame.bind("<Configure>", configure_scroll_region)
        self.wizard_canvas.bind("<Configure>", configure_scroll_region)
        
        # Add mouse wheel scrolling support
        def on_mouse_wheel(event):
            """Handle mouse wheel scrolling"""
            if event.num == 5 or event.delta < 0:
                self.wizard_canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                self.wizard_canvas.yview_scroll(-1, "units")
        
        # Bind mouse wheel events (supporting Windows, Mac, and Linux)
        self.wizard_canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows/Mac
        self.wizard_canvas.bind_all("<Button-4>", on_mouse_wheel)    # Linux scroll up
        self.wizard_canvas.bind_all("<Button-5>", on_mouse_wheel)    # Linux scroll down
        
        # Show first page
        self.show_wizard_page(1)
    
    def show_wizard_page(self, page_num):
        """Display a specific page of the wizard"""
        # Clear current page
        for widget in self.wizard_scrollable_frame.winfo_children():
            widget.destroy()
        
        frame = self.wizard_scrollable_frame
        self.wizard_page = page_num
        
        # Page title (subheader) - full width with padding
        page_title = f"Restore Wizard: Page {page_num} of 3"
        tk.Label(frame, text=page_title, font=("Arial", 14), 
                 bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=(10, 10), fill="x", padx=40)
        
        # Return to Main Menu button - full width with padding
        btn_back = tk.Button(frame, text="Return to Main Menu", font=("Arial", 12), 
                            bg=self.theme_colors['button_bg'], fg=self.theme_colors['button_fg'],
                            command=self.show_landing)
        btn_back.pack(pady=8, fill="x", padx=40)
        
        if page_num == 1:
            self.create_wizard_page1(frame)
        elif page_num == 2:
            self.create_wizard_page2(frame)
        elif page_num == 3:
            self.create_wizard_page3(frame)
        
        # Apply theme recursively to all wizard page widgets
        self.apply_theme_recursive(frame)
        
        # Navigation buttons - full width with padding
        nav_frame = tk.Frame(frame, bg=self.theme_colors['bg'])
        nav_frame.pack(pady=(30, 20), fill="x", padx=40)
        
        if page_num > 1:
            tk.Button(
                nav_frame, 
                text="← Back", 
                font=("Arial", 12, "bold"),
                width=15,
                bg=self.theme_colors['button_bg'],
                fg=self.theme_colors['button_fg'],
                command=lambda: self.wizard_navigate(-1)
            ).pack(side="left", padx=10)
        
        if page_num < 3:
            tk.Button(
                nav_frame, 
                text="Next →", 
                font=("Arial", 12, "bold"),
                bg="#3daee9",
                fg="white",
                width=15,
                command=lambda: self.wizard_navigate(1)
            ).pack(side="left", padx=10)
        else:
            # Start Restore button on final page
            self.restore_now_btn = tk.Button(
                nav_frame, 
                text="Start Restore", 
                font=("Arial", 14, "bold"),
                bg="#45bf55",
                fg="white",
                width=18,
                command=self.validate_and_start_restore
            )
            self.restore_now_btn.pack(side="left", padx=10)
        
        # Error label - full width with padding
        self.error_label = tk.Label(frame, text="", font=("Arial", 12), 
                                    bg=self.theme_colors['bg'], fg="red", wraplength=500)
        self.error_label.pack(pady=10, fill="x", padx=40)
        
        # Progress section (shown after restore starts) - full width with padding
        self.progressbar = ttk.Progressbar(frame, length=520, mode='determinate', maximum=100)
        self.progressbar.pack(pady=(30, 3), fill="x", padx=40)
        self.progressbar.pack_forget()  # Hide initially
        
        self.progress_label = tk.Label(frame, text="0%", font=("Arial", 13),
                                       bg=self.theme_colors['bg'], fg=self.theme_colors['fg'])
        self.progress_label.pack(fill="x", padx=40)
        self.progress_label.pack_forget()  # Hide initially
        
        self.process_label = tk.Label(frame, text="", font=("Arial", 11), 
                                      bg=self.theme_colors['bg'], fg="gray", 
                                      anchor="center", justify="center")
        self.process_label.pack(padx=40, pady=4, fill="x")
        self.process_label.pack_forget()  # Hide initially
        
    def create_wizard_page1(self, parent):
        """Page 1: Backup Archive Selection and Decryption Password"""
        # Add info box about Quick Restore mode
        info_frame = tk.Frame(parent, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
        info_frame.pack(pady=(10, 15), fill="x", padx=40)
        tk.Label(info_frame, text="ℹ️ Quick Restore Mode", font=("Arial", 11, "bold"), 
                 bg=self.theme_colors['info_bg'], fg=self.theme_colors['info_fg']).pack(pady=(8, 3), fill="x", padx=10)
        tk.Label(info_frame, text="This wizard will guide you through the restore process step-by-step.\nAll Docker commands and configuration will be handled automatically.", 
                 font=("Arial", 9), bg=self.theme_colors['info_bg'], fg=self.theme_colors['info_fg'],
                 wraplength=500, justify="center").pack(pady=(0, 8), fill="x", padx=10)
        
        # Section 1: Backup file selection - full width with padding
        tk.Label(parent, text="Step 1: Select Backup Archive", font=("Arial", 14, "bold"),
                 bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=(20, 5), fill="x", padx=40)
        tk.Label(parent, text="Choose the backup file to restore (.tar.gz.gpg or .tar.gz)", font=("Arial", 10), 
                 bg=self.theme_colors['bg'], fg="gray").pack(pady=(0, 5), fill="x", padx=40)
        
        # Entry field - full width with padding
        self.backup_entry = tk.Entry(parent, font=("Arial", 11),
                                     bg=self.theme_colors['entry_bg'], fg=self.theme_colors['entry_fg'],
                                     insertbackground=self.theme_colors['entry_fg'])
        self.backup_entry.pack(pady=5, fill="x", padx=40)
        
        # Restore saved value if exists
        if 'backup_path' in self.wizard_data:
            self.backup_entry.delete(0, tk.END)
            self.backup_entry.insert(0, self.wizard_data['backup_path'])
        
        # Suggest default backup location
        default_backup_hint = tk.Label(parent, text="💡 Tip: Default backup location is usually in Documents/NextcloudBackups", 
                 font=("Arial", 9), bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg'])
        default_backup_hint.pack(pady=(0, 5), fill="x", padx=40)
        ToolTip(default_backup_hint, "Most users save backups in their Documents folder")
        
        tk.Button(parent, text="Browse...", font=("Arial", 11), width=20, 
                 bg=self.theme_colors['button_bg'], fg=self.theme_colors['button_fg'],
                 command=self.browse_backup).pack(pady=5, fill="x", padx=40)
        
        # Section 2: Decryption password - full width with padding
        tk.Label(parent, text="Step 2: Decryption Password", font=("Arial", 14, "bold"),
                 bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=(30, 5), fill="x", padx=40)
        tk.Label(parent, text="Enter password if backup is encrypted (.gpg)", font=("Arial", 10), 
                 bg=self.theme_colors['bg'], fg="gray").pack(pady=(0, 5), fill="x", padx=40)
        
        # Password entry - full width with padding
        self.password_entry = tk.Entry(parent, show="*", font=("Arial", 12),
                                       bg=self.theme_colors['entry_bg'], fg=self.theme_colors['entry_fg'],
                                       insertbackground=self.theme_colors['entry_fg'])
        self.password_entry.pack(pady=5, fill="x", padx=40)
        
        # Restore saved value if exists
        if 'password' in self.wizard_data:
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, self.wizard_data['password'])
    
    def create_wizard_page2(self, parent):
        """Page 2: Database Configuration and Admin Credentials"""
        # Section 3: Database credentials - full width with padding
        tk.Label(parent, text="Step 3: Database Configuration", font=("Arial", 14, "bold")).pack(pady=(20, 5), fill="x", padx=40)
        
        # Info about auto-detection - full width with padding
        info_frame = tk.Frame(parent, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
        info_frame.pack(pady=(5, 10), fill="x", padx=40)
        tk.Label(info_frame, text="ℹ️ Database Type Auto-Detection", font=("Arial", 10, "bold"), 
                 bg=self.theme_colors['info_bg'], fg=self.theme_colors['info_fg']).pack(pady=(5, 2), fill="x", padx=10)
        tk.Label(info_frame, text="The restore process will automatically detect your database type (SQLite, PostgreSQL, MySQL)", 
                 font=("Arial", 9), bg=self.theme_colors['info_bg'], fg=self.theme_colors['info_fg'],
                 wraplength=500, justify="center").pack(pady=2, fill="x", padx=10)
        tk.Label(info_frame, text="from the config.php file in your backup. You only need to provide credentials for MySQL/PostgreSQL.", 
                 font=("Arial", 9), bg=self.theme_colors['info_bg'], fg=self.theme_colors['info_fg'],
                 wraplength=500, justify="center").pack(pady=(0, 5), fill="x", padx=10)
        
        # SQLite-specific message (hidden by default, shown when SQLite is detected)
        # This message informs users that SQLite doesn't require separate database credentials
        self.db_sqlite_message_label = tk.Label(
            parent, 
            text="✓ SQLite Database Detected\n\nNo database credentials are needed for SQLite.\nThe database is stored as a single file within your backup.",
            font=("Arial", 11), 
            fg="#2e7d32",  # Dark green color
            bg="#e8f5e9",  # Light green background
            relief="solid",
            borderwidth=1,
            padx=20,
            pady=15,
            justify="center"
        )
        # Initially hidden - will be shown if SQLite is detected
        # Note: We don't pack it here; it will be shown/hidden dynamically
        
        # Warning and instructions for non-SQLite databases
        # These will be hidden when SQLite is detected
        warning_label = tk.Label(parent, text="⚠️ Enter the database credentials from your ORIGINAL Nextcloud setup", font=("Arial", 10, "bold"), fg="red")
        warning_label.pack(pady=(5, 0), fill="x", padx=40)
        
        instruction_label1 = tk.Label(parent, text="These credentials are stored in your backup and must match exactly", font=("Arial", 9), fg="gray")
        instruction_label1.pack(fill="x", padx=40)
        
        instruction_label2 = tk.Label(parent, text="💡 Tip: Default values are pre-filled, but verify they match your original setup", font=("Arial", 9), fg="gray")
        instruction_label2.pack(pady=(0, 10), fill="x", padx=40)
        
        db_frame = tk.Frame(parent)
        db_frame.pack(pady=10, fill="x", padx=40)
        
        # Configure column weights for responsive layout
        db_frame.grid_columnconfigure(0, weight=0)  # Label column - fixed width
        db_frame.grid_columnconfigure(1, weight=1, minsize=400)  # Entry column - expandable with minimum width
        db_frame.grid_columnconfigure(2, weight=0)  # Hint column - fixed width
        
        # Database Name field
        db_name_label = tk.Label(db_frame, text="Database Name:", font=("Arial", 11))
        db_name_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        
        self.db_name_entry = tk.Entry(db_frame, font=("Arial", 11))
        self.db_name_entry.insert(0, self.wizard_data.get('db_name', POSTGRES_DB))
        self.db_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        db_name_hint = tk.Label(db_frame, text="Must match your original database name", font=("Arial", 9), fg="gray")
        db_name_hint.grid(row=0, column=2, sticky="w", padx=(5, 0))
        
        # Database User field
        db_user_label = tk.Label(db_frame, text="Database User:", font=("Arial", 11))
        db_user_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        
        self.db_user_entry = tk.Entry(db_frame, font=("Arial", 11))
        self.db_user_entry.insert(0, self.wizard_data.get('db_user', POSTGRES_USER))
        self.db_user_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        db_user_hint = tk.Label(db_frame, text="Must match your original database user", font=("Arial", 9), fg="gray")
        db_user_hint.grid(row=1, column=2, sticky="w", padx=(5, 0))
        
        # Database Password field
        db_password_label = tk.Label(db_frame, text="Database Password:", font=("Arial", 11))
        db_password_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        
        self.db_password_entry = tk.Entry(db_frame, show="*", font=("Arial", 11))
        self.db_password_entry.insert(0, self.wizard_data.get('db_password', POSTGRES_PASSWORD))
        self.db_password_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        db_password_hint = tk.Label(db_frame, text="Must match your original database password", font=("Arial", 9), fg="gray")
        db_password_hint.grid(row=2, column=2, sticky="w", padx=(5, 0))
        
        # Store references to database credential widgets for conditional display
        # These widgets will be hidden when SQLite is detected
        # Note: We store packed widgets separately from the db_frame (which is also packed)
        self.db_credential_packed_widgets = [
            warning_label,
            instruction_label1,
            instruction_label2
        ]
        # Store reference to the frame containing grid widgets
        self.db_credential_frame = db_frame
        
        # If database type was already detected (e.g., user went back and forth),
        # update the UI accordingly
        if self.detected_dbtype:
            self.update_database_credential_ui(self.detected_dbtype)
        
        # Section 4: Nextcloud admin credentials - full width with padding
        tk.Label(parent, text="Step 4: Nextcloud Admin Credentials", font=("Arial", 14, "bold")).pack(pady=(30, 5), fill="x", padx=40)
        tk.Label(parent, text="These credentials are for accessing your Nextcloud admin panel", font=("Arial", 10), fg="gray").pack(pady=(0, 5), fill="x", padx=40)
        
        admin_frame = tk.Frame(parent)
        admin_frame.pack(pady=10, fill="x", padx=40)
        
        # Configure column weights for responsive layout
        admin_frame.grid_columnconfigure(0, weight=0)  # Label column - fixed width
        admin_frame.grid_columnconfigure(1, weight=1, minsize=400)  # Entry column - expandable with minimum width
        
        tk.Label(admin_frame, text="Admin Username:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.admin_user_entry = tk.Entry(admin_frame, font=("Arial", 11))
        self.admin_user_entry.insert(0, self.wizard_data.get('admin_user', 'admin'))
        self.admin_user_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        tk.Label(admin_frame, text="Admin Password:", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.admin_password_entry = tk.Entry(admin_frame, show="*", font=("Arial", 11))
        self.admin_password_entry.insert(0, self.wizard_data.get('admin_password', 'admin'))
        self.admin_password_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    
    def create_wizard_page3(self, parent):
        """Page 3: Container Configuration"""
        # Section 5: Container configuration - full width with padding
        tk.Label(parent, text="Step 5: Container Configuration", font=("Arial", 14, "bold")).pack(pady=(20, 5), fill="x", padx=40)
        tk.Label(parent, text="Configure Nextcloud container settings", font=("Arial", 10), fg="gray").pack(pady=(0, 5), fill="x", padx=40)
        
        container_frame = tk.Frame(parent)
        container_frame.pack(pady=10, fill="x", padx=40)
        
        # Configure column weights for responsive layout
        container_frame.grid_columnconfigure(0, weight=0)  # Label column - fixed width
        container_frame.grid_columnconfigure(1, weight=1, minsize=400)  # Entry column - expandable with minimum width
        
        tk.Label(container_frame, text="Container Name:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.container_name_entry = tk.Entry(container_frame, font=("Arial", 11))
        self.container_name_entry.insert(0, self.wizard_data.get('container_name', NEXTCLOUD_CONTAINER_NAME))
        self.container_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        tk.Label(container_frame, text="Container Port:", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.container_port_entry = tk.Entry(container_frame, font=("Arial", 11))
        self.container_port_entry.insert(0, self.wizard_data.get('container_port', '9000'))
        self.container_port_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Option to use existing container - full width with padding
        self.use_existing_var = tk.BooleanVar(value=self.wizard_data.get('use_existing', False))
        tk.Checkbutton(
            parent, 
            text="Use existing Nextcloud container if found", 
            variable=self.use_existing_var,
            font=("Arial", 11)
        ).pack(pady=15, fill="x", padx=40)
        
        # Add informative text about what will happen during restore - full width with padding
        info_frame = tk.Frame(parent, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
        info_frame.pack(pady=20, fill="x", padx=40)
        
        tk.Label(info_frame, text="🔧 Automated Restore Process", font=("Arial", 12, "bold"), 
                 bg=self.theme_colors['info_bg'], fg=self.theme_colors['info_fg']).pack(pady=(10, 8), anchor="center")
        tk.Label(info_frame, text="When you click 'Start Restore', the following will happen automatically:", 
                 font=("Arial", 10), bg=self.theme_colors['info_bg'], fg=self.theme_colors['info_fg']).pack(pady=(0, 5), anchor="center")
        
        restore_info = [
            "✓ Generate Docker Compose YAML configuration",
            "✓ Create required Docker volumes and networks",
            "✓ Extract and decrypt your backup files",
            "✓ Start database and Nextcloud containers",
            "✓ Copy all files to the container (/var/www/html)",
            "✓ Restore database from backup",
            "✓ Update configuration files automatically",
            "✓ Set proper file permissions",
            "✓ Restart services and validate installation"
        ]
        for info in restore_info:
            tk.Label(info_frame, text=info, font=("Arial", 9), 
                     bg=self.theme_colors['info_bg'], fg=self.theme_colors['info_fg'],
                     anchor="w", justify="left").pack(anchor="w", pady=1, padx=30)
        
        tk.Label(info_frame, text="No manual Docker commands or YAML editing required!", 
                 font=("Arial", 10, "bold"), bg=self.theme_colors['info_bg'], 
                 fg="#45bf55").pack(pady=(8, 10), anchor="center")
        
        # Advanced Options section (collapsible)
        self.create_advanced_options_section(parent)
    
    def create_advanced_options_section(self, parent):
        """Create an Advanced Options section for power users"""
        # Advanced Options header with expand/collapse
        advanced_frame = tk.Frame(parent)
        advanced_frame.pack(pady=10, fill="x", padx=40)
        
        # State variable for expansion
        if not hasattr(self, 'advanced_options_expanded'):
            self.advanced_options_expanded = tk.BooleanVar(value=False)
        
        def toggle_advanced_options():
            """Toggle visibility of advanced options"""
            expanded = self.advanced_options_expanded.get()
            if expanded:
                advanced_content_frame.pack(pady=5, fill="x")
            else:
                advanced_content_frame.pack_forget()
        
        # Header button for expand/collapse
        advanced_header_btn = tk.Button(
            advanced_frame,
            text="▶ Advanced Options (for power users)",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors.get('button_bg', '#3c3c3c'),
            fg=self.theme_colors.get('button_fg', '#ffffff'),
            command=lambda: [
                self.advanced_options_expanded.set(not self.advanced_options_expanded.get()),
                advanced_header_btn.config(
                    text="▼ Advanced Options (for power users)" if self.advanced_options_expanded.get() 
                    else "▶ Advanced Options (for power users)"
                ),
                toggle_advanced_options()
            ],
            relief="flat",
            padx=10,
            pady=5
        )
        advanced_header_btn.pack(fill="x")
        
        # Advanced options content (initially hidden)
        advanced_content_frame = tk.Frame(parent, bg=self.theme_colors.get('info_bg', '#2d3e50'), 
                                         relief="solid", borderwidth=1)
        
        tk.Label(
            advanced_content_frame,
            text="Docker Compose Configuration",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors.get('info_bg', '#2d3e50'),
            fg=self.theme_colors.get('info_fg', '#ecf0f1')
        ).pack(pady=(10, 5))
        
        tk.Label(
            advanced_content_frame,
            text="Docker Compose YAML files are automatically generated and stored internally.\n"
                 "Use these options if you need to customize or export the configuration.",
            font=("Arial", 9),
            bg=self.theme_colors.get('info_bg', '#2d3e50'),
            fg=self.theme_colors.get('hint_fg', '#95a5a6'),
            justify="center"
        ).pack(pady=(0, 10))
        
        # Buttons for YAML operations
        button_frame = tk.Frame(advanced_content_frame, bg=self.theme_colors.get('info_bg', '#2d3e50'))
        button_frame.pack(pady=(0, 10))
        
        tk.Button(
            button_frame,
            text="📄 View Generated YAML",
            font=("Arial", 10),
            command=self.view_generated_yaml,
            width=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="💾 Export YAML File",
            font=("Arial", 10),
            command=self.export_yaml_file,
            width=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="📁 Open YAML Folder",
            font=("Arial", 10),
            command=self.open_yaml_folder,
            width=20
        ).pack(side="left", padx=5)
    
    def view_generated_yaml(self):
        """View the most recently generated YAML file"""
        try:
            compose_dir = get_compose_directory()
            yaml_files = sorted(compose_dir.glob("docker-compose-*.yml"), reverse=True)
            
            if not yaml_files:
                messagebox.showinfo(
                    "No YAML Files",
                    "No Docker Compose YAML files have been generated yet.\n\n"
                    "YAML files are created automatically during the restore process.",
                    parent=self
                )
                return
            
            # Get the most recent file
            latest_yaml = yaml_files[0]
            
            with open(latest_yaml, 'r') as f:
                yaml_content = f.read()
            
            # Create a dialog to display the YAML content
            dialog = tk.Toplevel(self)
            dialog.title("Docker Compose YAML Configuration")
            dialog.geometry("800x600")
            dialog.transient(self)
            dialog.grab_set()
            
            # Header
            header_frame = tk.Frame(dialog, bg="#3daee9", height=60)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            tk.Label(
                header_frame,
                text=f"📄 {latest_yaml.name}",
                font=("Arial", 14, "bold"),
                bg="#3daee9",
                fg="white"
            ).pack(pady=15)
            
            # Text widget with scrollbar
            text_frame = tk.Frame(dialog)
            text_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side="right", fill="y")
            
            text_widget = tk.Text(
                text_frame,
                wrap="none",
                font=("Courier", 10),
                yscrollcommand=scrollbar.set
            )
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=text_widget.yview)
            
            text_widget.insert("1.0", yaml_content)
            text_widget.config(state="disabled")
            
            # Close button
            tk.Button(
                dialog,
                text="Close",
                font=("Arial", 11),
                command=dialog.destroy,
                width=15
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to view YAML file:\n{e}",
                parent=self
            )
            logger.error(f"Error viewing YAML file: {e}")
    
    def export_yaml_file(self):
        """Export the most recently generated YAML file to a user-selected location"""
        try:
            compose_dir = get_compose_directory()
            yaml_files = sorted(compose_dir.glob("docker-compose-*.yml"), reverse=True)
            
            if not yaml_files:
                messagebox.showinfo(
                    "No YAML Files",
                    "No Docker Compose YAML files have been generated yet.\n\n"
                    "YAML files are created automatically during the restore process.",
                    parent=self
                )
                return
            
            # Get the most recent file
            latest_yaml = yaml_files[0]
            
            # Ask user where to save
            save_path = filedialog.asksaveasfilename(
                title="Export Docker Compose YAML",
                defaultextension=".yml",
                initialfile="docker-compose.yml",
                filetypes=[("YAML files", "*.yml"), ("YAML files", "*.yaml"), ("All files", "*.*")],
                parent=self
            )
            
            if not save_path:
                return
            
            # Copy the file
            shutil.copy2(latest_yaml, save_path)
            
            messagebox.showinfo(
                "Export Successful",
                f"Docker Compose YAML file exported to:\n{save_path}\n\n"
                "You can now use 'docker-compose up -d' to start your containers.",
                parent=self
            )
            logger.info(f"YAML file exported to: {save_path}")
            
        except Exception as e:
            messagebox.showerror(
                "Export Failed",
                f"Failed to export YAML file:\n{e}",
                parent=self
            )
            logger.error(f"Error exporting YAML file: {e}")
    
    def open_yaml_folder(self):
        """Open the folder containing generated YAML files in the system file explorer"""
        try:
            compose_dir = get_compose_directory()
            
            # Open the folder in the default file manager
            if platform.system() == 'Windows':
                os.startfile(str(compose_dir))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(compose_dir)])
            else:  # Linux and others
                subprocess.run(['xdg-open', str(compose_dir)])
            
            logger.info(f"Opened YAML folder: {compose_dir}")
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to open YAML folder:\n{e}",
                parent=self
            )
            logger.error(f"Error opening YAML folder: {e}")
    
    def wizard_navigate(self, direction):
        """Navigate between wizard pages, saving current page data"""
        # Save current page data
        self.save_wizard_page_data()
        
        # If navigating back to Page 1 from Page 2, reset detection state
        # This allows users to change backup file or password and re-detect
        if self.wizard_page == 2 and direction == -1:
            logger.info("User navigating back to Page 1 - resetting detection state")
            print("Resetting detection - user navigating back to Page 1")
            
            # Reset extraction/detection state to allow re-extraction
            self.extraction_attempted = False
            self.extraction_successful = False
            self.detected_dbtype = None
            self.detected_db_config = None
            self.db_auto_detected = False
            self.current_backup_path = None
        
        # If navigating from Page 1 to Page 2, perform extraction and detection
        if self.wizard_page == 1 and direction == 1:
            logger.info("Navigation from Page 1 to Page 2: Attempting extraction and detection")
            
            # Start non-blocking extraction and detection
            # The actual navigation will happen in _process_detection_results
            self.perform_extraction_and_detection()
            # Don't navigate yet - let the background thread complete and navigate
            return
        
        # Navigate to new page
        new_page = self.wizard_page + direction
        if 1 <= new_page <= 3:
            logger.info(f"Navigating to wizard page {new_page}")
            self.show_wizard_page(new_page)
    
    def save_wizard_page_data(self):
        """Save data from current wizard page"""
        if self.wizard_page == 1:
            if hasattr(self, 'backup_entry'):
                self.wizard_data['backup_path'] = self.backup_entry.get()
            if hasattr(self, 'password_entry'):
                self.wizard_data['password'] = self.password_entry.get()
        elif self.wizard_page == 2:
            if hasattr(self, 'db_name_entry'):
                self.wizard_data['db_name'] = self.db_name_entry.get()
            if hasattr(self, 'db_user_entry'):
                self.wizard_data['db_user'] = self.db_user_entry.get()
            if hasattr(self, 'db_password_entry'):
                self.wizard_data['db_password'] = self.db_password_entry.get()
            if hasattr(self, 'admin_user_entry'):
                self.wizard_data['admin_user'] = self.admin_user_entry.get()
            if hasattr(self, 'admin_password_entry'):
                self.wizard_data['admin_password'] = self.admin_password_entry.get()
        elif self.wizard_page == 3:
            if hasattr(self, 'container_name_entry'):
                self.wizard_data['container_name'] = self.container_name_entry.get()
            if hasattr(self, 'container_port_entry'):
                self.wizard_data['container_port'] = self.container_port_entry.get()
            if hasattr(self, 'use_existing_var'):
                self.wizard_data['use_existing'] = self.use_existing_var.get()
    
    def validate_extraction_tools(self, backup_path):
        """
        Validate that required extraction tools are available for the selected backup.
        
        This method performs early validation when a backup file is selected to provide
        immediate feedback about missing dependencies before the user proceeds through
        the wizard.
        
        Args:
            backup_path: Path to the backup file selected by the user
            
        Returns:
            bool: True if tools are available, False otherwise
        """
        logger.info(f"Validating extraction tools for backup: {backup_path}")
        
        # Check if file exists
        if not os.path.isfile(backup_path):
            logger.error(f"Backup file does not exist: {backup_path}")
            return False
        
        # Determine what tools are needed based on file extension
        is_encrypted = backup_path.endswith('.gpg')
        is_tarball = backup_path.endswith('.tar.gz') or backup_path.endswith('.tar.gz.gpg')
        
        missing_tools = []
        
        # Check for GPG if file is encrypted
        if is_encrypted:
            gpg_available, gpg_error = check_gpg_available()
            if not gpg_available:
                logger.warning(f"GPG not available: {gpg_error}")
                missing_tools.append(('gpg', gpg_error))
        
        # Check for tarfile module
        if is_tarball:
            tar_available, tar_error = check_tarfile_available()
            if not tar_available:
                logger.warning(f"tarfile not available: {tar_error}")
                missing_tools.append(('tarfile', tar_error))
        
        # If tools are missing, show error and offer to install
        if missing_tools:
            logger.error(f"Missing extraction tools: {[tool[0] for tool in missing_tools]}")
            
            # Show error for the first missing tool (usually the most critical)
            missing_tool, error_msg = missing_tools[0]
            
            # Show user-friendly error dialog with installation options
            action = show_extraction_error_dialog(self, missing_tool, backup_path)
            
            if action == 'install':
                # User chose to install the missing tool
                if missing_tool == 'gpg':
                    logger.info("User chose to install GPG")
                    webbrowser.open(GPG_DOWNLOAD_URL)
                    messagebox.showinfo(
                        "Installation Started",
                        "GPG installer has been opened in your browser.\n\n"
                        "Please complete the installation and restart the application.",
                        parent=self
                    )
                return False
            else:
                # User cancelled
                logger.info("User cancelled tool installation")
                return False
        
        logger.info("All required extraction tools are available")
        return True
    
    def perform_extraction_and_detection(self):
        """
        Perform database type detection before showing Page 2.
        
        This is the entry point for early database detection, called when the user
        clicks "Next" on Page 1 to navigate to the database configuration page.
        
        EXTRACTION STRATEGY:
        - ONLY config.php is extracted at this stage (not the full backup)
        - This is a lightweight operation (<1 second) vs full extraction (minutes)
        - Full backup extraction is deferred until the actual restore process
        - Extraction is attempted ONLY ONCE per backup file selection
        
        WHY THIS MATTERS:
        - SQLite users can immediately see that no database credentials are needed
        - MySQL/PostgreSQL users see the appropriate credential fields
        - GUI remains responsive - no waiting for multi-GB extraction
        - Better user experience with immediate feedback
        - No duplicate extraction attempts on multiple navigations
        
        THREADING:
        - Detection runs in a background thread to keep GUI responsive
        - Animated spinner shows progress while detection is in progress
        - All GUI updates happen on the main thread (thread-safe)
        
        STATE TRACKING:
        - extraction_attempted: True if we've tried to extract this backup
        - extraction_successful: True if extraction and detection succeeded
        - current_backup_path: Path of the backup we extracted (to detect changes)
        
        Returns:
            True if detection successful (or already detected), False if validation fails
        """
        # Get backup path and password from wizard data
        backup_path = self.wizard_data.get('backup_path', '').strip()
        password = self.wizard_data.get('password', '')
        
        # Validate backup file exists
        if not backup_path or not os.path.isfile(backup_path):
            logger.error("No valid backup file selected")
            self.error_label.config(text="Error: Please select a valid backup archive file.", fg="red")
            return False
        
        # CHECK: If we've already successfully extracted this same backup, skip re-extraction
        if (self.extraction_successful and 
            self.current_backup_path == backup_path and 
            self.detected_dbtype):
            logger.info(f"Extraction already completed for {os.path.basename(backup_path)} - skipping re-extraction")
            print(f"✓ Database type already detected: {self.detected_dbtype}")
            # Navigate to Page 2 immediately since extraction is already complete
            self.show_wizard_page(2)
            return True
        
        # If backup path changed, reset state
        if self.current_backup_path and self.current_backup_path != backup_path:
            logger.info(f"Backup path changed from {os.path.basename(self.current_backup_path)} to {os.path.basename(backup_path)} - resetting state")
            self.extraction_attempted = False
            self.extraction_successful = False
            self.detected_dbtype = None
            self.detected_db_config = None
            self.db_auto_detected = False
        
        # Mark that we're attempting extraction for this backup
        self.current_backup_path = backup_path
        self.extraction_attempted = True
        logger.info(f"Starting extraction and detection for backup: {os.path.basename(backup_path)}")
        
        # Early validation: Check if required extraction tools are available
        # This prevents the user from proceeding if essential tools are missing
        logger.info("Checking extraction tools availability before detection")
        is_encrypted = backup_path.endswith('.gpg')
        is_tarball = backup_path.endswith('.tar.gz') or backup_path.endswith('.tar.gz.gpg')
        
        # Check for GPG if file is encrypted
        if is_encrypted:
            gpg_available, gpg_error = check_gpg_available()
            if not gpg_available:
                logger.error(f"GPG not available, cannot proceed: {gpg_error}")
                error_msg = (
                    f"⚠️ Cannot extract encrypted backup:\n{gpg_error}\n\n"
                    "Please install GPG to continue with encrypted backups."
                )
                self.error_label.config(text=error_msg, fg="red")
                
                # Show detailed error dialog with installation options
                action = show_extraction_error_dialog(self, 'gpg', backup_path)
                if action == 'install':
                    logger.info("User chose to install GPG")
                    webbrowser.open(GPG_DOWNLOAD_URL)
                    messagebox.showinfo(
                        "Installation Started",
                        "GPG installer has been opened in your browser.\n\n"
                        "Please complete the installation and restart the application.",
                        parent=self
                    )
                self.extraction_successful = False
                return False
        
        # Check for tarfile module
        if is_tarball:
            tar_available, tar_error = check_tarfile_available()
            if not tar_available:
                logger.error(f"tarfile not available, cannot proceed: {tar_error}")
                error_msg = (
                    f"⚠️ Cannot extract tar.gz archive:\n{tar_error}\n\n"
                    "Please ensure Python is properly installed."
                )
                self.error_label.config(text=error_msg, fg="red")
                
                # Show detailed error dialog
                action = show_extraction_error_dialog(self, 'tarfile', backup_path)
                self.extraction_successful = False
                return False
        
        # Validate password for encrypted backups
        if backup_path.endswith('.gpg') and not password:
            logger.error("Password required for encrypted backup but not provided")
            self.error_label.config(text="Error: Please enter decryption password for encrypted backup.", fg="red")
            self.extraction_successful = False
            return False
        
        # Show progress spinner with message
        logger.info("Starting config.php extraction and database type detection")
        self.error_label.config(text="⏳ Extracting and detecting database type...\nPlease wait, this may take a moment...", fg=self.theme_colors['progress_fg'], font=("Arial", 12, "bold"))
        self.update_idletasks()
        
        # Disable navigation buttons to prevent user actions during detection
        self._disable_wizard_navigation()
        
        # Use a list to store results from background thread (mutable)
        detection_result = [None]  # Will store (dbtype, db_config, error)
        detection_complete = [False]
        
        def do_detection():
            """Background thread function for detection"""
            try:
                dbtype, db_config = self.early_detect_database_type_from_backup(backup_path, password)
                detection_result[0] = (dbtype, db_config, None)
            except Exception as e:
                detection_result[0] = (None, None, e)
            finally:
                detection_complete[0] = True
        
        # Start detection in background thread
        detection_thread = threading.Thread(target=do_detection, daemon=True)
        detection_thread.start()
        
        # Setup spinner animation state
        spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spinner_state = {'idx': 0}
        
        def check_detection_progress():
            """Non-blocking progress checker called via .after()"""
            if detection_complete[0]:
                # Detection finished - process results
                self._process_detection_results(detection_result[0])
            else:
                # Update spinner and schedule next check
                spinner_state['idx'] = (spinner_state['idx'] + 1) % len(spinner_chars)
                self.error_label.config(
                    text=f"{spinner_chars[spinner_state['idx']]} Extracting and detecting database type...\nPlease wait, this may take a moment...", 
                    fg=self.theme_colors['progress_fg'],
                    font=("Arial", 12, "bold")
                )
                # Schedule next check in 100ms (non-blocking)
                self.after(100, check_detection_progress)
        
        # Start non-blocking progress check
        check_detection_progress()
        
        # Return True immediately - actual navigation will be handled in check_detection_progress
        return True
    
    def _process_detection_results(self, result):
        """
        Process detection results and navigate to Page 2 if successful.
        This is called from the non-blocking progress checker.
        
        Args:
            result: Tuple of (dbtype, db_config, error) from detection thread
        """
        # Re-enable navigation buttons
        self._enable_wizard_navigation()
        
        backup_path = self.wizard_data.get('backup_path', '').strip()
        
        if result:
            dbtype, db_config, error = result
            
            if error:
                error_str = str(error)
                logger.error(f"Error during extraction and detection: {error_str}")
                
                # Provide more specific error messages based on the error type
                if "GPG" in error_str or "gpg" in error_str:
                    if "command not found" in error_str or "not installed" in error_str:
                        error_msg = (
                            "⚠️ GPG Error: GPG is not installed or not in PATH.\n\n"
                            "GPG is required to decrypt encrypted backups.\n"
                            "Please install GPG and try again."
                        )
                        # Offer to install
                        action = show_extraction_error_dialog(self, 'gpg', backup_path)
                        if action == 'install':
                            webbrowser.open(GPG_DOWNLOAD_URL)
                            messagebox.showinfo(
                                "Installation Started",
                                "GPG installer has been opened in your browser.\n\n"
                                "Please complete the installation and restart the application.",
                                parent=self
                            )
                    elif "Bad session key" in error_str or "decryption failed" in error_str:
                        error_msg = (
                            "⚠️ Decryption Error: Incorrect password.\n\n"
                            "The password you entered is incorrect.\n"
                            "Please go back and enter the correct password."
                        )
                    else:
                        error_msg = f"⚠️ GPG Error: {error_str}"
                elif "Invalid or corrupted archive" in error_str or "tarfile" in error_str:
                    error_msg = (
                        "⚠️ Archive Error: The backup file appears to be corrupted\n"
                        "or is not a valid tar.gz archive.\n\n"
                        "Please verify the backup file and try again."
                    )
                elif "Permission denied" in error_str:
                    error_msg = (
                        "⚠️ Permission Error: Cannot access the backup file.\n\n"
                        "Please check file permissions and try again."
                    )
                elif "No space left" in error_str:
                    error_msg = (
                        "⚠️ Disk Space Error: Not enough space to extract backup.\n\n"
                        "Please free up some disk space and try again."
                    )
                else:
                    error_msg = f"⚠️ Extraction Error:\n{error_str}\n\nPlease check the logs for details."
                
                self.error_label.config(text=error_msg, fg="red")
                logger.error(f"Extraction failed, preventing navigation to Page 2")
                self.extraction_successful = False
                return
            
            if dbtype:
                # Mark extraction as successful
                self.extraction_successful = True
                self.detected_dbtype = dbtype
                self.detected_db_config = db_config
                self.db_auto_detected = True
                
                logger.info(f"✓ Database type detected successfully: {dbtype}")
                print(f"✓ Database type detected before Page 2: {dbtype}")
                self.error_label.config(text="✓ Database type detected successfully!", fg="green")
                
                # Navigate to Page 2 now that detection is complete
                logger.info("Detection successful - navigating to Page 2")
                self.show_wizard_page(2)
                
                # Docker Compose is now automatically generated during restore
                # No need to prompt user for YAML file generation
                # Advanced users can access YAML options from the Advanced Options section
                # Clear success message after a brief moment
                self.after(1500, lambda: self.error_label.config(text=""))
            else:
                # Detection failed - show warning but allow navigation
                # User may still be able to proceed with manual configuration
                logger.warning("Could not detect database type from backup - config.php not found or unreadable")
                print("⚠️ Warning: Could not detect database type from backup")
                warning_msg = (
                    "⚠️ Warning: config.php not found or could not be read.\n"
                    "Database type detection failed. You can still continue,\n"
                    "but please ensure your database credentials are correct."
                )
                self.error_label.config(text=warning_msg, fg="orange")
                self.detected_dbtype = None
                self.detected_db_config = None
                self.db_auto_detected = False
                
                # Clear success message after a brief moment, then allow navigation
                self.after(1500, lambda: [
                    self.error_label.config(text=""),
                    self.show_wizard_page(2)
                ])
        else:
            # No result - something went wrong
            logger.error("Detection returned no result")
            self.error_label.config(text="⚠️ Unexpected error during detection", fg="red")
            self.extraction_successful = False
    
    def _disable_wizard_navigation(self):
        """Disable wizard navigation buttons during background processing"""
        # Find and disable navigation buttons in the wizard frame
        for widget in self.wizard_scrollable_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        child.config(state='disabled')
    
    def _enable_wizard_navigation(self):
        """Re-enable wizard navigation buttons after background processing"""
        # Find and enable navigation buttons in the wizard frame
        for widget in self.wizard_scrollable_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        child.config(state='normal')
                self.extraction_successful = True  # Extraction worked, just couldn't detect DB type
                return True  # Still allow navigation - don't break workflow
        else:
            # Should not happen, but handle gracefully
            logger.error("Detection process failed unexpectedly - no result returned")
            self.error_label.config(text="⚠️ Detection process failed unexpectedly", fg="red")
            self.extraction_successful = False
            return False

    def browse_backup(self):
        path = filedialog.askopenfilename(
            title="Select .tar.gz.gpg backup",
            filetypes=[("PGP Archive", "*.tar.gz.gpg"), ("All files", "*.*")]
        )
        if path:
            self.backup_entry.delete(0, tk.END)
            self.backup_entry.insert(0, path)
            
            # Early validation: Check if required extraction tools are available
            # This provides immediate feedback to the user about missing dependencies
            self.validate_extraction_tools(path)
            
            # Note: Database type detection is deferred until after the user enters
            # the decryption password (if needed) and clicks "Next" to navigate to Page 2.
            # This ensures encrypted backups can be properly decrypted before detection.
            # See perform_extraction_and_detection() method for the detection logic.

    def validate_and_start_restore(self):
        """Validate all input fields and start the restore process"""
        self.error_label.config(text="", fg="red")
        
        # Save current page data first
        self.save_wizard_page_data()
        
        # Get all values from wizard_data
        backup_path = self.wizard_data.get('backup_path', '').strip()
        password = self.wizard_data.get('password', '')
        db_name = self.wizard_data.get('db_name', '').strip()
        db_user = self.wizard_data.get('db_user', '').strip()
        db_password = self.wizard_data.get('db_password', '')
        admin_user = self.wizard_data.get('admin_user', '').strip()
        admin_password = self.wizard_data.get('admin_password', '')
        container_name = self.wizard_data.get('container_name', '').strip()
        container_port = self.wizard_data.get('container_port', '').strip()
        use_existing = self.wizard_data.get('use_existing', False)
        
        # Validate backup file
        if not backup_path or not os.path.isfile(backup_path):
            self.error_label.config(text="Error: Please select a valid backup archive file.")
            return
        
        # Validate password if encrypted
        if backup_path.endswith('.gpg'):
            if not password:
                self.error_label.config(text="Error: Please enter decryption password for encrypted backup.")
                return
        
        # Validate database credentials (skip for SQLite databases)
        # SQLite databases don't require separate credentials as they're file-based
        is_sqlite = self.detected_dbtype and self.detected_dbtype.lower() in ['sqlite', 'sqlite3']
        
        if not is_sqlite:
            # Only validate database credentials for MySQL and PostgreSQL
            if not db_name:
                self.error_label.config(text="Error: Database name is required.")
                return
            if not db_user:
                self.error_label.config(text="Error: Database user is required.")
                return
            if not db_password:
                self.error_label.config(text="Error: Database password is required.")
                return
        
        # Validate admin credentials
        if not admin_user:
            self.error_label.config(text="Error: Admin username is required.")
            return
        if not admin_password:
            self.error_label.config(text="Error: Admin password is required.")
            return
        
        # Validate container configuration
        if not container_name:
            self.error_label.config(text="Error: Container name is required.")
            return
        if not container_port.isdigit() or not (1 <= int(container_port) <= 65535):
            self.error_label.config(text="Error: Port must be a number between 1 and 65535.")
            return
        
        # Store all values for restore process
        self.restore_backup_path = backup_path
        self.restore_password = password if password else None
        self.restore_db_name = db_name
        self.restore_db_user = db_user
        self.restore_db_password = db_password
        self.restore_admin_user = admin_user
        self.restore_admin_password = admin_password
        self.restore_container_name = container_name
        self.restore_container_port = int(container_port)
        self.restore_use_existing = use_existing
        
        # Disable the restore button
        self.restore_now_btn.config(state="disabled")
        
        # Show progress bars
        if hasattr(self, 'progressbar'):
            self.progressbar.pack(pady=(30, 3))
        if hasattr(self, 'progress_label'):
            self.progress_label.pack()
        if hasattr(self, 'process_label'):
            self.process_label.pack(fill="x", padx=10, pady=4)
        
        # Start restore
        self.start_restore_thread()

    def set_restore_progress(self, percent, msg=""):
        # percent: 0-100
        # Initialize start time on first call
        if not hasattr(self, 'restore_start_time') or percent == 0:
            self.restore_start_time = time.time()
            self.last_progress_percent = 0
        
        # Update progress bar
        if hasattr(self, "progressbar") and self.progressbar:
            safe_widget_update(
                self.progressbar,
                lambda: self.progressbar.__setitem__('value', percent),
                "progress bar value update"
            )
        
        # Calculate elapsed time and estimate
        elapsed_time = time.time() - self.restore_start_time
        elapsed_str = self._format_time(elapsed_time)
        
        # Estimate remaining time if progress > 0
        if percent > 0 and percent < 100:
            total_estimated = (elapsed_time / percent) * 100
            remaining_time = total_estimated - elapsed_time
            remaining_str = self._format_time(remaining_time)
            progress_text = f"{percent}% | Elapsed: {elapsed_str} | Est. remaining: {remaining_str}"
        elif percent == 100:
            progress_text = f"100% | Total time: {elapsed_str}"
        else:
            progress_text = f"{percent}%"
        
        # Update progress label with time info
        if hasattr(self, "progress_label") and self.progress_label:
            safe_widget_update(
                self.progress_label,
                lambda: self.progress_label.config(text=progress_text),
                "progress label update"
            )
        
        # Update status message
        if msg and hasattr(self, "status_label") and self.status_label:
            safe_widget_update(
                self.status_label,
                lambda: self.status_label.config(text=msg),
                "status label update"
            )
        
        # Update process label with current step
        if msg and hasattr(self, "process_label") and self.process_label:
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text=f"Current step: {msg}"),
                "process label update"
            )
        
        self.last_progress_percent = percent
        
        try:
            if self.winfo_exists():
                self.update_idletasks()
        except tk.TclError:
            logger.debug("TclError during update_idletasks - window may have been closed")
    
    def _format_time(self, seconds):
        """Format time in seconds to human-readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def _format_bytes(self, bytes_count):
        """Format bytes to human-readable format (KB, MB, GB)"""
        if bytes_count < 1024:
            return f"{bytes_count}B"
        elif bytes_count < 1024 * 1024:
            return f"{bytes_count / 1024:.1f}KB"
        elif bytes_count < 1024 * 1024 * 1024:
            return f"{bytes_count / (1024 * 1024):.1f}MB"
        else:
            return f"{bytes_count / (1024 * 1024 * 1024):.2f}GB"

    def copy_folder_to_container_with_progress(self, local_path, container_name, container_path, 
                                               folder_name, progress_start, progress_end, 
                                               progress_callback=None):
        """
        Copy a folder to a Docker container with live file-by-file progress updates.
        
        Args:
            local_path: Local folder path to copy from
            container_name: Docker container name
            container_path: Destination path in container
            folder_name: Name of the folder being copied (for display)
            progress_start: Starting progress percentage (e.g., 30)
            progress_end: Ending progress percentage (e.g., 37)
            progress_callback: Optional callback(files_copied, total_files, current_file, percent)
        
        Returns:
            True on success, False on failure
        """
        try:
            # First, remove existing folder in container
            subprocess.run(
                f'docker exec {container_name} rm -rf {container_path}/{folder_name}',
                shell=True, check=False  # Don't fail if folder doesn't exist
            )
            
            # Create destination folder in container
            subprocess.run(
                f'docker exec {container_name} mkdir -p {container_path}/{folder_name}',
                shell=True, check=True
            )
            
            # Count total files to copy
            total_files = 0
            all_files = []
            for dirpath, dirnames, filenames in os.walk(local_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    # Get relative path for destination
                    rel_path = os.path.relpath(filepath, local_path)
                    all_files.append((filepath, rel_path))
                    total_files += 1
            
            if total_files == 0:
                logger.info(f"No files to copy in {folder_name}")
                return True
            
            logger.info(f"Copying {total_files} files from {folder_name} to container...")
            
            # Copy files one by one with progress updates
            files_copied = 0
            copy_start_time = time.time()
            
            for filepath, rel_path in all_files:
                try:
                    # Get the directory portion of the relative path
                    rel_dir = os.path.dirname(rel_path)
                    
                    # Create directory structure in container if needed
                    if rel_dir:
                        container_dest_dir = f"{container_path}/{folder_name}/{rel_dir.replace(os.sep, '/')}"
                        subprocess.run(
                            f'docker exec {container_name} mkdir -p "{container_dest_dir}"',
                            shell=True, check=True
                        )
                    
                    # Copy the file
                    container_dest = f"{container_path}/{folder_name}/{rel_path.replace(os.sep, '/')}"
                    subprocess.run(
                        f'docker cp "{filepath}" {container_name}:"{container_dest}"',
                        shell=True, check=True, capture_output=True
                    )
                    
                    files_copied += 1
                    
                    # Calculate progress percentage
                    file_percent = (files_copied / total_files) * 100
                    current_progress = progress_start + int((progress_end - progress_start) * (files_copied / total_files))
                    
                    # Call progress callback if provided
                    if progress_callback and (files_copied % 5 == 0 or files_copied == total_files):
                        # Only update every 5 files to avoid overwhelming the UI
                        elapsed = time.time() - copy_start_time
                        progress_callback(files_copied, total_files, rel_path, current_progress, elapsed)
                    
                except Exception as e:
                    logger.warning(f"Failed to copy {rel_path}: {e}")
                    # Continue with other files even if one fails
                    continue
            
            logger.info(f"Successfully copied {files_copied}/{total_files} files from {folder_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error copying folder {folder_name}: {e}")
            return False

    def auto_extract_backup(self, backup_path, password=None):
        """
        Perform FULL backup extraction during the actual restore process.
        
        WHEN THIS IS CALLED:
        - Only called when user clicks "Start Restore" on Page 3
        - This is the actual restore process, not the initial detection
        - At this point, database type has already been detected from config.php
        
        WHAT THIS DOES:
        - Decrypts the backup if encrypted (full backup decryption)
        - Extracts ALL files from the backup archive (apps, config, data, database)
        - This is the heavy operation that can take minutes for large backups
        
        WHY DEFERRED UNTIL NOW:
        - User has already confirmed they want to proceed with restore
        - Database credentials have been collected and validated
        - All configuration has been finalized
        - No point extracting everything until we're ready to use it
        
        THREADING:
        - Decryption runs in background thread with progress updates
        - Extraction runs in background thread with progress updates
        - GUI remains responsive throughout with animated progress indicators
        
        Returns:
            Path to extracted directory, or None if extraction fails
        """
        extract_temp = os.path.join(tempfile.gettempdir(), "nextcloud_restore_extract")
        shutil.rmtree(extract_temp, ignore_errors=True)
        os.makedirs(extract_temp, exist_ok=True)
        extracted_file = backup_path

        safe_widget_update(
            self.error_label,
            lambda: self.error_label.config(text=""),
            "error label clear"
        )

        # Step 1: If encrypted, decrypt using provided password
        if backup_path.endswith('.gpg'):
            if not password:
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text="No password entered. Cannot decrypt backup."),
                    "error label update"
                )
                return None
            decrypted_file = os.path.splitext(backup_path)[0]  # remove .gpg
            try:
                self.set_restore_progress(0, "Decrypting backup archive ...")
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text=f"Decrypting: {os.path.basename(backup_path)}"),
                    "process label update"
                )
                try:
                    if self.winfo_exists():
                        self.update_idletasks()
                except tk.TclError:
                    logger.debug("TclError during update_idletasks - window may have been closed")
                
                # Start decryption with progress monitoring
                decryption_done = [False]  # Use list for mutable flag
                
                def do_decryption():
                    try:
                        decrypt_file_gpg(backup_path, decrypted_file, password)
                        decryption_done[0] = True
                    except Exception as ex:
                        decryption_done[0] = ex
                
                # Start decryption in a thread
                decryption_thread = threading.Thread(target=do_decryption, daemon=True)
                decryption_thread.start()
                
                # Update progress while decryption is running (0-10% range)
                progress_val = 0
                while decryption_thread.is_alive():
                    if progress_val < 10:
                        progress_val += 1
                        self.set_restore_progress(progress_val, "Decrypting backup archive ...")
                        self.update_idletasks()
                    time.sleep(0.3)  # Check every 0.3 seconds
                
                # Wait for thread to finish
                decryption_thread.join()
                
                # Check if decryption failed
                if decryption_done[0] is not True:
                    if isinstance(decryption_done[0], Exception):
                        raise decryption_done[0]
                    else:
                        raise Exception("Decryption failed")
                
                extracted_file = decrypted_file
            except Exception as e:
                tb = traceback.format_exc()
                self.set_restore_progress(0, "Restore failed!")
                error_msg = str(e)
                # Provide user-friendly error messages
                if "Bad session key" in error_msg or "decryption failed" in error_msg:
                    user_msg = "Decryption failed: Incorrect password provided"
                elif "gpg: command not found" in error_msg or "No such file or directory: 'gpg'" in error_msg:
                    user_msg = "Decryption failed: GPG is not installed on your system"
                else:
                    user_msg = f"Decryption failed: {e}"
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=user_msg),
                    "error label update after decryption failure"
                )
                print(f"Error details:\n{tb}")
                shutil.rmtree(extract_temp, ignore_errors=True)
                return None

        # Step 2: FULL EXTRACTION - Extract all files from backup archive
        # This is where the complete backup (apps, config, data, database) is extracted
        # Unlike early detection which only extracted config.php, this extracts everything
        try:
            self.set_restore_progress(0, "Extracting full backup archive...")
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            
            # Initialize extraction tracking
            extraction_done = [False]  # Use list for mutable flag
            extraction_start_time = [time.time()]  # Track extraction start time
            
            def extraction_progress_callback(files_extracted, total_files, current_file, bytes_processed=0, total_bytes=0):
                """
                Callback function to update UI with extraction progress.
                Called after each file is extracted (batch_size=1 for real-time updates).
                Uses Tkinter's after() method for thread-safe UI updates.
                
                Supports both byte-based progress (when total_files is None) and
                file-count-based progress (when total_files is known).
                
                Args:
                    files_extracted: Number of files extracted so far
                    total_files: Total files (None if unknown in streaming mode)
                    current_file: Name of current file being extracted
                    bytes_processed: Bytes read from compressed archive so far
                    total_bytes: Total size of compressed archive
                """
                try:
                    # Calculate progress percentage
                    # Extraction phase: 0-20% of overall restore progress
                    if total_files is not None and total_files > 0:
                        # File count-based progress (accurate when total is known)
                        file_percent = (files_extracted / total_files) * 100
                        # Map extraction progress to 0-20% range
                        progress_val = int((file_percent / 100) * 20)
                        status_msg = f"Extracting: {files_extracted}/{total_files} files"
                    elif total_bytes > 0 and bytes_processed > 0:
                        # Byte-based progress (estimated from compressed bytes read)
                        byte_percent = (bytes_processed / total_bytes) * 100
                        # Map extraction progress to 0-20% range
                        progress_val = min(int((byte_percent / 100) * 20), 19)  # Cap at 19% until complete
                        status_msg = f"Extracting: {files_extracted} files (~{int(byte_percent)}% by size)"
                    else:
                        # Unknown progress, show activity
                        progress_val = 0
                        status_msg = f"Extracting: {files_extracted} files..."
                    
                    # Calculate elapsed time and estimate
                    elapsed = time.time() - extraction_start_time[0]
                    if files_extracted > 0 and elapsed > 0:
                        rate = files_extracted / elapsed
                        
                        elapsed_str = self._format_time(elapsed)
                        
                        # Estimate remaining time
                        if total_files is not None and total_files > 0:
                            # File-based estimate
                            remaining_files = total_files - files_extracted
                            est_remaining = remaining_files / rate if rate > 0 else 0
                        elif total_bytes > 0 and bytes_processed > 0:
                            # Byte-based estimate
                            remaining_bytes = total_bytes - bytes_processed
                            bytes_per_sec = bytes_processed / elapsed if elapsed > 0 else 0
                            est_remaining = remaining_bytes / bytes_per_sec if bytes_per_sec > 0 else 0
                        else:
                            est_remaining = 0
                        
                        est_str = self._format_time(est_remaining)
                        
                        status_msg += f" | Elapsed: {elapsed_str}"
                        if est_remaining > 0:
                            status_msg += f" | Est: {est_str}"
                    
                    # Use after() for thread-safe UI updates instead of direct widget updates
                    def update_ui():
                        try:
                            # Update progress bar and status
                            self.set_restore_progress(progress_val, status_msg)
                            
                            # Update process label with current file
                            if current_file and len(current_file) > 0:
                                file_display = current_file[:50] + "..." if len(current_file) > 50 else current_file
                                if hasattr(self, "process_label") and self.process_label:
                                    self.process_label.config(text=f"Extracting: {file_display}")
                            
                            # Force UI update
                            if self.winfo_exists():
                                self.update_idletasks()
                        except tk.TclError:
                            pass
                        except Exception as ex:
                            logger.debug(f"Error updating UI: {ex}")
                    
                    # Schedule UI update on main thread
                    try:
                        self.after(0, update_ui)
                    except tk.TclError:
                        pass
                except Exception as ex:
                    logger.debug(f"Error in extraction progress callback: {ex}")
            
            def prepare_extraction_callback():
                """
                Callback to show immediate feedback before extraction starts.
                With streaming extraction, there's no blocking archive scan.
                """
                def show_preparing():
                    try:
                        self.set_restore_progress(0, "Starting extraction...")
                        if hasattr(self, "process_label") and self.process_label:
                            self.process_label.config(text="Initializing streaming extraction...")
                        if self.winfo_exists():
                            self.update_idletasks()
                    except tk.TclError:
                        pass
                    except Exception as ex:
                        logger.debug(f"Error showing preparing message: {ex}")
                
                try:
                    self.after(0, show_preparing)
                except tk.TclError:
                    pass
            
            def do_extraction():
                try:
                    # Extract ALL files from the backup (not just config.php)
                    # Pass progress callback for live updates with batch_size=1 for real-time updates
                    fast_extract_tar_gz(
                        extracted_file, 
                        extract_temp, 
                        progress_callback=extraction_progress_callback,
                        batch_size=1,  # Update for every file, like 7-Zip
                        prepare_callback=prepare_extraction_callback
                    )
                    extraction_done[0] = True
                except Exception as ex:
                    extraction_done[0] = ex
            
            # Start extraction in a thread
            extraction_thread = threading.Thread(target=do_extraction, daemon=True)
            extraction_thread.start()
            
            # Wait for thread to finish
            extraction_thread.join()
            
            # Check if extraction failed
            if extraction_done[0] is not True:
                if isinstance(extraction_done[0], Exception):
                    raise extraction_done[0]
                else:
                    raise Exception("Extraction failed")
                    
        except Exception as e:
            tb = traceback.format_exc()
            self.set_restore_progress(0, "Restore failed!")
            error_msg = str(e)
            # Provide user-friendly error messages
            if "Invalid or corrupted archive" in error_msg or "ReadError" in error_msg:
                user_msg = "Extraction failed: The backup archive appears to be corrupted or invalid"
            elif "No space left on device" in error_msg:
                user_msg = "Extraction failed: Not enough disk space to extract the backup"
            elif "Permission denied" in error_msg:
                user_msg = "Extraction failed: Permission denied - please check file permissions"
            else:
                user_msg = f"Extraction failed: {e}"
            safe_widget_update(
                self.error_label,
                lambda: self.error_label.config(text=user_msg),
                "error label update after extraction failure"
            )
            print(f"Error details:\n{tb}")
            shutil.rmtree(extract_temp, ignore_errors=True)
            return None

        self.set_restore_progress(20, "Extraction complete!")
        safe_widget_update(
            self.process_label,
            lambda: self.process_label.config(text="Extraction complete."),
            "process label update after extraction"
        )
        return extract_temp  # Temp folder with extracted files

    # The rest of the class code (ensure_nextcloud_container, ensure_db_container, etc.) remains unchanged.
    # ... (rest of the code unchanged from your previous script) ...

    def ensure_nextcloud_container(self, dbtype=None):
        """Ensure Nextcloud container is running, using values from GUI
        
        Args:
            dbtype: Database type ('sqlite', 'mysql', 'pgsql'). If 'sqlite', skip DB container linking.
        """
        container = get_nextcloud_container_name()
        
        # Check if we should use existing container
        if container and self.restore_use_existing:
            self.set_restore_progress(20, f"Using existing Nextcloud container: {container}")
            self.process_label.config(text=f"Using container: {container}")
            self.update_idletasks()
            
            # Check and attach to bridge network if not connected
            if not check_container_network(container, "bridge"):
                self.set_restore_progress(20, f"Attaching {container} to bridge network...")
                self.process_label.config(text=f"Connecting container to bridge network...")
                self.update_idletasks()
                
                if not attach_container_to_network(container, "bridge"):
                    error_msg = (
                        f"Failed to attach container '{container}' to bridge network.\n\n"
                        "This is required for the restore process to work correctly.\n"
                        "Please ensure the container is running and you have permission to modify it.\n\n"
                        "You can manually attach it using:\n"
                        f"  docker network connect bridge {container}\n\n"
                        "Or restart the container with proper network settings."
                    )
                    self.set_restore_progress(0, "Restore failed!")
                    self.error_label.config(text=error_msg)
                    messagebox.showerror("Network Connection Failed", error_msg)
                    return None
                
                self.set_restore_progress(20, f"Container {container} attached to bridge network")
            
            return container
        
        # Start a new container with configured values
        new_container_name = self.restore_container_name
        port = self.restore_container_port
        
        self.set_restore_progress(20, "Checking for Nextcloud image...")
        self.process_label.config(text="Checking if Nextcloud image is available...")
        self.update_idletasks()
        
        # Check if image exists locally
        check_image = subprocess.run(
            f'docker images -q {NEXTCLOUD_IMAGE}',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        if not check_image.stdout.strip():
            # Need to pull image
            self.set_restore_progress(20, "Pulling Nextcloud image (first-time setup)...")
            self.process_label.config(text="Downloading Nextcloud image from Docker Hub...")
            self.update_idletasks()
            
            pull_result = subprocess.run(
                f'docker pull {NEXTCLOUD_IMAGE}',
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if pull_result.returncode != 0:
                # Analyze Docker error
                error_info = analyze_docker_error(pull_result.stderr, container_name=new_container_name)
                
                # Log to dedicated Docker error file
                log_docker_error(
                    error_type='image_pull_failed',
                    error_message=pull_result.stderr,
                    container_name=new_container_name,
                    additional_info=f"Failed to pull image: {NEXTCLOUD_IMAGE}"
                )
                
                error_msg = f"Failed to pull Nextcloud image: {error_info['user_message']}"
                self.set_restore_progress(0, "Restore failed!")
                self.error_label.config(text=error_msg, fg="red")
                
                # Store and show error dialog
                self.last_docker_error = {
                    'error_info': error_info,
                    'stderr': pull_result.stderr,
                    'container_name': new_container_name,
                    'port': None
                }
                self.show_docker_error_page(error_info, pull_result.stderr, f"{NEXTCLOUD_IMAGE} (image)", "N/A")
                
                return None
            
            self.set_restore_progress(20, "Image downloaded successfully")
            self.process_label.config(text="✓ Nextcloud image ready")
        else:
            self.set_restore_progress(20, "Using cached Nextcloud image")
            self.process_label.config(text="✓ Nextcloud image found")
        
        self.update_idletasks()
        time.sleep(0.5)
        
        self.set_restore_progress(20, f"Creating Nextcloud container on port {port}...")
        self.process_label.config(text=f"Creating container: {new_container_name}")
        self.update_idletasks()
        
        # For SQLite, do NOT attempt to link to database container
        # For MySQL/PostgreSQL, try to link to database container for proper Docker networking
        
        # Prepare admin credentials environment variables if available
        admin_env = ""
        if hasattr(self, 'restore_admin_user') and self.restore_admin_user:
            # Use shlex.quote to safely escape credentials and prevent command injection
            safe_user = shlex.quote(self.restore_admin_user)
            safe_password = shlex.quote(self.restore_admin_password)
            admin_env = f'-e NEXTCLOUD_ADMIN_USER={safe_user} -e NEXTCLOUD_ADMIN_PASSWORD={safe_password} '
        
        if dbtype == 'sqlite':
            # SQLite - no database container, start without linking
            logger.info("SQLite detected - starting Nextcloud container without database linking")
            result = subprocess.run(
                f'docker run -d --name {new_container_name} {admin_env}--network bridge -p {port}:80 {NEXTCLOUD_IMAGE}',
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        else:
            # MySQL/PostgreSQL - try to link to database container
            # First attempt with link and explicit bridge network
            result = subprocess.run(
                f'docker run -d --name {new_container_name} {admin_env}--network bridge --link {POSTGRES_CONTAINER_NAME}:db -p {port}:80 {NEXTCLOUD_IMAGE}',
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            # If linking failed, try without link but still with bridge network
            if result.returncode != 0 and "Could not find" in result.stderr:
                print(f"Warning: Could not link to database container, starting without link: {result.stderr}")
                result = subprocess.run(
                    f'docker run -d --name {new_container_name} {admin_env}--network bridge -p {port}:80 {NEXTCLOUD_IMAGE}',
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
        
        if result.returncode != 0:
            tb = traceback.format_exc()
            
            # Analyze Docker error
            error_info = analyze_docker_error(result.stderr, container_name=new_container_name, port=port, dbtype=dbtype)
            
            # Log to dedicated Docker error file
            log_docker_error(
                error_type=error_info['error_type'],
                error_message=result.stderr,
                container_name=new_container_name,
                port=port,
                additional_info=f"Full traceback:\n{tb}"
            )
            
            # Build user-friendly error message
            error_msg = (
                f"Failed to start Nextcloud container.\n\n"
                f"{error_info['user_message']}\n\n"
                f"Raw Error: {result.stderr[:200]}..."  # Show first 200 chars
            )
            
            self.set_restore_progress(0, "Restore failed!")
            self.error_label.config(text=error_info['user_message'], fg="red")
            print(f"Container start failed: {result.stderr}\n{tb}")
            
            # Store error info for detailed view
            self.last_docker_error = {
                'error_info': error_info,
                'stderr': result.stderr,
                'container_name': new_container_name,
                'port': port
            }
            
            # Show error page (not dialog) within the main GUI
            self.show_docker_error_page(error_info, result.stderr, new_container_name, port)
            
            return None
        
        container_id = new_container_name
        self.set_restore_progress(20, f"Container created: {container_id}")
        self.process_label.config(text=f"✓ Container created on port {port}")
        self.update_idletasks()
        
        self.set_restore_progress(20, "Waiting for Nextcloud to initialize...")
        self.process_label.config(text="Waiting for container to be ready...")
        self.update_idletasks()
        time.sleep(5)
        
        return container_id

    def ensure_db_container(self, dbtype=None):
        """Ensure database container is running, using credentials from GUI
        
        Args:
            dbtype: Database type ('sqlite', 'mysql', 'pgsql')
        """
        db_container = get_postgres_container_name()
        if db_container:
            # Check and attach to bridge network if not connected
            if not check_container_network(db_container, "bridge"):
                self.set_restore_progress(20, f"Attaching {db_container} to bridge network...")
                self.process_label.config(text=f"Connecting DB container to bridge network...")
                self.update_idletasks()
                
                if not attach_container_to_network(db_container, "bridge"):
                    error_msg = (
                        f"Failed to attach database container '{db_container}' to bridge network.\n\n"
                        "This is required for the restore process to work correctly.\n"
                        "Please ensure the container is running and you have permission to modify it.\n\n"
                        "You can manually attach it using:\n"
                        f"  docker network connect bridge {db_container}\n\n"
                        "Or restart the container with proper network settings."
                    )
                    self.set_restore_progress(0, "Restore failed!")
                    self.error_label.config(text=error_msg)
                    messagebox.showerror("Network Connection Failed", error_msg)
                    return None
                
                self.set_restore_progress(20, f"Database container {db_container} attached to bridge network")
            
            return db_container
        
        self.set_restore_progress(20, "Checking for database image...")
        self.process_label.config(text="Checking if database image is available...")
        self.update_idletasks()
        
        # Check if PostgreSQL image exists locally
        check_db_image = subprocess.run(
            f'docker images -q {POSTGRES_IMAGE}',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        if not check_db_image.stdout.strip():
            self.set_restore_progress(20, "Pulling PostgreSQL image...")
            self.process_label.config(text="Downloading PostgreSQL image...")
            self.update_idletasks()
            
            pull_db_result = subprocess.run(
                f'docker pull {POSTGRES_IMAGE}',
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if pull_db_result.returncode != 0:
                # Analyze Docker error
                error_info = analyze_docker_error(pull_db_result.stderr, container_name=POSTGRES_CONTAINER_NAME, dbtype=dbtype)
                
                # Log to dedicated Docker error file
                log_docker_error(
                    error_type='image_pull_failed',
                    error_message=pull_db_result.stderr,
                    container_name=POSTGRES_CONTAINER_NAME,
                    additional_info=f"Failed to pull image: {POSTGRES_IMAGE}"
                )
                
                error_msg = f"Failed to pull PostgreSQL image: {error_info['user_message']}"
                self.set_restore_progress(0, "Restore failed!")
                self.error_label.config(text=error_msg, fg="red")
                
                # Store and show error dialog
                self.last_docker_error = {
                    'error_info': error_info,
                    'stderr': pull_db_result.stderr,
                    'container_name': POSTGRES_CONTAINER_NAME,
                    'port': None
                }
                self.show_docker_error_page(error_info, pull_db_result.stderr, f"{POSTGRES_IMAGE} (image)", "N/A")
                
                return None
        
        self.set_restore_progress(20, "Creating database container...")
        self.process_label.config(text=f"Starting DB container: {POSTGRES_CONTAINER_NAME}")
        self.update_idletasks()
        
        # Use credentials from GUI and explicitly set network to bridge
        result = subprocess.run(
            f'docker run -d --name {POSTGRES_CONTAINER_NAME} '
            f'--network bridge '
            f'-e POSTGRES_DB={self.restore_db_name} '
            f'-e POSTGRES_USER={self.restore_db_user} '
            f'-e POSTGRES_PASSWORD={self.restore_db_password} '
            f'-p {POSTGRES_PORT}:5432 {POSTGRES_IMAGE}',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        if result.returncode != 0:
            tb = traceback.format_exc()
            
            # Analyze Docker error
            error_info = analyze_docker_error(result.stderr, container_name=POSTGRES_CONTAINER_NAME, port=POSTGRES_PORT, dbtype=dbtype)
            
            # Log to dedicated Docker error file
            log_docker_error(
                error_type=error_info['error_type'],
                error_message=result.stderr,
                container_name=POSTGRES_CONTAINER_NAME,
                port=POSTGRES_PORT,
                additional_info=f"Full traceback:\n{tb}"
            )
            
            # Build user-friendly error message
            error_msg = (
                f"Failed to start PostgreSQL container.\n\n"
                f"{error_info['user_message']}\n\n"
                f"Raw Error: {result.stderr[:200]}..."  # Show first 200 chars
            )
            
            self.set_restore_progress(0, "Restore failed!")
            self.error_label.config(text=error_info['user_message'], fg="red")
            print(f"Database container start failed: {result.stderr}\n{tb}")
            
            # Store error info for detailed view
            self.last_docker_error = {
                'error_info': error_info,
                'stderr': result.stderr,
                'container_name': POSTGRES_CONTAINER_NAME,
                'port': POSTGRES_PORT
            }
            
            # Show error page (not dialog) within the main GUI
            self.show_docker_error_page(error_info, result.stderr, POSTGRES_CONTAINER_NAME, POSTGRES_PORT)
            
            return None
        
        db_container_id = POSTGRES_CONTAINER_NAME
        self.set_restore_progress(20, f"Started DB container: {db_container_id}")
        self.process_label.config(text=f"Started DB container: {db_container_id}")
        self.update_idletasks()
        time.sleep(5)
        return db_container_id

    def restore_sqlite_database(self, extract_dir, nextcloud_container, nextcloud_path):
        """Restore SQLite database by copying the .db file"""
        try:
            # Look for SQLite database file (usually owncloud.db or nextcloud.db)
            db_files = []
            data_dir = os.path.join(extract_dir, "data")
            
            self.set_restore_progress(82, "Checking for SQLite database...")
            
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if file.endswith('.db'):
                        db_files.append(file)
            
            if not db_files:
                warning_msg = "Warning: No SQLite .db file found in backup data folder. Database restore skipped."
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update"
                )
                print(warning_msg)
                return False
            
            # Use the first .db file found (typically owncloud.db or nextcloud.db)
            db_file = db_files[0]
            db_path = os.path.join(data_dir, db_file)
            
            # Get file size for progress display
            db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            db_size_str = self._format_bytes(db_size)
            
            self.set_restore_progress(85, f"Verifying SQLite database: {db_file} ({db_size_str})")
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text=f"Verifying SQLite database: {db_file} ({db_size_str})"),
                "process label update"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            
            # The .db file should already be copied with the data folder
            # Just verify it exists
            self.set_restore_progress(87, f"Validating SQLite database in container...")
            check_cmd = f'docker exec {nextcloud_container} test -f {nextcloud_path}/data/{db_file}'
            result = subprocess.run(check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode == 0:
                self.set_restore_progress(90, f"✓ SQLite database restored successfully")
                logger.info(f"SQLite database file {db_file} successfully restored")
                return True
            else:
                error_msg = f"Error: SQLite database file {db_file} not found in container after copy"
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=error_msg, fg="red"),
                    "error label update"
                )
                return False
                
        except Exception as e:
            tb = traceback.format_exc()
            safe_widget_update(
                self.error_label,
                lambda: self.error_label.config(text=f"SQLite database restore error: {e}\n{tb}"),
                "error label update"
            )
            logger.error(f"SQLite restore error: {e}")
            print(tb)
            return False
    
    def restore_mysql_database(self, extract_dir, db_container):
        """Restore MySQL/MariaDB database from SQL dump"""
        sql_path = os.path.join(extract_dir, "nextcloud-db.sql")
        
        if not os.path.isfile(sql_path):
            warning_msg = "Warning: No database backup file (nextcloud-db.sql) found in backup. Skipping database restore."
            self.error_label.config(text=warning_msg, fg="orange")
            print(warning_msg)
            return False
        
        try:
            # Get file size for progress estimation
            sql_size = os.path.getsize(sql_path)
            sql_size_str = self._format_bytes(sql_size)
            
            self.set_restore_progress(82, f"Restoring MySQL database ({sql_size_str})...")
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text=f"Restoring MySQL database ({sql_size_str})..."),
                "process label update"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            
            # Use credentials from GUI - MySQL version
            restore_cmd = f'docker exec -i {db_container} bash -c "mysql -u {self.restore_db_user} -p{self.restore_db_password} {self.restore_db_name}"'
            
            # Start restore in thread with progress updates
            restore_done = [False]
            restore_result = [None, None]  # [returncode, stderr]
            
            def do_restore():
                try:
                    with open(sql_path, "rb") as f:
                        proc = subprocess.Popen(restore_cmd, shell=True, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = proc.communicate()
                        restore_result[0] = proc.returncode
                        restore_result[1] = stderr
                    restore_done[0] = True
                except Exception as e:
                    restore_result[0] = -1
                    restore_result[1] = str(e).encode()
                    restore_done[0] = True
            
            restore_thread = threading.Thread(target=do_restore, daemon=True)
            restore_thread.start()
            
            # Update progress while restoring (82-89% range)
            progress = 82
            last_update = time.time()
            while not restore_done[0]:
                current_time = time.time()
                if current_time - last_update >= 1.0 and progress < 89:
                    progress += 1
                    self.set_restore_progress(progress, f"Restoring MySQL database ({sql_size_str})...")
                    last_update = current_time
                time.sleep(0.2)
            
            restore_thread.join()
            
            # Check results
            if restore_result[0] != 0:
                error_msg = restore_result[1].decode('utf-8', errors='replace') if restore_result[1] else "Unknown error"
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=f"MySQL database restore failed: {error_msg}"),
                    "error label update"
                )
                return False
            
            # Validate that database tables were imported
            self.set_restore_progress(90, "Validating MySQL database restore...")
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text="Validating MySQL database restore..."),
                "process label update"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            
            check_cmd = f'docker exec {db_container} bash -c "mysql -u {self.restore_db_user} -p{self.restore_db_password} {self.restore_db_name} -e \'SHOW TABLES;\'"'
            result = subprocess.run(check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0 and "oc_" in result.stdout:
                print(f"MySQL database validation successful. Tables found.")
                return True
            else:
                warning_msg = "Warning: Could not validate MySQL database tables. Please check manually."
                self.error_label.config(text=warning_msg, fg="orange")
                print(f"Warning: MySQL database validation unclear: {result.stdout}")
                return True  # Don't fail restore, just warn
                
        except Exception as e:
            tb = traceback.format_exc()
            self.error_label.config(text=f"MySQL database restore error: {e}\n{tb}")
            print(tb)
            return False
    
    def restore_postgresql_database(self, extract_dir, db_container):
        """Restore PostgreSQL database from SQL dump"""
        sql_path = os.path.join(extract_dir, "nextcloud-db.sql")
        
        if not os.path.isfile(sql_path):
            warning_msg = "Warning: No database backup file (nextcloud-db.sql) found in backup. Skipping database restore."
            self.error_label.config(text=warning_msg, fg="orange")
            print(warning_msg)
            return False
        
        try:
            # Get file size for progress estimation
            sql_size = os.path.getsize(sql_path)
            sql_size_str = self._format_bytes(sql_size)
            
            self.set_restore_progress(82, f"Restoring PostgreSQL database ({sql_size_str})...")
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text=f"Restoring PostgreSQL database ({sql_size_str})..."),
                "process label update"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            
            # Use credentials from GUI
            restore_cmd = f'docker exec -i {db_container} bash -c "PGPASSWORD={self.restore_db_password} psql -U {self.restore_db_user} -d {self.restore_db_name}"'
            
            # Start restore in thread with progress updates
            restore_done = [False]
            restore_result = [None, None]  # [returncode, stderr]
            
            def do_restore():
                try:
                    with open(sql_path, "rb") as f:
                        proc = subprocess.Popen(restore_cmd, shell=True, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = proc.communicate()
                        restore_result[0] = proc.returncode
                        restore_result[1] = stderr
                    restore_done[0] = True
                except Exception as e:
                    restore_result[0] = -1
                    restore_result[1] = str(e).encode()
                    restore_done[0] = True
            
            restore_thread = threading.Thread(target=do_restore, daemon=True)
            restore_thread.start()
            
            # Update progress while restoring (82-89% range)
            progress = 82
            last_update = time.time()
            while not restore_done[0]:
                current_time = time.time()
                if current_time - last_update >= 1.0 and progress < 89:
                    progress += 1
                    self.set_restore_progress(progress, f"Restoring PostgreSQL database ({sql_size_str})...")
                    last_update = current_time
                time.sleep(0.2)
            
            restore_thread.join()
            
            # Check results
            if restore_result[0] != 0:
                error_msg = restore_result[1].decode('utf-8', errors='replace') if restore_result[1] else "Unknown error"
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=f"PostgreSQL database restore failed: {error_msg}"),
                    "error label update"
                )
                return False
            
            # Validate that database tables were imported
            self.set_restore_progress(90, "Validating PostgreSQL database restore...")
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text="Validating PostgreSQL database restore..."),
                "process label update"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            
            check_cmd = f'docker exec {db_container} bash -c "PGPASSWORD={self.restore_db_password} psql -U {self.restore_db_user} -d {self.restore_db_name} -c \'\\dt\'"'
            result = subprocess.run(check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0 and "oc_" in result.stdout:
                print(f"PostgreSQL database validation successful. Tables found.")
                return True
            else:
                warning_msg = "Warning: Could not validate PostgreSQL database tables. Please check manually."
                self.error_label.config(text=warning_msg, fg="orange")
                print(f"Warning: PostgreSQL database validation unclear: {result.stdout}")
                return True  # Don't fail restore, just warn
                
        except Exception as e:
            tb = traceback.format_exc()
            self.error_label.config(text=f"PostgreSQL database restore error: {e}\n{tb}")
            print(tb)
            return False
    
    def detect_database_type(self, extract_dir):
        """
        Detect database type from config.php in the extracted backup.
        Uses recursive search to find config.php in any subdirectory.
        Returns: (dbtype, db_config) or (None, None) if detection fails
        """
        # First try the standard location
        config_path = os.path.join(extract_dir, "config", "config.php")
        
        if not os.path.exists(config_path):
            print(f"config.php not found at standard location: {config_path}")
            print("Performing recursive search for config.php...")
            # Recursively search for config.php in any subdirectory
            config_path = find_config_php_recursive(extract_dir)
            
            if not config_path:
                print("⚠️ Warning: config.php not found in backup after recursive search")
                print("Cannot auto-detect database type - will use defaults")
                return None, None
        else:
            print(f"Found config.php at standard location: {config_path}")
        
        dbtype, db_config = parse_config_php_dbtype(config_path)
        
        if dbtype:
            print(f"✓ Auto-detected database type: {dbtype}")
            if db_config:
                print(f"Database config from backup: {db_config}")
        else:
            print("⚠️ Warning: Could not parse database type from config.php")
        
        return dbtype, db_config
    
    def early_detect_database_type_from_backup(self, backup_path, password=None):
        """
        Early detection: Extract ONLY config.php from backup to detect database type.
        
        This is a lightweight operation that allows us to determine the database type
        (SQLite, MySQL, or PostgreSQL) without extracting the full backup archive, which
        can be several gigabytes and take minutes to extract.
        
        IMPORTANT BEHAVIOR:
        - On startup/Page 1 navigation: Only config.php is extracted (fast, <1 second)
        - Database type is detected from config.php to control UI (show/hide credential fields)
        - Full archive extraction is deferred until actual restore process begins
        
        This two-phase approach keeps the GUI responsive and provides a better user experience:
        - SQLite users never see unnecessary database credential fields
        - MySQL/PostgreSQL users see the appropriate fields immediately
        - No waiting for full extraction until user is ready to proceed
        
        Args:
            backup_path: Path to the backup file (.tar.gz or .tar.gz.gpg)
            password: Optional decryption password for encrypted backups
        
        Returns: 
            (dbtype, db_config): Database type and configuration dict, or (None, None) if detection fails
            
        Note: 
            - Handles both encrypted (.gpg) and unencrypted backups
            - Normalizes 'sqlite3' to 'sqlite' for consistent handling
            - All operations run in background thread for GUI responsiveness
            - Temporary files are cleaned up automatically
        """
        temp_extract_dir = None
        temp_decrypted_path = None
        
        try:
            # Step 1: Handle encrypted backups - decrypt if needed
            if backup_path.endswith('.gpg'):
                if not password:
                    # Password not provided - cannot decrypt
                    # This is expected when called before password entry - detection will happen later
                    print("⚠️ Encrypted backup requires password for detection")
                    return None, None
                
                print("🔐 Decrypting backup for database type detection...")
                # Decrypt to a temporary file
                temp_decrypted_path = tempfile.mktemp(suffix=".tar.gz", prefix="nextcloud_decrypt_")
                
                try:
                    decrypt_file_gpg(backup_path, temp_decrypted_path, password)
                    print("✓ Backup decrypted successfully for early detection")
                    # Use the decrypted file for extraction
                    backup_to_extract = temp_decrypted_path
                except FileNotFoundError as decrypt_err:
                    # GPG command not found
                    error_msg = "GPG (GNU Privacy Guard) is not installed or not in PATH"
                    print(f"✗ Failed to decrypt backup: {error_msg}")
                    logger.error(f"GPG not found: {decrypt_err}")
                    raise Exception(error_msg)
                except Exception as decrypt_err:
                    error_msg = str(decrypt_err)
                    if "Bad session key" in error_msg or "decryption failed" in error_msg:
                        print(f"✗ Failed to decrypt backup: Incorrect password")
                        logger.error(f"GPG decryption failed: incorrect password")
                        raise Exception("Incorrect decryption password")
                    elif "gpg: command not found" in error_msg or "not found" in error_msg.lower():
                        print(f"✗ Failed to decrypt backup: GPG is not installed")
                        logger.error(f"GPG not installed: {error_msg}")
                        raise Exception("GPG is not installed")
                    else:
                        print(f"✗ Failed to decrypt backup: {decrypt_err}")
                        logger.error(f"GPG decryption error: {error_msg}")
                        raise Exception(f"GPG decryption failed: {error_msg}")
            else:
                # Unencrypted backup - use directly
                backup_to_extract = backup_path
            
            # Step 2: Extract ONLY config.php (efficient single-file extraction)
            # This is much faster than extracting the entire multi-gigabyte backup
            # Use timestamp-based directory for better traceability
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            temp_extract_dir = tempfile.mkdtemp(prefix=f"ncbackup_extract_{timestamp}_")
            print(f"=" * 70)
            print(f"📂 Config.php Extraction for Database Detection")
            print(f"=" * 70)
            print(f"Backup file: {os.path.basename(backup_to_extract)}")
            print(f"Extraction directory: {temp_extract_dir}")
            print(f"Detection only occurs in this temporary directory")
            print(f"=" * 70)
            
            try:
                # Use efficient single-file extraction instead of extracting everything
                config_path = extract_config_php_only(backup_to_extract, temp_extract_dir)
                
                if not config_path:
                    print("⚠️ Early detection: config.php not found in backup archive")
                    print("   This may indicate an incompatible backup format")
                    return None, None
                    
            except tarfile.ReadError as extract_err:
                print(f"✗ Failed to extract backup: Invalid or corrupted archive")
                print(f"  Error details: {extract_err}")
                logger.error(f"tarfile ReadError: {extract_err}")
                raise Exception(f"Invalid or corrupted archive: {extract_err}")
            except Exception as extract_err:
                print(f"✗ Failed to extract backup: {extract_err}")
                logger.error(f"Extraction error: {extract_err}")
                raise Exception(f"Extraction failed: {extract_err}")
            
            # Step 3: Parse the config.php file to extract database configuration
            print(f"📖 Parsing config.php to detect database type...")
            dbtype, db_config = parse_config_php_dbtype(config_path)
            
            # Normalize sqlite3 to sqlite for consistent handling throughout the app
            if dbtype and dbtype.lower() in ['sqlite', 'sqlite3']:
                dbtype = 'sqlite'
                if db_config:
                    db_config['dbtype'] = 'sqlite'
            
            # Step 3.5: Parse full config.php for Docker Compose detection
            # This happens immediately after database detection as per requirements
            full_config = None
            if config_path and os.path.exists(config_path):
                print(f"📖 Parsing full config.php for Docker Compose detection...")
                full_config = parse_config_php_full(config_path)
                
                if full_config:
                    # Store full config for later use in showing Docker Compose suggestion
                    self.detected_full_config = full_config
                    
                    # Detect Docker Compose usage
                    print(f"🔍 Detecting Docker Compose usage...")
                    is_compose, compose_file = detect_docker_compose_usage()
                    self.detected_compose_usage = is_compose
                    self.detected_compose_file = compose_file
                    
                    if is_compose:
                        print(f"✓ Docker Compose usage detected")
                        if compose_file:
                            print(f"  Found compose file: {compose_file}")
                    else:
                        print(f"ℹ️ No Docker Compose usage detected - can generate new compose file")
            
            # Report results
            print(f"=" * 70)
            print(f"📊 Database Detection Results")
            print(f"=" * 70)
            if dbtype:
                print(f"✓ Detection Status: Successful")
                print(f"Database Type: {dbtype.upper()}")
                if db_config:
                    print(f"Database Configuration:")
                    for key, value in db_config.items():
                        # Don't print sensitive info like passwords
                        if 'password' not in key.lower():
                            print(f"  - {key}: {value}")
                print(f"=" * 70)
            else:
                print(f"✗ Detection Status: Failed")
                print(f"Reason: Could not parse database type from config.php")
                print(f"Details: The config.php file may be malformed or use an unexpected format")
                print(f"=" * 70)
            
            return dbtype, db_config
            
        except Exception as e:
            print(f"✗ Early detection error: {e}")
            traceback.print_exc()
            return None, None
        finally:
            # Step 4: Clean up temporary files
            # Always clean up, even if an error occurred, to avoid leaving temp files
            
            # Clean up temporary decrypted file (only exists for encrypted backups)
            if temp_decrypted_path and os.path.exists(temp_decrypted_path):
                try:
                    file_size = os.path.getsize(temp_decrypted_path)
                    os.remove(temp_decrypted_path)
                    print(f"=" * 70)
                    print(f"🧹 Cleanup: Temporary Decrypted File")
                    print(f"=" * 70)
                    print(f"Removed: {temp_decrypted_path}")
                    print(f"Size: {file_size / (1024*1024):.2f} MB")
                    print(f"✓ Cleanup successful")
                    print(f"=" * 70)
                except Exception as cleanup_err:
                    print(f"⚠️ Warning: Could not clean up temp decrypted file")
                    print(f"   Path: {temp_decrypted_path}")
                    print(f"   Error: {cleanup_err}")
            
            # Clean up temporary extraction directory (contains only config.php)
            if temp_extract_dir and os.path.exists(temp_extract_dir):
                try:
                    # Calculate directory size before cleanup
                    dir_size = sum(
                        os.path.getsize(os.path.join(root, file))
                        for root, _, files in os.walk(temp_extract_dir)
                        for file in files
                    )
                    file_count = sum(len(files) for _, _, files in os.walk(temp_extract_dir))
                    
                    shutil.rmtree(temp_extract_dir)
                    print(f"=" * 70)
                    print(f"🧹 Cleanup: Temporary Extraction Directory")
                    print(f"=" * 70)
                    print(f"Removed: {temp_extract_dir}")
                    print(f"Files removed: {file_count}")
                    print(f"Space freed: {dir_size / 1024:.2f} KB")
                    print(f"✓ Cleanup successful")
                    print(f"=" * 70)
                except Exception as cleanup_err:
                    print(f"⚠️ Warning: Could not clean up temp directory")
                    print(f"   Path: {temp_extract_dir}")
                    print(f"   Error: {cleanup_err}")
    
    def show_db_detection_message(self, dbtype, db_config):
        """Show a message to user about detected database type and allow override"""
        db_display_names = {
            'sqlite': 'SQLite',
            'pgsql': 'PostgreSQL', 
            'mysql': 'MySQL/MariaDB'
        }
        
        db_name = db_display_names.get(dbtype, dbtype)
        
        msg = f"Auto-detected database type: {db_name}\n\n"
        
        if db_config:
            if 'dbname' in db_config:
                msg += f"Database name: {db_config['dbname']}\n"
            if 'dbuser' in db_config:
                msg += f"Database user: {db_config['dbuser']}\n"
        
        msg += "\nThe restore will use this configuration.\n"
        msg += "Make sure the database credentials you entered match this backup."
        
        self.process_label.config(text=msg)
        print(f"Detected database info shown to user: {dbtype}")
    
    def show_docker_compose_suggestion(self):
        """
        Show a dialog suggesting Docker Compose file generation based on config.php.
        Called after database detection if full config was parsed successfully.
        """
        if not self.detected_full_config:
            return
        
        # Create modal dialog
        dialog = tk.Toplevel(self)
        dialog.title("Docker Compose Detection")
        dialog.geometry("700x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Header
        header_frame = tk.Frame(dialog, bg="#3daee9", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        tk.Label(
            header_frame, 
            text="🐋 Docker Compose Configuration",
            font=("Arial", 16, "bold"),
            bg="#3daee9",
            fg="white"
        ).pack(pady=15)
        
        # Main content frame with scrollbar
        content_frame = tk.Frame(dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Environment detection info
        info_text = tk.Text(content_frame, height=15, wrap="word", font=("Arial", 10))
        info_text.pack(fill="both", expand=True)
        
        # Build detection message
        message = "=" * 60 + "\n"
        message += "DETECTED ENVIRONMENT CONFIGURATION\n"
        message += "=" * 60 + "\n\n"
        
        config = self.detected_full_config
        message += f"📊 Database Type: {config.get('dbtype', 'Unknown').upper()}\n"
        message += f"📦 Database Name: {config.get('dbname', 'Not specified')}\n"
        message += f"👤 Database User: {config.get('dbuser', 'Not specified')}\n"
        message += f"🗄️  Database Host: {config.get('dbhost', 'Not specified')}\n"
        
        if config.get('datadirectory'):
            message += f"📁 Data Directory: {config.get('datadirectory')}\n"
        
        if config.get('trusted_domains'):
            message += f"🌐 Trusted Domains: {', '.join(config.get('trusted_domains', []))}\n"
        
        message += "\n" + "=" * 60 + "\n"
        message += "DOCKER COMPOSE STATUS\n"
        message += "=" * 60 + "\n\n"
        
        if self.detected_compose_usage:
            message += "✓ Docker Compose usage detected!\n"
            if self.detected_compose_file:
                message += f"  Found: {self.detected_compose_file}\n\n"
            message += "⚠️  WARNING: If your existing docker-compose.yml doesn't match\n"
            message += "the detected config.php settings, you may experience issues.\n\n"
            message += "We recommend reviewing your docker-compose.yml to ensure:\n"
            message += "  • Volume mappings match the detected data directory\n"
            message += "  • Database credentials match config.php\n"
            message += "  • Port mappings are correct\n"
        else:
            message += "ℹ️  No Docker Compose usage detected.\n\n"
            message += "We can generate a docker-compose.yml file for you based on\n"
            message += "the detected configuration. This will make your restore:\n"
            message += "  ✓ Safer and more reproducible\n"
            message += "  ✓ Easier to migrate or restore again\n"
            message += "  ✓ Better documented and portable\n"
        
        message += "\n" + "=" * 60 + "\n"
        message += "HOST FOLDER REQUIREMENTS\n"
        message += "=" * 60 + "\n\n"
        message += "Before starting containers, ensure these folders exist:\n"
        message += "  • ./nextcloud-data (for Nextcloud files)\n"
        if config.get('dbtype') not in ['sqlite', 'sqlite3']:
            message += "  • ./db-data (for database files)\n"
        message += "\nThese folders will be created if they don't exist.\n"
        
        info_text.insert("1.0", message)
        info_text.config(state="disabled")
        
        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def generate_compose():
            """Generate and save docker-compose.yml"""
            try:
                # Ask user where to save
                save_path = filedialog.asksaveasfilename(
                    title="Save docker-compose.yml",
                    defaultextension=".yml",
                    initialfile="docker-compose.yml",
                    filetypes=[("YAML files", "*.yml"), ("YAML files", "*.yaml"), ("All files", "*.*")]
                )
                
                if not save_path:
                    return
                
                # Generate compose file
                compose_content = generate_docker_compose_yml(
                    config,
                    nextcloud_port=self.wizard_data.get('container_port', 8080),
                    db_port=5432
                )
                
                # Write to file
                with open(save_path, 'w') as f:
                    f.write(compose_content)
                
                messagebox.showinfo(
                    "Success",
                    f"docker-compose.yml saved to:\n{save_path}\n\n"
                    "You can now use 'docker-compose up -d' to start your containers."
                )
                
                print(f"✓ Generated docker-compose.yml at: {save_path}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate docker-compose.yml:\n{e}")
                print(f"Error generating compose file: {e}")
        
        def check_folders():
            """Check and create required host folders"""
            try:
                folders = ['./nextcloud-data']
                if config.get('dbtype') not in ['sqlite', 'sqlite3']:
                    folders.append('./db-data')
                
                created = []
                existing = []
                
                for folder in folders:
                    if os.path.exists(folder):
                        existing.append(folder)
                    else:
                        os.makedirs(folder, exist_ok=True)
                        created.append(folder)
                
                msg = "Folder Check Complete\n\n"
                if created:
                    msg += "Created:\n" + "\n".join(f"  ✓ {f}" for f in created) + "\n\n"
                if existing:
                    msg += "Already exist:\n" + "\n".join(f"  ✓ {f}" for f in existing)
                
                messagebox.showinfo("Folder Check", msg)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folders:\n{e}")
        
        # Buttons
        tk.Button(
            button_frame,
            text="Generate docker-compose.yml",
            font=("Arial", 11, "bold"),
            bg="#45bf55",
            fg="white",
            command=generate_compose,
            width=25
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Check/Create Folders",
            font=("Arial", 11),
            bg="#f7b32b",
            fg="white",
            command=check_folders,
            width=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Continue",
            font=("Arial", 11),
            command=dialog.destroy,
            width=15
        ).pack(side="right", padx=5)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def update_database_credential_ui(self, dbtype):
        """
        Update the database credential UI based on detected database type.
        
        For SQLite/sqlite3: Hide credential fields and show informational message
        For MySQL/PostgreSQL: Show credential fields and hide SQLite message
        
        This method is called after early detection when user selects a backup file.
        """
        is_sqlite = dbtype and dbtype.lower() in ['sqlite', 'sqlite3']
        
        if is_sqlite:
            # Hide packed warning/instruction labels
            if hasattr(self, 'db_credential_packed_widgets'):
                for widget in self.db_credential_packed_widgets:
                    widget.pack_forget()
            
            # Hide the entire database credential frame (which contains grid widgets)
            if hasattr(self, 'db_credential_frame'):
                self.db_credential_frame.pack_forget()
            
            # Show SQLite informational message
            if hasattr(self, 'db_sqlite_message_label') and self.db_sqlite_message_label:
                self.db_sqlite_message_label.pack(pady=(10, 10), fill="x", padx=40)
        else:
            # Show packed warning/instruction labels
            if hasattr(self, 'db_credential_packed_widgets'):
                # Re-pack in the correct order with original settings
                self.db_credential_packed_widgets[0].pack(pady=(5, 0), fill="x", padx=40)  # warning_label
                self.db_credential_packed_widgets[1].pack(fill="x", padx=40)  # instruction_label1
                self.db_credential_packed_widgets[2].pack(pady=(0, 10), fill="x", padx=40)  # instruction_label2
            
            # Show the database credential frame
            if hasattr(self, 'db_credential_frame'):
                self.db_credential_frame.pack(pady=10, fill="x", padx=40)
            
            # Hide SQLite message
            if hasattr(self, 'db_sqlite_message_label') and self.db_sqlite_message_label:
                self.db_sqlite_message_label.pack_forget()
        
        print(f"UI updated for database type: {dbtype} (is_sqlite={is_sqlite})")
    
    def update_config_php(self, nextcloud_container, db_container, dbtype='pgsql'):
        """Update config.php with database credentials and admin settings"""
        # For SQLite, we don't need to update database host/credentials
        # The database file is already in the data directory
        if dbtype == 'sqlite':
            logger.info("SQLite detected - skipping database host/credential updates in config.php")
            print("SQLite database - no database host configuration needed")
            return
        
        config_updates = f"""
docker exec {nextcloud_container} bash -c "cat > /tmp/update_config.php << 'EOFPHP'
<?php
\\$configFile = '/var/www/html/config/config.php';
if (file_exists(\\$configFile)) {{
    \\$config = include(\\$configFile);
    
    // Update database configuration
    \\$config['dbtype'] = '{dbtype}';
    \\$config['dbname'] = '{self.restore_db_name}';
    \\$config['dbhost'] = '{db_container}';
    \\$config['dbuser'] = '{self.restore_db_user}';
    \\$config['dbpassword'] = '{self.restore_db_password}';
    
    // Write updated config
    \\$output = '<?php' . PHP_EOL;
    \\$output .= '\\$CONFIG = ' . var_export(\\$config, true) . ';' . PHP_EOL;
    file_put_contents(\\$configFile, \\$output);
    echo 'Config updated successfully';
}} else {{
    echo 'Config file not found';
}}
EOFPHP
php /tmp/update_config.php"
"""
        result = subprocess.run(config_updates, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to update config.php: {result.stderr}")
        print(f"Config.php update output: {result.stdout}")
    
    def start_restore_thread(self):
        threading.Thread(target=self._restore_auto_thread, args=(self.restore_backup_path, self.restore_password), daemon=True).start()

    def _restore_auto_thread(self, backup_path, password):
        try:
            # Log restore operation start
            logger.info("=" * 60)
            logger.info("RESTORE OPERATION STARTED")
            logger.info(f"Backup Path: {backup_path}")
            logger.info(f"Has Password: {'Yes' if password else 'No'}")
            if self.verbose_logging:
                logger.debug(f"Container Name: {self.restore_container_name}")
                logger.debug(f"Container Port: {self.restore_container_port}")
                logger.debug(f"Database Type: {self.restore_db_type}")
                logger.debug(f"Database Name: {self.restore_db_name}")
                logger.debug(f"Database User: {self.restore_db_user}")
            logger.info("=" * 60)
            
            # Extraction happens in auto_extract_backup and will set progress to 0-20%
            logger.info("Step 1/7: Extracting backup...")
            extract_dir = self.auto_extract_backup(backup_path, password)
            if not extract_dir:
                logger.error("Backup extraction failed!")
                self.set_restore_progress(0, "Restore failed!")
                return
            if self.verbose_logging:
                logger.debug(f"Extraction directory: {extract_dir}")

            # Auto-detect database type from config.php (20% - brief transition)
            self.set_restore_progress(20, "Detecting database type ...")
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text="Reading config.php to detect database type ..."),
                "process label update in restore thread"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            logger.info("Step 2/7: Detecting database configuration...")
            
            dbtype, db_config = self.detect_database_type(extract_dir)
            
            if dbtype:
                # Normalize sqlite3 to sqlite for consistent handling
                if dbtype.lower() in ['sqlite', 'sqlite3']:
                    dbtype = 'sqlite'
                    if db_config:
                        db_config['dbtype'] = 'sqlite'
                
                self.detected_dbtype = dbtype
                self.detected_db_config = db_config
                self.db_auto_detected = True
                logger.info(f"Database type detected: {dbtype}")
                if self.verbose_logging and db_config:
                    logger.debug(f"Database config: {db_config}")
                self.show_db_detection_message(dbtype, db_config)
                time.sleep(2)  # Give user time to see the detection message
            else:
                # Fallback: assume PostgreSQL (current default behavior)
                warning_msg = (
                    "⚠️ WARNING: config.php not found in backup!\n\n"
                    "Database type could not be automatically detected.\n"
                    "Using PostgreSQL as default. The restore will continue,\n"
                    "but please verify your database configuration matches your backup."
                )
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update in restore thread"
                )
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text="Proceeding with PostgreSQL (default)..."),
                    "process label update in restore thread"
                )
                logger.warning("config.php not found - using PostgreSQL as default")
                print(warning_msg)
                dbtype = 'pgsql'
                self.detected_dbtype = dbtype
                time.sleep(3)  # Give user more time to see the warning

            # Docker configuration (20% - brief setup before copying)
            self.set_restore_progress(20, self.restore_steps[1])
            logger.info("Step 3/7: Generating Docker Compose configuration...")
            
            # Generate Docker Compose YAML automatically
            self.set_restore_progress(20, "Generating Docker Compose configuration...")
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text="Creating docker-compose.yml with detected settings..."),
                "process label update in restore thread"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            
            try:
                # Generate docker-compose.yml based on detected configuration
                compose_config = {
                    'dbtype': dbtype,
                    'dbname': self.restore_db_name,
                    'dbuser': self.restore_db_user,
                    'dbpassword': self.restore_db_password,
                    'datadirectory': '/var/www/html/data',
                    'trusted_domains': ['localhost']
                }
                
                compose_content = generate_docker_compose_yml(
                    compose_config,
                    nextcloud_port=self.restore_container_port,
                    db_port=5432 if dbtype == 'pgsql' else 3306
                )
                
                # Save to app data directory with timestamp
                compose_dir = get_compose_directory()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                compose_filename = f"docker-compose-{timestamp}.yml"
                compose_file_path = compose_dir / compose_filename
                
                with open(compose_file_path, 'w') as f:
                    f.write(compose_content)
                
                # Store the compose file path for later reference (e.g., advanced options)
                self.last_generated_compose_file = str(compose_file_path)
                
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text=f"✓ Generated docker-compose.yml with {dbtype} configuration"),
                    "process label update in restore thread"
                )
                logger.info(f"Docker Compose file saved to: {compose_file_path}")
                print(f"Docker Compose file saved to internal storage: {compose_file_path}")
                print(f"Configuration: {dbtype} database on port {self.restore_container_port}")
                time.sleep(1)
            except Exception as yaml_err:
                # Not fatal - continue with manual container creation
                warning_msg = f"⚠️ Warning: Could not generate docker-compose.yml: {yaml_err}\nContinuing with manual container setup..."
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update in restore thread"
                )
                print(f"Warning: YAML generation failed: {yaml_err}")
                time.sleep(2)
            
            # Auto-create required host folders before starting containers
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text="Checking and creating required host folders..."),
                "process label update in restore thread"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            
            try:
                # Detect required folders from config.php and docker-compose.yml
                config_php_path = os.path.join(extract_dir, 'config', 'config.php')
                compose_files = ['docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml']
                compose_file_path = None
                for cf in compose_files:
                    if os.path.exists(cf):
                        compose_file_path = cf
                        break
                
                folders_dict = detect_required_host_folders(
                    config_php_path=config_php_path if os.path.exists(config_php_path) else None,
                    compose_file_path=compose_file_path,
                    extract_dir=extract_dir
                )
                
                # Create the folders
                success, created, existing, errors = create_required_host_folders(folders_dict)
                
                # Inform user about created folders
                if created or existing:
                    msg_parts = []
                    if created:
                        msg_parts.append(f"Created: {', '.join(created)}")
                    if existing:
                        msg_parts.append(f"Already exist: {', '.join(existing)}")
                    
                    folder_msg = "Host folders prepared: " + " | ".join(msg_parts)
                    safe_widget_update(
                        self.process_label,
                        lambda: self.process_label.config(text=folder_msg),
                        "process label update in restore thread"
                    )
                    print(f"✓ {folder_msg}")
                    time.sleep(1)  # Give user time to see the message
                
                # Show errors if any, but continue with warning
                if errors:
                    error_text = "\n".join(errors)
                    warning_msg = f"⚠️ Warning: Some folders could not be created:\n{error_text}\n\nContinuing with restore..."
                    safe_widget_update(
                        self.error_label,
                        lambda: self.error_label.config(text=warning_msg, fg="orange"),
                        "error label update in restore thread"
                    )
                    print(f"⚠️ {warning_msg}")
                    time.sleep(2)
                
            except Exception as folder_err:
                # Log error but continue - folder creation failure shouldn't stop the restore
                warning_msg = f"⚠️ Warning: Could not auto-create folders: {folder_err}\n\nContinuing with restore..."
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update in restore thread"
                )
                print(f"⚠️ {warning_msg}")
                time.sleep(2)
            
            # Update to step 2 with detailed messaging (25-30% range for container setup)
            self.set_restore_progress(20, self.restore_steps[2])
            logger.info("Step 4/7: Setting up Docker containers...")
            
            # For SQLite, we don't need a separate database container
            db_container = None
            if dbtype != 'sqlite':
                # Start database container first (needed for Nextcloud container linking)
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text=f"Starting {dbtype.upper()} database container..."),
                    "process label update in restore thread"
                )
                try:
                    if self.winfo_exists():
                        self.update_idletasks()
                except tk.TclError:
                    logger.debug("TclError during update_idletasks - window may have been closed")
                logger.info(f"Creating {dbtype.upper()} database container...")
                db_container = self.ensure_db_container(dbtype=dbtype)
                if not db_container:
                    logger.error("Failed to create database container!")
                    self.set_restore_progress(0, "Restore failed!")
                    return
                logger.info(f"Database container ready: {db_container}")
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text=f"✓ Database container ready: {db_container}"),
                    "process label update in restore thread"
                )
            else:
                logger.info("SQLite detected - no separate database container needed")
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text="✓ SQLite detected - no separate database container needed"),
                    "process label update in restore thread"
                )
                try:
                    if self.winfo_exists():
                        self.update_idletasks()
                except tk.TclError:
                    logger.debug("TclError during update_idletasks - window may have been closed")
            
            # Start Nextcloud container (linked to database if not SQLite)
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text=f"Starting Nextcloud container on port {self.restore_container_port}..."),
                "process label update in restore thread"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            logger.info(f"Creating Nextcloud container on port {self.restore_container_port}...")
            nextcloud_container = self.ensure_nextcloud_container(dbtype=dbtype)
            if not nextcloud_container:
                self.set_restore_progress(0, "Restore failed!")
                return
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text=f"✓ Nextcloud container ready: {nextcloud_container}"),
                "process label update in restore thread"
            )

            # Copying files to container (20-80% range for file copying)
            self.set_restore_progress(20, self.restore_steps[3])
            nextcloud_path = "/var/www/html"
            # Copy config/data/apps/custom_apps into container
            # Note: We need to remove existing folders first, then copy the backup folders
            folders_to_copy = ["config", "data", "apps", "custom_apps"]
            
            # Calculate total size and files for progress tracking
            folder_sizes = {}
            total_size = 0
            for folder in folders_to_copy:
                local_path = os.path.join(extract_dir, folder)
                if os.path.isdir(local_path):
                    folder_size = 0
                    try:
                        for dirpath, dirnames, filenames in os.walk(local_path):
                            for filename in filenames:
                                filepath = os.path.join(dirpath, filename)
                                try:
                                    folder_size += os.path.getsize(filepath)
                                except:
                                    pass
                    except Exception as e:
                        logger.debug(f"Could not calculate size for {folder}: {e}")
                    folder_sizes[folder] = folder_size
                    total_size += folder_size
            
            # Track total files for overall progress
            total_files_all_folders = 0
            folder_file_counts = {}
            
            # Count files in each folder
            for folder in folders_to_copy:
                local_path = os.path.join(extract_dir, folder)
                if os.path.isdir(local_path):
                    file_count = 0
                    for dirpath, dirnames, filenames in os.walk(local_path):
                        file_count += len(filenames)
                    folder_file_counts[folder] = file_count
                    total_files_all_folders += file_count
            
            logger.info(f"Total files to copy: {total_files_all_folders} across {len(folders_to_copy)} folders")
            
            # Copy each folder with live progress updates
            files_copied_so_far = 0
            copy_start_time_all = time.time()
            
            for idx, folder in enumerate(folders_to_copy):
                local_path = os.path.join(extract_dir, folder)
                if os.path.isdir(local_path):
                    # Calculate base progress for this folder (20-80% range, 60% total / 4 folders = 15% per folder)
                    folder_start_progress = 20 + int((idx / len(folders_to_copy)) * 60)
                    folder_end_progress = 20 + int(((idx + 1) / len(folders_to_copy)) * 60)
                    
                    folder_size = folder_sizes.get(folder, 0)
                    file_count = folder_file_counts.get(folder, 0)
                    
                    self.set_restore_progress(folder_start_progress, f"Copying {folder} folder ({file_count} files)...")
                    safe_widget_update(
                        self.process_label,
                        lambda f=folder, fc=file_count: self.process_label.config(text=f"Copying {f} folder ({fc} files)..."),
                        "process label update in restore thread"
                    )
                    try:
                        if self.winfo_exists():
                            self.update_idletasks()
                    except tk.TclError:
                        logger.debug("TclError during update_idletasks - window may have been closed")
                    
                    # Define progress callback for this folder
                    def copy_progress_callback(files_copied, total_files, current_file, percent, elapsed):
                        """
                        Callback function to update UI with copying progress.
                        Uses Tkinter's after() method for thread-safe UI updates.
                        """
                        try:
                            # Calculate overall progress
                            overall_files_copied = files_copied_so_far + files_copied
                            
                            # Format current file for display (shorten if needed)
                            file_display = current_file
                            if len(file_display) > 60:
                                file_display = "..." + file_display[-57:]
                            
                            # Calculate time estimates
                            elapsed_str = self._format_time(elapsed)
                            
                            if total_files > 0 and files_copied > 0:
                                rate = files_copied / elapsed if elapsed > 0 else 0
                                remaining_files = total_files - files_copied
                                est_remaining = remaining_files / rate if rate > 0 else 0
                                est_str = self._format_time(est_remaining)
                                
                                status_msg = f"Copying {folder}: {files_copied}/{total_files} files | Elapsed: {elapsed_str} | Est: {est_str}"
                            else:
                                status_msg = f"Copying {folder}: {files_copied} files | Elapsed: {elapsed_str}"
                            
                            # Use after() for thread-safe UI updates
                            def update_ui():
                                try:
                                    # Update progress bar and status
                                    self.set_restore_progress(percent, status_msg)
                                    
                                    # Update process label with current file
                                    if hasattr(self, "process_label") and self.process_label:
                                        self.process_label.config(text=f"Copying: {file_display}")
                                    
                                    # Force UI update
                                    if self.winfo_exists():
                                        self.update_idletasks()
                                except tk.TclError:
                                    pass
                                except Exception as ex:
                                    logger.debug(f"Error updating UI: {ex}")
                            
                            # Schedule UI update on main thread
                            try:
                                self.after(0, update_ui)
                            except tk.TclError:
                                pass
                        except Exception as ex:
                            logger.debug(f"Error in copy progress callback: {ex}")
                    
                    try:
                        # Copy folder with file-by-file progress
                        success = self.copy_folder_to_container_with_progress(
                            local_path=local_path,
                            container_name=nextcloud_container,
                            container_path=nextcloud_path,
                            folder_name=folder,
                            progress_start=folder_start_progress,
                            progress_end=folder_end_progress,
                            progress_callback=copy_progress_callback
                        )
                        
                        if not success:
                            raise Exception(f"Failed to copy {folder} folder")
                        
                        # Update counters
                        files_copied_so_far += file_count
                        
                        # Show completion for this folder
                        self.set_restore_progress(folder_end_progress, f"✓ Copied {folder} folder ({file_count} files)")
                        safe_widget_update(
                            self.process_label,
                            lambda f=folder, fc=file_count: self.process_label.config(text=f"✓ Copied {f} folder ({fc} files)"),
                            "process label update in restore thread"
                        )
                        logger.info(f"Successfully copied {folder} to container ({file_count} files, {self._format_bytes(folder_size)})")
                        
                    except Exception as copy_err:
                        tb = traceback.format_exc()
                        safe_widget_update(
                            self.error_label,
                            lambda f=folder, e=copy_err, t=tb: self.error_label.config(text=f"Error copying {f}: {e}\n{t}"),
                            "error label update in restore thread"
                        )
                        logger.error(f"Error copying {folder}: {copy_err}")
                        print(tb)
                        self.set_restore_progress(0, "Restore failed!")
                        return
            
            # Log overall copying stats
            total_elapsed = time.time() - copy_start_time_all
            logger.info(f"Completed copying {files_copied_so_far} files in {self._format_time(total_elapsed)}")

            # Database restore - branch based on detected database type (80-90% range)
            self.set_restore_progress(80, self.restore_steps[4])
            logger.info("Step 5/7: Restoring database...")
            
            db_restore_success = False
            
            if dbtype == 'sqlite':
                # SQLite: restore by copying .db file (already done with data folder)
                logger.info("Restoring SQLite database...")
                db_restore_success = self.restore_sqlite_database(extract_dir, nextcloud_container, nextcloud_path)
            elif dbtype == 'mysql':
                # MySQL/MariaDB: restore from SQL dump
                logger.info("Restoring MySQL/MariaDB database...")
                db_restore_success = self.restore_mysql_database(extract_dir, db_container)
            elif dbtype == 'pgsql':
                # PostgreSQL: restore from SQL dump
                logger.info("Restoring PostgreSQL database...")
                db_restore_success = self.restore_postgresql_database(extract_dir, db_container)
            else:
                # Unknown database type - show warning
                warning_msg = f"Warning: Unknown database type '{dbtype}'. Skipping database restore."
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update in restore thread"
                )
                logger.warning(f"Unknown database type: {dbtype}")
                print(warning_msg)
            
            if db_restore_success:
                logger.info("Database restore completed successfully")
            else:
                logger.warning("Database restore had issues")
            
            if not db_restore_success and dbtype != 'sqlite':
                # For non-SQLite databases, if restore failed, we might want to continue with warning
                # rather than failing the entire restore
                warning_msg = f"Warning: Database restore had issues. Please check manually."
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update in restore thread"
                )
                print(warning_msg)
            
            # Update config.php with database credentials (90-92% range)
            self.set_restore_progress(90, "Updating Nextcloud configuration ...")
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text="Updating config.php with database credentials ..."),
                "process label update in restore thread"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            try:
                self.update_config_php(nextcloud_container, db_container, dbtype)
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text="✓ Configuration updated successfully"),
                    "process label update in restore thread"
                )
                print("Config.php updated with correct database settings")
            except Exception as config_err:
                # Show warning but continue
                warning_msg = f"Warning: Could not update config.php: {config_err}. You may need to configure manually."
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update in restore thread"
                )
                print(f"Warning: config.php update failed: {config_err}")

            # Validate that required files exist (92-94% range)
            self.set_restore_progress(92, "Validating restored files ...")
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text="Validating config and data folders ..."),
                "process label update in restore thread"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            try:
                # Check if config.php exists
                check_config = subprocess.run(
                    f'docker exec {nextcloud_container} test -f {nextcloud_path}/config/config.php',
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                if check_config.returncode != 0:
                    error_msg = "Error: config.php not found after restore. The backup may be incomplete."
                    safe_widget_update(
                        self.error_label,
                        lambda: self.error_label.config(text=error_msg, fg="red"),
                        "error label update in restore thread"
                    )
                    self.set_restore_progress(0, "Restore failed!")
                    return
                
                # Check if data folder exists
                check_data = subprocess.run(
                    f'docker exec {nextcloud_container} test -d {nextcloud_path}/data',
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                if check_data.returncode != 0:
                    error_msg = "Error: data folder not found after restore. The backup may be incomplete."
                    safe_widget_update(
                        self.error_label,
                        lambda: self.error_label.config(text=error_msg, fg="red"),
                        "error label update in restore thread"
                    )
                    self.set_restore_progress(0, "Restore failed!")
                    return
                
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text="✓ All critical files validated"),
                    "process label update in restore thread"
                )
                print("File validation successful: config.php and data folder exist.")
            except Exception as val_err:
                warning_msg = f"Warning: Could not validate files: {val_err}"
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update in restore thread"
                )
                print(f"Warning: file validation error: {val_err}")
            
            # Setting permissions (94-96% range)
            self.set_restore_progress(94, self.restore_steps[5])
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text="Setting file permissions for web server..."),
                "process label update in restore thread"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            try:
                subprocess.run(
                    f'docker exec {nextcloud_container} chown -R www-data:www-data {nextcloud_path}/config {nextcloud_path}/data',
                    shell=True, check=True
                )
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text="✓ File permissions set correctly"),
                    "process label update in restore thread"
                )
                print("Permissions set successfully.")
            except subprocess.CalledProcessError as perm_err:
                # Display warning but allow restore to continue
                warning_msg = f"Warning: Could not set file permissions (chown failed). You may need to set permissions manually."
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update in restore thread"
                )
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text=f"Permission warning (continuing restore): {perm_err}"),
                    "process label update in restore thread"
                )
                print(f"Warning: chown failed but continuing restore: {perm_err}")
            except Exception as perm_err:
                # For other exceptions, show warning but also continue
                warning_msg = f"Warning: Error setting permissions: {perm_err}. You may need to set permissions manually."
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update in restore thread"
                )
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text=f"Permission warning (continuing restore): {perm_err}"),
                    "process label update in restore thread"
                )
                print(f"Warning: permission error but continuing restore: {perm_err}")

            # Restart Nextcloud container to apply all changes (96-99% range)
            self.set_restore_progress(96, "Restarting Nextcloud container ...")
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text="Restarting Nextcloud to apply changes..."),
                "process label update in restore thread"
            )
            try:
                if self.winfo_exists():
                    self.update_idletasks()
            except tk.TclError:
                logger.debug("TclError during update_idletasks - window may have been closed")
            try:
                subprocess.run(
                    f'docker restart {nextcloud_container}',
                    shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                safe_widget_update(
                    self.process_label,
                    lambda: self.process_label.config(text="✓ Nextcloud restarted successfully"),
                    "process label update in restore thread"
                )
                print(f"Nextcloud container restarted successfully.")
                time.sleep(3)  # Give container time to start
            except Exception as restart_err:
                warning_msg = f"Warning: Could not restart Nextcloud container: {restart_err}"
                safe_widget_update(
                    self.error_label,
                    lambda: self.error_label.config(text=warning_msg, fg="orange"),
                    "error label update in restore thread"
                )
                print(f"Warning: container restart failed: {restart_err}")

            self.set_restore_progress(100, self.restore_steps[6])
            safe_widget_update(
                self.process_label,
                lambda: self.process_label.config(text="✅ Restore completed successfully!"),
                "process label update in restore thread"
            )
            
            # Clear or show final status in error label
            try:
                if hasattr(self, "error_label") and self.error_label:
                    current_text = self.error_label.cget("text")
                    if current_text and "Warning" in current_text:
                        # Keep the warning message but add success note
                        pass  # Keep the warning visible
                    else:
                        safe_widget_update(
                            self.error_label,
                            lambda: self.error_label.config(text="", fg="red"),
                            "error label update in restore thread"
                        )
            except tk.TclError:
                logger.debug("TclError during final error label update - window may have been closed")
            
            # Show completion dialog with "Open Nextcloud" option
            self.show_restore_completion_dialog(nextcloud_container, self.restore_container_port)
            shutil.rmtree(extract_dir, ignore_errors=True)
        except tk.TclError as e:
            # Widget was destroyed - likely user closed window or navigated away
            logger.info("Restore thread terminated: Widget destroyed (user may have closed window or navigated away)")
            logger.debug(f"TclError details: {e}")
            # Don't show error dialog - this is expected behavior when user navigates away
        except Exception as e:
            tb = traceback.format_exc()
            # Log the error with full details
            logger.error("=" * 60)
            logger.error("RESTORE FAILED - Error Details:")
            logger.error(f"Error Type: {type(e).__name__}")
            logger.error(f"Error Message: {str(e)}")
            logger.error(f"Backup Path: {backup_path}")
            logger.error("Full Traceback:")
            logger.error(tb)
            logger.error("=" * 60)
            
            self.set_restore_progress(0, "Restore failed!")
            # Show actionable error message with recovery options
            self.show_restore_error_dialog(e, tb)
            print(tb)

    def show_restore_completion_dialog(self, container_name, port):
        """
        Show a completion dialog with an option to open Nextcloud in browser.
        This provides a beginner-friendly post-restore action.
        """
        # Create completion message frame
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        completion_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        completion_frame.pack(expand=True, fill="both", pady=40)
        
        # Success icon and message
        success_label = tk.Label(
            completion_frame,
            text="✅ Restore Complete!",
            font=("Arial", 24, "bold"),
            bg=self.theme_colors['bg'],
            fg="#45bf55"
        )
        success_label.pack(pady=20)
        
        info_label = tk.Label(
            completion_frame,
            text="Your Nextcloud instance has been successfully restored from backup.",
            font=("Arial", 14),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        info_label.pack(pady=10)
        
        # Container info
        container_info = tk.Label(
            completion_frame,
            text=f"Container: {container_name}\nPort: {port}",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        )
        container_info.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(completion_frame, bg=self.theme_colors['bg'])
        button_frame.pack(pady=30)
        
        # Open Nextcloud button
        open_btn = tk.Button(
            button_frame,
            text="🌐 Open Nextcloud in Browser",
            font=("Arial", 14, "bold"),
            bg="#3daee9",
            fg="white",
            width=30,
            height=2,
            command=lambda: self.open_nextcloud_in_browser(port)
        )
        open_btn.pack(pady=10)
        ToolTip(open_btn, f"Open http://localhost:{port} in your default web browser")
        
        # Return to menu button
        menu_btn = tk.Button(
            button_frame,
            text="Return to Main Menu",
            font=("Arial", 12),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=30,
            command=self.show_landing
        )
        menu_btn.pack(pady=10)
        
        # Apply theme
        self.apply_theme_recursive(completion_frame)
    
    def show_restore_error_dialog(self, error, traceback_str):
        """
        Show a user-friendly error dialog with actionable recovery options.
        """
        # Create error message frame
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        error_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        error_frame.pack(expand=True, fill="both", pady=40, padx=40)
        
        # Error icon and message
        error_label = tk.Label(
            error_frame,
            text="❌ Restore Failed",
            font=("Arial", 24, "bold"),
            bg=self.theme_colors['bg'],
            fg="#d32f2f"
        )
        error_label.pack(pady=20)
        
        # Error message
        error_msg = str(error)
        error_text = tk.Label(
            error_frame,
            text=f"Error: {error_msg}",
            font=("Arial", 12),
            bg=self.theme_colors['bg'],
            fg="#d32f2f",
            wraplength=600,
            justify="left"
        )
        error_text.pack(pady=10)
        
        # Actionable suggestions based on error type
        suggestions_frame = tk.Frame(error_frame, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
        suggestions_frame.pack(pady=20, fill="x", padx=20)
        
        suggestions_title = tk.Label(
            suggestions_frame,
            text="💡 Suggested Actions",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        )
        suggestions_title.pack(pady=(10, 5))
        
        # Determine specific suggestions based on error
        suggestions = self.get_error_suggestions(error_msg)
        
        for suggestion in suggestions:
            suggestion_label = tk.Label(
                suggestions_frame,
                text=f"• {suggestion}",
                font=("Arial", 10),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['info_fg'],
                wraplength=550,
                justify="left",
                anchor="w"
            )
            suggestion_label.pack(pady=2, padx=20, anchor="w")
        
        # Log file location info
        log_info_frame = tk.Frame(error_frame, bg=self.theme_colors['bg'])
        log_info_frame.pack(pady=15, fill="x", padx=20)
        
        log_info_label = tk.Label(
            log_info_frame,
            text=f"📁 Error details saved to:\n{LOG_FILE_PATH}",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="center"
        )
        log_info_label.pack()
        
        # Button frame
        button_frame = tk.Frame(error_frame, bg=self.theme_colors['bg'])
        button_frame.pack(pady=20)
        
        # Show logs button - opens full log viewer
        logs_btn = tk.Button(
            button_frame,
            text="📋 Show Logs",
            font=("Arial", 12, "bold"),
            bg="#3daee9",
            fg="white",
            width=20,
            command=self.show_log_viewer
        )
        logs_btn.pack(side="left", padx=10)
        ToolTip(logs_btn, "View detailed error logs and troubleshooting information")
        
        # Try again button
        retry_btn = tk.Button(
            button_frame,
            text="🔄 Try Again",
            font=("Arial", 12),
            bg="#f7b32b",
            fg="white",
            width=20,
            command=self.start_restore
        )
        retry_btn.pack(side="left", padx=10)
        
        # Return to menu button
        menu_btn = tk.Button(
            button_frame,
            text="Return to Main Menu",
            font=("Arial", 12),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=20,
            command=self.show_landing
        )
        menu_btn.pack(side="left", padx=10)
        
        # Apply theme
        self.apply_theme_recursive(error_frame)
    
    def get_error_suggestions(self, error_msg):
        """
        Provide actionable suggestions based on the error message.
        """
        suggestions = []
        
        error_lower = error_msg.lower()
        
        if "docker" in error_lower and ("not running" in error_lower or "cannot connect" in error_lower):
            suggestions.append("Ensure Docker is installed and running on your system")
            suggestions.append("Try starting Docker Desktop manually")
            suggestions.append("Check Docker service status: 'docker ps' in terminal")
        elif "password" in error_lower or "decrypt" in error_lower:
            suggestions.append("Verify you entered the correct decryption password")
            suggestions.append("Check if the backup file is corrupted")
            suggestions.append("Ensure GPG is installed for encrypted backups")
        elif "database" in error_lower:
            suggestions.append("Verify database credentials match your original setup")
            suggestions.append("Check if the database container is running")
            suggestions.append("Ensure database dump file exists in backup")
        elif "permission" in error_lower:
            suggestions.append("Run the application with appropriate permissions")
            suggestions.append("Check file and folder permissions on your system")
            suggestions.append("Ensure Docker has access to required directories")
        elif "container" in error_lower:
            suggestions.append("Check if another container is using the same name")
            suggestions.append("Try removing existing containers: 'docker rm -f <container_name>'")
            suggestions.append("Verify Docker has sufficient resources (CPU, memory)")
        elif "port" in error_lower:
            suggestions.append("Ensure the port is not already in use by another service")
            suggestions.append("Try using a different port number")
            suggestions.append("Check firewall settings")
        else:
            suggestions.append("Check the log file for detailed error information")
            suggestions.append("Verify all backup files are present and not corrupted")
            suggestions.append("Ensure you have sufficient disk space")
            suggestions.append("Try restarting Docker and running the restore again")
        
        return suggestions
    
    def show_error_details(self, traceback_str):
        """
        Show detailed error logs in a popup window.
        """
        details_window = tk.Toplevel(self)
        details_window.title("Error Details")
        details_window.geometry("800x600")
        details_window.configure(bg=self.theme_colors['bg'])
        
        # Title
        title_label = tk.Label(
            details_window,
            text="Detailed Error Log",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        title_label.pack(pady=10)
        
        # Text widget with scrollbar for logs
        frame = tk.Frame(details_window, bg=self.theme_colors['bg'])
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(
            frame,
            wrap="word",
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg'],
            font=("Courier", 9),
            yscrollcommand=scrollbar.set
        )
        text_widget.pack(expand=True, fill="both")
        scrollbar.config(command=text_widget.yview)
        
        text_widget.insert("1.0", traceback_str)
        text_widget.config(state="disabled")
        
        # Close button
        close_btn = tk.Button(
            details_window,
            text="Close",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=details_window.destroy
        )
        close_btn.pack(pady=10)
    
    def show_docker_container_error_dialog(self, error_info, stderr_output, container_name, port):
        """
        Show error dialog when Docker container creation fails.
        Includes "Show Docker Error Details" button.
        """
        # Create a modal dialog
        error_dialog = tk.Toplevel(self)
        error_dialog.title("Docker Container Creation Failed")
        error_dialog.geometry("700x500")
        error_dialog.configure(bg=self.theme_colors['bg'])
        error_dialog.transient(self)
        error_dialog.grab_set()
        
        # Center the dialog
        error_dialog.update_idletasks()
        x = (error_dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (error_dialog.winfo_screenheight() // 2) - (500 // 2)
        error_dialog.geometry(f"+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(error_dialog, bg='#d32f2f', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="❌ Docker Container Failed",
            font=("Arial", 18, "bold"),
            bg='#d32f2f',
            fg='white'
        ).pack(pady=25)
        
        # Content frame
        content_frame = tk.Frame(error_dialog, bg=self.theme_colors['bg'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Error type label
        tk.Label(
            content_frame,
            text=f"Error Type: {error_info['error_type'].replace('_', ' ').title()}",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(0, 10))
        
        # Container info
        info_frame = tk.Frame(content_frame, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(
            info_frame,
            text=f"Container: {container_name}  |  Port: {port}",
            font=("Arial", 10),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=8)
        
        # Error message
        tk.Label(
            content_frame,
            text=error_info['user_message'],
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg='#d32f2f',
            wraplength=640,
            justify="left"
        ).pack(pady=10)
        
        # Suggested action frame
        action_frame = tk.Frame(content_frame, bg='#e8f5e9', relief="solid", borderwidth=1)
        action_frame.pack(fill='x', pady=15)
        
        tk.Label(
            action_frame,
            text="💡 Suggested Action:",
            font=("Arial", 11, "bold"),
            bg='#e8f5e9',
            fg='#2e7d32'
        ).pack(pady=(8, 3), padx=10, anchor='w')
        
        tk.Label(
            action_frame,
            text=error_info['suggested_action'],
            font=("Arial", 9),
            bg='#e8f5e9',
            fg='#1b5e20',
            wraplength=620,
            justify="left"
        ).pack(pady=(0, 8), padx=15, anchor='w')
        
        # Alternative port suggestion (if applicable)
        if error_info.get('alternative_port'):
            port_label = tk.Label(
                content_frame,
                text=f"🔌 Try alternative port: {error_info['alternative_port']}",
                font=("Arial", 10, "bold"),
                bg=self.theme_colors['bg'],
                fg='#f7b32b'
            )
            port_label.pack(pady=5)
        
        # Log location
        tk.Label(
            content_frame,
            text=f"📁 Error logged to: {DOCKER_ERROR_LOG_PATH}",
            font=("Arial", 8),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(15, 5))
        
        # Button frame
        button_frame = tk.Frame(content_frame, bg=self.theme_colors['bg'])
        button_frame.pack(pady=15)
        
        # Show Docker Error Details button
        details_btn = tk.Button(
            button_frame,
            text="📋 Show Docker Error Details",
            font=("Arial", 11, "bold"),
            bg="#3daee9",
            fg="white",
            width=25,
            command=lambda: self.show_docker_error_details(error_info, stderr_output)
        )
        details_btn.pack(side="left", padx=5)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=15,
            command=error_dialog.destroy
        )
        close_btn.pack(side="left", padx=5)
    
    def show_docker_error_details(self, error_info, stderr_output):
        """
        Show detailed Docker error information in a popup window with actionable guidance.
        
        Args:
            error_info: Dictionary with error analysis from analyze_docker_error()
            stderr_output: Raw stderr output from Docker command
        """
        details_window = tk.Toplevel(self)
        details_window.title("Docker Error Details")
        details_window.geometry("900x700")
        details_window.configure(bg=self.theme_colors['bg'])
        
        # Title with error type
        title_frame = tk.Frame(details_window, bg=self.theme_colors['header_bg'])
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text=f"🐳 Docker Error: {error_info['error_type'].replace('_', ' ').title()}",
            font=("Arial", 16, "bold"),
            bg=self.theme_colors['header_bg'],
            fg=self.theme_colors['header_fg']
        )
        title_label.pack(pady=15)
        
        # Main content with scrollbar
        main_frame = tk.Frame(details_window, bg=self.theme_colors['bg'])
        main_frame.pack(expand=True, fill="both", padx=15, pady=5)
        
        canvas = tk.Canvas(main_frame, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # User-friendly error message
        error_msg_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=2)
        error_msg_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            error_msg_frame,
            text="❌ Error Description",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        tk.Label(
            error_msg_frame,
            text=error_info['user_message'],
            font=("Arial", 11),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg'],
            wraplength=820,
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor="w")
        
        # Suggested action
        action_frame = tk.Frame(scrollable_frame, bg='#e8f5e9', relief="solid", borderwidth=2)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            action_frame,
            text="💡 Suggested Action",
            font=("Arial", 12, "bold"),
            bg='#e8f5e9',
            fg='#2e7d32'
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        tk.Label(
            action_frame,
            text=error_info['suggested_action'],
            font=("Arial", 10),
            bg='#e8f5e9',
            fg='#1b5e20',
            wraplength=820,
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor="w")
        
        # Alternative port suggestion (if applicable)
        if error_info.get('alternative_port'):
            port_frame = tk.Frame(scrollable_frame, bg='#fff3cd', relief="solid", borderwidth=2)
            port_frame.pack(fill="x", padx=10, pady=10)
            
            tk.Label(
                port_frame,
                text="🔌 Alternative Port Suggestion",
                font=("Arial", 12, "bold"),
                bg='#fff3cd',
                fg='#856404'
            ).pack(pady=(10, 5), padx=10, anchor="w")
            
            tk.Label(
                port_frame,
                text=f"Try using port {error_info['alternative_port']} instead.",
                font=("Arial", 10),
                bg='#fff3cd',
                fg='#856404',
                wraplength=820,
                justify="left"
            ).pack(pady=(0, 10), padx=15, anchor="w")
        
        # Raw Docker error output
        raw_error_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['bg'])
        raw_error_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(
            raw_error_frame,
            text="📋 Raw Docker Error Output",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(5, 5), anchor="w")
        
        text_frame = tk.Frame(raw_error_frame)
        text_frame.pack(fill="both", expand=True)
        
        text_scrollbar = tk.Scrollbar(text_frame)
        text_scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(
            text_frame,
            wrap="word",
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg'],
            font=("Courier", 9),
            height=8,
            yscrollcommand=text_scrollbar.set
        )
        text_widget.pack(fill="both", expand=True)
        text_scrollbar.config(command=text_widget.yview)
        
        text_widget.insert("1.0", stderr_output)
        text_widget.config(state="disabled")
        
        # Docker error log file location
        log_location_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['bg'])
        log_location_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            log_location_frame,
            text=f"📁 Docker errors are logged to:\n{DOCKER_ERROR_LOG_PATH}",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            justify="left"
        ).pack(anchor="w")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button frame at bottom
        button_frame = tk.Frame(details_window, bg=self.theme_colors['bg'])
        button_frame.pack(fill="x", padx=15, pady=15)
        
        # Open Docker error log button
        open_log_btn = tk.Button(
            button_frame,
            text="📂 Open Docker Error Log",
            font=("Arial", 10),
            bg="#3daee9",
            fg="white",
            command=lambda: self.open_file_location(DOCKER_ERROR_LOG_PATH)
        )
        open_log_btn.pack(side="left", padx=5)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 10),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=details_window.destroy
        )
        close_btn.pack(side="right", padx=5)
    
    def show_docker_error_page(self, error_info, stderr_output, container_name, port):
        """
        Show Docker error as a dedicated page within the main GUI (not a popup dialog).
        Displays error details, suggested actions, and a 'Return to Main Menu' button.
        
        Args:
            error_info: Dictionary with error analysis from analyze_docker_error()
            stderr_output: Raw stderr output from Docker command
            container_name: Name of the container that failed
            port: Port that was being used (or None)
        """
        # Store error information for potential detailed view
        self.current_docker_error = {
            'error_info': error_info,
            'stderr': stderr_output,
            'container_name': container_name,
            'port': port
        }
        
        # Clear the body frame and show error page
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        # Update current page tracking
        self.current_page = 'docker_error'
        
        # Main error container with scrolling
        main_container = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        main_container.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(main_container, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, command=canvas.yview)
        error_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        # Function to center content in canvas
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Center the window horizontally
            canvas_width = canvas.winfo_width()
            frame_width = error_frame.winfo_reqwidth()
            x_position = max(0, (canvas_width - frame_width) // 2)
            canvas.coords(canvas_window, x_position, 0)
        
        error_frame.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", update_scroll_region)
        
        canvas_window = canvas.create_window((0, 0), window=error_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header with error icon
        header_frame = tk.Frame(error_frame, bg='#d32f2f', height=100)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="❌ Docker Container Failed",
            font=("Arial", 22, "bold"),
            bg='#d32f2f',
            fg='white'
        ).pack(pady=30)
        
        # Content container with padding
        content_container = tk.Frame(error_frame, bg=self.theme_colors['bg'])
        content_container.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Error type label
        tk.Label(
            content_container,
            text=f"Error Type: {error_info['error_type'].replace('_', ' ').title()}",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(0, 15), anchor='w')
        
        # Container info frame
        info_frame = tk.Frame(content_container, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=2)
        info_frame.pack(fill='x', pady=10)
        
        port_text = port if port else "N/A"
        tk.Label(
            info_frame,
            text=f"Container: {container_name}  |  Port: {port_text}",
            font=("Arial", 11),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=10)
        
        # Error message frame
        error_msg_frame = tk.Frame(content_container, bg='#ffebee', relief="solid", borderwidth=2)
        error_msg_frame.pack(fill='x', pady=15)
        
        tk.Label(
            error_msg_frame,
            text="❌ Error Description",
            font=("Arial", 12, "bold"),
            bg='#ffebee',
            fg='#c62828'
        ).pack(pady=(10, 5), padx=15, anchor='w')
        
        tk.Label(
            error_msg_frame,
            text=error_info['user_message'],
            font=("Arial", 11),
            bg='#ffebee',
            fg='#b71c1c',
            wraplength=780,
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor='w')
        
        # Suggested action frame
        action_frame = tk.Frame(content_container, bg='#e8f5e9', relief="solid", borderwidth=2)
        action_frame.pack(fill='x', pady=15)
        
        tk.Label(
            action_frame,
            text="💡 Suggested Action",
            font=("Arial", 12, "bold"),
            bg='#e8f5e9',
            fg='#2e7d32'
        ).pack(pady=(10, 5), padx=15, anchor='w')
        
        tk.Label(
            action_frame,
            text=error_info['suggested_action'],
            font=("Arial", 10),
            bg='#e8f5e9',
            fg='#1b5e20',
            wraplength=780,
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor='w')
        
        # Alternative port suggestion (if applicable)
        if error_info.get('alternative_port'):
            port_frame = tk.Frame(content_container, bg='#fff3cd', relief="solid", borderwidth=2)
            port_frame.pack(fill='x', pady=15)
            
            tk.Label(
                port_frame,
                text="🔌 Alternative Port Suggestion",
                font=("Arial", 12, "bold"),
                bg='#fff3cd',
                fg='#856404'
            ).pack(pady=(10, 5), padx=15, anchor='w')
            
            tk.Label(
                port_frame,
                text=f"Try using port {error_info['alternative_port']} instead.",
                font=("Arial", 10),
                bg='#fff3cd',
                fg='#856404',
                wraplength=780,
                justify="left"
            ).pack(pady=(0, 10), padx=15, anchor='w')
        
        # Docker error details section (expandable)
        details_section = tk.Frame(content_container, bg=self.theme_colors['bg'])
        details_section.pack(fill='both', expand=True, pady=15)
        
        tk.Label(
            details_section,
            text="📋 Docker Error Output",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(5, 5), anchor='w')
        
        # Text widget for Docker error output
        text_frame = tk.Frame(details_section)
        text_frame.pack(fill='both', expand=True, pady=5)
        
        text_scrollbar = tk.Scrollbar(text_frame)
        text_scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(
            text_frame,
            wrap="word",
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg'],
            font=("Courier", 9),
            height=10,
            yscrollcommand=text_scrollbar.set
        )
        text_widget.pack(fill="both", expand=True)
        text_scrollbar.config(command=text_widget.yview)
        
        text_widget.insert("1.0", stderr_output)
        text_widget.config(state="disabled")
        
        # Log file location
        tk.Label(
            content_container,
            text=f"📁 Error logged to: {DOCKER_ERROR_LOG_PATH}",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(15, 5), anchor='w')
        
        # Button frame
        button_frame = tk.Frame(content_container, bg=self.theme_colors['bg'])
        button_frame.pack(pady=20)
        
        # Open Docker Error Log button
        open_log_btn = tk.Button(
            button_frame,
            text="📂 Open Error Log Folder",
            font=("Arial", 12),
            bg="#3daee9",
            fg="white",
            width=22,
            command=lambda: self.open_file_location(DOCKER_ERROR_LOG_PATH)
        )
        open_log_btn.pack(side="left", padx=5)
        
        # Return to Main Menu button
        menu_btn = tk.Button(
            button_frame,
            text="Return to Main Menu",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=22,
            command=self.show_landing
        )
        menu_btn.pack(side="left", padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Apply theme
        self.apply_theme_recursive(error_frame)
    
    def open_file_location(self, file_path):
        """Open the file location in the system file explorer."""
        try:
            if platform.system() == 'Windows':
                os.startfile(os.path.dirname(file_path))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', os.path.dirname(file_path)])
            else:  # Linux
                subprocess.run(['xdg-open', os.path.dirname(file_path)])
        except Exception as e:
            messagebox.showinfo(
                "File Location",
                f"Log file location:\n{file_path}",
                parent=self
            )
    
    def open_nextcloud_in_browser(self, port):
        """
        Open Nextcloud instance in the default web browser.
        """
        url = f"http://localhost:{port}"
        try:
            webbrowser.open(url)
            messagebox.showinfo(
                "Opening Nextcloud",
                f"Opening Nextcloud at {url} in your browser.",
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                "Error Opening Browser",
                f"Could not open browser automatically.\n\n"
                f"Please manually navigate to: {url}",
                parent=self
            )

    # --- New instance logic ---
    def start_new_instance_workflow(self):
        # Check if Docker is installed first
        if not is_tool_installed('docker'):
            for widget in self.body_frame.winfo_children():
                widget.destroy()
            self.status_label.config(text="Start New Nextcloud Instance")
            def proceed_to_port():
                # Check if Docker is running before proceeding
                if not self.check_docker_running():
                    self.show_landing()
                    return
                self.show_port_entry()
            prompt_install_docker_link(self, self.status_label, proceed_to_port)
            return
        
        # Check if Docker is running before proceeding
        if not self.check_docker_running():
            self.show_landing()
            return
        
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        self.status_label.config(text="Start New Nextcloud Instance")
        self.show_port_entry()

    def show_port_entry(self):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        entry_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        entry_frame.pack(pady=30)
        btn_back = tk.Button(entry_frame, text="Return to Main Menu", font=("Arial", 12), 
                            bg=self.theme_colors['button_bg'], fg=self.theme_colors['button_fg'],
                            command=self.show_landing)
        btn_back.pack(pady=8)
        tk.Label(entry_frame, text="Select a port to access Nextcloud in your browser.", font=("Arial", 14),
                bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=8)
        tk.Label(entry_frame, text="The port determines the address you use to reach Nextcloud.\nFor example, if you choose port 8080, you'll go to http://localhost:8080", 
                font=("Arial", 11), bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg']).pack(pady=(0,10))
        ports = ["8080", "8888", "3000", "5000", "9000", "80", "Custom"]
        port_var = tk.StringVar(value=ports[0])
        port_combo = ttk.Combobox(entry_frame, textvariable=port_var, values=ports, font=("Arial", 13), state="readonly", width=10)
        port_combo.pack(pady=3)
        custom_port_entry = tk.Entry(entry_frame, font=("Arial", 13), width=10,
                                     bg=self.theme_colors['entry_bg'], fg=self.theme_colors['entry_fg'],
                                     insertbackground=self.theme_colors['entry_fg'])
        custom_port_entry.pack_forget()

        def on_combo_change(event):
            if port_var.get() == "Custom":
                custom_port_entry.pack(pady=3)
                custom_port_entry.delete(0, tk.END)
                custom_port_entry.focus_set()
            else:
                custom_port_entry.pack_forget()

        port_combo.bind("<<ComboboxSelected>>", on_combo_change)
        
        # Add admin credentials section
        tk.Label(entry_frame, text="", font=("Arial", 6), bg=self.theme_colors['bg']).pack()  # Spacer
        tk.Label(entry_frame, text="Admin Credentials", font=("Arial", 14, "bold"),
                bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=(10, 8))
        tk.Label(entry_frame, text="These credentials will be used to log into Nextcloud.", 
                font=("Arial", 11), bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg']).pack(pady=(0, 10))
        
        # Admin username
        tk.Label(entry_frame, text="Admin Username:", font=("Arial", 11),
                bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=(5, 2))
        admin_user_entry = tk.Entry(entry_frame, font=("Arial", 13), width=25,
                                     bg=self.theme_colors['entry_bg'], fg=self.theme_colors['entry_fg'],
                                     insertbackground=self.theme_colors['entry_fg'])
        admin_user_entry.insert(0, "admin")
        admin_user_entry.pack(pady=3)
        
        # Admin password
        tk.Label(entry_frame, text="Admin Password:", font=("Arial", 11),
                bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=(5, 2))
        admin_password_entry = tk.Entry(entry_frame, show="*", font=("Arial", 13), width=25,
                                         bg=self.theme_colors['entry_bg'], fg=self.theme_colors['entry_fg'],
                                         insertbackground=self.theme_colors['entry_fg'])
        admin_password_entry.insert(0, "admin")
        admin_password_entry.pack(pady=3)

        start_btn = tk.Button(entry_frame, text="Start Nextcloud Instance", font=("Arial", 13, "bold"), bg="#f7b32b", fg="white", width=24)
        start_btn.pack(pady=18)

        def on_start():
            selected = port_var.get()
            port = selected
            if selected == "Custom":
                port = custom_port_entry.get().strip()
            if not port.isdigit() or not (1 <= int(port) <= 65535):
                messagebox.showerror("Invalid Port", "Please enter a valid port number (1-65535).")
                return
            
            admin_user = admin_user_entry.get().strip()
            admin_password = admin_password_entry.get()
            
            if not admin_user:
                messagebox.showerror("Invalid Input", "Please enter an admin username.")
                return
            if not admin_password:
                messagebox.showerror("Invalid Input", "Please enter an admin password.")
                return
            
            start_btn.config(state="disabled")
            threading.Thread(target=self.launch_nextcloud_instance, args=(int(port), admin_user, admin_password), daemon=True).start()
        start_btn.config(command=on_start)
        
        # Apply theme recursively to all widgets in the panel
        self.apply_theme_recursive(entry_frame)

    def launch_nextcloud_instance(self, port, admin_user="admin", admin_password="admin"):
        try:
            # Clear body and show progress UI
            for widget in self.body_frame.winfo_children():
                widget.destroy()
            
            progress_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
            progress_frame.pack(pady=30, expand=True)
            
            # Status label with spinner
            status_label = tk.Label(progress_frame, text="", font=("Arial", 13), 
                                   bg=self.theme_colors['bg'], fg=self.theme_colors['fg'])
            status_label.pack(pady=10)
            
            # Detailed message label
            detail_label = tk.Label(progress_frame, text="", font=("Arial", 11), 
                                   bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg'])
            detail_label.pack(pady=5)
            
            # Track if we should continue (for cancellation)
            should_continue = [True]
            
            def update_status(spinner_char, main_text, detail_text=""):
                """Update status with spinner"""
                if should_continue[0]:
                    status_label.config(text=f"{spinner_char} {main_text}")
                    detail_label.config(text=detail_text)
                    self.status_label.config(text=main_text)
                    self.update_idletasks()
            
            # Spinner animation characters
            spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            spinner_idx = [0]
            
            def spin():
                """Get next spinner character"""
                char = spinner_chars[spinner_idx[0]]
                spinner_idx[0] = (spinner_idx[0] + 1) % len(spinner_chars)
                return char
            
            # Phase 1: Check if image exists locally
            update_status(spin(), "Checking for Nextcloud image...", "This will only take a moment")
            
            check_image = subprocess.run(
                f'docker images -q {NEXTCLOUD_IMAGE}',
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            image_exists = bool(check_image.stdout.strip())
            
            if not image_exists:
                # Phase 2: Pull image (this can take a while)
                update_status(spin(), "Pulling Nextcloud image from Docker Hub...", 
                             "First-time setup: This may take 2-5 minutes depending on your internet speed")
                
                # Start pull in background and animate spinner
                pull_process = subprocess.Popen(
                    f'docker pull {NEXTCLOUD_IMAGE}',
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                
                # Animate spinner while pulling
                while pull_process.poll() is None:
                    update_status(spin(), "Pulling Nextcloud image from Docker Hub...",
                                 "This may take a few minutes on first run...")
                    time.sleep(0.15)
                
                if pull_process.returncode != 0:
                    error_msg = pull_process.stderr.read() if pull_process.stderr else "Unknown error"
                    raise Exception(f"Failed to pull Nextcloud image: {error_msg}")
                
                update_status("✓", "Nextcloud image downloaded successfully", "")
                time.sleep(0.5)
            else:
                update_status("✓", "Nextcloud image found", "Using cached image")
                time.sleep(0.3)
            
            # Phase 3: Create container
            update_status(spin(), "Creating Nextcloud container...", 
                         f"Starting container on port {port}")
            
            # Use shlex.quote to safely escape credentials and prevent command injection
            safe_admin_user = shlex.quote(admin_user)
            safe_admin_password = shlex.quote(admin_password)
            
            result = subprocess.run(
                f'docker run -d --name {NEXTCLOUD_CONTAINER_NAME} -e NEXTCLOUD_ADMIN_USER={safe_admin_user} -e NEXTCLOUD_ADMIN_PASSWORD={safe_admin_password} --network bridge -p {port}:80 {NEXTCLOUD_IMAGE}',
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if result.returncode != 0:
                tb = traceback.format_exc()
                error_msg = (
                    f"Failed to start Nextcloud container.\n\n"
                    f"Error: {result.stderr}\n\n"
                    "Common issues:\n"
                    "- Container name already in use\n"
                    "- Port already in use\n"
                    "- Not attached to default bridge network\n\n"
                    "Please check Docker status and try again."
                )
                messagebox.showerror("Docker Error", error_msg)
                print(f"Container start failed: {result.stderr}\n{tb}")
                self.show_landing()
                return
            
            container_id = NEXTCLOUD_CONTAINER_NAME
            url = f"http://localhost:{port}"
            
            update_status("✓", "Container created successfully", f"Container ID: {container_id}")
            time.sleep(0.5)
            
            # Phase 4: Wait for Nextcloud to be ready
            update_status(spin(), "Waiting for Nextcloud to start...", 
                         "The service is initializing. This may take 1-2 minutes.")
            
            # Check readiness in background thread
            ready = [False]
            check_thread = threading.Thread(
                target=lambda: ready.__setitem__(0, check_nextcloud_ready(port, timeout=120)),
                daemon=True
            )
            check_thread.start()
            
            # Animate spinner while checking
            while check_thread.is_alive():
                update_status(spin(), "Waiting for Nextcloud to start...",
                             "Nextcloud is initializing. Please wait...")
                time.sleep(0.15)
            
            # Show final UI
            for widget in self.body_frame.winfo_children():
                widget.destroy()
            
            info_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
            info_frame.pack(pady=30)
            
            if ready[0]:
                tk.Label(info_frame, text="✓ Nextcloud is ready!", font=("Arial", 16, "bold"), 
                        bg=self.theme_colors['bg'], fg=self.theme_colors['warning_fg']).pack(pady=8)
                tk.Label(info_frame, text="Access it at:", font=("Arial", 14),
                        bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=(10, 5))
                
                def open_localhost(event=None, link=url):
                    webbrowser.open(link)
                
                link_label = tk.Label(
                    info_frame,
                    text=url,
                    font=("Arial", 16, "bold"),
                    bg=self.theme_colors['bg'],
                    fg="#3daee9",
                    cursor="hand2"
                )
                link_label.pack(pady=8)
                link_label.bind("<Button-1>", lambda e: open_localhost(link=url))
                
                tk.Label(info_frame, text=f"Container ID: {container_id}", font=("Arial", 11), 
                        bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg']).pack(pady=5)
                self.status_label.config(text=f"Nextcloud is ready at {url}")
            else:
                # Nextcloud started but not ready yet
                tk.Label(info_frame, text="⚠ Nextcloud container is starting", font=("Arial", 16, "bold"), 
                        bg=self.theme_colors['bg'], fg=self.theme_colors['warning_fg']).pack(pady=8)
                tk.Label(info_frame, text="The service is still initializing.\nThe link will become available when ready.", 
                        font=("Arial", 12), bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg']).pack(pady=10)
                tk.Label(info_frame, text="Access it at:", font=("Arial", 14),
                        bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=(10, 5))
                
                # Disabled link initially
                link_label = tk.Label(
                    info_frame,
                    text=url,
                    font=("Arial", 16, "bold"),
                    bg=self.theme_colors['bg'],
                    fg=self.theme_colors['hint_fg']  # Use hint color for disabled state
                )
                link_label.pack(pady=8)
                
                tk.Label(info_frame, text=f"Container ID: {container_id}", font=("Arial", 11), 
                        bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg']).pack(pady=5)
                tk.Label(info_frame, text="⏳ Waiting for Nextcloud to become ready...", 
                        font=("Arial", 11), bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=10)
                
                self.status_label.config(text="Nextcloud container started, initializing...")
                
                # Continue checking in background and enable link when ready
                def check_and_enable():
                    if check_nextcloud_ready(port, timeout=180):
                        # Update UI to show link is ready
                        link_label.config(fg="#3daee9", cursor="hand2")
                        link_label.bind("<Button-1>", lambda e: webbrowser.open(url))
                        
                        # Find and update the waiting message
                        for child in info_frame.winfo_children():
                            if isinstance(child, tk.Label) and "Waiting for Nextcloud" in child.cget("text"):
                                child.config(text="✓ Nextcloud is now ready! Click the link above.", 
                                           fg=self.theme_colors['warning_fg'])
                        
                        self.status_label.config(text=f"Nextcloud is ready at {url}")
                
                threading.Thread(target=check_and_enable, daemon=True).start()
            
            tk.Button(info_frame, text="Return to Main Menu", font=("Arial", 13), 
                     bg=self.theme_colors['button_bg'], fg=self.theme_colors['button_fg'],
                     command=self.show_landing).pack(pady=18)
            
            # Apply theme recursively to all widgets in the panel
            self.apply_theme_recursive(info_frame)
            
        except Exception as e:
            tb = traceback.format_exc()
            messagebox.showerror("Error", f"Failed to start Nextcloud: {e}\n{tb}")
            print(tb)
            self.show_landing()

    # ----- Scheduled Backup Methods -----
    
    def _update_schedule_status_label(self, parent):
        """Update the schedule status label on the landing page."""
        config = load_schedule_config()
        if config and config.get('enabled'):
            task_name = config.get('task_name', 'NextcloudBackup')
            status = get_scheduled_task_status(task_name)
            
            if status and status.get('exists'):
                status_text = f"📅 Scheduled: {config.get('frequency', 'Unknown')} at {config.get('time', 'Unknown')}"
                status_label = tk.Label(
                    parent, 
                    text=status_text, 
                    font=("Arial", 11),
                    bg=self.theme_colors['bg'],
                    fg=self.theme_colors['warning_fg']
                )
                status_label.pack(pady=(0, 10))
    
    def show_schedule_backup(self):
        """Show the schedule backup configuration UI."""
        self.current_page = 'schedule_backup'
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        self.status_label.config(text="Schedule Backup Configuration")
        
        # Create main frame
        frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        frame.pack(pady=20, fill="both", expand=True)
        
        # Back button
        tk.Button(
            frame, 
            text="Return to Main Menu", 
            font=("Arial", 12),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_landing
        ).pack(pady=8)
        
        # Title
        tk.Label(
            frame, 
            text="Schedule Automatic Backups", 
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=15)
        
        # Create scrollable canvas for all content
        canvas = tk.Canvas(frame, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_scroll(event=None):
            """Update scroll region when content changes"""
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make scrollable_frame width match canvas width
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        # Add mouse wheel scrolling support
        def on_mouse_wheel(event):
            """Handle mouse wheel scrolling"""
            # Windows and macOS use event.delta
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            # Linux uses event.num (Button-4 = scroll up, Button-5 = scroll down)
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
        
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows/Mac
        canvas.bind_all("<Button-4>", on_mouse_wheel)    # Linux scroll up
        canvas.bind_all("<Button-5>", on_mouse_wheel)    # Linux scroll down
        
        # Load existing config
        config = load_schedule_config()
        
        # Show current status
        task_name = config.get('task_name', 'NextcloudBackup') if config else 'NextcloudBackup'
        status = get_scheduled_task_status(task_name)
        
        status_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['info_bg'], relief="ridge", borderwidth=2)
        status_frame.pack(pady=10, fill="x", padx=40)
        
        tk.Label(
            status_frame, 
            text="Current Status", 
            font=("Arial", 14, "bold"), 
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=5)
        
        if status and status.get('exists'):
            status_text = f"✓ Scheduled backup is active\n"
            if config:
                status_text += f"Frequency: {config.get('frequency', 'Unknown')}\n"
                tz_info = get_system_timezone_info()
                status_text += f"Time: {config.get('time', 'Unknown')} ({tz_info})\n"
                backup_dir = config.get('backup_dir', 'Unknown')
                status_text += f"Backup Directory: {backup_dir}"
                
                # Check if backup directory is in a cloud sync folder
                cloud_folders = detect_cloud_sync_folders()
                cloud_sync_detected = None
                for cloud_name, cloud_path in cloud_folders.items():
                    if backup_dir.startswith(cloud_path):
                        cloud_sync_detected = cloud_name
                        break
                
                if cloud_sync_detected:
                    status_text += f"\n☁️ Cloud Sync: {cloud_sync_detected} (automatic sync enabled)"
                else:
                    status_text += "\n💾 Storage: Local only (no cloud sync detected)"
            
            tk.Label(
                status_frame, 
                text=status_text, 
                font=("Arial", 11), 
                bg=self.theme_colors['info_bg'], 
                fg=self.theme_colors['warning_fg']
            ).pack(pady=5)
            
            # Add buttons for managing existing schedule
            btn_frame = tk.Frame(status_frame, bg=self.theme_colors['info_bg'])
            btn_frame.pack(pady=10)
            
            # Test Run button (enabled when schedule is active)
            test_run_btn = tk.Button(
                btn_frame,
                text="🧪 Test Run",
                font=("Arial", 11),
                bg="#3498db",
                fg="white",
                command=lambda: self._run_test_backup_scheduled(config)
            )
            test_run_btn.pack(side="left", padx=5)
            
            # Add tooltip for Test Run button
            ToolTip(test_run_btn, 
                   "Click to immediately run a backup using the current schedule configuration.\n"
                   "This will verify that your scheduled backup is working correctly.")
            
            tk.Button(
                btn_frame, 
                text="Disable Schedule", 
                font=("Arial", 11),
                bg=self.theme_colors['button_bg'],
                fg=self.theme_colors['button_fg'],
                command=lambda: self._disable_schedule(task_name)
            ).pack(side="left", padx=5)
            
            tk.Button(
                btn_frame, 
                text="Delete Schedule", 
                font=("Arial", 11),
                bg=self.theme_colors['button_bg'],
                fg=self.theme_colors['button_fg'],
                command=lambda: self._delete_schedule(task_name)
            ).pack(side="left", padx=5)
        else:
            tk.Label(
                status_frame, 
                text="✗ No scheduled backup configured", 
                font=("Arial", 11), 
                bg=self.theme_colors['info_bg'], 
                fg=self.theme_colors['error_fg']
            ).pack(pady=5)
            
            # Add disabled Test Run button when no schedule exists
            btn_frame = tk.Frame(status_frame, bg=self.theme_colors['info_bg'])
            btn_frame.pack(pady=10)
            
            # Disabled Test Run button
            test_run_btn = tk.Button(
                btn_frame,
                text="🧪 Test Run",
                font=("Arial", 11),
                bg="#d3d3d3",  # Gray background when disabled
                fg="#808080",  # Gray text when disabled
                state=tk.DISABLED
            )
            test_run_btn.pack(side="left", padx=5)
            
            # Add tooltip explaining why it's disabled
            ToolTip(test_run_btn, 
                   "Test Run is disabled because no backup schedule is configured.\n"
                   "Please create a schedule first to enable this feature.")
        
        # Configuration section
        config_frame = tk.Frame(scrollable_frame, bg=self.theme_colors['bg'])
        config_frame.pack(pady=20, fill="x", padx=40)
        
        tk.Label(
            config_frame, 
            text="Configure New Schedule", 
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=10)
        
        # Backup directory with cloud storage detection
        dir_label_frame = tk.Frame(config_frame, bg=self.theme_colors['bg'])
        dir_label_frame.pack(pady=5)
        
        tk.Label(dir_label_frame, text="Backup Directory:", font=("Arial", 11),
                bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(side="left")
        
        # Add info icon with tooltip
        info_icon = tk.Label(dir_label_frame, text="ℹ️", font=("Arial", 11),
                            bg=self.theme_colors['bg'], fg=self.theme_colors['info_fg'], cursor="hand2")
        info_icon.pack(side="left", padx=5)
        ToolTip(info_icon, 
                "Choose where to save your backups:\n\n"
                "• Local folder: Backups saved only on this computer\n"
                "• Cloud sync folder: Backups automatically sync to cloud\n\n"
                "Cloud Storage Options:\n"
                "✓ OneDrive, Google Drive, Dropbox, iCloud Drive\n"
                "✓ Select your cloud provider's local sync folder\n"
                "✓ Files will automatically upload to the cloud\n\n"
                "Note: Large backups may take time to sync.")
        
        dir_frame = tk.Frame(config_frame, bg=self.theme_colors['bg'])
        dir_frame.pack(pady=5, fill="x")
        
        backup_dir_var = tk.StringVar(value=config.get('backup_dir', '') if config else '')
        dir_entry = tk.Entry(dir_frame, textvariable=backup_dir_var, font=("Arial", 11),
                            bg=self.theme_colors['entry_bg'], fg=self.theme_colors['entry_fg'],
                            insertbackground=self.theme_colors['entry_fg'])
        dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(
            dir_frame, 
            text="Browse", 
            font=("Arial", 10),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=lambda: self._browse_backup_dir(backup_dir_var)
        ).pack(side="right")
        
        # Detect and display cloud sync folders
        cloud_folders = detect_cloud_sync_folders()
        if cloud_folders:
            cloud_info_frame = tk.Frame(config_frame, bg=self.theme_colors['bg'])
            cloud_info_frame.pack(pady=5, fill="x")
            
            # Header with info icon
            cloud_header_frame = tk.Frame(cloud_info_frame, bg=self.theme_colors['bg'])
            cloud_header_frame.pack(anchor="w", pady=(0, 5))
            
            tk.Label(cloud_header_frame, text="📁 Detected Cloud Sync Folders:", font=("Arial", 9, "italic"),
                    bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg']).pack(side="left")
            
            # Add info icon that opens the Cloud Storage Setup Guide
            info_icon = tk.Label(
                cloud_header_frame,
                text=" ℹ️",
                font=("Arial", 10),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['info_fg'],
                cursor="hand2"
            )
            info_icon.pack(side="left", padx=5)
            info_icon.bind("<Button-1>", lambda e: self._show_cloud_storage_guide())
            ToolTip(info_icon, "Click for Cloud Storage Setup Guide")
            
            for cloud_name, cloud_path in cloud_folders.items():
                cloud_btn_frame = tk.Frame(cloud_info_frame, bg=self.theme_colors['bg'])
                cloud_btn_frame.pack(pady=2, fill="x")
                
                cloud_btn = tk.Button(
                    cloud_btn_frame,
                    text=f"☁️ {cloud_name}: {cloud_path}",
                    font=("Arial", 9),
                    bg=self.theme_colors['entry_bg'],
                    fg=self.theme_colors['entry_fg'],
                    command=lambda p=cloud_path: backup_dir_var.set(p),
                    anchor="w",
                    relief=tk.FLAT,
                    cursor="hand2"
                )
                cloud_btn.pack(side="left", fill="x", expand=True)
                ToolTip(cloud_btn, f"Click to select {cloud_name} as backup destination.\nBackups will sync automatically to your cloud storage.")
        
        # Frequency
        tk.Label(config_frame, text="Frequency:", font=("Arial", 11),
                bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(pady=(15, 5))
        frequency_var = tk.StringVar(value=config.get('frequency', 'daily') if config else 'daily')
        
        freq_frame = tk.Frame(config_frame, bg=self.theme_colors['bg'])
        freq_frame.pack(pady=5)
        
        for freq in ['daily', 'weekly', 'monthly']:
            tk.Radiobutton(
                freq_frame, 
                text=freq.capitalize(), 
                variable=frequency_var, 
                value=freq,
                font=("Arial", 11),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['fg'],
                selectcolor=self.theme_colors['entry_bg']
            ).pack(side="left", padx=10)
        
        # Time with timezone info
        time_label_frame = tk.Frame(config_frame, bg=self.theme_colors['bg'])
        time_label_frame.pack(pady=(15, 5))
        
        tk.Label(time_label_frame, text="Backup Time (HH:MM):", font=("Arial", 11),
                bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack(side="left")
        
        # Add timezone display
        tz_info = get_system_timezone_info()
        tz_label = tk.Label(time_label_frame, text=f"  [{tz_info}]", font=("Arial", 9),
                           bg=self.theme_colors['bg'], fg=self.theme_colors['hint_fg'])
        tz_label.pack(side="left")
        ToolTip(tz_label, "Backup times are in your system's local time zone.\nThe task scheduler will run at this time on your local system.")
        
        time_var = tk.StringVar(value=config.get('time', '02:00') if config else '02:00')
        time_entry = tk.Entry(config_frame, textvariable=time_var, font=("Arial", 11), width=10,
                             bg=self.theme_colors['entry_bg'], fg=self.theme_colors['entry_fg'],
                             insertbackground=self.theme_colors['entry_fg'])
        time_entry.pack(pady=5)
        ToolTip(time_entry, f"Enter time in 24-hour format (HH:MM)\nExample: 02:00 for 2 AM, 14:30 for 2:30 PM\nTimezone: {tz_info}")
        
        # Encryption
        encrypt_var = tk.BooleanVar(value=config.get('encrypt', False) if config else False)
        tk.Checkbutton(
            config_frame, 
            text="Encrypt backups", 
            variable=encrypt_var,
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            selectcolor=self.theme_colors['entry_bg']
        ).pack(pady=10)
        
        # Password (shown only if encryption is enabled)
        password_frame = tk.Frame(config_frame, bg=self.theme_colors['bg'])
        password_frame.pack(pady=5)
        
        tk.Label(password_frame, text="Encryption Password:", font=("Arial", 11),
                bg=self.theme_colors['bg'], fg=self.theme_colors['fg']).pack()
        password_var = tk.StringVar(value=config.get('password', '') if config else '')
        password_entry = tk.Entry(password_frame, textvariable=password_var, show="*", font=("Arial", 11), width=30,
                                 bg=self.theme_colors['entry_bg'], fg=self.theme_colors['entry_fg'],
                                 insertbackground=self.theme_colors['entry_fg'])
        password_entry.pack(pady=5)
        
        def toggle_password_field(*args):
            if encrypt_var.get():
                password_frame.pack(pady=5)
            else:
                password_frame.pack_forget()
        
        encrypt_var.trace_add('write', toggle_password_field)
        toggle_password_field()  # Initial state
        
        # Component selection section
        component_frame = tk.Frame(config_frame, bg=self.theme_colors['bg'])
        component_frame.pack(pady=(15, 10), fill="x")
        
        tk.Label(
            component_frame,
            text="📁 Components to Backup:",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(0, 5))
        
        tk.Label(
            component_frame,
            text="Select which folders to include in scheduled backups",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(0, 10))
        
        # Get component selection from config
        components_config = config.get('components', {}) if config else {}
        
        # Component checkboxes
        component_vars = {}
        components = [
            ("config", True, "Configuration files (Required)"),
            ("data", True, "User data and files (Required)"),
            ("apps", False, "Standard Nextcloud apps"),
            ("custom_apps", False, "Custom/third-party apps"),
        ]
        
        for folder, is_critical, description in components:
            comp_row = tk.Frame(component_frame, bg=self.theme_colors['bg'])
            comp_row.pack(fill="x", pady=2, padx=20)
            
            # Default to True for required components, check config for optional ones
            default_value = True if is_critical else components_config.get(folder, True)
            var = tk.BooleanVar(value=default_value)
            component_vars[folder] = (var, is_critical)
            
            cb = tk.Checkbutton(
                comp_row,
                text=f"{folder}",
                variable=var,
                font=("Arial", 10, "bold" if is_critical else "normal"),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['fg'],
                selectcolor=self.theme_colors['entry_bg'],
                state=tk.DISABLED if is_critical else tk.NORMAL
            )
            cb.pack(side="left", padx=(0, 10))
            
            desc_label = tk.Label(
                comp_row,
                text=f"- {description}",
                font=("Arial", 8),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['hint_fg'],
                anchor="w"
            )
            desc_label.pack(side="left")
            
            if is_critical:
                ToolTip(cb, "This component is required for a complete backup")
        
        # Backup rotation section
        rotation_frame = tk.Frame(config_frame, bg=self.theme_colors['bg'])
        rotation_frame.pack(pady=(15, 10), fill="x")
        
        tk.Label(
            rotation_frame,
            text="♻️ Backup Rotation:",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(0, 5))
        
        tk.Label(
            rotation_frame,
            text="Automatically delete old backups when limit is reached",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(0, 10))
        
        # Rotation options
        rotation_label_frame = tk.Frame(rotation_frame, bg=self.theme_colors['bg'])
        rotation_label_frame.pack(pady=5)
        
        tk.Label(
            rotation_label_frame,
            text="Keep last:",
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(side="left", padx=(20, 10))
        
        # Get rotation setting from config (default to 0 = unlimited)
        current_rotation = config.get('rotation_keep', 0) if config else 0
        rotation_var = tk.IntVar(value=current_rotation)
        
        rotation_options_frame = tk.Frame(rotation_frame, bg=self.theme_colors['bg'])
        rotation_options_frame.pack(pady=5)
        
        rotation_options = [
            (0, "Unlimited (no deletion)"),
            (1, "1 backup (always replace)"),
            (2, "2 backups"),
            (3, "3 backups"),
            (5, "5 backups"),
            (10, "10 backups")
        ]
        
        # Create dropdown menu for rotation options
        rotation_dropdown_frame = tk.Frame(rotation_options_frame, bg=self.theme_colors['bg'])
        rotation_dropdown_frame.pack(padx=20, pady=5)
        
        # Create a mapping from display text to value
        rotation_display_options = [label for value, label in rotation_options]
        rotation_value_map = {label: value for value, label in rotation_options}
        rotation_reverse_map = {value: label for value, label in rotation_options}
        
        # Set initial selection based on current rotation value
        initial_selection = rotation_reverse_map.get(current_rotation, "Unlimited (no deletion)")
        
        rotation_combobox = ttk.Combobox(
            rotation_dropdown_frame,
            values=rotation_display_options,
            state='readonly',
            font=("Arial", 10),
            width=30
        )
        rotation_combobox.set(initial_selection)
        rotation_combobox.pack(side="left")
        
        # Update rotation_var when selection changes
        def on_rotation_change(event):
            selected_label = rotation_combobox.get()
            rotation_var.set(rotation_value_map[selected_label])
        
        rotation_combobox.bind('<<ComboboxSelected>>', on_rotation_change)
        
        # Add tooltip to the combobox
        tooltip_text = ("Select how many backups to keep. Older backups will be automatically deleted.\n"
                       "• Unlimited: Keep all backups (requires manual cleanup)\n"
                       "• 1 backup: Always replace the previous backup (saves disk space)\n"
                       "• 2-10 backups: Keep this many recent backups, delete older ones")
        ToolTip(rotation_combobox, tooltip_text)
        
        # Note about Windows only
        if platform.system() != "Windows":
            warning_label = tk.Label(
                config_frame,
                text="⚠️ Note: Scheduled backups are currently only supported on Windows",
                font=("Arial", 10),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['warning_fg']
            )
            warning_label.pack(pady=10)
        
        # Inline notification/message area
        self.schedule_message_label = tk.Label(
            config_frame, 
            text="", 
            font=("Arial", 11), 
            bg=self.theme_colors['bg'],
            fg="green",
            wraplength=600,
            justify=tk.LEFT
        )
        self.schedule_message_label.pack(pady=10, fill="x")
        
        # Create schedule button
        tk.Button(
            config_frame,
            text="Create/Update Schedule",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            command=lambda: self._create_schedule(
                backup_dir_var.get(),
                frequency_var.get(),
                time_var.get(),
                encrypt_var.get(),
                password_var.get(),
                component_vars,
                rotation_var.get()
            )
        ).pack(pady=20)
        
        # Verify Backup button (if schedule exists)
        if status and status.get('exists'):
            tk.Button(
                config_frame,
                text="🔍 Verify Scheduled Backup",
                font=("Arial", 11),
                bg="#9b59b6",
                fg="white",
                command=lambda: self._verify_scheduled_backup(backup_dir, task_name)
            ).pack(pady=10)
        
        # Apply theme recursively to all widgets in the panel
        self.apply_theme_recursive(frame)
    
    def _browse_backup_dir(self, var):
        """Browse for backup directory."""
        directory = filedialog.askdirectory(title="Select backup destination folder")
        if directory:
            var.set(directory)
    
    def _show_cloud_storage_guide(self):
        """Show the Cloud Storage Setup Guide in a dialog window."""
        dialog = tk.Toplevel(self)
        dialog.title("Cloud Storage Setup Guide")
        dialog.geometry("600x500")
        dialog.configure(bg=self.theme_colors['bg'])
        
        # Make it modal
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"600x500+{x}+{y}")
        
        # Main frame with scrollbar
        main_frame = tk.Frame(dialog, bg=self.theme_colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_label = tk.Label(
            main_frame,
            text="💡 Cloud Storage Setup Guide",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        header_label.pack(pady=(0, 10))
        
        # Content frame with scrollbar
        canvas = tk.Canvas(main_frame, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content text
        help_text = (
            "To sync backups to cloud storage:\n\n"
            "OneDrive:\n"
            "  1. Install OneDrive desktop app\n"
            "  2. Sign in and select folders to sync\n"
            "  3. Choose a folder inside your OneDrive folder above\n\n"
            "Google Drive:\n"
            "  1. Install Google Drive for Desktop\n"
            "  2. Sign in and configure sync settings\n"
            "  3. Choose a folder inside your Google Drive folder above\n\n"
            "Dropbox:\n"
            "  1. Install Dropbox desktop app\n"
            "  2. Sign in and select folders to sync\n"
            "  3. Choose a folder inside your Dropbox folder above\n\n"
            "Note: Backups will automatically upload to the cloud after creation.\n"
            "Large backups may take time to sync depending on your internet speed."
        )
        
        content_label = tk.Label(
            scrollable_frame,
            text=help_text,
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['entry_fg'],
            justify=tk.LEFT,
            wraplength=550
        )
        content_label.pack(pady=10, padx=10)
        
        # Close button
        close_btn = tk.Button(
            main_frame,
            text="Close",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=dialog.destroy
        )
        close_btn.pack(pady=(10, 0))
        
        # Apply theme
        self.apply_theme_recursive(dialog)
    
    def _create_schedule(self, backup_dir, frequency, time, encrypt, password, component_vars, rotation_keep):
        """Create or update a scheduled backup with validation."""
        task_name = "NextcloudBackup"
        
        # Clear any previous messages
        if hasattr(self, 'schedule_message_label'):
            self.schedule_message_label.config(text="", fg="green")
        
        # Extract selected components
        components = {}
        for folder, (var, is_critical) in component_vars.items():
            components[folder] = var.get()
        
        # Run validation checks
        logger.info("Running pre-creation validation checks...")
        validation_results = validate_scheduled_task_setup(
            task_name, frequency, time, backup_dir, encrypt, password
        )
        
        # Show validation results inline
        if not validation_results['all_valid']:
            error_msg = "❌ Setup Validation Failed\n\n"
            error_msg += "The following issues were found:\n\n"
            for error in validation_results['errors']:
                error_msg += f"• {error}\n"
            error_msg += "\nPlease fix these issues before creating the scheduled backup."
            
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(text=error_msg, fg=self.theme_colors['error_fg'])
            return
        
        # All validations passed - proceed with creation directly (no confirmation pop-up)
        
        # Create the scheduled task
        success, message = create_scheduled_task(
            task_name, 
            frequency, 
            time, 
            backup_dir, 
            encrypt, 
            password,
            components,
            rotation_keep
        )
        
        if success:
            # Save configuration
            config = {
                'task_name': task_name,
                'backup_dir': backup_dir,
                'frequency': frequency,
                'time': time,
                'encrypt': encrypt,
                'password': password,  # Note: In production, consider more secure storage
                'components': components,
                'rotation_keep': rotation_keep,
                'enabled': True,
                'created_at': datetime.now().isoformat()
            }
            
            if save_schedule_config(config):
                # Build success message with component details
                selected_comps = [k for k, v in components.items() if v]
                comp_list = ", ".join(selected_comps)
                rotation_msg = f"{rotation_keep} backups" if rotation_keep > 0 else "unlimited"
                
                success_msg = (
                    f"✅ Scheduled backup created successfully!\n\n"
                    f"Frequency: {frequency}\n"
                    f"Time: {time}\n"
                    f"Backup Directory: {backup_dir}\n"
                    f"Components: {comp_list}\n"
                    f"Rotation: Keep {rotation_msg}\n\n"
                    f"Your backups will run automatically according to this schedule.\n"
                    f"You can now use the Test Run button to verify your setup."
                )
                if hasattr(self, 'schedule_message_label'):
                    self.schedule_message_label.config(text=success_msg, fg="green")
                self.show_schedule_backup()  # Stay on schedule page to allow testing
            else:
                warning_msg = "⚠️ Task created but configuration could not be saved."
                if hasattr(self, 'schedule_message_label'):
                    self.schedule_message_label.config(text=warning_msg, fg=self.theme_colors['warning_fg'])
                self.show_schedule_backup()
        else:
            error_msg = f"❌ Failed to create scheduled task:\n{message}"
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(text=error_msg, fg=self.theme_colors['error_fg'])
            else:
                self.show_schedule_backup()
    
    def _disable_schedule(self, task_name):
        """Disable the scheduled backup."""
        success, message = disable_scheduled_task(task_name)
        
        if success:
            # Update config
            config = load_schedule_config()
            if config:
                config['enabled'] = False
                save_schedule_config(config)
            
            # Show inline success message
            self.show_schedule_backup()  # Refresh the UI
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(text="✅ Scheduled backup has been disabled.", fg="green")
        else:
            # Show inline error message
            self.show_schedule_backup()
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(text=f"❌ Failed to disable schedule:\n{message}", fg=self.theme_colors['error_fg'])
    
    def _delete_schedule(self, task_name):
        """Delete the scheduled backup."""
        # Show inline confirmation request
        if hasattr(self, 'schedule_message_label'):
            self.schedule_message_label.config(
                text="⚠️ Are you sure? Click Delete Schedule again to confirm deletion. This will remove the scheduled task completely.",
                fg=self.theme_colors['warning_fg']
            )
        
        # Use a simple confirmation approach - user needs to click twice
        if not hasattr(self, '_delete_confirm_pending'):
            self._delete_confirm_pending = False
        
        if not self._delete_confirm_pending:
            self._delete_confirm_pending = True
            # After 5 seconds, reset the confirmation
            self.after(5000, lambda: setattr(self, '_delete_confirm_pending', False))
            return
        
        # Reset confirmation flag
        self._delete_confirm_pending = False
        
        success, message = delete_scheduled_task(task_name)
        
        if success:
            # Delete config file
            config_path = get_schedule_config_path()
            if os.path.exists(config_path):
                os.remove(config_path)
            
            # Return to landing page since no schedule exists now
            self.show_landing()
        else:
            # Stay on page and show error
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(text=f"❌ Failed to delete schedule:\n{message}", fg=self.theme_colors['error_fg'])
            self.show_schedule_backup()
    
    def _run_test_backup_scheduled(self, config):
        """
        Run a test backup using Windows Task Scheduler.
        This creates a temporary scheduled task, runs it, monitors completion, and cleans up.
        """
        # Clear previous messages
        if hasattr(self, 'schedule_message_label'):
            self.schedule_message_label.config(text="", fg="green")
        
        if not config:
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(
                    text="❌ No schedule configuration found. Please create a schedule first.",
                    fg=self.theme_colors['error_fg']
                )
            return
        
        # Get configuration from schedule
        backup_dir = config.get('backup_dir', '')
        encrypt = config.get('encrypt', False)
        password = config.get('password', '')
        task_name = config.get('task_name', 'NextcloudBackup')
        
        if not backup_dir:
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(
                    text="❌ Backup directory not configured in schedule.",
                    fg=self.theme_colors['error_fg']
                )
            return
        
        if not os.path.isdir(backup_dir):
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(
                    text=f"❌ Backup directory does not exist: {backup_dir}",
                    fg=self.theme_colors['error_fg']
                )
            return
        
        # Show inline progress message
        if hasattr(self, 'schedule_message_label'):
            self.schedule_message_label.config(
                text="⏳ Running test backup via Task Scheduler... Please wait...",
                fg="#FFD700"
            )
        
        def run_test():
            """Run test backup through Windows Task Scheduler."""
            try:
                # Create a temporary test task
                test_task_name = f"{task_name}_TestRun"
                
                # Get the executable path
                exe_path = get_exe_path()
                
                # Ensure backup_dir is safely quoted (prevents argument splitting with spaces)
                backup_dir_quoted = '"' + backup_dir.strip('"') + '"'
                
                # Build the command arguments for test run
                args = [
                    "--test-run",
                    "--backup-dir", backup_dir_quoted,
                    "--encrypt" if encrypt else "--no-encrypt"
                ]
                
                if encrypt and password:
                    args.extend(["--password", password])
                
                # Build the full command
                if exe_path.lower().endswith('.py'):
                    # For Python scripts, invoke through Python interpreter
                    command = f'python "{exe_path}" {" ".join(args)}'
                else:
                    # For compiled executables (.exe), run directly
                    command = f'"{exe_path}" {" ".join(args)}'
                
                logger.info(f"Creating temporary test task: {test_task_name}")
                
                # Delete any existing test task
                creation_flags = get_subprocess_creation_flags()
                subprocess.run(
                    ["schtasks", "/Delete", "/TN", test_task_name, "/F"],
                    creationflags=creation_flags,
                    capture_output=True,
                    text=True
                )
                
                # Create temporary scheduled task (runs once, immediately)
                schtasks_cmd = [
                    "schtasks", "/Create",
                    "/TN", test_task_name,
                    "/TR", command,
                    "/SC", "ONCE",  # Run only once
                    "/ST", "00:00",  # Start time (not used for /Run)
                    "/F"  # Force creation
                ]
                
                print("Scheduled Task Command:", schtasks_cmd)
                result = subprocess.run(
                    schtasks_cmd,
                    creationflags=creation_flags,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    error_msg = f"Failed to create test task: {result.stderr}"
                    logger.error(error_msg)
                    if hasattr(self, 'schedule_message_label'):
                        self.schedule_message_label.config(
                            text=f"❌ {error_msg}",
                            fg=self.theme_colors['error_fg']
                        )
                    return
                
                logger.info(f"Test task created, triggering execution...")
                
                # Run the task immediately
                run_success, run_message = run_scheduled_task_now(test_task_name)
                
                if not run_success:
                    logger.error(f"Failed to run test task: {run_message}")
                    if hasattr(self, 'schedule_message_label'):
                        self.schedule_message_label.config(
                            text=f"❌ {run_message}",
                            fg=self.theme_colors['error_fg']
                        )
                    # Clean up
                    subprocess.run(
                        ["schtasks", "/Delete", "/TN", test_task_name, "/F"],
                        creationflags=creation_flags,
                        capture_output=True
                    )
                    return
                
                logger.info("Test task triggered, waiting for completion...")
                
                # Wait for task to complete (poll status)
                max_wait_time = 60  # Maximum 60 seconds
                poll_interval = 1  # Check every second
                elapsed_time = 0
                
                while elapsed_time < max_wait_time:
                    time.sleep(poll_interval)
                    elapsed_time += poll_interval
                    
                    # Check task status
                    status_result = subprocess.run(
                        ["schtasks", "/Query", "/TN", test_task_name, "/FO", "LIST", "/V"],
                        creationflags=creation_flags,
                        capture_output=True,
                        text=True
                    )
                    
                    if status_result.returncode == 0:
                        output = status_result.stdout
                        # Check if task is still running
                        if "Running" not in output:
                            # Task completed
                            logger.info("Test task completed")
                            break
                
                # Check if we timed out
                if elapsed_time >= max_wait_time:
                    logger.warning("Test task execution timed out")
                    if hasattr(self, 'schedule_message_label'):
                        self.schedule_message_label.config(
                            text="⚠️ Test backup timed out. Task may still be running in background.",
                            fg=self.theme_colors['warning_fg']
                        )
                else:
                    # Task completed - determine success/failure
                    # Check if test backup file exists (it should be deleted if successful)
                    test_files = [f for f in os.listdir(backup_dir) if f.startswith('test_config_backup_')]
                    
                    if not test_files:
                        # Success - no test files found (they were deleted)
                        logger.info("Test backup successful - files cleaned up as expected")
                        if hasattr(self, 'schedule_message_label'):
                            result_msg = (
                                f"✅ Test Backup Successful!\n\n"
                                f"Config file backed up: schedule_config.json\n"
                                f"Task Scheduler: Verified ✓\n"
                                f"Permissions: Verified ✓\n"
                                f"Environment: Verified ✓\n"
                                f"Test backup deleted (as expected)\n\n"
                                f"Your scheduled backup is configured correctly and will run as scheduled."
                            )
                            self.schedule_message_label.config(text=result_msg, fg="green")
                    else:
                        # Partial success - files created but not deleted
                        logger.warning("Test backup files not cleaned up properly")
                        if hasattr(self, 'schedule_message_label'):
                            self.schedule_message_label.config(
                                text=f"⚠️ Test backup ran but cleanup failed.\nPlease check {backup_dir} for test files.",
                                fg=self.theme_colors['warning_fg']
                            )
                
                # Clean up the temporary task
                logger.info(f"Cleaning up test task: {test_task_name}")
                subprocess.run(
                    ["schtasks", "/Delete", "/TN", test_task_name, "/F"],
                    creationflags=creation_flags,
                    capture_output=True,
                    text=True
                )
                
            except Exception as e:
                error_msg = f"Test backup failed: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                if hasattr(self, 'schedule_message_label'):
                    self.schedule_message_label.config(
                        text=f"❌ {error_msg}",
                        fg=self.theme_colors['error_fg']
                    )
        
        # Run test in thread
        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()
    
    def _run_test_backup(self, backup_dir, encrypt, password):
        """Run a test backup to verify configuration."""
        # Clear previous messages
        if hasattr(self, 'schedule_message_label'):
            self.schedule_message_label.config(text="", fg="green")
        
        if not backup_dir:
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(text="❌ Please select a backup directory first.", fg=self.theme_colors['error_fg'])
            return
        
        if not os.path.isdir(backup_dir):
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(text="❌ Invalid backup directory.", fg=self.theme_colors['error_fg'])
            return
        
        if encrypt and not password:
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(text="❌ Please provide an encryption password or disable encryption.", fg=self.theme_colors['error_fg'])
            return
        
        # Show inline progress message
        if hasattr(self, 'schedule_message_label'):
            self.schedule_message_label.config(text="⏳ Running test backup... Please wait...", fg="#FFD700")
        
        def run_test():
            success, message = run_test_backup(backup_dir, encrypt, password)
            
            # Update inline message with result
            if success:
                if hasattr(self, 'schedule_message_label'):
                    self.schedule_message_label.config(text=f"✅ Test Backup Successful!\n{message}", fg="green")
            else:
                if hasattr(self, 'schedule_message_label'):
                    self.schedule_message_label.config(text=f"❌ Test Backup Failed:\n{message}", fg=self.theme_colors['error_fg'])
        
        # Run test in thread
        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()
    
    def _show_recent_logs(self, backup_dir):
        """Show recent log entries related to scheduled backups."""
        # Create a new window for logs
        log_window = tk.Toplevel(self.root)
        log_window.title("Recent Backup Logs")
        log_window.geometry("800x600")
        log_window.transient(self.root)
        
        # Center the window
        log_window.update_idletasks()
        x = (log_window.winfo_screenwidth() // 2) - (400)
        y = (log_window.winfo_screenheight() // 2) - (300)
        log_window.geometry(f"800x600+{x}+{y}")
        
        # Title
        tk.Label(
            log_window,
            text="📄 Recent Scheduled Backup Logs",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=10)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(log_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg']
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Get recent log entries
        log_entries = get_recent_log_entries(200)
        
        if log_entries:
            # Filter for scheduled backup entries
            scheduled_entries = [line for line in log_entries if 'SCHEDULED' in line or 'scheduled' in line or 'VALIDATION' in line or 'TEST RUN' in line]
            
            if scheduled_entries:
                text_widget.insert(tk.END, f"Found {len(scheduled_entries)} relevant log entries:\n\n")
                text_widget.insert(tk.END, "=" * 80 + "\n\n")
                for entry in scheduled_entries:
                    text_widget.insert(tk.END, entry)
            else:
                text_widget.insert(tk.END, "No scheduled backup log entries found.\n\n")
                text_widget.insert(tk.END, "Showing all recent logs:\n\n")
                text_widget.insert(tk.END, "=" * 80 + "\n\n")
                for entry in log_entries[-50:]:  # Last 50 entries
                    text_widget.insert(tk.END, entry)
        else:
            text_widget.insert(tk.END, "No log entries found.")
        
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        tk.Button(
            log_window,
            text="Close",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=log_window.destroy
        ).pack(pady=10)
    
    def _verify_scheduled_backup(self, backup_dir, task_name):
        """Verify that scheduled backup is working correctly."""
        if not backup_dir:
            if hasattr(self, 'schedule_message_label'):
                self.schedule_message_label.config(text="❌ No backup directory configured.", fg=self.theme_colors['error_fg'])
            return
        
        # Show inline progress message
        if hasattr(self, 'schedule_message_label'):
            self.schedule_message_label.config(text="⏳ Verifying scheduled backup... Checking backup files and logs...", fg=self.theme_colors['progress_fg'], font=("Arial", 11, "bold"))
        
        def run_verification():
            verification = verify_scheduled_backup_ran(backup_dir, task_name)
            
            # Show results inline
            if hasattr(self, 'schedule_message_label'):
                icon = "✅" if verification.get('backup_file_exists', False) else "⚠️"
                self.schedule_message_label.config(
                    text=f"{icon} Verification Results:\n{verification['message']}", 
                    fg="green" if verification.get('backup_file_exists', False) else self.theme_colors['warning_fg']
                )
        
        # Run verification in thread
        thread = threading.Thread(target=run_verification, daemon=True)
        thread.start()
    
    def run_scheduled_backup(self, backup_dir, encrypt, password, components=None, rotation_keep=0):
        """
        Run a backup in scheduled/silent mode (no GUI interactions).
        This is called when the app is launched with --scheduled flag.
        
        Args:
            backup_dir: Directory to save backup
            encrypt: Whether to encrypt the backup
            password: Encryption password
            components: List of component names to backup (None = all)
            rotation_keep: Number of backups to keep (0 = unlimited)
        """
        try:
            # Check if Docker is running with detailed status
            docker_status = detect_docker_status()
            if docker_status['status'] != 'running':
                error_msg = f"ERROR: Cannot perform backup. {docker_status['message']}"
                if docker_status['suggested_action']:
                    error_msg += f"\n\nSuggested action:\n{docker_status['suggested_action']}"
                print(error_msg)
                logger.error(f"Scheduled backup failed: {docker_status['message']}")
                return
            
            # Get Nextcloud container
            container_names = get_nextcloud_container_name()
            if not container_names:
                print("ERROR: No running Nextcloud container found.")
                return
            
            chosen_container = container_names
            
            # Detect database type
            dbtype, db_config = detect_database_type_from_container(chosen_container)
            if not dbtype:
                dbtype = 'pgsql'  # Default to PostgreSQL
            
            # Store for backup process
            self.backup_dbtype = dbtype
            self.backup_db_config = db_config
            
            # Override set_progress to use print instead of GUI
            self._scheduled_mode = True
            
            # Run backup process silently
            print(f"Starting scheduled backup to {backup_dir}")
            if components:
                print(f"Backing up components: {', '.join(components)}")
            if rotation_keep > 0:
                print(f"Backup rotation: keeping last {rotation_keep} backup(s)")
            
            self.run_backup_process_scheduled(backup_dir, encrypt, password, chosen_container, components)
            print("Scheduled backup completed successfully")
            
            # Perform backup rotation if configured
            if rotation_keep > 0:
                print(f"\nPerforming backup rotation (keep last {rotation_keep} backups)...")
                self._perform_backup_rotation(backup_dir, rotation_keep)
            
        except Exception as e:
            print(f"ERROR: Scheduled backup failed: {e}")
            traceback.print_exc()
    
    def run_backup_process_scheduled(self, backup_dir, encrypt, encryption_password, container_name, components=None):
        """
        Run backup process in scheduled mode (no GUI, just logging to console).
        
        Args:
            backup_dir: Directory to save backup
            encrypt: Whether to encrypt
            encryption_password: Encryption password
            container_name: Nextcloud container name
            components: List of component names to backup (None = all)
        """
        NEXTCLOUD_PATH = "/var/www/html"
        try:
            print("Step 1/10: Preparing backup...")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_temp = os.path.join(tempfile.gettempdir(), f"ncbackup_{timestamp}")
            os.makedirs(backup_temp, exist_ok=True)
            backup_file = os.path.join(backup_dir, f"nextcloud-backup-{timestamp}.tar.gz")
            encrypted_file = backup_file + ".gpg"

            # Define folders with their criticality
            all_folders = [
                ("config", True),
                ("data", True),
                ("apps", False),
                ("custom_apps", False),
            ]
            
            # Filter folders based on component selection
            if components:
                folders_to_copy = [(f, c) for f, c in all_folders if f in components or c]
            else:
                folders_to_copy = all_folders
            
            copied_folders = []
            skipped_folders = []
            
            for idx, (folder, is_critical) in enumerate(folders_to_copy, start=2):
                print(f"Step {idx}/10: Checking and copying '{folder}'...")
                check = subprocess.run(
                    f'docker exec {container_name} test -d {NEXTCLOUD_PATH}/{folder}',
                    shell=True
                )
                if check.returncode == 0:
                    try:
                        subprocess.run(
                            f'docker cp {container_name}:{NEXTCLOUD_PATH}/{folder} {backup_temp}/{folder}',
                            shell=True, check=True
                        )
                        copied_folders.append(folder)
                        print(f"  ✓ Copied '{folder}'")
                    except Exception as cp_err:
                        print(f"  ✗ Failed to copy '{folder}' but continuing...")
                else:
                    if is_critical:
                        print(f"CRITICAL FOLDER '{folder}' IS MISSING! Backup aborted.")
                        shutil.rmtree(backup_temp, ignore_errors=True)
                        return
                    else:
                        skipped_folders.append(folder)
                        print(f"  - Skipping '{folder}' (not found; not critical)")

            # Database backup
            dbtype = getattr(self, 'backup_dbtype', 'pgsql')
            db_config = getattr(self, 'backup_db_config', {})
            
            if dbtype in ['sqlite', 'sqlite3']:
                print("Step 6/10: SQLite database backed up with data folder")
            else:
                db_name = dbtype.upper() if dbtype == 'pgsql' else 'MySQL/MariaDB'
                print(f"Step 6/10: Dumping {db_name} database...")
                dump_file = os.path.join(backup_temp, "nextcloud-db.sql")
                db_dump_result = None
                
                try:
                    if dbtype == 'pgsql':
                        db_container = get_postgres_container_name() or POSTGRES_CONTAINER_NAME
                        db_name_actual = db_config.get('dbname', POSTGRES_DB)
                        db_user = db_config.get('dbuser', POSTGRES_USER)
                        db_password = POSTGRES_PASSWORD
                        
                        db_dump_cmd = f'docker exec {db_container} bash -c "PGPASSWORD=\'{db_password}\' pg_dump -U {db_user} {db_name_actual}"'
                    elif dbtype in ['mysql', 'mariadb']:
                        db_host = db_config.get('dbhost', 'db')
                        db_name_actual = db_config.get('dbname', 'nextcloud')
                        db_user = db_config.get('dbuser', 'nextcloud')
                        
                        db_dump_cmd = f'docker exec {container_name} bash -c "mysqldump -h {db_host} -u {db_user} -p{POSTGRES_PASSWORD} {db_name_actual}"'
                    else:
                        raise Exception(f"Unsupported database type: {dbtype}")
                    
                    with open(dump_file, "w", encoding="utf8") as f:
                        proc = subprocess.Popen(db_dump_cmd, shell=True, stdout=f, stderr=subprocess.PIPE)
                        proc.wait()
                        db_dump_result = proc.returncode
                        
                except Exception as e:
                    print(f"Database dump error: {e}")
                    db_dump_result = 1
                
                if db_dump_result != 0:
                    print(f"CRITICAL: Database backup failed! Backup aborted.")
                    shutil.rmtree(backup_temp, ignore_errors=True)
                    return

            print("Step 7/10: Creating archive...")
            shutil.make_archive(backup_file.replace('.tar.gz',''), 'gztar', backup_temp)
            
            if encrypt and encryption_password:
                print("Step 8/10: Encrypting archive...")
                encrypt_file_gpg(backup_file, encrypted_file, encryption_password)
                os.remove(backup_file)
                final_file = encrypted_file
            else:
                final_file = backup_file
            
            print("Step 9/10: Cleaning up temp files...")
            shutil.rmtree(backup_temp, ignore_errors=True)

            print(f"Step 10/10: Backup complete!")
            print(f"Backup saved to: {final_file}")
            
            # Add backup to history
            print("Adding backup to history database...")
            logger.info(f"SCHEDULED BACKUP: Adding to history - File: {final_file}")
            folders_list = ['config', 'data'] + [f for f in copied_folders if f not in ['config', 'data']]
            backup_id = self.backup_history.add_backup(
                backup_path=final_file,
                database_type=dbtype,
                folders=folders_list,
                encrypted=bool(encrypt and encryption_password),
                notes="Scheduled backup"
            )
            print(f"✓ Backup added to history with ID: {backup_id}")
            print(f"  Database location: {self.backup_history.db_path}")
            logger.info(f"SCHEDULED BACKUP: Successfully added to history with ID {backup_id}")
            
        except Exception as e:
            tb = traceback.format_exc()
            print(f"Backup failed: {e}")
            print(tb)
    
    def _perform_backup_rotation(self, backup_dir, keep_count):
        """
        Perform backup rotation by deleting old backups when the limit is exceeded.
        
        Args:
            backup_dir: Directory containing backups
            keep_count: Number of backups to keep
        """
        try:
            # Get list of backup files in the directory
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith('nextcloud-backup-') and (
                    filename.endswith('.tar.gz') or filename.endswith('.tar.gz.gpg')
                ):
                    filepath = os.path.join(backup_dir, filename)
                    if os.path.isfile(filepath):
                        backup_files.append(filepath)
            
            if not backup_files:
                print("No backup files found for rotation")
                return
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            print(f"Found {len(backup_files)} backup file(s) in {backup_dir}")
            
            # Delete old backups if we exceed the limit
            if len(backup_files) > keep_count:
                files_to_delete = backup_files[keep_count:]
                print(f"Deleting {len(files_to_delete)} old backup(s)...")
                
                for filepath in files_to_delete:
                    try:
                        print(f"  Deleting: {os.path.basename(filepath)}")
                        os.remove(filepath)
                        logger.info(f"BACKUP ROTATION: Deleted old backup: {filepath}")
                        
                        # Also remove from backup history database if present
                        # Find the backup in history by path
                        backups = self.backup_history.get_all_backups(limit=1000)
                        for backup in backups:
                            backup_id, backup_path = backup[0], backup[1]
                            if backup_path == filepath:
                                self.backup_history.delete_backup(backup_id)
                                print(f"    Removed from backup history (ID: {backup_id})")
                                logger.info(f"BACKUP ROTATION: Removed from history - ID: {backup_id}")
                                break
                    except Exception as e:
                        print(f"  Warning: Failed to delete {filepath}: {e}")
                        logger.warning(f"BACKUP ROTATION: Failed to delete {filepath}: {e}")
                
                print(f"✓ Backup rotation complete. Kept {keep_count} newest backup(s)")
                logger.info(f"BACKUP ROTATION: Complete - kept {keep_count} backup(s)")
            else:
                print(f"✓ No rotation needed. Current backup count ({len(backup_files)}) ≤ limit ({keep_count})")
                logger.info(f"BACKUP ROTATION: Not needed - {len(backup_files)} backups ≤ {keep_count} limit")
        
        except Exception as e:
            print(f"ERROR during backup rotation: {e}")
            logger.error(f"BACKUP ROTATION: Error - {e}")
            traceback.print_exc()
    
    # ----- Tailscale Setup Wizard -----
    
    @log_page_render("TAILSCALE WIZARD")
    def show_tailscale_wizard(self):
        """Show the Tailscale setup wizard main page"""
        logger.info("TAILSCALE WIZARD: Setting current_page to 'tailscale_wizard'")
        self.current_page = 'tailscale_wizard'
        logger.info("TAILSCALE WIZARD: Clearing existing widgets")
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        self.status_label.config(text="Remote Access Setup")
        
        # Create minimal loading indicator first so page is never blank
        logger.info("TAILSCALE WIZARD: Creating minimal loading indicator")
        loading_label = tk.Label(
            self.body_frame,
            text="Loading Remote Access Setup...",
            font=("Arial", 12),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        loading_label.pack(expand=True)
        self.update_idletasks()
        
        # Remove loading indicator and create content frame with simplified geometry
        logger.info("TAILSCALE WIZARD: Creating centered content frame")
        loading_label.destroy()
        
        # Create content frame using .place() for centering (600px wide)
        # This is simpler than Canvas/scrollbar approach and uses only .pack() for children
        content = tk.Frame(self.body_frame, bg=self.theme_colors['bg'], width=600)
        
        # Maintain fixed width
        def maintain_width(event=None):
            content.config(width=600)
        
        content.bind('<Configure>', maintain_width)
        content.place(relx=0.5, anchor="n", y=10)
        logger.info("TAILSCALE WIZARD: Content frame placed successfully")
        
        # Title
        logger.info("TAILSCALE WIZARD: Creating title labels")
        tk.Label(
            content,
            text="🌐 Remote Access Setup",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(10, 5), fill="x", padx=40)
        
        tk.Label(
            content,
            text="Securely access your Nextcloud from anywhere using Tailscale VPN",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            wraplength=520
        ).pack(pady=(0, 20), fill="x", padx=40)
        
        # Info box
        logger.info("TAILSCALE WIZARD: Creating info box")
        info_frame = tk.Frame(content, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
        info_frame.pack(pady=10, fill="x", padx=40)
        
        tk.Label(
            info_frame,
            text="ℹ️ What is Tailscale?",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        tk.Label(
            info_frame,
            text="Tailscale creates a secure, private network (VPN) between your devices.\n"
                 "It allows you to access your Nextcloud server from anywhere without\n"
                 "exposing it to the public internet.",
            font=("Arial", 10),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg'],
            justify=tk.LEFT,
            wraplength=520
        ).pack(pady=(0, 10), padx=10, anchor="w")
        
        # Return to main menu button
        logger.info("TAILSCALE WIZARD: Creating return button")
        tk.Button(
            content,
            text="Return to Main Menu",
            font=("Arial", 12),
            command=self.show_landing,
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg']
        ).pack(pady=(10, 20), fill="x", padx=40)
        
        # Check Tailscale status
        logger.info("TAILSCALE WIZARD: Checking Tailscale installation status")
        self.status_label.config(text="Checking Tailscale installation...")
        self.update_idletasks()
        
        ts_installed = self._check_tailscale_installed()
        ts_running = self._check_tailscale_running() if ts_installed else False
        logger.info(f"TAILSCALE WIZARD: Status - Installed: {ts_installed}, Running: {ts_running}")
        
        # Status display
        logger.info("TAILSCALE WIZARD: Creating status display")
        status_frame = tk.Frame(content, bg=self.theme_colors['bg'])
        status_frame.pack(pady=10, fill="x", padx=40)
        
        # Installation status
        install_status = "✓ Installed" if ts_installed else "✗ Not Installed"
        install_color = self.theme_colors['warning_fg'] if ts_installed else self.theme_colors['error_fg']
        
        tk.Label(
            status_frame,
            text=f"Tailscale Installation: {install_status}",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['bg'],
            fg=install_color,
            wraplength=520
        ).pack(pady=5, anchor="w")
        
        # Running status
        if ts_installed:
            running_status = "✓ Running" if ts_running else "✗ Not Running"
            running_color = self.theme_colors['warning_fg'] if ts_running else self.theme_colors['error_fg']
            
            tk.Label(
                status_frame,
                text=f"Tailscale Status: {running_status}",
                font=("Arial", 11, "bold"),
                bg=self.theme_colors['bg'],
                fg=running_color,
                wraplength=520
            ).pack(pady=5, anchor="w")
        
        self.status_label.config(text="Remote Access Setup")
        
        # Action buttons frame
        logger.info("TAILSCALE WIZARD: Creating action buttons")
        actions_frame = tk.Frame(content, bg=self.theme_colors['bg'])
        actions_frame.pack(pady=20, fill="x", padx=40)
        
        if not ts_installed:
            logger.info("TAILSCALE WIZARD: Creating Install button (Tailscale not installed)")
            # Install button
            tk.Button(
                actions_frame,
                text="📦 Install Tailscale",
                font=("Arial", 13, "bold"),
                bg="#3daee9",
                fg="white",
                width=30,
                height=2,
                command=self._install_tailscale
            ).pack(pady=5)
            
            tk.Label(
                actions_frame,
                text="Note: Installation requires administrator privileges",
                font=("Arial", 9),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['hint_fg']
            ).pack(pady=5)
        
        elif not ts_running:
            logger.info("TAILSCALE WIZARD: Creating Start button (Tailscale not running)")
            # Start Tailscale button
            tk.Button(
                actions_frame,
                text="▶️ Start Tailscale",
                font=("Arial", 13, "bold"),
                bg="#45bf55",
                fg="white",
                width=30,
                height=2,
                command=self._start_tailscale
            ).pack(pady=5)
        
        else:
            logger.info("TAILSCALE WIZARD: Creating Configure button (Tailscale running)")
            # Tailscale is running - show configuration options
            tk.Button(
                actions_frame,
                text="⚙️ Configure Remote Access",
                font=("Arial", 13, "bold"),
                bg="#45bf55",
                fg="white",
                width=30,
                height=2,
                command=self._show_tailscale_config
            ).pack(pady=5)
            
            # Show current status
            logger.info("TAILSCALE WIZARD: Displaying Tailscale info")
            self._display_tailscale_info(content)
        
        logger.info("TAILSCALE WIZARD: All widgets created successfully")
    
    def _find_tailscale_exe(self):
        """
        Find tailscale.exe on Windows by checking multiple locations.
        Returns the full path to tailscale.exe if found, None otherwise.
        Delegates to the standalone function for consistency.
        """
        return find_tailscale_exe()
    
    def _check_tailscale_installed(self):
        """Check if Tailscale is installed"""
        try:
            if platform.system() == "Windows":
                # Use enhanced detection for Windows
                tailscale_path = self._find_tailscale_exe()
                return tailscale_path is not None
            else:
                result = subprocess.run(
                    ["which", "tailscale"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0
        except Exception as e:
            print(f"Error checking Tailscale installation: {e}")
            return False
    
    def _check_tailscale_running(self):
        """Check if Tailscale is running with robust cross-platform detection"""
        try:
            system = platform.system()
            
            if system == "Windows":
                # Method 1: Check Windows service status
                try:
                    creation_flags = get_subprocess_creation_flags()
                    result = subprocess.run(
                        ['sc', 'query', 'Tailscale'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        creationflags=creation_flags
                    )
                    if result.returncode == 0 and 'RUNNING' in result.stdout:
                        return True
                    elif result.returncode == 0 and 'STOPPED' in result.stdout:
                        return False
                except Exception:
                    pass
                
                # Method 2: Check using tailscale status command
                tailscale_path = self._find_tailscale_exe()
                if tailscale_path:
                    try:
                        creation_flags = get_subprocess_creation_flags()
                        result = subprocess.run(
                            [tailscale_path, "status"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            creationflags=creation_flags
                        )
                        return result.returncode == 0
                    except Exception:
                        pass
                
                # Method 3: Check if process is running
                try:
                    creation_flags = get_subprocess_creation_flags()
                    result = subprocess.run(
                        ['tasklist', '/FI', 'IMAGENAME eq tailscaled.exe'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        creationflags=creation_flags
                    )
                    return 'tailscaled.exe' in result.stdout
                except Exception:
                    pass
                
                return False
            
            elif system == "Linux":
                # Method 1: Check systemd service status
                try:
                    result = subprocess.run(
                        ['systemctl', 'is-active', 'tailscaled'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip() == 'active':
                        return True
                except Exception:
                    pass
                
                # Method 2: Check using tailscale status command
                try:
                    result = subprocess.run(
                        ["tailscale", "status"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    return result.returncode == 0
                except Exception:
                    pass
                
                # Method 3: Check if process is running
                try:
                    result = subprocess.run(
                        ['pgrep', '-x', 'tailscaled'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    return result.returncode == 0
                except Exception:
                    pass
                
                return False
            
            elif system == "Darwin":  # macOS
                # Method 1: Check using tailscale status command
                try:
                    result = subprocess.run(
                        ["tailscale", "status"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    return result.returncode == 0
                except Exception:
                    pass
                
                # Method 2: Check if process is running
                try:
                    result = subprocess.run(
                        ['pgrep', '-x', 'tailscaled'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    return result.returncode == 0
                except Exception:
                    pass
                
                return False
            
            else:
                # Unknown system, try basic check
                try:
                    result = subprocess.run(
                        ["tailscale", "status"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    return result.returncode == 0
                except Exception:
                    return False
                    
        except Exception as e:
            logger.error(f"Error checking Tailscale status: {e}")
            return False
    
    def _install_tailscale(self):
        """Guide user through Tailscale installation"""
        system = platform.system()
        
        if system == "Windows":
            message = (
                "To install Tailscale on Windows:\n\n"
                "1. Click 'Open Download Page' below\n"
                "2. Download and run the Tailscale installer\n"
                "3. Follow the installation wizard\n"
                "4. Return here and click 'Check Installation' when done\n\n"
                "The download page will open in your browser."
            )
            url = "https://tailscale.com/download/windows"
        
        elif system == "Linux":
            message = (
                "To install Tailscale on Linux:\n\n"
                "1. Click 'Open Installation Guide' below\n"
                "2. Follow the instructions for your Linux distribution\n"
                "3. Return here and click 'Check Installation' when done\n\n"
                "Common command (for Debian/Ubuntu):\n"
                "curl -fsSL https://tailscale.com/install.sh | sh"
            )
            url = "https://tailscale.com/download/linux"
        
        elif system == "Darwin":  # macOS
            message = (
                "To install Tailscale on macOS:\n\n"
                "1. Click 'Open Download Page' below\n"
                "2. Download and install the Tailscale app\n"
                "3. Return here and click 'Check Installation' when done"
            )
            url = "https://tailscale.com/download/mac"
        
        else:
            messagebox.showerror(
                "Unsupported Platform",
                f"Automatic installation is not supported for {system}.\n"
                "Please visit https://tailscale.com/download to install manually."
            )
            return
        
        # Show installation dialog
        dialog = tk.Toplevel(self)
        dialog.title("Install Tailscale")
        dialog.geometry("500x350")
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.configure(bg=self.theme_colors['bg'])
        
        # Message
        tk.Label(
            dialog,
            text="Install Tailscale",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(20, 10))
        
        tk.Label(
            dialog,
            text=message,
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            justify=tk.LEFT,
            wraplength=450
        ).pack(pady=10, padx=20)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.theme_colors['bg'])
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Open Download Page",
            font=("Arial", 11, "bold"),
            bg="#3daee9",
            fg="white",
            command=lambda: webbrowser.open(url)
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="Check Installation",
            font=("Arial", 11, "bold"),
            bg="#45bf55",
            fg="white",
            command=lambda: [dialog.destroy(), self.show_tailscale_wizard()]
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 11),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=dialog.destroy
        ).pack(side="left", padx=10)
    
    def _start_tailscale(self):
        """Start Tailscale service"""
        try:
            system = platform.system()
            
            if system == "Windows":
                # On Windows, Tailscale service should auto-start
                # Just try to bring up the interface
                result = subprocess.run(
                    ["tailscale", "up"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif system == "Linux":
                # Try to start the systemd service
                result = subprocess.run(
                    ["sudo", "systemctl", "start", "tailscaled"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    # Service started, now bring up interface
                    result = subprocess.run(
                        ["tailscale", "up"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
            else:
                messagebox.showinfo(
                    "Manual Start Required",
                    "Please start Tailscale manually from your system tray or applications menu."
                )
                self.show_tailscale_wizard()
                return
            
            if result.returncode == 0 or "logged in" in result.stdout.lower():
                messagebox.showinfo("Success", "Tailscale started successfully!")
                self.show_tailscale_wizard()
            else:
                # User might need to authenticate
                messagebox.showinfo(
                    "Authentication Required",
                    "Tailscale needs authentication.\n\n"
                    "A browser window should open for you to log in.\n"
                    "If not, please run 'tailscale up' in your terminal."
                )
                self.show_tailscale_wizard()
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to start Tailscale: {e}\n\n"
                "Please start Tailscale manually from your system."
            )
    
    @log_page_render("TAILSCALE CONFIG")
    def _show_tailscale_config(self):
        """Show Tailscale configuration wizard"""
        logger.info("TAILSCALE CONFIG: Setting current_page to 'tailscale_config'")
        self.current_page = 'tailscale_config'
        logger.info("TAILSCALE CONFIG: Clearing existing widgets")
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        self.status_label.config(text="Configure Remote Access")
        
        # Create minimal loading indicator first so page is never blank
        logger.info("TAILSCALE CONFIG: Creating minimal loading indicator")
        loading_label = tk.Label(
            self.body_frame,
            text="Loading Configuration...",
            font=("Arial", 12),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        loading_label.pack(expand=True)
        self.update_idletasks()
        
        # Remove loading indicator and create content frame with responsive layout
        logger.info("TAILSCALE CONFIG: Creating responsive content frame")
        loading_label.destroy()
        
        # Create scrollable content frame for responsive layout
        # Use Canvas with scrollbar for proper vertical scrolling
        canvas = tk.Canvas(self.body_frame, bg=self.theme_colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.body_frame, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.theme_colors['bg'])
        
        # Configure canvas scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas with responsive layout
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas for content
        canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")
        
        # Update scroll region and canvas width when frame size changes
        def configure_canvas(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make content frame width match canvas width for centering
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:  # Only update if canvas has been rendered
                # Center content with max width of 600px
                content_width = min(600, canvas_width - 20)
                x_offset = (canvas_width - content_width) // 2
                canvas.itemconfig(canvas_window, width=content_width)
                canvas.coords(canvas_window, x_offset, 10)
        
        content.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", configure_canvas)
        
        # Add mouse wheel scrolling support for the main canvas
        def on_mouse_wheel(event):
            """Handle mouse wheel scrolling for the canvas"""
            # Windows and MacOS
            if event.num == 5 or event.delta < 0:
                canvas.yview_scroll(1, "units")
            if event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")
        
        # Bind mouse wheel events (both Windows/Mac and Linux)
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows and MacOS
        canvas.bind_all("<Button-4>", on_mouse_wheel)    # Linux scroll up
        canvas.bind_all("<Button-5>", on_mouse_wheel)    # Linux scroll down
        
        logger.info("TAILSCALE CONFIG: Content frame configured with responsive layout and mouse wheel scrolling")
        
        # Title
        logger.info("TAILSCALE CONFIG: Creating title and back button")
        tk.Label(
            content,
            text="⚙️ Configure Remote Access",
            font=("Arial", 18, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(pady=(10, 5), fill="x", padx=40)
        
        # Back button
        tk.Button(
            content,
            text="← Back to Remote Access Setup",
            font=("Arial", 11),
            command=self.show_tailscale_wizard,
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg']
        ).pack(pady=(0, 20), fill="x", padx=40)
        
        # Get Tailscale info
        logger.info("TAILSCALE CONFIG: Retrieving Tailscale network information")
        ts_ip, ts_hostname, error_message = self._get_tailscale_info()
        logger.info(f"TAILSCALE CONFIG: Retrieved - IP: {ts_ip}, Hostname: {ts_hostname}, Error: {error_message}")
        
        # Display Tailscale info
        logger.info("TAILSCALE CONFIG: Creating Tailscale info display")
        info_frame = tk.Frame(content, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
        info_frame.pack(pady=10, fill="x", padx=40)
        
        tk.Label(
            info_frame,
            text="📡 Your Tailscale Network Information",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        ).pack(pady=(15, 5), padx=15, anchor="w")
        
        if ts_ip:
            tk.Label(
                info_frame,
                text=f"Tailscale IP: {ts_ip}",
                font=("Arial", 11, "bold"),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['info_fg'],
                wraplength=480
            ).pack(pady=5, padx=15, anchor="w")
        
        if ts_hostname:
            tk.Label(
                info_frame,
                text=f"MagicDNS Name: {ts_hostname}",
                font=("Arial", 11, "bold"),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['info_fg'],
                wraplength=480
            ).pack(pady=5, padx=15, anchor="w")
        
        if error_message:
            tk.Label(
                info_frame,
                text=f"⚠️ {error_message}",
                font=("Arial", 11),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['error_fg'],
                wraplength=480,
                justify=tk.LEFT
            ).pack(pady=10, padx=15, anchor="w")
        
        if ts_ip or ts_hostname:
            tk.Label(
                info_frame,
                text="Use these addresses to access Nextcloud from any device on your Tailscale network.",
                font=("Arial", 10),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['info_fg'],
                wraplength=480,
                justify=tk.LEFT
            ).pack(pady=(5, 15), padx=15, anchor="w")
        
        # Custom domains section
        tk.Label(
            content,
            text="Custom Domains (Optional)",
            font=("Arial", 13, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            wraplength=520
        ).pack(pady=(20, 5), fill="x", padx=40)
        
        tk.Label(
            content,
            text="Add any custom domains you want to use to access Nextcloud:",
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            wraplength=520,
            justify=tk.LEFT
        ).pack(pady=(0, 10), fill="x", padx=40)
        
        # Custom domain entry
        domain_frame = tk.Frame(content, bg=self.theme_colors['bg'])
        domain_frame.pack(pady=5, fill="x", padx=40)
        
        tk.Label(
            domain_frame,
            text="Domain:",
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(side="left", padx=(0, 10))
        
        custom_domain_var = tk.StringVar()
        tk.Entry(
            domain_frame,
            textvariable=custom_domain_var,
            font=("Arial", 11),
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg'],
            insertbackground=self.theme_colors['entry_fg']
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Label(
            content,
            text="Example: mycloud.example.com",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            wraplength=520,
            justify=tk.LEFT
        ).pack(pady=(0, 15), fill="x", padx=40)
        
        # Auto-serve configuration section
        logger.info("TAILSCALE CONFIG: Creating auto-serve configuration section")
        tk.Label(
            content,
            text="Automatic Tailscale Serve (Optional)",
            font=("Arial", 13, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            wraplength=520
        ).pack(pady=(20, 5), fill="x", padx=40)
        
        # Detect Nextcloud port
        detected_port = get_nextcloud_port()
        port_info_text = f"Detected Nextcloud port: {detected_port}" if detected_port else "No Nextcloud port detected"
        
        tk.Label(
            content,
            text=port_info_text,
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            wraplength=520,
            justify=tk.LEFT
        ).pack(pady=(0, 5), fill="x", padx=40)
        
        tk.Label(
            content,
            text="Enable automatic 'tailscale serve' at system startup to make Nextcloud accessible via HTTPS on your Tailscale network.",
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg'],
            wraplength=520,
            justify=tk.LEFT
        ).pack(pady=(0, 10), fill="x", padx=40)
        
        # Auto-serve checkbox (checked by default)
        auto_serve_var = tk.BooleanVar(value=True)
        auto_serve_check = tk.Checkbutton(
            content,
            text="Enable automatic Tailscale serve at startup",
            variable=auto_serve_var,
            font=("Arial", 11),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg'],
            selectcolor=self.theme_colors['entry_bg'],
            activebackground=self.theme_colors['bg'],
            activeforeground=self.theme_colors['fg'],
            wraplength=520,
            justify=tk.LEFT
        )
        auto_serve_check.pack(pady=5, fill="x", padx=40, anchor="w")
        
        # Port override entry (in case auto-detection fails)
        port_override_frame = tk.Frame(content, bg=self.theme_colors['bg'])
        port_override_frame.pack(pady=5, fill="x", padx=40)
        
        tk.Label(
            port_override_frame,
            text="Port (override):",
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(side="left", padx=(0, 10))
        
        port_override_var = tk.StringVar(value=str(detected_port) if detected_port else "")
        tk.Entry(
            port_override_frame,
            textvariable=port_override_var,
            font=("Arial", 10),
            bg=self.theme_colors['entry_bg'],
            fg=self.theme_colors['entry_fg'],
            insertbackground=self.theme_colors['entry_fg'],
            width=10
        ).pack(side="left", padx=(0, 5))
        
        tk.Label(
            port_override_frame,
            text="(leave empty to use detected port)",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(side="left", padx=(10, 0))
        
        # Action buttons
        tk.Button(
            content,
            text="✓ Apply Configuration to Nextcloud",
            font=("Arial", 13, "bold"),
            bg="#45bf55",
            fg="white",
            width=35,
            height=2,
            command=lambda: self._apply_tailscale_config(
                ts_ip, ts_hostname, custom_domain_var.get(),
                auto_serve_var.get(), port_override_var.get()
            )
        ).pack(pady=20, fill="x", padx=40)
        
        # Startup automation button (for Linux systems)
        if platform.system() == "Linux":
            tk.Button(
                content,
                text="⚡ Setup Startup Automation",
                font=("Arial", 11),
                bg="#3daee9",
                fg="white",
                width=35,
                height=1,
                command=self._show_startup_automation_guide
            ).pack(pady=(0, 20), fill="x", padx=40)
        
        # Info about what will be configured
        info_box = tk.Frame(content, bg=self.theme_colors['warning_bg'], relief="solid", borderwidth=1)
        info_box.pack(pady=10, fill="x", padx=40)
        
        tk.Label(
            info_box,
            text="ℹ️ What will be configured:",
            font=("Arial", 11, "bold"),
            bg=self.theme_colors['warning_bg'],
            fg=self.theme_colors['warning_fg']
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        config_items = []
        if ts_ip:
            config_items.append(f"• Tailscale IP: {ts_ip}")
        if ts_hostname:
            config_items.append(f"• MagicDNS name: {ts_hostname}")
        if custom_domain_var.get():
            config_items.append(f"• Custom domain: {custom_domain_var.get()}")
        
        if not config_items:
            config_items = ["• No domains will be added (check your Tailscale setup)"]
        
        config_text = "These addresses will be added to Nextcloud's trusted_domains:\n" + "\n".join(config_items)
        
        tk.Label(
            info_box,
            text=config_text,
            font=("Arial", 10),
            bg=self.theme_colors['warning_bg'],
            fg=self.theme_colors['warning_fg'],
            justify=tk.LEFT
        ).pack(pady=(0, 10), padx=10, anchor="w")
        
        # Display current trusted domains section
        logger.info("TAILSCALE CONFIG: Displaying current trusted domains")
        self._display_current_trusted_domains(content)
        
        logger.info("TAILSCALE CONFIG: All widgets created successfully")
    
    def _display_current_trusted_domains(self, parent):
        """Display all current trusted domains with enhanced management features"""
        # Get Nextcloud container
        container_names = get_nextcloud_container_name()
        if not container_names:
            return
        
        nextcloud_container = container_names
        
        # Get current trusted domains
        current_domains = self._get_trusted_domains(nextcloud_container)
        
        # Section title with help icon
        title_frame = tk.Frame(parent, bg=self.theme_colors['bg'])
        title_frame.pack(pady=(30, 10), fill="x", padx=20)
        
        tk.Label(
            title_frame,
            text="Current Trusted Domains",
            font=("Arial", 13, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        ).pack(side="left")
        
        # Help tooltip button
        help_btn = tk.Button(
            title_frame,
            text="ℹ️",
            font=("Arial", 10),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            width=2,
            command=self._show_domain_help
        )
        help_btn.pack(side="left", padx=10)
        
        tk.Label(
            parent,
            text="These domains are currently configured for Nextcloud access:",
            font=("Arial", 10),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        ).pack(pady=(0, 10), anchor="w", padx=20)
        
        # Management controls frame
        controls_frame = tk.Frame(parent, bg=self.theme_colors['bg'])
        controls_frame.pack(pady=(0, 10), fill="x", padx=20)
        
        # Refresh status button
        tk.Button(
            controls_frame,
            text="🔄 Refresh Status",
            font=("Arial", 9),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=lambda: self._refresh_domain_status(parent)
        ).pack(side="left", padx=(0, 5))
        
        # Restore defaults button
        if self.original_domains:
            tk.Button(
                controls_frame,
                text="↺ Restore Defaults",
                font=("Arial", 9),
                bg=self.theme_colors['button_bg'],
                fg=self.theme_colors['button_fg'],
                command=lambda: self._on_restore_defaults(parent)
            ).pack(side="left", padx=5)
        
        # Undo button
        if self.domain_change_history:
            tk.Button(
                controls_frame,
                text="↶ Undo Last Change",
                font=("Arial", 9),
                bg=self.theme_colors['button_bg'],
                fg=self.theme_colors['button_fg'],
                command=lambda: self._on_undo_change(parent)
            ).pack(side="left", padx=5)
        
        # Check if there are domains to display
        if not current_domains:
            # Display "No trusted domains configured" message
            no_domains_frame = tk.Frame(parent, bg=self.theme_colors['warning_bg'], relief="solid", borderwidth=1)
            no_domains_frame.pack(pady=10, fill="x", padx=20)
            
            tk.Label(
                no_domains_frame,
                text="No trusted domains configured",
                font=("Arial", 12, "bold"),
                bg=self.theme_colors['warning_bg'],
                fg=self.theme_colors['warning_fg']
            ).pack(pady=15, padx=10)
            
            tk.Label(
                no_domains_frame,
                text="Add domains using the form below to allow access to your Nextcloud instance.",
                font=("Arial", 10),
                bg=self.theme_colors['warning_bg'],
                fg=self.theme_colors['warning_fg'],
                wraplength=540
            ).pack(pady=(0, 15), padx=10)
        else:
            # Scrollable domains list frame with canvas
            list_container = tk.Frame(parent, bg=self.theme_colors['bg'])
            list_container.pack(pady=5, fill="both", expand=True, padx=20)
            
            # Create canvas and scrollbar
            canvas = tk.Canvas(
                list_container,
                bg=self.theme_colors['bg'],
                height=min(300, len(current_domains) * 50),  # Max height 300px
                highlightthickness=0
            )
            scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
            domains_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
            
            # Configure canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack scrollbar and canvas
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Create window in canvas
            canvas_window = canvas.create_window((0, 0), window=domains_frame, anchor="nw")
            
            # Update scroll region and canvas width when frame size changes
            def configure_scroll_region(event=None):
                canvas.configure(scrollregion=canvas.bbox("all"))
                # Make canvas window width match canvas width
                canvas_width = canvas.winfo_width()
                if canvas_width > 1:  # Only update if canvas has been rendered
                    canvas.itemconfig(canvas_window, width=canvas_width)
            
            domains_frame.bind("<Configure>", configure_scroll_region)
            canvas.bind("<Configure>", configure_scroll_region)
            
            # Add mouse wheel scrolling support for the domain list canvas
            def on_domain_mouse_wheel(event):
                """Handle mouse wheel scrolling for the domain list canvas"""
                # Windows and MacOS
                if event.num == 5 or event.delta < 0:
                    canvas.yview_scroll(1, "units")
                if event.num == 4 or event.delta > 0:
                    canvas.yview_scroll(-1, "units")
            
            # Bind mouse wheel events for domain list
            canvas.bind("<MouseWheel>", on_domain_mouse_wheel)  # Windows and MacOS
            canvas.bind("<Button-4>", on_domain_mouse_wheel)    # Linux scroll up
            canvas.bind("<Button-5>", on_domain_mouse_wheel)    # Linux scroll down
            
            # Display each domain with status icon and remove button
            for domain in current_domains:
                domain_row = tk.Frame(domains_frame, bg=self.theme_colors['entry_bg'], relief="solid", borderwidth=1)
                domain_row.pack(pady=3, fill="x", padx=2)
                
                # Check domain status
                status = self._check_domain_reachability(domain)
                
                # Status icon
                status_icons = {
                    'active': '✓',
                    'unreachable': '⚠️',
                    'pending': '⏳',
                    'error': '❌'
                }
                status_colors = {
                    'active': '#45bf55',
                    'unreachable': '#ff9800',
                    'pending': '#2196f3',
                    'error': '#f44336'
                }
                
                status_label = tk.Label(
                    domain_row,
                    text=status_icons.get(status, '?'),
                    font=("Arial", 12),
                    bg=self.theme_colors['entry_bg'],
                    fg=status_colors.get(status, self.theme_colors['entry_fg']),
                    width=2
                )
                status_label.pack(side="left", padx=(5, 0), pady=8)
                
                # Domain label with tooltip on hover
                domain_label = tk.Label(
                    domain_row,
                    text=domain,
                    font=("Arial", 11),
                    bg=self.theme_colors['entry_bg'],
                    fg=self.theme_colors['entry_fg'],
                    anchor="w"
                )
                domain_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)
                
                # Add tooltip
                self._create_tooltip(domain_label, self._get_domain_tooltip(domain, status))
                
                # Remove button
                remove_btn = tk.Button(
                    domain_row,
                    text="✕",
                    font=("Arial", 12, "bold"),
                    bg=self.theme_colors['error_bg'] if hasattr(self.theme_colors, '__getitem__') and 'error_bg' in self.theme_colors else "#ff6b6b",
                    fg="white",
                    width=3,
                    height=1,
                    command=lambda d=domain: self._on_remove_domain(d, parent)
                )
                remove_btn.pack(side="right", padx=5, pady=5)
        
        # Info note with legend
        info_note = tk.Frame(parent, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
        info_note.pack(pady=10, fill="x", padx=20)
        
        info_text = (
            "💡 Status Icons: ✓ Active | ⚠️ Unreachable | ⏳ Pending | ❌ Error\n\n"
            "• Click ✕ to remove a domain (with confirmation)\n"
            "• Use the \"Custom Domains (Optional)\" section at the top to add new domains\n"
            "• Changes are logged and can be undone\n"
            "• Hover over domains for more information"
        )
        
        tk.Label(
            info_note,
            text=info_text,
            font=("Arial", 9),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg'],
            wraplength=540,
            justify=tk.LEFT
        ).pack(pady=8, padx=10, anchor="w")
    
    def _on_add_domain(self, domain, parent_frame, validation_label):
        """Handle adding a new domain"""
        domain = domain.strip()
        
        if not domain:
            validation_label.config(
                text="✗ Please enter a domain",
                fg=self.theme_colors['error_fg']
            )
            return
        
        # Get Nextcloud container
        container_names = get_nextcloud_container_name()
        if not container_names:
            messagebox.showerror(
                "Error",
                "No running Nextcloud container found.\n\n"
                "Please ensure your Nextcloud instance is running."
            )
            return
        
        nextcloud_container = container_names
        
        # Add the domain
        success, msg = self._add_trusted_domain(nextcloud_container, domain)
        
        if success:
            if msg:  # Has warning
                messagebox.showinfo(
                    "Success",
                    f"✓ Domain added successfully!\n\n"
                    f"Added: {domain}\n\n"
                    f"Note: {msg}\n\n"
                    f"The configuration will refresh now."
                )
            else:
                messagebox.showinfo(
                    "Success",
                    f"✓ Domain added successfully!\n\n"
                    f"Added: {domain}\n\n"
                    f"The configuration will refresh now."
                )
            # Refresh the page to show updated list
            self._show_tailscale_config()
        else:
            messagebox.showerror(
                "Error",
                f"Failed to add domain: {domain}\n\n"
                f"Reason: {msg}"
            )
    
    def _on_remove_domain(self, domain, parent_frame):
        """Handle domain removal"""
        # Confirm removal
        confirm = messagebox.askyesno(
            "Remove Trusted Domain",
            f"Are you sure you want to remove this domain from trusted domains?\n\n"
            f"Domain: {domain}\n\n"
            f"Note: Removing this domain will prevent access to Nextcloud from this address."
        )
        
        if not confirm:
            return
        
        # Get Nextcloud container
        container_names = get_nextcloud_container_name()
        if not container_names:
            messagebox.showerror(
                "Error",
                "No running Nextcloud container found.\n\n"
                "Please ensure your Nextcloud instance is running."
            )
            return
        
        nextcloud_container = container_names
        
        # Remove the domain
        success = self._remove_trusted_domain(nextcloud_container, domain)
        
        if success:
            messagebox.showinfo(
                "Success",
                f"✓ Domain removed successfully!\n\n"
                f"Removed: {domain}\n\n"
                f"The configuration will refresh now."
            )
            # Refresh the page to show updated list
            self._show_tailscale_config()
        else:
            messagebox.showerror(
                "Error",
                f"Failed to remove domain: {domain}\n\n"
                "Please check that the Nextcloud container is running\n"
                "and you have the necessary permissions."
            )
    
    def _on_undo_change(self, parent_frame):
        """Handle undo of last domain change"""
        # Get Nextcloud container
        container_names = get_nextcloud_container_name()
        if not container_names:
            messagebox.showerror(
                "Error",
                "No running Nextcloud container found.\n\n"
                "Please ensure your Nextcloud instance is running."
            )
            return
        
        nextcloud_container = container_names
        
        # Undo last change
        success, msg = self._undo_last_domain_change(nextcloud_container)
        
        if success:
            messagebox.showinfo(
                "Success",
                f"✓ {msg}\n\n"
                f"The configuration will refresh now."
            )
            # Refresh the page
            self._show_tailscale_config()
        else:
            messagebox.showerror(
                "Error",
                f"Failed to undo change.\n\n"
                f"Reason: {msg}"
            )
    
    def _on_restore_defaults(self, parent_frame):
        """Handle restore defaults"""
        # Get Nextcloud container
        container_names = get_nextcloud_container_name()
        if not container_names:
            messagebox.showerror(
                "Error",
                "No running Nextcloud container found.\n\n"
                "Please ensure your Nextcloud instance is running."
            )
            return
        
        nextcloud_container = container_names
        
        # Restore defaults
        success, msg = self._restore_default_domains(nextcloud_container)
        
        if success:
            messagebox.showinfo(
                "Success",
                f"✓ {msg}\n\n"
                f"The configuration will refresh now."
            )
            # Refresh the page
            self._show_tailscale_config()
        else:
            if msg != "Restore cancelled":
                messagebox.showerror(
                    "Error",
                    f"Failed to restore defaults.\n\n"
                    f"Reason: {msg}"
                )
    
    def _refresh_domain_status(self, parent_frame):
        """Refresh domain status by clearing cache and reloading"""
        # Clear status cache
        self.domain_status_cache.clear()
        logger.info("Domain status cache cleared")
        
        # Show brief notification
        messagebox.showinfo(
            "Refresh Status",
            "✓ Domain status cache cleared.\n\n"
            "The page will refresh to show updated status."
        )
        
        # Refresh the page
        self._show_tailscale_config()
    
    def _show_domain_help(self):
        """Show help information about domain management"""
        help_text = """
Domain Management Help

Types of Domains:
• Tailscale IP: Direct IP address (e.g., 100.x.x.x)
• MagicDNS: Tailscale hostname (e.g., device-name.tailnet.ts.net)
• Custom Domain: Your own domain (e.g., mycloud.example.com)
• Wildcard Domain: Matches subdomains (e.g., *.example.com)

Status Icons:
• ✓ Active: Domain is reachable
• ⚠️ Unreachable: Domain cannot be resolved
• ⏳ Pending: Status check in progress
• ❌ Error: Error checking domain status

Features:
• Add Domain: Enter a domain and click Add
• Remove Domain: Click ✕ next to a domain
• Restore Defaults: Revert to original domains
• Undo: Revert the last change
• Refresh Status: Update domain reachability status

Validation:
• Domains are validated before adding
• Duplicates are prevented
• Wildcard domains are supported with warnings
• Removing all domains requires confirmation

All changes are logged for troubleshooting and audit purposes.
"""
        
        messagebox.showinfo("Domain Management Help", help_text)
    
    def _get_domain_tooltip(self, domain, status):
        """Get tooltip text for a domain"""
        status_text = {
            'active': 'Active - Domain is reachable',
            'unreachable': 'Unreachable - Domain cannot be resolved',
            'pending': 'Pending - Status check in progress',
            'error': 'Error - Error checking domain status'
        }
        
        tooltip = f"Domain: {domain}\nStatus: {status_text.get(status, 'Unknown')}"
        
        # Add domain type info
        if domain.startswith('100.'):
            tooltip += "\nType: Tailscale IP"
        elif '.ts.net' in domain:
            tooltip += "\nType: Tailscale MagicDNS"
        elif domain.startswith('*.'):
            tooltip += "\nType: Wildcard Domain"
        elif domain == 'localhost' or domain.startswith('127.'):
            tooltip += "\nType: Local"
        else:
            tooltip += "\nType: Custom Domain"
        
        return tooltip
    
    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                justify=tk.LEFT,
                background=self.theme_colors['info_bg'],
                foreground=self.theme_colors['info_fg'],
                relief=tk.SOLID,
                borderwidth=1,
                font=("Arial", 9),
                padx=10,
                pady=5
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _show_startup_automation_guide(self):
        """Show startup automation installation guide"""
        guide_text = """
Startup Automation Setup

This feature ensures your Tailscale domains are automatically added to
Nextcloud's trusted domains when your system boots.

Installation Steps (Linux only):

1. Open a terminal and navigate to this application's directory

2. Copy the startup script:
   sudo cp nextcloud-remote-access-startup.sh /usr/local/bin/
   sudo chmod +x /usr/local/bin/nextcloud-remote-access-startup.sh

3. Install the systemd service:
   sudo cp nextcloud-remote-access.service /etc/systemd/system/

4. Enable the service:
   sudo systemctl daemon-reload
   sudo systemctl enable nextcloud-remote-access.service

5. Start the service:
   sudo systemctl start nextcloud-remote-access.service

6. Check status:
   sudo systemctl status nextcloud-remote-access.service

For detailed instructions and troubleshooting, see:
REMOTE_ACCESS_STARTUP_GUIDE.md

Benefits:
✓ Domains applied automatically on system boot
✓ Always accessible via Tailscale after restarts
✓ Supports custom domains via configuration file
✓ Logged for troubleshooting

Would you like to open the detailed guide?
"""
        
        response = messagebox.askyesnocancel(
            "Startup Automation Setup",
            guide_text
        )
        
        if response:  # Yes - open the guide
            guide_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "REMOTE_ACCESS_STARTUP_GUIDE.md")
            if os.path.exists(guide_path):
                try:
                    if platform.system() == "Linux":
                        subprocess.run(["xdg-open", guide_path])
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", guide_path])
                    else:
                        webbrowser.open(f"file://{guide_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open guide: {e}")
            else:
                messagebox.showwarning("Guide Not Found", "The guide file could not be found.")
        elif response is False:  # No - just close
            pass
        # Cancel - do nothing
    
    def _get_tailscale_info(self):
        """
        Get Tailscale IP and hostname with detailed error information.
        
        Returns:
            tuple: (ts_ip, ts_hostname, error_message)
                - ts_ip: Tailscale IP address or None
                - ts_hostname: Tailscale hostname or None
                - error_message: Detailed error message or None if successful
        """
        ts_ip = None
        ts_hostname = None
        error_message = None
        
        try:
            # Get Tailscale executable path
            if platform.system() == "Windows":
                tailscale_path = self._find_tailscale_exe()
                if not tailscale_path:
                    return None, None, "Tailscale CLI not found. Please ensure Tailscale is installed and in your PATH."
                tailscale_cmd = tailscale_path
            else:
                # Use shutil.which() to reliably locate the executable
                tailscale_cmd = shutil.which("tailscale")
                if not tailscale_cmd:
                    return None, None, "Tailscale CLI not found. Please ensure Tailscale is installed and in your PATH."
            
            # Get Tailscale status with increased timeout
            try:
                result = subprocess.run(
                    [tailscale_cmd, "status", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
            except subprocess.TimeoutExpired:
                error_msg = "Tailscale command timed out. The service may be unresponsive."
                logger.error(error_msg)
                return None, None, error_msg
            
            if result.returncode != 0:
                # Log and return full error output
                stderr_output = result.stderr.strip()
                logger.error(f"Tailscale command failed with code {result.returncode}: {stderr_output}")
                
                # Parse stderr for specific errors
                stderr_lower = result.stderr.lower()
                if "not running" in stderr_lower or "stopped" in stderr_lower:
                    return None, None, "Tailscale service is not running. Please start Tailscale."
                elif "permission denied" in stderr_lower or "access denied" in stderr_lower:
                    return None, None, "Permission denied. Try running with administrator/sudo privileges."
                elif "not logged in" in stderr_lower or "logged out" in stderr_lower:
                    return None, None, "Tailscale is not logged in. Please login to Tailscale first."
                else:
                    return None, None, f"Tailscale command failed: {stderr_output or 'Unknown error'}"
            
            # Parse JSON output
            try:
                status_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse Tailscale status JSON: {str(e)}"
                logger.error(error_msg)
                return None, None, error_msg
            
            # Get self info
            if 'Self' in status_data:
                self_data = status_data['Self']
                
                # Get Tailscale IP
                if 'TailscaleIPs' in self_data and self_data['TailscaleIPs']:
                    ts_ip = self_data['TailscaleIPs'][0]
                
                # Get hostname
                if 'DNSName' in self_data:
                    ts_hostname = self_data['DNSName'].rstrip('.')
                
                # Check if we got any data
                if not ts_ip and not ts_hostname:
                    return None, None, "Tailscale is running but no network information available. Ensure Tailscale is connected."
            else:
                return None, None, "Tailscale status response missing 'Self' information."
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Error getting Tailscale info: {e}")
            return None, None, error_msg
        
        return ts_ip, ts_hostname, None
    
    def _display_tailscale_info(self, parent):
        """Display current Tailscale network information"""
        ts_ip, ts_hostname, error_message = self._get_tailscale_info()
        
        if ts_ip or ts_hostname or error_message:
            info_frame = tk.Frame(parent, bg=self.theme_colors['info_bg'], relief="solid", borderwidth=1)
            info_frame.pack(pady=15, fill="x", padx=20)
            
            tk.Label(
                info_frame,
                text="📡 Current Tailscale Network Info",
                font=("Arial", 11, "bold"),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['info_fg']
            ).pack(pady=(10, 5), padx=10, anchor="w")
            
            if ts_ip:
                tk.Label(
                    info_frame,
                    text=f"IP Address: {ts_ip}",
                    font=("Arial", 10),
                    bg=self.theme_colors['info_bg'],
                    fg=self.theme_colors['info_fg'],
                    wraplength=520
                ).pack(pady=2, padx=20, anchor="w")
            
            if ts_hostname:
                tk.Label(
                    info_frame,
                    text=f"Hostname: {ts_hostname}",
                    font=("Arial", 10),
                    bg=self.theme_colors['info_bg'],
                    fg=self.theme_colors['info_fg'],
                    wraplength=520
                ).pack(pady=2, padx=20, anchor="w")
            
            if error_message:
                tk.Label(
                    info_frame,
                    text=f"⚠️ {error_message}",
                    font=("Arial", 10),
                    bg=self.theme_colors['info_bg'],
                    fg=self.theme_colors['error_fg'],
                    wraplength=520,
                    justify=tk.LEFT
                ).pack(pady=5, padx=20, anchor="w")
            
            tk.Label(
                info_frame,
                text="",
                bg=self.theme_colors['info_bg']
            ).pack(pady=5)
    
    def _apply_tailscale_config(self, ts_ip, ts_hostname, custom_domain, enable_auto_serve=False, port_override=""):
        """Apply Tailscale configuration to Nextcloud"""
        # Get Nextcloud container
        container_names = get_nextcloud_container_name()
        if not container_names:
            messagebox.showerror(
                "Error",
                "No running Nextcloud container found.\n\n"
                "Please ensure your Nextcloud instance is running."
            )
            return
        
        nextcloud_container = container_names
        
        # Collect domains to add
        domains_to_add = []
        if ts_ip:
            domains_to_add.append(ts_ip)
        if ts_hostname:
            domains_to_add.append(ts_hostname)
        if custom_domain and custom_domain.strip():
            domains_to_add.append(custom_domain.strip())
        
        if not domains_to_add:
            messagebox.showwarning(
                "No Domains",
                "No domains to add to Nextcloud configuration."
            )
            return
        
        # Update trusted_domains in config.php
        try:
            self.status_label.config(text="Updating Nextcloud configuration...")
            self.update_idletasks()
            
            success = self._update_trusted_domains(nextcloud_container, domains_to_add)
            
            # Handle auto-serve setup if requested
            auto_serve_status = ""
            if enable_auto_serve:
                # Determine port to use
                if port_override and port_override.strip().isdigit():
                    serve_port = int(port_override.strip())
                else:
                    serve_port = get_nextcloud_port()
                
                if serve_port:
                    self.status_label.config(text="Setting up automatic Tailscale serve...")
                    self.update_idletasks()
                    
                    serve_success, serve_message = setup_tailscale_serve_startup(serve_port, enable=True)
                    auto_serve_status = f"\n\nAuto-serve setup: {serve_message}"
                else:
                    auto_serve_status = "\n\nAuto-serve setup: Failed - Could not detect Nextcloud port. Please configure manually."
            
            if success:
                messagebox.showinfo(
                    "Success",
                    f"✓ Remote access configured successfully!\n\n"
                    f"Added to trusted domains:\n" + "\n".join(f"  • {d}" for d in domains_to_add) + "\n\n"
                    f"You can now access Nextcloud using these addresses from any device\n"
                    f"connected to your Tailscale network."
                    f"{auto_serve_status}"
                )
                self.show_landing()
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to update Nextcloud configuration.\n\n"
                    "Please check that the Nextcloud container is running\n"
                    "and you have the necessary permissions."
                )
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply configuration: {e}")
    
    def _validate_domain_format(self, domain):
        """
        Validate domain format with comprehensive checks.
        Returns: (is_valid, error_message)
        """
        if not domain or not domain.strip():
            return (False, "Domain cannot be empty")
        
        domain = domain.strip()
        
        # Check for wildcard domains
        is_wildcard = domain.startswith('*.')
        if is_wildcard:
            domain_to_check = domain[2:]  # Remove *. prefix
        else:
            domain_to_check = domain
        
        # Basic format validation
        # Allow localhost, IP addresses, and domain names
        if domain_to_check == 'localhost':
            return (True, None)
        
        # Check if it's an IP address (IPv4 or IPv6)
        ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ipv4_pattern, domain_to_check):
            if is_wildcard:
                return (False, "Wildcard domains are not valid for IP addresses")
            return (True, None)
        
        # Check for IPv6 (simple check)
        if ':' in domain_to_check and '[' not in domain_to_check:
            if is_wildcard:
                return (False, "Wildcard domains are not valid for IPv6 addresses")
            return (True, None)
        
        # Domain name validation
        domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
        if not re.match(domain_pattern, domain_to_check):
            return (False, "Invalid domain format. Use format like: example.com or subdomain.example.com")
        
        # Check for port specification
        if ':' in domain_to_check and not domain_to_check.count(':') > 1:  # Not IPv6
            parts = domain_to_check.rsplit(':', 1)
            try:
                port = int(parts[1])
                if port < 1 or port > 65535:
                    return (False, "Invalid port number")
            except ValueError:
                return (False, "Invalid port specification")
        
        return (True, "Wildcard domain" if is_wildcard else None)
    
    def _check_domain_reachability(self, domain):
        """
        Check if a domain is reachable (non-blocking check).
        Returns: ('active', 'unreachable', 'pending', 'error')
        """
        # Check cache first
        if domain in self.domain_status_cache:
            cached_time, status = self.domain_status_cache[domain]
            # Cache valid for 5 minutes
            if time.time() - cached_time < 300:
                return status
        
        try:
            # Quick DNS resolution check (timeout 2 seconds)
            import socket
            socket.setdefaulttimeout(2)
            
            # Extract domain without port
            check_domain = domain
            if ':' in domain and not domain.startswith('['):
                check_domain = domain.rsplit(':', 1)[0]
            
            # Skip validation for special cases
            if check_domain in ['localhost', '127.0.0.1', '::1']:
                status = 'active'
            elif check_domain.startswith('100.'):  # Tailscale IP range
                status = 'active'
            elif check_domain.startswith('*.'):  # Wildcard
                status = 'active'  # Can't validate wildcards
            else:
                # Try to resolve the domain
                try:
                    socket.gethostbyname(check_domain)
                    status = 'active'
                except socket.gaierror:
                    status = 'unreachable'
            
            # Cache the result
            self.domain_status_cache[domain] = (time.time(), status)
            return status
            
        except Exception as e:
            logger.warning(f"Error checking domain reachability for {domain}: {e}")
            return 'error'
    
    def _get_trusted_domains(self, container_name):
        """Get list of current trusted domains from Nextcloud config.php"""
        try:
            # Read current config.php
            result = subprocess.run(
                ["docker", "exec", container_name, "cat", "/var/www/html/config/config.php"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"Failed to read config.php: {result.stderr}")
                return []
            
            config_content = result.stdout
            
            # Parse trusted_domains array
            trusted_domains_pattern = r"'trusted_domains'\s*=>\s*array\s*\((.*?)\),"
            match = re.search(trusted_domains_pattern, config_content, re.DOTALL)
            
            if not match:
                print("Could not find trusted_domains in config.php")
                return []
            
            # Extract existing domains
            existing_domains_str = match.group(1)
            existing_domains = []
            
            # Parse existing domain entries
            domain_pattern = r"\d+\s*=>\s*'([^']+)'"
            for domain_match in re.finditer(domain_pattern, existing_domains_str):
                existing_domains.append(domain_match.group(1))
            
            # Store original domains if not yet stored
            if self.original_domains is None and existing_domains:
                self.original_domains = existing_domains.copy()
                logger.info(f"Stored original domains: {self.original_domains}")
            
            return existing_domains
        
        except Exception as e:
            print(f"Error getting trusted_domains: {e}")
            return []
    
    def _add_trusted_domain(self, container_name, domain_to_add):
        """
        Add a specific domain to trusted_domains in Nextcloud config.php.
        Returns: (success, error_message)
        """
        try:
            # Validate domain format first
            is_valid, validation_msg = self._validate_domain_format(domain_to_add)
            if not is_valid:
                return (False, validation_msg)
            
            # Get current domains
            current_domains = self._get_trusted_domains(container_name)
            
            # Check for duplicates
            if domain_to_add in current_domains:
                return (False, "Domain already exists in trusted domains")
            
            # Log the change for audit and undo
            change_record = {
                'timestamp': datetime.now().isoformat(),
                'action': 'add',
                'domain': domain_to_add,
                'previous_domains': current_domains.copy()
            }
            self.domain_change_history.append(change_record)
            logger.info(f"Domain change recorded: {change_record}")
            
            # Add the domain
            new_domains = current_domains + [domain_to_add]
            success = self._set_trusted_domains(container_name, new_domains)
            
            if success:
                # Check reachability if it's a warning about wildcard
                if validation_msg:
                    return (True, f"Domain added with warning: {validation_msg}")
                return (True, None)
            else:
                # Remove from history if failed
                self.domain_change_history.pop()
                return (False, "Failed to update config.php")
        
        except Exception as e:
            logger.error(f"Error adding trusted domain: {e}")
            return (False, f"Error: {str(e)}")
    
    def _remove_trusted_domain(self, container_name, domain_to_remove):
        """Remove a specific domain from trusted_domains in Nextcloud config.php"""
        try:
            # Get current domains
            current_domains = self._get_trusted_domains(container_name)
            
            # Check if this is the last domain
            if len(current_domains) <= 1:
                # Warn about removing all domains
                confirm = messagebox.askyesno(
                    "Warning: Removing Last Domain",
                    "⚠️ WARNING: You are about to remove the last trusted domain!\n\n"
                    "This will prevent ALL access to Nextcloud through the web interface.\n"
                    "You will be locked out and need to manually fix the config.php file.\n\n"
                    "Are you ABSOLUTELY SURE you want to continue?",
                    icon='warning'
                )
                if not confirm:
                    return False
            
            # Log the change for audit and undo
            change_record = {
                'timestamp': datetime.now().isoformat(),
                'action': 'remove',
                'domain': domain_to_remove,
                'previous_domains': current_domains.copy()
            }
            self.domain_change_history.append(change_record)
            logger.info(f"Domain change recorded: {change_record}")
            
            # Read current config.php
            result = subprocess.run(
                ["docker", "exec", container_name, "cat", "/var/www/html/config/config.php"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"Failed to read config.php: {result.stderr}")
                self.domain_change_history.pop()  # Remove from history
                return False
            
            config_content = result.stdout
            
            # Parse trusted_domains array
            trusted_domains_pattern = r"'trusted_domains'\s*=>\s*array\s*\((.*?)\),"
            match = re.search(trusted_domains_pattern, config_content, re.DOTALL)
            
            if not match:
                print("Could not find trusted_domains in config.php")
                self.domain_change_history.pop()  # Remove from history
                return False
            
            # Extract existing domains
            existing_domains_str = match.group(1)
            existing_domains = []
            
            # Parse existing domain entries
            domain_pattern = r"\d+\s*=>\s*'([^']+)'"
            for domain_match in re.finditer(domain_pattern, existing_domains_str):
                domain = domain_match.group(1)
                if domain != domain_to_remove:
                    existing_domains.append(domain)
            
            # Build new trusted_domains array
            new_domains_array = "array(\n"
            for i, domain in enumerate(existing_domains):
                new_domains_array += f"    {i} => '{domain}',\n"
            new_domains_array += "  )"
            
            # Replace in config
            new_config = re.sub(
                trusted_domains_pattern,
                f"'trusted_domains' => {new_domains_array},",
                config_content,
                count=1,
                flags=re.DOTALL
            )
            
            # Write back to container
            write_cmd = f"cat > /var/www/html/config/config.php << 'EOFCONFIG'\n{new_config}\nEOFCONFIG"
            
            result = subprocess.run(
                ["docker", "exec", container_name, "sh", "-c", write_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"Failed to write config.php: {result.stderr}")
                self.domain_change_history.pop()  # Remove from history
                return False
            
            print(f"✓ Removed domain from trusted_domains: {domain_to_remove}")
            logger.info(f"✓ Removed domain from trusted_domains: {domain_to_remove}")
            return True
        
        except Exception as e:
            print(f"Error removing trusted domain: {e}")
            logger.error(f"Error removing trusted domain: {e}")
            return False
    
    def _set_trusted_domains(self, container_name, domains_list):
        """
        Set the complete list of trusted domains in Nextcloud config.php.
        This replaces all existing domains with the provided list.
        Returns: True on success, False on failure
        """
        try:
            # Read current config.php
            result = subprocess.run(
                ["docker", "exec", container_name, "cat", "/var/www/html/config/config.php"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"Failed to read config.php: {result.stderr}")
                return False
            
            config_content = result.stdout
            
            # Parse trusted_domains array
            trusted_domains_pattern = r"'trusted_domains'\s*=>\s*array\s*\((.*?)\),"
            match = re.search(trusted_domains_pattern, config_content, re.DOTALL)
            
            if not match:
                print("Could not find trusted_domains in config.php")
                return False
            
            # Build new trusted_domains array
            new_domains_array = "array(\n"
            for i, domain in enumerate(domains_list):
                new_domains_array += f"    {i} => '{domain}',\n"
            new_domains_array += "  )"
            
            # Replace in config
            new_config = re.sub(
                trusted_domains_pattern,
                f"'trusted_domains' => {new_domains_array},",
                config_content,
                count=1,
                flags=re.DOTALL
            )
            
            # Write back to container
            write_cmd = f"cat > /var/www/html/config/config.php << 'EOFCONFIG'\n{new_config}\nEOFCONFIG"
            
            result = subprocess.run(
                ["docker", "exec", container_name, "sh", "-c", write_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"Failed to write config.php: {result.stderr}")
                return False
            
            print(f"✓ Updated trusted_domains")
            logger.info(f"✓ Updated trusted_domains: {domains_list}")
            return True
        
        except Exception as e:
            print(f"Error setting trusted domains: {e}")
            logger.error(f"Error setting trusted domains: {e}")
            return False
    
    def _undo_last_domain_change(self, container_name):
        """
        Undo the last domain change.
        Returns: (success, message)
        """
        if not self.domain_change_history:
            return (False, "No changes to undo")
        
        try:
            # Get the last change
            last_change = self.domain_change_history.pop()
            logger.info(f"Undoing change: {last_change}")
            
            # Restore previous domains
            success = self._set_trusted_domains(container_name, last_change['previous_domains'])
            
            if success:
                action = last_change['action']
                domain = last_change['domain']
                return (True, f"Undone: {action} of domain '{domain}'")
            else:
                # Put it back if failed
                self.domain_change_history.append(last_change)
                return (False, "Failed to undo change")
        
        except Exception as e:
            logger.error(f"Error undoing domain change: {e}")
            return (False, f"Error: {str(e)}")
    
    def _restore_default_domains(self, container_name):
        """
        Restore trusted domains to their original values.
        Returns: (success, message)
        """
        if self.original_domains is None:
            return (False, "No original domains stored")
        
        try:
            # Confirm restore
            confirm = messagebox.askyesno(
                "Restore Default Domains",
                "This will restore trusted domains to their original values:\n\n" +
                "\n".join(f"• {d}" for d in self.original_domains) +
                "\n\nAll current domains will be replaced. Continue?"
            )
            
            if not confirm:
                return (False, "Restore cancelled")
            
            # Log the change
            current_domains = self._get_trusted_domains(container_name)
            change_record = {
                'timestamp': datetime.now().isoformat(),
                'action': 'restore_defaults',
                'domain': None,
                'previous_domains': current_domains.copy()
            }
            self.domain_change_history.append(change_record)
            
            # Restore
            success = self._set_trusted_domains(container_name, self.original_domains.copy())
            
            if success:
                logger.info("✓ Restored default domains")
                return (True, "Default domains restored successfully")
            else:
                self.domain_change_history.pop()
                return (False, "Failed to restore defaults")
        
        except Exception as e:
            logger.error(f"Error restoring default domains: {e}")
            return (False, f"Error: {str(e)}")
    
    def _update_trusted_domains(self, container_name, new_domains):
        """Update trusted_domains in Nextcloud config.php"""
        try:
            # Read current config.php
            result = subprocess.run(
                ["docker", "exec", container_name, "cat", "/var/www/html/config/config.php"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"Failed to read config.php: {result.stderr}")
                return False
            
            config_content = result.stdout
            
            # Parse trusted_domains array
            trusted_domains_pattern = r"'trusted_domains'\s*=>\s*array\s*\((.*?)\),"
            match = re.search(trusted_domains_pattern, config_content, re.DOTALL)
            
            if not match:
                print("Could not find trusted_domains in config.php")
                return False
            
            # Extract existing domains
            existing_domains_str = match.group(1)
            existing_domains = []
            
            # Parse existing domain entries
            domain_pattern = r"\d+\s*=>\s*'([^']+)'"
            for domain_match in re.finditer(domain_pattern, existing_domains_str):
                existing_domains.append(domain_match.group(1))
            
            # Add new domains (avoid duplicates)
            for domain in new_domains:
                if domain not in existing_domains:
                    existing_domains.append(domain)
            
            # Build new trusted_domains array
            new_domains_array = "array(\n"
            for i, domain in enumerate(existing_domains):
                new_domains_array += f"    {i} => '{domain}',\n"
            new_domains_array += "  )"
            
            # Replace in config
            new_config = re.sub(
                trusted_domains_pattern,
                f"'trusted_domains' => {new_domains_array},",
                config_content,
                count=1,
                flags=re.DOTALL
            )
            
            # Write back to container
            write_cmd = f"cat > /var/www/html/config/config.php << 'EOFCONFIG'\n{new_config}\nEOFCONFIG"
            
            result = subprocess.run(
                ["docker", "exec", container_name, "sh", "-c", write_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"Failed to write config.php: {result.stderr}")
                return False
            
            print(f"✓ Updated trusted_domains with: {', '.join(new_domains)}")
            return True
        
        except Exception as e:
            print(f"Error updating trusted_domains: {e}")
            return False
    
    def _add_health_dashboard(self, parent_frame):
        """Add service health dashboard to landing page"""
        # Create collapsible health section
        health_frame = tk.Frame(parent_frame, bg=self.theme_colors['bg'])
        health_frame.pack(fill="x", padx=20, pady=(10, 5))
        
        # Header with refresh button
        header_frame = tk.Frame(health_frame, bg=self.theme_colors['bg'])
        header_frame.pack(fill="x")
        
        health_label = tk.Label(
            header_frame,
            text="🏥 System Health",
            font=("Arial", 12, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        health_label.pack(side="left")
        
        refresh_btn = tk.Button(
            header_frame,
            text="🔄",
            font=("Arial", 10),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=lambda: self._refresh_health_dashboard(status_container),
            cursor="hand2",
            width=3
        )
        refresh_btn.pack(side="right")
        ToolTip(refresh_btn, "Refresh health status")
        
        # Status container
        status_container = tk.Frame(health_frame, bg=self.theme_colors['bg'])
        status_container.pack(fill="x", pady=(5, 0))
        
        # Initial health check
        self._refresh_health_dashboard(status_container)
    
    def _refresh_health_dashboard(self, container):
        """Refresh health status display"""
        # Clear existing widgets
        for widget in container.winfo_children():
            widget.destroy()
        
        # Run health check in background to avoid blocking UI
        def check_and_update():
            health_status = check_service_health()
            self.health_check_cache = health_status
            self.last_health_check = datetime.now()
            
            # Update UI in main thread
            self.after(0, lambda: self._display_health_status(container, health_status))
        
        # Show loading message
        loading_label = tk.Label(
            container,
            text="Checking system health...",
            font=("Arial", 9),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['hint_fg']
        )
        loading_label.pack()
        
        # Run check in thread
        threading.Thread(target=check_and_update, daemon=True).start()
    
    def _display_health_status(self, container, health_status):
        """Display health status in container"""
        # Clear loading message
        for widget in container.winfo_children():
            widget.destroy()
        
        # Status icons
        status_icons = {
            'healthy': '✅',
            'warning': '⚠️',
            'error': '❌',
            'unknown': '❓'
        }
        
        # Create grid layout for status items
        row = 0
        for service, status_info in health_status.items():
            status = status_info['status']
            message = status_info['message']
            
            # Service name
            service_label = tk.Label(
                container,
                text=f"{service.capitalize()}:",
                font=("Arial", 9),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['fg'],
                width=12,
                anchor="w"
            )
            service_label.grid(row=row, column=0, sticky="w", padx=(5, 2), pady=2)
            
            # Status icon and message
            status_label = tk.Label(
                container,
                text=f"{status_icons[status]} {message}",
                font=("Arial", 9),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['fg'],
                anchor="w"
            )
            status_label.grid(row=row, column=1, sticky="w", padx=(2, 5), pady=2)
            
            row += 1
        
        # Last checked time
        if self.last_health_check:
            time_str = self.last_health_check.strftime("%H:%M:%S")
            time_label = tk.Label(
                container,
                text=f"Last checked: {time_str}",
                font=("Arial", 8),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['hint_fg']
            )
            time_label.grid(row=row, column=0, columnspan=2, pady=(5, 0))
    
    def show_backup_history(self):
        """Show backup history window with list of previous backups"""
        self.current_page = 'backup_history'
        
        # Unbind any previous mousewheel events to prevent binding accumulation
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
        
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        
        self.status_label.config(text="Backup History")
        
        # Create main container
        main_frame = tk.Frame(self.body_frame, bg=self.theme_colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Header with back button
        header_frame = tk.Frame(main_frame, bg=self.theme_colors['bg'])
        header_frame.pack(fill="x", pady=(0, 10))
        
        back_btn = tk.Button(
            header_frame,
            text="← Back",
            font=("Arial", 10),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=self.show_landing
        )
        back_btn.pack(side="left")
        
        title_label = tk.Label(
            header_frame,
            text="📜 Backup History & Restore Points",
            font=("Arial", 14, "bold"),
            bg=self.theme_colors['bg'],
            fg=self.theme_colors['fg']
        )
        title_label.pack(side="left", padx=20)
        
        # Create scrollable list
        list_frame = tk.Frame(main_frame, bg=self.theme_colors['bg'])
        list_frame.pack(fill="both", expand=True)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Canvas for scrolling
        canvas = tk.Canvas(
            list_frame,
            bg=self.theme_colors['bg'],
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=canvas.yview)
        
        # Inner frame for content
        content_frame = tk.Frame(canvas, bg=self.theme_colors['bg'])
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Bind resize event to update scroll region and canvas width
        def configure_scroll(event=None):
            """Update scroll region when content changes"""
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make content_frame width match canvas width
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        content_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        # Add mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # Linux scroll down
        
        # Get backup history
        backups = self.backup_history.get_all_backups()
        
        # Filter out backups whose files no longer exist and clean up database
        existing_backups = []
        for backup in backups:
            backup_id = backup[0]
            backup_path = backup[1]
            
            if os.path.exists(backup_path):
                existing_backups.append(backup)
            else:
                # Remove missing backup from database
                logger.info(f"BACKUP HISTORY: Removing missing backup from history: {backup_path}")
                self.backup_history.delete_backup(backup_id)
        
        if not existing_backups:
            no_backups_label = tk.Label(
                content_frame,
                text="No backup history found.\n\nBackups created using this tool will appear here.",
                font=("Arial", 12),
                bg=self.theme_colors['bg'],
                fg=self.theme_colors['hint_fg'],
                justify=tk.CENTER
            )
            no_backups_label.pack(pady=50)
        else:
            # Display each backup
            for backup in existing_backups:
                self._create_backup_item(content_frame, backup)
    
    def _create_backup_item(self, parent, backup_data):
        """Create a single backup item in the history list"""
        backup_id, path, timestamp, size_bytes, encrypted, db_type, folders, verification_status, verification_details, notes = backup_data
        
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            timestamp_str = timestamp
        
        # Format size
        size_mb = size_bytes / (1024 * 1024) if size_bytes else 0
        size_str = f"{size_mb:.1f} MB"
        
        # Status icon
        status_icons = {
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'pending': '⏳'
        }
        status_icon = status_icons.get(verification_status, '❓')
        
        # Create frame for this backup
        item_frame = tk.Frame(
            parent,
            bg=self.theme_colors['info_bg'],
            relief=tk.RAISED,
            borderwidth=1
        )
        item_frame.pack(fill="x", pady=5, padx=5)
        
        # Top row: timestamp and size
        top_row = tk.Frame(item_frame, bg=self.theme_colors['info_bg'])
        top_row.pack(fill="x", padx=10, pady=(8, 2))
        
        timestamp_label = tk.Label(
            top_row,
            text=f"📅 {timestamp_str}",
            font=("Arial", 10, "bold"),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        )
        timestamp_label.pack(side="left")
        
        size_label = tk.Label(
            top_row,
            text=f"💾 {size_str}",
            font=("Arial", 9),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg']
        )
        size_label.pack(side="right")
        
        # Middle row: path and details
        path_label = tk.Label(
            item_frame,
            text=f"📁 {os.path.basename(path)}",
            font=("Arial", 9),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg'],
            anchor="w"
        )
        path_label.pack(fill="x", padx=10, pady=2)
        
        # Details row
        details_text = []
        if encrypted:
            details_text.append("🔒 Encrypted")
        if db_type:
            details_text.append(f"DB: {db_type}")
        
        if details_text:
            details_label = tk.Label(
                item_frame,
                text=" | ".join(details_text),
                font=("Arial", 8),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['hint_fg'],
                anchor="w"
            )
            details_label.pack(fill="x", padx=10, pady=2)
        
        # Verification status
        verification_label = tk.Label(
            item_frame,
            text=f"{status_icon} Verification: {verification_status}",
            font=("Arial", 8),
            bg=self.theme_colors['info_bg'],
            fg=self.theme_colors['info_fg'],
            anchor="w"
        )
        verification_label.pack(fill="x", padx=10, pady=2)
        
        # Notes if present
        if notes:
            notes_label = tk.Label(
                item_frame,
                text=f"📝 {notes}",
                font=("Arial", 8, "italic"),
                bg=self.theme_colors['info_bg'],
                fg=self.theme_colors['hint_fg'],
                anchor="w"
            )
            notes_label.pack(fill="x", padx=10, pady=2)
        
        # Action buttons
        button_frame = tk.Frame(item_frame, bg=self.theme_colors['info_bg'])
        button_frame.pack(fill="x", padx=10, pady=(5, 8))
        
        # Restore button
        restore_btn = tk.Button(
            button_frame,
            text="🛠 Restore",
            font=("Arial", 9),
            bg=self.theme_colors['restore_btn'],
            fg="white",
            command=lambda p=path: self._restore_from_history(p),
            cursor="hand2"
        )
        restore_btn.pack(side="left", padx=(0, 5))
        ToolTip(restore_btn, "Restore from this backup")
        
        # Verify button
        verify_btn = tk.Button(
            button_frame,
            text="✓ Verify",
            font=("Arial", 9),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=lambda bid=backup_id, p=path, enc=encrypted: self._verify_backup_from_history(bid, p, enc),
            cursor="hand2"
        )
        verify_btn.pack(side="left", padx=5)
        ToolTip(verify_btn, "Verify backup integrity")
        
        # Export button
        export_btn = tk.Button(
            button_frame,
            text="📤 Export",
            font=("Arial", 9),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=lambda p=path: self._export_backup(p),
            cursor="hand2"
        )
        export_btn.pack(side="left", padx=5)
        ToolTip(export_btn, "Copy backup to another location")
        
        # Show full path button
        path_btn = tk.Button(
            button_frame,
            text="📍",
            font=("Arial", 9),
            bg=self.theme_colors['button_bg'],
            fg=self.theme_colors['button_fg'],
            command=lambda p=path: messagebox.showinfo("Backup Location", f"Full path:\n\n{p}"),
            cursor="hand2",
            width=2
        )
        path_btn.pack(side="right")
        ToolTip(path_btn, "Show full path")
    
    def _restore_from_history(self, backup_path):
        """Initiate restore from a backup in history"""
        if not os.path.exists(backup_path):
            messagebox.showerror("Error", f"Backup file not found:\n{backup_path}")
            return
        
        # Ask for confirmation
        result = messagebox.askyesno(
            "Restore Backup",
            f"Restore from this backup?\n\n{os.path.basename(backup_path)}\n\nThis will replace current Nextcloud data."
        )
        
        if result:
            # Set backup path and start restore wizard
            self.restore_backup_path = backup_path
            self.start_restore()
    
    def _verify_backup_from_history(self, backup_id, backup_path, is_encrypted):
        """Verify backup integrity and update history"""
        if not os.path.exists(backup_path):
            messagebox.showerror("Error", f"Backup file not found:\n{backup_path}")
            self.backup_history.update_verification(backup_id, "error", "File not found")
            return
        
        # Ask for password if encrypted
        password = None
        if is_encrypted:
            password = simpledialog.askstring(
                "Encryption Password",
                "Enter backup encryption password for verification:",
                show='*'
            )
            if not password:
                return
        
        # Show progress
        progress_window = tk.Toplevel(self)
        progress_window.title("Verifying Backup")
        progress_window.geometry("400x100")
        progress_window.transient(self)
        progress_window.grab_set()
        
        progress_label = tk.Label(
            progress_window,
            text="Verifying backup integrity...",
            font=("Arial", 10)
        )
        progress_label.pack(pady=20)
        
        # Run verification in thread
        def verify():
            status, details = verify_backup_integrity(backup_path, password)
            self.backup_history.update_verification(backup_id, status, details)
            
            # Close progress window and show result
            progress_window.destroy()
            
            if status == 'success':
                messagebox.showinfo("Verification Complete", f"✅ {details}")
            elif status == 'warning':
                messagebox.showwarning("Verification Warning", f"⚠️ {details}")
            else:
                messagebox.showerror("Verification Failed", f"❌ {details}")
            
            # Refresh history view
            self.show_backup_history()
        
        threading.Thread(target=verify, daemon=True).start()
    
    def _export_backup(self, backup_path):
        """Export/copy backup to another location"""
        if not os.path.exists(backup_path):
            messagebox.showerror("Error", f"Backup file not found:\n{backup_path}")
            return
        
        # Ask for destination
        dest_dir = filedialog.askdirectory(title="Select destination folder for backup copy")
        if not dest_dir:
            return
        
        # Copy file
        try:
            dest_path = os.path.join(dest_dir, os.path.basename(backup_path))
            
            # Show progress window
            progress_window = tk.Toplevel(self)
            progress_window.title("Exporting Backup")
            progress_window.geometry("400x100")
            progress_window.transient(self)
            progress_window.grab_set()
            
            progress_label = tk.Label(
                progress_window,
                text="Copying backup file...",
                font=("Arial", 10)
            )
            progress_label.pack(pady=20)
            
            def do_copy():
                shutil.copy2(backup_path, dest_path)
                progress_window.destroy()
                messagebox.showinfo("Export Complete", f"Backup copied to:\n\n{dest_path}")
            
            threading.Thread(target=do_copy, daemon=True).start()
        
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to copy backup:\n\n{str(e)}")
    
    def _on_window_resize(self, event):
        """Handle window resize for responsive layout"""
        # Only process resize events for the main window
        if event.widget == self:
            new_size = (event.width, event.height)
            
            # Only update if size changed significantly (avoid micro-adjustments)
            if abs(new_size[0] - self.last_window_size[0]) > 10 or \
               abs(new_size[1] - self.last_window_size[1]) > 10:
                self.last_window_size = new_size
                
                # Adjust font sizes based on window size
                if new_size[0] < 750:
                    # Smaller font for narrow windows
                    self.header_label.config(font=("Arial", 18, "bold"))
                else:
                    # Normal font
                    self.header_label.config(font=("Arial", 22, "bold"))
    
    def _check_scheduled_task_on_startup(self):
        """
        Check on startup if the scheduled task needs repair (app has been moved).
        Shows a notification to the user if repair was performed.
        """
        try:
            repaired, message = check_and_repair_scheduled_task("NextcloudBackup")
            
            if repaired:
                # App was moved and task was repaired - notify user
                logger.info(f"Scheduled task auto-repaired: {message}")
                
                # Show notification dialog
                dialog = tk.Toplevel(self)
                dialog.title("Scheduled Task Updated")
                dialog.geometry("500x200")
                dialog.transient(self)
                dialog.resizable(False, False)
                
                # Apply theme
                dialog.configure(bg=self.theme_colors['bg'])
                
                # Icon and title
                title_frame = tk.Frame(dialog, bg=self.theme_colors['bg'])
                title_frame.pack(pady=20, padx=20, fill="x")
                
                icon_label = tk.Label(
                    title_frame,
                    text="✅",
                    font=("Arial", 24),
                    bg=self.theme_colors['bg'],
                    fg=self.theme_colors['fg']
                )
                icon_label.pack(side="left", padx=(0, 10))
                
                title_label = tk.Label(
                    title_frame,
                    text="Scheduled Task Auto-Repaired",
                    font=("Arial", 14, "bold"),
                    bg=self.theme_colors['bg'],
                    fg=self.theme_colors['fg']
                )
                title_label.pack(side="left")
                
                # Message
                msg_label = tk.Label(
                    dialog,
                    text="The application location has changed.\nScheduled backup task updated automatically.",
                    font=("Arial", 10),
                    bg=self.theme_colors['bg'],
                    fg=self.theme_colors['fg'],
                    justify="left"
                )
                msg_label.pack(pady=10, padx=20)
                
                # OK button
                ok_btn = tk.Button(
                    dialog,
                    text="OK",
                    font=("Arial", 10),
                    width=10,
                    bg=self.theme_colors['button_bg'],
                    fg=self.theme_colors['button_fg'],
                    command=dialog.destroy
                )
                ok_btn.pack(pady=20)
                
                # Center the dialog
                dialog.update_idletasks()
                x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
                y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
                dialog.geometry(f"+{x}+{y}")
        
        except Exception as e:
            # Silently log any errors - we don't want startup to fail
            logger.error(f"Error checking scheduled task on startup: {e}")
    
    def check_dependencies(self):
        pass # handled stepwise

if __name__ == "__main__":
    # Parse command-line arguments for scheduled execution
    parser = argparse.ArgumentParser(description='Nextcloud Restore & Backup Utility')
    parser.add_argument('--scheduled', action='store_true', help='Run in scheduled backup mode (no GUI)')
    parser.add_argument('--test-run', action='store_true', help='Run a test backup (config file only, deleted after)')
    parser.add_argument('--backup-dir', type=str, help='Backup directory path')
    parser.add_argument('--encrypt', action='store_true', help='Enable encryption')
    parser.add_argument('--no-encrypt', action='store_true', help='Disable encryption')
    parser.add_argument('--password', type=str, default='', help='Encryption password')
    parser.add_argument('--components', type=str, default='', help='Comma-separated list of components to backup')
    parser.add_argument('--rotation-keep', type=int, default=0, help='Number of backups to keep (0 = unlimited)')
    
    args = parser.parse_args()
    
    if args.test_run:
        # Run in test mode (backup config file only, no GUI)
        if not args.backup_dir:
            print("ERROR: --backup-dir is required for test backups")
            sys.exit(1)
        
        encrypt = args.encrypt and not args.no_encrypt
        
        # Run test backup directly
        success, message = run_test_backup(args.backup_dir, encrypt, args.password)
        if success:
            print(f"SUCCESS: {message}")
            sys.exit(0)
        else:
            print(f"FAILED: {message}")
            sys.exit(1)
    elif args.scheduled:
        # Run in scheduled mode (no GUI)
        if not args.backup_dir:
            print("ERROR: --backup-dir is required for scheduled backups")
            sys.exit(1)
        
        encrypt = args.encrypt and not args.no_encrypt
        
        # Parse components
        components = []
        if args.components:
            components = [c.strip() for c in args.components.split(',') if c.strip()]
        
        # Create a minimal app instance in scheduled mode (no GUI initialization)
        app = NextcloudRestoreWizard(scheduled_mode=True)
        app.run_scheduled_backup(args.backup_dir, encrypt, args.password, components, args.rotation_keep)
        sys.exit(0)
    else:
        # Normal GUI mode
        NextcloudRestoreWizard().mainloop()