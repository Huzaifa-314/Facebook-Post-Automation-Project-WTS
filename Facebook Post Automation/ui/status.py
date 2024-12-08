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
