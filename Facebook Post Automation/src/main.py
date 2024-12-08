import logging
from itertools import cycle
from src.browser import setup_browser_with_extension, login_to_facebook
from src.fewfeed import join_groups, post_to_groups
from ui.inputs import BotUI
from ui.status import StatusUI  # Import the Status UI class
import tkinter as tk
import queue

# Setup logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def process_account(status_queue, inputs, username, link, group_uuids, account_index):
    """
    Process a single account: login to Facebook, join groups, and post.
    Updates the status_queue with the progress for the corresponding thread.
    """
    status = {"account": username, "status": "Initializing"}
    status_queue.put(status)

    try:
        # Update status
        status["status"] = "Launching browser"
        status_queue.put(status)

        # Install and load the extensions
        browser = setup_browser_with_extension([inputs["extension_file_1"], inputs["extension_file_2"]])

        # Update status
        status["status"] = "Logging in to Facebook"
        status_queue.put(status)

        # Log into Facebook
        login_to_facebook(browser, username, inputs["password"])
        status["status"] = "Login successful"
        status_queue.put(status)

        # Fewfeed logic: join groups and post to groups
        status["status"] = "Joining groups"
        status_queue.put(status)
        join_groups(browser, group_uuids, account_index)

        status["status"] = "Posting to groups"
        status_queue.put(status)
        post_to_groups(browser, link)

        status["status"] = "Completed"
        status_queue.put(status)
    except Exception as e:
        logging.error(f"Error processing account {username}: {e}")
        status["status"] = f"Error: {e}"
        status_queue.put(status)
    finally:
        browser.quit()

def start_browser_and_login(inputs):
    """
    Start the browser with the given extensions, log in to Facebook, and perform actions.
    """
    try:
        # Extract inputs from UI
        accounts_file = inputs["accounts_file"]
        links_file = inputs["links_file"]
        group_uuids_file = inputs["group_uuids_file"]

        # Read accounts and links from the files
        with open(accounts_file, "r") as f:
            usernames = f.read().splitlines()
        with open(links_file, "r") as f:
            links = f.read().splitlines()
        with open(group_uuids_file, "r") as f:
            group_uuids = f.read().splitlines()

        if not usernames:
            raise ValueError("No usernames found in the accounts file!")
        if not links:
            raise ValueError("Links file is empty!")

        # Use links in a round-robin fashion
        link_cycle = cycle(links)

        # Create a queue for status updates
        status_queue = queue.Queue()

        # Launch Status UI
        status_ui = StatusUI(status_queue, len(usernames), 1)  # 1 thread for sequential execution
        status_ui.start()

        # Process accounts sequentially
        for account_index, username in enumerate(usernames):
            link = next(link_cycle)
            process_account(status_queue, inputs, username, link, group_uuids, account_index)

        status_queue.put({"status": "All accounts processed successfully."})

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
    def on_closing():
        print("UI closed without collecting inputs. Exiting...")
        root.destroy()
        raise SystemExit

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

    # Collect inputs after UI is closed
    inputs = app.get_inputs()
    return inputs

if __name__ == "__main__":
    try:
        # Start the UI and get the inputs
        user_inputs = start_ui()

        # Start the browser and log in to Facebook using the collected inputs
        start_browser_and_login(user_inputs)
    except SystemExit:
        print("Program exited gracefully after UI closure.")
