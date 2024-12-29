import threading
import time
import pygame
import ctypes
from ctypes import wintypes
import win32gui
import win32con
from threads_.simgui.overlays import msg_overlay
from threads_.simgui.overlays import dim_scale_overlay
from threads_.simgui.libs import graphics_draw_figure as gdf
from libs.varstructs.SIM_STATE import SIM_STATE
import os
from screeninfo import get_monitors
import traceback

# Window title for the simulation GUI
WIN_TITLE = "Simulation"

class simgui_t(threading.Thread):
    """
    A threaded class for managing the graphical user interface (GUI) of the simulation.
    Handles display, user inputs, and interactions for the double inverted pendulum simulation.
    """

    # Define the RECT structure for handling window positions and sizes
    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long)
        ]

    def __init__(self, config_dict, SIM_STATE_ref: SIM_STATE) -> None:
        """
        Initializes the GUI thread with configuration data and simulation state.

        Args:
            config_dict (dict): Configuration dictionary for GUI settings.
            SIM_STATE_ref (SIM_STATE): Reference to the simulation state object.
        """
        threading.Thread.__init__(self)
        self.SIM_STATE = SIM_STATE_ref
        self.config_dict = config_dict

        # Callback for stopping the simulation
        self.stop_callback_function = None
        self.stop_callback_f_args = None

        # Default window properties
        self.win_w: int = self.config_dict["sim_gui_config"]["def_win_width_px"]
        self.win_h: int = self.config_dict["sim_gui_config"]["def_win_height_px"]
        self.win_x: int = 0
        self.win_y: int = 0

        # Figure positioning
        self.rect_y = self.win_h - self.config_dict["graphics_config"]["figure_pos_y_px"]

        self.is_fullscreen = False
        self.rdt_cntr_update_flag = True
        self.rdt_cntr_strt_1 = -1
        self.rdt_cntr_strt_2 = -1

        # Initialize the pygame window
        self.init_pygame_panel()

    def set_stop_callback_function(self, stop_callback_function, *args):
        """
        Sets a callback function to be executed when the simulation stops.

        Args:
            stop_callback_function (function): The callback function.
            *args: Additional arguments for the callback function.
        """
        self.stop_callback_function = stop_callback_function
        self.stop_callback_f_args = args

    def run(self) -> None:
        """
        Main loop for the simulation GUI. Processes events, updates the display, and handles user inputs.
        """
        last_center_top_msg = ""
        string_tmp_1 = ""

        is_active = False
        cursor_in_window = False

        # Determine pendulum type for the display message
        if self.SIM_STATE.get_data_by_key("simulation_config.DOUBLE_PENDULUM"):
            if self.config_dict["geometry_config"]["rod_b_visibile"]:
                string_tmp_1 = "double pendulum, second rod visible"
            else:
                string_tmp_1 = "double pendulum, second rod invisible"
        else:
            string_tmp_1 = "single pendulum"

        # Main event loop
        while self.SIM_STATE.run_status() != 0:  # 0 - Nothing running, 1 - Static run, 2 - Simulation running
            tmp_timer_for_fps_start = time.time()

            to_status_zero_flag = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Handle window close event
                    self.SIM_STATE.set_run_status(0)
                    to_status_zero_flag = True

                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize event
                    self._window_resize_listener()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Start or pause simulation
                        if self.SIM_STATE.run_status() == 1:
                            if len(self.SIM_STATE.get_data_by_key("mouse_input.dx")) > 1:
                                self.SIM_STATE.set_run_status(2)  # Start simulation

                        elif self.SIM_STATE.run_status() == 2:
                            self.SIM_STATE.set_run_status(1)  # Pause simulation

                    elif event.key == pygame.K_q:
                        # Quit simulation
                        self.SIM_STATE.set_run_status(0)
                        to_status_zero_flag = True

                # Check if the window is active or inactive
                if event.type == pygame.ACTIVEEVENT:
                    if event.state == 1:  # Focus change event
                        is_active = bool(event.gain)  # 1 for active, 0 for inactive

                # Check if the mouse is within the Pygame window
                if event.type == pygame.MOUSEMOTION:
                    cursor_in_window = pygame.mouse.get_focused()

            if to_status_zero_flag:
                break

            if cursor_in_window and is_active and self.SIM_STATE.get_data_by_key("GUI_conditions.INFINITE_SPACE"):
                # Infinite mouse movement handling
                x, y = pygame.mouse.get_pos()

                if self.SIM_STATE.SIM_STATE_VAR["mouse_input"]["cursor_replace_flag"] == 0:
                    if x < 2:
                        pygame.mouse.set_pos(self.win_w - 2, y)
                        self.SIM_STATE.SIM_STATE_VAR["mouse_input"]["replace_counter"] -= 1
                    elif x > self.win_w - 2:
                        pygame.mouse.set_pos(2, y)
                        self.SIM_STATE.SIM_STATE_VAR["mouse_input"]["replace_counter"] += 1

            # Fill background
            self.window.fill(self.config_dict["sim_gui_config"]["bg_color_-"])

            # Update window position
            self._window_pos_update()

            # Draw the simulation figure
            if len(self.SIM_STATE.read_mouse_input("x", False)) > 0:
                raw_cart_x = (self.SIM_STATE.read_mouse_input("x", True)[-1][0] -
                              self.SIM_STATE.get_data_by_key("mouse_input.replace_counter") * (self.win_w - 2))

                DoF_State = self.SIM_STATE.read_DoF_State_Stack(-1, True)[0]
                cart_x = self.mouse_pos_to_viewport_pos(raw_cart_x)

                end_a, end_b = gdf.draw_figure(
                    self,
                    cart_x,
                    self.rect_y,
                    DoF_State[0][0],
                    DoF_State[1][0],
                    self.SIM_STATE.get_l1(),
                    self.SIM_STATE.get_l2(),
                    self.config_dict["graphics_config"]["figure_config"],
                    self.SIM_STATE.get_data_by_key("GUI_conditions.dim_scale"),
                    self.config_dict["geometry_config"]["mass_visibile"],
                    self.config_dict["geometry_config"]["rod_a_visibile"],
                    self.SIM_STATE.get_data_by_key("simulation_config.DOUBLE_PENDULUM") and self.config_dict["geometry_config"]["rod_b_visibile"],
                    self.SIM_STATE.get_data_by_key("GUI_conditions.INFINITE_SPACE")
                )

            # Display static or simulation messages
            if self.SIM_STATE.run_status() == 1:  # Static run
                self.rdt_cntr_update_flag = True
                msg_overlay.msg_center(self, "Press SPACE to start the simulation or Q to quit")

            elif self.SIM_STATE.run_status() == 2:  # Simulation running
                last_center_top_msg = f"{time.time() - self.SIM_STATE.get_data_by_key('run_conditions.simulation_timer')['start']:.2f} s"

            msg_overlay.msg_center_top(self, last_center_top_msg)

            # Update right-top overlay messages
            msg_right_top_str = f"{self.SIM_STATE.SIM_STATE_VAR['meta']['SIM_TITLE']}\n{string_tmp_1}"
            msg_overlay.msg_left_top(self, msg_right_top_str)

            # Update dimension scale overlay
            x_axis_start_pos, x_axis_end_pos, y_axis_start_pos, y_axis_end_pos, x_axis_length_in_m, y_axis_length_in_m, x_axis_unti, y_axis_unti, rot_ref_end_pos, phi_ref_deg_rounded = dim_scale_overlay.calculate_dim_scale_props(
                self, 10, self.rect_y, self.SIM_STATE.get_data_by_key("GUI_conditions.dim_scale"))
            dim_scale_overlay.draw_dim_scale(self, x_axis_start_pos, x_axis_end_pos, y_axis_start_pos, y_axis_end_pos, x_axis_length_in_m, y_axis_length_in_m, x_axis_unti, y_axis_unti, rot_ref_end_pos, phi_ref_deg_rounded)

            # Refresh display
            pygame.display.flip()
            self.clock.tick(60)

            # Update FPS
            divider = (time.time() - tmp_timer_for_fps_start)
            self.SIM_STATE.set_data_by_key("run_conditions.fps", 1 / max(divider, 1e-6))

        if self.stop_callback_function is not None:
            self.stop_callback_function()

        simgui_t.pygame_quit()
        print("SimGUI thread finished.")
