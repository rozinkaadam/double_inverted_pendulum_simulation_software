import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    """
    A custom scrollable frame widget for displaying content with vertical and horizontal scrollbars.

    This widget is useful for creating a scrollable area inside a Tkinter GUI.

    Attributes:
        scrollable_frame (ttk.Frame): The inner frame where widgets can be added.
    """
    def __init__(self, container, *args, **kwargs):
        """
        Initializes the ScrollableFrame widget.

        Args:
            container (tk.Widget): The parent widget to attach the scrollable frame.
            *args: Variable-length argument list for the ttk.Frame.
            **kwargs: Keyword arguments for the ttk.Frame.
        """
        super().__init__(container, *args, **kwargs)

        # Create the canvas and scrollbars
        canvas = tk.Canvas(self)
        scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)

        # Create the inner frame to hold the scrollable content
        self.scrollable_frame = ttk.Frame(canvas)

        # Bind the scrollable frame to the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        # Add the inner frame to the canvas
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure the canvas to work with the scrollbars
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Layout the widgets
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Configure the grid layout to make the canvas resizable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
