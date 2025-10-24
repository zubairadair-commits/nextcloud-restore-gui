#!/usr/bin/env python3
"""
Visual demonstration of admin username extraction feature.

This demo shows:
1. How the admin username is extracted from the database
2. How it's displayed in the completion dialog
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def demo_admin_username_display():
    """Demonstrate the admin username display in completion dialog"""
    print("=" * 70)
    print("Admin Username Extraction Feature Demo")
    print("=" * 70)
    print()
    
    print("FEATURE OVERVIEW:")
    print("-" * 70)
    print("After restoring a Nextcloud backup, the system now:")
    print("1. Queries the restored database to find admin users")
    print("2. Extracts the admin username from oc_users/oc_group_user tables")
    print("3. Displays it in the completion dialog")
    print()
    
    print("DATABASE QUERIES BY TYPE:")
    print("-" * 70)
    print()
    
    print("SQLite:")
    print('  Query: SELECT u.uid FROM oc_users u')
    print('         INNER JOIN oc_group_user g ON u.uid = g.uid')
    print("         WHERE g.gid = 'admin' LIMIT 1;")
    print('  Command: docker exec <container> sqlite3 /var/www/html/data/nextcloud.db')
    print()
    
    print("MySQL/MariaDB:")
    print('  Query: SELECT u.uid FROM oc_users u')
    print('         INNER JOIN oc_group_user g ON u.uid = g.uid')
    print("         WHERE g.gid = 'admin' LIMIT 1;")
    print('  Command: docker exec <db_container> mysql -u<user> -p<pass> <dbname>')
    print()
    
    print("PostgreSQL:")
    print('  Query: SELECT u.uid FROM oc_users u')
    print('         INNER JOIN oc_group_user g ON u.uid = g.uid')
    print("         WHERE g.gid = 'admin' LIMIT 1;")
    print('  Command: docker exec <db_container> psql -U <user> -d <dbname>')
    print()
    
    print("COMPLETION DIALOG ENHANCEMENT:")
    print("-" * 70)
    print()
    print("BEFORE (without admin username):")
    print("┌────────────────────────────────────────────────┐")
    print("│         ✅ Restore Complete!                   │")
    print("│                                                │")
    print("│  Your Nextcloud instance has been             │")
    print("│  successfully restored from backup.           │")
    print("│                                                │")
    print("│  Container: nextcloud-app                     │")
    print("│  Port: 8080                                   │")
    print("│                                                │")
    print("│  [🌐 Open Nextcloud in Browser]               │")
    print("│  [Return to Main Menu]                        │")
    print("└────────────────────────────────────────────────┘")
    print()
    
    print("AFTER (with admin username extracted):")
    print("┌────────────────────────────────────────────────┐")
    print("│         ✅ Restore Complete!                   │")
    print("│                                                │")
    print("│  Your Nextcloud instance has been             │")
    print("│  successfully restored from backup.           │")
    print("│                                                │")
    print("│  Container: nextcloud-app                     │")
    print("│  Port: 8080                                   │")
    print("│                                                │")
    print("│  Log in with your previous admin credentials. │")
    print("│  Your admin username is: john_admin           │")
    print("│                                                │")
    print("│  [🌐 Open Nextcloud in Browser]               │")
    print("│  [Return to Main Menu]                        │")
    print("└────────────────────────────────────────────────┘")
    print()
    
    print("ERROR HANDLING:")
    print("-" * 70)
    print("If admin username cannot be extracted:")
    print("  • Timeout occurs (> 10 seconds)")
    print("  • Database query fails")
    print("  • No admin users found in database")
    print()
    print("The system will:")
    print("  ✓ Log a warning message")
    print("  ✓ Continue with restore completion")
    print("  ✓ Show completion dialog WITHOUT admin username")
    print("  ✓ Not fail the entire restore process")
    print()
    
    print("SECURITY CONSIDERATIONS:")
    print("-" * 70)
    print("  ✓ Only displays username (not password)")
    print("  ✓ Uses existing database credentials from restore")
    print("  ✓ Queries are read-only (SELECT only)")
    print("  ✓ Timeout prevents indefinite hanging")
    print("  ✓ Errors are logged but don't block restore")
    print()
    
    print("USER EXPERIENCE BENEFITS:")
    print("-" * 70)
    print("  • Users immediately know which account to log in with")
    print("  • Reduces confusion about admin credentials")
    print("  • Helpful for backups from different systems")
    print("  • No need to remember or guess admin username")
    print("  • Especially useful for inherited/old backups")
    print()
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)


def show_code_snippets():
    """Show relevant code snippets"""
    print("\n\nKEY CODE SNIPPETS:")
    print("=" * 70)
    
    print("\n1. Admin Username Extraction Method:")
    print("-" * 70)
    print("""
    def extract_admin_username(self, container_name, dbtype):
        '''Extract admin username from the restored Nextcloud database.'''
        try:
            if dbtype == 'sqlite':
                query = "SELECT u.uid FROM oc_users u ..."
                cmd = f"docker exec {container_name} sqlite3 ..."
                result = subprocess.run(cmd, timeout=10, ...)
                
            elif dbtype in ['mysql', 'mariadb']:
                query = "SELECT u.uid FROM oc_users u ..."
                cmd = f"docker exec {db_container} mysql ..."
                result = subprocess.run(cmd, timeout=10, ...)
                
            elif dbtype == 'pgsql':
                query = "SELECT u.uid FROM oc_users u ..."
                cmd = f"docker exec {db_container} psql ..."
                result = subprocess.run(cmd, timeout=10, ...)
                
            return admin_username if found else None
        except Exception as e:
            logger.warning(f"Error extracting admin username: {e}")
            return None
    """)
    
    print("\n2. Updated Completion Dialog:")
    print("-" * 70)
    print("""
    def show_restore_completion_dialog(self, container_name, port, admin_username=None):
        ...
        # Admin credentials info (if available)
        if admin_username:
            admin_info = tk.Label(
                completion_frame,
                text=f"Log in with your previous admin credentials.\\n"
                     f"Your admin username is: {admin_username}",
                font=("Arial", 12, "bold"),
                bg=self.theme_colors['bg'],
                fg="#3daee9"
            )
            admin_info.pack(pady=15)
    """)
    
    print("\n3. Extraction Call in Restore Thread:")
    print("-" * 70)
    print("""
    # Extract admin username from restored database
    admin_username = None
    try:
        logger.info("Step 7/7: Extracting admin username...")
        time.sleep(1)  # Brief delay for database to be ready
        admin_username = self.extract_admin_username(nextcloud_container, dbtype)
        if admin_username:
            logger.info(f"Successfully extracted: {admin_username}")
    except Exception as extract_err:
        logger.warning(f"Failed to extract admin username: {extract_err}")
    
    # Show completion dialog with admin username
    self.show_restore_completion_dialog(
        nextcloud_container, 
        self.restore_container_port, 
        admin_username
    )
    """)


def main():
    """Run the demo"""
    demo_admin_username_display()
    
    # Ask if user wants to see code snippets
    print("\nWould you like to see the code snippets? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response == 'y':
            show_code_snippets()
    except (EOFError, KeyboardInterrupt):
        print("\nDemo ended.")
    
    print("\n\nThank you for viewing the demo!")
    return True


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nDemo error: {e}")
        sys.exit(1)
