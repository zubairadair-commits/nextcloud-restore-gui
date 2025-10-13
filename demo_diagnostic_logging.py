#!/usr/bin/env python3
"""
Demonstration of diagnostic logging for Tailscale pages.
Simulates page rendering and theme changes to show logging output.
"""

import logging
import traceback

# Configure logging the same way as in the main application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockApp:
    """Mock application to demonstrate logging"""
    def __init__(self):
        self.current_theme = 'light'
        self.current_page = 'landing'
    
    def show_landing(self):
        logger.info("Showing landing page")

def log_page_render(page_name):
    """
    Decorator to add diagnostic logging and error handling to page rendering methods.
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
                # In real app, would show error dialog
                print(f"\n[Error Dialog Would Show]: Failed to render {page_name} page:\n{str(e)}\nCheck nextcloud_restore_gui.log for details.\n")
                # Try to show landing page as fallback
                try:
                    logger.info(f"{page_name}: Attempting fallback to landing page")
                    self.show_landing()
                except:
                    logger.error(f"{page_name}: Fallback to landing page also failed")
        return wrapper
    return decorator

class DemoApp(MockApp):
    """Demo application with logged methods"""
    
    @log_page_render("TAILSCALE WIZARD")
    def show_tailscale_wizard(self):
        """Show the Tailscale setup wizard main page"""
        logger.info("TAILSCALE WIZARD: Setting current_page to 'tailscale_wizard'")
        self.current_page = 'tailscale_wizard'
        logger.info("TAILSCALE WIZARD: Clearing existing widgets")
        logger.info("TAILSCALE WIZARD: Creating container frame")
        logger.info("TAILSCALE WIZARD: Creating canvas and scrollbar")
        logger.info("TAILSCALE WIZARD: Creating content widgets")
        logger.info("TAILSCALE WIZARD: All widgets created successfully")
    
    @log_page_render("TAILSCALE CONFIG")
    def show_tailscale_config(self):
        """Show Tailscale configuration wizard"""
        logger.info("TAILSCALE CONFIG: Setting current_page to 'tailscale_config'")
        self.current_page = 'tailscale_config'
        logger.info("TAILSCALE CONFIG: Clearing existing widgets")
        logger.info("TAILSCALE CONFIG: Creating container frame")
        logger.info("TAILSCALE CONFIG: Getting Tailscale network info")
        logger.info("TAILSCALE CONFIG: Creating form widgets")
        logger.info("TAILSCALE CONFIG: All widgets created successfully")
    
    @log_page_render("TAILSCALE WIZARD")
    def show_tailscale_wizard_with_error(self):
        """Simulate a page render with an error"""
        logger.info("TAILSCALE WIZARD: Setting current_page to 'tailscale_wizard'")
        self.current_page = 'tailscale_wizard'
        logger.info("TAILSCALE WIZARD: Clearing existing widgets")
        logger.info("TAILSCALE WIZARD: Creating container frame")
        # Simulate an error
        raise AttributeError("'NoneType' object has no attribute 'pack'")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        old_theme = self.current_theme
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        logger.info(f"THEME TOGGLE: Changed theme from {old_theme} to {self.current_theme}")
        logger.info("THEME TOGGLE: Applied theme to UI elements")
        logger.info(f"THEME TOGGLE: Refreshing current page: {self.current_page}")
        self.refresh_current_page()
    
    def refresh_current_page(self):
        """Refresh the current page after theme change"""
        logger.info(f"REFRESH PAGE: Starting refresh for page: {self.current_page}")
        if self.current_page == 'tailscale_wizard':
            logger.info("REFRESH PAGE: Calling show_tailscale_wizard()")
            self.show_tailscale_wizard()
        elif self.current_page == 'tailscale_config':
            logger.info("REFRESH PAGE: Calling show_tailscale_config()")
            self.show_tailscale_config()
        else:
            logger.info("REFRESH PAGE: Calling show_landing() (default)")
            self.show_landing()
        logger.info("REFRESH PAGE: Page refresh complete")

def main():
    print("\n" + "=" * 70)
    print("Diagnostic Logging Demonstration")
    print("=" * 70)
    print("\nThis demonstrates the logging added to Tailscale pages.")
    print("All output below would appear in nextcloud_restore_gui.log")
    print("=" * 70)
    print()
    
    app = DemoApp()
    
    # Scenario 1: Navigate to Tailscale wizard
    print("\n📋 SCENARIO 1: Navigate to Tailscale Wizard")
    print("-" * 70)
    app.show_tailscale_wizard()
    
    # Scenario 2: Toggle theme while on Tailscale wizard
    print("\n📋 SCENARIO 2: Toggle Theme (Light → Dark)")
    print("-" * 70)
    app.toggle_theme()
    
    # Scenario 3: Navigate to config page
    print("\n📋 SCENARIO 3: Navigate to Tailscale Config")
    print("-" * 70)
    app.show_tailscale_config()
    
    # Scenario 4: Toggle theme back
    print("\n📋 SCENARIO 4: Toggle Theme (Dark → Light)")
    print("-" * 70)
    app.toggle_theme()
    
    # Scenario 5: Simulate an error
    print("\n📋 SCENARIO 5: Page Render Error (with Fallback)")
    print("-" * 70)
    app.show_tailscale_wizard_with_error()
    
    print("\n" + "=" * 70)
    print("Demonstration Complete")
    print("=" * 70)
    print("\n✅ Key Features Demonstrated:")
    print("  • Page rendering start/complete logging")
    print("  • Theme change tracking")
    print("  • Page refresh with current page preservation")
    print("  • Error catching with full stack trace")
    print("  • Automatic fallback to landing page on error")
    print("\n📁 In production, all this would be in: nextcloud_restore_gui.log")
    print()

if __name__ == '__main__':
    main()
