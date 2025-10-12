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

DOCKER_INSTALLER_URL = "https://www.docker.com/products/docker-desktop/"
GPG_DOWNLOAD_URL = "https://files.gpg4win.org/gpg4win-latest.exe"

# --- Customizable container and DB settings ---
NEXTCLOUD_IMAGE = "nextcloud"
POSTGRES_IMAGE = "postgres"
NEXTCLOUD_CONTAINER_NAME = "nextcloud-app"
POSTGRES_CONTAINER_NAME = "nextcloud-db"
POSTGRES_DB = "nextcloud"
POSTGRES_USER = "nextcloud"
POSTGRES_PASSWORD = "example"
POSTGRES_PORT = 5432

def is_tool_installed(tool):
    try:
        subprocess.run([tool, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False

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
    result = subprocess.run([
        'gpg', '--batch', '--yes', '--passphrase', passphrase,
        '-c', '--cipher-algo', 'AES256',
        '-o', encrypted_path, unencrypted_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(result.stderr.decode() or "GPG encryption failed")

def decrypt_file_gpg(encrypted_path, decrypted_path, passphrase):
    result = subprocess.run([
        'gpg', '--batch', '--yes', '--passphrase', passphrase,
        '-o', decrypted_path, '-d', encrypted_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(result.stderr.decode() or "GPG decryption failed")

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
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}} {{.Image}}'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0:
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
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}} {{.Image}}'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0:
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
        result = subprocess.run(
            ['docker', 'inspect', container_name, '--format', '{{range $net, $config := .NetworkSettings.Networks}}{{$net}} {{end}}'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode == 0:
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
        result = subprocess.run(
            ['docker', 'network', 'connect', network_name, container_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
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


def fast_extract_tar_gz(archive_path, extract_to):
    """
    Extract full tar.gz archive using Python's tarfile module.
    
    This function performs a complete extraction of all files in the backup archive.
    It should only be called during the actual restore process, not during initial
    database detection (use extract_config_php_only for that).
    
    Rationale: Full extraction is a heavy operation that can take minutes for large
    backups (several GB). By deferring this until the user confirms they want to
    proceed with the restore, we keep the initial UI responsive and fast.
    
    Args:
        archive_path: Path to the .tar.gz backup archive
        extract_to: Directory where all files should be extracted
    
    Raises:
        Exception: If archive is corrupted, unreadable, or extraction fails
    """
    os.makedirs(extract_to, exist_ok=True)
    try:
        with tarfile.open(archive_path, 'r:gz') as tar:
            # Extract all members
            tar.extractall(path=extract_to)
        print(f"✓ Successfully extracted full archive to {extract_to}")
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
# ---------------------------------------------------------------

class NextcloudRestoreWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nextcloud Restore & Backup Utility")
        self.geometry("700x900")  # Increased height for more input fields
        self.minsize(600, 700)  # Set minimum window size to prevent excessive collapsing

        self.header_frame = tk.Frame(self)
        tk.Label(self.header_frame, text="Nextcloud Restore & Backup Utility", font=("Arial", 22, "bold")).pack(pady=10)
        self.header_frame.pack(fill="x")

        self.status_label = tk.Label(self, text="", font=("Arial", 14))
        self.status_label.pack(pady=(0,10))

        self.body_frame = tk.Frame(self)
        self.body_frame.pack(fill="both", expand=True)

        self.restore_password = None  # store password for restore workflow
        self.restore_backup_path = None
        self.restore_steps = [
            "Decrypting/extracting backup ...",
            "Ensuring containers running ...",
            "Copying files into container ...",
            "Restoring database ...",
            "Setting permissions ...",
            "Restore complete!"
        ]
        
        # Multi-page wizard state
        self.wizard_page = 1
        self.wizard_data = {}
        
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

        self.show_landing()

    def show_landing(self):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        self.status_label.config(text="")
        landing_frame = tk.Frame(self.body_frame)
        landing_frame.pack(fill="both", expand=True)
        self.backup_btn = tk.Button(
            landing_frame, text="🔄 Backup Now", font=("Arial", 16, "bold"),
            height=2, width=24, bg="#3daee9", fg="white", command=self.start_backup
        )
        self.backup_btn.pack(pady=(18,6))
        self.restore_btn = tk.Button(
            landing_frame, text="🛠 Restore from Backup", font=("Arial", 16, "bold"),
            height=2, width=24, bg="#45bf55", fg="white", command=self.start_restore
        )
        self.restore_btn.pack(pady=6)
        self.new_btn = tk.Button(
            landing_frame, text="✨ Start New Nextcloud Instance", font=("Arial", 16, "bold"),
            height=2, width=24, bg="#f7b32b", fg="white", command=self.start_new_instance_workflow
        )
        self.new_btn.pack(pady=(6,22))

    # ----- Backup logic -----
    def start_backup(self):
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

        self.ask_encryption_password_inline(backup_dir, chosen_container)

    def ask_encryption_password_inline(self, backup_dir, container_name):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        frame = tk.Frame(self.body_frame)
        frame.pack(pady=30, fill="both", expand=True)
        btn_back = tk.Button(frame, text="Return to Main Menu", font=("Arial", 12), command=self.show_landing)
        btn_back.pack(pady=8, anchor="center")
        tk.Label(frame, text="Enter password to encrypt your backup (leave blank for no encryption):", font=("Arial", 13)).pack(pady=10, anchor="center")
        
        # Create a container for the password entry to control its width responsively
        pwd_container = tk.Frame(frame)
        pwd_container.pack(pady=8, fill="x", padx=100)
        pwd_entry = tk.Entry(pwd_container, font=("Arial", 13), show="*")
        pwd_entry.pack(fill="x", expand=True)
        def submit_pwd():
            encryption_password = pwd_entry.get()
            encrypt = bool(encryption_password)
            self.progressbar = ttk.Progressbar(self.body_frame, length=520, mode='determinate', maximum=10)
            self.progressbar.pack(pady=10)
            self.progress_message = tk.Label(self.body_frame, text="", font=("Arial", 13))
            self.progress_message.pack(pady=10)
            threading.Thread(target=self.run_backup_process, args=(backup_dir, encrypt, encryption_password, container_name), daemon=True).start()
        tk.Button(frame, text="Continue", font=("Arial", 12), command=submit_pwd).pack(pady=10)

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

            self.set_progress(6, "Dumping PostgreSQL database ...")
            dump_file = os.path.join(backup_temp, "nextcloud-db.sql")
            db_dump_cmd = f'docker exec {POSTGRES_CONTAINER_NAME} bash -c "PGPASSWORD=\'{POSTGRES_PASSWORD}\' pg_dump -U {POSTGRES_USER} {POSTGRES_DB}"'
            db_dump_result = None
            try:
                with open(dump_file, "w", encoding="utf8") as f:
                    proc = subprocess.Popen(db_dump_cmd, shell=True, stdout=f)
                    proc.wait()
                    db_dump_result = proc.returncode
            except Exception as e:
                db_dump_result = 1
            if db_dump_result != 0:
                self.set_progress(0, f"CRITICAL: Database backup failed! Backup aborted.")
                messagebox.showerror("Backup failed", "Could not dump Nextcloud database. Backup cannot continue.")
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
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        self.status_label.config(text="Restore Wizard: Select backup archive to restore.")
        self.create_wizard()

    def create_wizard(self):
        """Create multi-page restore wizard"""
        # Reset wizard state
        self.wizard_page = 1
        
        # Create scrollable frame for wizard content
        canvas = tk.Canvas(self.body_frame)
        scrollbar = tk.Scrollbar(self.body_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        def on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Center the window horizontally
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:  # Only update if canvas has been rendered
                canvas.coords(self.canvas_window, canvas_width // 2, 0)
        
        scrollable_frame.bind("<Configure>", on_configure)
        
        # Create window with north (top-center) anchor for horizontal centering
        self.canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Also bind canvas resize to re-center content
        canvas.bind("<Configure>", on_configure)
        
        # Store references
        self.wizard_canvas = canvas
        self.wizard_scrollbar = scrollbar
        self.wizard_scrollable_frame = scrollable_frame
        
        # Pack canvas and scrollbar first
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Show first page
        self.show_wizard_page(1)
        
        # Force an immediate update to center the content on initial display
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        if canvas_width > 1:
            canvas.coords(self.canvas_window, canvas_width // 2, 0)
    
    def show_wizard_page(self, page_num):
        """Display a specific page of the wizard"""
        # Clear current page
        for widget in self.wizard_scrollable_frame.winfo_children():
            widget.destroy()
        
        frame = self.wizard_scrollable_frame
        self.wizard_page = page_num
        
        # Page title (subheader) - centered
        page_title = f"Restore Wizard: Page {page_num} of 3"
        tk.Label(frame, text=page_title, font=("Arial", 14)).pack(pady=(10, 10), anchor="center")
        
        # Return to Main Menu button - centered
        btn_back = tk.Button(frame, text="Return to Main Menu", font=("Arial", 12), command=self.show_landing)
        btn_back.pack(pady=8, anchor="center")
        
        if page_num == 1:
            self.create_wizard_page1(frame)
        elif page_num == 2:
            self.create_wizard_page2(frame)
        elif page_num == 3:
            self.create_wizard_page3(frame)
        
        # Navigation buttons - centered
        nav_frame = tk.Frame(frame)
        nav_frame.pack(pady=20, anchor="center")
        
        if page_num > 1:
            tk.Button(
                nav_frame, 
                text="← Back", 
                font=("Arial", 12, "bold"),
                width=12,
                command=lambda: self.wizard_navigate(-1)
            ).pack(side="left", padx=10)
        
        if page_num < 3:
            tk.Button(
                nav_frame, 
                text="Next →", 
                font=("Arial", 12, "bold"),
                bg="#3daee9",
                fg="white",
                width=12,
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
                width=15,
                command=self.validate_and_start_restore
            )
            self.restore_now_btn.pack(side="left", padx=10)
        
        # Error label - centered
        self.error_label = tk.Label(frame, text="", font=("Arial", 12), fg="red", wraplength=600)
        self.error_label.pack(pady=10, anchor="center")
        
        # Progress section (shown after restore starts) - centered
        self.progressbar = ttk.Progressbar(frame, length=520, mode='determinate', maximum=100)
        self.progressbar.pack(pady=(30, 3), anchor="center")
        self.progressbar.pack_forget()  # Hide initially
        
        self.progress_label = tk.Label(frame, text="0%", font=("Arial", 13))
        self.progress_label.pack(anchor="center")
        self.progress_label.pack_forget()  # Hide initially
        
        self.process_label = tk.Label(frame, text="", font=("Arial", 11), fg="gray", anchor="center", justify="center")
        self.process_label.pack(padx=10, pady=4, anchor="center")
        self.process_label.pack_forget()  # Hide initially
        
    def create_wizard_page1(self, parent):
        """Page 1: Backup Archive Selection and Decryption Password"""
        # Section 1: Backup file selection - all centered
        tk.Label(parent, text="Step 1: Select Backup Archive", font=("Arial", 14, "bold")).pack(pady=(10, 5), anchor="center")
        tk.Label(parent, text="Choose the backup file to restore (.tar.gz.gpg or .tar.gz)", font=("Arial", 10), fg="gray").pack(pady=(0, 5), anchor="center")
        
        # Create a container frame for the entry to control its width responsively
        # Using anchor="center" ensures the frame itself is centered horizontally
        entry_container = tk.Frame(parent)
        entry_container.pack(pady=5, anchor="center")
        
        self.backup_entry = tk.Entry(entry_container, font=("Arial", 11), justify="center", width=60)
        self.backup_entry.pack()
        
        # Restore saved value if exists
        if 'backup_path' in self.wizard_data:
            self.backup_entry.delete(0, tk.END)
            self.backup_entry.insert(0, self.wizard_data['backup_path'])
        
        tk.Button(parent, text="Browse...", font=("Arial", 11), command=self.browse_backup).pack(pady=5, anchor="center")
        
        # Section 2: Decryption password - all centered
        tk.Label(parent, text="Step 2: Decryption Password", font=("Arial", 14, "bold")).pack(pady=(25, 5), anchor="center")
        tk.Label(parent, text="Enter password if backup is encrypted (.gpg)", font=("Arial", 10), fg="gray").pack(pady=(0, 5), anchor="center")
        
        # Create a container frame for the password entry to control its width responsively
        # Using anchor="center" ensures the frame itself is centered horizontally
        password_container = tk.Frame(parent)
        password_container.pack(pady=5, anchor="center")
        
        self.password_entry = tk.Entry(password_container, show="*", font=("Arial", 12), justify="center", width=50)
        self.password_entry.pack()
        
        # Restore saved value if exists
        if 'password' in self.wizard_data:
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, self.wizard_data['password'])
    
    def create_wizard_page2(self, parent):
        """Page 2: Database Configuration and Admin Credentials"""
        # Section 3: Database credentials - all centered
        tk.Label(parent, text="Step 3: Database Configuration", font=("Arial", 14, "bold")).pack(pady=(10, 5), anchor="center")
        
        # Info about auto-detection - centered
        info_frame = tk.Frame(parent, bg="#e3f2fd", relief="solid", borderwidth=1)
        info_frame.pack(pady=(5, 10), anchor="center")
        tk.Label(info_frame, text="ℹ️ Database Type Auto-Detection", font=("Arial", 10, "bold"), bg="#e3f2fd").pack(pady=(5, 2), anchor="center")
        tk.Label(info_frame, text="The restore process will automatically detect your database type (SQLite, PostgreSQL, MySQL)", 
                 font=("Arial", 9), bg="#e3f2fd", wraplength=600, justify="center").pack(pady=2, anchor="center")
        tk.Label(info_frame, text="from the config.php file in your backup and restore accordingly.", 
                 font=("Arial", 9), bg="#e3f2fd", wraplength=600, justify="center").pack(pady=(0, 5), anchor="center")
        
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
        warning_label.pack(anchor="center", pady=(5, 0))
        
        instruction_label1 = tk.Label(parent, text="These credentials are stored in your backup and must match exactly", font=("Arial", 9), fg="gray")
        instruction_label1.pack(anchor="center")
        
        instruction_label2 = tk.Label(parent, text="The database will be automatically imported using these credentials", font=("Arial", 9), fg="gray")
        instruction_label2.pack(anchor="center", pady=(0, 10))
        
        db_frame = tk.Frame(parent)
        db_frame.pack(pady=10, anchor="center")
        
        # Configure column weights for responsive layout
        db_frame.grid_columnconfigure(0, weight=0)  # Label column - fixed width
        db_frame.grid_columnconfigure(1, weight=1)  # Entry column - expandable
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
        
        # Section 4: Nextcloud admin credentials - all centered
        tk.Label(parent, text="Step 4: Nextcloud Admin Credentials", font=("Arial", 14, "bold")).pack(pady=(25, 5), anchor="center")
        tk.Label(parent, text="Admin credentials for Nextcloud instance", font=("Arial", 10), fg="gray").pack(pady=(0, 5), anchor="center")
        
        admin_frame = tk.Frame(parent)
        admin_frame.pack(pady=10, anchor="center")
        
        # Configure column weights for responsive layout
        admin_frame.grid_columnconfigure(0, weight=0)  # Label column - fixed width
        admin_frame.grid_columnconfigure(1, weight=1)  # Entry column - expandable
        
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
        # Section 5: Container configuration - all centered
        tk.Label(parent, text="Step 5: Container Configuration", font=("Arial", 14, "bold")).pack(pady=(10, 5), anchor="center")
        tk.Label(parent, text="Configure Nextcloud container settings", font=("Arial", 10), fg="gray").pack(pady=(0, 5), anchor="center")
        
        container_frame = tk.Frame(parent)
        container_frame.pack(pady=10, anchor="center")
        
        # Configure column weights for responsive layout
        container_frame.grid_columnconfigure(0, weight=0)  # Label column - fixed width
        container_frame.grid_columnconfigure(1, weight=1)  # Entry column - expandable
        
        tk.Label(container_frame, text="Container Name:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.container_name_entry = tk.Entry(container_frame, font=("Arial", 11))
        self.container_name_entry.insert(0, self.wizard_data.get('container_name', NEXTCLOUD_CONTAINER_NAME))
        self.container_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        tk.Label(container_frame, text="Container Port:", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.container_port_entry = tk.Entry(container_frame, font=("Arial", 11))
        self.container_port_entry.insert(0, self.wizard_data.get('container_port', '9000'))
        self.container_port_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Option to use existing container - centered
        self.use_existing_var = tk.BooleanVar(value=self.wizard_data.get('use_existing', False))
        tk.Checkbutton(
            parent, 
            text="Use existing Nextcloud container if found", 
            variable=self.use_existing_var,
            font=("Arial", 11)
        ).pack(pady=15, anchor="center")
        
        # Add informative text about what will happen during restore - centered
        info_frame = tk.Frame(parent, bg="#e8f4f8", relief="ridge", borderwidth=2)
        info_frame.pack(pady=20, anchor="center")
        
        tk.Label(info_frame, text="ℹ️ The restore process will automatically:", font=("Arial", 11, "bold"), bg="#e8f4f8").pack(pady=(10, 5), anchor="center")
        restore_info = [
            "• Extract your backup archive",
            "• Start database and Nextcloud containers (if needed)",
            "• Copy config, data, and app folders to /var/www/html",
            "• Import the database backup",
            "• Update config.php with correct database credentials",
            "• Set proper file permissions (www-data:www-data)",
            "• Validate all files and database tables exist",
            "• Restart the Nextcloud container"
        ]
        for info in restore_info:
            tk.Label(info_frame, text=info, font=("Arial", 10), bg="#e8f4f8", anchor="center", justify="center").pack(anchor="center", pady=2)
        tk.Label(info_frame, text="", bg="#e8f4f8").pack(pady=5)  # Spacing
    
    def wizard_navigate(self, direction):
        """Navigate between wizard pages, saving current page data"""
        # Save current page data
        self.save_wizard_page_data()
        
        # If navigating back to Page 1 from Page 2, reset detection
        # This allows users to change backup file or password and re-detect
        if self.wizard_page == 2 and direction == -1:
            # Only reset if detection was done via the "Next" button flow
            # Don't reset if detection was done via browse_backup for unencrypted files
            if self.detected_dbtype and self.wizard_data.get('backup_path', '').endswith('.gpg'):
                print("Resetting detection - user navigating back to Page 1")
                self.detected_dbtype = None
                self.detected_db_config = None
                self.db_auto_detected = False
        
        # If navigating from Page 1 to Page 2, perform extraction and detection
        if self.wizard_page == 1 and direction == 1:
            if not self.perform_extraction_and_detection():
                # Detection failed or was cancelled - don't navigate
                return
        
        # Navigate to new page
        new_page = self.wizard_page + direction
        if 1 <= new_page <= 3:
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
    
    def perform_extraction_and_detection(self):
        """
        Perform database type detection before showing Page 2.
        
        This is the entry point for early database detection, called when the user
        clicks "Next" on Page 1 to navigate to the database configuration page.
        
        EXTRACTION STRATEGY:
        - ONLY config.php is extracted at this stage (not the full backup)
        - This is a lightweight operation (<1 second) vs full extraction (minutes)
        - Full backup extraction is deferred until the actual restore process
        
        WHY THIS MATTERS:
        - SQLite users can immediately see that no database credentials are needed
        - MySQL/PostgreSQL users see the appropriate credential fields
        - GUI remains responsive - no waiting for multi-GB extraction
        - Better user experience with immediate feedback
        
        THREADING:
        - Detection runs in a background thread to keep GUI responsive
        - Animated spinner shows progress while detection is in progress
        - All GUI updates happen on the main thread (thread-safe)
        
        Returns:
            True if detection successful (or already detected), False if validation fails
        """
        # Get backup path and password from wizard data
        backup_path = self.wizard_data.get('backup_path', '').strip()
        password = self.wizard_data.get('password', '')
        
        # Validate backup file exists
        if not backup_path or not os.path.isfile(backup_path):
            self.error_label.config(text="Error: Please select a valid backup archive file.")
            return False
        
        # Validate password for encrypted backups
        if backup_path.endswith('.gpg') and not password:
            self.error_label.config(text="Error: Please enter decryption password for encrypted backup.")
            return False
        
        # If already detected, skip re-detection
        if self.detected_dbtype:
            print(f"Database type already detected: {self.detected_dbtype}")
            return True
        
        # Show progress spinner with message
        self.error_label.config(text="⏳ Extracting and detecting database type...\nPlease wait, this may take a moment...", fg="blue")
        self.update_idletasks()
        
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
        
        # Update progress spinner while detection is running
        spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spinner_idx = 0
        
        while detection_thread.is_alive():
            spinner_idx = (spinner_idx + 1) % len(spinner_chars)
            self.error_label.config(
                text=f"{spinner_chars[spinner_idx]} Extracting and detecting database type...\nPlease wait, this may take a moment...", 
                fg="blue"
            )
            self.update_idletasks()
            time.sleep(0.1)  # Update spinner every 100ms
        
        # Wait for thread to complete
        detection_thread.join()
        
        # Process results
        if detection_result[0]:
            dbtype, db_config, error = detection_result[0]
            
            if error:
                print(f"Error during extraction and detection: {error}")
                self.error_label.config(text=f"⚠️ Error: {str(error)}", fg="red")
                return False
            
            if dbtype:
                self.detected_dbtype = dbtype
                self.detected_db_config = db_config
                self.db_auto_detected = True
                print(f"✓ Database type detected before Page 2: {dbtype}")
                self.error_label.config(text="✓ Database type detected successfully!", fg="green")
                
                # Show Docker Compose suggestion dialog if full config was detected
                # This happens immediately after config.php extraction and database detection
                if self.detected_full_config:
                    # Schedule the dialog to show after the success message clears
                    self.after(1500, lambda: [
                        self.error_label.config(text=""),
                        self.show_docker_compose_suggestion()
                    ])
                else:
                    # Clear success message after a brief moment
                    self.after(1500, lambda: self.error_label.config(text=""))
                
                return True
            else:
                # Detection failed - allow navigation but show clear warning
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
                return True  # Still allow navigation - don't break workflow
        else:
            # Should not happen, but handle gracefully
            self.error_label.config(text="⚠️ Detection process failed unexpectedly", fg="red")
            return False

    def browse_backup(self):
        path = filedialog.askopenfilename(
            title="Select .tar.gz.gpg backup",
            filetypes=[("PGP Archive", "*.tar.gz.gpg"), ("All files", "*.*")]
        )
        if path:
            self.backup_entry.delete(0, tk.END)
            self.backup_entry.insert(0, path)
            
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
        if hasattr(self, "progressbar") and self.progressbar:
            self.progressbar['value'] = percent
        if hasattr(self, "progress_label") and self.progress_label:
            self.progress_label.config(text=f"{percent}%")
        if msg:
            self.status_label.config(text=msg)
        self.update_idletasks()

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

        self.error_label.config(text="")  # Clear error

        # Step 1: If encrypted, decrypt using provided password
        if backup_path.endswith('.gpg'):
            if not password:
                self.error_label.config(text="No password entered. Cannot decrypt backup.")
                return None
            decrypted_file = os.path.splitext(backup_path)[0]  # remove .gpg
            try:
                self.set_restore_progress(5, "Decrypting backup archive ...")
                self.process_label.config(text=f"Decrypting: {os.path.basename(backup_path)}")
                self.update_idletasks()
                
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
                
                # Update progress while decryption is running
                progress_val = 5
                while decryption_thread.is_alive():
                    if progress_val < 9:
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
                self.error_label.config(text=user_msg)
                print(f"Error details:\n{tb}")
                shutil.rmtree(extract_temp, ignore_errors=True)
                return None

        # Step 2: FULL EXTRACTION - Extract all files from backup archive
        # This is where the complete backup (apps, config, data, database) is extracted
        # Unlike early detection which only extracted config.php, this extracts everything
        try:
            self.set_restore_progress(10, "Extracting full backup archive...")
            self.update_idletasks()
            
            # Start extraction in a background thread with progress updates
            extraction_done = [False]  # Use list for mutable flag
            
            def do_extraction():
                try:
                    # Extract ALL files from the backup (not just config.php)
                    fast_extract_tar_gz(extracted_file, extract_temp)
                    extraction_done[0] = True
                except Exception as ex:
                    extraction_done[0] = ex
            
            # Start extraction in a thread
            extraction_thread = threading.Thread(target=do_extraction, daemon=True)
            extraction_thread.start()
            
            # Update progress while extraction is running
            progress_val = 10
            while extraction_thread.is_alive():
                if progress_val < 18:
                    progress_val += 2
                    self.set_restore_progress(progress_val, "Extracting backup archive ...")
                    self.update_idletasks()
                time.sleep(0.5)  # Check every 0.5 seconds
            
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
            self.error_label.config(text=user_msg)
            print(f"Error details:\n{tb}")
            shutil.rmtree(extract_temp, ignore_errors=True)
            return None

        self.set_restore_progress(20, "Extraction complete!")
        self.process_label.config(text="Extraction complete.")
        return extract_temp  # Temp folder with extracted files

    # The rest of the class code (ensure_nextcloud_container, ensure_db_container, etc.) remains unchanged.
    # ... (rest of the code unchanged from your previous script) ...

    def ensure_nextcloud_container(self):
        """Ensure Nextcloud container is running, using values from GUI"""
        container = get_nextcloud_container_name()
        
        # Check if we should use existing container
        if container and self.restore_use_existing:
            self.set_restore_progress(30, f"Using existing Nextcloud container: {container}")
            self.process_label.config(text=f"Using container: {container}")
            self.update_idletasks()
            
            # Check and attach to bridge network if not connected
            if not check_container_network(container, "bridge"):
                self.set_restore_progress(32, f"Attaching {container} to bridge network...")
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
                
                self.set_restore_progress(33, f"Container {container} attached to bridge network")
            
            return container
        
        # Start a new container with configured values
        new_container_name = self.restore_container_name
        port = self.restore_container_port
        
        self.set_restore_progress(30, f"Starting a new Nextcloud container on port {port} ...")
        self.process_label.config(text=f"Starting container: {new_container_name}")
        self.update_idletasks()
        
        # Try to link to database container for proper Docker networking
        # First attempt with link and explicit bridge network
        result = subprocess.run(
            f'docker run -d --name {new_container_name} --network bridge --link {POSTGRES_CONTAINER_NAME}:db -p {port}:80 {NEXTCLOUD_IMAGE}',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        # If linking failed, try without link but still with bridge network
        if result.returncode != 0 and "Could not find" in result.stderr:
            print(f"Warning: Could not link to database container, starting without link: {result.stderr}")
            result = subprocess.run(
                f'docker run -d --name {new_container_name} --network bridge -p {port}:80 {NEXTCLOUD_IMAGE}',
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        
        if result.returncode != 0:
            tb = traceback.format_exc()
            error_msg = (
                f"Failed to start Nextcloud container.\n\n"
                f"Error: {result.stderr}\n\n"
                "Common issues:\n"
                "- Container name already in use (try a different name)\n"
                "- Port already in use (try a different port)\n"
                "- Not attached to default bridge network\n\n"
                "Please check Docker status and try again."
            )
            self.set_restore_progress(0, "Restore failed!")
            self.error_label.config(text=error_msg)
            print(f"Container start failed: {result.stderr}\n{tb}")
            return None
        
        container_id = new_container_name
        self.set_restore_progress(35, f"Started Nextcloud container: {container_id} on port {port}")
        self.process_label.config(text=f"Started container: {container_id} on port {port}")
        self.update_idletasks()
        time.sleep(5)
        return container_id

    def ensure_db_container(self):
        """Ensure database container is running, using credentials from GUI"""
        db_container = get_postgres_container_name()
        if db_container:
            # Check and attach to bridge network if not connected
            if not check_container_network(db_container, "bridge"):
                self.set_restore_progress(42, f"Attaching {db_container} to bridge network...")
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
                
                self.set_restore_progress(43, f"Database container {db_container} attached to bridge network")
            
            return db_container
        
        self.set_restore_progress(40, "No database container found. Starting a new PostgreSQL container ...")
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
            error_msg = (
                f"Failed to start PostgreSQL container.\n\n"
                f"Error: {result.stderr}\n\n"
                "Common issues:\n"
                "- Container name already in use\n"
                "- Port 5432 already in use\n"
                "- Not attached to default bridge network\n\n"
                "Please check Docker status and try again."
            )
            self.set_restore_progress(0, "Restore failed!")
            self.error_label.config(text=error_msg)
            print(f"Database container start failed: {result.stderr}\n{tb}")
            return None
        
        db_container_id = POSTGRES_CONTAINER_NAME
        self.set_restore_progress(45, f"Started DB container: {db_container_id}")
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
            
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if file.endswith('.db'):
                        db_files.append(file)
            
            if not db_files:
                warning_msg = "Warning: No SQLite .db file found in backup data folder. Database restore skipped."
                self.error_label.config(text=warning_msg, fg="orange")
                print(warning_msg)
                return False
            
            # Use the first .db file found (typically owncloud.db or nextcloud.db)
            db_file = db_files[0]
            db_path = os.path.join(data_dir, db_file)
            
            self.process_label.config(text=f"Restoring SQLite database: {db_file}")
            self.update_idletasks()
            
            # The .db file should already be copied with the data folder
            # Just verify it exists
            check_cmd = f'docker exec {nextcloud_container} test -f {nextcloud_path}/data/{db_file}'
            result = subprocess.run(check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode == 0:
                print(f"SQLite database file {db_file} successfully restored")
                return True
            else:
                error_msg = f"Error: SQLite database file {db_file} not found in container after copy"
                self.error_label.config(text=error_msg, fg="red")
                return False
                
        except Exception as e:
            tb = traceback.format_exc()
            self.error_label.config(text=f"SQLite database restore error: {e}\n{tb}")
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
            self.process_label.config(text="Restoring MySQL database (this may take a few minutes) ...")
            self.update_idletasks()
            
            # Use credentials from GUI - MySQL version
            restore_cmd = f'docker exec -i {db_container} bash -c "mysql -u {self.restore_db_user} -p{self.restore_db_password} {self.restore_db_name}"'
            
            with open(sql_path, "rb") as f:
                proc = subprocess.Popen(restore_cmd, shell=True, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = proc.communicate()
                if proc.returncode != 0:
                    error_msg = stderr.decode('utf-8', errors='replace') if stderr else "Unknown error"
                    self.error_label.config(text=f"MySQL database restore failed: {error_msg}")
                    return False
            
            # Validate that database tables were imported
            self.process_label.config(text="Validating MySQL database restore ...")
            self.update_idletasks()
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
            self.process_label.config(text="Restoring PostgreSQL database (this may take a few minutes) ...")
            self.update_idletasks()
            
            # Use credentials from GUI
            restore_cmd = f'docker exec -i {db_container} bash -c "PGPASSWORD={self.restore_db_password} psql -U {self.restore_db_user} -d {self.restore_db_name}"'
            
            with open(sql_path, "rb") as f:
                proc = subprocess.Popen(restore_cmd, shell=True, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = proc.communicate()
                if proc.returncode != 0:
                    error_msg = stderr.decode('utf-8', errors='replace') if stderr else "Unknown error"
                    self.error_label.config(text=f"PostgreSQL database restore failed: {error_msg}")
                    return False
            
            # Validate that database tables were imported
            self.process_label.config(text="Validating PostgreSQL database restore ...")
            self.update_idletasks()
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
                except Exception as decrypt_err:
                    error_msg = str(decrypt_err)
                    if "Bad session key" in error_msg or "decryption failed" in error_msg:
                        print(f"✗ Failed to decrypt backup: Incorrect password")
                    elif "gpg: command not found" in error_msg:
                        print(f"✗ Failed to decrypt backup: GPG is not installed")
                    else:
                        print(f"✗ Failed to decrypt backup: {decrypt_err}")
                    return None, None
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
                return None, None
            except Exception as extract_err:
                print(f"✗ Failed to extract backup: {extract_err}")
                return None, None
            
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
                self.db_sqlite_message_label.pack(pady=(10, 10), anchor="center")
        else:
            # Show packed warning/instruction labels
            if hasattr(self, 'db_credential_packed_widgets'):
                # Re-pack in the correct order with original settings
                self.db_credential_packed_widgets[0].pack(anchor="center", pady=(5, 0))  # warning_label
                self.db_credential_packed_widgets[1].pack(anchor="center")  # instruction_label1
                self.db_credential_packed_widgets[2].pack(anchor="center", pady=(0, 10))  # instruction_label2
            
            # Show the database credential frame
            if hasattr(self, 'db_credential_frame'):
                self.db_credential_frame.pack(pady=10, anchor="center")
            
            # Hide SQLite message
            if hasattr(self, 'db_sqlite_message_label') and self.db_sqlite_message_label:
                self.db_sqlite_message_label.pack_forget()
        
        print(f"UI updated for database type: {dbtype} (is_sqlite={is_sqlite})")
    
    def update_config_php(self, nextcloud_container, db_container, dbtype='pgsql'):
        """Update config.php with database credentials and admin settings"""
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
            self.set_restore_progress(5, self.restore_steps[0])
            extract_dir = self.auto_extract_backup(backup_path, password)
            if not extract_dir:
                self.set_restore_progress(0, "Restore failed!")
                return

            # Auto-detect database type from config.php
            self.set_restore_progress(18, "Detecting database type ...")
            self.process_label.config(text="Reading config.php to detect database type ...")
            self.update_idletasks()
            
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
                self.error_label.config(text=warning_msg, fg="orange")
                self.process_label.config(text="Proceeding with PostgreSQL (default)...")
                print(warning_msg)
                dbtype = 'pgsql'
                self.detected_dbtype = dbtype
                time.sleep(3)  # Give user more time to see the warning

            self.set_restore_progress(20, self.restore_steps[1])
            
            # For SQLite, we don't need a separate database container
            db_container = None
            if dbtype != 'sqlite':
                # Start database container first (needed for Nextcloud container linking)
                db_container = self.ensure_db_container()
                if not db_container:
                    self.set_restore_progress(0, "Restore failed!")
                    return
            else:
                self.process_label.config(text="SQLite detected - no separate database container needed")
                self.update_idletasks()
            
            # Start Nextcloud container (linked to database if not SQLite)
            nextcloud_container = self.ensure_nextcloud_container()
            if not nextcloud_container:
                self.set_restore_progress(0, "Restore failed!")
                return

            self.set_restore_progress(50, self.restore_steps[2])
            nextcloud_path = "/var/www/html"
            # Copy config/data/apps/custom_apps into container
            # Note: We need to remove existing folders first, then copy the backup folders
            for folder in ["config", "data", "apps", "custom_apps"]:
                local_path = os.path.join(extract_dir, folder)
                if os.path.isdir(local_path):
                    self.process_label.config(text=f"Copying: {folder}")
                    self.update_idletasks()
                    try:
                        # Remove existing folder in container (if it exists)
                        subprocess.run(
                            f'docker exec {nextcloud_container} rm -rf {nextcloud_path}/{folder}',
                            shell=True, check=False  # Don't fail if folder doesn't exist
                        )
                        # Copy folder from backup - use /. to copy contents, not the folder itself
                        subprocess.run(
                            f'docker cp "{local_path}/." {nextcloud_container}:{nextcloud_path}/{folder}/',
                            shell=True, check=True
                        )
                    except Exception as copy_err:
                        tb = traceback.format_exc()
                        self.error_label.config(text=f"Error copying {folder}: {copy_err}\n{tb}")
                        print(tb)
                        self.set_restore_progress(0, "Restore failed!")
                        return

            # Database restore - branch based on detected database type
            self.set_restore_progress(70, self.restore_steps[3])
            
            db_restore_success = False
            
            if dbtype == 'sqlite':
                # SQLite: restore by copying .db file (already done with data folder)
                db_restore_success = self.restore_sqlite_database(extract_dir, nextcloud_container, nextcloud_path)
            elif dbtype == 'mysql':
                # MySQL/MariaDB: restore from SQL dump
                db_restore_success = self.restore_mysql_database(extract_dir, db_container)
            elif dbtype == 'pgsql':
                # PostgreSQL: restore from SQL dump
                db_restore_success = self.restore_postgresql_database(extract_dir, db_container)
            else:
                # Unknown database type - show warning
                warning_msg = f"Warning: Unknown database type '{dbtype}'. Skipping database restore."
                self.error_label.config(text=warning_msg, fg="orange")
                print(warning_msg)
            
            if not db_restore_success and dbtype != 'sqlite':
                # For non-SQLite databases, if restore failed, we might want to continue with warning
                # rather than failing the entire restore
                warning_msg = f"Warning: Database restore had issues. Please check manually."
                self.error_label.config(text=warning_msg, fg="orange")
                print(warning_msg)
            
            # Update config.php with database credentials
            self.set_restore_progress(75, "Updating Nextcloud configuration ...")
            self.process_label.config(text="Updating config.php with database credentials ...")
            self.update_idletasks()
            try:
                self.update_config_php(nextcloud_container, db_container, dbtype)
            except Exception as config_err:
                # Show warning but continue
                warning_msg = f"Warning: Could not update config.php: {config_err}. You may need to configure manually."
                self.error_label.config(text=warning_msg, fg="orange")
                print(f"Warning: config.php update failed: {config_err}")

            # Validate that required files exist
            self.set_restore_progress(85, "Validating restored files ...")
            self.process_label.config(text="Validating config and data folders ...")
            self.update_idletasks()
            try:
                # Check if config.php exists
                check_config = subprocess.run(
                    f'docker exec {nextcloud_container} test -f {nextcloud_path}/config/config.php',
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                if check_config.returncode != 0:
                    error_msg = "Error: config.php not found after restore. The backup may be incomplete."
                    self.error_label.config(text=error_msg, fg="red")
                    self.set_restore_progress(0, "Restore failed!")
                    return
                
                # Check if data folder exists
                check_data = subprocess.run(
                    f'docker exec {nextcloud_container} test -d {nextcloud_path}/data',
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                if check_data.returncode != 0:
                    error_msg = "Error: data folder not found after restore. The backup may be incomplete."
                    self.error_label.config(text=error_msg, fg="red")
                    self.set_restore_progress(0, "Restore failed!")
                    return
                
                print("File validation successful: config.php and data folder exist.")
            except Exception as val_err:
                warning_msg = f"Warning: Could not validate files: {val_err}"
                self.error_label.config(text=warning_msg, fg="orange")
                print(f"Warning: file validation error: {val_err}")
            
            self.set_restore_progress(90, self.restore_steps[4])
            self.process_label.config(text="Setting permissions ...")
            self.update_idletasks()
            try:
                subprocess.run(
                    f'docker exec {nextcloud_container} chown -R www-data:www-data {nextcloud_path}/config {nextcloud_path}/data',
                    shell=True, check=True
                )
                print("Permissions set successfully.")
            except subprocess.CalledProcessError as perm_err:
                # Display warning but allow restore to continue
                warning_msg = f"Warning: Could not set file permissions (chown failed). You may need to set permissions manually."
                self.error_label.config(text=warning_msg, fg="orange")
                self.process_label.config(text=f"Permission warning (continuing restore): {perm_err}")
                print(f"Warning: chown failed but continuing restore: {perm_err}")
            except Exception as perm_err:
                # For other exceptions, show warning but also continue
                warning_msg = f"Warning: Error setting permissions: {perm_err}. You may need to set permissions manually."
                self.error_label.config(text=warning_msg, fg="orange")
                self.process_label.config(text=f"Permission warning (continuing restore): {perm_err}")
                print(f"Warning: permission error but continuing restore: {perm_err}")

            # Restart Nextcloud container to apply all changes
            self.set_restore_progress(95, "Restarting Nextcloud container ...")
            self.process_label.config(text="Restarting Nextcloud container ...")
            self.update_idletasks()
            try:
                subprocess.run(
                    f'docker restart {nextcloud_container}',
                    shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                print(f"Nextcloud container restarted successfully.")
                time.sleep(3)  # Give container time to start
            except Exception as restart_err:
                warning_msg = f"Warning: Could not restart Nextcloud container: {restart_err}"
                self.error_label.config(text=warning_msg, fg="orange")
                print(f"Warning: container restart failed: {restart_err}")

            self.set_restore_progress(100, self.restore_steps[5])
            self.process_label.config(text="Restore complete.")
            
            # Clear or show final status in error label
            if hasattr(self, "error_label") and self.error_label:
                current_text = self.error_label.cget("text")
                if current_text and "Warning" in current_text:
                    # Keep the warning message but add success note
                    pass  # Keep the warning visible
                else:
                    self.error_label.config(text="", fg="red")
            
            messagebox.showinfo("Restore Complete", "Your Nextcloud instance was successfully restored from backup.")
            shutil.rmtree(extract_dir, ignore_errors=True)
            self.show_landing()
        except Exception as e:
            tb = traceback.format_exc()
            self.set_restore_progress(0, "Restore failed!")
            self.error_label.config(text=f"Restore failed: {e}\n{tb}")
            print(tb)
            self.show_landing()

    # --- New instance logic ---
    def start_new_instance_workflow(self):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        self.status_label.config(text="Start New Nextcloud Instance")
        def proceed_to_port():
            self.show_port_entry()
        if not is_tool_installed('docker'):
            prompt_install_docker_link(self, self.status_label, proceed_to_port)
        else:
            self.show_port_entry()

    def show_port_entry(self):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        entry_frame = tk.Frame(self.body_frame)
        entry_frame.pack(pady=30)
        btn_back = tk.Button(entry_frame, text="Return to Main Menu", font=("Arial", 12), command=self.show_landing)
        btn_back.pack(pady=8)
        tk.Label(entry_frame, text="Select a port to access Nextcloud in your browser.", font=("Arial", 14)).pack(pady=8)
        tk.Label(entry_frame, text="The port determines the address you use to reach Nextcloud.\nFor example, if you choose port 8080, you'll go to http://localhost:8080", font=("Arial", 11), fg="gray").pack(pady=(0,10))
        ports = ["8080", "8888", "3000", "5000", "9000", "80", "Custom"]
        port_var = tk.StringVar(value=ports[0])
        port_combo = ttk.Combobox(entry_frame, textvariable=port_var, values=ports, font=("Arial", 13), state="readonly", width=10)
        port_combo.pack(pady=3)
        custom_port_entry = tk.Entry(entry_frame, font=("Arial", 13), width=10)
        custom_port_entry.pack_forget()

        def on_combo_change(event):
            if port_var.get() == "Custom":
                custom_port_entry.pack(pady=3)
                custom_port_entry.delete(0, tk.END)
                custom_port_entry.focus_set()
            else:
                custom_port_entry.pack_forget()

        port_combo.bind("<<ComboboxSelected>>", on_combo_change)

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
            start_btn.config(state="disabled")
            threading.Thread(target=self.launch_nextcloud_instance, args=(int(port),), daemon=True).start()
        start_btn.config(command=on_start)

    def launch_nextcloud_instance(self, port):
        try:
            self.status_label.config(text=f"Pulling nextcloud image and starting container on port {port}...")
            result = subprocess.run(
                f'docker run -d --name {NEXTCLOUD_CONTAINER_NAME} --network bridge -p {port}:80 {NEXTCLOUD_IMAGE}',
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
            self.status_label.config(text=f"Nextcloud started! Access it at {url}\nContainer ID: {container_id}")
            for widget in self.body_frame.winfo_children():
                widget.destroy()
            info_frame = tk.Frame(self.body_frame)
            info_frame.pack(pady=30)
            tk.Label(info_frame, text=f"Nextcloud is running!\nAccess it at:", font=("Arial", 14)).pack(pady=8)
            def open_localhost(event=None, link=url):
                webbrowser.open(link)
            link_label = tk.Label(
                info_frame,
                text=url,
                font=("Arial", 16, "bold"),
                fg="#3daee9",
                cursor="hand2"
            )
            link_label.pack(pady=8)
            link_label.bind("<Button-1>", lambda e: open_localhost(link=url))
            tk.Label(info_frame, text=f"Container ID: {container_id}", font=("Arial", 11), fg="gray").pack()
            tk.Button(info_frame, text="Return to Main Menu", font=("Arial", 13), command=self.show_landing).pack(pady=18)
        except Exception as e:
            tb = traceback.format_exc()
            messagebox.showerror("Error", f"Failed to start Nextcloud: {e}\n{tb}")
            print(tb)
            self.show_landing()

    def check_dependencies(self):
        pass # handled stepwise

if __name__ == "__main__":
    NextcloudRestoreWizard().mainloop()