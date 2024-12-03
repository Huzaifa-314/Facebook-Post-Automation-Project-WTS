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

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def join_groups(browser, group_uuids, account_index):
    """
    Navigate to Fewfeed and use the tool to join groups.
    :param browser: Selenium WebDriver instance
    :param group_uuids: List of group UUIDs.
    :param account_index: Index of the current account.
    """
    try:
        print("Navigating to Fewfeed to join groups...")
        # Navigate to the 'Join Groups' tool
        navigate_to_fewfeed_tool(browser, button_index=1)

        # Divide the group UUIDs into chunks of 80
        chunk_size = 80
        start_index = account_index * chunk_size
        end_index = min(start_index + chunk_size, len(group_uuids))  # Ensure end_index doesn't exceed list size
        group_chunk = group_uuids[start_index:end_index]

        if not group_chunk:
            print("No more groups to process for this account.")
            return

        # Locate the textarea and paste the groups
        print(f"Pasting {len(group_chunk)} groups for this account.")
        textarea = browser.find_element(By.CSS_SELECTOR, "textarea")  # Adjust selector if needed
        textarea.clear()
        textarea.send_keys("\n".join(group_chunk))

        # Locate the input tags
        inputs = browser.find_elements(By.TAG_NAME, "input")
        if len(inputs) < 4:
            raise Exception("Expected at least 4 input elements but found fewer.")

        # Set the values for thread, delay, and limit
        print("Configuring thread, delay, and limit inputs...")
        # inputs[0].clear()  # Thread input (default, no change needed)
        inputs[1].clear()  # Delay input
        inputs[1].send_keys("1")  # Set delay to 1
        inputs[2].clear()  # Limit input
        inputs[2].send_keys("80")  # Set limit to 80

        # Find the submit button
        print("Clicking the submit button to start joining groups...")
        submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        initial_text = submit_button.text

        # Click the submit button
        submit_button.click()

        # Wait for the button text to change back to its initial state
        print("Waiting for the groups joining process to complete...")
        WebDriverWait(browser, 300).until(
            lambda driver: driver.find_element(By.CSS_SELECTOR, "button[type='submit']").text == initial_text
        )

        print("Groups joining process completed successfully.")
    except Exception as e:
        print(f"An error occurred in 'join_groups': {e}")



def post_to_groups(browser, link):
    """
    Navigate to Fewfeed and use the tool to post in groups.
    :param browser: Selenium WebDriver instance
    :param link: The link to be posted.
    """
    try:
        print("Navigating to Fewfeed to post to groups...")
        # Navigate to the 'Post to Groups' tool
        navigate_to_fewfeed_tool(browser, button_index=0)

        # Locate the textarea with the placeholder "Write something..." and set its value to a space
        print("Configuring the post content...")
        textarea = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Write something...']"))
        )
        textarea.clear()
        textarea.send_keys(" ")

        # Locate the input with id "simple-search" and set its value to the provided link
        print("Adding the link to the input field...")
        link_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#simple-search"))
        )
        link_input.clear()
        link_input.send_keys(link)

        # Locate the parent div with class "relative" and wait for a new "relative" div to appear under it
        print("Waiting for the new 'relative' div to appear...")
        parent_div = link_input.find_element(By.XPATH, "./ancestor::div[contains(@class, 'relative')]")
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'relative')][2]"))
        )

        # Locate the Thread input and set it to 3
        # print("Increasing the thread...")
        # thread_input = WebDriverWait(browser, 10).until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, "//p[contains(text(), 'Thread')]/following-sibling::input[@type='number']")
        #     )
        # )
        # thread_input.clear()
        # thread_input.send_keys("3")

        # Locate the first checkbox and check it
        print("Selecting the checkbox...")
        checkbox = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox']"))
        )
        if not checkbox.is_selected():
            checkbox.click()

        # Locate and click the "Post" button
        print("Submitting the post...")
        post_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Post']"))
        )
        initial_text = post_button.text  # Store the initial button text
        
        post_button.click()

        # Wait for the button text to change
        print("Waiting for the post action to complete...")
        WebDriverWait(browser, 60).until(
            EC.text_to_be_present_in_element((By.XPATH, "//button[text()='Post']"), initial_text)
        )
        print("Post action completed successfully.")

    except Exception as e:
        print(f"An error occurred in 'post_to_groups': {e}")

