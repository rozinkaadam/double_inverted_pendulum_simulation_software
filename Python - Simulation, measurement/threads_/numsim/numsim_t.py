import threading
from libs.varstructs.SIM_STATE import SIM_STATE
import time
from threads_.numsim.num_sim_loop import num_sim_update

class numsim_t(threading.Thread):
    """
    A threaded class to run the simulation loop for the double inverted pendulum on a cart system.

    Attributes:
        config_dict (dict): A dictionary containing simulation configuration values.
        SIM_STATE (SIM_STATE): An instance of SIM_STATE that manages the simulation's state.
    """

    def __init__(self, config_dict_ref, SIM_STATE_ref: SIM_STATE) -> None:
        """
        Initializes the numsim_t class.

        Args:
            config_dict_ref (dict): A reference to the simulation configuration dictionary.
            SIM_STATE_ref (SIM_STATE): A reference to the SIM_STATE object for simulation state management.
        """
        threading.Thread.__init__(self)
        self.config_dict = config_dict_ref  # Store the reference to the configuration dictionary.
        self.SIM_STATE = SIM_STATE_ref      # Store the reference to the SIM_STATE object.

    def run(self) -> None:
        """
        Starts the simulation thread and continuously updates the simulation state while it is active.
        """
        while self.SIM_STATE.run_status() != 0:  # 0 indicates the simulation is stopped.
            # Update the simulation state using the num_sim_update function.
            num_sim_update(self.SIM_STATE, self.config_dict["simulation_config"]["maximum_theta1_rad"])

            # Sleep for the simulation's sampling rate to control update frequency.
            time.sleep(self.SIM_STATE.get_data_by_key("simulation_config.SAMPLERATE_S"))

        return super().run()