def pygame_quit():
    """
    Safely quits the Pygame window and handles any potential exceptions.
    """
    print("SimGUI thread: Close pygame panel...")
    try:
        pygame.quit()
    except Exception as e:
        traceback.print_exc()
        print(f"Error: {e}")

def set_cursor_visibility(self, visible):
    """
    Sets the visibility of the cursor in the Pygame window.

    Parameters:
        visible (bool): If True, the cursor is visible; otherwise, it is hidden.
    """
    pygame.mouse.set_visible(visible)

def maximize_pygame_window(self):
    """
    Maximizes the Pygame window using Windows API.
    """
    win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)

def toggle_fullscreen(self):
    """
    Toggles between fullscreen and windowed mode.
    """
    self.set_fullscreen(not self.is_fullscreen)

def set_fullscreen(self, fullscreen=True):
    """
    Sets the window to fullscreen or resizable mode.

    Parameters:
        fullscreen (bool): If True, enables fullscreen mode; otherwise, sets resizable mode.
    """
    if self.is_fullscreen != fullscreen:
        if fullscreen:
            pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
        self.is_fullscreen = fullscreen

def init_pygame_panel(self):
    """
    Initializes the Pygame window with specified configurations and positions it on the correct monitor.
    """
    monitors = get_monitors()
    open_on_monitor_id = self.config_dict["sim_gui_config"]["open_on_monitor_id"]

    # Initialize Pygame
    pygame.init()

    # Position the window on the specified monitor
    if len(monitors) > open_on_monitor_id:
        target_monitor = monitors[open_on_monitor_id]
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{target_monitor.x},{target_monitor.y}"

    # Create a resizable Pygame window
    self.window = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
    pygame.display.set_caption(WIN_TITLE)

    # Get the window handle (HWND) for further manipulations
    self.hwnd = pygame.display.get_wm_info()['window']

    # Set fullscreen or hide cursor if specified in the configuration
    if self.SIM_STATE.get_data_by_key("GUI_conditions.INFINITE_SPACE") or self.SIM_STATE.get_data_by_key("GUI_conditions.FULLSCREEN"):
        self.set_fullscreen(True)
        self.set_cursor_visibility(False)
    else:
        self.maximize_pygame_window()

    # Define required Windows API functions and constants
    self.GetWindowLong = ctypes.windll.user32.GetWindowLongW
    self.GetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int]
    self.GetWindowLong.restype = ctypes.c_long

    self.GetWindowRect = ctypes.windll.user32.GetWindowRect
    self.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(simgui_t.RECT)]

    self.GWL_STYLE = -16  # Constant for getting the window style
    self.WS_MAXIMIZE = 0x01000000  # Constant for checking maximized state

    # Update window dimensions and state
    self._window_resize_listener()

    # Create a clock for managing frame rates
    self.clock = pygame.time.Clock()

