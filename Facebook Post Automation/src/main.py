import logging
from itertools import cycle
from src.browser import setup_browser_with_extension, login_to_facebook, open_extension_page
from src.extension import *
from src.fewfeed import join_groups, post_to_groups
import time
import tkinter as tk
from ui.inputs import BotUI  # Import the UI class from inputs.py

# Setup logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def start_browser_and_login(inputs):
    """
    Start the browser with the given extensions, log in to Facebook, and perform actions.
    """
    try:
        # Extract inputs from UI
        threads = inputs["threads"]
        extension_file_1 = inputs["extension_file_1"]
        extension_file_2 = inputs["extension_file_2"]
        accounts_file = inputs["accounts_file"]
        links_file = inputs["links_file"]
        group_uuids_file = inputs["group_uuids_file"]
        password = inputs["password"]

        # Read accounts and links from the files
        with open(accounts_file, "r") as f:
            usernames = f.read().splitlines()
        with open(links_file, "r") as f:
            links = f.read().splitlines()
        # Load group UUIDs
        with open(group_uuids_file, "r") as f:
            group_uuids = f.read().splitlines()

        if not usernames:
            raise ValueError("No usernames found in the accounts file!")
        if not links:
            raise ValueError("Links file is empty!")
        
        # Use links in a round-robin fashion if there are fewer links than accounts
        link_cycle = cycle(links)

        # Process each account
        for account_index,username in enumerate(usernames):
            link = next(link_cycle)
            logging.info(f"Processing account: {username}")
            print(f"Processing account: {username}")

            # Install and load the extensions
            logging.info("Installing and loading extensions")
            browser = setup_browser_with_extension([extension_file_1, extension_file_2])

            # Log into Facebook
            logging.info(f"Logging into Facebook with username: {username}")
            login_to_facebook(browser, username, password)

            logging.info(f"Successfully logged in with account: {username}")
            print(f"Successfully logged in with account: {username}")

            ############################################
            # Fewfeed logic: join groups and post to groups
            logging.info("Using Fewfeed to join groups")
            join_groups(browser, group_uuids, account_index)
            logging.info("Using Fewfeed to post to groups")
            post_to_groups(browser,link)

            ########################################
            # JERA extension logic
            # logging.info("Navigating to JERA extension page")
            # open_extension_page(browser, extension_file_1)  # Use the JERA extension
            
            # logging.info("Clicking the 'Link' button in JERA extension")
            # click_the_link_button(browser)

            # logging.info(f"Handling link input: {link}")
            # handle_link_input(browser, link)

            # Keep browser open for verification (optional)
            time.sleep(1)

            # Close browser after processing each account
            browser.quit()

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

def start_ui():
    """
    Start the Tkinter UI to gather user inputs.
    """
    root = tk.Tk()
    app = BotUI(root)

    # Add a protocol handler for the window close event
    inputs = {}

    def on_closing():
        print("UI closed without collecting inputs. Exiting...")
        root.destroy()  # Destroy the Tkinter root window
        raise SystemExit  # Exit the script gracefully

    root.protocol("WM_DELETE_WINDOW", on_closing)  # Attach the on_closing function to the close button
    root.mainloop()

    # Collect inputs after UI is closed
    inputs = app.get_inputs()  # This function should retrieve the validated inputs from the UI
    return inputs

if __name__ == "__main__":
    try:
        # Start the UI and get the inputs
        user_inputs = start_ui()

        # Start the browser and log in to Facebook using the collected inputs
        start_browser_and_login(user_inputs)
    except SystemExit:
        print("Program exited gracefully after UI closure.")

