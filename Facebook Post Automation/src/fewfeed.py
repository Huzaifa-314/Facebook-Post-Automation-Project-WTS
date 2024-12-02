import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def navigate_to_fewfeed_tool(browser, button_index):
    """
    Navigate to the Fewfeed tool and click on the specified button.
    :param browser: Selenium WebDriver instance
    :param button_index: Index of the button to click (0-based, 0 for 'post', 1 for 'join groups')
    """
    browser.execute_script("window.open('');")
    browser.switch_to.window(browser.window_handles[-1])
    browser.get("https://v2.fewfeed.com/")
    wait = WebDriverWait(browser, 10)

    # Wait for the buttons to load
    buttons = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.bg-blue-400"))
    )

    if len(buttons) <= button_index:
        raise Exception(f"Expected at least {button_index + 1} buttons, but found {len(buttons)}.")

    # Click the specified button
    buttons[button_index].click()
    print(f"Clicked the button with index {button_index}.")
    time.sleep(2)  # Wait for navigation

def join_groups(browser):
    """
    Navigate to Fewfeed and use the tool to join groups.
    :param browser: Selenium WebDriver instance
    """
    print("Navigating to Fewfeed to join groups...")
    navigate_to_fewfeed_tool(browser, button_index=1)
    print("Ready to interact with the 'Join Groups' tool.")
    time.sleep(10)

def post_to_groups(browser):
    """
    Navigate to Fewfeed and use the tool to post in groups.
    :param browser: Selenium WebDriver instance
    """
    print("Navigating to Fewfeed to post to groups...")
    navigate_to_fewfeed_tool(browser, button_index=0)
    print("Ready to interact with the 'Post to Groups' tool.")
