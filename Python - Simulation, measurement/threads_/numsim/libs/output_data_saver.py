import csv
from copy import copy
from datetime import datetime
import os
import yaml

class output_data_saver:
    """
    A utility class to save simulation output data, organize simulation sections, 
    and manage configuration files in YAML format. Provides methods to save data 
    for each simulation round and create organized folders for outputs.
    
    Attributes:
        config_dict (dict): Configuration dictionary for the simulation.
        section_folder_path (str): Path to the folder for the current simulation section.
        round_counter (int): Counter for simulation rounds.
    """
    
    def __init__(self, config_dict) -> None:
        """
        Initialize the output data saver with a configuration dictionary.

        Parameters:
            config_dict (dict): Configuration dictionary for the simulation.
        """
        self.config_dict = config_dict
        self.section_folder_path = None
        self.round_counter = 0

    def save_new_round(self, SIM_STATE_VAR):
        """
        Save output data for a new simulation round.

        Parameters:
            SIM_STATE_VAR (dict): Current state of the simulation.
        """
        if self.section_folder_path is None:
            self.new_section()
        
        self.round_counter += 1

        sim_title = SIM_STATE_VAR["meta"]["SIM_TITLE"]
        start_time = SIM_STATE_VAR["meta"]["START_SIM_TIMESTAMP"]

        csv_file_name = output_data_saver.gen_file_name(sim_title, start_time, self.round_counter)
        
        output_data_saver._save_output_file(csv_file_name, self.section_folder_path, SIM_STATE_VAR)

    def new_section(self):
        """
        Start a new simulation section by creating a folder and saving the configuration.
        """
        self.round_counter = 0
        self.section_folder_path = output_data_saver._create_section_folder(self.config_dict)
        output_data_saver._save_config_to_yaml(self.section_folder_path, self.config_dict)

    @staticmethod   
    def gen_file_name(sim_title, sim_start_timestamp, index):
        """
        Generate a unique file name for a simulation output file.

        Parameters:
            sim_title (str): Title of the simulation.
            sim_start_timestamp (float): Simulation start timestamp.
            index (int): Round index for the simulation.

        Returns:
            str: Generated file name.
        """
        dt_object = datetime.fromtimestamp(int(sim_start_timestamp))
        formatted_date = dt_object.strftime("%Y%m%d_%H%M%S")
        
        output_file_name = output_data_saver._generate_unique_filename(f"{index}_{formatted_date}.csv")
        return output_file_name

    @staticmethod    
    def _save_config_to_yaml(folder_path, config_dict):
        """
        Save the configuration dictionary to a YAML file in the given folder.

        Parameters:
            folder_path (str): Path to the folder where the YAML file will be saved.
            config_dict (dict): Configuration dictionary to save.

        Returns:
            bool: True if saving was successful, False otherwise.
        """
        file_path = os.path.join(folder_path, "config_file.yaml")
        try:
            with open(file_path, 'w') as file:
                yaml.safe_dump(config_dict, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
            print(f"Successfully saved: {file_path}")
            return True
        except FileNotFoundError:
            print(f"Error: Path not found: {file_path}")
        except PermissionError:
            print(f"Error: Permission denied to write file: {file_path}")
        except Exception as e:
            print(f"Unknown error occurred: {e}")

        return False

    @staticmethod    
    def _create_section_folder(config_dict):
        """
        Create a folder for a new simulation section.

        Parameters:
            config_dict (dict): Configuration dictionary for the simulation.

        Returns:
            str: Path to the created folder.
        """
        title = config_dict["simulation_config"]["simulation_title"]
        parent_path = "./output_datasets"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{title}_{timestamp}"
        folder_path = os.path.join(parent_path, folder_name)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        return folder_path

    @staticmethod    
    def _generate_unique_filename(base_filename):
        """
        Generate a unique filename by appending a counter if the file already exists.

        Parameters:
            base_filename (str): Base file name.

        Returns:
            str: Unique file name.
        """
        if not os.path.exists(base_filename):
            return base_filename

        base, extension = os.path.splitext(base_filename)
        counter = 2
        new_filename = f"{base}_{counter}{extension}"
        while os.path.exists(new_filename):
            counter += 1
            new_filename = f"{base}_{counter}{extension}"
        
        return new_filename

    def create_list_of_lists(SIM_STATE_VAR):
        """
        Create a nested list structure from simulation state variables.

        Parameters:
            SIM_STATE_VAR (dict): Current state of the simulation.

        Returns:
            list: Nested list containing simulation data.
        """
        dx = copy(SIM_STATE_VAR["mouse_input"]["dx"])
        dx.insert(0, [0, 0, 0])
        ddx = copy(SIM_STATE_VAR["mouse_input"]["ddx"])
        ddx.insert(0, [0, 0, 0])
        ddx.insert(0, [0, 0, 0])
        ret_list = [
            copy(SIM_STATE_VAR["mouse_input"]["x"]),
            dx,
            ddx,
            copy(SIM_STATE_VAR["PD_control"]["PD_u_q"]),
            copy(SIM_STATE_VAR["simulation_config"]["l1"]),
            copy(SIM_STATE_VAR["simulation_config"]["l2"]),
            copy(SIM_STATE_VAR["mouse_input"]["q_array_list"]),
        ]

        return ret_list

    @staticmethod 
    def write_constant_datas(writer:csv.writer, SIM_STATE_VAR):
        """
        Write constant data from the simulation state variables (SIM_STATE_VAR) into a CSV file.

        Parameters:
        writer (csv.writer): CSV writer object to write data into the file.
        SIM_STATE_VAR (dict): A dictionary containing simulation state variables and constants.
        """

        # Dictionary mapping high-level keys to specific constant subkeys to extract
        constant_keys = {
            "meta":                 ["SIM_TITLE",
                                     "START_SIM_TIMESTAMP"],
            "GUI_conditions":       ["INFINITE_SPACE",
                                     "FULLSCREEN",
                                     "DPI_SCALEING",
                                     "SCREEN_WIDTH_PX",
                                     "WIN_DIMS",
                                     "meter_per_pixel",
                                     "dim_scale"],
            "simulation_config":    ["DOUBLE_PENDULUM",
                                     "NUM_METHOD",
                                     "G",
                                     "SAMPLERATE_S",
                                     "CONSTANT_ROD_LENGTH",
                                     "ROD_A_DL_M",
                                     "ROD_A_DT_S",
                                     "ROD_B_DL_M",
                                     "ROD_B_DT_S"],
            "PD_control":           ["PD_CONTROL_ON",
                                     "PD_MOUSE_INPUT",
                                     "PD_FRAME_TRIM",
                                     "CONTROL_METHOD",
                                     "PD_K_1",
                                     "PD_K_2",
                                     "PD_K_3",
                                     "PD_K_4",
                                     "PD_PHI_1_D",
                                     "PD_PHI_2_D"],
            "run_conditions":       ["FRAME_TRIM",
                                     "TIME_DELAY_S",
                                     "simulation_timer"]
        }

        # Iterate over the keys and their corresponding values to write them into the CSV
        for key, values in constant_keys.items():
            # Write the top-level key as a header row
            writer.writerow([f"{key}", f"_", f"_", f"_",])
            for value in values:
                element = SIM_STATE_VAR[key][value]
                # Handle nested dictionaries
                if isinstance(element, dict):
                    writer.writerow(["_", f"{value}", f"_", f"_",])
                    for sub_key, sub_val in element.items():
                        writer.writerow(["_", "_", f"{sub_key}", f"{sub_val}",])
                # Handle iterable objects (except strings)
                elif output_data_saver.is_iterable(element):
                    writer.writerow(["_", f"{value}", f"_", f"_",])
                    for i in range(0, len(element)):
                        writer.writerow(["_", "_", f"{element[i]}", f"_",])
                # Handle non-iterable elements (e.g., numbers, strings)
                else:
                    writer.writerow(["_", f"{value}", f"{element}", f"_",])

    @staticmethod
    def is_iterable(obj):
        """
        Determine if an object is iterable, excluding strings.

        Parameters:
        obj: The object to check for iterability.

        Returns:
        bool: True if the object is iterable and not a string, False otherwise.
        """
        try:
            if isinstance(obj, str):
                return False  # Exclude strings as they are technically iterable but not treated as such here
            iter(obj)
            return True  # Object is iterable
        except TypeError:
            return False  # Object is not iterable

    
    @staticmethod 
    def write_listable_datas(writer:csv.writer, SIM_STATE_VAR):
        """
        Writes listable data from the simulation state to the CSV file.

        Parameters:
        writer (csv.writer): The CSV writer object to write data.
        SIM_STATE_VAR (dict): The simulation state variables containing the data.
        """
        
        # q_array_list:
        q_a_l = SIM_STATE_VAR["mouse_input"]["q_array_list"]
        if q_a_l is not None:
            writer.writerow(['#','mouse_input','q_array_list'])
            writer.writerow(['*','x_m',"_"]+[d[0] for d in q_a_l])
            writer.writerow(['*','dx_m',"_"]+[d[1] for d in q_a_l])
            writer.writerow(['*','ddx_m',"_"]+[d[2] for d in q_a_l])
            writer.writerow(['*','timestamp',"_"]+[d[3] for d in q_a_l])

        # sys_state:
        sys_state_l = SIM_STATE_VAR["stateVars"]["sys_state"]
        if sys_state_l is not None:
            writer.writerow(['#','stateVars','sys_state'])
            lngth = len(sys_state_l[0][2])
            for i in range(lngth):
                writer.writerow(['*',f"id_{i}","_"]+[d[2][i] for d in sys_state_l])
            writer.writerow(['*','timestamp',"_"]+[d[3] for d in sys_state_l])

        # phi_np_array_list:
        phi_l = SIM_STATE_VAR["stateVars"]["phi_np_array_list"]
        if phi_l is not None:
            writer.writerow(['#','stateVars','phi_np_array_list'])
            writer.writerow(['*',"x","phi_1"]+[d[0][0][0] for d in phi_l])
            writer.writerow(['*',"x","phi_2"]+[d[0][1][0] for d in phi_l])
            writer.writerow(['*',"x","dphi_1"]+[d[0][2][0] for d in phi_l])
            writer.writerow(['*',"x","dphi_2"]+[d[0][3][0] for d in phi_l])
            writer.writerow(['*',"dx","dphi_1"]+[d[1][0][0] for d in phi_l])
            writer.writerow(['*',"dx","dphi_2"]+[d[1][1][0] for d in phi_l])
            writer.writerow(['*',"dx","ddphi_1"]+[d[1][2][0] for d in phi_l])
            writer.writerow(['*',"dx","ddphi_2"]+[d[1][3][0] for d in phi_l])
            writer.writerow(['*',"timestamp","_"]+[d[2] for d in phi_l])
            writer.writerow(['*',"F1","_"]+[d[3] for d in phi_l])
            writer.writerow(['*',"ddq","_"]+[d[4] for d in phi_l])
            
        # phi_np_array_list:
        sys_reps_l = SIM_STATE_VAR["stateVars"]["sys_reports"]
        if sys_reps_l is not None:
            writer.writerow(['#','stateVars','sys_reports'])
            writer.writerow(['*', "timestamp", "_"] + [(d["timestamp"] if d is not None else "None") for d in sys_reps_l])
            writer.writerow(['*', "M_rank", "_"] + [(d["M_rank"] if d is not None else "None") for d in sys_reps_l])
            writer.writerow(['*', "desired_poles", "_"] + [(d["desired_poles"] if d is not None else "None") for d in sys_reps_l])
            writer.writerow(['*', "K_gain", "_"] + [(str(d["K_gain"].tolist()) if d is not None else "None") for d in sys_reps_l])
            writer.writerow(['*', "LQR_Q", "_"] + [(str(d["LQR_Q"].tolist()) if d is not None else "None") for d in sys_reps_l])
            writer.writerow(['*', "LQR_R", "_"] + [(d["LQR_R"] if d is not None else "None") for d in sys_reps_l])
            writer.writerow(['*', "LQR_P_ARE", "_"] + [(str(d["LQR_P_ARE"].tolist()) if d is not None else "None") for d in sys_reps_l])
            writer.writerow(['*', "LQR_K_opt", "_"] + [(str(d["LQR_K_opt"].tolist()) if d is not None else "None") for d in sys_reps_l])
            writer.writerow(['*', "t_span", "_"] + [(d["t_span"] if d is not None else "None") for d in sys_reps_l])
            writer.writerow(['*', "H_inf_K", "_"] + [(d["H_inf_K"] if d is not None else "None") for d in sys_reps_l])

        # PD_control_stack:
        PD_cs_l = SIM_STATE_VAR["PD_control"]["PD_control_stack"]
        if PD_cs_l is not None:
            writer.writerow(['#','PD_control','PD_control_stack'])
            writer.writerow(['*',"PD_phi_1_act"     ,"_"]+[d["PD_phi_1_act"] for d in PD_cs_l])
            writer.writerow(['*',"PD_phi_2_act"     ,"_"]+[d["PD_phi_2_act"] for d in PD_cs_l])
            writer.writerow(['*',"PD_dphi_1_act"    ,"_"]+[d["PD_dphi_1_act"] for d in PD_cs_l])
            writer.writerow(['*',"PD_dphi_2_act"    ,"_"]+[d["PD_dphi_2_act"] for d in PD_cs_l])
            writer.writerow(['*',"PD_u_q"           ,"u_q"]+[d["PD_u_q"][0] for d in PD_cs_l])
            writer.writerow(['*',"PD_u_q"           ,"du_q"]+[d["PD_u_q"][1] for d in PD_cs_l])
            writer.writerow(['*',"PD_u_q"           ,"ddu_q"]+[d["PD_u_q"][2] for d in PD_cs_l])
            writer.writerow(['*',"PD_u_q"           ,"timestamp"]+[d["PD_u_q"][3] for d in PD_cs_l])


    @staticmethod   
    def _save_output_file(file_name, folder_path, SIM_STATE_VAR):
        """
        Saves simulation data to a CSV file.

        Parameters:
        file_name (str): The name of the output file.
        folder_path (str): The directory where the file should be saved.
        SIM_STATE_VAR (dict): The simulation state variables to save.
        """
        csv_file_path = os.path.join(folder_path, file_name)

        print(f"csv_file_path: {csv_file_path}")

        # Write data to the CSV file
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write constant data
            output_data_saver.write_constant_datas(writer,SIM_STATE_VAR)
            
            writer.writerow(['____','____','____','____'])

            # Write listable data
            output_data_saver.write_listable_datas(writer,SIM_STATE_VAR)
                
        print(f"Data successfully saved to {csv_file_path}.")