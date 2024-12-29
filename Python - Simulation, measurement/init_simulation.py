from libs.varstructs import SIM_STATE
from libs import set_displays
from libs import pointer_enhance
from libs import get_dpi_scaling
from threads_.diag import diag_t
from threads_.numsim import numsim_t
from threads_.simgui import simgui_t
import threads_.diag.diag_gui as diag_gui

class simulationManager:
    """
    Manages the initialization and execution of the simulation, including its graphical and numerical components,
    as well as diagnostic tools.

    Attributes:
        config_dict (dict): The configuration dictionary for the simulation.
        diag_frame_ref: A reference to the diagnostic frame for displaying information.
        SIM_STATE (SIM_STATE): Manages the state variables and configurations of the simulation.
        disp_settings: Display settings used for infinite space mode.
        simgui_thread (simgui_t): The graphical interface thread for the simulation.
        numsim_thread (numsim_t): The numerical simulation thread.
        diag_gui (diag_gui_widget): The GUI for diagnostics.
        diag_thread (diag_t): The diagnostic thread.
    """

    def __init__(self, config_dict_ref, diag_frame_ref) -> None:
        """
        Initializes the simulation manager and its components.

        Parameters:
            config_dict_ref (dict): The simulation configuration dictionary.
            diag_frame_ref: A reference to the diagnostic frame for displaying information.
        """
        self.config_dict = config_dict_ref
        self.diag_frame_ref = diag_frame_ref

        # Fetch DPI scaling for GUI adjustments
        DPI_SCALE = get_dpi_scaling.get_dpi_scaling()

        # Initialize the simulation state
        self.SIM_STATE = SIM_STATE.SIM_STATE(self.config_dict, DPI_SCALE)
        self._init_threads()

    def _init_threads(self):
        """
        Initializes threads for simulation GUI, numerical simulation, and diagnostics.
        Adjusts display settings and pointer precision as needed for the simulation.
        """
        infinite_space = self.SIM_STATE.get_data_by_key("GUI_conditions.INFINITE_SPACE")
        self.disp_settings = None

        # Adjust display settings for infinite space mode
        if infinite_space:
            self.disp_settings = set_displays.set_correct_display_settings(False)

        # Disable pointer precision enhancement for accurate simulation
        pointer_enhance.set_enhance_pointer_precision(False)
        pointer_enhance_status = pointer_enhance.is_enhance_pointer_precision_enabled()
        print(f"pointer_enhance_status: {pointer_enhance_status}")
        self.SIM_STATE.pointer_enhance_status = pointer_enhance_status

        # Initialize GUI, numerical simulation, and diagnostic threads
        self.simgui_thread = simgui_t.simgui_t(self.config_dict, self.SIM_STATE) 
        self.numsim_thread = numsim_t.numsim_t(self.config_dict, self.SIM_STATE)
        self.diag_gui = diag_gui.diag_gui_widget(self.diag_frame_ref, self.SIM_STATE)
        self.diag_thread = diag_t.diag_t(self.config_dict, self.SIM_STATE, self.diag_gui)
        
    def start_threads(self):
        """
        Starts the threads for GUI, numerical simulation, and diagnostics.
        Sets the initial run status and ensures proper thread startup.
        """
        self.SIM_STATE.set_run_status(1)
        self.simgui_thread.set_stop_callback_function(self.after_threads_stops, self)
        
        # Start the simulation GUI, numerical simulation, and diagnostic threads
        self.simgui_thread.start()
        self.numsim_thread.start()
        self.diag_thread.start()

    def after_threads_stops(self):
        """
        Callback function executed after the simulation threads stop.
        Restores display settings and pointer precision to their original state.
        """
        set_displays.restore_og_display_settings(self.disp_settings)
        pointer_enhance.set_enhance_pointer_precision(True)
        pointer_enhance.is_enhance_pointer_precision_enabled()
