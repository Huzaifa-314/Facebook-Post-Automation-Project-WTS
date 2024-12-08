from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import time

def setup_browser_with_extension(extension_files):
    """Setup the browser with the given extension."""
    options = webdriver.ChromeOptions()
    for ext in extension_files:
        options.add_extension(ext)  # Load each extension
    
    browser = webdriver.Chrome(options=options)
    
    # Set the browser size to a standard resolution (non-mobile)
    browser.set_window_size(200, 650)  # Set to a larger screen size
    return browser

def login_to_facebook(browser, username, password):
    """Logs into Facebook using the given username and password."""
    browser.get("https://www.facebook.com")
    time.sleep(0)  # Wait for the page to load

    # Find the username and password fields
    email_field = browser.find_element(By.ID, "email")
    password_field = browser.find_element(By.ID, "pass")

    # Input username and password
    email_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)  # Hit Enter to log in

    time.sleep(0)  # Wait for login to complete

    # Check if login was successful
    if "Facebook" in browser.title:
        print(f"Successfully logged in as {username}")
    else:
        print(f"Login failed for {username}")


def open_extension_page_with_retry(browser, extension_id, retries=3, delay=5):
    for attempt in range(retries):
        try:
            browser.get(f"chrome-extension://{extension_id}/index.html")
            print("Navigated to extension page successfully.")
            return
        except WebDriverException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    raise Exception("Failed to open extension page after multiple attempts.")

def open_extension_page(browser, extension_id):
    """
    Navigate to the extension's page using its extension ID and handle issues.
    """
    # Ensure a new tab is open for the extension
    browser.execute_script("window.open('');")
    browser.switch_to.window(browser.window_handles[-1])

    # Construct and navigate to the extension page
    extension_url = f"chrome-extension://{extension_id}/index.html"

    # Retry logic
    try:
        open_extension_page_with_retry(browser, extension_id)
    except Exception as e:
        print(f"Failed to navigate to the extension page: {e}")
        browser.quit()
        raise

    print(f"Navigated to extension page: {extension_url}")


