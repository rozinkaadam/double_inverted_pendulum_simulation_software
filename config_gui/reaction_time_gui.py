import tkinter as tk
import random
import time
from datetime import datetime
import csv
import os
import subprocess

class ReactionTest:
    """
    A GUI application for conducting reaction time tests.

    Attributes:
        tl (tk.Toplevel): The main window for the reaction test.
        num_trials (int): Number of trials in the test.
        min_time (int): Minimum delay (in milliseconds) before the button appears.
        max_time (int): Maximum delay (in milliseconds) before the button appears.
        current_trial (int): The current trial number.
        reaction_times (list): List of recorded reaction times.
        is_ready (bool): Whether the test is ready to measure reaction time.
        started_test (bool): Whether the test has started.
    """

    def __init__(self, parent_root, num_trials=10, min_time=1000, max_time=3000):
        """
        Initializes the ReactionTest class.

        Args:
            parent_root (tk.Tk): The parent window.
            num_trials (int): Number of trials in the test.
            min_time (int): Minimum delay (in milliseconds) before the button appears.
            max_time (int): Maximum delay (in milliseconds) before the button appears.
        """
        self.tl = tk.Toplevel(parent_root)
        self.tl.title("Reaction Test")

        self.tl.geometry("800x600")  # Sets the initial window size
        self.num_trials = num_trials
        self.min_time = min_time
        self.max_time = max_time
        self.current_trial = 0
        self.reaction_times = []
        self.is_ready = False

        self.main_label = tk.Label(self.tl, text="Reaction Test", font=("Helvetica", 32))
        self.main_label.pack(pady=20)

        self.label = tk.Label(self.tl)
        self.label.pack(pady=20)

        self.button = tk.Button(self.tl, command=self.button_clicked, width=20, height=10)
        self.button.pack(pady=20)

        self.message_label = tk.Label(self.tl)
        self.message_label.pack(pady=1)

        self.hyperlink_label = tk.Label(self.tl, fg="blue", cursor="hand2")
        self.hyperlink_label.pack(pady=1)
        self.hyperlink_label.bind("<Button-1>", self.open_directory)

        self.reset_test()

    def start_new_test(self):
        """
        Starts a new reaction test session.
        """
        self.started_test = True
        self.label.config(text=f'Trial: {self.current_trial + 1} / {self.num_trials}')
        self.button.config(text="", bg="SystemButtonFace")

    def reset_test(self):
        """
        Resets the test to its initial state.
        """
        self.current_trial = 0
        self.reaction_times = []
        self.started_test = False
        self.label.config(text='')
        self.button.config(text="Click to start!", bg="SystemButtonFace")

    def start_next_trial(self):
        """
        Prepares the next trial in the reaction test.
        """
        if self.current_trial < self.num_trials:
            self.is_ready = False
            self.button.config(bg="SystemButtonFace")
            self.message_label.config(text="")
            delay = random.randint(self.min_time, self.max_time)
            self.tl.after(delay, self.show_button)
        else:
            self.show_results()

    def show_button(self):
        """
        Displays the button and starts timing the reaction.
        """
        if self.started_test:
            self.is_ready = True
            self.start_time = time.time()
            self.button.config(bg="red")

    def button_clicked(self):
        """
        Handles button click events during the test.
        """
        if not self.started_test:
            self.start_new_test()
            self.start_next_trial()
        else:
            if not self.is_ready:
                self.reset_test()
                self.message_label.config(text="You clicked too early!")
                return

            reaction_time = time.time() - self.start_time
            self.reaction_times.append(reaction_time)
            self.current_trial += 1
            self.label.config(text=f'Trial: {self.current_trial + 1} / {self.num_trials}')
            self.start_next_trial()

    def show_results(self):
        """
        Displays the average reaction time and saves the results.
        """
        self.average_reaction_time = sum(self.reaction_times) / len(self.reaction_times)
        self.message_label.config(text=f"Average reaction time: {self.average_reaction_time:.4f} seconds.")
        self.save_results()
        self.reset_test()

    def save_results(self):
        """
        Saves the reaction times to a CSV file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.saved_file_name = f'reaction_times_{timestamp}.csv'
        self.file_path = os.path.join(os.getcwd(), self.saved_file_name)
        with open(self.file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Average reaction time [s]", self.average_reaction_time])
            writer.writerow(["Trial", "Reaction Time [s]"])
            for i, reaction_time in enumerate(self.reaction_times, 1):
                writer.writerow([i, reaction_time])
                print(f"i, reaction_time: {i}, {reaction_time}")
        self.message_label.config(text=f'Average reaction time: {self.average_reaction_time:.4f} seconds.\nReaction times saved to the following directory, named "{self.saved_file_name}"')
        self.show_open_dir_hyperlink()

    def show_open_dir_hyperlink(self):
        """
        Displays a clickable hyperlink to open the directory of the saved file.
        """
        if self.file_path:
            directory = os.path.dirname(self.file_path)
            self.hyperlink_label.config(text=f"{directory}")

    def open_directory(self, event):
        """
        Opens the directory containing the saved results file.

        Args:
            event (tk.Event): The click event triggered on the hyperlink.
        """
        if self.file_path:
            subprocess.run(f'explorer /select,"{self.file_path}"')
