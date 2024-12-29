import threads_.numsim.libs.cursor_position as cursor_pos
import threads_.numsim.num_simulator as num_simulator
from libs.varstructs.SIM_STATE import SIM_STATE

def num_sim_update(SIM_STATE_ref: SIM_STATE, max_theta_1):
    """
    Updates the numerical simulation state and processes cursor input.

    Parameters:
    - SIM_STATE_ref (SIM_STATE): Reference to the simulation state object.
    - max_theta_1 (float): Maximum allowable angle for the first pendulum before stopping the simulation.

    Returns:
    - None
    """

    # Retrieve necessary simulation parameters from the state
    screen_width_px = SIM_STATE_ref.get_data_by_key("GUI_conditions.SCREEN_WIDTH_PX")
    meter_per_pixel = SIM_STATE_ref.get_data_by_key("GUI_conditions.meter_per_pixel")
    double_pendulum = SIM_STATE_ref.get_data_by_key("simulation_config.DOUBLE_PENDULUM")

    # Update cursor position and mouse input data in the simulation state
    cursor_pos.update(
        SIM_STATE_ref.SIM_STATE_VAR["mouse_input"],
        SIM_STATE_ref.SIM_STATE_VAR["plotable_datasets"],
        screen_width_px,
        False,  # const_null_pos: indicates whether to use a constant null position
        meter_per_pixel
    )

    # Check if sufficient data points exist to start the simulation
    if len(SIM_STATE_ref.read_mouse_input("q_array_list", False)) > 2 + SIM_STATE_ref.get_frame_trim():
        
        # Check if the simulation is currently running
        if SIM_STATE_ref.run_status() == 2:
            # Perform a single step of the numerical simulation
            result = num_simulator.num_sim(double_pendulum, SIM_STATE_ref)

            # Update the simulation state with the results
            SIM_STATE_ref.append_DoF_State_Stack(result)
            SIM_STATE_ref.update_PD_vals()

            # Stop the simulation if the first pendulum's angle exceeds the maximum limit
            if abs(SIM_STATE_ref.read_DoF_State_Stack(-1, True, False)[0][0][0]) >= max_theta_1:
                SIM_STATE_ref.set_run_status(1)  # Set run status to stopped (1)

        elif SIM_STATE_ref.run_status() == 1:
            # If the simulation is already stopped, take no further action
            pass