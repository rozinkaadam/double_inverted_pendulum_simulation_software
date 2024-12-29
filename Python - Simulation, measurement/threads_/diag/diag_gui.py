import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from libs.varstructs.SIM_STATE import SIM_STATE

class diag_gui_widget():
    def __init__(self, root, SIM_STATE_VAR: SIM_STATE) -> None:
        # Clear frame root
        for widget in root.winfo_children():
            widget.destroy()

        # Create a main frame to hold both scrollable panels
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        # Scrollable frame for the left panel (state variables)
        left_canvas = tk.Canvas(main_frame)
        left_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=left_canvas.yview)
        self.left_scrollable_frame = ttk.Frame(left_canvas)

        # Set scroll region to the size of the content in self.left_scrollable_frame
        def update_left_scroll_region(event=None):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))

        self.left_scrollable_frame.bind("<Configure>", update_left_scroll_region)

        # Dynamically adjust the canvas width based on the scrollable frame content width
        def adjust_left_canvas_width(event):
            left_canvas.config(width=self.left_scrollable_frame.winfo_reqwidth())

        self.left_scrollable_frame.bind("<Configure>", adjust_left_canvas_width)

        left_canvas.create_window((0, 0), window=self.left_scrollable_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        # Pack left panel components
        left_canvas.pack(side="left", fill="y")  # Only fill vertically
        left_scrollbar.pack(side="left", fill="y")

        # Scrollable frame for the right panel (plots)
        right_canvas = tk.Canvas(main_frame)
        right_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=right_canvas.yview)
        right_scrollable_frame = ttk.Frame(right_canvas)

        # Set scroll region for the right panel
        def update_right_scroll_region(event=None):
            right_canvas.configure(scrollregion=right_canvas.bbox("all"))

        right_scrollable_frame.bind("<Configure>", update_right_scroll_region)

        right_canvas.create_window((0, 0), window=right_scrollable_frame, anchor="nw")
        right_canvas.configure(yscrollcommand=right_scrollbar.set)

        # Pack right panel components
        right_canvas.pack(side="left", fill="both", expand=True)
        right_scrollbar.pack(side="right", fill="y")

        # Scroll with mouse wheel when the cursor is over the left or right canvas
        def on_mouse_wheel_left(event):
            left_canvas.yview_scroll(-1 * int(event.delta / 120), "units")

        def on_mouse_wheel_right(event):
            right_canvas.yview_scroll(-1 * int(event.delta / 120), "units")

        left_canvas.bind("<Enter>", lambda e: left_canvas.bind_all("<MouseWheel>", on_mouse_wheel_left))
        left_canvas.bind("<Leave>", lambda e: left_canvas.unbind_all("<MouseWheel>"))

        right_canvas.bind("<Enter>", lambda e: right_canvas.bind_all("<MouseWheel>", on_mouse_wheel_right))
        right_canvas.bind("<Leave>", lambda e: right_canvas.unbind_all("<MouseWheel>"))

        self.updateable_labels = {}

        # Display state variables in the left scrollable frame
        for main_key, sub_dict in SIM_STATE_VAR.get_all_items():
            if main_key == "plotable_datasets":
                continue
            group_frame = tk.LabelFrame(self.left_scrollable_frame, text=main_key, padx=10, pady=5)
            group_frame.pack(fill="both", expand=True, padx=10, pady=5)

            self.updateable_labels[main_key] = {}

            for key, value in sub_dict.items():
                if not isinstance(value, str) and isinstance(value, list) and len(value) > 0:
                    label = tk.Label(group_frame, text=f"{key}: {value[-1]}", width=40, anchor="w", justify="left")
                elif isinstance(value, dict) and len(value) > 0:
                    continue
                else:
                    label = tk.Label(group_frame, text=f"{key}: {value}", width=40, anchor="w", justify="left")
                label.pack(anchor="w")
                self.updateable_labels[main_key][key] = label

        # Setup for dynamic plots in the right scrollable frame
        plot_vars = []
        control_frames = []
        lines = []
        canvases = []

        def update_selected_lists():
            selected_data = []
            for var in plot_vars:
                key = var["plot_var"].get()
                if key in SIM_STATE_VAR.SIM_STATE_VAR["plotable_datasets"]:
                    selected_data.append(SIM_STATE_VAR.SIM_STATE_VAR["plotable_datasets"][key])
            return selected_data

        def add_plot():
            # Create a frame to hold the dropdown, slider, and entry horizontally
            control_frame = tk.Frame(right_scrollable_frame)
            control_frame.pack(anchor="w", padx=5, pady=(20, 0))

            # Add a dropdown for selecting data to plot
            plot_var = tk.StringVar(value=list_options[0])  # Default selection
            dropdown = ttk.Combobox(control_frame, textvariable=plot_var, values=list_options)
            dropdown.pack(side="left", padx=5)
            dropdown.bind("<MouseWheel>", lambda e: "break")
            dropdown.state(["readonly"])

            # Horizontal slider for setting the x-axis range
            x_range_slider = tk.Scale(control_frame, from_=100, to=5000, resolution=10, orient="horizontal", length=150, showvalue=False)
            x_range_slider.pack(side="left", padx=(20, 1))

            # Entry for displaying and modifying the slider value
            x_range_entry = tk.Entry(control_frame, width=10)
            x_range_entry.pack(side="left", padx=(1, 0))
            x_range_entry.insert(0, x_range_slider.get())

            # Link slider and entry value
            def update_entry_from_slider(event):
                # Update entry when slider is changed
                x_range_value = x_range_slider.get()
                if x_range_value >= 5000:
                    x_range_entry.delete(0, tk.END)
                    x_range_entry.insert(0, "∞")
                else:
                    x_range_entry.delete(0, tk.END)
                    x_range_entry.insert(0, str(x_range_value))

            def update_slider_from_entry(event):
                # Update slider when entry is changed
                try:
                    entry_value = x_range_entry.get()
                    if entry_value == "∞":
                        x_range_slider.set(5000)  # Set slider to max if "∞" is entered
                    else:
                        x_range_slider.set(int(entry_value))
                except ValueError:
                    pass  # Ignore if the entry does not contain a valid integer

            x_range_slider.bind("<Motion>", update_entry_from_slider)
            x_range_entry.bind("<Return>", update_slider_from_entry)  # Update slider when Enter is pressed

            # Create a new figure and axis for the new plot
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.set_title(f"Live Plot {len(canvases) + 1}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Values")
            ax.grid(True)

            # Set the background color of the plot
            ax.set_facecolor("lightgrey")
            fig.patch.set_facecolor("#f0f0f0")  # Set the figure background color as well

            # Initialize line
            line, = ax.plot([], [], label=plot_var.get())
            lines.append(line)

            # Embed the plot into the Tkinter scrollable frame
            canvas_plot = FigureCanvasTkAgg(fig, master=right_scrollable_frame)
            canvas_plot.get_tk_widget().pack(fill="both", expand=True, padx=5, anchor="w")
            canvases.append(canvas_plot)

            control_frames.append(control_frame)

            fig.tight_layout()  # Adjust layout to fit new plots

            # Store the slider for each plot to access in update_plot
            plot_vars.append({"plot_var": plot_var, "slider": x_range_slider, "ax": ax})

            # Start animation for live updating
            self.ani = FuncAnimation(fig, update_plot, init_func=init_plot, blit=False, interval=100)

        def remove_plot():
            if plot_vars:
                # Remove last dropdown, plot var, and line
                plot_vars.pop()
                control_frame = control_frames.pop()
                control_frame.pack_forget()

                line = lines.pop()
                canvas_plot = canvases.pop()
                canvas_plot.get_tk_widget().pack_forget()
                canvas_plot.figure.clear()

        # Buttons to add and remove plots, placed side by side in a new frame
        button_frame = tk.Frame(right_scrollable_frame)
        button_frame.pack(pady=5, padx=5, anchor="w")

        button_add = tk.Button(button_frame, text="Add Plot", command=add_plot)
        button_add.pack(side="left", padx=5)

        button_remove = tk.Button(button_frame, text="Remove Plot", command=remove_plot)
        button_remove.pack(side="left", padx=5)

        self.paused = False

        self.button_pause = tk.Button(button_frame, text="Pause Plotting", command=self.toggle_animation)
        self.button_pause.pack(side="left", padx=5)

        # Set up the live plot with selected lists
        list_options = list(SIM_STATE_VAR.SIM_STATE_VAR["plotable_datasets"].keys())

        print(f"list_options: {list_options}")

        # Function to initialize the plot limits
        def init_plot():
            for line in lines:
                line.set_data([], [])
            return lines

        # Function to update the plot
        def update_plot(frame):
            # Skip updating if paused
            if self.paused:
                return lines  # Return the lines without updating them
            # Get the data to plot (e.g., a list of values for y-axis)
            selected_data = update_selected_lists()

            # Check if there is data and the line exists
            if selected_data and lines:
                for i, data in enumerate(selected_data):
                    if i < len(lines):  # Ensure the line exists
                        ax = lines[i].axes
                        x_data = range(len(data))
                        
                        # Check if data has sufficient points
                        if len(data) > 0:
                            # Update the line with new data
                            lines[i].set_data(x_data, data)

                            # Get the slider value for x-axis range
                            slider_value = plot_vars[i]["slider"].get()
                            if slider_value == 1000:  # Treat 1000 as "infinity"
                                ax.set_xlim(0, len(data))
                            else:
                                ax.set_xlim(max(0, len(data) - slider_value), len(data))

                            ax.set_ylim(min(data) - 10, max(data) + 10)  # Adjust y-axis based on data range
                            canvases[i].draw_idle()  # Update the plot display

            return lines


    def toggle_animation(self):
            # Toggle the paused state
            self.paused = not self.paused
            # Update button text based on paused state
            pause_button_text = "Resume Plotting" if self.paused else "Pause Plotting"
            self.button_pause.config(text=pause_button_text)

    def update_state_var_display(self,SIM_STATE_VAR:SIM_STATE):
        # Display state variables in the left scrollable frame
        for main_key, sub_dict in self.updateable_labels.items():
            for key, _ in sub_dict.items():
                value=SIM_STATE_VAR.SIM_STATE_VAR[main_key][key]
                if not isinstance(value, str) and isinstance(value, list) and len(value)>0:
                    print_val=value[-1]
                    if isinstance(print_val, float):
                        self.updateable_labels[main_key][key].configure(text=f"{key}: {print_val:.2f}")
                    elif isinstance(print_val, list):
                        prtin_v_form=""
                        for sub_pv in print_val:
                            if isinstance(sub_pv, float):
                                prtin_v_form+=f"{sub_pv:.2f}, "
                            elif isinstance(sub_pv, tuple):
                                prtin_v_form+=f"\n("
                                for sub_sub_pv in sub_pv:
                                    if isinstance(sub_sub_pv, float):
                                        prtin_v_form+=f"{sub_sub_pv:.2f}, "
                                    else:
                                        prtin_v_form+=f"{sub_sub_pv}, "
                                prtin_v_form+=f")\n"
                            else:
                                prtin_v_form+=f"{sub_pv}, "
                        
                        self.updateable_labels[main_key][key].configure(text=f"{key}: {prtin_v_form}")
                    else:
                        self.updateable_labels[main_key][key].configure(text=f"{key}: {print_val}")
                elif isinstance(value, dict) and len(value)>0:
                    #self.updateable_labels[main_key][key].configure(text=f"{key}: {value[-1]}")
                    print_val=value[-1]
                    if isinstance(print_val, float):
                        self.updateable_labels[main_key][key].configure(text=f"{key}: {print_val:.2f}")
                    elif isinstance(print_val, list):
                        prtin_v_form=""
                        for sub_pv in print_val:
                            if isinstance(sub_pv, float):
                                prtin_v_form+=f"{sub_pv:.2f}, "
                            elif isinstance(sub_pv, tuple):
                                prtin_v_form+=f"\n("
                                for sub_sub_pv in sub_pv:
                                    if isinstance(sub_sub_pv, float):
                                        prtin_v_form+=f"{sub_sub_pv:.2f}, "
                                    else:
                                        prtin_v_form+=f"{sub_sub_pv}, "
                                prtin_v_form+=f")\n"
                            else:
                                prtin_v_form+=f"{sub_pv}, "
                        
                        self.updateable_labels[main_key][key].configure(text=f"{key}: {prtin_v_form}")
                    else:
                        self.updateable_labels[main_key][key].configure(text=f"{key}: {print_val}")
                else:
                    if isinstance(value, float):
                        self.updateable_labels[main_key][key].configure(text=f"{key}: {value:.2f}")
                    else:
                        self.updateable_labels[main_key][key].configure(text=f"{key}: {value}")
                