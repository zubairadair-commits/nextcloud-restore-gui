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

# ----------- FASTER EXTRACTION USING SYSTEM TAR -----------
def fast_extract_tar_gz(archive_path, extract_to):
    os.makedirs(extract_to, exist_ok=True)
    result = subprocess.run(
        f'tar --ignore-failed-read -xzf "{archive_path}" -C "{extract_to}"',
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    # Accept exit code 0 (success) or 1 (warnings/errors that were ignored)
    if result.returncode not in [0, 1]:
        raise Exception("Extraction failed: " + result.stderr)
# -----------------------------------------------------------

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
        frame.pack(pady=30)
        btn_back = tk.Button(frame, text="Return to Main Menu", font=("Arial", 12), command=self.show_landing)
        btn_back.pack(pady=8)
        tk.Label(frame, text="Enter password to encrypt your backup (leave blank for no encryption):", font=("Arial", 13)).pack(pady=10)
        pwd_entry = tk.Entry(frame, font=("Arial", 13), show="*", width=30)
        pwd_entry.pack(pady=8)
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
        
        # Show first page
        self.show_wizard_page(1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
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
        tk.Label(parent, text="Choose the backup file to restore (.tar.gz.gpg or .tar.gz)", font=("Arial", 10), fg="gray").pack(anchor="center")
        
        self.backup_entry = tk.Entry(parent, width=70, font=("Arial", 11))
        self.backup_entry.pack(pady=5, anchor="center")
        
        # Restore saved value if exists
        if 'backup_path' in self.wizard_data:
            self.backup_entry.insert(0, self.wizard_data['backup_path'])
        
        tk.Button(parent, text="Browse...", font=("Arial", 11), command=self.browse_backup).pack(pady=5, anchor="center")
        
        # Section 2: Decryption password - all centered
        tk.Label(parent, text="Step 2: Decryption Password", font=("Arial", 14, "bold")).pack(pady=(25, 5), anchor="center")
        tk.Label(parent, text="Enter password if backup is encrypted (.gpg)", font=("Arial", 10), fg="gray").pack(anchor="center")
        
        self.password_entry = tk.Entry(parent, show="*", font=("Arial", 12), width=40)
        self.password_entry.pack(pady=5, anchor="center")
        
        # Restore saved value if exists
        if 'password' in self.wizard_data:
            self.password_entry.insert(0, self.wizard_data['password'])
    
    def create_wizard_page2(self, parent):
        """Page 2: Database Configuration and Admin Credentials"""
        # Section 3: Database credentials - all centered
        tk.Label(parent, text="Step 3: Database Configuration", font=("Arial", 14, "bold")).pack(pady=(10, 5), anchor="center")
        tk.Label(parent, text="⚠️ Enter the database credentials from your ORIGINAL Nextcloud setup", font=("Arial", 10, "bold"), fg="red").pack(anchor="center")
        tk.Label(parent, text="These credentials are stored in your backup and must match exactly", font=("Arial", 9), fg="gray").pack(anchor="center")
        tk.Label(parent, text="The database will be automatically imported using these credentials", font=("Arial", 9), fg="gray").pack(anchor="center", pady=(0, 10))
        
        db_frame = tk.Frame(parent)
        db_frame.pack(pady=10, anchor="center")
        
        tk.Label(db_frame, text="Database Name:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.db_name_entry = tk.Entry(db_frame, font=("Arial", 11), width=30)
        self.db_name_entry.insert(0, self.wizard_data.get('db_name', POSTGRES_DB))
        self.db_name_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(db_frame, text="Must match your original database name", font=("Arial", 9), fg="gray").grid(row=0, column=2, sticky="w", padx=(5, 0))
        
        tk.Label(db_frame, text="Database User:", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.db_user_entry = tk.Entry(db_frame, font=("Arial", 11), width=30)
        self.db_user_entry.insert(0, self.wizard_data.get('db_user', POSTGRES_USER))
        self.db_user_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(db_frame, text="Must match your original database user", font=("Arial", 9), fg="gray").grid(row=1, column=2, sticky="w", padx=(5, 0))
        
        tk.Label(db_frame, text="Database Password:", font=("Arial", 11)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.db_password_entry = tk.Entry(db_frame, show="*", font=("Arial", 11), width=30)
        self.db_password_entry.insert(0, self.wizard_data.get('db_password', POSTGRES_PASSWORD))
        self.db_password_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(db_frame, text="Must match your original database password", font=("Arial", 9), fg="gray").grid(row=2, column=2, sticky="w", padx=(5, 0))
        
        # Section 4: Nextcloud admin credentials - all centered
        tk.Label(parent, text="Step 4: Nextcloud Admin Credentials", font=("Arial", 14, "bold")).pack(pady=(25, 5), anchor="center")
        tk.Label(parent, text="Admin credentials for Nextcloud instance", font=("Arial", 10), fg="gray").pack(anchor="center")
        
        admin_frame = tk.Frame(parent)
        admin_frame.pack(pady=10, anchor="center")
        
        tk.Label(admin_frame, text="Admin Username:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.admin_user_entry = tk.Entry(admin_frame, font=("Arial", 11), width=30)
        self.admin_user_entry.insert(0, self.wizard_data.get('admin_user', 'admin'))
        self.admin_user_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(admin_frame, text="Admin Password:", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.admin_password_entry = tk.Entry(admin_frame, show="*", font=("Arial", 11), width=30)
        self.admin_password_entry.insert(0, self.wizard_data.get('admin_password', 'admin'))
        self.admin_password_entry.grid(row=1, column=1, padx=5, pady=5)
    
    def create_wizard_page3(self, parent):
        """Page 3: Container Configuration"""
        # Section 5: Container configuration - all centered
        tk.Label(parent, text="Step 5: Container Configuration", font=("Arial", 14, "bold")).pack(pady=(10, 5), anchor="center")
        tk.Label(parent, text="Configure Nextcloud container settings", font=("Arial", 10), fg="gray").pack(anchor="center")
        
        container_frame = tk.Frame(parent)
        container_frame.pack(pady=10, anchor="center")
        
        tk.Label(container_frame, text="Container Name:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.container_name_entry = tk.Entry(container_frame, font=("Arial", 11), width=30)
        self.container_name_entry.insert(0, self.wizard_data.get('container_name', NEXTCLOUD_CONTAINER_NAME))
        self.container_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(container_frame, text="Container Port:", font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.container_port_entry = tk.Entry(container_frame, font=("Arial", 11), width=30)
        self.container_port_entry.insert(0, self.wizard_data.get('container_port', '9000'))
        self.container_port_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Option to use existing container - centered
        self.use_existing_var = tk.BooleanVar(value=self.wizard_data.get('use_existing', False))
        tk.Checkbutton(
            parent, 
            text="Use existing Nextcloud container if found", 
            variable=self.use_existing_var,
            font=("Arial", 11)
        ).pack(pady=15, anchor="center")
        
        # Add informative text about what will happen during restore
        info_frame = tk.Frame(parent, bg="#e8f4f8", relief="ridge", borderwidth=2)
        info_frame.pack(pady=20, padx=30, fill="x")
        
        tk.Label(info_frame, text="ℹ️ The restore process will automatically:", font=("Arial", 11, "bold"), bg="#e8f4f8").pack(pady=(10, 5))
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
            tk.Label(info_frame, text=info, font=("Arial", 10), bg="#e8f4f8", anchor="w").pack(anchor="w", padx=20, pady=2)
        tk.Label(info_frame, text="", bg="#e8f4f8").pack(pady=5)  # Spacing
    
    def wizard_navigate(self, direction):
        """Navigate between wizard pages, saving current page data"""
        # Save current page data
        self.save_wizard_page_data()
        
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

    def browse_backup(self):
        path = filedialog.askopenfilename(
            title="Select .tar.gz.gpg backup",
            filetypes=[("PGP Archive", "*.tar.gz.gpg"), ("All files", "*.*")]
        )
        if path:
            self.backup_entry.delete(0, tk.END)
            self.backup_entry.insert(0, path)

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
        
        # Validate database credentials
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
                self.error_label.config(text=f"Decryption failed: {e}\n{tb}")
                print(tb)
                shutil.rmtree(extract_temp, ignore_errors=True)
                return None

        # Step 2: FAST EXTRACTION using system tar with progress monitoring
        try:
            self.set_restore_progress(10, "Extracting backup archive (fast) ...")
            self.update_idletasks()
            
            # Start extraction in a separate thread-like approach with progress updates
            extraction_done = [False]  # Use list for mutable flag
            
            def do_extraction():
                try:
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
            self.error_label.config(text=f"Extraction failed: {e}\n{tb}")
            print(tb)
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

    def update_config_php(self, nextcloud_container, db_container):
        """Update config.php with database credentials and admin settings"""
        config_updates = f"""
docker exec {nextcloud_container} bash -c "cat > /tmp/update_config.php << 'EOFPHP'
<?php
\\$configFile = '/var/www/html/config/config.php';
if (file_exists(\\$configFile)) {{
    \\$config = include(\\$configFile);
    
    // Update database configuration
    \\$config['dbtype'] = 'pgsql';
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

            self.set_restore_progress(20, self.restore_steps[1])
            # Start database container first (needed for Nextcloud container linking)
            db_container = self.ensure_db_container()
            if not db_container:
                self.set_restore_progress(0, "Restore failed!")
                return
            
            # Start Nextcloud container (linked to database)
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

            self.set_restore_progress(70, self.restore_steps[3])
            sql_path = os.path.join(extract_dir, "nextcloud-db.sql")
            if os.path.isfile(sql_path):
                self.process_label.config(text="Restoring database (this may take a few minutes) ...")
                self.update_idletasks()
                # Use credentials from GUI
                restore_cmd = f'docker exec -i {db_container} bash -c "PGPASSWORD={self.restore_db_password} psql -U {self.restore_db_user} -d {self.restore_db_name}"'
                try:
                    with open(sql_path, "rb") as f:
                        proc = subprocess.Popen(restore_cmd, shell=True, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = proc.communicate()
                        if proc.returncode != 0:
                            error_msg = stderr.decode('utf-8', errors='replace') if stderr else "Unknown error"
                            self.error_label.config(text=f"Database restore failed: {error_msg}")
                            self.set_restore_progress(0, "Restore failed!")
                            return
                    
                    # Validate that database tables were imported
                    self.process_label.config(text="Validating database restore ...")
                    self.update_idletasks()
                    check_cmd = f'docker exec {db_container} bash -c "PGPASSWORD={self.restore_db_password} psql -U {self.restore_db_user} -d {self.restore_db_name} -c \'\\dt\'"'
                    result = subprocess.run(check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.returncode == 0 and "oc_" in result.stdout:
                        print(f"Database validation successful. Tables found.")
                    else:
                        warning_msg = "Warning: Could not validate database tables. Please check manually."
                        self.error_label.config(text=warning_msg, fg="orange")
                        print(f"Warning: Database validation unclear: {result.stdout}")
                        
                except Exception as db_err:
                    tb = traceback.format_exc()
                    self.error_label.config(text=f"Database restore error: {db_err}\n{tb}")
                    print(tb)
                    self.set_restore_progress(0, "Restore failed!")
                    return
            else:
                warning_msg = "Warning: No database backup file (nextcloud-db.sql) found in backup. Skipping database restore."
                self.error_label.config(text=warning_msg, fg="orange")
                print(warning_msg)
            
            # Update config.php with database credentials
            self.set_restore_progress(75, "Updating Nextcloud configuration ...")
            self.process_label.config(text="Updating config.php with database credentials ...")
            self.update_idletasks()
            try:
                self.update_config_php(nextcloud_container, db_container)
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