def mouse_pos_to_viewport_pos(self, mouse_pos_x):
    """
    Converts the mouse position in screen coordinates to the corresponding viewport position.

    Parameters:
        mouse_pos_x (int): The mouse x-coordinate on the screen.

    Returns:
        int: The x-coordinate of the mouse relative to the viewport.
    """
    return mouse_pos_x - self.win_x
    if self._is_maximized():
        return mouse_pos_x
    else:
        return mouse_pos_x - self.win_x

def _is_maximized(self):
    """
    Checks if the window is currently maximized.

    Returns:
        bool: True if the window is maximized, False otherwise.
    """
    style = self.GetWindowLong(self.hwnd, self.GWL_STYLE)
    return (style & self.WS_MAXIMIZE) == self.WS_MAXIMIZE

def _window_pos_update(self):
    """
    Updates the position of the simulation window on the screen by fetching its current coordinates.
    """
    rect = simgui_t.RECT()
    self.GetWindowRect(self.hwnd, ctypes.byref(rect))
    # Calculate the top-left corner (x, y) of the window
    self.win_x, self.win_y = rect.left, rect.top

def _window_resize_listener(self):
    """
    Handles changes to the window size and updates relevant simulation parameters accordingly.
    """
    self.win_w, self.win_h = pygame.display.get_surface().get_size()
    dim_scale = dim_scale_overlay.calculate_fit_dim_scale(
        self.win_w,
        self.win_h,
        self.SIM_STATE.get_l1(), 
        self.SIM_STATE.get_l2(),
        self.config_dict["graphics_config"]["figure_config"]["mass_height_px"],
        self.config_dict["graphics_config"]["figure_pos_y_px"],
        self.SIM_STATE.get_data_by_key("GUI_conditions.meter_per_pixel"),
        self.config_dict["graphics_config"]["figure_config"]["rod_section_ratio_-"],
        self.config_dict["input_config"]["scale_rotation_-"],
        self.config_dict["input_config"]["scale_x_axis_-"],
        self.SIM_STATE.get_data_by_key("simulation_config.DOUBLE_PENDULUM") and self.config_dict["geometry_config"]["rod_b_visibile"]
    )
    self.SIM_STATE.set_data_by_key("GUI_conditions.dim_scale", dim_scale)
    self.SIM_STATE.set_data_by_key("GUI_conditions.WIN_DIMS", [self.win_w, self.win_h])
    self.rect_y = self.win_h - self.config_dict["graphics_config"]["figure_pos_y_px"]

