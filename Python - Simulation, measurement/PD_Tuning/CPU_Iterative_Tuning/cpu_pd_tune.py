import cpu_pd_tune_funs 
from cpu_pd_tune_animation import play_animation
import numpy as np
from datetime import datetime
import pandas as pd
from pathlib import Path

class PD_Controller:
    def __init__(self, title, M_data):
        """
        Initializes the PD_Controller class with the given title and simulation configuration data.

        Args:
            title (str): Title for the controller instance.
            M_data (dict): Configuration data for the PD tuning process.
        """
        self.title = title
        self.directory = Path("PD_tuning_saves")
        self.path = self.directory.joinpath(f'{title}.pkl')
        self.M_data = M_data
        self.l1 = M_data["sys_consts_double"][5]
        self.l2 = M_data["sys_consts_double"][6]
        self.D_a = M_data["D_a"]
        self.tau = M_data["delay"]
        self.simTs = M_data["simTs"]
        self.D_cor_P = M_data["D_cor_P"]
        self.D_cor_D = M_data["D_cor_D"]
        self._raw_results = None
        self.ordered_runs = None  # Contains detailed results.
        self.ordered_results = None  # Contains summarized results.

    def load_from_pkl_file(self):
        """
        Loads simulation results from a pickle file.

        Returns:
            self: Returns the instance after loading.
        """
        self.set_ord_runs(cpu_pd_tune_funs.load_runs_from_file(self.path))
        return self

    def generate_optimization(self, M_data=None):
        """
        Runs the PD optimization process.

        Args:
            M_data (dict, optional): New configuration data to replace the current one.

        Returns:
            self: Returns the instance after optimization.
        """
        if M_data is not None:
            self.M_data = M_data
        self._raw_results = cpu_pd_tune_funs.M_data_iterate(self.M_data, X_0, USABLE_CORES_ARRAY)
        print("Iteration finished.")
        self.set_ord_runs(cpu_pd_tune_funs.calc_PD_scores(self._raw_results, self.simTs))
        cpu_pd_tune_funs.save_runs_to_file(self.ordered_runs, self.path)
        return self

    def printresults(self):
        """
        Prints the summarized results.

        Returns:
            self: Returns the instance.
        """
        print("________________RESULTS________________")
        print(self.ordered_results)
        return self

    def plot_PD_p(self):
        """
        Plots the PD plane and associated results.

        Returns:
            self: Returns the instance.
        """
        cpu_pd_tune_funs.plot_PD_plane(self.ordered_runs, self.D_cor_P, self.D_cor_D, self.D_a, self.tau)
        return self

    def play_animation(self, index=0):
        """
        Plays the animation for a specific simulation result.

        Args:
            index (int): Index of the result to animate (default: 0).

        Returns:
            self: Returns the instance.
        """
        sel_run = self.ordered_runs[index]
        play_animation(sel_run["data_stream"], sel_run["Kp_phi1"], sel_run["Kd_phi1"], self.l1, self.l2, self.simTs)
        return self

    def save_best_pair(self):
        """
        Saves the best simulation result to a CSV file.

        Returns:
            self: Returns the instance.
        """
        cpu_pd_tune_funs.save_a_run_to_file(self.ordered_runs[0], self.title)
        return self

    def set_ord_runs(self, v):
        """
        Sets the ordered runs and updates summarized results.

        Args:
            v (list): Detailed simulation results.
        """
        self.ordered_runs = v
        self._filter_ordered_results()

    def _filter_ordered_results(self):
        """
        Filters and summarizes detailed simulation results into a DataFrame.
        """
        ordered_results = [
            {
                "Kp_phi1": res["Kp_phi1"],
                "Kd_phi1": res["Kd_phi1"],
                "time": res["time"],
                "finish_flag": res["finish_flag"],
                "phi1_square_sum": res["phi1_square_sum"],
            }
            for res in self.ordered_runs
        ]
        self.ordered_results = pd.DataFrame(ordered_results)
    
USABLE_CORES_ARRAY = np.array([False, True, True, True, True, True, True, True])
X_0 = np.array([[-0.01], [0], [0], [0]])

