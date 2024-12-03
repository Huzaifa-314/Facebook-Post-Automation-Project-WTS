import zipfile
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def install_extension(zip_path, unpack_dir="extensions/unpacked"):
    """
    Unzips the extension file to the specified directory.
    :param zip_path: Path to the extension zip file.
    :param unpack_dir: Directory where the extension will be unpacked.
    :return: Path to the unpacked extension directory.
    """
    if not os.path.exists(unpack_dir):
        os.makedirs(unpack_dir)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(unpack_dir)

    return unpack_dir


def get_extension_id(browser):
    """
    Retrieve the dynamic ID of the installed extension by enabling developer mode.
    :param browser: WebDriver instance with the extension loaded.
    :return: Extension's unique ID.
    """
    browser.execute_script("window.open('');")  # Open a new tab
    browser.switch_to.window(browser.window_handles[-1])
    browser.get("chrome://extensions/")  # Go to the Chrome extensions page

    # Enable developer mode using JavaScript to traverse shadow DOM
    try:
        print("Attempting to enable developer mode...")
        # Use JavaScript to toggle developer mode
        browser.execute_script("""
            document.querySelector("body > extensions-manager")
            .shadowRoot.querySelector("#toolbar")
            .shadowRoot.querySelector("#devMode").click();
        """)
        print("Developer mode enabled successfully.")
    except Exception as e:
        print("Failed to enable developer mode:", e)
        raise Exception("Could not find or enable the developer mode toggle.")

    # Retrieve the extension ID using shadow DOM traversal
    try:
        print("Retrieving the extension ID...")
        extension_id_raw = browser.execute_script("""
            return document.querySelector("body > extensions-manager")
            .shadowRoot.querySelector("extensions-item-list")
            .shadowRoot.querySelector("extensions-item")
            .shadowRoot.querySelector("#extension-id").textContent.trim();
        """)
        
        # Remove "ID: " prefix
        extension_id = extension_id_raw.replace("ID: ", "")
        print(f"Extension ID retrieved: {extension_id}")
        return extension_id
    except Exception as e:
        print("Failed to retrieve the extension ID:", e)
        raise Exception("Could not find the extension ID element.")
    
def click_the_link_button(browser):
    # Wait for the LINK button to be clickable
    wait = WebDriverWait(browser, 20)  # Adjust the timeout as needed
    link_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ui.instagram.mini.fluid.button"))
    )
    
    # Click the LINK button
    link_button.click()
    print("LINK button clicked successfully.")



def handle_link_input(browser, link):
    """
    Handles the popup and inputs the provided link into the input field.
    :param browser: Selenium WebDriver instance.
    :param link: The link to be pasted into the input field.
    """
    try:
        # Wait for the popup and locate the input field
        wait = WebDriverWait(browser, 10)
        input_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Link facebook post - youtube - your website ...etc']"))
        )

        # Input the link
        input_field.clear()
        input_field.send_keys(link)
        print(f"Link '{link}' has been pasted into the input field.")

        # Optional: Submit or confirm the input if needed
        # For example, clicking a confirm button if present
        # confirm_button = browser.find_element(By.CSS_SELECTOR, "button.confirm-class")  # Replace with actual selector
        # confirm_button.click()

    except Exception as e:
        print(f"Failed to input the link: {e}")
        raise
