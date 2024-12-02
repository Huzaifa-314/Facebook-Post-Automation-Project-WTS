import sys
import os

# Add the parent directory (project root) to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.browser import setup_browser_with_extension
from src.extension import install_extension, get_extension_id

if __name__ == "__main__":
    extension_zip = "extensions/selected_extension.zip"

    # Install the extension
    unpacked_path = install_extension(extension_zip)

    # Launch browser with the extension
    browser = setup_browser_with_extension(unpacked_path)

    # Get and print the extension ID
    try:
        extension_id = get_extension_id(browser)
        print(f"Extension loaded with ID: {extension_id}")
    finally:
        browser.quit()