def check_for_length_decrease(self):
    """
    Checks whether the rod lengths need to be decreased based on the simulation configuration and updates the lengths accordingly.
    """
    if not self.config_dict["simulation_config"]["constant_rod_length"]:
        time_now = time.time()

        if self.rdt_cntr_update_flag:
            # Initialize rod lengths and counters
            self.SIM_STATE.SIM_STATE_VAR["simulation_config"]["l1"] = []
            self.SIM_STATE.SIM_STATE_VAR["simulation_config"]["l1"].append([
                self.config_dict["geometry_config"]["rod_a_length_m"], 0
            ])
            self.SIM_STATE.SIM_STATE_VAR["simulation_config"]["l2"] = []
            self.SIM_STATE.SIM_STATE_VAR["simulation_config"]["l2"].append([
                self.config_dict["geometry_config"]["rod_b_length_m"], 0
            ])
            self.rdt_cntr_strt_1 = time_now
            self.rdt_cntr_strt_2 = time_now
            self.rdt_cntr_update_flag = False
        else:
            if self.config_dict["simulation_config"]["rod_a_dt_s"] == self.config_dict["simulation_config"]["rod_b_dt_s"]:
                if (
                    self.config_dict["simulation_config"]["rod_a_dt_s"] > 0.0001 and
                    self.rdt_cntr_strt_1 + self.config_dict["simulation_config"]["rod_a_dt_s"] < time_now
                ):
                    self.rdt_cntr_strt_1 = time_now
                    self.rdt_cntr_strt_2 = time_now
                    self.rod_length_decrease_action(
                        self.config_dict["simulation_config"]["rod_a_dl_m"],
                        self.config_dict["simulation_config"]["rod_b_dl_m"]
                    )
            else:
                if (
                    self.config_dict["simulation_config"]["rod_a_dt_s"] > 0.0001 and
                    self.rdt_cntr_strt_1 + self.config_dict["simulation_config"]["rod_a_dt_s"] < time_now
                ):
                    self.rdt_cntr_strt_1 = time_now
                    self.rod_length_decrease_action(
                        self.config_dict["simulation_config"]["rod_a_dl_m"], 0
                    )

                if (
                    self.config_dict["simulation_config"]["rod_b_dt_s"] > 0.0001 and
                    self.rdt_cntr_strt_2 + self.config_dict["simulation_config"]["rod_b_dt_s"] < time_now
                ):
                    self.rdt_cntr_strt_2 = time_now
                    self.rod_length_decrease_action(
                        0, self.config_dict["simulation_config"]["rod_b_dl_m"]
                    )

def rod_length_decrease_action(self, dL1, dL2):
    """
    Updates the rod lengths by reducing them based on the specified values.

    Parameters:
        dL1 (float): The amount by which the length of rod A should be decreased.
        dL2 (float): The amount by which the length of rod B should be decreased.
    """
    l1 = self.SIM_STATE.get_l1()
    l2 = self.SIM_STATE.get_l2()
    if l2 is None:
        self.SIM_STATE.update_sys_variables(l1 - dL1, None)
    else:
        self.SIM_STATE.update_sys_variables(l1 - dL1, l2 - dL2)
