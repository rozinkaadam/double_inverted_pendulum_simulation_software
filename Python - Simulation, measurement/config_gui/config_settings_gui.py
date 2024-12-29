import yaml
import tkinter as tk
from tkinter import ttk
from copy import copy
from init_simulation import simulationManager
import re
import config_gui.reaction_time_gui as reaction_time_gui
from screeninfo import get_monitors

# Constant for background color
BRIGHT_BG = "#eaeaea"

class ConfigGUI:
    """
    GUI for configuring simulation settings for a double inverted pendulum on a cart.

    Attributes:
        program_config_dict (dict): Configuration dictionary provided by the program.
        def_config_dict (dict): Default configuration dictionary.
        config_dict (dict): Working copy of the configuration dictionary.
        root (tk.Tk): The root window for the GUI.
        main_frame (ttk.Frame): The main frame containing all GUI elements.
        entries (dict): Dictionary to hold references to input fields.
        rod_b_fields (list): List of rod-related fields.
        rod_length_mod (list): List of rod length modifiers.
    """

    def __init__(self, program_config_dict, def_config_dict) -> None:
        """
        Initializes the ConfigGUI class.

        Args:
            program_config_dict (dict): Configuration dictionary provided by the program.
            def_config_dict (dict): Default configuration dictionary.
        """
        self.program_config_dict = program_config_dict
        self.def_config_dict = def_config_dict
        self.config_dict = copy(self.def_config_dict)

        monitors = get_monitors()

        self.root = tk.Tk()
        self.root.title("Set config settings")
        self.root.state('zoomed')

        open_on_monitor_id = self.config_dict["simulation_config"]["_open_on_monitor_id"]

        if len(monitors) <= open_on_monitor_id:
            # Default window size if the target monitor is unavailable
            self.root.geometry("1920x1080")
        else:
            target_monitor = monitors[open_on_monitor_id]
            # Place the window on the specified monitor
            self.root.geometry(f"400x300+{target_monitor.x}+{target_monitor.y}")

        self._create_settings_gui()
        self.root.mainloop()

    def _create_settings_gui(self):
        """
        Creates and arranges all the widgets for the settings GUI.
        """
        # Main frame setup
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)
        sizegrip = ttk.Sizegrip(self.root)
        sizegrip.pack(side=tk.BOTTOM, anchor=tk.SE)
        self.main_frame.columnconfigure(4, weight=1)
        self.main_frame.rowconfigure(3, weight=1)

        # Section labels
        self.parameters_label = tk.Label(self.main_frame, text="Parameters:", font=('Helvetica', 18, 'bold'))
        self.parameters_label.grid(row=0, column=0, sticky="w")
        self.diag_label = tk.Label(self.main_frame, text="Diagnostic data:", font=('Helvetica', 18, 'bold'))
        self.diag_label.grid(row=0, column=4, sticky="w")

        # Simulation title input
        self.sim_title_frame = tk.Frame(self.main_frame)
        self.sim_title_frame.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=(2, 50))
        self.sim_title_frame.columnconfigure(1, weight=1)

        self.sim_title_label = tk.Label(self.sim_title_frame, text="Simulation Title:")
        self.sim_title_label.grid(row=1, column=0, sticky="nsew", padx=(0, 20))

        self.sim_title_entry_string_var = tk.StringVar()

        self.sim_title_entry = tk.Entry(self.sim_title_frame, textvariable=self.sim_title_entry_string_var)
        self.sim_title_entry.grid(row=1, column=1, sticky="nsew")

        # Pre-fill the simulation title if available in the configuration
        if "simulation_config" in self.config_dict and "_simulation_title" in self.config_dict["simulation_config"]:
            self.sim_title_entry_string_var.set(self.config_dict["simulation_config"]["_simulation_title"])

        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(5, 0))

        # Scrollable content area
        self.frame = tk.Frame(self.main_frame)
        self.frame.grid(row=3, column=0, columnspan=3, sticky="nsew")

        # Canvas and scrollbar for scrolling content
        self.canvas = tk.Canvas(self.frame, bg=BRIGHT_BG)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame inside the canvas to hold scrollable widgets
        self.scrollable_frame = tk.Frame(self.canvas, bg=BRIGHT_BG)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Mouse wheel scrolling
        def on_mouse_wheel(event):
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

        def bind_mouse_wheel(event):
            self.canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        def unbind_mouse_wheel(event):
            self.canvas.unbind_all("<MouseWheel>")

        def update_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Bind mouse wheel events
        self.canvas.bind("<Enter>", bind_mouse_wheel)
        self.canvas.bind("<Leave>", unbind_mouse_wheel)

        # Update scroll region dynamically
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: (
                update_scroll_region(e),
                self.canvas.configure(
                    scrollregion=self.canvas.bbox("all"),
                    width=self.scrollable_frame.winfo_reqwidth()
                )
            )
        )

        self.entries = {}
        self.rod_b_fields = []
        self.rod_length_mod = []
        self.create_fields_from_dict(self.config_dict)

        self._on_rod_const_length_checkbutton_toggle()
        self._on_double_pendulum_checkbutton_toggle()

        # Diagnostic frame
        self.diag_frame = tk.Frame(self.main_frame)
        self.diag_frame.grid(row=2, rowspan=3, column=4, pady=10, sticky="nsew")

        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(0, 5))

        # Button frame
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky="nsew")
        self.button_frame.columnconfigure(1, weight=1)

        # Buttons
        self.reaction_test_button = tk.Button(
            self.button_frame,
            text="Reaction Test",
            command=self._start_reaction_test_button_event,
            bg="#66C3EB",
            fg="black",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=2,
            activebackground="#5AA7D6",
            activeforeground="white"
        )
        self.reaction_test_button.grid(row=0, column=0, padx=10, sticky="nsew")

        self.start_simulation_button = tk.Button(
            self.button_frame,
            text="Start Simulation",
            command=self._start_simulation_button_event,
            bg="#46D074",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=2,
            activebackground="#3BB360",
            activeforeground="white"
        )
        self.start_simulation_button.grid(row=0, column=1, padx=10, sticky="nsew")

        self.playback_button = tk.Button(
            self.button_frame,
            text="Playback",
            command=self._start_simulation_button_event,
            bg="#FCD060",
            fg="black",
            font=("Arial", 10, "bold"),
            relief="raised",
            bd=2,
            activebackground="#E5B852",
            activeforeground="black"
        )
        self.playback_button.grid(row=0, column=2, padx=10, sticky="nsew")

        # Footer label
        self.my_name_label = tk.Label(self.main_frame, text="Ádám Rozinka - 2024", fg="#aaaaaa")
        self.my_name_label.grid(row=5, column=4, sticky="es")

        # Update scrollable frame dimensions
        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"), width=self.scrollable_frame.winfo_reqwidth())
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        

    def create_fields_from_dict(self, config_dict, row=0, parent_key=""):
        """
        Recursively creates input fields in the GUI based on the given configuration dictionary.

        Args:
            config_dict (dict): Dictionary containing configuration data.
            row (int): Current row index for placing widgets.
            parent_key (str): The parent key for nested dictionaries.

        Returns:
            int: The next available row index after adding fields.
        """
        for key, value in config_dict.items():
            if key[0] != "_":
                full_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, dict):
                    label = ' '.join(word.capitalize() for word in key.split('_'))
                    tk.Label(self.scrollable_frame, text=label, font=('Helvetica', 10, 'bold'), bg=BRIGHT_BG).grid(row=row, column=0, columnspan=2, sticky=tk.W)
                    row += 1
                    row = self.create_fields_from_dict(value, row, full_key)

                elif isinstance(value, bool):
                    label = ' '.join(key.split('_'))
                    tk.Label(self.scrollable_frame, text=f"{label}:", bg=BRIGHT_BG).grid(row=row, column=0, sticky=tk.W)
                    var = tk.BooleanVar(value=value)
                    checkbox = tk.Checkbutton(self.scrollable_frame, bg=BRIGHT_BG, variable=var)
                    checkbox.grid(row=row, column=1)
                    self.entries[full_key] = var

                    if "rod b" in label:
                        self.rod_b_fields.append(checkbox)
                    elif "double pendulum" in label:
                        self._dp_key = full_key
                        checkbox.config(command=lambda: self._on_double_pendulum_checkbutton_toggle())
                    elif "constant rod length" in label:
                        self._cr_key = full_key
                        checkbox.config(command=lambda: self._on_rod_const_length_checkbutton_toggle())
                    row += 1

                else:
                    unit = key.split('_')[-1]
                    key_l = key.split('_')[:-1]
                    label = ' '.join(key_l)
                    tk.Label(self.scrollable_frame, text=f"{label}:", bg=BRIGHT_BG).grid(row=row, column=0, sticky=tk.W)
                    entry = tk.Entry(self.scrollable_frame)
                    entry.grid(row=row, column=1)
                    tk.Label(self.scrollable_frame, text=f"[{unit}]", bg=BRIGHT_BG).grid(row=row, column=2, sticky=tk.W)
                    entry.insert(0, value)
                    self.entries[full_key] = entry
                    row += 1

                    if "rod b" in label:
                        self.rod_b_fields.append(entry)
                    if "rod" in label and ("dl" in label or "dt" in label):
                        self.rod_length_mod.append(entry)

        return row

    def _on_double_pendulum_checkbutton_toggle(self):
        """
        Toggles the state of rod-related fields based on the double pendulum checkbox.
        """
        if self.entries[self._dp_key].get():
            print("Checkbutton is checked")
            for w in self.rod_b_fields:
                if w in self.rod_length_mod:
                    if self.entries[self._cr_key].get():
                        pass
                    else:
                        w.config(state=tk.NORMAL)
                else:
                    w.config(state=tk.NORMAL)
        else:
            print("Checkbutton is unchecked")
            for w in self.rod_b_fields:
                w.config(state=tk.DISABLED)

    def _on_rod_const_length_checkbutton_toggle(self):
        """
        Toggles the state of rod length modifier fields based on the constant rod length checkbox.
        """
        if self.entries[self._cr_key].get():
            print("Checkbutton is checked")
            for w in self.rod_length_mod:
                w.config(state=tk.DISABLED)
        else:
            print("Checkbutton is unchecked")
            for w in self.rod_length_mod:
                if w in self.rod_b_fields:
                    if self.entries[self._dp_key].get():
                        w.config(state=tk.NORMAL)
                    else:
                        pass
                else:
                    w.config(state=tk.NORMAL)

    def _start_simulation_button_event(self):
        """
        Handles the start simulation button event by updating configuration values and starting the simulation.
        """
        self.update_config_dict_gui_values()
        self.start_simulation()

        # Bind the on_closing function to the window close event
        def on_closing():
            self.simManager.SIM_STATE.set_run_status(0)
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

    def _start_reaction_test_button_event(self):
        """
        Handles the reaction test button event by opening the reaction test GUI.
        """
        self.reaction_time_TL = reaction_time_gui.ReactionTest(self.root)

    def update_config_dict_gui_values(self):
        """
        Updates the configuration dictionary with the values from the GUI.
        """
        self.marked_config_dict, self.config_dict = self.combine_configs(copy(self.def_config_dict), self.read_gui_values())
        print(f"config_dict: {self.config_dict}")
        ConfigGUI.write_config_file(self.program_config_dict["default_parameters_file_path"], self.marked_config_dict)

    def combine_configs(self, def_config, readed_config):
        """
        Combines the default and read configuration dictionaries.

        Args:
            def_config (dict): Default configuration dictionary.
            readed_config (dict): Read configuration dictionary.

        Returns:
            tuple: Updated default configuration and striped dictionary.
        """
        for key, value in readed_config.items():
            if isinstance(value, dict):
                self.combine_configs(def_config[key], value)
            else:
                def_config[key] = value

        striped_dict = self.strip_dict_keys(def_config)

        return def_config, striped_dict

    def strip_dict_keys(self, source_dict):
        """
        Strips underscores from keys in the configuration dictionary.

        Args:
            source_dict (dict): Dictionary to process.

        Returns:
            dict: Processed dictionary with underscores removed from keys.
        """
        striped_dictionary = {}
        for key, value in source_dict.items():
            if isinstance(value, dict):
                striped_dictionary[key.strip('_')] = self.strip_dict_keys(value)
            else:
                value = ConfigGUI.string_to_list(value)
                striped_dictionary[key.strip('_')] = value
        return striped_dictionary

    def read_gui_values(self):
        """
        Reads and parses the values entered in the GUI.

        Returns:
            dict: Parsed configuration dictionary.
        """
        config = {}
        for full_key, entry in self.entries.items():
            keys = full_key.split('.')

            d = config
            for key in keys[:-1]:
                d = d.setdefault(key, {})
            d[keys[-1]] = self.parse_value(entry.get(), self.get_default_value(keys))

        config["simulation_config"]["_simulation_title"] = f"{self.sim_title_entry_string_var.get()}"
        if config["geometry_config"]["rod_b_length_m"] < 0.0001:
            config["geometry_config"]["double_pendulum"] = False

        return config

    def get_default_value(self, keys):
        """
        Retrieves the default value for a given key path.

        Args:
            keys (list): List of keys representing the path in the dictionary.

        Returns:
            Any: Default value for the given key path.
        """
        d = self.def_config_dict
        for key in keys:
            d = d[key]
        return d

    def parse_value(self, value, example):
        """
        Parses a value entered in the GUI to match the expected data type.

        Args:
            value (str): The value entered in the GUI.
            example (Any): Example value to determine the expected type.

        Returns:
            Any: Parsed value.
        """
        if isinstance(example, bool):
            return value.lower() in ('true', '1', 'yes') if isinstance(value, str) else value
        if isinstance(example, (int, float)):
            if isinstance(value, str):
                return float(value) if '.' in value else int(value)
            return type(example)(value)
        elif isinstance(example, list):
            return [float(v) for v in value.strip('[]').split(',')]
        return value

    def start_simulation(self):
        """
        Starts the simulation by initializing the simulation manager and threads.
        """
        self.simManager = simulationManager(self.config_dict, self.diag_frame)
        self.simManager.start_threads()

    def simulation_end(self):
        """
        Handles the end of the simulation.
        """
        print(f"Simulation panel closed!")
        self.enable_widgets_on_frames()

    def disable_all_widgets_on_frames(self, frames):
        """
        Disables all widgets in the specified frames.

        Args:
            frames (list): List of frames to disable widgets in.
        """
        self.initial_widget_states = {}  # Clear previous states

        for frame in frames:
            for widget in frame.winfo_children():
                if widget.winfo_class() == 'Entry' and widget['state'] == 'normal':
                    self.initial_widget_states[widget] = 'normal'
                    widget.config(state='disabled')
                elif widget.winfo_class() == 'Text' and widget['state'] == 'normal':
                    self.initial_widget_states[widget] = 'normal'
                    widget.config(state='disabled')
                elif widget.winfo_class() == 'Button' and widget['state'] == 'normal':
                    self.initial_widget_states[widget] = 'normal'
                    widget.config(state='disabled')
                elif widget.winfo_class() == 'Checkbutton' and widget['state'] == 'normal':
                    self.initial_widget_states[widget] = 'normal'
                    widget.config(state='disabled')

    def enable_widgets_on_frames(self):
        """
        Restores the initial states of the widgets in the frames.
        """
        for widget, state in self.initial_widget_states.items():
            widget.config(state=state)
        self.initial_widget_states = {}  # Clear the stored states after enabling


    @staticmethod
    def read_config_file(file_path):
        """
        Reads a configuration file in YAML format.

        Args:
            file_path (str): Path to the configuration file.

        Returns:
            dict: Configuration data if successfully read, None otherwise.
        """
        try:
            with open(file_path, 'r') as file:
                config_dict = yaml.safe_load(file)
            print(f"Successfully read: {file_path}")
            return config_dict
        except FileNotFoundError:
            print(f"Error: Path not found: {file_path}")
        except PermissionError:
            print(f"Error: No permission to read the file: {file_path}")
        except yaml.YAMLError as e:
            print(f"Error processing YAML file: {e}")
        except Exception as e:
            print(f"Unknown error occurred: {e}")

        return None

    @staticmethod
    def write_config_file(file_path, config_dict):
        """
        Writes a configuration dictionary to a YAML file.

        Args:
            file_path (str): Path to the configuration file.
            config_dict (dict): Configuration data to write.

        Returns:
            bool: True if successfully written, False otherwise.
        """
        try:
            with open(file_path, 'w') as file:
                yaml.safe_dump(config_dict, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
            print(f"Successfully saved: {file_path}")
            return True
        except FileNotFoundError:
            print(f"Error: Path not found: {file_path}")
        except PermissionError:
            print(f"Error: No permission to write to the file: {file_path}")
        except Exception as e:
            print(f"Unknown error occurred: {e}")

        return False

    @staticmethod
    def string_to_complex(value):
        """
        Converts a string to a complex number if valid.

        Args:
            value (str): String representation of the value.

        Returns:
            complex or str: Converted complex number or original string if invalid.
        """
        if not isinstance(value, str):
            return value

        complex_pattern = re.compile(r'^[+-]?(\d+(\.\d*)?|\.\d+)([+-](\d+(\.\d*)?|\.\d+))?[ij]?$')
        value = value.replace('i', 'j')
        if complex_pattern.match(value.replace(' ', '')):
            try:
                return complex(value.replace(' ', ''))
            except ValueError:
                return value
        return value

    @staticmethod
    def string_to_list(value):
        """
        Converts a string to a list of floats if valid.

        Args:
            value (str): String representation of the value.

        Returns:
            list or str: Converted list of floats or original string if invalid.
        """
        if not isinstance(value, str):
            return value

        if ',' in value:
            try:
                return [float(x.strip()) for x in value.split(',')]
            except ValueError:
                return value
        return value