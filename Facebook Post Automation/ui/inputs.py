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
