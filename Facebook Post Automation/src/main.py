import logging
from itertools import cycle
import tkinter as tk
import queue


import tkinter as tk
from tkinter import ttk
from queue import Queue, Empty
import threading
import time

class StatusUI(threading.Thread):
    """
    Status UI for monitoring thread statuses and displaying logs.
    """
    def __init__(self, status_queue, total_threads, max_threads):
        threading.Thread.__init__(self)
        self.status_queue = status_queue
        self.total_threads = total_threads
        self.max_threads = max_threads
        self.root = None
        self.log_text = None
        self.thread_boxes = []
        self.running = True
        self.browsers = []  # This will store browser instances for each thread

    def run(self):
        self.root = tk.Tk()
        self.root.title("Status UI")

        # Set up the layout
        self.setup_ui()

        # Periodically update statuses
        self.update_statuses()

        # Start the Tkinter main loop
        self.root.mainloop()

    def setup_ui(self):
        # Divide the window into two halves
        self.root.geometry("800x600")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Frame for thread boxes
        thread_frame = tk.Frame(self.root, bg="white", bd=2, relief=tk.SUNKEN)
        thread_frame.grid(row=0, column=0, sticky="nsew")

        # Scrollable area for thread boxes
        canvas = tk.Canvas(thread_frame, bg="white")
        scrollbar = ttk.Scrollbar(thread_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create thread boxes without the Show Browser button
        for i in range(self.max_threads):
            box = self.create_thread_box(scrollable_frame, f"Account Status", i)
            box.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            self.thread_boxes.append(box)

        # Frame for logs
        log_frame = tk.Frame(self.root, bg="black", bd=2, relief=tk.SUNKEN)
        log_frame.grid(row=1, column=0, sticky="nsew")

        # Terminal-like area for logs
        self.log_text = tk.Text(
            log_frame,
            bg="black",
            fg="white",
            insertbackground="white",
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        self.log_text.pack(fill="both", expand=True)

    def create_thread_box(self, parent, label, thread_index):
        """
        Create a single thread status box without the Show Browser button.
        """
        frame = tk.Frame(parent, bg="lightgray", bd=2, relief=tk.RAISED)
        frame.grid_columnconfigure(1, weight=1)

        # Status label
        status_label = tk.Label(frame, text=label, bg="lightgray", font=("Arial", 12))
        status_label.grid(row=0, column=0, padx=5, pady=5)

        # Status indicator
        indicator = tk.Label(frame, text="Idle", bg="lightgray", font=("Arial", 10), anchor="w")
        indicator.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Store references
        frame.status_label = status_label
        frame.indicator = indicator

        return frame

    def update_statuses(self):
        """
        Update thread statuses from the queue.
        """
        try:
            while True:
                status = self.status_queue.get_nowait()
                self.log_text.insert(tk.END, f"{status['account']}: {status['status']}\n")
                self.log_text.see(tk.END)  # Scroll to the bottom

                # Update corresponding thread box
                thread_index = status.get("thread_index", 0)
                if thread_index < len(self.thread_boxes):
                    box = self.thread_boxes[thread_index]
                    box.indicator.config(text=status["status"])
        except Empty:
            pass

        if self.running:
            self.root.after(100, self.update_statuses)  # Check again after 100ms

    def stop(self):
        """
        Stop the status UI.
        """
        self.running = False
        self.root.destroy()

    def set_browser_for_thread(self, thread_index, browser):
        """
        Set the browser for a specific thread.
        """
        if len(self.browsers) <= thread_index:
            # Extend the list if necessary
            self.browsers.extend([None] * (thread_index + 1 - len(self.browsers)))
        self.browsers[thread_index] = browser


import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

class BotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Facebook Group Posting Bot")

        # Variables to store user inputs
        self.threads = tk.IntVar(value=1)
        self.group_uuids_file = tk.StringVar()
        self.accounts_file = tk.StringVar()
        self.links_file = tk.StringVar()
        self.password = tk.StringVar()
        self.extension_file_1 = tk.StringVar()
        self.extension_file_2 = tk.StringVar()

        # File to save/load user inputs
        self.saved_inputs_file = "saved_inputs.json"

        # Load previously saved inputs, if any
        self.load_saved_inputs()

        # Create input fields
        self.create_form()

    def create_form(self):
        # Number of threads
        tk.Label(self.root, text="Number of Threads:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.threads, width=10).grid(row=0, column=1, padx=5, pady=5)

        # Group UUIDs file
        self.create_file_selector("Group UUIDs File:", self.group_uuids_file, 1)

        # Account usernames file
        self.create_file_selector("Account Usernames File:", self.accounts_file, 2)

        # Links file
        self.create_file_selector("Links File:", self.links_file, 3)

        # Password
        tk.Label(self.root, text="Password:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.password, show="*", width=30).grid(row=4, column=1, padx=5, pady=5)

        # Extension 1 file
        self.create_file_selector("First Extension File:", self.extension_file_1, 5)

        # Extension 2 file
        self.create_file_selector("Second Extension File:", self.extension_file_2, 6)

        # Proceed button
        tk.Button(self.root, text="Proceed", command=self.validate_and_proceed).grid(row=7, column=0, columnspan=2, pady=15)

    def create_file_selector(self, label_text, variable, row):
        """Creates a label, entry, and browse button for file selection."""
        tk.Label(self.root, text=label_text).grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.root, textvariable=variable, width=30).grid(row=row, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=lambda: self.browse_file(variable)).grid(row=row, column=2, padx=5, pady=5)

    def browse_file(self, variable):
        """Open a file dialog to select a file."""
        file_path = filedialog.askopenfilename()
        if file_path:
            variable.set(file_path)

    def load_saved_inputs(self):
        """Load saved inputs from a JSON file."""
        if os.path.exists(self.saved_inputs_file):
            with open(self.saved_inputs_file, "r") as file:
                saved_data = json.load(file)
                # Populate the fields with the saved data
                self.threads.set(saved_data.get("threads", 1))
                self.group_uuids_file.set(saved_data.get("group_uuids_file", ""))
                self.accounts_file.set(saved_data.get("accounts_file", ""))
                self.links_file.set(saved_data.get("links_file", ""))
                self.password.set(saved_data.get("password", ""))
                self.extension_file_1.set(saved_data.get("extension_file_1", ""))
                self.extension_file_2.set(saved_data.get("extension_file_2", ""))

    def save_inputs(self):
        """Save the current inputs to a JSON file."""
        inputs = {
            "threads": self.threads.get(),
            "group_uuids_file": self.group_uuids_file.get(),
            "accounts_file": self.accounts_file.get(),
            "links_file": self.links_file.get(),
            "password": self.password.get(),
            "extension_file_1": self.extension_file_1.get(),
            "extension_file_2": self.extension_file_2.get()
        }
        with open(self.saved_inputs_file, "w") as file:
            json.dump(inputs, file, indent=4)

    def get_inputs(self):
        """Retrieve the validated inputs as a dictionary."""
        return {
            "threads": self.threads.get(),
            "group_uuids_file": self.group_uuids_file.get(),
            "accounts_file": self.accounts_file.get(),
            "links_file": self.links_file.get(),
            "password": self.password.get(),
            "extension_file_1": self.extension_file_1.get(),
            "extension_file_2": self.extension_file_2.get()
        }

    def validate_and_proceed(self):
        """Validate user inputs and proceed to the next step."""
        if not all([self.group_uuids_file.get(), self.accounts_file.get(), self.links_file.get(), self.password.get(), self.extension_file_1.get(), self.extension_file_2.get()]): 
            messagebox.showerror("Input Error", "All fields are required!")
            return

        # Validate if the files exist
        if not os.path.exists(self.group_uuids_file.get()):
            messagebox.showerror("File Error", "Group UUIDs file does not exist!")
            return
        if not os.path.exists(self.accounts_file.get()):
            messagebox.showerror("File Error", "Accounts file does not exist!")
            return
        if not os.path.exists(self.links_file.get()):
            messagebox.showerror("File Error", "Links file does not exist!")
            return
        if not os.path.exists(self.extension_file_1.get()):
            messagebox.showerror("File Error", "First Extension file does not exist!")
            return
        if not os.path.exists(self.extension_file_2.get()):
            messagebox.showerror("File Error", "Second Extension file does not exist!")
            return

        # Save the inputs before proceeding
        self.save_inputs()

        # If validation passes, proceed to the next step
        self.root.destroy()  # Close the current window
        print("Proceeding with inputs:")
        print(f"Threads: {self.threads.get()}")
        print(f"Group UUIDs File: {self.group_uuids_file.get()}")
        print(f"Account Usernames File: {self.accounts_file.get()}")
        print(f"Links File: {self.links_file.get()}")
        print(f"Password: {self.password.get()}")
        print(f"First Extension File: {self.extension_file_1.get()}")
        print(f"Second Extension File: {self.extension_file_2.get()}")


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




# Check if 'logs' directory and 'app.log' file exist, if not create them
log_dir = 'logs'
log_file = os.path.join(log_dir, 'app.log')

os.makedirs(log_dir, exist_ok=True)  # Create the 'logs' directory if it doesn't exist
if not os.path.isfile(log_file):    # Create the 'app.log' file if it doesn't exist
    open(log_file, 'w').close()

# Setup logging
logging.basicConfig(
    filename=log_file,
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
        global current_browser 
        current_browser = [browser]
        # print(current_browser)

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
