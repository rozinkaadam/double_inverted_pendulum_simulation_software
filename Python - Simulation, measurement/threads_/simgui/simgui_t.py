import threading
import time
import pygame
import ctypes
from ctypes import wintypes
import threading
import win32gui
import win32con
import time
from threads_.simgui.overlays import msg_overlay
from threads_.simgui.overlays import dim_scale_overlay
from threads_.simgui.libs import graphics_draw_figure as gdf
from libs.varstructs.SIM_STATE import SIM_STATE
import os 
from screeninfo import get_monitors
import traceback

WIN_TITLE = "Simulation"

class simgui_t(threading.Thread):
    """
    A thread-based GUI class for simulating a double inverted pendulum on a cart.
    
    This class handles the graphical user interface using Pygame, manages window events,
    and displays simulation parameters and graphics. It interacts with the simulation state
    through the SIM_STATE object.
    
    Attributes:
        SIM_STATE (SIM_STATE): Reference to the simulation state.
        config_dict (dict): Configuration dictionary for GUI and simulation settings.
    """

    # Define the RECT structure
    class RECT(ctypes.Structure):
        """
        A structure representing a rectangle, used for graphical calculations.
        
        Attributes:
            left (int): Left boundary of the rectangle.
            top (int): Top boundary of the rectangle.
            right (int): Right boundary of the rectangle.
            bottom (int): Bottom boundary of the rectangle.
        """
        _fields_ = [("left", ctypes.c_long),
                    ("top", ctypes.c_long),
                    ("right", ctypes.c_long),
                    ("bottom", ctypes.c_long)]

    def __init__(self, config_dict, SIM_STATE_ref):
        """
        Initialize the GUI thread with configuration and simulation state.

        Args:
            config_dict (dict): Configuration settings for the GUI and simulation.
            SIM_STATE_ref (SIM_STATE): Reference to the simulation state object.
        """
        threading.Thread.__init__(self)
        self.SIM_STATE = SIM_STATE_ref
        self.config_dict = config_dict

        self.stop_callback_function = None
        self.stop_callback_f_args = None

        # Set default properties
        # Window properties
        self.win_w = self.config_dict["sim_gui_config"]["def_win_width_px"]
        self.win_h = self.config_dict["sim_gui_config"]["def_win_height_px"]
        self.win_x = 0
        self.win_y = 0

        # Figure start position
        self.rect_y = self.win_h - self.config_dict["graphics_config"]["figure_pos_y_px"]

        self.is_fullscreen = False

        self.rdt_cntr_update_flag = True
        self.rdt_cntr_strt_1 = -1
        self.rdt_cntr_strt_2 = -1

        self.init_pygame_panel()

    def set_stop_callback_function(self, stop_callback_function, *args):
        """
        Set a callback function to be called when the simulation stops.

        Args:
            stop_callback_function (function): The callback function.
            *args: Additional arguments for the callback function.
        """
        self.stop_callback_function = stop_callback_function
        self.stop_callback_f_args = args

    def run(self):
        """
        Main thread function to handle GUI events and updates during the simulation.
        """
        last_center_top_msg = ""
        string_tmp_1 = ""

        is_active = False
        cursor_in_window = False

        # Determine simulation type
        if self.SIM_STATE.get_data_by_key("simulation_config.DOUBLE_PENDULUM"):
            if self.config_dict["geometry_config"]["rod_b_visibile"]:
                string_tmp_1 = "double pendulum, second rod visible"
            else:
                string_tmp_1 = "double pendulum, second rod invisible"
        else:
            string_tmp_1 = "single pendulum"

        # Main loop for handling events and rendering
        while self.SIM_STATE.run_status() != 0:  # 0 - Nothing running, 1 - Static run, 2 - Run simulation
            tmp_timer_for_fps_start = time.time()

            to_status_zero_flag = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.SIM_STATE.set_run_status(0)
                    to_status_zero_flag = True

                elif event.type == pygame.VIDEORESIZE:
                    self._window_resize_listener()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Toggle simulation state between static run and running simulation
                        if self.SIM_STATE.run_status() == 1:
                            if len(self.SIM_STATE.get_data_by_key("mouse_input.dx")) > 1:
                                self.SIM_STATE.set_run_status(2)

                        elif self.SIM_STATE.run_status() == 2:
                            self.SIM_STATE.set_run_status(1)

                    elif event.key == pygame.K_q:
                        self.SIM_STATE.set_run_status(0)
                        to_status_zero_flag = True

                # Check if the window is active or inactive
                if event.type == pygame.ACTIVEEVENT:
                    if event.state == 1:  # Window focus changes
                        is_active = bool(event.gain)

                # Check if the mouse is over the Pygame window
                if event.type == pygame.MOUSEMOTION:
                    cursor_in_window = pygame.mouse.get_focused()

            if to_status_zero_flag:
                break

            # Handle infinite space for mouse cursor
            if cursor_in_window and is_active and self.SIM_STATE.get_data_by_key("GUI_conditions.INFINITE_SPACE"):
                x, y = pygame.mouse.get_pos()

                if self.SIM_STATE.SIM_STATE_VAR["mouse_input"]["cursor_replace_flag"] == 0:
                    if x < 2:
                        self.SIM_STATE.SIM_STATE_VAR["mouse_input"]["cursor_replace_flag"] = 1
                        pygame.mouse.set_pos(self.win_w - 2, y)
                        self.SIM_STATE.SIM_STATE_VAR["mouse_input"]["replace_counter"] -= 1
                        self.SIM_STATE.SIM_STATE_VAR["mouse_input"]["cursor_replace_flag"] = 2
                    elif x > self.win_w - 2:
                        self.SIM_STATE.SIM_STATE_VAR["mouse_input"]["cursor_replace_flag"] = 1
                        pygame.mouse.set_pos(2, y)
                        self.SIM_STATE.SIM_STATE_VAR["mouse_input"]["replace_counter"] += 1
                        self.SIM_STATE.SIM_STATE_VAR["mouse_input"]["cursor_replace_flag"] = 2

            # Fill background with color
            self.window.fill(self.config_dict["sim_gui_config"]["bg_color_-"])

            self._window_pos_update()

            # Handle mouse input and draw pendulum
            if len(self.SIM_STATE.read_mouse_input("x", False)) > 0:
                raw_cart_x = (self.SIM_STATE.read_mouse_input("x", True)[-1][0] -
                              self.SIM_STATE.get_data_by_key("mouse_input.replace_counter") * (self.win_w - 2) +
                              self.SIM_STATE.read_PD_u_q()[2])

                DoF_State = self.SIM_STATE.read_DoF_State_Stack(-1, True)[0]
                cart_x = self.mouse_pos_to_viewport_pos(raw_cart_x)

                end_a, end_b = gdf.draw_figure(self,
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
                                               self.SIM_STATE.get_data_by_key("simulation_config.DOUBLE_PENDULUM") and
                                               self.config_dict["geometry_config"]["rod_b_visibile"],
                                               self.SIM_STATE.get_data_by_key("GUI_conditions.INFINITE_SPACE"))

            # Display messages and overlay information
            if self.SIM_STATE.run_status() == 1:
                self.rdt_cntr_update_flag = True
                msg_overlay.msg_center(self, "Press...\nSPACE - start a new simulation\nQ - quit")
            elif self.SIM_STATE.run_status() == 2:
                self.check_for_length_decrease()
                last_center_top_msg = f"{time.time() - self.SIM_STATE.get_data_by_key('run_conditions.simulation_timer')['start']:.2f} s"

            msg_overlay.msg_center_top(self, last_center_top_msg)

            msg_right_top_str=f"{self.SIM_STATE.SIM_STATE_VAR["meta"]["SIM_TITLE"]}\n{string_tmp_1}"
            if self.SIM_STATE.get_data_by_key("simulation_config.DOUBLE_PENDULUM"):
                msg_right_top_str+=f"\nrod a length [m]: {self.SIM_STATE.get_l1():.2f}"
                msg_right_top_str+=f"\nrod b length [m]: {self.SIM_STATE.get_l2():.2f}"
            else:
                msg_right_top_str+=f"\nrod a length [m]: {self.SIM_STATE.get_l1():.2f}"
            
            msg_right_top_str+=f"\ntime delay [s]: {self.config_dict["simulation_config"]["time_delay_s"]:.2f}"
            msg_right_top_str+=f"\nnumeric method: {self.SIM_STATE.get_data_by_key("simulation_config.NUM_METHOD")}"
            msg_right_top_str+=f"\nresolution [px]: {self.SIM_STATE.get_data_by_key("GUI_conditions.WIN_DIMS")}"
            msg_right_top_str+=f"\nfps: {self.SIM_STATE.get_data_by_key("run_conditions.fps"):.2f}"
            if self.SIM_STATE.get_data_by_key("PD_control.PD_CONTROL_ON"):
                msg_right_top_str+=f"\nControl method: {self.SIM_STATE.get_data_by_key("PD_control.CONTROL_METHOD")}"
                msg_right_top_str+=f"\ntimedelay: {(self.SIM_STATE.get_frame_trim(True)*self.SIM_STATE.get_data_by_key("simulation_config.SAMPLERATE_S")):.3f} s"
                msg_right_top_str+=f"\n -> K: [{self.SIM_STATE.get_data_by_key("PD_control.PD_K_1"):.2f}, {self.SIM_STATE.get_data_by_key("PD_control.PD_K_2"):.2f}, {self.SIM_STATE.get_data_by_key("PD_control.PD_K_3"):.2f}, {self.SIM_STATE.get_data_by_key("PD_control.PD_K_4"):.2f}]"
            else:
                msg_right_top_str+=f"\nWithout control loop."
            msg_overlay.msg_left_top(self,msg_right_top_str)
            
            x_axis_start_pos, x_axis_end_pos, y_axis_start_pos, y_axis_end_pos,x_axis_length_in_m,y_axis_length_in_m,x_axis_unti,y_axis_unti,rot_ref_end_pos, phi_ref_deg_rounded=dim_scale_overlay.calculate_dim_scale_props(
                self,10,self.rect_y,self.SIM_STATE.get_data_by_key("GUI_conditions.dim_scale"))
            dim_scale_overlay.draw_dim_scale(self,x_axis_start_pos, x_axis_end_pos, y_axis_start_pos, y_axis_end_pos,x_axis_length_in_m,y_axis_length_in_m,x_axis_unti,y_axis_unti,rot_ref_end_pos, phi_ref_deg_rounded)
            
            pygame.display.flip()
            self.clock.tick(60)

            divider = time.time() - tmp_timer_for_fps_start
            if divider < 0.00000001:
                divider = 0.00000001
            self.SIM_STATE.set_data_by_key("run_conditions.fps", 1 / divider)

        if self.stop_callback_function is not None:
            self.stop_callback_function()

        simgui_t.pygame_quit()
        print("SimGUI thread finished.")
        
    def pygame_quit():
        """
        Safely quit the Pygame environment and close the GUI panel.

        This function ensures that Pygame resources are properly released
        and prints a message indicating the closure process.
        """
        print("SimGUI thread: Close pygame panel...")
        try:
            pygame.quit()
        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}")

    def set_cursor_visibility(self, visible):
        """
        Set the visibility of the mouse cursor in the Pygame window.

        Args:
            visible (bool): If True, the cursor is visible; otherwise, it is hidden.
        """
        pygame.mouse.set_visible(visible)
    
    def maximize_pygame_window(self):
        """
        Maximize the Pygame window using Windows-specific API.
        """
        win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)

    def toggle_fullscreen(self):
        """
        Toggle the fullscreen mode of the Pygame window.
        """
        self.set_fullscreen(not self.is_fullscreen)

    def set_fullscreen(self, fullscreen=True):
        """
        Set the Pygame window to fullscreen or resizable mode.

        Args:
            fullscreen (bool): If True, the window is set to fullscreen mode; otherwise, it is resizable.
        """
        if self.is_fullscreen != fullscreen:
            if fullscreen:
                pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
            else:
                pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
            self.is_fullscreen = fullscreen

    def init_pygame_panel(self):
        """
        Initialize the Pygame panel with window settings and graphical configurations.

        This function configures the Pygame window's position, dimensions, and rendering properties.
        It also sets up the Windows API for additional functionalities.
        """
        monitors = get_monitors()
        open_on_monitor_id = self.config_dict["sim_gui_config"]["open_on_monitor_id"]

        # Initialize Pygame
        pygame.init()

        if len(monitors) > open_on_monitor_id:
            target_monitor = monitors[open_on_monitor_id]
            os.environ['SDL_VIDEO_WINDOW_POS'] = f"{target_monitor.x},{target_monitor.y}"

        # Create Pygame window
        self.window = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
        pygame.display.set_caption(WIN_TITLE)
        
        # Get the window handle (HWND)
        self.hwnd = pygame.display.get_wm_info()['window']

        # Hide the cursor or set fullscreen based on conditions
        if self.SIM_STATE.get_data_by_key("GUI_conditions.INFINITE_SPACE") or self.SIM_STATE.get_data_by_key("GUI_conditions.FULLSCREEN"):
            self.set_fullscreen(True)
            self.set_cursor_visibility(False)
        else:
            self.maximize_pygame_window()

        # Define necessary Windows API functions and constants
        self.GetWindowLong = ctypes.windll.user32.GetWindowLongW
        self.GetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int]
        self.GetWindowLong.restype = ctypes.c_long

        self.GetWindowRect = ctypes.windll.user32.GetWindowRect
        self.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(simgui_t.RECT)]

        # Constants for checking the maximized state
        self.GWL_STYLE = -16
        self.WS_MAXIMIZE = 0x01000000
        
        self._window_resize_listener()

        self.clock = pygame.time.Clock()
    
    def mouse_pos_to_viewport_pos(self, mouse_pos_x):
        """
        Convert the mouse position to the viewport position, adjusting for window coordinates.

        Args:
            mouse_pos_x (int): The x-coordinate of the mouse position.

        Returns:
            int: The x-coordinate adjusted to the viewport.
        """
        return mouse_pos_x - self.win_x

    def _is_maximized(self):
        """
        Check if the Pygame window is currently maximized.

        Returns:
            bool: True if the window is maximized, False otherwise.
        """
        style = self.GetWindowLong(self.hwnd, self.GWL_STYLE)
        return (style & self.WS_MAXIMIZE) == self.WS_MAXIMIZE

    def _window_pos_update(self):
        """
        Update the position of the Pygame window by retrieving its top-left corner coordinates.
        """
        rect = simgui_t.RECT()
        self.GetWindowRect(self.hwnd, ctypes.byref(rect))
        self.win_x, self.win_y = rect.left, rect.top

    def _window_resize_listener(self):
        """
        Update the window dimensions and adjust the simulation's dimensional scaling.
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
                                self.SIM_STATE.get_data_by_key("simulation_config.DOUBLE_PENDULUM") and self.config_dict["geometry_config"]["rod_b_visibile"])
        self.SIM_STATE.set_data_by_key("GUI_conditions.dim_scale", dim_scale)
        self.SIM_STATE.set_data_by_key("GUI_conditions.WIN_DIMS", [self.win_w, self.win_h])
        self.rect_y = self.win_h - self.config_dict["graphics_config"]["figure_pos_y_px"]

    def check_for_length_decrease(self):
        """
        Check if the lengths of the rods should be decreased over time, based on simulation configuration.
        """
        if not self.config_dict["simulation_config"]["constant_rod_length"]:
            time_now = time.time()

            if self.rdt_cntr_update_flag:
                self.SIM_STATE.SIM_STATE_VAR["simulation_config"]["l1"] = []
                self.SIM_STATE.SIM_STATE_VAR["simulation_config"]["l1"].append([
                    self.config_dict["geometry_config"]["rod_a_length_m"], 0])
                self.SIM_STATE.SIM_STATE_VAR["simulation_config"]["l2"] = []
                self.SIM_STATE.SIM_STATE_VAR["simulation_config"]["l2"].append([
                    self.config_dict["geometry_config"]["rod_b_length_m"], 0])
                self.rdt_cntr_strt_1 = time_now
                self.rdt_cntr_strt_2 = time_now
                self.rdt_cntr_update_flag = False
            else:
                if self.config_dict["simulation_config"]["rod_a_dt_s"] == self.config_dict["simulation_config"]["rod_b_dt_s"]:
                    if self.config_dict["simulation_config"]["rod_a_dt_s"] > 0.0001 and self.rdt_cntr_strt_1 + self.config_dict["simulation_config"]["rod_a_dt_s"] < time_now:    
                        self.rdt_cntr_strt_1 = time_now
                        self.rdt_cntr_strt_2 = time_now
                        self.rod_length_decrease_action(
                            self.config_dict["simulation_config"]["rod_a_dl_m"],
                            self.config_dict["simulation_config"]["rod_b_dl_m"])
                else:
                    if self.config_dict["simulation_config"]["rod_a_dt_s"] > 0.0001 and self.rdt_cntr_strt_1 + self.config_dict["simulation_config"]["rod_a_dt_s"] < time_now:
                        self.rdt_cntr_strt_1 = time_now
                        self.rod_length_decrease_action(self.config_dict["simulation_config"]["rod_a_dl_m"], 0)

                    if self.config_dict["simulation_config"]["rod_b_dt_s"] > 0.0001 and self.rdt_cntr_strt_2 + self.config_dict["simulation_config"]["rod_b_dt_s"] < time_now:
                        self.rdt_cntr_strt_2 = time_now
                        self.rod_length_decrease_action(0, self.config_dict["simulation_config"]["rod_b_dl_m"])

    def rod_length_decrease_action(self, dL1, dL2):
        """
        Decrease the lengths of the rods in the simulation state.

        Args:
            dL1 (float): Decrease in length for rod A.
            dL2 (float): Decrease in length for rod B.
        """
        l1 = self.SIM_STATE.get_l1()
        l2 = self.SIM_STATE.get_l2()
        if l2 is None:
            self.SIM_STATE.update_sys_variables(l1 - dL1, None)        
        else:
            self.SIM_STATE.update_sys_variables(l1 - dL1, l2 - dL2)