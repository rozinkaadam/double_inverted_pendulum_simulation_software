import threading
import time
import threads_.diag.diag_update_loop as diag_update_loop
from libs.varstructs.SIM_STATE import SIM_STATE

class diag_t(threading.Thread):
    """
    This class represents a diagnostic thread for the simulation.
    It inherits from threading.Thread and manages the diagnostic updates
    during the simulation runtime.

    Attributes:
        config_dict (dict): Reference to the configuration dictionary.
        SIM_STATE (SIM_STATE): Reference to the simulation state object.
        diag_gui: GUI object used for displaying diagnostic information.
    """
    def __init__(self, config_dict_ref, SIM_STATE_ref : SIM_STATE, diag_gui) -> None:
        """
        Initializes the diagnostic thread with references to configuration, 
        simulation state, and diagnostic GUI.

        Args:
            config_dict_ref (dict): Reference to the configuration dictionary.
            SIM_STATE_ref (SIM_STATE): Reference to the simulation state object.
            diag_gui: GUI object used for displaying diagnostic information.
        """
        threading.Thread.__init__(self)
        self.config_dict            = config_dict_ref
        self.SIM_STATE              = SIM_STATE_ref
        self.diag_gui               = diag_gui

    def run(self):
        """
        Main execution loop of the diagnostic thread. Continuously updates
        diagnostic values as long as the simulation is running. It uses the
        simulation state's `run_status` to determine whether to stop the loop.

        The update frequency is controlled by the `SAMPLERATE_S` value
        from the simulation configuration.
        """
        while self.SIM_STATE.run_status() != 0:
            diag_update_loop.diag_update_values(self.SIM_STATE, self.diag_gui)
            time.sleep(self.SIM_STATE.get_data_by_key("simulation_config.SAMPLERATE_S"))
        
        print("Diag thread stopping...")