# Run optimized PD tuning
if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reaction_time_s = 0.3457119703292847
    time_stamp_s    = 0.011291212918763702

    # Constants and initial conditions
    M_1_data = {
        "sys_consts_double" : [18.0000, 0.333333333333333, 1.5000, -73.5750, -4.9050, 3.0000, 1.0000, 3.0000, 1.0000, 9.8100],
        "Kp_phi1_range"     : np.linspace(7.5, 17.5, 40),
        "Kd_phi1_range"     : np.linspace(0, 15, 40),
        "delay"             : reaction_time_s,
        "run_time"          : 120,
        "max_deg"           : 30,
        "p_g_d"             : False,
        "simTs"             : time_stamp_s,
        "D_a"               : 10.6,
        "D_cor_P"           : 8,
        "D_cor_D"           : 4.6,
    }

    M_3_data = {
        "sys_consts_double" : [66.6666666667, 0.333333333333333, 2.5000, -171.6750, -4.9050, 5.0000, 1.0000, 5.0000, 1.0000, 9.8100],
        "Kp_phi1_range"     : np.linspace(8, 25, 40),
        "Kd_phi1_range"     : np.linspace(0, 20, 40),
        "delay"             : reaction_time_s,
        "run_time"          : 120,
        "max_deg"           : 30,
        "p_g_d"             : False,
        "simTs"             : time_stamp_s,
        "D_a"               : 10,
        "D_cor_P"           : 15,
        "D_cor_D"           : 7.65,
    }

    M_5_data = {
        "sys_consts_double" : [433.3333333333333, 0.333333333333333, 5.0000, -588.6000, -4.9050, 10.0000, 1.0000, 10.0000, 1.0000, 9.8100],
        "Kp_phi1_range"     : np.linspace(0, 40, 40),
        "Kd_phi1_range"     : np.linspace(0, 40, 40),
        "delay"             : reaction_time_s,
        "run_time"          : 120,
        "max_deg"           : 30,
        "p_g_d"             : False,
        "simTs"             : time_stamp_s,
        "D_a"               : 10,
        "D_cor_P"           : 41.913626779,
        "D_cor_D"           : 18.7894721524,
    }

    M_7_data = {
        "sys_consts_double" : [433.3333333333333, 0.333333333333333, 5.0000, -588.6000, -4.9050, 10.0000, 1.0000, 10.0000, 1.0000, 9.8100],
        "Kp_phi1_range"     : np.linspace(0, 40, 20),
        "Kd_phi1_range"     : np.linspace(0, 40, 20),
        "delay"             : reaction_time_s+0.1,
        "run_time"          : 120,
        "max_deg"           : 30,
        "p_g_d"             : False,
        "simTs"             : time_stamp_s,
        "D_a"               : 10,
        "D_cor_P"           : 1,
        "D_cor_D"           : 4,
    }   

    M_9_data = {
        "sys_consts_double" : [66.6666666667, 0.333333333333, 2.5000, -171.6750, -4.9050, 5.0000, 1.0000, 5.0000, 1.0000, 9.8100],
        "Kp_phi1_range"     : np.linspace(0, 40, 20),
        "Kd_phi1_range"     : np.linspace(0, 40, 20),
        "delay"             : reaction_time_s+0.1,
        "run_time"          : 120,
        "max_deg"           : 30,
        "p_g_d"             : False,
        "simTs"             : time_stamp_s,
        "D_a"               : 10,
        "D_cor_P"           : 18.7894721524,
        "D_cor_D"           : 41.913626779,
    }

    PD_M1 = PD_Controller(f"M_1_20241220_043435",M_1_data)
    PD_M3 = PD_Controller(f"M_3_20241220_050127",M_3_data)
    PD_M5 = PD_Controller(f"M_5_20241220_040545",M_5_data)
    PD_M7 = PD_Controller(f"M_7_20241220_053347",M_7_data)
    PD_M9 = PD_Controller(f"M_9_20241220_065000",M_9_data)

    #PD_M1.generate_optimization().printresults().plot_PD_p().play_animation()
    #PD_M1.load_from_pkl_file().printresults().plot_PD_p()
    #PD_M3.generate_optimization().printresults().plot_PD_p().play_animation()
    #PD_M3.load_from_pkl_file().printresults().plot_PD_p().play_animation()
    PD_M5.generate_optimization().printresults()#.plot_PD_p().play_animation()
    #PD_M5.load_from_pkl_file().printresults().plot_PD_p().play_animation()
    #PD_M7.generate_optimization().printresults().save_best_pair()#.plot_PD_p().play_animation()
    #PD_M7.load_from_pkl_file().printresults().plot_PD_p().play_animation()
    #PD_M9.generate_optimization().printresults()#.plot_PD_p().play_animation()
    #PD_M9.load_from_pkl_file().printresults().plot_PD_p().play_animation()