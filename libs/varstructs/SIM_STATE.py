import time
import numpy as np
from threads_.numsim.libs import output_data_saver as ods
from threads_.numsim.libs.state_space import state_space

class SIM_STATE:
    """
    Simulation state manager for a double inverted pendulum simulation.

    This class initializes and manages the simulation state, including system variables,
    plotting data, control parameters, and mouse input data.

    Attributes:
        config_dict (dict): Configuration dictionary for the simulation.
        data_saver_obj (output_data_saver): Object for saving simulation output data.
        pointer_enhance_status (bool): Status flag for pointer enhancement.
        phi_var_0 (numpy.array): Initial state of the pendulum variables.
        SIM_STATE_VAR (dict): Dictionary containing all simulation state variables and configurations.
    """

    def __init__(self, config_dict, DPI_SCALEING) -> None:
        """
        Initializes the SIM_STATE class with the given configuration dictionary.

        Args:
            config_dict (dict): Configuration dictionary containing simulation parameters.
            DPI_SCALEING (float): DPI scaling factor for screen dimensions.
        """
        self.config_dict = config_dict
        self.data_saver_obj = ods.output_data_saver(self.config_dict)
        self.pointer_enhance_status = False

        # Initialize LQR control parameters
        LQR_Q = np.diag(config_dict["PD_control"]["LQR_Q"])
        pd_ft = round(config_dict["PD_control"]["time_delay_s"] / config_dict["simulation_config"]["sample_rate_s"])
        if pd_ft > 0:
            pd_ft -= 1

        self.state_space_ref = state_space(
            config_dict["geometry_config"]["double_pendulum"], 
            LQR_Q, 
            config_dict["PD_control"]["LQR_R"],
            config_dict["simulation_config"]["sample_rate_s"],
            config_dict["PD_control"]["time_delay_s"]
        )

        idofs = self.config_dict["simulation_config"]["model_initial_dof_values_rad"]
        phi_var_0 = np.array([[idofs[0]], [idofs[1]], [0.0], [0.0]])
        self.phi_var_0 = phi_var_0

        # Initialize the simulation state variables
        self.SIM_STATE_VAR = {
            "meta": {
                "SIM_TITLE": config_dict.get("simulation_config", {}).get("simulation_title", ""),
                "START_SIM_TIMESTAMP": int(time.time())
            },
            "GUI_conditions": {
                "INFINITE_SPACE": config_dict["geometry_config"]["infinite_vertical_space"],
                "FULLSCREEN": config_dict["geometry_config"]["fullscreen"],
                "DPI_SCALEING": DPI_SCALEING,
                "SCREEN_WIDTH_PX": config_dict.get("input_config", {}).get("screen_width_px", "") * DPI_SCALEING,
                "WIN_DIMS": [0, 0],
                "meter_per_pixel": (
                    config_dict["input_config"]["mouse_osl_move_mm"] / 1000 / config_dict["input_config"]["screen_width_px"]
                ) * config_dict["input_config"]["scale_x_axis_-"]
            },
            "simulation_config": {
                "DOUBLE_PENDULUM": config_dict["geometry_config"]["double_pendulum"],
                "NUM_METHOD": config_dict["simulation_config"]["num_method_-"],
                "G": config_dict["simulation_config"]["gravitational_force_m/s^2"],
                "SAMPLERATE_S": config_dict["simulation_config"]["sample_rate_s"],
                "CONSTANT_ROD_LENGTH": config_dict["simulation_config"]["constant_rod_length"],
                "ROD_A_DL_M": config_dict["simulation_config"]["rod_a_dl_m"],
                "ROD_A_DT_S": config_dict["simulation_config"]["rod_a_dt_s"],
                "ROD_B_DL_M": config_dict["simulation_config"]["rod_b_dl_m"],
                "ROD_B_DT_S": config_dict["simulation_config"]["rod_b_dt_s"]
            },
            "PD_control": {
                "PD_CONTROL_ON": config_dict["PD_control"]["PD_control_on"],
                "PD_MOUSE_INPUT": config_dict["PD_control"]["enable_mouse_input"],
                "PD_FRAME_TRIM": pd_ft,
                "CONTROL_METHOD": config_dict["PD_control"]["optimal_control_calc_method"],
                "PD_K_1": config_dict["PD_control"]["k1_-"],
                "PD_K_2": config_dict["PD_control"]["k2_-"],
                "PD_K_3": config_dict["PD_control"]["k3_-"],
                "PD_K_4": config_dict["PD_control"]["k4_-"],
                "PD_PHI_1_D": config_dict["PD_control"]["desired_phi_rad"],
                "PD_PHI_2_D": config_dict["PD_control"]["desired_phi_rad"],
                "PD_control_stack": [],
                "LQR_Q": LQR_Q,
                "LQR_R": config_dict["PD_control"]["LQR_R"]
            },
            "run_conditions": {
                "run_status": 0,
                "fps": 0,
                "FRAME_TRIM": 0,
                "TIME_DELAY_S": config_dict["simulation_config"]["time_delay_s"],
                "simulation_timer": {
                    "start": None,
                    "end": None,
                    "interrupted": False,
                    "dtime": 0
                }
            },
            "mouse_input": {
                "x": [],
                "dx": [],
                "ddx": [],
                "ddx_m": [],
                "h_s": [],
                "q_array_list": [],  # Contains arrays: [x_m, dx_m, ddx_m, timestamp]
                "cursor_replace_flag": 0,  # 0 - no replace method, 1 - replace method start, 2 - replace method finished
                "replace_counter": 0
            },
            "stateVars": {
                "sys_state": [],  # System state variables to be filled by self.update_sys_variables
                "phi_np_array_list": [
                    [phi_var_0, np.array([[0], [0], [0], [0]]), None, .0, .0]
                ],  # List of np arrays: [phi1, phi2, dphi1, dphi2]
                "sys_reports": []
            },
            "plotable_datasets": {
                "x": [],
                "dx": [],
                "ddx": [],
                "x_m": [],
                "dx_m": [],
                "ddx_m": [],
                "phi_1": [],
                "phi_2": [],
                "dphi_1": [],
                "dphi_2": [],
                "ddphi_1": [],
                "ddphi_2": [],
                "F": []
            }
        }

        self.update_sys_variables(
            self.config_dict["geometry_config"]["rod_a_length_m"],
            self.config_dict["geometry_config"]["rod_b_length_m"]
        )
        self.calculate_frame_trim()

    def run_status(self):
        """
        Retrieves the current run status of the simulation.

        Returns:
            int: The current run status (0: Nothing running, 1: Static run, 2: Simulation running).
        """
        return self.SIM_STATE_VAR["run_conditions"]["run_status"]

    def set_run_status(self, new_state: int, user_interrupted: bool = True):
        """
        Updates the run status of the simulation.

        Run status states:
            0 - Nothing running
            1 - Static run
            2 - Simulation running

        Args:
            new_state (int): The new run status to set.
            user_interrupted (bool): Flag indicating if the state change was user-interrupted (default: True).
        """
        if (
            (self.SIM_STATE_VAR["run_conditions"]["run_status"] == 1 and new_state == 2 and len(self.read_mouse_input("q_array_list", False)) < 3 + self.get_frame_trim())
            or (self.SIM_STATE_VAR["run_conditions"]["run_status"] == 2 and new_state != 2 and self.SIM_STATE_VAR["run_conditions"]["simulation_timer"]["start"] is None)
        ):
            return

        prev_state = self.SIM_STATE_VAR["run_conditions"]["run_status"]
        self.SIM_STATE_VAR["run_conditions"]["run_status"] = new_state

        print(f"prev_state: {prev_state},\t new_state: {new_state}")

        if prev_state == 0:
            if new_state == 1:  # Start simulation with static run.
                pass
            elif new_state == 2:  # Start simulation with simulation run (impossible).
                print("ERROR")
                return
            else:
                # Same state, do nothing.
                return
        elif prev_state == 1:
            if new_state == 0:  # Close simulation from static run (soft quit).
                pass
            elif new_state == 2:  # Start numsim from static run (start balancing).
                self.SIM_STATE_VAR["run_conditions"]["simulation_timer"]["start"] = time.time()
            else:
                # Same state, do nothing.
                return
        elif prev_state == 2:
            if new_state == 2:
                # Same state, do nothing.
                return
            else:
                """
                Save data and reset simulation variables:
                - mouse_input.*
                - stateVars.*
                - run_conditions.simulation_timer
                - plotable_datasets.*
                """
                self.SIM_STATE_VAR["run_conditions"]["simulation_timer"]["end"] = time.time()
                self.SIM_STATE_VAR["run_conditions"]["simulation_timer"]["interrupted"] = user_interrupted
                self.SIM_STATE_VAR["run_conditions"]["simulation_timer"]["dtime"] = (
                    self.SIM_STATE_VAR["run_conditions"]["simulation_timer"]["end"] - self.SIM_STATE_VAR["run_conditions"]["simulation_timer"]["start"]
                )

                # Save data
                self.data_saver_obj.save_new_round(self.SIM_STATE_VAR)

                # Reset data
                self.reset_numsim_round_data()

                if new_state == 0:  # Close simulation from numsim (hard quit).
                    pass
                elif new_state == 1:  # Finish numsim back to static run.
                    pass

    def reset_numsim_round_data(self):
        """
        Resets data for a new simulation round.

        This includes resetting the following:
        - mouse_input.*
        - stateVars.*
        - run_conditions.simulation_timer
        - plotable_datasets.*
        """
        idofs = self.config_dict["simulation_config"]["model_initial_dof_values_rad"]
        phi_var_0 = np.array([[idofs[0]], [idofs[1]], [0.0], [0.0]])

        self.SIM_STATE_VAR["mouse_input"] = {
            "x": [],
            "dx": [],
            "ddx": [],
            "ddx_m": [],
            "h_s": [],
            "q_array_list": [],  # np array containing [x_m, dx_m, ddx_m, timestamp]
            "cursor_replace_flag": 0,  # 0 - no replace method, 1 - replace method start, 2 - replace method finished
            "replace_counter": 0
        }
        self.SIM_STATE_VAR["stateVars"] = {
            "sys_state": [],  # System constants to be filled by self.update_sys_variables
            "phi_np_array_list": [
                [phi_var_0, np.array([[0], [0], [0], [0]]), None, .0, .0]
            ],  # List of phi angles and associated values
            "sys_reports": []
        }
        self.update_sys_variables(
            self.config_dict["geometry_config"]["rod_a_length_m"],
            self.config_dict["geometry_config"]["rod_b_length_m"]
        )

        self.SIM_STATE_VAR["run_conditions"]["simulation_timer"] = {
            "start": None,
            "end": None,
            "interrupted": False,
            "dtime": 0
        }

        self.SIM_STATE_VAR["PD_control"]["PD_control_stack"] = []

        self.SIM_STATE_VAR["plotable_datasets"] = {
            "x": [],
            "dx": [],
            "ddx": [],
            "x_m": [],
            "dx_m": [],
            "ddx_m": [],
            "phi_1": [],
            "phi_2": [],
            "dphi_1": [],
            "dphi_2": [],
            "ddphi_1": [],
            "ddphi_2": [],
            "F": []
        }

        self.calculate_frame_trim()

    def get_all_items(self):
        """
        Retrieves all key-value pairs from the simulation state variable.

        Returns:
            dict_items: All key-value pairs in SIM_STATE_VAR.
        """
        return self.SIM_STATE_VAR.items()

    def get_key_list(self):
        """
        Retrieves a list of all top-level keys in the simulation state variable.

        Returns:
            dict_keys: All top-level keys in SIM_STATE_VAR.
        """
        return self.SIM_STATE_VAR.keys()

    def get_l1(self, index=-1):
        """
        Retrieves the length of rod A from the system state or the default value.

        Args:
            index (int): The index of the desired system state (default: -1 for the latest).

        Returns:
            float: The length of rod A.
        """
        try:
            return self.SIM_STATE_VAR["stateVars"]["sys_state"][index][0]
        except IndexError:
            return self.config_dict["geometry_config"]["rod_a_length_m"]

    def get_l2(self, index=-1):
        """
        Retrieves the length of rod B from the system state or the default value.

        Args:
            index (int): The index of the desired system state (default: -1 for the latest).

        Returns:
            float: The length of rod B.
        """
        try:
            return self.SIM_STATE_VAR["stateVars"]["sys_state"][index][1]
        except IndexError:
            return self.config_dict["geometry_config"]["rod_b_length_m"]

    def get_data_by_key(self, key):
        """
        Retrieves a value from the simulation state variable by its hierarchical key.

        Args:
            key (str): The hierarchical key (e.g., "stateVars.sys_state").

        Returns:
            Any: The value associated with the key, or None if the key does not exist.
        """
        keys = key.split('.')
        current = self.SIM_STATE_VAR
        try:
            for k in keys:
                current = current[k]
            return current
        except KeyError:
            return None

    def set_data_by_key(self, key, value):
        """
        Sets a value in the simulation state variable using a hierarchical key.

        Args:
            key (str): The hierarchical key (e.g., "stateVars.sys_state").
            value (Any): The value to set.
        """
        keys = key.split('.')
        current = self.SIM_STATE_VAR
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    def get_latest_sys_consts(self, index=-1):
        """
        Retrieves the latest system constants from the system state.

        Args:
            index (int): The index of the desired system state (default: -1 for the latest).

        Returns:
            Any: The latest system constants, or None if unavailable.
        """
        try:
            return self.SIM_STATE_VAR["stateVars"]["sys_state"][index][2]
        except Exception as e:
            print(f"Error occurred: {e}")
            return None   
             
    # DoF_State_Stack
    def read_DoF_State_Stack(self, index=-1, trim=False, PD=False):
        """
        Reads the Degree of Freedom (DoF) state stack at the specified index.

        Args:
            index (int): The index of the desired state (default: -1 for the latest).
            trim (bool): Whether to trim the index by the frame trim value (default: False).
            PD (bool): Whether to consider PD (Proportional-Derivative) frame trim (default: False).

        Returns:
            Any: The DoF state at the specified index or the first state if the index is out of bounds.
        """
        frame_trim = self.get_frame_trim(PD)
        dataset = self.SIM_STATE_VAR["stateVars"]["phi_np_array_list"]

        if frame_trim > 0 and trim:
            index -= frame_trim

        if len(dataset) > abs(index):
            return dataset[index]

        return dataset[0]

    def append_DoF_State_Stack(self, value):
        """
        Appends a new state to the Degree of Freedom (DoF) state stack.

        Args:
            value (list): The new state to append, containing phi and its derivatives.
        """
        self.SIM_STATE_VAR["stateVars"]["phi_np_array_list"].append(value)
        plotable_datasets = self.SIM_STATE_VAR["plotable_datasets"]
        if plotable_datasets is not None:
            plotable_datasets["phi_1"].append(value[0][0][0])
            plotable_datasets["phi_2"].append(value[0][1][0])
            plotable_datasets["dphi_1"].append(value[0][2][0])
            plotable_datasets["dphi_2"].append(value[0][3][0])
            plotable_datasets["ddphi_1"].append(value[1][2][0])
            plotable_datasets["ddphi_2"].append(value[1][3][0])
            plotable_datasets["F"].append(value[3])

    def update_sys_variables(self, l1, l2=None):
        """
        Updates the system variables using the given lengths and configuration parameters.

        Args:
            l1 (float): The length of rod A.
            l2 (float, optional): The length of rod B. Defaults to None.
        """
        rho1 = self.config_dict["geometry_config"]["rod_a_m/l_ratio_kg/m"]
        rho2 = self.config_dict["geometry_config"]["rod_b_m/l_ratio_kg/m"]
        g = self.config_dict["simulation_config"]["gravitational_force_m/s^2"]

        self.state_space_ref.update_system_constants(rho1, rho2, l1, l2, g)
        sys_consts = self.state_space_ref.get_system_constants()
        self.SIM_STATE_VAR["stateVars"]["sys_reports"].append(self.state_space_ref.doReport())
        timestamp = time.time()
        self.SIM_STATE_VAR["stateVars"]["sys_state"].append([l1, l2, sys_consts, timestamp])

    def calculate_frame_trim(self, measured_sample_rate=None):
        """
        Calculates the frame trim based on the simulation sample rate and time delay.

        Args:
            measured_sample_rate (float, optional): Measured sample rate in seconds. Defaults to None.
        """
        sample_rate_s = self.get_data_by_key("simulation_config.SAMPLERATE_S") if measured_sample_rate is None else measured_sample_rate
        time_delay_s = self.get_data_by_key("run_conditions.TIME_DELAY_S")

        frame_trim = round(time_delay_s / sample_rate_s)

        if frame_trim > 0:
            frame_trim -= 1

        self.SIM_STATE_VAR["run_conditions"]["FRAME_TRIM"] = frame_trim

    def get_frame_trim(self, PD=False):
        """
        Retrieves the frame trim value for the simulation.

        Args:
            PD (bool): Whether to retrieve the PD frame trim value (default: False).

        Returns:
            int: The frame trim value.
        """
        if PD:
            return self.SIM_STATE_VAR["PD_control"]["PD_FRAME_TRIM"]
        else:
            return self.SIM_STATE_VAR["run_conditions"]["FRAME_TRIM"]

    def read_mouse_input(self, key, trim=False, PD=False):
        """
        Reads mouse input data by key with optional frame trimming.

        Args:
            key (str): The key to retrieve mouse input data (e.g., "x", "dx", "ddx").
            trim (bool): Whether to trim the dataset by frame trim (default: False).
            PD (bool): Whether to consider PD frame trim (default: False).

        Returns:
            list: The mouse input dataset.
        """
        dataset = self.get_data_by_key(f"mouse_input.{key}")

        if trim:
            frame_trim = self.get_frame_trim(PD)
            if len(dataset) > frame_trim:
                return dataset[:-frame_trim] if frame_trim > 0 else dataset
            else:
                return dataset[0:1]
        else:
            return dataset

    def get_PD_K_vector(self, update=True):
        """
        Retrieves the Proportional-Derivative (PD) K vector values.

        Args:
            update (bool): Whether to update the K vector values before retrieval (default: True).

        Returns:
            tuple: The K vector values (K_1, K_2, K_3, K_4).
        """
        if update:
            self.update_control_K_vector()

        return (
            self.get_data_by_key("PD_control.PD_K_1"),
            self.get_data_by_key("PD_control.PD_K_2"),
            self.get_data_by_key("PD_control.PD_K_3"),
            self.get_data_by_key("PD_control.PD_K_4")
        )

    def update_control_K_vector(self):
        """
        Updates the Proportional-Derivative (PD) K vector based on the control method.

        Supported control methods:
        - "custom": Uses custom K vector values from the configuration.
        - "h_inf": Uses H-infinity control K vector.
        - "lqr": Uses Linear Quadratic Regulator (LQR) K vector.

        Returns:
            tuple: The control indicator and K vector values (control_method, K_1, K_2, K_3, K_4).
        """
        control_method = str(self.get_data_by_key("PD_control.CONTROL_METHOD"))

        pole_place_K, riccati_K, cnt_K_H_inf = self.state_space_ref.get_K()

        control_indicator = None

        if control_method.lower() == "custom":
            K_1, K_2, K_3, K_4 = self._get_custom_PD_K_vector()
            control_indicator = "custom"
        elif control_method.lower() == "h_inf":
            K_1, K_2, K_3, K_4 = cnt_K_H_inf.flatten()
            control_indicator = "h_inf"
        elif control_method.lower() == "lqr":
            K_1, K_2, K_3, K_4 = riccati_K.flatten()
            control_indicator = "lqr"
        else:
            K_1, K_2, K_3, K_4 = None, None, None, None

        self.set_data_by_key("PD_control.PD_K_1", K_1)
        self.set_data_by_key("PD_control.PD_K_2", K_2)
        self.set_data_by_key("PD_control.PD_K_3", K_3)
        self.set_data_by_key("PD_control.PD_K_4", K_4)

        self.set_data_by_key("PD_control.CONTROL_METHOD", control_indicator)

        return control_indicator, K_1, K_2, K_3, K_4

    def _get_custom_PD_K_vector(self):
        """
        Retrieves custom Proportional-Derivative (PD) K vector values from the configuration.

        Returns:
            tuple: Custom K vector values (K_1, K_2, K_3, K_4).
        """
        K_1 = self.config_dict["PD_control"]["k1_-"]
        K_2 = self.config_dict["PD_control"]["k2_-"]
        K_3 = self.config_dict["PD_control"]["k3_-"]
        K_4 = self.config_dict["PD_control"]["k4_-"]

        return K_1, K_2, K_3, K_4

    @staticmethod
    def _convert_K_to_elements(var):
        """
        Converts a variable to two numerical elements (K1, K2).

        Args:
            var (Any): The variable to convert. It can be a number, string, or comma-separated values.

        Returns:
            tuple: Two numerical elements (K1, K2).

        Raises:
            ValueError: If the input cannot be converted to numerical values.
        """
        try:
            # Attempt to convert the variable to a single number
            var = float(var)
            K1 = var
            K2 = var
        except ValueError:
            var = str(var).strip()  # Remove spaces
            if ',' in var:
                parts = var.split(',')
                if len(parts) == 2:
                    try:
                        # Convert comma-separated values to numbers
                        K1 = float(parts[0].strip())
                        K2 = float(parts[1].strip())
                    except ValueError:
                        raise ValueError("The parts of the string cannot be converted to numbers.")
                else:
                    raise ValueError("The string contains more than one comma.")
            else:
                try:
                    var = float(var.replace(' ', ''))  # Remove spaces
                    K1 = var
                    K2 = var
                except ValueError:
                    raise ValueError("The string cannot be converted to a number.")
        return K1, K2
    
    def read_PD_u_q(self, index=-1, force_read=False, trim=True):
        """
        Reads the Proportional-Derivative (PD) control values for a given index.

        Args:
            index (int): The index of the desired PD control value (default: -1 for the latest).
            force_read (bool): Whether to force reading the PD control values regardless of control status (default: False).
            trim (bool): Whether to trim the dataset using the PD frame trim value (default: True).

        Returns:
            list: The PD control values [ddu_m, du_m, u_m, ts] or a default zeroed list if unavailable.
        """
        if len(self.SIM_STATE_VAR["PD_control"]["PD_control_stack"]) >= abs(index):
            if force_read or self.get_data_by_key("PD_control.PD_CONTROL_ON"):
                PD_frame_trim = self.get_data_by_key("PD_control.PD_FRAME_TRIM")
                dataset = self.get_data_by_key("PD_control.PD_control_stack")

                if trim and len(dataset) > PD_frame_trim:
                    if abs(index - PD_frame_trim) < len(dataset):
                        return dataset[index - PD_frame_trim]["PD_u_q"]
                    else:
                        return dataset[index]["PD_u_q"]
                else:
                    return dataset[index]["PD_u_q"]
            else:
                return [.0, .0, .0, None]
        else:
            return [.0, .0, .0, None]

    def update_PD_vals(self, force_calc=False):
        """
        Updates the Proportional-Derivative (PD) control values.

        Args:
            force_calc (bool): Whether to force the calculation of PD values regardless of control status (default: False).
        """
        if force_calc or self.get_data_by_key("PD_control.PD_CONTROL_ON"):
            dof_state_stack = self.read_DoF_State_Stack(-1, True, True)[0]

            phi_1_act = dof_state_stack[0][0]
            phi_2_act = dof_state_stack[1][0]
            dphi_1_act = dof_state_stack[2][0]
            dphi_2_act = dof_state_stack[3][0]

            K_1, K_2, K_3, K_4 = self.get_PD_K_vector()

            # Calculate cart acceleration
            ddq_u = -(K_1 * phi_1_act + K_2 * phi_2_act + K_3 * dphi_1_act + K_4 * dphi_2_act)

            u_q_l = [0.0, 0.0, 0.0, 0.0]  # [ddu, du, u, ts]
            len_PD_cs = len(self.SIM_STATE_VAR["PD_control"]["PD_control_stack"])

            if len_PD_cs > 1:
                pre_u = self.read_PD_u_q()
                ts_p = pre_u[3]
                ts_n = time.time()
                dt_s = ts_n - ts_p
                du = ddq_u * dt_s

                u_q_l = [ddq_u, du, du * dt_s, ts_n]  # [ddu, du, u, ts]
            else:
                u_q_l = [ddq_u, 0.0, 0.0, time.time()]  # [ddu, du, u, ts]

            PD_s = {
                "PD_phi_1_act": phi_1_act,
                "PD_phi_2_act": phi_2_act,
                "PD_dphi_1_act": dphi_1_act,
                "PD_dphi_2_act": dphi_2_act,
                "PD_u_q": u_q_l
            }

            self.SIM_STATE_VAR["PD_control"]["PD_control_stack"].append(PD_s)
