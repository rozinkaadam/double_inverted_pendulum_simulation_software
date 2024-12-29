import threading
import time
import threads_.diag.diag_update_loop as diag_update_loop
from libs.varstructs.SIM_STATE import SIM_STATE

class diag_t(threading.Thread):
    def __init__(self, config_dict_ref, SIM_STATE_ref : SIM_STATE, diag_gui) -> None:
        threading.Thread.__init__(self)
        self.config_dict            = config_dict_ref
        self.SIM_STATE              = SIM_STATE_ref
        self.diag_gui               = diag_gui

    def run(self):
        while self.SIM_STATE.run_status() is not 0:
            diag_update_loop.diag_update_values(self.SIM_STATE,self.diag_gui)
            time.sleep(self.SIM_STATE.get_data_by_key("simulation_config.SAMPLERATE_S"))
        
        print("Diag thread stopping...")
